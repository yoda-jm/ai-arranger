"""The checks of the evaluation that arranger-core's groundtruth.py does not cover, recomputed from this folder.

usage (from the repository root):  .venv/bin/python examples/code-monkey/evaluation/extra_checks.py

1. lyrics: the transcription's words (../lyrics.txt) against the JoCo wiki's (lyrics_reference.txt), word by word
2. the verse riff: Electric Guitar 2, top pitch classes per 8th, bars 41-44, next to the transcription's chord symbols
3. the pre-chorus and chorus chords: Electric Guitar 4 per half bar, bars 17-28
4. A or A minor at the end of chorus 2: C against C# in guitars 2, 4 and 5, per half bar, bars 73-80
5. the harmony vocal: its interval above the lead vocal, per 16th where both sing
"""
import os, re, sys, json, difflib
from collections import Counter
import numpy as np
import librosa

HERE = os.path.dirname(os.path.abspath(__file__)); SONG = os.path.dirname(HERE)
T = os.path.join(HERE, "master-tracks"); SR = 22050
sys.path.insert(0, SONG)
import song as S                                   # noqa: E402  the transcription's chords (CH[bar])
bars = json.load(open(os.path.join(SONG, "work", "bars.json")))["bars"]; Q = 0.37497 / 4
NM = "C C# D D# E F F# G G# A A# B".split()


def load(name): return librosa.load(os.path.join(T, name + ".mp3"), sr=SR, mono=True)[0]


# ---------------------------------------------------------------- 1. lyrics
def words(path):    # spelling-only differences ("'cause"/"cause", "goddamn"/"god damned") are not errors
    return re.findall(r"[a-z]+(?:'[a-z]+)*", open(path).read().lower().replace("goddamn", "god damned"))


print("1. LYRICS: transcription (lyrics.txt) against the JoCo wiki (lyrics_reference.txt)")
a, b = words(os.path.join(SONG, "lyrics.txt")), words(os.path.join(HERE, "lyrics_reference.txt"))
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if op != "equal":
        ctx = " ".join(a[max(0, i1 - 4):i1])
        print(f"   ...{ctx} [transcription: {' '.join(a[i1:i2]) or '-'}] [wiki: {' '.join(b[j1:j2]) or '-'}]")

# ---------------------------------------------------------------- alignment of the master tracks to the mix
mix, _ = librosa.load(os.path.join(SONG, "work", "audio.wav"), sr=SR, mono=True)
names = ["Lead Vox", "Harmony Vox", "Electric Guitar 2", "Electric Guitar 4", "Electric Guitar 5"]
Y = {n: load(n) for n in names}
summ = sum(Y.values())
e1 = librosa.onset.onset_strength(y=mix, sr=SR, hop_length=256); e2 = librosa.onset.onset_strength(y=summ, sr=SR, hop_length=256)
c = np.correlate(e1 - e1.mean(), e2 - e2.mean(), mode="full"); OFF = (np.argmax(c) - (len(e2) - 1)) * 256 / SR
print(f"\nmaster tracks start {OFF:+.3f} s into the mix")


def t_of(b, c=0): return bars[str(b)]["t"] + c * Q - OFF


def chroma(y, b, c0, c1):
    seg = y[int(t_of(b, c0) * SR):int(t_of(b, c1) * SR)]
    C = librosa.feature.chroma_cqt(y=seg, sr=SR, hop_length=256, fmin=librosa.note_to_hz("E1"), n_octaves=6)
    return C.mean(1) if C.size else np.zeros(12)


def top(v, n=3): return " ".join(NM[i] for i in np.argsort(v)[::-1][:n])


# ---------------------------------------------------------------- 2-3. guitars and chords
print("\n2. VERSE RIFF: Electric Guitar 2, top pitch classes per 8th (the record) | the transcription's chords")
for b in (41, 42, 43, 44):
    print(f"   bar {b}: " + " | ".join(top(chroma(Y['Electric Guitar 2'], b, k, k + 2)) for k in range(0, 16, 2))
          + f"   || {' '.join(S.CH[b])}")
print("\n3. PRE-CHORUS AND CHORUS: Electric Guitar 4 per half bar | the transcription's chords")
for b in range(17, 29):
    print(f"   bar {b}: " + " | ".join(top(chroma(Y['Electric Guitar 4'], b, k, k + 8)) for k in (0, 8)) + f"   || {' '.join(S.CH[b])}")

# ---------------------------------------------------------------- 4. A or Am
print("\n4. END OF CHORUS 2: C (A minor) against C# (A major) in guitars 2+4+5, per half bar | transcription")
for b in range(73, 81):
    cells = []
    for k in (0, 8):
        v = sum(chroma(Y[n], b, k, k + 8) for n in ("Electric Guitar 2", "Electric Guitar 4", "Electric Guitar 5"))
        cells.append(f"C {v[0]:.2f} / C# {v[1]:.2f} -> {'minor' if v[0] > v[1] else 'major'}")
    print(f"   bar {b}: " + " | ".join(cells) + f"   || {' '.join(S.CH[b])}")


# ---------------------------------------------------------------- 5. harmony vocal
def f0_grid(y):
    import torch, torchcrepe
    y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
    f0, per = torchcrepe.predict(torch.tensor(y16)[None], 16000, hop_length=160, fmin=70, fmax=1000, model="full",
                                 decoder=torchcrepe.decode.viterbi, return_periodicity=True,
                                 device="cuda" if torch.cuda.is_available() else "cpu", batch_size=128)
    f0, per = f0[0].cpu().numpy(), per[0].cpu().numpy(); t = np.arange(len(f0)) * 0.01
    rms = librosa.feature.rms(y=y16, frame_length=640, hop_length=160)[0][:len(f0)]
    ok = (per > 0.5) & (rms > np.percentile(rms[rms > 0], 50) * 0.3); g = {}
    for b in range(1, 125):
        for k in range(16):
            m = ok & (t >= t_of(b, k)) & (t < t_of(b, k) + Q)
            if m.sum() >= 3: g[(b, k)] = 69 + 12 * np.log2(np.median(f0[m]) / 440)
    return g


lead, harm = f0_grid(Y["Lead Vox"]), f0_grid(Y["Harmony Vox"])
iv = Counter(round(harm[k] - lead[k]) for k in harm if k in lead)
names_iv = {3: "minor 3rd", 4: "major 3rd", 5: "4th", 7: "5th", 8: "minor 6th", 9: "major 6th", 12: "octave", 0: "unison"}
print("\n5. HARMONY VOCAL: interval above the lead, per 16th where both sing (the transcription has no harmony part)")
tot = sum(iv.values())
for k, n in iv.most_common(8): print(f"   {k:+3d} semitones ({names_iv.get(k, '')}): {n / tot:.0%}")
print("   bars:", ", ".join(f"{a}-{b}" for a, b in [(24, 33), (36, 40), (64, 73), (76, 79), (108, 117), (120, 124)]),
      "(sounding in", len({k[0] for k in harm}), "bars)")
