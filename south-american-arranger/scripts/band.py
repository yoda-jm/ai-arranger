"""Band layer of the south-american-arranger skill, on top of arranger-core's engine (tokens, chords, voicings,
sections, warps). An arrangement file does:

    from band import *
    setup(title=..., meter=(12, 8), rec_shift=-1)           # the band's parts, kits, renders and checks
    s = section("Verse 1", "Dm", 4, CHORDS, S.V1, S.V1_LYR, warp="swing", tempo=72, style="landó")
    lead(s, "W1")                                           # the tune in a singer's part, remembered as the lead
    strum(s, "GTR", "D.u D.u D.u D.u")                      # rhythm slashes, voiced per instrument for the renders
    arp(s, "GTR", "1.3.2.4.3.2.")                           # fingerpicked notes of a chord voicing (1 = bass)
    bassline(s, "1....5 1....5")                            # degrees of the chord sounding at each attack
    perc(s, "P1", cajon="B..TS. B..TS.")                    # percussion lanes, one per instrument
    hang_arp(s, "0.3.4.0.3.4.")                             # hang notes taken from the chord tones it has (0 = ding)

Patterns: one character per `unit` 16ths (default 8ths in 6/8 and 12/8, 16ths in 2/4 and 4/4); spaces and '|' are
ignored; a short pattern repeats to fill the bar, a long one spans several bars. '.' = rest (strums and arpeggios ring
through it unless ring=False), '-' = hold. Every writer takes local= (section-bar indices), text= (an italic direction
at the first bar) and dyn=. The patterns are also kept on the section for the groove cards (sheets.py).
Full reference: references/band.md.
"""
import os, re, sys


def _core():
    here = os.path.dirname(os.path.realpath(__file__))
    for c in (os.environ.get("ARRANGER_CORE"), os.path.join(here, "..", "..", "arranger-core", "scripts"),
              os.path.expanduser("~/.claude/skills/arranger-core/scripts")):
        if c and os.path.exists(os.path.join(c, "engine.py")): return os.path.abspath(c)
    raise SystemExit("arranger-core/scripts not found: set ARRANGER_CORE")


if _core() not in sys.path: sys.path.insert(0, _core())
import engine as E
import fretboard
from engine import *  # noqa: F401,F403  (section, parse_line, harm, block, put_*, shift, tr_tokens, ...)

# ---------------------------------------------------------------- the band
# key -> (staff name, abbreviation, clef (sign, line, octave change), sounding range, pan, volume)
BAND = {
    "W1": ("Mezzo 1", "Mz1", ("G", 2, 0), (55, 77), -20, 100),        # the band: 2 mezzos, 3 baritones
    "W2": ("Mezzo 2", "Mz2", ("G", 2, 0), (55, 76), -35, 85),
    "M1": ("Baritone 1", "Bar1", ("G", 2, -1), (43, 67), 20, 100),
    "M2": ("Baritone 2", "Bar2", ("G", 2, -1), (43, 66), 35, 85),
    "M3": ("Baritone 3", "Bar3", ("F", 4, 0), (41, 64), 10, 85),
    "GTR": ("Guitar", "Gtr", ("G", 2, 0), (40, 83), 30, 100),     # written an octave up (TRANSPOSE)
    "UKE": ("Ukulele", "Uke", ("G", 2, 0), (60, 81), 30, 78),
    "AH": ("Autoharp", "AHp", ("G", 2, 0), (41, 84), -30, 72),
    "HANG": ("Hang (D Kurd)", "Hang", ("G", 2, -1), (50, 69), -10, 85),
    "BASS": ("Electric Bass", "Bs", ("F", 4, 0), (28, 55), 0, 100),   # 8vb; the name makes MuseScore pick a bass guitar, not a singer
    "P1": ("Percussion 1", "Perc 1", ("percussion", 2, 0), None, -15, 95),
    "P2": ("Percussion 2", "Perc 2", ("percussion", 2, 0), None, 15, 90),
}
PARTS = ["W1", "W2", "M1", "M2", "M3", "GTR", "AH", "HANG", "BASS", "P1", "P2"]
INSTRUMENTS = {"GTR", "UKE", "AH", "HANG", "BASS"}
# renders (GM, 0-based): the leads on clear melody timbres, coros on "voice oohs"
PROGRAMS = {"W1": 73, "W2": 53, "M1": 71, "M2": 53, "M3": 53, "GTR": 25, "UKE": 24, "AH": 46, "HANG": 114, "BASS": 33}
SOUNDS = {"GTR": "pluck.guitar.steel-string", "UKE": "pluck.ukulele", "AH": "pluck.autoharp",
          "HANG": "metal.steel-drums", "BASS": "pluck.bass.electric"}
TRANSPOSE = {"GTR": 12, "BASS": 12}
TABS = {"GTR": "guitar", "BASS": "bass", "UKE": "ukulele"}    # parts that get a tablature staff (fretboard.TUNINGS)
LAST0 = dict(W1=67, W2=64, M1=57, M2=55, M3=50, BASS=40)
# player -> the parts one person plays (one at a time). Who sings which vocal part is decided per song (README).
PLAYERS = {"percussionist": ["P1", "HANG"], "small drums": ["P2"], "autoharp": ["AH"], "guitar": ["GTR", "UKE"],
           "bass": ["BASS"]}

# percussion kits: sound -> staff position, GM note for the renders, notehead, stem, mark, velocity scale, label
def _s(step, octave, gm, head=None, stem="up", mark=None, vel=1.0, label=""):
    return dict(step=step, octave=octave, gm=gm, head=head, stem=stem, mark=mark, vel=vel, label=label)


KITS = {
    "P1": {
        "cB": _s("F", 4, 35, stem="down", label="cajón bass (grave)"),
        "cT": _s("C", 5, 62, vel=0.9, label="cajón tone (agudo)"),
        "cS": _s("C", 5, 38, "x", vel=0.9, label="cajón slap"),
        "cg": _s("C", 5, 62, mark="ghost", vel=0.35, label="cajón ghost"),
        "gL": _s("G", 5, 74, "x", vel=0.8, label="güiro long"),
        "gs": _s("G", 5, 73, "x", vel=0.7, label="güiro short"),
        "gt": _s("G", 5, 76, "triangle", vel=0.6, label="güiro tap"),
        "shX": _s("E", 5, 70, "x", mark="accent", vel=0.9, label="shaker accent"),
        "shx": _s("E", 5, 70, "x", vel=0.55, label="shaker soft"),
        "sX": _s("C", 5, 40, mark="accent", vel=1.0, label="snare accent"),
        "sx": _s("C", 5, 40, vel=0.75, label="snare normal"),
        "sg": _s("C", 5, 40, mark="ghost", vel=0.3, label="snare ghost"),
        "sR": _s("C", 5, 37, "x", vel=0.8, label="snare rim"),
        "sr": _s("C", 5, 40, mark="roll", vel=0.6, label="snare roll"),
        "sK": _s("D", 5, 37, "x", mark="accent", vel=0.85, label="snare shell, stick on the side (accent)"),
        "sk": _s("D", 5, 37, "x", vel=0.5, label="snare shell, stick on the side"),
        "cbO": _s("A", 5, 56, "triangle", mark="accent", vel=0.85, label="snare-stand cowbell, other stick (or a jam block)"),
        "cbo": _s("A", 5, 56, "triangle", vel=0.45, label="snare-stand cowbell, soft"),
    },
    "P2": {
        "dB": _s("F", 4, 64, stem="down", label="djembé bass"),
        "dT": _s("A", 4, 63, vel=0.85, label="djembé tone"),
        "dS": _s("C", 5, 62, vel=0.95, label="djembé slap"),
        "dg": _s("A", 4, 63, mark="ghost", vel=0.3, label="djembé ghost"),
        "bM": _s("D", 5, 60, vel=0.85, label="bongos macho"),
        "bm": _s("D", 5, 60, mark="ghost", vel=0.35, label="bongos macho-finger"),
        "bH": _s("B", 4, 61, vel=0.85, label="bongos hembra"),
        "bS": _s("D", 5, 60, "x", mark="accent", vel=1.0, label="bongos slap"),
        "bp": _s("B", 4, 61, mark="ghost", vel=0.3, label="bongos thumb"),
        "kH": _s("E", 5, 78, "diamond", vel=0.8, label="cuíca high"),
        "kL": _s("B", 4, 79, "diamond", vel=0.8, label="cuíca low"),
        "km": _s("E", 5, 78, "diamond", mark="ghost", vel=0.4, label="cuíca muted"),
        "shX": _s("G", 5, 70, "x", mark="accent", vel=0.9, label="shaker accent"),
        "shx": _s("G", 5, 70, "x", vel=0.55, label="shaker soft"),
    },
}
INSTR = {"cajon": "c", "guiro": "g", "shaker": "sh", "snare": "s", "djembe": "d", "bongos": "b", "cuica": "k",
         "cowbell": "cb"}

# ---------------------------------------------------------------- fixed-pitch instruments
HANG_NOTES = [50, 57, 58, 60, 62, 64, 65, 67, 69]       # D Kurd 9: D3 (ding) | A3 Bb3 C4 D4 E4 F4 G4 A4
# Oscar Schmidt 21-chord chromatic autoharp, standard bars (rows: Eb Bb F C G D A | F7 C7 G7 D7 A7 E7 B7 |
# Ab Bb7 Cm Gm Dm Am Em): no E / B / F# major, no Bm F#m C#m Fm, no maj7 or m7
AUTOHARP = ["Eb", "Bb", "F", "C", "G", "D", "A", "Ab",
            "F7", "C7", "G7", "D7", "A7", "E7", "B7", "Bb7",
            "Cm", "Gm", "Dm", "Am", "Em"]
_REDUCE = {"": "", "6": "", "add9": "", "maj7": "", "maj9": "", "sus2": "", "sus": "", "sus4": "",
           "m": "m", "m7": "m", "m9": "m", "madd9": "m", "m6": "m",
           "7": "7", "9": "7", "7sus": "7", "7sus4": "7"}
_FLATS = "C Db D Eb E F Gb G Ab A Bb B".split()
_SHARPS = "C C# D D# E F F# G G# A A# B".split()


def autoharp_chord(sym, bars=None):
    """The autoharp bar for a chord symbol -> (bar, exact) or None. Colours are dropped (maj7/add9/6/sus -> triad,
    m7/m9 -> minor, 9/7sus -> 7); a missing 7th bar falls back to the triad and vice versa (exact=False)."""
    bars = bars or AUTOHARP
    c = chord(sym); q = c["q"]
    if q not in _REDUCE: return None
    rq = _REDUCE[q]
    names = {_FLATS[c["root"]], _SHARPS[c["root"]]}
    for want in (rq,) + {"7": ("",), "": ("7",), "m": ()}[rq]:
        for n in names:
            if n + want in bars: return n + want, (want == q and "/" not in sym)
    return None


# ---------------------------------------------------------------- setup
def setup(work=None, parts=None, title=None, composer=None, arranger=None, subtitle=None, meter=(12, 8), ranges=None,
          name=None, rec_shift=0, last=None, tab=True):
    """The band score: parts (default PARTS; use "UKE" instead of "GTR" for ukulele songs; leave out "AH" when the
    autoharp sits out), meter, ranges overrides, rec_shift = semitones from the recording's key to the arrangement's
    (renders and qa.py compare in the record's key), tab = add a tablature staff under guitar, ukulele and bass."""
    E.VOICE_INFO.update(BAND)
    E.RANGE.update({k: v[3] for k, v in BAND.items() if v[3]})
    parts = list(parts or PARTS)
    l0 = dict(LAST0); l0.update(last or {})
    E.setup(work=work, voices=parts, title=title, composer=composer, arranger=arranger or "band arrangement",
            subtitle=subtitle, meter=meter, ranges=ranges, name=name, last=l0)
    E.KITS.clear(); E.KITS.update({k: v for k, v in KITS.items() if k in parts})
    E.PROGRAM.update({k: v for k, v in PROGRAMS.items() if k in parts})
    E.SOUND.update({k: v for k, v in SOUNDS.items() if k in parts})
    E.TRANSPOSE.update({k: v for k, v in TRANSPOSE.items() if k in parts})
    E.KIND.update({k: "pitched" for k in INSTRUMENTS if k in parts})
    E.CHORD_PARTS[:] = [p for p in ("GTR", "UKE", "AH", "BASS") if p in parts] or parts[:1]
    if "HANG" in parts: E.PITCHSET["HANG"] = set(HANG_NOTES)
    if "AH" in parts: E.CHORDSET["AH"] = autoharp_chord
    E.PLAYERS.clear(); E.PLAYERS.update({p: [v for v in vs if v in parts] for p, vs in PLAYERS.items()})
    E.TAB.clear()
    if tab: E.TAB.update({p: (fretboard.TUNINGS[n], fretboard.MAX_FRET[n]) for p, n in TABS.items() if p in parts})
    E.META["score_render"] = True; E.META["rec_shift"] = rec_shift


# ---------------------------------------------------------------- lanes
def _unit(unit): return unit or (2 if E.BEAT == 6 else 1)


def _cells(pattern, unit, nbars):
    """Per section bar: [(16th, char), ...] for every cell of the pattern (repeated / spanning bars)."""
    p = re.sub(r"[\s|]", "", pattern); step = _unit(unit); span = len(p) * step
    if not (E.BAR % span == 0 or span % E.BAR == 0):
        raise ValueError(f"pattern {pattern!r}: {len(p)} cells x {step} 16ths = {span}, not a divisor or multiple of "
                         f"the bar ({E.BAR} 16ths)")
    out = []
    for bi in range(nbars):
        row = []
        if span <= E.BAR:
            for r in range(E.BAR // span):
                row += [(r * span + k * step, ch) for k, ch in enumerate(p)]
        else:
            off = (bi % (span // E.BAR)) * E.BAR
            row = [(k * step - off, ch) for k, ch in enumerate(p) if 0 <= k * step - off < E.BAR]
        out.append(row)
    return out


def _card(sec, part, kind, local, text, **pat):
    sec.setdefault("cards", []).append(dict(part=part, kind=kind, bars=_local(sec, local), text=text,
                                            unit=pat.pop("unit", None) or _unit(None), patterns=pat))


def _local(sec, local): return list(range(sec["nbars"])) if local is None else list(local)


def _pitched(sec, cells, pick, ring):
    """Cells -> event bars. pick(bar, 16th, char) -> (midi or tuple, extras dict) or None for a rest."""
    bars = []
    for bi, row in enumerate(cells):
        evs = []                                   # [start, end, midi, extras]
        for t, ch in row:
            if ch == "-" or (ring and ch == "."):
                if t == 0 and ch == "-" and bars and bars[-1][-1]["midi"] is not None:
                    p = bars[-1][-1]; p["tie_out"] = True
                    evs.append([0, None, p["midi"], {k: p[k] for k in ("slash", "stroke", "vel") if k in p}, True])
                continue
            if evs and evs[-1][1] is None: evs[-1][1] = t
            if ch == ".": continue
            r = pick(bi, t, ch)
            if r is not None: evs.append([t, None, r[0], r[1], False])
        if evs and evs[-1][1] is None: evs[-1][1] = E.BAR
        b, cur = [], 0
        for s, e_, m, x, tie in evs:
            if s > cur: b.append(ev(cur, s - cur))
            d = ev(s, e_ - s, m, "", tie_in=tie); d.update(x); b.append(d); cur = e_
        if cur < E.BAR: b.append(ev(cur, E.BAR - cur))
        bars.append(b)
    return bars


def _put(sec, part, bars, local, text, dyn):
    idx = _local(sec, local)
    for e in bars[idx[0]]:
        if e.get("slash"): e["show"] = True
    put(sec, part, bars, idx, text, dyn)


# ---------------------------------------------------------------- chord voicings for the renders
_GTR_FRETS = {}     # guitar voicing (pitches) -> its shape (frets per string)


def voicing(part, sym, prev=None):
    """Sounding notes for a chord on an instrument (for the renders and arpeggios), low to high."""
    if part == "AH":
        r = autoharp_chord(sym); sym = r[0] if r else sym
    c = chord(sym); tones = c["tones"]
    if part == "GTR":     # a shape a guitarist plays (open chord or barre), near the previous one on the neck
        f = fretboard.shape(sym, fretboard.TUNINGS["guitar"], _GTR_FRETS.get(prev))
        v = fretboard.pitches(f); _GTR_FRETS[v] = f
        return v
    if part == "UKE":
        start = min(q for q in range(60, 72) if q % 12 in tones)
        out = [start]
        while len(out) < 4: out.append(next(q for q in range(out[-1] + 1, out[-1] + 13) if q % 12 in tones))
        return tuple(out)
    if part == "AH":
        return tuple(q for q in range(53, 84) if q % 12 in tones)
    lo, hi = E.RANGE.get(part, (48, 72))
    return tuple(q for q in range(lo, hi + 1) if q % 12 in tones)[:5]


VEL = {"D": 1.0, "U": 0.8, "d": 0.65, "u": 0.55, "x": 0.5, "A": 0.9}


def strum(sec, part, pattern, local=None, text=None, dyn=None, unit=None, ring=True):
    """Strummed chords as rhythm slashes: D down, U up, d/u soft, x muted chop, A rolled; the chord is the one
    sounding at each attack (the autoharp plays its nearest bar)."""
    prev = [None]

    def pick(bi, t, ch):
        if ch not in VEL: raise ValueError(f"strum {pattern!r}: {ch!r} is not one of D U d u x A . -")
        v = voicing(part, chord_at(sec, bi, t)["sym"], prev[0]); prev[0] = v
        return v, dict(slash=True, stroke=ch, vel=VEL[ch])
    _put(sec, part, _pitched(sec, _cells(pattern, unit, sec["nbars"]), pick, ring), local, text, dyn)
    _card(sec, part, "strum", local, text, strum=pattern, unit=unit)


def arp(sec, part, pattern, local=None, text=None, dyn=None, unit=None, ring=True, rng=None):
    """Fingerpicked notes: digit k = k-th note (from the bottom) of the instrument's voicing of the chord sounding
    at that moment (1 = bass); 'b' = the chord's bass note an octave lower when it fits the range."""
    prev = [None]; lo, hi = rng or E.RANGE.get(part, (40, 84))

    def pick(bi, t, ch):
        v = voicing(part, chord_at(sec, bi, t)["sym"], prev[0]); prev[0] = v
        if ch == "b":
            p = v[0] - 12 if v[0] - 12 >= lo else v[0]
        elif ch.isdigit():
            p = v[(int(ch) - 1) % len(v)]
        else:
            raise ValueError(f"arp {pattern!r}: {ch!r} is not a digit, b, . or -")
        return E.fit(p, (lo, hi)), dict(vel=1.0 if ch in "1b" else 0.8)
    _put(sec, part, _pitched(sec, _cells(pattern, unit, sec["nbars"]), pick, ring), local, text, dyn)
    _card(sec, part, "arpeggio", local, text, arp=pattern, unit=unit)


def bassline(sec, pattern, local=None, text=None, dyn=None, unit=None, ring=False, rng=None, part="BASS"):
    """Bass from chord degrees: 1 (the chord's bass note) 2 3 4 5 6 7 (the chord's 7th, else b7), 8 (root above the
    last note), < (fifth below the root), > (half step below the next chord's root), N (the next chord's bass, played
    early: the Cuban tumbao's anticipation, tie it over with '-'); '-' holds, '.' rests."""
    lo, hi = rng or E.RANGE[part]; last = [E.LAST.get(part, 40)]; cells = _cells(pattern, unit, sec["nbars"])
    step = _unit(unit)

    def next_root(bi, t):
        if t + step < E.BAR: c = chord_at(sec, bi, t + step)
        elif bi + 1 < sec["nbars"]: c = chord_at(sec, bi + 1, 0)
        else: c = chord_at(sec, bi, t)
        return c["bass"]

    def next_bass(bi, t):
        """The bass of the next chord change after t (within the section), else this chord's."""
        cur = chord_at(sec, bi, t)["sym"]
        for b in range(bi, sec["nbars"]):
            for u in range(t + 1 if b == bi else 0, E.BAR):
                c = chord_at(sec, b, u)
                if c["sym"] != cur: return c["bass"]
        return chord_at(sec, bi, t)["bass"]

    def pick(bi, t, ch):
        c = chord_at(sec, bi, t); r = c["root"]
        pcs = {"1": c["bass"], "2": (r + 2) % 12, "3": c["third"] if c["third"] is not None else (r + 4) % 12,
               "4": (r + 5) % 12, "5": next((x for x in c["tones"] if (x - r) % 12 in (6, 7, 8)), (r + 7) % 12),
               "6": (r + 9) % 12, "7": c["sev"] if c["sev"] is not None else (r + 10) % 12, "8": c["bass"],
               "<": (r + 7) % 12, ">": (next_root(bi, t) - 1) % 12, "N": next_bass(bi, t)}
        if ch not in pcs: raise ValueError(f"bassline {pattern!r}: {ch!r} is not one of 1-8 < > N . -")
        cand = [q for q in range(lo, hi + 1) if q % 12 == pcs[ch]]
        if ch == "8": cand = [q for q in cand if q > last[0]] or cand
        if ch == "<":
            root = min((q for q in range(lo, hi + 1) if q % 12 == r), key=lambda q: abs(q - last[0]))
            cand = [q for q in cand if q < root] or cand
        p = min(cand, key=lambda q: abs(q - last[0]) + (2 if q > lo + 17 else 0)); last[0] = p
        return p, ({"spell": "sharp"} if ch == ">" else {})
    _put(sec, part, _pitched(sec, cells, pick, ring), local, text, dyn)
    _card(sec, part, "bass", local, text, bass=pattern, unit=unit)


def _perc_bar(hits):
    """{16th: [sounds]} -> one percussion bar (each hit lasts to the next one, within its beat)."""
    b, t, on = [], 0, sorted(hits)
    for i, s in enumerate(on):
        if s > t: b.append(ev(t, s - t))
        nxt = on[i + 1] if i + 1 < len(on) else E.BAR
        lim = min(nxt - s, E.BEAT - s % E.BEAT)
        d = next(x for x in (6, 4, 3, 2, 1) if x <= lim)
        b.append(ev(s, d, tuple(hits[s]))); t = s + d
    if t < E.BAR: b.append(ev(t, E.BAR - t))
    return b


def perc(sec, part, local=None, text=None, dyn=None, unit=None, **lanes):
    """Percussion lanes for one player, e.g. perc(s, "P1", cajon="B..TS.", shaker="xxXxxX"). Instruments: cajon
    (B T S g), guiro (L s t), shaker (X x), snare (X x g R r; K k = a stick on the shell), cowbell (O o) on P1;
    djembe (B T S g), bongos (M m H S p), cuica (H L m), shaker (X x) on P2."""
    kit = KITS[part]; hits = [dict() for _ in range(sec["nbars"])]
    for inst, pat in lanes.items():
        pre = INSTR.get(inst)
        if pre is None: raise ValueError(f"perc: unknown instrument {inst!r} (one of {sorted(INSTR)})")
        for bi, row in enumerate(_cells(pat, unit, sec["nbars"])):
            for t, ch in row:
                if ch in ".-": continue
                k = pre + ch
                if k not in kit:
                    raise ValueError(f"perc {part} {inst}={pat!r}: no sound {ch!r} (have "
                                     f"{[s[len(pre):] for s in kit if s.startswith(pre)]})")
                hits[bi].setdefault(t, []).append(k)
    put(sec, part, [_perc_bar(h) for h in hits], _local(sec, local), text, dyn)
    _card(sec, part, "percussion", local, text, unit=unit, **lanes)


def perc_bar(part, unit=None, **lanes):
    """One hand-written percussion bar (fills, breaks, the final hit) to drop into sec['parts'][part][i]."""
    hits = {}
    for inst, pat in lanes.items():
        for t, ch in _cells(pat, unit, 1)[0]:
            if ch not in ".-": hits.setdefault(t, []).append(INSTR[inst] + ch)
    return _perc_bar(hits)


def hang_arp(sec, pattern, local=None, text=None, dyn=None, unit=None, ring=True):
    """Hang notes from the chord tones the hang has: 0 = ding (D3), k = k-th chord tone among the other notes (low to
    high, wrapping). A chord with no tone on the hang leaves a rest (qa.py lists it)."""
    def pick(bi, t, ch):
        if ch == "0": return HANG_NOTES[0], {}
        c = chord_at(sec, bi, t); tones = [q for q in HANG_NOTES[1:] if q % 12 in c["tones"]]
        if not tones: return None
        return tones[(int(ch) - 1) % len(tones)], {}
    _put(sec, "HANG", _pitched(sec, _cells(pattern, unit, sec["nbars"]), pick, ring), local, text, dyn)
    _card(sec, "HANG", "hang", local, text, hang=pattern, unit=unit)


# ---------------------------------------------------------------- singers
def bordon(sec, pattern, local=None, text=None, dyn=None, unit=None, part="GTR", rng=(40, 55)):
    """A bass-string guitar line (the landó bordón) by chord degrees, same grammar as bassline: 1 2 3 4 5 6 7 8 < >
    '-' '.'. The Toro mata archetype over i is "1.354.53.42." (styles.md 1.5)."""
    bassline(sec, pattern, local, text, dyn, unit, ring=False, rng=rng, part=part)
    sec["cards"][-1]["kind"] = "bordón (bass strings)"


def hang(sec, line, local=None, text=None, dyn=None, unit=None):
    """Hang notes written out: space-separated tokens, one per cell (note names from D Kurd, '.' rest, '-' hold),
    repeated to fill the bar. line may be a dict {chord symbol: line, '*': default} picked by each bar's first chord."""
    def cells_for(bi):
        ln = line
        if isinstance(line, dict):
            ln = line.get(sec["chords"][bi][0], line.get("*"))
        if ln is None: return []
        toks = [t for t in ln.replace("|", " ").split()]
        step = _unit(unit); span = len(toks) * step
        if E.BAR % span: raise ValueError(f"hang line {ln!r}: {len(toks)} cells x {step} 16ths don't divide the bar")
        return [(r * span + k * step, t) for r in range(E.BAR // span) for k, t in enumerate(toks)]

    def pick(bi, t, tok):
        p = pmidi(tok)
        if p not in HANG_NOTES: raise ValueError(f"hang: {tok} is not on the D Kurd hang {HANG_NOTES}")
        return p, {}
    bars = []
    for bi in range(sec["nbars"]):
        bars += _pitched(sec, [cells_for(bi)], pick, False)
    _put(sec, "HANG", bars, local, text, dyn)
    _card(sec, "HANG", "hang", local, text, unit=unit,
          **({k: v for k, v in line.items()} if isinstance(line, dict) else {"hang": line}))


def lead(sec, voice, octave=0, local=None, text=None, dyn=None):
    """The section's tune (its melody) in a singer's part, `octave` semitones away (-12: a man singing a woman's
    line); the renders, qa.py and the lead sheet follow the lead per bar."""
    idx = _local(sec, local)
    put(sec, voice, shift(sec["mel"], octave), idx, text, dyn)
    L = sec.setdefault("lead", {})
    for i in idx: L[i] = (voice, octave)


def coro(sec, voices, tokens, lyrics, local=None, mode="close", text=None, dyn=None):
    """A sung answer (coro) voiced as a block under its top line: voices high to low, tokens/lyrics per section bar
    (use 'r:BAR' bars where the coro rests)."""
    put_block(sec, voices, parse_line(tokens, lyrics), local=local, mode=mode, text=text, dyn=dyn)
