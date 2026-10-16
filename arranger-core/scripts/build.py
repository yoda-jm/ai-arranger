"""Build the score of an arrangement file: MusicXML -> MuseScore .mscz (voices play as piano, VP as drum kit, chord
symbols muted) -> PDF + MIDI (+ PNG page previews), and OUTDIR/events.json for render.py / qa.py.

usage: build.py ARRANGEMENT.py OUTDIR [--work W] [--name BASE] [--bars-per-system 4] [--play-chords]
                [--no-mscore] [--png] [--scaling 5.2] [--lib DIR ...]
  --lib DIR (or $ARRANGER_LIBS): a style layer's scripts folder the arrangement imports from (e.g. band.py)
"""
import sys, os, json, subprocess, zipfile, shutil, re, argparse, runpy, shlex, glob
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ap = argparse.ArgumentParser()
ap.add_argument("arrangement"); ap.add_argument("out"); ap.add_argument("--work"); ap.add_argument("--name")
ap.add_argument("--bars-per-system", type=int, default=4); ap.add_argument("--play-chords", action="store_true")
ap.add_argument("--no-mscore", action="store_true"); ap.add_argument("--png", action="store_true")
ap.add_argument("--scaling", type=float, default=5.2, help="mm per staff space (smaller = more music per A4 page)")
ap.add_argument("--staff-distance", type=int, default=55, help="space between staves, in tenths (band scores: ~40)")
ap.add_argument("--lib", action="append", default=[], help="extra module folder for the arrangement (a style layer)")
a = ap.parse_args()
for lib in reversed(a.lib + [x for x in os.environ.get("ARRANGER_LIBS", "").split(os.pathsep) if x]):
    sys.path.insert(1, os.path.abspath(lib))

import engine as E
if a.work: E.WORK = os.path.abspath(a.work); os.environ["ACAP_WORK"] = E.WORK
sys.path.insert(0, os.path.dirname(os.path.abspath(a.arrangement)))
runpy.run_path(a.arrangement, run_name="__arrangement__")
if a.work: E.WORK = os.path.abspath(a.work)
E.finish()
SECS, VOICES, BAR = E.SECS, E.VOICES, E.BAR
OUT = a.out; os.makedirs(OUT, exist_ok=True)
BASE = a.name or E.META.get("name") or re.sub(r"\W+", "_", E.META["title"].lower()).strip("_") or "arrangement"

FIFTHS = {"C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "C#": 7, "F": -1, "Bb": -2, "Eb": -3, "Ab": -4,
          "Db": -5, "Gb": -6, "Cb": -7}
KIND = {"": ("major", ""), "m": ("minor", "m"), "7": ("dominant", "7"), "m7": ("minor-seventh", "m7"),
        "maj7": ("major-seventh", "maj7"), "sus": ("suspended-fourth", "sus4"), "sus4": ("suspended-fourth", "sus4"),
        "7sus": ("suspended-fourth", "7sus4"), "7sus4": ("suspended-fourth", "7sus4"), "6": ("major-sixth", "6"),
        "dim": ("diminished", "dim"), "m6": ("minor-sixth", "m6"), "add9": ("major", "add9"),
        "madd9": ("minor", "madd9"), "sus2": ("suspended-second", "sus2"), "aug": ("augmented", "+"),
        "dim7": ("diminished-seventh", "dim7"), "m7b5": ("half-diminished", "m7b5"), "9": ("dominant-ninth", "9"),
        "m9": ("minor-ninth", "m9"), "maj9": ("major-ninth", "maj9")}
REP = {1: ("16th", 0), 2: ("eighth", 0), 3: ("eighth", 1), 4: ("quarter", 0), 6: ("quarter", 1), 7: ("quarter", 2),
       8: ("half", 0), 12: ("half", 1), 14: ("half", 2), 16: ("whole", 0), 24: ("whole", 1)}
INFO = E.VOICE_INFO
DRUM = E.DRUM
# tablature: a part in E.TAB gets a second (TAB) staff; its notation staff uses an octave clef instead of a
# transposition, because MuseScore recomputes the frets from the written pitch of a transposed part
TRANS = {v: k for v, k in E.TRANSPOSE.items() if v not in E.TAB}
TABF = {}
if E.TAB:
    import fretboard
    for v in [x for x in VOICES if x in E.TAB]:
        tuning, maxf = E.TAB[v]
        keys, seq, last = [], [], {}
        m0 = 0
        for si, s in enumerate(SECS):
            for bi in range(s["nbars"]):
                for ei, e in enumerate(s["parts"][v][bi]):
                    if e["midi"] is None: continue
                    ps = tuple(sorted(e["midi"])) if isinstance(e["midi"], tuple) else (e["midi"],)
                    if e.get("slash") and e.get("stroke") in ("U", "u"): ps = ps[-4:]
                    if e["tie_in"] and ps in last: TABF[(v, si, bi, ei)] = last[ps]; continue
                    keys.append((v, si, bi, ei)); seq.append((ps, (m0 + bi) * BAR + e["start"]))
            m0 += s["nbars"]
        for k, pl in zip(keys, fretboard.fingering(seq, tuning, maxf)):
            TABF[k] = pl
        bad = sum(pl is None for pl in TABF.values())
        print(f"tab {v}: {len(keys)} attacks placed" + (f", {bad} out of the instrument's range" if bad else ""))
for v in VOICES:
    if v not in INFO: raise SystemExit(f"unknown voice key {v!r}: add it to engine.VOICE_INFO")
PERC = {v: E.is_perc(v) for v in VOICES}


def kit(v):
    """Percussion map of a part: sound -> dict(step, octave, gm, head, stem, mark, vel, label)."""
    if v in E.KITS: return E.KITS[v]
    return {k: dict(step=st, octave=oc, gm=num, head=head, stem="down" if k == "B" else "up", mark=None, vel=1.0, label=k)
            for k, (st, oc, num, head) in DRUM.items()}


def slash_pos(v):
    """Written position of a rhythm slash: the middle line of the part's clef."""
    sign, _, octv = INFO[v][2]
    return ("D", 3 + octv) if sign == "F" else ("B", 4 + octv)


# ---------------------------------------------------------------- tie sanitation across the whole part
def flat(v):
    for s in SECS:
        for b in s["parts"][v]:
            for e in b: yield e


for v in VOICES:
    evs = list(flat(v))
    flags = [(e["tie_in"], e["tie_out"]) for e in evs]
    for e in evs: e["tie_in"] = e["tie_out"] = False
    for i in range(len(evs) - 1):
        e, nxt = evs[i], evs[i + 1]
        if e["midi"] is None or nxt["midi"] is None or PERC[v]: continue
        if nxt["midi"] == e["midi"] and (flags[i][1] or flags[i + 1][0]):
            e["tie_out"] = nxt["tie_in"] = True; nxt["lyr"] = ""


# ---------------------------------------------------------------- spelling / durations
def fifths(key): return FIFTHS[E.major_of(key)]


LETTERS = "CDEFGAB"; NATURAL = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)


def _on_letter(pc, letter):
    """Spell pitch class pc on a given letter (with up to two accidentals) -> name or None."""
    alt = (pc - NATURAL[letter] + 6) % 12 - 6
    return letter + ("#" * alt if alt > 0 else "b" * -alt) if abs(alt) <= 2 else None


def spell(m, key, sym=None, hint=None):
    """(step, alter, octave) for MIDI m: key signature spelling; a chromatic note that is the 3rd or 7th of the chord
    sounding (sym) is spelled from the chord's root (C# in A7, Ab in Bb7), a minor key's leading tone is sharp, and
    hint 'sharp' / 'flat' forces the direction (chromatic approach notes)."""
    f = fifths(key)
    names_s = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    names_f = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    pc = m % 12
    if f == 0: nm = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"][pc]
    else: nm = (names_s if f > 0 else names_f)[pc]
    if hint in ("sharp", "flat"):
        nm = (names_s if hint == "sharp" else names_f)[pc]
    elif pc not in E.scale(key):
        if key.endswith("m") and pc == (E.PC[key[:-1]] + 11) % 12:      # leading tone of a minor key
            nm = _on_letter(pc, LETTERS[(LETTERS.index(key[0]) + 6) % 7]) or nm
        elif sym:
            c = E.chord(sym)
            for deg, tone in ((2, c["third"]), (6, c["sev"])):
                if tone == pc:
                    nm = _on_letter(pc, LETTERS[(LETTERS.index(sym[0]) + deg) % 7]) or nm; break
    alt = nm[1:].count("#") - nm[1:].count("b")
    oc = (m - alt) // 12 - 1                    # B#3 sounds as C4, Cb4 as B3
    return nm[0], alt, oc


def ok(s, d):
    """Can a note of d 16ths start at 16th s without hiding the beat structure?"""
    if d not in REP or s + d > BAR: return False
    if BAR == 16:
        if d in (7, 14, 24): return False
        if s == 0: return True
        if s == 8: return d <= 8
        if s % 4 == 0: return (d in (1, 2, 3, 4, 6) and (s + d <= 8 or s >= 8)) or (s == 4 and d == 12)
        if s % 2 == 0: return d in (1, 2) or (d in (3, 4, 6) and (s + d <= 8 or s >= 8))
        if s % 4 == 1: return d in (1, 2, 3)
        return d == 1 or (d == 3 and (s + d <= 8 or s >= 8))
    bt = E.BEAT
    if d in (7, 14, 24): return False
    if s % bt == 0: return d <= bt or (d % bt == 0) or s + d == BAR
    return (s // bt) == ((s + d - 1) // bt)


def split(s, d):
    if ok(s, d): return [d]
    for g in ((8, 4, 2, 1) if BAR == 16 else (E.BEAT, 2, 1)):
        b = (s // g + 1) * g
        if s < b < s + d: return split(s, b - s) + split(b, s + d - b)
    return [d]


def syllabic(t):
    if t.startswith("-") and t.endswith("-") and len(t) > 1: return "middle", t.strip("-")
    if t.endswith("-"): return "begin", t[:-1]
    if t.startswith("-"): return "end", t[1:]
    return "single", t


def note_xml(e, key, d, first, last_piece, pid, perc=False, v=None, sym=None):
    """One event piece -> <note> elements. Percussion events hold a tuple of sounds; pitched events hold a MIDI
    number or a tuple of MIDI numbers (a chord); e['slash'] writes one rhythm slash ('x' head for a muted stroke)."""
    x = []
    typ, dots = REP[d]
    tie_stop = (not first) or e["tie_in"]; tie_start = (not last_piece) or e["tie_out"]
    hits = e["midi"] if (perc or isinstance(e["midi"], tuple)) else [e["midi"]]
    slash = bool(e.get("slash")) and not perc
    if slash: hits = hits[:1]
    K = kit(v) if perc else None
    tr = TRANS.get(v, 0)
    for hi, m in enumerate(hits):
        n = ["<note>"]
        if hi: n.append("<chord/>")
        if perc:
            snd = K[m]; st, oc, num, head = snd["step"], snd["octave"], snd["gm"], snd["head"]
            n.append(f"<unpitched><display-step>{st}</display-step><display-octave>{oc}</display-octave></unpitched>")
        elif slash:
            st, oc = slash_pos(v)
            f = fifths(key)      # follow the key signature, or the slash shows an accidental (a natural in Bb)
            alt = 1 if f > 0 and st in "FCGDAEB"[:f] else -1 if f < 0 and st in "BEADGCF"[:-f] else 0
            n.append(f"<pitch><step>{st}</step>{f'<alter>{alt}</alter>' if alt else ''}<octave>{oc}</octave></pitch>")
        else:
            st, alt, oc = spell(m + tr, key, sym, e.get("spell"))
            n.append(f"<pitch><step>{st}</step>{f'<alter>{alt}</alter>' if alt else ''}<octave>{oc}</octave></pitch>")
        n.append(f"<duration>{d}</duration>")
        if not perc:
            if tie_stop: n.append('<tie type="stop"/>')
            if tie_start: n.append('<tie type="start"/>')
        if perc: n.append(f'<instrument id="{pid}-I{num}"/>')
        n.append("<voice>1</voice>")
        n.append(f"<type>{typ}</type>" + "<dot/>" * dots)
        if perc:
            n.append(f"<stem>{snd['stem']}</stem>")
            if snd.get("mark") == "ghost": n.append(f'<notehead parentheses="yes">{head or "normal"}</notehead>')
            elif head: n.append(f"<notehead>{head}</notehead>")
        elif slash:
            n.append(f"<notehead>{'x' if e.get('stroke') == 'x' else 'slash'}</notehead>")
        if v in E.TAB: n.append("<staff>1</staff>")
        nots = []
        if not perc and tie_stop: nots.append('<tied type="stop"/>')
        if not perc and tie_start: nots.append('<tied type="start"/>')
        if first and e.get("art") == "staccato" and not tie_start: nots.append("<articulations><staccato/></articulations>")
        if first and (e.get("art") == "accent" or (perc and snd.get("mark") == "accent")):
            nots.append("<articulations><accent/></articulations>")
        if first and e.get("art") == "tenuto": nots.append("<articulations><tenuto/></articulations>")
        if first and perc and snd.get("mark") == "roll":
            nots.append('<ornaments><tremolo type="single">3</tremolo></ornaments>')
        if first and slash and e.get("show") and e.get("stroke") in ("D", "U", "d", "u"):
            nots.append(f'<technical><{"down" if e["stroke"] in "Dd" else "up"}-bow/></technical>')
        if first and not perc and e.get("stroke") == "A": nots.append('<arpeggiate/>')
        if last_piece and e.get("art") == "fermata": nots.append('<fermata type="upright"/>')
        if nots: n.append("<notations>" + "".join(nots) + "</notations>")
        if first and hi == 0 and e.get("lyr"):
            sy, t = syllabic(e["lyr"])
            n.append(f'<lyric number="1"><syllabic>{sy}</syllabic><text>{escape(t)}</text></lyric>')
        n.append("</note>")
        x.append("".join(n))
    return x


def tab_xml(e, key, d, first, last_piece, sym, pl, nstr, rest=False):
    """One event piece on the TAB staff (staff 2, voice 5): every string of a strum (the top four on an up-stroke,
    'x' heads for a muted chop), single notes; pl = [(string from the lowest, fret), ...] in pitch order."""
    typ, dots = REP[d]
    if rest:
        if d == BAR and first: return [f'<note><rest measure="yes"/><duration>{BAR}</duration><voice>5</voice><staff>2</staff></note>']
        return [f'<note><rest/><duration>{d}</duration><voice>5</voice><type>{typ}</type>' + "<dot/>" * dots
                + '<staff>2</staff></note>']
    ps = sorted(e["midi"]) if isinstance(e["midi"], tuple) else [e["midi"]]
    if e.get("slash") and e.get("stroke") in ("U", "u"): ps = ps[-4:]
    tie_stop = (not first) or e["tie_in"]; tie_start = (not last_piece) or e["tie_out"]
    out = []
    for hi, m in enumerate(ps):
        st, alt, oc = spell(m, key, sym, e.get("spell"))
        n = ["<note>" + ("<chord/>" if hi else "")]
        n.append(f"<pitch><step>{st}</step>{f'<alter>{alt}</alter>' if alt else ''}<octave>{oc}</octave></pitch>")
        n.append(f"<duration>{d}</duration>")
        if tie_stop: n.append('<tie type="stop"/>')
        if tie_start: n.append('<tie type="start"/>')
        n.append("<voice>5</voice>" + f"<type>{typ}</type>" + "<dot/>" * dots)
        if e.get("stroke") == "x": n.append("<notehead>x</notehead>")
        n.append("<staff>2</staff>")
        nots = []
        if tie_stop: nots.append('<tied type="stop"/>')
        if tie_start: nots.append('<tied type="start"/>')
        if first and hi == 0 and e.get("art") in ("staccato", "accent", "tenuto") and not (tie_start and e["art"] == "staccato"):
            nots.append(f"<articulations><{e['art']}/></articulations>")
        tech = []
        if first and hi == 0 and e.get("slash") and e.get("show") and e.get("stroke") in ("D", "U", "d", "u"):
            tech.append(f'<{"down" if e["stroke"] in "Dd" else "up"}-bow/>')
        if pl: tech.append(f"<string>{nstr - pl[hi][0]}</string><fret>{pl[hi][1]}</fret>")
        if tech: nots.append("<technical>" + "".join(tech) + "</technical>")
        if first and hi == 0 and e.get("stroke") == "A": nots.append("<arpeggiate/>")
        if last_piece and hi == 0 and e.get("art") == "fermata": nots.append('<fermata type="upright"/>')
        if nots: n.append("<notations>" + "".join(nots) + "</notations>")
        n.append("</note>")
        out.append("".join(n))
    return out


def harmony_xml(sym, offset):
    s, bass = (sym.split("/") + [None])[:2]
    r = s[:2] if len(s) > 1 and s[1] in "#b" else s[:1]
    q = s[len(r):]
    kind, text = KIND[q]

    def rt(tag, n):
        alt = {"#": 1, "b": -1}.get(n[1:], 0)
        return f"<{tag}-step>{n[0]}</{tag}-step>" + (f"<{tag}-alter>{alt}</{tag}-alter>" if alt else "")
    x = "<harmony>" + (f"<offset>{offset}</offset>" if offset else "")
    x += f"<root>{rt('root', r)}</root><kind text=\"{text}\">{kind}</kind>"
    if bass: x += f"<bass>{rt('bass', bass)}</bass>"
    if q in ("add9", "madd9"):
        x += "<degree><degree-value>9</degree-value><degree-alter>0</degree-alter><degree-type>add</degree-type></degree>"
    return x + "</harmony>"


def direction(inner, place="above", sound=""):
    return f'<direction placement="{place}"><direction-type>{inner}</direction-type>{sound}</direction>'


# ---------------------------------------------------------------- MusicXML
pl = ['<part-list>']
for i, v in enumerate(VOICES, 1):
    name, ab, clef, rng, pan, vol = INFO[v]
    pl.append(f'<score-part id="P{i}"><part-name>{escape(name)}</part-name><part-abbreviation>{escape(ab)}</part-abbreviation>')
    if PERC[v]:
        sounds = {}
        for k, snd in kit(v).items(): sounds.setdefault(snd["gm"], snd.get("label", k) if v != "VP" else k)
        for num, lab in sounds.items():
            pl.append(f'<score-instrument id="P{i}-I{num}"><instrument-name>{escape(lab)}</instrument-name></score-instrument>')
        for num in sounds:
            pl.append(f'<midi-instrument id="P{i}-I{num}"><midi-channel>10</midi-channel><midi-unpitched>{num + 1}'
                      f'</midi-unpitched><volume>{vol}</volume></midi-instrument>')
    else:
        ch = i if i < 10 else i + 1  # skip channel 10 (drums)
        snd = E.SOUND.get(v, "keyboard.piano"); iname = "Piano" if v not in E.SOUND else name
        pl.append(f'<score-instrument id="P{i}-I1"><instrument-name>{escape(iname)}</instrument-name>'
                  f'<instrument-sound>{snd}</instrument-sound></score-instrument>')
        pl.append(f'<midi-instrument id="P{i}-I1"><midi-channel>{min(ch, 16)}</midi-channel>'
                  f'<midi-program>{E.PROGRAM.get(v, 0) + 1}</midi-program>'
                  f'<volume>{vol}</volume><pan>{pan}</pan></midi-instrument>')
    pl.append('</score-part>')
pl.append('</part-list>')

TOTAL = sum(s["nbars"] for s in SECS)
parts = []
events_out = {v: [] for v in VOICES}
VEL = dict(pp=40, p=50, mp=62, mf=74, f=88, ff=100)
for i, v in enumerate(VOICES, 1):
    name, ab, clef, rng, pan, vol = INFO[v]
    perc = PERC[v]; pid = f"P{i}"
    px = [f'<part id="{pid}">']
    m = 0; cur_key = None; dyn = "mf"
    for s in SECS:
        for bi in range(s["nbars"]):
            m += 1
            mx = [f'<measure number="{m}">']
            if m > 1 and (m - 1) % a.bars_per_system == 0 and m != TOTAL: mx.append('<print new-system="yes"/>')
            attrs = []
            if m == 1: attrs.append("<divisions>4</divisions>")
            if bi == 0 and s["key"] != cur_key and not perc:
                mode = "<mode>minor</mode>" if s["key"].endswith("m") else ""
                attrs.append(f"<key><fifths>{fifths(s['key'])}</fifths>{mode}</key>")
            if m == 1:
                attrs.append(f"<time><beats>{E.METER[0]}</beats><beat-type>{E.METER[1]}</beat-type></time>")
                sign, line, octv = clef
                if v in E.TAB:
                    octv = octv - E.TRANSPOSE.get(v, 0) // 12
                    attrs.append("<staves>2</staves>")
                cnum = ' number="1"' if v in E.TAB else ""
                attrs.append(f"<clef{cnum}><sign>{sign}</sign>" + (f"<line>{line}</line>" if sign != "percussion" else "")
                             + (f"<clef-octave-change>{octv}</clef-octave-change>" if octv else "") + "</clef>")
                if v in E.TAB:
                    tuning = E.TAB[v][0]
                    attrs.append('<clef number="2"><sign>TAB</sign><line>5</line></clef>')
                    attrs.append(f'<staff-details number="2"><staff-lines>{len(tuning)}</staff-lines>' + "".join(
                        f'<staff-tuning line="{j + 1}"><tuning-step>{E.NAMES[o % 12][0]}</tuning-step>'
                        + (f"<tuning-alter>{1 if '#' in E.NAMES[o % 12] else -1}</tuning-alter>" if len(E.NAMES[o % 12]) > 1 else "")
                        + f"<tuning-octave>{o // 12 - 1}</tuning-octave></staff-tuning>" for j, o in enumerate(tuning))
                        + "</staff-details>")
                if TRANS.get(v):
                    k = TRANS[v]
                    assert k % 12 == 0, f"{v}: only octave transpositions are supported"
                    attrs.append(f"<transpose><diatonic>0</diatonic><chromatic>0</chromatic>"
                                 f"<octave-change>{-k // 12}</octave-change></transpose>")
            if bi == 0: cur_key = s["key"]
            if attrs: mx.append("<attributes>" + "".join(attrs) + "</attributes>")
            if i == 1 and bi == 0:
                mx.append(direction(f"<rehearsal>{escape(s['name'])}</rehearsal>"))
                if s.get("tempo"):
                    t = s["tempo"]
                    if E.BEAT == 6:   # compound meter: the beat is a dotted quarter; <sound tempo> counts quarters
                        mx.append(direction(f"<metronome><beat-unit>quarter</beat-unit><beat-unit-dot/><per-minute>{t}"
                                            f"</per-minute></metronome>", sound=f'<sound tempo="{t * 1.5:g}"/>'))
                    else:
                        mx.append(direction(f"<metronome><beat-unit>quarter</beat-unit><per-minute>{t}</per-minute></metronome>",
                                            sound=f'<sound tempo="{t}"/>'))
                if s.get("note"):
                    mx.append(direction(f'<words font-style="italic">{escape(s["note"])}</words>'))
            if (v in E.CHORD_PARTS) if E.CHORD_PARTS else i == 1:
                row = s["chords"][bi]; prev = None
                for k, sym in enumerate(row):
                    if sym != prev: mx.append(harmony_xml(sym, k * BAR // len(row)))
                    prev = sym
            if (v, bi) in s["dyn"]:
                dyn = s["dyn"][(v, bi)]
                mx.append(direction(f"<dynamics><{dyn}/></dynamics>", "below"))
            if (v, bi) in s["text"]:
                mx.append(direction(f'<words font-style="italic">{escape(s["text"][(v, bi)])}</words>'))
            bar = s["parts"][v][bi]
            tpos = 0; tab = []; si = SECS.index(s)
            row = s["chords"][bi]
            for ei, e in enumerate(bar):
                if v in E.TAB:
                    sym_t = row[min(len(row) - 1, e["start"] * len(row) // BAR)]
                    if e["midi"] is None:
                        if e["dur"] == BAR: tab += tab_xml(e, s["key"], BAR, True, True, sym_t, None, 0, rest=True)
                        else:
                            for d in split(e["start"], e["dur"]): tab += tab_xml(e, s["key"], d, False, False, sym_t, None, 0, rest=True)
                    else:
                        pcs = split(e["start"], e["dur"])
                        for j, d in enumerate(pcs):
                            tab += tab_xml(e, s["key"], d, j == 0, j == len(pcs) - 1, sym_t, TABF.get((v, si, bi, ei)),
                                           len(E.TAB[v][0]))
                assert e["start"] == tpos, f"{v} {s['name']} bar {bi}: event at {e['start']}, expected {tpos}: {bar}"
                tpos += e["dur"]
                if e["midi"] is None:
                    if e["dur"] == BAR:
                        mx.append(f'<note><rest measure="yes"/><duration>{BAR}</duration><voice>1</voice></note>')
                    else:
                        for d in split(e["start"], e["dur"]):
                            typ, dots = REP[d]
                            mx.append(f'<note><rest/><duration>{d}</duration><voice>1</voice><type>{typ}</type>'
                                      + "<dot/>" * dots + "</note>")
                    continue
                pieces = split(e["start"], e["dur"])
                for j, d in enumerate(pieces):
                    row = s["chords"][bi]; sym = row[min(len(row) - 1, e["start"] * len(row) // BAR)]
                    mx += note_xml(e, s["key"], d, j == 0, j == len(pieces) - 1, pid, perc, v, sym)
                lead = v == "L" or s.get("lead", {}).get(bi, (None,))[0] == v
                vel = VEL[dyn] + (8 if lead else 0)
                if "vel" in e: vel = max(1, min(127, int(round(vel * e["vel"]))))
                rec = s["first"] + bi if s["first"] is not None else None
                x = {k: e[k] for k in ("slash", "stroke") if e.get(k)}
                if e.get("art") == "fermata": x["art"] = "fermata"
                events_out[v].append([rec, e["start"], e["dur"], list(e["midi"]) if isinstance(e["midi"], tuple)
                                      else e["midi"], vel, e["tie_in"], m, e.get("lyr", "")] + ([x] if x else []))
            assert tpos == BAR, f"{v} {s['name']} bar {bi}: {tpos} sixteenths, expected {BAR}"
            if tab: mx += [f"<backup><duration>{BAR}</duration></backup>"] + tab
            if s is SECS[-1] and bi == s["nbars"] - 1:
                mx.append('<barline location="right"><bar-style>light-heavy</bar-style></barline>')
            mx.append("</measure>")
            px += mx
    px.append("</part>")
    parts.append("\n".join(px))

M = E.META
head = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 '
        'Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n<score-partwise version="4.0">'
        f'<work><work-title>{escape(M["title"])}</work-title></work>'
        f'<identification><creator type="composer">{escape(M["composer"])}</creator>'
        f'<creator type="arranger">{escape(M["arranger"])}</creator></identification>'
        f'<defaults><scaling><millimeters>{a.scaling}</millimeters><tenths>40</tenths></scaling>'
        f'<page-layout><page-height>{round(297 * 40 / a.scaling)}</page-height><page-width>{round(210 * 40 / a.scaling)}</page-width>'
        '<page-margins type="both"><left-margin>70</left-margin><right-margin>70</right-margin>'
        '<top-margin>70</top-margin><bottom-margin>70</bottom-margin></page-margins></page-layout>'
        '<system-layout><system-distance>90</system-distance><top-system-distance>110</top-system-distance></system-layout>'
        f'<staff-layout><staff-distance>{a.staff_distance}</staff-distance></staff-layout></defaults>')
if M.get("subtitle"):   # with any credit present MuseScore takes the whole title block from the credits
    head += (f'<credit page="1"><credit-type>title</credit-type><credit-words justify="center" valign="top" '
             f'default-x="{round(105 * 40 / a.scaling)}" default-y="{round(297 * 40 / a.scaling) - 85}" font-size="22">{escape(M["title"])}</credit-words></credit>'
             f'<credit page="1"><credit-type>subtitle</credit-type><credit-words justify="center" valign="top" '
             f'default-x="{round(105 * 40 / a.scaling)}" default-y="{round(297 * 40 / a.scaling) - 155}" font-size="12">{escape(M["subtitle"])}</credit-words></credit>')
    W_, H_ = round(210 * 40 / a.scaling), round(297 * 40 / a.scaling)
    for typ, txt, x, just in (("composer", M["composer"], W_ - 70, "right"), ("lyricist", M["arranger"], 70, "left")):
        if txt:   # MuseScore's title frame has a right (composer) and a left (lyricist) slot: the arranger goes left
            head += (f'<credit page="1"><credit-type>{typ}</credit-type><credit-words justify="{just}" valign="top" '
                     f'default-x="{x}" default-y="{H_ - 185}" font-size="9">{escape(txt)}</credit-words></credit>')
xml = head + "\n".join(pl) + "\n" + "\n".join(parts) + "</score-partwise>\n"
fx = f"{OUT}/{BASE}.musicxml"
open(fx, "w").write(xml)
# ---------------------------------------------------------------- events.json: what render.py / qa.py need
sections = []; m0 = 1
for s in SECS:
    sections.append(dict(name=s["name"], measure=m0, nbars=s["nbars"], first=s["first"], key=s["key"], tempo=s.get("tempo"),
                         chords=s["chords"], warp=s.get("warp"), style=s.get("style"), cards=s.get("cards"),
                         lead={str(bi): list(x) for bi, x in s.get("lead", {}).items()}))
    m0 += s["nbars"]


def played_chords(v, check):
    """Every chord slot in a measure where part v plays -> [measure, symbol, playable, exact]."""
    out = []; m0 = 0
    for s in SECS:
        for bi in range(s["nbars"]):
            if any(e["midi"] is not None for e in s["parts"][v][bi]):
                for sym in dict.fromkeys(s["chords"][bi]):
                    r = check(sym); out.append([m0 + bi + 1, sym] + (list(r) if r else [None, False]))
        m0 += s["nbars"]
    return out


json.dump(dict(meta=dict(voices=VOICES, ranges={v: E.RANGE.get(v) for v in VOICES}, bar=BAR, meter=list(E.METER),
                         work=E.WORK, title=M["title"], name=BASE, info={v: INFO[v][:2] for v in VOICES},
                         pan={v: INFO[v][4] for v in VOICES}, vol={v: INFO[v][5] for v in VOICES}, beat=E.BEAT,
                         sections=sections,
                         kinds={v: E.kind(v) for v in VOICES},
                         programs={v: E.PROGRAM[v] for v in VOICES if v in E.PROGRAM},
                         kits={v: {k: [snd["gm"], snd.get("vel", 1.0), snd.get("label", k)] for k, snd in kit(v).items()}
                               for v in VOICES if PERC[v]},
                         pitchset={v: sorted(E.PITCHSET[v]) for v in VOICES if v in E.PITCHSET},
                         chordset={v: played_chords(v, E.CHORDSET[v]) for v in VOICES if v in E.CHORDSET},
                         players={p: [v for v in vs if v in VOICES] for p, vs in E.PLAYERS.items()},
                         rec_shift=M.get("rec_shift", 0), score_render=bool(M.get("score_render"))),
               events=events_out), open(f"{OUT}/events.json", "w"))
print(f"measures: {m}  ->  {fx}")


# ---------------------------------------------------------------- MuseScore
def mscore_cmd():
    if os.environ.get("ACAP_MSCORE"): return shlex.split(os.environ["ACAP_MSCORE"])
    for c in ("mscore", "mscore4", "musescore4", "musescore", "MuseScore4", "mscore4portable"):
        if shutil.which(c): return [shutil.which(c)]
    for c in glob.glob(os.path.expanduser("~/Applications/MuseScore*.AppImage")) + glob.glob("/Applications/MuseScore 4.app/Contents/MacOS/mscore"):
        return [c]
    return None


if a.no_mscore: sys.exit(0)
MS = mscore_cmd()
if not MS:
    print("MuseScore not found (set ACAP_MSCORE): only the MusicXML was written"); sys.exit(0)
env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
ab = os.path.abspath(OUT)
mz = f"{ab}/{BASE}.mscz"
r = subprocess.run(MS + ["-o", mz, f"{ab}/{BASE}.musicxml"], env=env, capture_output=True, text=True)
if not os.path.exists(mz): raise SystemExit(f"MuseScore import failed:\n{r.stderr[-2000:]}")
tmp = f"{ab}/.mscz_tmp"; shutil.rmtree(tmp, ignore_errors=True)
with zipfile.ZipFile(mz) as z: z.extractall(tmp)
mscx = [f for f in os.listdir(tmp) if f.endswith(".mscx")][0]
t = open(f"{tmp}/{mscx}").read()
n_h = t.count("<Harmony>")
if not a.play_chords: t = t.replace("<Harmony>", "<Harmony>\n            <play>0</play>")
# rhythm slashes are notation only: silence them in MuseScore's playback
t = re.sub(r"<Note>((?:(?!</Note>).)*?<head>slash</head>)", r"<Note>\n            <play>0</play>\1", t, flags=re.S)
# tablature staves show the notation staff's notes again: silence them so the part does not play twice
n_staff, tab_ids = 0, set()
for part in re.findall(r"<Part\b.*?</Part>", t, flags=re.S):
    for st in re.findall(r"<Staff\b.*?</Staff>", part, flags=re.S):
        n_staff += 1
        if 'group="tablature"' in st: tab_ids.add(str(n_staff))
if tab_ids:
    cuts = [(mm.start(), mm.group(1)) for mm in re.finditer(r'<Staff id="(\d+)">', t)] + [(len(t), None)]
    out = [t[:cuts[0][0]]]
    for (p0, sid), (p1, _) in zip(cuts, cuts[1:]):
        seg = t[p0:p1]
        out.append(seg.replace("<Note>", "<Note>\n            <play>0</play>") if sid in tab_ids else seg)
    t = "".join(out)
open(f"{tmp}/{mscx}", "w").write(t)
sp = f"{tmp}/score_style.mss"
if os.path.exists(sp):
    st = open(sp).read()
    for k, val in (("lyricsOddFontSize", "8.5"), ("lyricsEvenFontSize", "8.5"), ("lyricsMinDistance", "0.6")):
        st = re.sub(f"<{k}>[^<]*</{k}>", f"<{k}>{val}</{k}>", st)
    open(sp, "w").write(st)
os.remove(mz)
with zipfile.ZipFile(mz, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(tmp):
        for f in files:
            p = os.path.join(root, f); z.write(p, os.path.relpath(p, tmp))
shutil.rmtree(tmp)
for ext in ("pdf", "mid"):
    subprocess.run(MS + ["-o", f"{ab}/{BASE}.{ext}", mz], env=env, capture_output=True)
print(f"mscz/pdf/mid written; chord symbols {'playing' if a.play_chords else 'muted'}: {n_h}")
if a.png and shutil.which("pdftoppm"):
    os.makedirs(f"{ab}/png", exist_ok=True)
    for f in glob.glob(f"{ab}/png/page-*.png"): os.remove(f)
    subprocess.run(["pdftoppm", "-r", "50", "-png", f"{ab}/{BASE}.pdf", f"{ab}/png/page"], check=True)
    print("page previews:", sorted(os.listdir(f"{ab}/png")))
