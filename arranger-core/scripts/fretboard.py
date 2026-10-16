"""Fretted instruments: the chord shapes guitarists actually play, and string/fret numbers for a tablature staff.

    TUNINGS["guitar"]            open strings, lowest string first, as sounding MIDI numbers
    shape(sym, tuning, prev)     -> frets per string (-1 = muted) of a playable shape for a chord symbol
    pitches(frets, tuning)       -> the sounding notes of a shape, low to high
    fingering(seq, tuning)       -> per event, [(string, fret), ...]: a shortest path over hand positions

Strings are numbered from 0 = the lowest string here; MusicXML numbers them from 1 = the highest.
"""
import itertools
from functools import lru_cache
from engine import chord

TUNINGS = {"guitar": (40, 45, 50, 55, 59, 64), "bass": (28, 33, 38, 43), "ukulele": (67, 60, 64, 69)}
MAX_FRET = {"guitar": 15, "bass": 15, "ukulele": 12}

# movable shapes: frets relative to the root's fret on the root string (E shape: string 0, A shape: string 1)
E_SHAPE = {"": [0, 2, 2, 1, 0, 0], "m": [0, 2, 2, 0, 0, 0], "7": [0, 2, 0, 1, 0, 0], "m7": [0, 2, 0, 0, 0, 0],
           "maj7": [0, 2, 1, 1, 0, 0], "sus": [0, 2, 2, 2, 0, 0], "sus4": [0, 2, 2, 2, 0, 0],
           "7sus": [0, 2, 0, 2, 0, 0], "7sus4": [0, 2, 0, 2, 0, 0], "6": [0, 2, 2, 1, 2, 0], "m6": [0, 2, 2, 0, 2, 0]}
A_SHAPE = {"": [-1, 0, 2, 2, 2, 0], "m": [-1, 0, 2, 2, 1, 0], "7": [-1, 0, 2, 0, 2, 0], "m7": [-1, 0, 2, 0, 1, 0],
           "maj7": [-1, 0, 2, 1, 2, 0], "sus": [-1, 0, 2, 2, 3, 0], "sus4": [-1, 0, 2, 2, 3, 0],
           "sus2": [-1, 0, 2, 2, 0, 0], "7sus": [-1, 0, 2, 0, 3, 0], "7sus4": [-1, 0, 2, 0, 3, 0],
           "6": [-1, 0, 2, 2, 2, 2], "m6": [-1, 0, 2, 2, 1, 2], "dim": [-1, 0, 1, 2, 1, -1],
           "m7b5": [-1, 0, 1, 0, 1, -1], "dim7": [-1, 0, 1, 2, 1, 2]}
# open-position chords that are not an E or A shape at fret 0
OPEN = {"C": [-1, 3, 2, 0, 1, 0], "C7": [-1, 3, 2, 3, 1, 0], "Cmaj7": [-1, 3, 2, 0, 0, 0], "Cadd9": [-1, 3, 2, 0, 3, 0],
        "D": [-1, -1, 0, 2, 3, 2], "Dm": [-1, -1, 0, 2, 3, 1], "D7": [-1, -1, 0, 2, 1, 2], "Dm7": [-1, -1, 0, 2, 1, 1],
        "Dmaj7": [-1, -1, 0, 2, 2, 2], "Dsus4": [-1, -1, 0, 2, 3, 3], "Dsus": [-1, -1, 0, 2, 3, 3],
        "Dsus2": [-1, -1, 0, 2, 3, 0], "D6": [-1, -1, 0, 2, 0, 2], "G": [3, 2, 0, 0, 0, 3], "G7": [3, 2, 0, 0, 0, 1],
        "Gmaj7": [3, 2, 0, 0, 0, 2], "G6": [3, 2, 0, 0, 0, 0], "Fmaj7": [-1, -1, 3, 2, 1, 0], "B7": [-1, 2, 1, 2, 0, 2],
        "Eadd9": [0, 2, 2, 1, 0, 2], "Aadd9": [-1, 0, 2, 4, 2, 0]}


def pitches(frets, tuning=TUNINGS["guitar"]):
    return tuple(sorted(o + f for o, f in zip(tuning, frets) if f >= 0))


def _pos(frets):
    fr = [f for f in frets if f > 0]
    return min(fr) if fr else 0


def _ok(frets, c, tuning):
    """Sounds the chord: lowest note = the bass, every note a chord tone, root + 3rd (+ 7th) present."""
    ps = pitches(frets, tuning)
    if len(ps) < 3 or ps[0] % 12 != c["bass"]: return False
    pcs = {p % 12 for p in ps}
    need = {c["root"], c["third"], c["sev"]} - {None}
    return pcs <= c["tones"] | {c["bass"]} and need <= pcs


def _with_bass(frets, c, tuning):
    """A slash chord from a plain shape: put the bass on a muted low string (open or inside the shape), or mute
    low strings until the bass is the lowest note."""
    f = list(frets)
    low = next(i for i, x in enumerate(f) if x >= 0)
    fr = [x for x in f if x > 0]; lo, hi = (min(fr), max(fr)) if fr else (0, 3)
    for s in range(low - 1, -1, -1):
        for x in [0] + list(range(max(1, hi - 3), lo + 4)):
            if (tuning[s] + x) % 12 == c["bass"]:
                g = [-1] * s + [x] + f[s + 1:]
                return g
    while sum(x >= 0 for x in f) > 3:
        s = next(i for i, x in enumerate(f) if x >= 0)
        if (tuning[s] + f[s]) % 12 == c["bass"]: return f
        f[s] = -1
    return f


def _search(c, tuning, maxf):
    """Any playable shape: strings sounding from one string up to the top, a 4-fret window, at most 4 fingers
    (a barre on the lowest fret counts as one)."""
    best = []
    for w in range(0, maxf - 3):
        opts = []
        for o in tuning:
            fs = [x for x in [0] + list(range(max(1, w), w + 4)) if (o + x) % 12 in c["tones"] | {c["bass"]}]
            opts.append(fs)
        for first in range(len(tuning) - 2):
            for combo in itertools.product(*opts[first:]):
                f = [-1] * first + list(combo)
                fr = [x for x in f if x > 0]
                if fr and (max(fr) - min(fr) > 3 or len([x for x in fr if x > min(fr)]) + 1 > 4): continue
                if _ok(f, c, tuning): best.append(f)
        if best: break
    return best


@lru_cache(maxsize=None)
def _shapes(sym, tuning, maxf):
    c = chord(sym); q = c["q"]; plain = sym.split("/")[0]
    cands = []
    if plain in OPEN: cands.append((OPEN[plain], 0.0))
    for table, string in ((E_SHAPE, 0), (A_SHAPE, 1)):
        if q in table:
            r = (c["root"] - tuning[string]) % 12
            for base in (r, r + 12):
                f = [x + base if x >= 0 else -1 for x in table[q]]
                if max(f) <= maxf: cands.append((f, 0.6 * base + (2.0 if base >= 8 else 0.0) + (0.3 if string else 0)))
    out = []
    for f, cost in cands:
        if c["bass"] != c["root"] or not _ok(f, c, tuning): f = _with_bass(f, c, tuning)
        if _ok(f, c, tuning): out.append((f, cost + 0.4 * (6 - sum(x >= 0 for x in f))))
    if not out:
        out = [(f, 3.0 + 0.6 * _pos(f) + 0.4 * (6 - sum(x >= 0 for x in f))) for f in _search(c, tuning, maxf)]
    return out


def shape(sym, tuning=TUNINGS["guitar"], prev=None, maxf=12):
    """Frets per string (-1 = muted) for a chord symbol: an open chord, an E- or A-shape barre, or a searched
    shape, choosing the cheapest (low on the neck, many strings) near the previous shape's position."""
    cands = _shapes(sym, tuple(tuning), maxf)
    if not cands: raise ValueError(f"no playable shape for {sym!r}")
    p0 = _pos(prev) if prev else None
    return list(min(cands, key=lambda fc: fc[1] + (0.25 * abs(_pos(fc[0]) - p0) if p0 is not None else 0))[0])


@lru_cache(maxsize=None)
def places(ps, tuning, maxf):
    """Every way to play the notes ps (low to high) on distinct strings -> [((string, fret), ...), ...] in the order
    of ps, keeping fretted notes inside a 5-fret span."""
    out = []
    for strs in itertools.permutations(range(len(tuning)), len(ps)):
        fr = [p - tuning[s] for p, s in zip(ps, strs)]
        if min(fr) < 0 or max(fr) > maxf: continue
        f2 = [x for x in fr if x > 0]
        if f2 and max(f2) - min(f2) > 4: continue
        out.append(tuple(zip(strs, fr)))
    return out


def _cost(pl):
    f2 = [f for _, f in pl if f > 0]
    span = (max(f2) - min(f2)) if f2 else 0
    return span + 0.3 * (min(f2) if f2 else 0) + 0.05 * sum(1 for _, f in pl if f > 0)


def _hand(pl):
    f2 = [f for _, f in pl if f > 0]
    return min(f2) if f2 else None


def fingering(seq, tuning, maxf=15):
    """seq: [(pitches low to high, start in 16ths), ...] in time order -> per event the cheapest placement on the
    neck, found by a shortest path where moving the hand more than 2 frets costs (less after a rest), or None
    for an event that does not fit the instrument."""
    tuning = tuple(tuning)
    layers = []
    for ps, t in seq:
        c = places(tuple(ps), tuning, maxf)
        layers.append((c, t))
    best = []; prev = None
    for k, (cands, t) in enumerate(layers):
        if not cands:
            best.append(None); continue
        row = []
        for pl in cands:
            here = _cost(pl)
            if prev is None:
                row.append((here, None)); continue
            pc, pt, prow = prev
            gap = t - pt
            w = 1.0 if gap <= 4 else 0.5
            h = _hand(pl)
            def trans(q):
                hq = _hand(q)
                if h is None or hq is None: return 0.0
                d = abs(h - hq)
                return w * max(0, d - 2) + 0.05 * d
            j = min(range(len(pc)), key=lambda j: prow[j][0] + trans(pc[j]))
            row.append((here + prow[j][0] + trans(pc[j]), j))
        best.append((cands, row))
        prev = (cands, t, row)
    # backtrack each run of placeable events
    out = [None] * len(layers); k = len(layers) - 1
    while k >= 0:
        if best[k] is None: k -= 1; continue
        cands, row = best[k]
        j = min(range(len(row)), key=lambda j: row[j][0])
        while k >= 0 and best[k] is not None:
            cands, row = best[k]
            out[k] = cands[j]; j = row[j][1]; k -= 1
            if j is None: break
    return out
