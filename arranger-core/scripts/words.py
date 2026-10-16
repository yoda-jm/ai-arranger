"""Second opinion on the lyrics: run Whisper again on short clips of a vocal stem, one per bar range, and print each
word with the bar it starts in. Short clips stop Whisper from skipping or merging lines; compare two stems (lead and
vocals) and the first pass (W/words.json) and keep the reading most passes agree on.

    $PY words.py W 12-19 35-43 103-110 [--stem lead|vocals] [--language en] [--model medium]
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acap import Bars, stem

ap = argparse.ArgumentParser()
ap.add_argument("W"); ap.add_argument("ranges", nargs="+", help="bar ranges like 12-19")
ap.add_argument("--stem", default="lead"); ap.add_argument("--language"); ap.add_argument("--model", default="medium")
ap.add_argument("--device")
a = ap.parse_args()

import librosa, soundfile as sf, torch, whisper
dev = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
B = Bars(a.W)
y, sr = sf.read(stem(a.W, a.stem)); y = y.mean(1) if y.ndim > 1 else y
y = librosa.resample(y.astype(np.float32), orig_sr=sr, target_sr=16000)
model = whisper.load_model(a.model, device=dev)
for r in a.ranges:
    lo, hi = (int(x) for x in (r.split("-") + [r])[:2])
    t0 = max(0.0, B.start(lo) - 0.3)
    t1 = B.start(hi + 1) if hi + 1 in B else B.start(hi) + B.length(hi)
    out = model.transcribe(y[int(t0 * 16000):int(t1 * 16000)], language=a.language, word_timestamps=True,
                           condition_on_previous_text=False, temperature=0, fp16=False)   # fp16 breaks on GTX 16xx
    print(f"--- bars {lo}-{hi} ({a.stem})")
    for seg in out["segments"]:
        print("   " + " ".join(f"{w['word'].strip()}[{B.bar_at(t0 + w['start'])}]" for w in seg.get("words", [])))
