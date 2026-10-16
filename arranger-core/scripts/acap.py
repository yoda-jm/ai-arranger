"""Shared helpers for the a cappella toolkit: work-dir layout, bar map, note names, CQT / NNLS multi-pitch.

Work directory layout (created by analyze.py):
  W/audio.wav                     44.1 kHz stereo copy of the input
  W/stems/{vocals,drums,bass,other}.wav   Demucs htdemucs_ft
  W/stems/{lead,backing}.wav      karaoke split of the vocal stem (lead vs backing vocals)
  W/beats.json                    raw beats + downbeats from the beat tracker
  W/bars.json                     THE bar map: bar number -> start time + beat times (edit / re-run barmap.py)
  W/meta.json                     tuning, keys, tempo, durations
  W/lead_f0.npy                   lead pitch per 10 ms (MIDI float, tuning-corrected, nan = unvoiced)
  W/words.json                    Whisper word timestamps [[start, end, word], ...]
  W/drumgrid.json                 per bar: K/S/h strings, one char per 16th ('X' strong, 'x' weak, '.')
  W/report.md, W/draft.py         analysis report and editable transcription drafts (report.py)
"""
import os, json, re
import numpy as np

NAMES_FLAT = "C Db D Eb E F Gb G Ab A Bb B".split()
NAMES_SHARP = "C C# D D# E F F# G G# A A# B".split()
NAMES_MIX = "C C# D Eb E F F# G Ab A Bb B".split()
PC = {n: i for i, n in enumerate(NAMES_MIX)}
PC.update({"Db": 1, "D#": 3, "Gb": 6, "G#": 8, "A#": 10, "Cb": 11, "Fb": 4, "E#": 5, "B#": 0})
FIFTHS = {"C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "C#": 7,
          "F": -1, "Bb": -2, "Eb": -3, "Ab": -4, "Db": -5, "Gb": -6, "Cb": -7}
REL_MAJOR = {m + "m": NAMES_MIX[(PC[m] + 3) % 12] for m in NAMES_MIX + ["D#", "G#", "A#", "C#", "F#"]}
REL_MAJOR.update({"Am": "C", "Em": "G", "Bm": "D", "F#m": "A", "C#m": "E", "G#m": "B", "D#m": "F#", "A#m": "C#",
                  "Dm": "F", "Gm": "Bb", "Cm": "Eb", "Fm": "Ab", "Bbm": "Db", "Ebm": "Gb", "Abm": "Cb"})


def major_of(key):
    """'Bb' -> 'Bb', 'Gm' -> 'Bb' (relative major, used for key signature and scale)."""
    return REL_MAJOR[key] if key.endswith("m") else key


def names_for(key=None):
    if key is None: return NAMES_MIX
    f = FIFTHS.get(major_of(key), 0)
    return NAMES_SHARP if f > 0 else (NAMES_FLAT if f < 0 else NAMES_MIX)


def nm(m, key=None):
    m = int(round(m)); return names_for(key)[m % 12] + str(m // 12 - 1)


def pmidi(p):
    n, acc, o = re.fullmatch(r"([A-G])([#b]?)(-?\d)", p).groups()
    return {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[n] + {"#": 1, "b": -1, "": 0}[acc] + 12 * (int(o) + 1)


# ---------------------------------------------------------------- paths
STEMS = ("vocals", "drums", "bass", "other", "lead", "backing")


def stem(W, name):
    """Path of a stem by short name, or a path relative to W / absolute path."""
    if name in STEMS or name == "audio":
        return f"{W}/audio.wav" if name == "audio" else f"{W}/stems/{name}.wav"
    return name if os.path.isabs(name) or os.path.exists(name) else f"{W}/{name}"


def load_json(p, default=None):
    if not os.path.exists(p): return default
    return json.load(open(p))


def save_json(obj, p):
    json.dump(obj, open(p, "w"), indent=1)


def meta(W):
    return load_json(f"{W}/meta.json", {})


def update_meta(W, **kw):
    m = meta(W); m.update(kw); save_json(m, f"{W}/meta.json"); return m


def tuning(W):
    """Tuning offset in semitones (e.g. +0.12 = 12 cents sharp of A440)."""
    return meta(W).get("tuning_cents", 0) / 100


# ---------------------------------------------------------------- bar map
class Bars:
    """Bar map: bar number -> start time and beat times. Positions inside a bar are in 16ths (pos 0..sub*beats-1)."""

    def __init__(self, W):
        d = load_json(f"{W}/bars.json")
        if d is None: raise SystemExit(f"{W}/bars.json missing: run barmap.py first")
        self.meter = tuple(d.get("meter", (4, 4)))
        self.beats_per_bar = d.get("beats_per_bar", self.meter[0])
        self.sub = d.get("sub", 4)                # 16ths per beat (4 for x/4, 6 for compound x/8 with dotted-quarter beats)
        self.L = self.sub * self.beats_per_bar    # 16ths per bar
        self.B = {int(k): v for k, v in d["bars"].items()}
        self.end = d.get("end")
        self.numbers = sorted(self.B)

    def __contains__(self, n): return n in self.B

    def start(self, n): return self.B[n]["t"]

    def length(self, n):
        if n + 1 in self.B: return self.B[n + 1]["t"] - self.B[n]["t"]
        if self.end and n == self.numbers[-1]: return self.end - self.B[n]["t"]
        return self.B[n]["t"] - self.B[n - 1]["t"]

    def beats(self, n):
        b = list(self.B[n].get("beats") or [])
        if len(b) != self.beats_per_bar:
            a, ln = self.start(n), self.length(n)
            b = [a + ln * k / self.beats_per_bar for k in range(self.beats_per_bar)]
        return b + [self.start(n) + self.length(n)]

    def t(self, n, pos):
        """Time of 16th position `pos` in bar n (pos may run past the bar: continues into following bars)."""
        while pos >= self.L and n + 1 in self.B: pos -= self.L; n += 1
        while pos < 0 and n - 1 in self.B: n -= 1; pos += self.L
        bt = self.beats(n)
        k, f = divmod(pos, self.sub)
        k = int(k)
        if k >= self.beats_per_bar: return bt[-1] + (pos - self.L) * self.length(n) / self.L
        return bt[k] + (bt[k + 1] - bt[k]) * f / self.sub

    def span(self, n, pos, dur):
        return self.t(n, pos), self.t(n, pos + dur)

    def bpm(self, n):
        return 60 * self.beats_per_bar / self.length(n)

    def bar_at(self, t):
        """Bar number containing time t (None before the first bar)."""
        best = None
        for n in self.numbers:
            if self.start(n) <= t: best = n
            else: break
        return best


class Layout:
    """The measures of a built arrangement (events.json meta) on two clocks:
    - score tempo (section tempos, beats per minute in the arrangement's beat unit): time(measure, pos)
    - the recording (needs a Bars map): rec(measure, rec_bar, pos) -> position in the recording bar's 16ths, through the
      section's warp when the melody was re-timed into another meter (or scaled when only the bar length differs)."""

    def __init__(self, meta, bars=None):
        self.bar = meta["bar"]; self.beat = meta.get("beat", 4); self.B = bars
        self.secs = meta.get("sections") or []
        self.of, self.t0 = {}, {}
        t, tempo = 0.0, None
        for s in self.secs:
            tempo = s.get("tempo") or tempo or 100
            d = 60.0 / (tempo * self.beat)              # seconds per 16th
            for k in range(s["nbars"]):
                self.of[s["measure"] + k] = s; self.t0[s["measure"] + k] = (t, d); t += self.bar * d
        self.total = t

    def time(self, measure, pos):
        while pos >= self.bar and measure + 1 in self.t0: pos -= self.bar; measure += 1
        t, d = self.t0[measure]; return t + pos * d

    def rec(self, measure, pos):
        """Position in 16ths of the recording bar for 16th `pos` of `measure` (may exceed the bar: Bars.t continues)."""
        s = self.of.get(measure); w = s and s.get("warp"); L = self.B.L if self.B else 16
        if w:
            if pos >= w[-1]: return len(w) - 1 + (pos - w[-1]) * (len(w) - 1) / w[-1]
            k = max(i for i in range(len(w) - 1) if w[i] <= pos)
            return k + (pos - w[k]) / (w[k + 1] - w[k])
        return pos * L / self.bar if self.bar != L else pos


# ---------------------------------------------------------------- audio features
def load(path, sr=22050, mono=True):
    import librosa
    y, _ = librosa.load(path, sr=sr, mono=mono); return y


def cqt(y, sr, hop, lo_midi, n_semitones, tune=0.0, bpo=36):
    """Magnitude CQT, 3 bins per semitone; bin 3*(m-lo) is centred on MIDI m (tuning-corrected)."""
    import librosa
    return np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.midi_to_hz(lo_midi + tune),
                              n_bins=n_semitones * bpo // 12, bins_per_octave=bpo))


def harmonic_dict(cands, lo, nbins, decay=0.8, nh=8):
    """Dictionary of harmonic templates (one column per candidate MIDI pitch) for NNLS multi-pitch."""
    D = []
    for m in cands:
        v = np.zeros(nbins)
        for h in range(1, nh + 1):
            k = int(round((m - lo) * 3 + 36 * np.log2(h)))
            for d in (-1, 0, 1):
                if 0 <= k + d < nbins: v[k + d] += (decay ** (h - 1)) * (1 if d == 0 else .4)
        D.append(v / (np.linalg.norm(v) + 1e-12))
    return np.array(D).T


def nnls_pitches(D, cands, x, thr=0.3):
    """Active pitches in a spectrum slice x (NNLS on harmonic templates); adjacent semitones collapsed."""
    from scipy.optimize import nnls
    act, _ = nnls(D, x)
    if act.max() <= 0: return []
    act /= act.max()
    sel = [m for j, m in enumerate(cands) if act[j] > thr]
    out = []
    for m in sel:
        if out and m - out[-1] == 1:
            if act[cands.index(m)] > act[cands.index(out[-1])]: out[-1] = m
        else: out.append(m)
    return out


def salience(C, nb, weights=((1, 1), (2, .7), (3, .5))):
    """Harmonic-sum salience (rows 0..nb-1 of C, 3 bins per semitone)."""
    S = np.zeros((nb, C.shape[1]))
    for h, w in weights:
        o = int(round(36 * np.log2(h)))
        seg = C[o:o + nb]; S[:seg.shape[0]] += w * seg
    return S


# ---------------------------------------------------------------- chords
QUALITIES = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11),
             "sus4": (0, 5, 7), "7sus": (0, 5, 7, 10), "dim": (0, 3, 6), "6": (0, 4, 7, 9), "m6": (0, 3, 7, 9),
             "add9": (0, 2, 4, 7), "sus2": (0, 2, 7), "aug": (0, 4, 8), "dim7": (0, 3, 6, 9), "m7b5": (0, 3, 6, 10),
             "9": (0, 4, 7, 10, 2), "m9": (0, 3, 7, 10, 2), "maj9": (0, 4, 7, 11, 2)}
MAJ_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def key_of(chroma_vec):
    """Krumhansl key estimate: returns (key_name, score, runner_up). Minor keys as 'Gm'."""
    sc = []
    for k in range(12):  # small major bias: pop songs are mostly major, and the relative minor is the usual confusion
        sc.append((np.corrcoef(np.roll(MAJ_PROFILE, k), chroma_vec)[0, 1] + 0.04, NAMES_MIX[k]))
        sc.append((np.corrcoef(np.roll(MIN_PROFILE, k), chroma_vec)[0, 1], NAMES_MIX[k] + "m"))
    sc.sort(reverse=True)
    return sc[0][1], float(sc[0][0]), sc[1][1]


def chord_templates(quals=("", "m", "7", "m7", "maj7", "sus4", "dim")):
    T = {}
    for r in range(12):
        for q in quals:
            v = np.zeros(12); iv = QUALITIES[q]
            for i, x in enumerate(iv): v[(r + x) % 12] = 1.0 if i < 3 else 0.7
            T[(r, q)] = v / np.linalg.norm(v)
    return T


PENALTY = {"": 0, "m": 0, "7": 0.02, "m7": 0.02, "maj7": 0.03, "sus4": 0.06, "7sus": 0.06, "dim": 0.04}


def guess_chord(ch, bass_pc, key, T, prior=0.04):
    """Best chord symbol for a 12-d chroma vector with an observed bass pitch class (or None).
    Diatonic chords of `key` get a small bonus; 4-note qualities a small penalty. Returns [(score, symbol)] best first."""
    ch = ch / (np.linalg.norm(ch) + 1e-9)
    sc_ = set((PC[major_of(key)] + i) % 12 for i in (0, 2, 4, 5, 7, 9, 11)) if key else set()
    names = names_for(key)
    out = []
    for (r, q), v in T.items():
        s = float(v @ ch)
        tones = {(r + i) % 12 for i in QUALITIES[q]}
        if sc_ and tones <= sc_: s += prior
        s -= PENALTY.get(q, 0.03)
        if bass_pc is not None:
            if bass_pc == r: s += 0.03
            elif bass_pc in tones: s += 0.01
            else: s -= 0.05
        sym = names[r] + q
        if bass_pc is not None and bass_pc != r and bass_pc in tones: sym += "/" + names[bass_pc]
        out.append((s, sym))
    out.sort(reverse=True)
    return out


def bars_arg(s, B):
    """'1-8' / '12' / 'all' -> list of bar numbers present in the bar map."""
    if s in (None, "all"): return B.numbers
    a, b = re.fullmatch(r"(-?\d+)(?:-(-?\d+))?", str(s)).groups()
    a = int(a); b = int(b) if b is not None else a
    return [n for n in B.numbers if a <= n <= b]
