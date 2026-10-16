"""Zoom tools on bars of the recording (W = analysis dir, BARS = '17-24' or '5', recording bar numbers).

  look.py W roll STEM BARS [--lo 40 --hi 88] [--f0] [--part OUTDIR:VOICE] [--out x.png]
        harmonic-salience piano roll with bar / beat / 16th lines -> PNG (open it with the Read tool).
        --f0 overlays the lead pitch, --part overlays an arranged voice from OUTDIR/events.json (transcription check)
  look.py W nnls STEM BARS [--lo 48 --hi 93 --thr 0.3 --div 8]   multi-pitch per 8th (high to low), text
  look.py W f0 BARS                     lead pitch per 16th (MIDI float -> note), onsets '*', words
  look.py W chords BARS [--div 2]       top chord candidates per half bar (or per beat with --div 4) + bass
  look.py W drums BARS                  kick / snare / hat per 16th
  look.py W bp STEM BARS [--minvel 0.3] basic-pitch notes on the 16th grid (needs analyze.py --basic-pitch)
  look.py W clip BARS [--stem audio] [--out x.wav]   cut the audio of these bars (for the human to listen)
STEM: vocals drums bass other lead backing audio (or a path).
"""
import sys, os, json, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acap import (Bars, stem, nm, tuning, cqt, harmonic_dict, nnls_pitches, salience, chord_templates, guess_chord,
                  load_json, bars_arg, meta)

ap = argparse.ArgumentParser()
ap.add_argument("W"); ap.add_argument("cmd"); ap.add_argument("args", nargs="*")
ap.add_argument("--lo", type=int); ap.add_argument("--hi", type=int); ap.add_argument("--thr", type=float, default=0.3)
ap.add_argument("--div", type=int); ap.add_argument("--f0", action="store_true"); ap.add_argument("--part")
ap.add_argument("--out"); ap.add_argument("--minvel", type=float, default=0.3); ap.add_argument("--stem", default="audio")
ap.add_argument("--key")
a = ap.parse_args()
W = a.W; B = Bars(W); TUNE = tuning(W); L = B.L
import librosa
SR = 22050; HOP = 256


def need(n):
    if len(a.args) < n: raise SystemExit(__doc__)


def span(bs):
    return B.start(bs[0]), B.start(bs[-1]) + B.length(bs[-1])


if a.cmd == "roll":
    need(2); st, bs = a.args[0], bars_arg(a.args[1], B)
    lo, hi = a.lo or 40, a.hi or 88
    t0, t1 = span(bs); t0 = max(0, t0)
    sr = 44100; hop = 256
    y, _ = librosa.load(stem(W, st), sr=sr, offset=t0, duration=t1 - t0)
    nb = (hi - lo) * 3
    C = cqt(y, sr, hop, lo, hi - lo + 24, TUNE)
    Sx = librosa.amplitude_to_db(salience(C, nb) / (salience(C, nb).max() + 1e-9), ref=1, top_db=35)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(min(60, 4.2 * len(bs)), (hi - lo) * 0.22 + 1))
    ax.imshow(Sx, origin="lower", aspect="auto", extent=[t0, t1, lo - 1 / 6, hi - 1 / 6], cmap="magma")
    for n in bs:
        for k in range(L):
            ax.axvline(B.t(n, k), color="w", lw=1.6 if k == 0 else (0.7 if k % B.sub == 0 else 0.15), alpha=.7)
        ax.text(B.start(n), hi - 0.8, f"bar {n}", color="c", fontsize=11)
    for m in range(lo, hi): ax.axhline(m + 0.5, color="gray", lw=0.2, alpha=.5)
    ax.set_yticks(range(lo, hi)); ax.set_yticklabels([nm(m, a.key) for m in range(lo, hi)], fontsize=8)
    if a.f0 and os.path.exists(f"{W}/lead_f0.npy"):
        f0 = np.load(f"{W}/lead_f0.npy"); tt = np.arange(len(f0)) / 100; s = (tt >= t0) & (tt <= t1)
        ax.plot(tt[s], f0[s], "c.", ms=2)
    if a.part:
        od, v = a.part.split(":"); J = json.load(open(f"{od}/events.json"))
        for e in J["events"][v]:
            rec, s_, d_, m = e[:4]
            if rec in bs and not isinstance(m, list):
                ax.add_patch(plt.Rectangle((B.t(rec, s_), m - 0.45), B.t(rec, s_ + d_) - B.t(rec, s_) - 0.01, 0.9,
                                           fill=False, ec="lime", lw=1.5))
    out = a.out or f"{W}/roll_{os.path.basename(st).split('.')[0]}_{bs[0]}-{bs[-1]}.png"
    ax.set_xlim(t0, t1); plt.tight_layout(); plt.savefig(out, dpi=60); print(out)

elif a.cmd == "nnls":
    need(2); st, bs = a.args[0], bars_arg(a.args[1], B)
    lo_c, hi_c, div = a.lo or 48, a.hi or 93, a.div or 8
    y = librosa.load(stem(W, st), sr=SR)[0]; lo = 36
    C = cqt(y, SR, HOP, lo, 72, TUNE); cands = list(range(lo_c, hi_c + 1)); D = harmonic_dict(cands, lo, C.shape[0])
    g = C.max(); k = meta(W)
    for n in bs:
        row = []
        for s in range(div):
            t0, t1 = B.t(n, s * L / div), B.t(n, (s + 1) * L / div)
            x = np.median(C[:, int(t0 * SR / HOP) + 1:max(int(t1 * SR / HOP), int(t0 * SR / HOP) + 2)], 1)
            row.append("/".join(nm(m, a.key) for m in nnls_pitches(D, cands, x, a.thr)[::-1]) if x.max() > 0.03 * g else ".")
        print(f"b{n:<4}" + " ".join(r.ljust(14) for r in row))

elif a.cmd == "f0":
    need(1); bs = bars_arg(a.args[0], B)
    f0 = np.load(f"{W}/lead_f0.npy"); words = load_json(f"{W}/words.json", [])
    y = librosa.load(stem(W, "lead"), sr=16000)[0]
    env = librosa.onset.onset_strength(y=y, sr=16000, hop_length=160); env /= np.percentile(env, 99) + 1e-9
    for n in bs:
        row = []
        for s in range(L):
            t0, t1 = B.t(n, s), B.t(n, s + 1)
            seg = f0[int(t0 * 100):int(t1 * 100)]; v = seg[~np.isnan(seg)]
            o = env[max(0, int(t0 * 100) - 2):int(t0 * 100) + 3].max() if int(t0 * 100) + 3 < len(env) else 0
            row.append(("*" if o > 0.35 else " ") + (f"{nm(np.median(v), a.key)}{np.median(v) - round(np.median(v)):+.1f}"
                                                     if len(v) >= 0.4 * max(len(seg), 1) else ".").ljust(8))
        wd = " ".join(w[2] for w in words if B.start(n) <= w[0] < B.start(n) + B.length(n))
        print(f"b{n:<4}" + "".join(row) + f"| {wd}")

elif a.cmd == "chords":
    need(1); bs = bars_arg(a.args[0], B); div = a.div or 2
    yo = librosa.load(stem(W, "other"), sr=SR)[0]; yb = librosa.load(stem(W, "bass"), sr=SR)[0]
    ch = librosa.feature.chroma_cqt(y=yo + 0.5 * yb, sr=SR, hop_length=HOP)
    bc = librosa.feature.chroma_cqt(y=yb, sr=SR, hop_length=HOP)
    T = chord_templates(("", "m", "7", "m7", "maj7", "sus4", "7sus", "dim", "6", "add9", "m7b5"))
    key = a.key or meta(W).get("key")
    for n in bs:
        cells = []
        for h in range(div):
            t0, t1 = B.t(n, h * L / div), B.t(n, (h + 1) * L / div)
            s_ = slice(int(t0 * SR / HOP), max(int(t1 * SR / HOP), int(t0 * SR / HOP) + 1))
            bp = int(np.argmax(bc[:, s_].mean(1)))
            r = guess_chord(ch[:, s_].mean(1), bp, key, T)[:3]
            cells.append(f"[bass {nm(bp + 48, key)[:-1]}] " + " ".join(f"{sym}({sc:.2f})" for sc, sym in r))
        print(f"b{n:<4}" + " | ".join(cells))

elif a.cmd == "drums":
    need(1); G = load_json(f"{W}/drumgrid.json", {})
    for n in bars_arg(a.args[0], B):
        g = G.get(str(n))
        if g: print(f"b{n:<4} K {g['K']}  S {g['S']}  h {g['h']}")

elif a.cmd == "bp":
    need(2); st, bs = a.args[0], bars_arg(a.args[1], B)
    csv = f"{W}/midi/{st}.csv"
    if not os.path.exists(csv): raise SystemExit(f"{csv} missing: run analyze.py ... --basic-pitch --only bp")
    notes = [tuple(map(float, l.split(","))) for l in open(csv)]
    lo, hi = a.lo or 0, a.hi or 127
    for n in bs:
        row = []
        for s, t, p, v in notes:
            if v < a.minvel or not (lo <= p <= hi): continue
            if not (B.t(n, -0.5) <= s < B.t(n, L - 0.5)): continue
            q = min(range(L), key=lambda k: abs(B.t(n, k) - s))
            d16 = B.length(n) / L
            row.append((q, int(p), max(1, round((t - s) / d16))))
        row.sort(key=lambda r: (r[0], -r[1]))
        print(f"b{n:<4}" + " ".join(f"{q}:{nm(p, a.key)}({d})" for q, p, d in row))

elif a.cmd == "clip":
    need(1); bs = bars_arg(a.args[0], B); t0, t1 = span(bs)
    out = a.out or f"{W}/clip_{bs[0]}-{bs[-1]}.wav"
    import subprocess
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{max(0, t0):.3f}", "-t", f"{t1 - t0:.3f}",
                    "-i", stem(W, a.stem), out], check=True)
    print(out)
else:
    raise SystemExit(__doc__)
