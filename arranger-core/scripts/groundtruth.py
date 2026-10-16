"""Score a transcription against the song's master tracks (official multitracks / stems), part by part.

usage: groundtruth.py OUT W TRACKS_DIR --map PART=TRACK[:kind] ... [--activity] [--device cuda|cpu]
  OUT         a build.py output (events.json)          W  the analysis dir (bars.json, audio.wav)
  TRACKS_DIR  the master tracks (mp3/wav, all the same length); they are aligned to W/audio.wav automatically
  --map       which track each transcribed part is scored against; kind = pitch (default: torchcrepe),
              bass (pyin, for low notes) or drums. TRACK is the file name without extension, e.g.
              --map V="Lead Vox" BV="Octave Vox" BASS=Bass:bass DR=Drums:drums
  --activity  print which track plays in which bar next to the transcribed parts (who plays when)

Pitched parts: per 16th where both sound, exact pitch and pitch class, octave errors, and 16ths where only one
side sounds (held through a breath, or a missed note). Drums: each 16th of the master drum track is classified by
the spectrum of its first 80 ms (kick 40-80 Hz, snare body 150-250 Hz, cymbals 7-10 kHz) and compared with the
part's sounds (band kits: bd* / s* / hh* rd* cr*; vocal percussion: B / Pf k / t ts Ksh): precision, recall, F.
Measure the yardstick before trusting it: plain onset bands count a snare's low end as kicks.
"""
import os, sys, json, glob, argparse
import numpy as np
import librosa

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("W"); ap.add_argument("tracks")
ap.add_argument("--map", nargs="+", default=[]); ap.add_argument("--activity", action="store_true")
ap.add_argument("--device", default=None)
a = ap.parse_args()
SR = 22050
bars = json.load(open(f"{a.W}/bars.json"))["bars"]
NB = max(int(k) for k in bars)
BEAT = float(np.median([bars[str(n + 1)]["t"] - bars[str(n)]["t"] for n in range(1, NB)])) / 4
Q = BEAT / 4
EV = json.load(open(f"{a.out}/events.json"))["events"]
files = {os.path.splitext(os.path.basename(f))[0]: f for f in sorted(glob.glob(f"{a.tracks}/*.mp3") + glob.glob(f"{a.tracks}/*.wav"))}
if not files: raise SystemExit(f"no mp3/wav in {a.tracks}")
Y = {k: librosa.load(f, sr=SR, mono=True)[0] for k, f in files.items()}

# ---------------------------------------------------------------- alignment: the tracks' sum against the mix
mix, _ = librosa.load(f"{a.W}/audio.wav", sr=SR, mono=True)
n = max(len(y) for y in Y.values()); summ = np.zeros(n)
for y in Y.values(): summ[:len(y)] += y
H = 256
e1 = librosa.onset.onset_strength(y=mix, sr=SR, hop_length=H); e2 = librosa.onset.onset_strength(y=summ, sr=SR, hop_length=H)
c = np.correlate(e1 - e1.mean(), e2 - e2.mean(), mode="full"); k0 = int((np.argmax(c) - (len(e2) - 1)) * H)
best, OFF = -1.0, k0
s0, s1 = int(0.25 * len(mix)), int(0.25 * len(mix)) + 40 * SR
for d in range(-700, 701, 5):
    k = k0 + d
    if s0 - k < 0 or s1 - k > len(summ): continue
    x, z = mix[s0:s1], summ[s0 - k:s1 - k]
    v = float(np.dot(x, z) / (np.linalg.norm(x) * np.linalg.norm(z) + 1e-9))
    if v > best: best, OFF = v, k
OFF /= SR
print(f"alignment: master tracks start {OFF:+.3f} s into the mix (waveform correlation {best:.2f})")


def bar_t(b, c=0): return bars[str(b)]["t"] + c * Q - OFF        # mix bar/16th -> time in the master tracks


# ---------------------------------------------------------------- who plays when
def part_bars(p):
    on = [0] * NB
    for nt in EV.get(p, []):
        for k in range(nt[2]):
            pos = nt[1] + k; b = nt[0] + pos // 16
            if 1 <= b <= NB and nt[3] is not None: on[b - 1] = 1
    return on


if a.activity:
    print("\nwho plays when (# loud, = soft, . faint; one character per bar)")
    for name, y in Y.items():
        r = []
        for b in range(1, NB + 1):
            seg = y[max(0, int(bar_t(b) * SR)):max(0, int((bar_t(b) + 16 * Q) * SR))]
            r.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -120.0)
        r = np.array(r); top = np.percentile(r, 95)
        print(f"  master {name[:20]:20s} |" + "".join("#" if x > top - 10 else "=" if x > top - 20 else "." if x > top - 35 else " "
                                                       for x in r) + "|")
    for p in EV:
        print(f"  score  {p[:20]:20s} |" + "".join("#" if x else " " for x in part_bars(p)) + "|")


# ---------------------------------------------------------------- pitched parts
def grid_of(p):
    g = {}
    for nt in EV[p]:
        if nt[3] is None or isinstance(nt[3], list): continue
        for k in range(nt[2]): pos = nt[1] + k; g[(nt[0] + pos // 16, pos % 16)] = nt[3]
    return g


def track_pitch(y, kind):
    if kind == "bass":
        f0, vf, _ = librosa.pyin(y, fmin=30, fmax=250, sr=SR, frame_length=4096, hop_length=256)
        t = librosa.frames_to_time(np.arange(len(f0)), sr=SR, hop_length=256); ok = vf & np.isfinite(f0)
    else:
        import torch, torchcrepe
        dev = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
        y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
        f0, per = torchcrepe.predict(torch.tensor(y16)[None], 16000, hop_length=160, fmin=60, fmax=1000, model="full",
                                     decoder=torchcrepe.decode.viterbi, return_periodicity=True, device=dev, batch_size=128)
        f0, per = f0[0].cpu().numpy(), per[0].cpu().numpy(); t = np.arange(len(f0)) * 0.01
        rms = librosa.feature.rms(y=y16, frame_length=640, hop_length=160)[0][:len(f0)]
        ok = (per > 0.5) & (rms > np.percentile(rms[rms > 0], 50) * 0.3)
    g = {}
    for b in range(1, NB + 1):
        for c in range(16):
            m = ok & (t >= bar_t(b, c)) & (t < bar_t(b, c) + Q)
            if m.sum() >= 2: g[(b, c)] = 69 + 12 * np.log2(np.median(f0[m]) / 440)
    return g


def score_pitch(p, track, kind):
    true, mine = track_pitch(Y[track], kind), grid_of(p)
    both = [k for k in true if k in mine]
    if not both: print(f"\n{p} vs {track}: nothing sounds in both"); return
    ex = np.mean([round(true[k]) == mine[k] for k in both]); pc = np.mean([round(true[k]) % 12 == mine[k] % 12 for k in both])
    print(f"\n{p} vs '{track}': {len(both)} 16ths in both | exact {ex:.1%} | pitch class {pc:.1%} | octave off {pc - ex:.1%}"
          f" | master sounds where the score rests: {len([k for k in true if k not in mine])}"
          f" | score sounds where the master is silent: {len([k for k in mine if k not in true])}")
    per_bar = {}
    for k in both: per_bar.setdefault(k[0], []).append(round(true[k]) % 12 == mine[k] % 12)
    worst = sorted((np.mean(v), b) for b, v in per_bar.items() if len(v) >= 4)[:12]
    print("   worst bars (pitch-class agreement): " + ", ".join(f"{b}: {s:.2f}" for s, b in worst))


# ---------------------------------------------------------------- drums
SOUND = {"kick": ("bd", "B"), "snare": ("s", "Pf", "k"), "cymbals": ("hh", "rd", "cr", "t", "ts", "Ksh")}


def score_drums(p, track):
    y = Y[track]; f = np.fft.rfftfreq(4096, 1 / SR); true = {k: set() for k in SOUND}
    for b in range(1, NB + 1):
        for c in range(16):
            i = int(bar_t(b, c) * SR); seg = y[max(0, i):i + int(0.08 * SR)]
            if len(seg) < 200: continue
            S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 4096))
            lo, mid, hi = (20 * np.log10(S[(f >= x) & (f < z)].mean() + 1e-9) for x, z in ((40, 80), (150, 250), (7000, 10000)))
            if lo > 12: true["kick"].add((b, c))
            if mid > 13 and mid - lo > -6: true["snare"].add((b, c))
            if hi > -15: true["cymbals"].add((b, c))
    mine = {k: set() for k in SOUND}
    for nt in EV[p]:
        snd = nt[3] if isinstance(nt[3], list) else []
        for k, pre in SOUND.items():
            if any(s == x or (len(x) > 1 and s.startswith(x)) or (x == "s" and s[:1] == "s" and not s.startswith("sh"))
                   for s in snd for x in pre): mine[k].add((nt[0], nt[1]))
    print(f"\n{p} vs '{track}' (hits per 16th, classified by spectrum):")
    for k in SOUND:
        tp = len(true[k] & mine[k]); pr = tp / max(1, len(mine[k])); rc = tp / max(1, len(true[k]))
        print(f"   {k:8s} master {len(true[k]):4d}  score {len(mine[k]):4d} | precision {pr:.0%} recall {rc:.0%} "
              f"F {2 * pr * rc / max(1e-9, pr + rc):.0%}")


for spec in a.map:
    part, _, rest = spec.partition("="); track, _, kind = rest.partition(":")
    if part not in EV: print(f"\n{part}: not in {a.out}/events.json"); continue
    if track not in Y: print(f"\n{track}: no such track in {a.tracks}"); continue
    score_drums(part, track) if kind == "drums" else score_pitch(part, track, kind or "pitch")
