"""Per-bar analysis report + editable transcription drafts.

usage: report.py W            -> W/report.md (read this first) and W/draft.py (LEAD, BASS, CHORDS, OTHER_TOP, KEYS)

report.md: header (tuning, key, tempo runs, irregular bars), a per-bar table (level of each stem, key, chord guess
per half bar, drums, repeat detection with transposition, words), instrument lines that quote the vocal tune
(transposition-aware), and backing-vocal pitches per 8th where backing vocals are present.
draft.py: one line per bar in the engine's token syntax, with syllables already distributed on the note onsets.
Drafts are automatic: verify every phrase you use (look.py roll / nnls), especially octaves, repeated notes and lyrics.
"""
import sys, os, json, re, collections
import numpy as np, librosa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acap import (Bars, stem, load_json, meta, nm, tuning, cqt, harmonic_dict, nnls_pitches, key_of,
                  chord_templates, guess_chord, PC, major_of, NAMES_MIX as NAMES)

W = sys.argv[1]
B = Bars(W); M = meta(W); TUNE = tuning(W); L = B.L
NB = B.numbers
SR = 22050; HOP = 256
FR = 100  # f0 frame rate
HALF = 2 if B.beats_per_bar % 2 == 0 else 1


def exists(s): return os.path.exists(stem(W, s))


def slot_times(n):
    return [B.t(n, s) for s in range(L + 1)]


SLOTS = [(n, s) for n in NB for s in range(L)]
ST = np.array([[B.t(n, s), B.t(n, s + 1)] for n, s in SLOTS])

# ---------------------------------------------------------------- levels per bar
LEV = {}
loaded = {}
for s in ("lead", "backing", "drums", "bass", "other"):
    if not exists(s): continue
    y = librosa.load(stem(W, s), sr=SR)[0]; loaded[s] = y
    r = librosa.feature.rms(y=y, hop_length=HOP)[0]
    LEV[s] = {n: float(np.sqrt(np.mean(r[int(B.start(n) * SR / HOP):max(int(B.start(n) * SR / HOP) + 1,
                                                                          int((B.start(n) + B.length(n)) * SR / HOP))] ** 2)))
              for n in NB}
gmax = max(max(v.values()) for v in LEV.values())


def lev_char(s, n):
    if s not in LEV: return "?"
    db = 20 * np.log10(LEV[s][n] / gmax + 1e-9)
    return " " if db < -40 else "." if db < -30 else ":" if db < -22 else "=" if db < -14 else "#"


# ---------------------------------------------------------------- note segmentation helper
def notes_from_slots(pitch, onset, fill_gap=1, jump=0.7, min_run=2):
    """pitch: per-slot float midi or nan; onset: per-slot bool. Returns [(start_slot, end_slot, midi)].
    A new note starts on an onset, after a rest, or on a pitch change that lasts >= min_run slots (so 1-slot
    scoops and glides are absorbed). Unvoiced gaps of <= fill_gap slots (consonants) are bridged."""
    p = pitch.copy(); on = onset.copy(); n = len(p); i = 0
    while i < n:
        if np.isnan(p[i]):
            j = i
            while j < n and np.isnan(p[j]): j += 1
            if 0 < i and j < n and j - i <= fill_gap:
                p[i:j] = p[i - 1]
                if on[i:j].any(): on[j] = True
                on[i:j] = False
            i = j
        else: i += 1
    notes = []; cur = None
    for i in range(n):
        if np.isnan(p[i]):
            if cur is not None: notes.append(cur); cur = None
            continue
        new = cur is None or on[i]
        if not new:
            ref = np.median(cur[2][-4:])
            if abs(p[i] - ref) > jump:
                new = all(i + k < n and not np.isnan(p[i + k]) and abs(p[i + k] - p[i]) < jump
                          for k in range(1, min_run))
        if new:
            if cur is not None: notes.append(cur)
            cur = [i, i + 1, [p[i]]]
        else:
            cur[1] = i + 1; cur[2].append(p[i])
    if cur is not None: notes.append(cur)
    out = []
    for a, b, ps in notes:
        ps = np.array(ps); core = ps[len(ps) // 3:] if len(ps) >= 3 else ps
        out.append((a, b, float(np.median(core))))
    return out


def snap(notes, key_of_slot, strict=0.25):
    """Round note pitches, preferring the scale of the local key: a chromatic pitch is kept only when the sung
    pitch is within `strict` semitones of it (singers scoop and sag; pop melodies are mostly diatonic)."""
    out = []
    for a, b, f in notes:
        k = key_of_slot(a); mj = PC[major_of(k)]
        sc = {(mj + i) % 12 for i in (0, 2, 4, 5, 7, 9, 11)}
        r = int(round(f))
        if r % 12 not in sc and abs(f - r) > strict:
            cands = [q for q in (r - 1, r + 1) if q % 12 in sc]
            if cands: r = min(cands, key=lambda q: abs(q - f))
        out.append((a, b, r))
    return out


def slot_pitch(notes):
    p = np.full(len(SLOTS), np.nan)
    for a, b, m in notes: p[a:b] = m
    return p


def onset_slots(times):
    on = np.zeros(len(SLOTS), bool)
    for t in times:
        j = int(np.searchsorted(ST[:, 0], t + 1e-6)) - 1
        for k in (j, j + 1):
            if 0 <= k < len(SLOTS):
                d = ST[k, 1] - ST[k, 0]
                if ST[k, 0] - 0.45 * d <= t < ST[k, 0] + 0.5 * d: on[k] = True
    return on


def tokens(notes, key_at):
    """notes over global slots -> {bar: (token string, [onset note indices])}."""
    per = {n: [] for n in NB}
    occ = [None] * len(SLOTS)
    for k, (a, b, m) in enumerate(notes):
        for i in range(a, min(b, len(SLOTS))): occ[i] = k
    out = {}
    for bi, n in enumerate(NB):
        toks = []; ons = []; s = 0
        base = bi * L
        while s < L:
            k = occ[base + s]
            e = s + 1
            while e < L and occ[base + e] == k: e += 1
            if k is None: toks.append(f"r:{e - s}")
            else:
                a, b, m = notes[k]
                tie = b > base + e
                toks.append(f"{nm(m, key_at(n))}{'~' if tie else ''}:{e - s}")
                if a == base + s: ons.append(k)
            s = e
        out[n] = (" ".join(toks), ons)
    return out


# ---------------------------------------------------------------- keys per window
# harmony chroma: accompaniment only (the lead's passing tones bias the guess); vocals if the song has no band
acc = [(s, g) for s, g in (("other", 1), ("bass", .5)) if s in loaded and max(LEV[s].values()) > 0.05 * gmax]
ymix = sum(loaded[s] * g for s, g in (acc or [(s, 1) for s in ("lead", "backing") if s in loaded]))
CH = librosa.feature.chroma_cqt(y=ymix, sr=SR, hop_length=HOP, tuning=TUNE * 3)
if "bass" in loaded: CHB = librosa.feature.chroma_cqt(y=loaded["bass"], sr=SR, hop_length=HOP, tuning=TUNE * 3)


def chroma(C, t0, t1):
    a, b = int(t0 * SR / HOP), max(int(t0 * SR / HOP) + 1, int(t1 * SR / HOP))
    return C[:, a:b].mean(1)


barch = {n: chroma(CH, B.start(n), B.start(n) + B.length(n)) for n in NB}
KEY = {}
for i, n in enumerate(NB):
    win = [barch[m] for m in NB[max(0, i - 3):i + 5]]
    KEY[n] = key_of(np.sum(win, 0))[0]
# smooth: a key must hold >= 4 bars
seq = [KEY[n] for n in NB]
for it in range(2):
    runs = []
    for n, k in zip(NB, seq):
        if runs and runs[-1][0] == k: runs[-1][1].append(n)
        else: runs.append([k, [n]])
    for j, (k, ns) in enumerate(runs):
        if len(ns) < 4 and len(runs) > 1:
            nk = runs[j - 1][0] if j > 0 else runs[j + 1][0]
            for n in ns: seq[NB.index(n)] = nk
KEY = dict(zip(NB, seq))
key_at = lambda n: KEY.get(n, M.get("key", "C"))

# ---------------------------------------------------------------- bass draft (NNLS per 16th on the bass stem)
BASS = {}; bass_notes = []
if "bass" in loaded:
    lo = 24; C = cqt(loaded["bass"], SR, HOP, lo, 60, TUNE)
    cands = list(range(28, 61)); D = harmonic_dict(cands, lo, C.shape[0])
    g = C.max(); pitch = np.full(len(SLOTS), np.nan)
    for i, (t0, t1) in enumerate(ST):
        x = np.median(C[:, int(t0 * SR / HOP) + 1:max(int(t1 * SR / HOP), int(t0 * SR / HOP) + 2)], 1)
        if not np.isfinite(x).all() or x.max() < 0.04 * g: continue   # slots past the end of the audio
        ps = nnls_pitches(D, cands, x, 0.5)
        if ps: pitch[i] = ps[0]
    env = librosa.onset.onset_strength(y=loaded["bass"], sr=SR, hop_length=HOP)
    ons = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, delta=0.15, units="time")
    bass_notes = snap(notes_from_slots(pitch, onset_slots(ons), fill_gap=0, jump=0.5, min_run=1), lambda a: key_at(NB[a // L]), 0.5)
    T = tokens(bass_notes, key_at)
    BASS = {n: T[n][0] for n in NB}

# ---------------------------------------------------------------- top line of the "other" stem (instrument hooks)
OTHER = {}; other_notes = []
if "other" in loaded:
    lo = 48; C = cqt(loaded["other"], SR, HOP, lo, 72, TUNE)
    cands = list(range(55, 97)); D = harmonic_dict(cands, lo, C.shape[0])
    g = C.max(); pitch = np.full(len(SLOTS), np.nan)
    for i, (t0, t1) in enumerate(ST):
        x = np.median(C[:, int(t0 * SR / HOP) + 1:max(int(t1 * SR / HOP), int(t0 * SR / HOP) + 2)], 1)
        if not np.isfinite(x).all() or x.max() < 0.05 * g: continue
        ps = nnls_pitches(D, cands, x, 0.45)
        if ps: pitch[i] = max(ps)
    env = librosa.onset.onset_strength(y=loaded["other"], sr=SR, hop_length=HOP)
    ons = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, delta=0.2, units="time")
    other_notes = snap(notes_from_slots(pitch, onset_slots(ons), fill_gap=0, min_run=1), lambda a: key_at(NB[a // L]), 0.5)
    T = tokens(other_notes, key_at)
    OTHER = {n: T[n][0] for n in NB}


# ---------------------------------------------------------------- chords per half bar (then keys re-read from the chords)
TPL = chord_templates()
bp = slot_pitch(bass_notes)


def bass_pc(bi, n, s0, s1):
    seg = bp[bi * L + s0: bi * L + s1]
    if np.any(~np.isnan(seg)):
        w = collections.Counter()
        for j, v in enumerate(seg):
            if not np.isnan(v): w[int(v) % 12] += 1.5 if j < 2 else 1
        return w.most_common(1)[0][0]
    if "bass" in loaded and LEV["bass"][n] > 0.05 * gmax:
        return int(np.argmax(chroma(CHB, B.t(n, s0), B.t(n, s1))))
    return None


def all_chords():
    C_, A_ = {}, {}
    for bi, n in enumerate(NB):
        row = []; alt = []
        for h in range(HALF):
            s0, s1 = h * L // HALF, (h + 1) * L // HALF
            r = guess_chord(chroma(CH, B.t(n, s0), B.t(n, s1)), bass_pc(bi, n, s0, s1), key_at(n), TPL)
            row.append(r[0][1]); alt.append(r[1][1] if r[0][0] - r[1][0] < 0.03 else "")
        C_[n] = row; A_[n] = alt
    return C_, A_


CHORDS, CHALT = all_chords()


def chord_pcs(sym):
    s_ = sym.split("/")[0]; r = s_[:2] if len(s_) > 1 and s_[1] in "#b" else s_[:1]
    from acap import QUALITIES
    return PC[r], {(PC[r] + i) % 12 for i in QUALITIES[s_[len(r):]]}


# key from the chords: the major key whose scale holds most chords of an 8-bar window, tonic / dominant favoured
kseq = []
for i, n in enumerate(NB):
    win = [c for m in NB[max(0, i - 2):i + 6] for c in CHORDS[m]]
    best = None
    for k in range(12):
        sc_ = {(k + x) % 12 for x in (0, 2, 4, 5, 7, 9, 11)}
        sc = 0
        for c in win:
            r, t = chord_pcs(c)
            sc += (t <= sc_) + 0.5 * (r == k) + 0.25 * (r == (k + 7) % 12)
        if best is None or sc > best[0] + 1e-9: best = (sc, k)
    kseq.append(NAMES[best[1]] if best[0] > 0 else KEY[n])
for it in range(2):
    runs = []
    for n, k in zip(NB, kseq):
        if runs and runs[-1][0] == k: runs[-1][1].append(n)
        else: runs.append([k, [n]])
    for j, (k, ns) in enumerate(runs):
        if len(ns) < 4 and len(runs) > 1:
            nk = runs[j - 1][0] if j > 0 else runs[j + 1][0]
            for n in ns: kseq[NB.index(n)] = nk
KEY = dict(zip(NB, kseq))
CHORDS, CHALT = all_chords()  # again with the better key prior (spelling + diatonic bonus)

# ---------------------------------------------------------------- lead melody draft
f0 = np.load(f"{W}/lead_f0.npy") if os.path.exists(f"{W}/lead_f0.npy") else None
words = load_json(f"{W}/words.json", [])
LEAD = {}
lead_notes = []
if f0 is not None:
    pitch = np.full(len(SLOTS), np.nan)
    for i, (t0, t1) in enumerate(ST):
        a, b = int(t0 * FR), int(t1 * FR); q = max(0, (b - a) // 5)
        seg = f0[a + q:max(b - q, a + q + 1)]
        if len(seg) and np.mean(~np.isnan(seg)) >= 0.5: pitch[i] = np.nanmedian(seg)
    y16 = librosa.load(stem(W, "lead"), sr=16000)[0]
    env = librosa.onset.onset_strength(y=y16, sr=16000, hop_length=160)
    ons = librosa.onset.onset_detect(onset_envelope=env, sr=16000, hop_length=160, delta=0.2, units="time")
    on = onset_slots(list(ons) + [w[0] for w in words])
    lead_notes = snap(notes_from_slots(pitch, on), lambda a: key_at(NB[a // L]))
    T = tokens(lead_notes, key_at)
    # syllables on note onsets
    try:
        import pyphen
        lang = {"en": "en_US", "fr": "fr_FR", "de": "de_DE", "es": "es_ES", "it": "it_IT", "nl": "nl_NL",
                "pt": "pt_PT"}.get(M.get("language") or "en", "en_US")
        HY = pyphen.Pyphen(lang=lang)
        syllab = lambda w: HY.inserted(w).split("-")
    except ImportError:
        syllab = lambda w: [w]
    note_t = [ST[a][0] for a, b, m in lead_notes]
    syl = {}
    for ws, we, wd in words:
        wd = re.sub(r"[^\w'’-]", "", wd)
        if not wd: continue
        ks = [k for k, t in enumerate(note_t) if ws - 0.12 <= t < max(we - 0.05, ws + 0.05) and k not in syl]
        if not ks:
            near = [k for k in range(len(note_t)) if k not in syl and abs(note_t[k] - ws) < 0.25]
            ks = near[:1]
        if not ks: continue
        sy = [x for x in syllab(wd) if x]
        if len(sy) > len(ks): sy = sy[:len(ks) - 1] + ["".join(sy[len(ks) - 1:])]
        for j, k in enumerate(ks):
            if j >= len(sy): syl[k] = "_"; continue
            if len(sy) == 1: syl[k] = sy[0]
            elif j == 0: syl[k] = sy[0] + "-"
            elif j == len(sy) - 1: syl[k] = "-" + sy[j]
            else: syl[k] = "-" + sy[j] + "-"
    for n in NB:
        tok, onk = T[n]
        ly = [syl.get(k, "_") for k in onk]
        LEAD[n] = (tok, " ".join(ly) if any(x != "_" for x in ly) else "")

WORDS_BAR = collections.defaultdict(list)
for ws, we, wd in words:
    n = B.bar_at(ws)
    if n is not None: WORDS_BAR[n].append(wd)

# ---------------------------------------------------------------- repeats (2-bar windows, transposition-aware)
REP = {}
for i, n in enumerate(NB):
    if i + 1 >= len(NB): break
    x = barch[n] / (np.linalg.norm(barch[n]) + 1e-9); x2 = barch[NB[i + 1]] / (np.linalg.norm(barch[NB[i + 1]]) + 1e-9)
    if lev_char("other", n) == " " and lev_char("bass", n) == " " and lev_char("lead", n) == " ": continue
    best = (0, None, 0)
    for j in range(0, i - 1):
        m = NB[j]; y1 = barch[m] / (np.linalg.norm(barch[m]) + 1e-9); y2 = barch[NB[j + 1]] / (np.linalg.norm(barch[NB[j + 1]]) + 1e-9)
        for k in range(12):
            sc = (np.roll(y1, k) @ x + np.roll(y2, k) @ x2) / 2 - (0.02 if k else 0)
            if sc > best[0]: best = (sc, m, k)
    if best[0] > 0.93:
        k = best[2] if best[2] <= 6 else best[2] - 12
        REP[n] = f"{best[1]}{'+' if k > 0 else ''}{k if k else ''}"

# ---------------------------------------------------------------- instrument lines that quote the vocal tune
lp = slot_pitch(lead_notes); op = slot_pitch(other_notes)
ECHO = []
if lead_notes and other_notes:
    WN = 2 * L
    for i in range(0, len(NB) - 1):
        o = op[i * L:i * L + WN]
        if np.sum(~np.isnan(o)) < L // 2: continue
        best = (0, None, 0, 0)
        vo = ~np.isnan(o)
        for j in range(0, len(NB) - 1):
            l = lp[j * L:j * L + WN]
            vl = ~np.isnan(l)
            if vl.sum() < L // 2: continue
            for k in range(12):
                # pitch-class match per slot, tolerating +-1 slot of timing
                hit = np.zeros(len(o), bool); dd = []
                for sh in (0, -1, 1):
                    l2 = np.roll(l, sh)
                    m_ = vo & ~np.isnan(l2) & (((o - l2 - k) % 12) == 0) & ~hit
                    hit |= m_; dd += list((o - l2)[m_])
                sc = hit.sum() / max(vo.sum(), vl.sum())
                if sc > best[0] + 0.02:
                    best = (sc, NB[j], k, int(np.median(dd)) if dd else k)
        if best[0] >= 0.6 and not (best[1] == NB[i] and best[3] % 12 == 0 and lev_char("lead", NB[i]) != " "):
            ECHO.append((NB[i], best[1], best[3], best[0]))
runs = []
for n, m, d, sc in ECHO:
    if runs and runs[-1]["n1"] + 1 == n and runs[-1]["m1"] + 1 == m and runs[-1]["d"] == d:
        runs[-1].update(n1=n, m1=m); runs[-1]["sc"].append(sc)
    else: runs.append(dict(n0=n, n1=n, m0=m, m1=m, d=d, sc=[sc]))

# ---------------------------------------------------------------- backing vocals NNLS per 8th
BK = []
if "backing" in loaded:
    lo = 36; C = cqt(loaded["backing"], SR, HOP, lo, 60, TUNE)
    cands = list(range(45, 88)); D = harmonic_dict(cands, lo, C.shape[0]); g = C.max()
    for n in NB:
        if lev_char("backing", n) in (" ", "."): continue
        row = []
        for s in range(0, L, 2):
            t0, t1 = B.t(n, s), B.t(n, s + 2)
            x = np.median(C[:, int(t0 * SR / HOP) + 1:max(int(t1 * SR / HOP), int(t0 * SR / HOP) + 2)], 1)
            row.append("/".join(nm(m, key_at(n)) for m in nnls_pitches(D, cands, x, 0.3)[::-1]) if x.max() > 0.04 * g else ".")
        BK.append((n, row))

# ---------------------------------------------------------------- write report.md
G = load_json(f"{W}/drumgrid.json", {})
out = []
P = out.append
P(f"# Analysis report: {os.path.basename(M.get('song', W))}\n")
home = collections.Counter(KEY.values()).most_common(1)[0][0]
P(f"- duration {M.get('duration', '?')} s, tuning {M.get('tuning_cents', 0):+d} cents (already corrected in f0/CQT), "
  f"main key **{home}** (most bars; minor keys show as their relative major)")
P(f"- meter {B.meter[0]}/{B.meter[1]}, bars {NB[0]}..{NB[-1]} (bar 1 at {B.start(1):.2f}s)" if 1 in B else
  f"- meter {B.meter[0]}/{B.meter[1]}, bars {NB[0]}..{NB[-1]}")
P("- tempo runs (bars: bpm): " + "  ".join(f"{a}-{b}: {t:g}" for a, b, t in M.get("tempo_runs", [])))
bj = load_json(f"{W}/bars.json")
irr = [int(k) for k, v in bj["bars"].items() if v.get("nbeats", B.beats_per_bar) != B.beats_per_bar]
if irr: P(f"- **irregular bars** (beat tracker on another metrical level, beats re-spread evenly; verify): {irr}")
kc = [(n, KEY[n]) for i, n in enumerate(NB) if i == 0 or KEY[NB[i - 1]] != KEY[n]]
P("- key regions (from the chords; boundaries can be 1-3 bars early or late): " + ", ".join(f"bar {n}: {k}" for n, k in kc))
P("")
P("Levels per bar: **L**ead **K**(backing) **d**rums **b**ass **o**ther, ' ' silent . : = # loud. "
  "Chords: one per half bar, from chroma + recorded bass (`X|Y` = close runner-up). "
  "`≈n+k` = this 2-bar window repeats bars n..n+1 transposed k semitones (harmony only).\n")
P("```")
P(f"{'bar':>4} {'time':>6} {'bpm':>4} LKdbo {'key':4} {'chords':24} {'≈rep':7} {'kick / snare (16ths)':38} words")
for n in NB:
    ch = "  ".join((c + ("|" + al if al else "")).ljust(11) for c, al in zip(CHORDS[n], CHALT[n]))
    lv = "".join(lev_char(s, n) for s in ("lead", "backing", "drums", "bass", "other"))
    g = G.get(str(n)); dr = f"K {g['K'].replace('.', '-')} S {g['S'].replace('.', '-')}" if g and "x" in (g['K'] + g['S']).lower() else ""
    wd = " ".join(WORDS_BAR.get(n, []))[:44]
    P(f"{n:>4} {B.start(n):6.2f} {B.bpm(n):4.0f} {lv} {key_at(n):4} {ch:24} {REP.get(n, ''):7} {dr:38} {wd}")
P("```\n")
P("## Instrument lines that quote a vocal phrase (top line of the `other` stem vs the lead draft)\n")
if runs:
    for r in runs:
        P(f"- bars {r['n0']}-{r['n1'] + 1}: like lead bars {r['m0']}-{r['m1'] + 1}, {r['d']:+d} semitones "
          f"(match {np.mean(r['sc']):.2f})")
else: P("- none found")
P("\n## Backing vocals: pitches per 8th (NNLS on the backing stem; high to low)\n")
P("```")
for n, row in BK: P(f"b{n:<4} " + " ".join(x.ljust(11) for x in row))
P("```\n")
P("Drafts: `draft.py` (LEAD tokens + syllables, BASS, CHORDS, OTHER_TOP, KEYS). Zoom with `look.py` (roll / nnls / chords / drums).")
open(f"{W}/report.md", "w").write("\n".join(out) + "\n")

# ---------------------------------------------------------------- write draft.py
d = ['"""Automatic transcription drafts (report.py). Copy what you need into your song file and FIX it:',
     "octaves, repeated notes, syllables ('_' = no syllable), chords (check against BASS).",
     'Token syntax: PITCH:DUR16 (r = rest, ~ = tie into the next note). One entry per recording bar."""', ""]
d.append("KEYS = {" + ", ".join(f"{n}: {k!r}" for n, k in kc) + "}")
d.append("\nLEAD = {  # bar: (tokens, syllables)   # time | whisper words")
for n in NB:
    if n in LEAD and LEAD[n][0] != f"r:{L}":
        d.append(f"    {n}: ({LEAD[n][0]!r}, {LEAD[n][1]!r}),  # {B.start(n):.2f}s | {' '.join(WORDS_BAR.get(n, []))}")
d.append("}\n\nBASS = {  # recorded bass, concert pitch (often an octave below the sung bass)")
for n in NB:
    if BASS.get(n, f"r:{L}") != f"r:{L}": d.append(f"    {n}: {BASS[n]!r},")
d.append("}\n\nCHORDS = {")
for n in NB: d.append(f"    {n}: {CHORDS[n]!r},")
d.append("}\n\nOTHER_TOP = {  # highest line of the instrument stem (hooks, fills, counter-melodies)")
for n in NB:
    if OTHER.get(n, f"r:{L}") != f"r:{L}": d.append(f"    {n}: {OTHER[n]!r},")
d.append("}")
open(f"{W}/draft.py", "w").write("\n".join(d) + "\n")
print(open(f"{W}/report.md").read()[:1200])
print(f"wrote {W}/report.md and {W}/draft.py")
