"""A cappella arranging engine: token parsing, chords, voicings, block harmony, pads, comping, bass lines,
vocal percussion from the recorded drums, and the section/part bookkeeping used by build.py.

An arrangement file does:   from engine import *;  setup(work=..., voices=[...], title=...);  then section()/put_*().
Times are in 16ths inside a bar of BAR sixteenths (16 in 4/4). Event = dict(start, dur, midi|None|tuple(VP hits),
lyr, tie_in, tie_out, art). Bars are lists of events covering exactly BAR sixteenths.
Full reference: references/engine.md
"""
import itertools, json, os, re

# ---------------------------------------------------------------- global state (set by setup())
WORK = os.environ.get("ACAP_WORK")
BAR = 16
METER = (4, 4)
BEAT = 4                  # 16ths per beat
SECS = []                 # sections in score order
VOICES = ["L", "S1", "S2", "A", "T", "Br", "B", "VP"]
META = dict(title="Untitled", composer="", arranger="a cappella arrangement", subtitle="", name=None)
LAST = {}                 # last sung pitch per voice (smooth voice leading across calls)
_GRID = None

PC = {n: i for i, n in enumerate("C C# D Eb E F F# G Ab A Bb B".split())}
PC.update({"Db": 1, "D#": 3, "Gb": 6, "G#": 8, "A#": 10, "Cb": 11, "Fb": 4, "E#": 5, "B#": 0})
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11),
        "sus": (0, 5, 7), "sus4": (0, 5, 7), "7sus": (0, 5, 7, 10), "7sus4": (0, 5, 7, 10), "dim": (0, 3, 6),
        "6": (0, 4, 7, 9), "m6": (0, 3, 7, 9), "add9": (0, 2, 4, 7), "sus2": (0, 2, 7), "aug": (0, 4, 8),
        "dim7": (0, 3, 6, 9), "m7b5": (0, 3, 6, 10), "9": (0, 4, 7, 10, 2), "m9": (0, 3, 7, 10, 2),
        "maj9": (0, 4, 7, 11, 2), "madd9": (0, 3, 7, 2)}
COLOR = {"": 2, "m": 10, "7": 2, "maj7": 2, "sus": 10, "sus4": 10, "7sus": 2, "6": 2, "m7": 2}  # pad tension
MAJOR = (0, 2, 4, 5, 7, 9, 11)

# voice key -> (name, abbreviation, clef (sign, line, octave-change), range (lo, hi) MIDI, pan -64..63, volume)
VOICE_INFO = {
    "L": ("Solo", "Solo", ("G", 2, -1), (43, 74), 0, 100),
    "S": ("Soprano", "S", ("G", 2, 0), (60, 79), -40, 80),
    "S1": ("Soprano 1", "S1", ("G", 2, 0), (62, 81), -45, 72),
    "S2": ("Soprano 2", "S2", ("G", 2, 0), (58, 74), -25, 72),
    "A": ("Alto", "A", ("G", 2, 0), (55, 72), -10, 72),
    "A1": ("Alto 1", "A1", ("G", 2, 0), (56, 72), -15, 72),
    "A2": ("Alto 2", "A2", ("G", 2, 0), (53, 69), -5, 72),
    "T": ("Tenor", "T", ("G", 2, -1), (50, 67), 10, 72),
    "T1": ("Tenor 1", "T1", ("G", 2, -1), (52, 69), 10, 72),
    "T2": ("Tenor 2", "T2", ("G", 2, -1), (48, 65), 18, 72),
    "Br": ("Baritone", "Bar", ("F", 4, 0), (45, 62), 25, 72),
    "B": ("Bass", "B", ("F", 4, 0), (38, 57), 0, 88),
    "B1": ("Bass 1", "B1", ("F", 4, 0), (41, 60), 25, 80),
    "B2": ("Bass 2", "B2", ("F", 4, 0), (36, 55), 0, 88),
    "VP": ("Vocal Percussion", "VP", ("percussion", 2, 0), None, 0, 80),
}
FEMALE_SOLO = ("G", 2, 0), (55, 79)
RANGE = {k: v[3] for k, v in VOICE_INFO.items() if v[3]}
# VP sounds: name -> (display step, octave, GM drum note, notehead)
DRUM = {"B": ("F", 4, 36, None), "Pf": ("C", 5, 38, None), "k": ("C", 5, 37, "x"), "t": ("G", 5, 42, "x"),
        "ts": ("G", 5, 46, "circle-x"), "Ksh": ("A", 5, 49, "x")}

# ---------------------------------------------------------------- part registries (filled by style layers such as the
# south-american band layer; build.py / render.py / qa.py read them). Empty = plain a cappella behaviour.
KITS = {}         # percussion part -> {sound: dict(step, octave, gm, head, stem, mark, vel, label)}  ("VP" uses DRUM)
PROGRAM = {}      # part -> GM program (0-based) for the renders and the MuseScore instrument
SOUND = {}        # part -> MusicXML instrument-sound id (MuseScore picks its instrument from it); default keyboard.piano
TRANSPOSE = {}    # part -> written pitch = sounding + k (12 for guitar / bass guitar: plain clef, sounds 8vb)
KIND = {}         # part -> "voice" | "pitched" | "perc" (default: voice, "VP" perc)
CHORD_PARTS = []  # parts that print chord symbols (default: the top staff only)
PITCHSET = {}     # part -> allowed MIDI pitches (a hang drum, a kalimba): qa.py lists the others
CHORDSET = {}     # part -> function(symbol) -> (playable symbol, exact?) or None (autoharp bars): qa.py checks
PLAYERS = {}      # player name -> [parts] played by one person, one at a time: qa.py lists overlaps
TAB = {}          # part -> (open strings low to high, max fret): build.py adds a tablature staff under the part


def is_perc(v):
    return v == "VP" or v in KITS


def kind(v):
    return KIND.get(v) or ("perc" if is_perc(v) else "voice")


def setup(work=None, voices=None, title=None, composer=None, arranger=None, subtitle=None, meter=(4, 4),
          solo="male", ranges=None, name=None, last=None):
    """Configure the arrangement. work = analysis dir (for vp() and QA); voices = staff order (keys of VOICE_INFO);
    solo = 'male' (tenor clef, G2-D5) or 'female' (treble, G3-G5); ranges = {voice: (lo, hi)} overrides."""
    global WORK, BAR, METER, BEAT, VOICES, _GRID
    if work: WORK = os.path.abspath(work)
    METER = tuple(meter)
    num, den = METER
    BEAT = 6 if (den == 8 and num % 3 == 0) else 16 // den
    BAR = num * 16 // den
    if voices: VOICES = list(voices)
    for k, v in (("title", title), ("composer", composer), ("arranger", arranger), ("subtitle", subtitle),
                 ("name", name)):
        if v is not None: META[k] = v
    if solo == "female":
        n, a, _, _, p, vol = VOICE_INFO["L"]; VOICE_INFO["L"] = (n, a, FEMALE_SOLO[0], FEMALE_SOLO[1], p, vol)
        RANGE["L"] = FEMALE_SOLO[1]
    if ranges: RANGE.update(ranges)
    LAST.update(dict(S=72, S1=74, S2=70, A=65, A1=67, A2=62, T=58, T1=60, T2=55, Br=50, B=46, B1=50, B2=43))
    if last: LAST.update(last)
    _GRID = None
    _patterns()


def R(**o):
    """Copy of the default ranges with overrides, e.g. R(S1=(70, 77), T=(55, 62))."""
    r = dict(RANGE); r.update(o); return r


# ---------------------------------------------------------------- chords and scales
def chord(sym):
    s, bass = (sym.split("/") + [None])[:2]
    r = s[:2] if len(s) > 1 and s[1] in "#b" else s[:1]
    q = s[len(r):]
    root = PC[r]; iv = QUAL[q]
    tones = [(root + i) % 12 for i in iv]
    third = next(((root + i) % 12 for i in iv if i in (3, 4, 5)), None)
    sev = next(((root + i) % 12 for i in iv if i in (9, 10, 11)), None)
    return dict(root=root, tones=set(tones), bass=PC[bass] if bass else root, third=third, sev=sev,
                color=(root + COLOR.get(q, 2)) % 12, q=q, sym=sym)


REL_MAJOR = {"Am": "C", "Em": "G", "Bm": "D", "F#m": "A", "C#m": "E", "G#m": "B", "D#m": "F#", "Dm": "F",
             "Gm": "Bb", "Cm": "Eb", "Fm": "Ab", "Bbm": "Db", "Ebm": "Gb"}


def major_of(key): return REL_MAJOR.get(key, key)


def scale(key):
    t = PC[major_of(key)]; return sorted((t + i) % 12 for i in MAJOR)


def ev(start, dur, midi=None, lyr="", tie_in=False, tie_out=False, art=None):
    return dict(start=start, dur=dur, midi=midi, lyr=lyr, tie_in=tie_in, tie_out=tie_out, art=art)


def rest_bar():
    return [ev(0, BAR)]


def chord_at(sec, bi, t16):
    row = sec["chords"][bi]
    return chord(row[min(len(row) - 1, t16 * len(row) // BAR)])


def chord_for(sec, bi, e):
    """Chord heard under an event: a long note starting an 8th before a chord change belongs to the new chord
    (the 'push' of pop rhythm sections)."""
    t = e["start"]; half = BAR // 2
    if e["dur"] >= 4 and (t + 2) % half == 0 and t + 2 < BAR: t += 2
    return chord_at(sec, bi, t)


def slot_of(sec, bi, t16):
    row = sec["chords"][bi]; return min(len(row) - 1, t16 * len(row) // BAR)


# ---------------------------------------------------------------- token lines
NAMES = "C C# D Eb E F F# G Ab A Bb B".split()


def pmidi(p):
    n, acc, o = re.fullmatch(r"([A-G])([#b]?)(-?\d)", p).groups()
    return {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[n] + {"#": 1, "b": -1, "": 0}[acc] + 12 * (int(o) + 1)


def parse_line(bars, lyrics=None, art=None):
    """Token bars ["D3:3 Bb2:3=doo r:2 C4~:4 ...", ...] -> event bars. PITCH:DUR16, r = rest, '~' ties into the next
    note, '=syl' attaches a syllable. lyrics: optional list (one string per bar) of syllables for the note onsets
    ('_' = no syllable; 'Dash-' begins a word, '-ing' ends it, '-ra-' is a middle syllable)."""
    out = []
    for bi, bar in enumerate(bars):
        evs, t = [], 0
        for tok in bar.split():
            pd, _, syl = tok.partition("=")
            p, d = pd.split(":"); d = int(d)
            e = ev(t, d, art=art)
            if p != "r":
                e["tie_out"] = p.endswith("~"); e["midi"] = pmidi(p.rstrip("~")); e["lyr"] = syl
            evs.append(e); t += d
        assert t == BAR, f"bar {bi} of {bars!r}: {t} sixteenths, expected {BAR}"
        out.append(evs)
    prev = None
    for b in out:
        for e in b:
            if prev is not None and prev["tie_out"] and e["midi"] == prev["midi"]:
                e["tie_in"] = True
            prev = e if e["midi"] is not None else None
    if lyrics:
        for bi, b in enumerate(out):
            syl = lyrics[bi].split() if bi < len(lyrics) and lyrics[bi] else []
            ons = [e for e in b if e["midi"] is not None and not e["tie_in"]]
            assert len(syl) in (0, len(ons)), f"bar {bi}: {len(syl)} syllables {syl} for {len(ons)} onsets in {bars[bi]!r}"
            for e, s in zip(ons, syl):
                e["lyr"] = "" if s == "_" else s
    return out


# ---------------------------------------------------------------- meter transplant (4/4 transcription -> another meter)
# A warp maps every 16th of a source bar (0..16) to a 16th of the target bar (0..BAR), monotonic, so note starts and
# ends move together and syllables stay on their notes. Ties across bars are kept.
def _swing(sub):
    return [b * 6 + sub[k] for b in range(4) for k in range(4)] + [24]


WARPS = {
    "swing": _swing((0, 2, 4, 5)),    # 4/4 -> 12/8: quarter -> dotted quarter, 8th pairs -> long-short (4+2), 16ths
                                      # -> 8th 8th 16th 16th. The usual way a straight pop line goes into 6/8 or 12/8.
    "duplet": _swing((0, 2, 3, 5)),   # 4/4 -> 12/8 keeping straight 8ths as dotted-8th duplets (3+3): hemiola feel
    "even": _swing((0, 1, 3, 4)),     # 4/4 -> 12/8: 16ths close together, 8ths as duplets
    "waltz": [0, 1, 2, 3, 4, 5, 6, 7, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12],  # 4/4 -> 3/4: beats 3-4 squeezed into beat 3
}


def warp_tokens(bars, how="swing", src=16):
    """Re-time token bars written in a source meter (src 16ths per bar, 4/4 = 16) into the current meter with a warp
    (a WARPS name or a list of src+1 target positions). Returns token bars that sum to BAR."""
    table = WARPS[how] if isinstance(how, str) else how
    assert len(table) == src + 1 and table[-1] == BAR, f"warp {how!r} maps a {src}-16th bar to {table[-1]}, not BAR={BAR}"
    out = []
    for bi, bar in enumerate(bars):
        toks, t = [], 0
        for tok in bar.split():
            pd, sep, syl = tok.partition("=")
            p, d = pd.split(":"); d = int(d)
            a, b = int(table[t] + .5), int(table[t + d] + .5) if t + d <= src else None
            assert b is not None, f"warp: bar {bi} of {bars!r} is longer than {src} 16ths"
            if b <= a: raise ValueError(f"warp {how!r}: note {tok!r} in bar {bi} collapses; rewrite this bar by hand")
            toks.append(f"{p}:{b - a}" + (sep + syl if sep else "")); t += d
        assert t == src, f"warp: bar {bi} of {bars!r} has {t} 16ths, expected {src}"
        out.append(" ".join(toks))
    return out


def take(D, a, b):
    """Bars a..b (inclusive, recording numbers) of a draft dict: LEAD-style {n: (tokens, lyr)} -> (tokens, lyrics);
    plain {n: tokens} / CHORDS {n: [..]} -> list. Missing bars become rests."""
    vals = [D.get(n) for n in range(a, b + 1)]
    if any(isinstance(v, tuple) for v in vals):
        return [v[0] if v else f"r:{BAR}" for v in vals], [v[1] if v else "" for v in vals]
    return [v if v is not None else f"r:{BAR}" for v in vals]


def shift(bars, k):
    return [[dict(e, midi=None if e["midi"] is None else e["midi"] + k) for e in b] for b in bars]


def relyric(bars, fn):
    """Replace syllables on onsets: fn(event, index_in_phrase) -> syllable (the index restarts after each rest)."""
    out = []; i = 0
    for b in bars:
        nb = []
        for e in b:
            e = dict(e)
            if e["midi"] is None:
                i = 0
            elif not e["tie_in"]:
                e["lyr"] = fn(e, i); i += 1
            nb.append(e)
        out.append(nb)
    return out


def _names(key):
    """Pitch-class names: sharps for sharp keys, flats for flat keys, C# Eb F# Ab Bb when no key is given."""
    if key is None or major_of(key) == "C": return "C C# D Eb E F F# G Ab A Bb B".split()
    if major_of(key) in ("G", "D", "A", "E", "B", "F#", "C#"): return "C C# D D# E F F# G G# A A# B".split()
    return "C Db D Eb E F Gb G Ab A Bb B".split()


def tr_tokens(bars, k, key=None):
    """Transpose token bars by k semitones (spelled for `key`; C# Eb F# Ab Bb when no key)."""
    names = _names(key)
    out = []
    for bar in bars:
        toks = []
        for t in bar.split():
            pd, sep, syl = t.partition("=")
            p, d = pd.split(":")
            if p != "r":
                tie = p.endswith("~"); m = pmidi(p.rstrip("~")) + k
                p = f"{names[m % 12]}{m // 12 - 1}{'~' if tie else ''}"
            toks.append(f"{p}:{d}" + (sep + syl if sep else ""))
        out.append(" ".join(toks))
    return out


def tr_chords(rows, k, key=None):
    """Transpose chord rows [[sym, ...], ...] by k semitones."""
    names = _names(key)

    def one(s):
        r = s[:2] if len(s) > 1 and s[1] in "#b" else s[:1]
        return names[(PC[r] + k) % 12] + s[len(r):]
    return [["/".join(one(x) for x in c.split("/")) for c in row] for row in rows]


# ---------------------------------------------------------------- scale helpers
def step(m, k, key):
    """Move midi m by k diatonic steps in key (a chromatic m is first snapped to the scale tone below)."""
    sc = scale(key)
    while m % 12 not in sc: m -= 1
    for _ in range(abs(k)):
        m += 1 if k > 0 else -1
        while m % 12 not in sc: m += 1 if k > 0 else -1
    return m


def fit(p, rng):
    lo, hi = rng
    while p > hi: p -= 12
    while p < lo: p += 12
    return p


# ---------------------------------------------------------------- harmony line a 3rd above/below a reference
def harm(ref_bars, sec, direction, rng, prev=None):
    """Parallel harmony a diatonic 3rd above (direction=+1) or below (-1), moved to a chord tone on long notes."""
    key = sec["key"]; out = []; last = None
    for bi, b in enumerate(ref_bars):
        nb = []
        for e in b:
            n = dict(e)
            if e["midi"] is None: nb.append(n); continue
            if e["tie_in"] and last is not None: n["midi"] = last; nb.append(n); continue
            c = chord_for(sec, bi, e); m = e["midi"]
            third = step(m, 2 * direction, key)
            cands = [p for p in (range(m + 3, m + 10) if direction > 0 else range(m - 9, m - 2))
                     if p % 12 in c["tones"] and rng[0] <= p <= rng[1]]     # out-of-range tones would fold an octave
            if third % 12 in c["tones"] or (e["dur"] <= 2 and m % 12 not in c["tones"]) or not cands:
                p = third
            else:
                ref = last if last is not None else (prev if prev is not None else m + 4 * direction)
                p = min(cands, key=lambda q: abs(q - ref) + 0.6 * abs(q - m - 4 * direction))
            p = fit(p, rng); n["midi"] = p; last = p; nb.append(n)
        out.append(nb)
    return out


# ---------------------------------------------------------------- block harmony under a top line
def block(top_bars, sec, n_below, mode="close", double=False):
    """Block voicing under a top line -> [top, v1, v2, ...] (high to low). Chord tones (or long tensions) get chord
    tones below; short non-chord tones get diatonic parallel 3rds. mode 'drop2' drops the 2nd voice an octave.
    double: add top-12 as the lowest voice. Tied notes are re-voiced when the chord changes under them."""
    key = sec["key"]
    nv = n_below + 1 + (1 if double else 0)
    outs = [[] for _ in range(nv)]
    last = None; last_c = None
    for bi, b in enumerate(top_bars):
        bars = [[] for _ in range(nv)]
        for e in b:
            if e["midi"] is None:
                for v in range(nv): bars[v].append(dict(e))
                continue
            c = chord_for(sec, bi, e); m = e["midi"]
            if e["tie_in"] and last is not None and (last_c is None or last_c["sym"] == c["sym"]):
                for v in range(nv): bars[v].append(dict(e, midi=last[v]))
                continue
            tied = e["tie_in"] and last is not None
            last_c = c
            tones = set(c["tones"])
            if c["q"] in ("", "m") and n_below >= 3:
                tones |= {c["color"]} if c["q"] == "" and m % 12 == c["color"] else set()
            stack = [m]
            if m % 12 in tones or e["dur"] >= 4:
                p = m
                for k in range(n_below):
                    p -= 1
                    while p % 12 not in tones or (k == 0 and m % 12 not in tones and m - p <= 2):
                        p -= 1
                    stack.append(p)
            else:
                for k in range(n_below):
                    stack.append(step(m, -2 * (k + 1), key))
            if mode == "drop2" and len(stack) >= 3:
                stack = [stack[0]] + stack[2:] + [stack[1] - 12]
            if double:
                stack.append(m - 12)
            for v in range(nv):
                if tied and stack[v] != last[v]:
                    bars[v].append(dict(e, midi=stack[v], tie_in=False, lyr=""))
                else:
                    bars[v].append(dict(e, midi=stack[v]))
            last = stack
        for v in range(nv): outs[v].append(bars[v])
    return outs


# ---------------------------------------------------------------- chord-slot voicings (pads / comping)
def voicings(sec, voices, ranges, prev, color=True, top_cap=None):
    """One voicing per chord slot for `voices` (high to low) with smooth voice leading: keeps 3rd and 7th, adds the
    colour tone (9th) in 4+ voices, penalises doubled 3rds/7ths, semitone and minor-9th rubs, low close intervals.
    Returns ({(bar, slot): {voice: midi}}, last)."""
    res = {}; prev = dict(prev)
    for bi, row in enumerate(sec["chords"]):
        for k, sym in enumerate(row):
            c = chord(sym)
            tones = set(c["tones"])
            if color and len(voices) >= 4 and len(tones) == 3: tones.add(c["color"])
            if color and len(voices) >= 5: tones.add(c["color"])
            ess = {c["third"]} | ({c["sev"]} if c["sev"] is not None else set())
            ess.discard(None)
            opts = []
            for v in voices:
                lo, hi = ranges[v]
                if top_cap and v == voices[0]: hi = min(hi, top_cap)
                cand = [p for p in range(lo, hi + 1) if p % 12 in tones]
                ref = prev.get(v, (lo + hi) // 2)
                opts.append(sorted(cand, key=lambda q: abs(q - ref))[:6])
            best = None
            for combo in itertools.product(*opts):
                if any(combo[i] <= combo[i + 1] for i in range(len(combo) - 1)): continue
                if any(combo[i] - combo[i + 1] > 12 for i in range(len(combo) - 2)): continue
                if len(combo) > 1 and combo[-2] - combo[-1] > 16: continue
                pcs = [p % 12 for p in combo]
                cost = sum(abs(p - prev.get(v, p)) for p, v in zip(combo, voices))
                cost += 12 * len(ess - set(pcs))
                dup = len(pcs) - len(set(pcs))
                cost += 5 * dup
                for t in (c["third"], c["sev"], c["color"]):
                    if t is not None and pcs.count(t) > 1: cost += 8
                for i in range(len(combo)):
                    for j in range(i + 1, len(combo)):
                        if (combo[i] - combo[j]) % 12 == 1: cost += 6 if combo[i] - combo[j] == 1 else 10
                for i in range(len(combo) - 1):
                    if combo[i + 1] < 50 and combo[i] - combo[i + 1] < 5: cost += 4
                if c["color"] in pcs and combo[0] % 12 == c["color"] and c["color"] not in c["tones"]: cost += 3
                if best is None or cost < best[0]: best = (cost, combo)
            if best is None:
                raise ValueError(f"no voicing for {sym} in {sec['name']} bar {bi} with ranges "
                                 f"{[ranges[v] for v in voices]}: widen the ranges")
            res[(bi, k)] = dict(zip(voices, best[1]))
            prev.update(res[(bi, k)])
    return res, prev


def pad(sec, voices, ranges, prev, syl="Oo", color=True, every_bar=False):
    """Sustained chords, one per chord slot; a repeated pitch is held (tied across bars unless every_bar)."""
    V, prev2 = voicings(sec, voices, ranges, prev, color)
    out = {v: [] for v in voices}
    for v in voices:
        lastp = None
        for bi, row in enumerate(sec["chords"]):
            seg = BAR // len(row); b = []
            for k in range(len(row)):
                p = V[(bi, k)][v]
                if b and b[-1]["midi"] == p:
                    b[-1]["dur"] += seg
                elif k == 0 and lastp == p and out[v] and not every_bar:
                    b.append(ev(0, seg, p, "", tie_in=True)); out[v][-1][-1]["tie_out"] = True
                else:
                    b.append(ev(k * seg, seg, p, syl))
                lastp = p
            if sum(e["dur"] for e in b) < BAR: b[-1]["dur"] += BAR - sum(e["dur"] for e in b)
            out[v].append(b)
    return out, prev2


PATTERNS = {}


def _patterns():
    """Comping rhythms (start, dur) per bar, for the current meter."""
    PATTERNS.clear()
    if BAR == 16:
        PATTERNS.update({
            "off8": [(2, 2), (6, 2), (10, 2), (14, 2)],                 # keyboard / guitar upstrokes
            "back": [(4, 2), (12, 2)],                                   # 2 & 4 (skank, keys backbeat)
            "tres": [(0, 2), (3, 2), (6, 2), (8, 2), (11, 2), (14, 2)],  # 3+3+2 tresillo stabs
            "push": [(0, 3), (6, 2), (10, 2), (14, 2)],
            "half": [(0, 8), (8, 8)],
            "whole": [(0, 16)],
            "bell": [(i, 2) for i in range(0, 16, 2)],
            "charleston": [(0, 3), (6, 4)],
            "sixteens": [(i, 1) for i in range(16)],
        })
    else:
        nb = BAR // BEAT
        PATTERNS.update({
            "off8": [(b * BEAT + BEAT // 2, BEAT // 2) for b in range(nb)],
            "back": [(b * BEAT, 2) for b in range(1, nb)],
            "half": [(0, BAR)], "whole": [(0, BAR)],
            "bell": [(i, 2) for i in range(0, BAR, 2)],
            "beats": [(b * BEAT, BEAT) for b in range(nb)],
        })


_patterns()


def comp(sec, voices, ranges, prev, pattern, syl="dn", art="staccato", color=True):
    """Rhythmic chord hits on a pattern: a PATTERNS name or a list of (start, dur) per bar."""
    V, prev2 = voicings(sec, voices, ranges, prev, color)
    pat = PATTERNS[pattern] if isinstance(pattern, str) else pattern
    out = {v: [] for v in voices}
    for bi, row in enumerate(sec["chords"]):
        for v in voices:
            b = []; t = 0
            for s, d in pat:
                if s > t: b.append(ev(t, s - t))
                p = V[(bi, slot_of(sec, bi, s))][v]
                b.append(ev(s, d, p, syl if isinstance(syl, str) else syl[len(b) % len(syl)], art=art)); t = s + d
            if t < BAR: b.append(ev(t, BAR - t))
            out[v].append(b)
    return out, prev2


def follow(sec, rhythm_bars, voice, rng, prev, pref=("root", "fifth")):
    """One voice singing the rhythm/lyrics of rhythm_bars on chord tones (pref: root, third, fifth, sev), smooth."""
    out = []; last = prev
    for bi, b in enumerate(rhythm_bars):
        nb = []
        for e in b:
            n = dict(e)
            if e["midi"] is None: nb.append(n); continue
            if e["tie_in"] and nb and nb[-1]["midi"] is not None:
                n["midi"] = nb[-1]["midi"]; nb.append(n); continue
            c = chord_for(sec, bi, e)
            names = dict(root=c["bass"], third=c["third"], fifth=(c["root"] + 7) % 12, sev=c["sev"])
            pcs = {names[k] for k in pref if names[k] is not None}
            cand = [p for p in range(rng[0], rng[1] + 1) if p % 12 in pcs]
            p = min(cand, key=lambda q: abs(q - last)); n["midi"] = p; last = p; n["tie_in"] = False
            nb.append(n)
        out.append(nb)
    return out, last


def bass_pat(sec, pattern, rng, prev, syl=None):
    """Bass line from a per-bar pattern of (selector, start, dur): selector 1 = the bar's first chord's bass,
    2 = second chord's bass, or an explicit pitch name. Octave chosen for smoothness. pattern may be a function of
    the bar index. Syllables: 'doom' on long notes, 'dm' on short ones (or syl)."""
    out = []; last = prev
    for bi, row in enumerate(sec["chords"]):
        b = []; t = 0
        pat = pattern(bi) if callable(pattern) else pattern
        for sel, s, d in pat:
            if s > t: b.append(ev(t, s - t))
            if isinstance(sel, str):
                p = pmidi(sel)
            else:
                c = chord(row[min(sel - 1, len(row) - 1)])
                cand = [q for q in range(rng[0], rng[1] + 1) if q % 12 == c["bass"]]
                p = min(cand, key=lambda q: abs(q - last) + (3 if q > 52 else 0))
            y = syl if syl else ("doom" if d >= 4 else "dm")
            b.append(ev(s, d, p, y)); last = p; t = s + d
        if t < BAR: b.append(ev(t, BAR - t))
        out.append(b)
    return out, last


def turns(bars, sec, syl=("doo", "dl"), cap=79):
    """Flute ornament: a sustained note (>= 8 sixteenths) at the end of an even-numbered bar ends with a 16th-note
    turn (upper, main, lower). cap = highest allowed pitch."""
    key = sec["key"]; out = []
    for bi, b in enumerate(bars):
        nb = []
        for e in b:
            phrase_end = bi % 2 == 1 and e["start"] + e["dur"] == BAR
            if (e["midi"] is not None and e["dur"] >= 8 and not e["tie_out"] and phrase_end
                    and step(e["midi"], 1, key) <= cap):
                m = e["midi"]; s = e["start"]; d = e["dur"]
                nb.append(dict(e, dur=d - 3, lyr=e["lyr"] if not e["tie_in"] else ""))
                for j, p in enumerate((step(m, 1, key), m, step(m, -1, key))):
                    nb.append(ev(s + d - 3 + j, 1, p, syl[1]))
            else:
                nb.append(e)
        out.append(nb)
    return out


def merge(a, b, at):
    """Bar-wise merge: events of a before 16th `at`, events of b from `at` (both bar lists)."""
    out = []
    for x, y in zip(a, b):
        xa = []
        for e in x:
            if e["start"] < at:
                e = dict(e, dur=min(e["dur"], at - e["start"]))
                if e["start"] + e["dur"] >= at: e["tie_out"] = False
                xa.append(e)
        out.append(xa + [e for e in y if e["start"] >= at])
    return out


# ---------------------------------------------------------------- syllables for instrument emulation
def horn(e, i): return "Bah" if i == 0 else ("dat" if e["dur"] <= 1 else "dah")
def flute(e, i): return "doo" if e["dur"] >= 3 or i == 0 else "dl"
def strings(e, i): return "Oo" if i == 0 else ""
def guitar(e, i): return "jen" if e["dur"] <= 2 else "jow"


def syl_seq(seq):
    """Syllable function cycling through a fixed list per phrase, e.g. syl_seq(['Bah', 'da', 'da', 'Bah!'])."""
    return lambda e, i: seq[min(i, len(seq) - 1)]


# ---------------------------------------------------------------- sections and parts
def section(name, key, first, chords, mel=None, lyr=None, tempo=None, note=None, warp=None, **kw):
    """Start a section. key: 'Bb', 'F#', 'Gm'...; first: recording bar number of its first bar (None if the bars
    don't exist in the recording); chords: one list of symbols per bar (each list splits the bar evenly);
    mel/lyr: solo melody token bars + per-bar syllables (or None for no solo); tempo: beats per minute (dotted
    quarters in 6/8, 12/8); warp: re-time a 4/4 melody into the current meter (a WARPS name, see warp_tokens) and
    remember the warp so the renders and qa.py can line the bars up with the recording."""
    n = len(chords)
    s = dict(name=name, key=key, first=first, nbars=n, chords=chords, parts={}, text={}, dyn={}, tempo=tempo,
             note=note, **kw)
    if warp:
        s["warp"] = list(WARPS[warp] if isinstance(warp, str) else warp)
        if mel: mel = warp_tokens(mel, warp)
    s["mel"] = parse_line(mel, lyr) if mel else [rest_bar() for _ in range(n)]
    assert len(s["mel"]) == n, f"{name}: {len(s['mel'])} melody bars for {n} chord bars"
    s["parts"]["L"] = s["mel"]
    SECS.append(s); return s


def put(sec, voice, bars, local=None, text=None, dyn=None):
    """Write bars (list over the whole section) into a voice, only at section-bar indices `local` (default all).
    A background voice entering mid-word loses the hyphen. text = italic direction, dyn = 'p' 'mf' 'f' ..."""
    P = sec["parts"].setdefault(voice, [None] * sec["nbars"])
    idx = list(range(sec["nbars"])) if local is None else list(local)
    for i in idx:
        P[i] = [dict(e) for e in bars[i]]
        ons = [e for e in P[i] if e["midi"] is not None and e["lyr"]]
        if ons and i - 1 not in idx and ons[0]["lyr"].startswith("-") and voice != "L":
            ons[0]["lyr"] = ons[0]["lyr"].lstrip("-")
        if ons and i + 1 not in idx and ons[-1]["lyr"].endswith("-") and voice != "L" and local is not None:
            ons[-1]["lyr"] = ons[-1]["lyr"].rstrip("-")
    if text: sec["text"][(voice, idx[0])] = text
    if dyn: sec["dyn"][(voice, idx[0])] = dyn
    for i in idx:
        for e in P[i]:
            if e["midi"] is not None and not isinstance(e["midi"], tuple): LAST[voice] = e["midi"]


def put_pad(sec, voices, syl, ranges, local=None, color=True, text=None, dyn=None):
    out, _ = pad(sec, voices, ranges, LAST, syl, color=color)
    for v in voices: put(sec, v, out[v], local, text, dyn)


def put_comp(sec, voices, pattern, syl, ranges, local=None, text=None, dyn=None, art="staccato"):
    out, _ = comp(sec, voices, ranges, LAST, pattern, syl, art=art)
    for v in voices: put(sec, v, out[v], local, text, dyn)


def put_block(sec, voices, top, local=None, mode="close", double=False, text=None, dyn=None, syl=None):
    """voices high to low; voices[0] sings `top`, the others are voiced below it (see block())."""
    if syl: top = relyric(top, syl)
    nb = len(voices) - 1 - (1 if double else 0)
    outs = block(top, sec, nb, mode, double)
    for v, b in zip(voices, outs): put(sec, v, b, local, text, dyn)


def put_follow(sec, voice, rhythm, rng, local=None, pref=("fifth", "third"), text=None, dyn=None):
    out, _ = follow(sec, rhythm, voice, rng, LAST.get(voice, sum(rng) // 2), pref)
    put(sec, voice, out, local, text, dyn)


def put_bass(sec, pattern, local=None, syl=None, text=None, dyn=None, rng=None, voice="B"):
    out, _ = bass_pat(sec, pattern, rng or RANGE[voice], LAST.get(voice, 46), syl)
    put(sec, voice, out, local, text, dyn)


# ---------------------------------------------------------------- vocal percussion
def drum_grid():
    global _GRID
    if _GRID is None:
        p = f"{WORK}/drumgrid.json" if WORK else None
        _GRID = json.load(open(p)) if p and os.path.exists(p) else {}
    return _GRID


DEFAULT_GROOVE = dict(K="X.......X.......", S="....X.......X...")


def vp(sec, hats="8", rim=False, crash=(), local=None, label=True, groove=None):
    """Vocal percussion copied from the recorded drums (W/drumgrid.json) bar by bar, fills included.
    hats: '8' / '4' / '16' / None (closed hats 't' added only where the record has drums); rim: snare -> rim 'k';
    crash: section-bar indices that start with a crash 'Ksh'; groove: dict(K=..., S=...) strings ('X' hit) used
    when the bar is not in the recording (first=None) or no drum grid exists. Syllables are written in the first
    bar of the section (label)."""
    G = drum_grid(); bars = []
    for bi in range(sec["nbars"]):
        g = G.get(str(sec["first"] + bi)) if sec["first"] is not None else None
        if g is None: g = groove or DEFAULT_GROOVE
        silent = "X" not in g["K"] + g["S"]
        hits = {}
        for s in range(BAR):
            K, S_ = g["K"][s % len(g["K"])], g["S"][s % len(g["S"])]
            k = K == "X" or (K == "x" and s % 2 == 0)
            sn = S_ == "X" or (S_ == "x" and K == "." and s not in (0, BAR // 2))
            h = not silent and ((hats == "8" and s % 2 == 0) or (hats == "4" and s % 4 == 0) or hats == "16")
            d = []
            if k: d.append("B")
            if sn: d.append("k" if rim else "Pf")
            if h and not sn: d.append("t")
            if bi in crash and s == 0: d = ["B", "Ksh"]
            if d: hits[s] = tuple(d)
        b = []; on = sorted(hits); t = 0
        for i, s in enumerate(on):
            if s > t: b.append(ev(t, s - t))
            nxt = on[i + 1] if i + 1 < len(on) else BAR
            d = min(nxt - s, 4 - s % 4 if s % 4 else 4)
            if d == 3: d = 2
            lyr = "/".join(x for x in hits[s] if x != "t") or "t"
            b.append(ev(s, d, hits[s], lyr if (label and bi == 0) else "")); t = s + d
        if t < BAR: b.append(ev(t, BAR - t))
        bars.append(b)
    put(sec, "VP", bars, local)


def vp_bar(hits):
    """One VP bar from {16th: 'B'|'Pf'|'B/Ksh'...}, e.g. vp_bar({0: 'B/Ksh'}) for a final crash."""
    b = []; t = 0
    for s in sorted(hits):
        if s > t: b.append(ev(t, s - t))
        nxt = min([x for x in hits if x > s] + [BAR]); d = min(nxt - s, 4)
        sounds = tuple(hits[s].split("/")); b.append(ev(s, d, sounds, hits[s] + ("!" if "Ksh" in sounds else "")))
        t = s + d
    if t < BAR: b.append(ev(t, BAR - t))
    return b


def finish():
    """Fill missing bars with rests (build.py calls this)."""
    for s in SECS:
        for v in VOICES:
            P = s["parts"].setdefault(v, [None] * s["nbars"])
            s["parts"][v] = [b if b else rest_bar() for b in P]


def fermata_last(sec, voices=None):
    """Put a fermata on the last sung note of every voice in the section's last bar."""
    for v in voices or [v for v in VOICES if not is_perc(v)]:
        notes = [e for e in (sec["parts"].get(v, [[]])[-1] or []) if e["midi"] is not None and not is_perc(v)]
        if notes: notes[-1]["art"] = "fermata"
