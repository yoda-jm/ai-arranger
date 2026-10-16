"""Build the bar map W/bars.json from tracked beats/downbeats (beat_this, fallback librosa).

usage: barmap.py W [--meter 4/4] [--anchor TIME=BAR] [--fix BAR=TIME,BAR=TIME | --fix file.json]
                   [--tracker beat_this|librosa] [--end TIME] [--retrack]

  --anchor 4.52=1   the downbeat nearest 4.52 s becomes bar 1 (earlier bars get 0, -1, ...). Default: first downbeat = 1.
  --fix 53=93.80,54=95.90   force bar starts (rubato / tempo changes the tracker got wrong); beats inside the fixed
                    bars are re-spread evenly and snapped to tracked beats within 60 ms.
  --meter 3/4 | 6/8 (6/8 = 2 dotted-quarter beats per bar, 6 sixteenths per beat).
Prints the tempo per bar run and every irregular bar (wrong number of beats = tracker problem or real meter change).
"""
import sys, os, argparse, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acap import load_json, save_json, update_meta

ap = argparse.ArgumentParser()
ap.add_argument("W"); ap.add_argument("--meter", default="4/4"); ap.add_argument("--anchor")
ap.add_argument("--fix"); ap.add_argument("--tracker", default="beat_this"); ap.add_argument("--end", type=float)
ap.add_argument("--retrack", action="store_true"); ap.add_argument("--device", default=None)
a = ap.parse_args()
W = a.W
num, den = map(int, a.meter.split("/"))
if den == 8 and num % 3 == 0: N, SUB = num // 3, 6
else: N, SUB = num, 16 // den


def track():
    audio = f"{W}/audio.wav"
    if a.tracker == "beat_this":
        try:
            import torch
            from beat_this.inference import File2Beats
            dev = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
            f2b = File2Beats(checkpoint_path="final0", device=dev, dbn=False)
            b, d = f2b(audio)
            return dict(tracker="beat_this", beats=[float(x) for x in b], downbeats=[float(x) for x in d])
        except ImportError:
            print("beat_this not installed -> librosa fallback (no tempo-change tracking, guessed downbeats)")
    import librosa
    y, sr = librosa.load(audio, sr=22050)
    env = librosa.onset.onset_strength(y=y, sr=sr)
    _, fr = librosa.beat.beat_track(onset_envelope=env, sr=sr)
    b = librosa.frames_to_time(fr, sr=sr)
    # downbeat phase: the beat phase (mod N) with the strongest low-frequency onsets (kick / bass)
    S = np.abs(librosa.stft(y)); f = librosa.fft_frequencies(sr=sr)
    low = np.maximum(0, np.diff(S[f < 150].sum(0), prepend=0))
    st = [low[librosa.time_to_frames(b[p::N], sr=sr)].sum() for p in range(N)]
    p = int(np.argmax(st))
    return dict(tracker="librosa", beats=[float(x) for x in b], downbeats=[float(x) for x in b[p::N]])


bj = f"{W}/beats.json"
T = load_json(bj)
if T is None or a.retrack:
    T = track(); save_json(T, bj)
beats = np.array(T["beats"]); downs = np.array(T["downbeats"])
period = float(np.median(np.diff(beats)))
I = sorted({int(np.argmin(abs(beats - d))) for d in downs})

# ---- group beats into bars, using downbeats but enforcing N beats per bar
starts = [I[0]]; irregular = []
k = 1
while k < len(I):
    gap = I[k] - starts[-1]
    if gap < N:
        nxt = next((j for j in I[k + 1:] if j - starts[-1] >= N), None)
        if nxt is not None and nxt - starts[-1] == N: k += 1; continue   # spurious downbeat (double-rate section)
        if gap >= max(2, N - 1) and (nxt is None or nxt - I[k] == N):
            starts.append(I[k]); irregular.append((I[k], gap)); k += 1; continue  # genuinely short bar
        k += 1; continue
    while I[k] - starts[-1] >= 2 * N: starts.append(starts[-1] + N)
    gap = I[k] - starts[-1]
    if gap != N: irregular.append((I[k], gap))
    starts.append(I[k]); k += 1
while starts[-1] + N < len(beats): starts.append(starts[-1] + N)
pre = []
s0 = starts[0]
while s0 - N >= 0: s0 -= N; pre.append(s0)
starts = sorted(pre) + starts
pickup = starts[0]  # beats before the first full bar


def beat_t(i):
    return float(beats[i]) if i < len(beats) else float(beats[-1] + (i - len(beats) + 1) * period)


bars = []
for j, s in enumerate(starts):
    e = starts[j + 1] if j + 1 < len(starts) else s + N
    bt = [beat_t(i) for i in range(s, e)]
    if e - s != N:  # tracker on another metrical level here (or a real odd bar): spread N beats evenly, flag it
        a0, a1 = beat_t(s), beat_t(e); bt = [a0 + (a1 - a0) * q / N for q in range(N)]
    bars.append(dict(t=beat_t(s), beats=bt, nbeats=e - s))
end = a.end or (beat_t(starts[-1] + N))

# ---- numbering
if a.anchor:
    ta, nb = a.anchor.split("="); ta = float(ta); nb = int(nb)
    j0 = int(np.argmin([abs(b["t"] - ta) for b in bars])); first = nb - j0
else:
    j0 = len(pre); first = 1 - j0
B = {first + j: b for j, b in enumerate(bars)}

# ---- manual fixes
if a.fix:
    fx = load_json(a.fix) if a.fix.endswith(".json") else dict(x.split("=") for x in a.fix.split(","))
    fx = {int(k): float(v) for k, v in fx.items()}
    for n, t in fx.items():
        B.setdefault(n, dict(t=t, beats=[], nbeats=N))["t"] = t
    ns = sorted(B)
    for n in ns:
        if n in fx or (n + 1) in fx:
            a0 = B[n]["t"]; a1 = B[n + 1]["t"] if n + 1 in B else a0 + N * period
            want = [a0 + (a1 - a0) * q / N for q in range(N)]
            snap = []
            for w in want:
                i = int(np.argmin(abs(beats - w)))
                snap.append(float(beats[i]) if abs(beats[i] - w) < 0.06 and (not snap or beats[i] > snap[-1]) else w)
            snap[0] = a0
            B[n]["beats"] = snap; B[n]["nbeats"] = N
    if max(fx) == max(B) and not a.end: end = B[max(B)]["t"] + N * period

ns = sorted(B)
for n in ns[:-1]:
    if B[n + 1]["t"] <= B[n]["t"]: raise SystemExit(f"bar {n + 1} does not start after bar {n}: check --fix values")
save_json(dict(meter=[num, den], beats_per_bar=N, sub=SUB, tracker=T["tracker"], end=end,
               bars={str(n): B[n] for n in ns}), f"{W}/bars.json")

# ---- summary
bpm = {n: 60 * N / ((B[n + 1]["t"] if n + 1 in B else end) - B[n]["t"]) for n in ns}
print(f"{len(ns)} bars ({ns[0]}..{ns[-1]}), meter {num}/{den}, tracker {T['tracker']}, "
      f"bar {ns[0]} at {B[ns[0]]['t']:.2f}s" + (f", bar 1 at {B[1]['t']:.2f}s" if 1 in B else ""))
if pickup: print(f"pickup: {pickup} beat(s) before bar {ns[0]} (from {beats[0]:.2f}s)")
runs = []
for n in ns:
    if runs and abs(bpm[n] - runs[-1][2]) < 4: runs[-1][1] = n; runs[-1][3].append(bpm[n]); continue
    runs.append([n, n, bpm[n], [bpm[n]]])
print("tempo runs (bars: bpm):", "  ".join(f"{r[0]}-{r[1]}: {np.median(r[3]):.0f}" for r in runs))
bad = [n for n in ns if B[n]["nbeats"] != N]
if bad: print("IRREGULAR bars (tracked beats != %d; beats re-spread evenly, check the bar lengths by ear):" % N, ", ".join(f"{n} ({B[n]['nbeats']} beats @ {B[n]['t']:.2f}s)" for n in bad))
update_meta(W, meter=[num, den], first_bar=ns[0], last_bar=ns[-1],
            tempo_runs=[[r[0], r[1], round(float(np.median(r[3])), 1)] for r in runs])
