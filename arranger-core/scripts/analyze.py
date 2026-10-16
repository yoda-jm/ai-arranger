"""One-shot analysis of a song for a cappella arranging. Every step is cached (skipped when its output exists).

usage: analyze.py SONG.mp3 W [--lyrics lyrics.txt] [--meter 4/4] [--anchor TIME=BAR] [--device cuda|cpu]
                  [--whisper medium] [--basic-pitch] [--force step,step] [--only step,step]

steps: wav sep kara bars tune f0 words drums bp(optional) report
  wav    ffmpeg -> W/audio.wav (44.1 kHz stereo)
  sep    Demucs htdemucs_ft -> W/stems/{vocals,drums,bass,other}.wav
  kara   karaoke Mel-RoFormer on the vocal stem -> W/stems/lead.wav (lead), W/stems/backing.wav (backing vocals)
  bars   beat_this beats/downbeats -> W/bars.json (barmap.py; re-run it alone with --anchor/--fix to correct)
  tune   tuning offset (cents vs A440) + global key -> W/meta.json
  f0     torchcrepe lead pitch -> W/lead_f0.npy (10 ms frames, MIDI, tuning-corrected)
  words  Whisper word timestamps on the vocal stem (prompted with the lyrics) -> W/words.json
  drums  kick / snare / hat onsets per 16th -> W/drumgrid.json
  bp     basic-pitch note CSVs per stem -> W/midi/*.csv (optional, for look.py bp)
  report report.py -> W/report.md + W/draft.py
"""
import sys, os, argparse, subprocess, shutil, glob, time, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acap import stem, load_json, save_json, update_meta, Bars, key_of, tuning

ap = argparse.ArgumentParser()
ap.add_argument("song"); ap.add_argument("W"); ap.add_argument("--lyrics"); ap.add_argument("--meter", default="4/4")
ap.add_argument("--anchor"); ap.add_argument("--device"); ap.add_argument("--whisper", default=None)
ap.add_argument("--basic-pitch", action="store_true"); ap.add_argument("--force", default="")
ap.add_argument("--only", default="")
a = ap.parse_args()
W = os.path.abspath(a.W); os.makedirs(f"{W}/stems", exist_ok=True)
PY = sys.executable; BIN = os.path.dirname(PY)
MODELS = os.path.expanduser(os.environ.get("ACAP_MODELS", "~/.cache/acappella/models"))
FORCE = set(filter(None, a.force.split(","))); ONLY = set(filter(None, a.only.split(",")))
try:
    import torch; DEV = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
except ImportError:
    DEV = a.device or "cpu"


def need(step, *outs):
    if ONLY and step not in ONLY: return False
    if step in FORCE: return True
    return not all(os.path.exists(o) for o in outs)


def run(cmd, **kw):
    print("  $", " ".join(map(str, cmd))[:200], flush=True)
    r = subprocess.run(list(map(str, cmd)), capture_output=True, text=True, **kw)
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-3000:]); raise SystemExit(f"failed: {cmd[0]}")
    return r


def step(name):
    print(f"== {name}  ({time.strftime('%H:%M:%S')})", flush=True)


# ---------------------------------------------------------------- wav
if need("wav", f"{W}/audio.wav"):
    step("wav")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.song, "-ar", "44100", "-ac", "2", f"{W}/audio.wav"])

# ---------------------------------------------------------------- Demucs 4 stems
S4 = [stem(W, s) for s in ("vocals", "drums", "bass", "other")]
if need("sep", *S4):
    step("sep (Demucs htdemucs_ft)")
    run([PY, "-m", "demucs", "-n", "htdemucs_ft", "-d", DEV, "--segment", "7", "-o", f"{W}/sep", f"{W}/audio.wav"])
    for s in ("vocals", "drums", "bass", "other"):
        shutil.move(f"{W}/sep/htdemucs_ft/audio/{s}.wav", stem(W, s))
    shutil.rmtree(f"{W}/sep", ignore_errors=True)

# ---------------------------------------------------------------- karaoke split lead / backing
if need("kara", stem(W, "lead"), stem(W, "backing")):
    step("kara (Mel-RoFormer karaoke)")
    os.makedirs(MODELS, exist_ok=True); tmp = f"{W}/kara_tmp"; shutil.rmtree(tmp, ignore_errors=True)
    exe = os.path.join(BIN, "audio-separator")
    run([exe if os.path.exists(exe) else "audio-separator", stem(W, "vocals"),
         "-m", os.environ.get("ACAP_KARAOKE", "mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt"),
         "--model_file_dir", MODELS, "--output_dir", tmp, "--output_format", "WAV"])
    lead = glob.glob(f"{tmp}/*(Vocals)*.wav"); back = glob.glob(f"{tmp}/*(Instrumental)*.wav")
    if not lead or not back: raise SystemExit(f"karaoke outputs not found in {tmp}: {os.listdir(tmp)}")
    shutil.move(lead[0], stem(W, "lead")); shutil.move(back[0], stem(W, "backing")); shutil.rmtree(tmp)

# ---------------------------------------------------------------- bars
if need("bars", f"{W}/bars.json"):
    step("bars (beat_this)")
    cmd = [PY, f"{HERE}/barmap.py", W, "--meter", a.meter] + (["--anchor", a.anchor] if a.anchor else [])
    if "bars" in FORCE: cmd.append("--retrack")
    print(run(cmd).stdout)

# ---------------------------------------------------------------- tuning + key
if need("tune", f"{W}/meta.json") or "tuning_cents" not in load_json(f"{W}/meta.json", {}):
    if not ONLY or "tune" in ONLY:
        step("tune")
        import librosa
        tv = []
        for s in ("vocals", "other"):
            y, sr = librosa.load(stem(W, s), sr=22050)
            if np.abs(y).max() > 1e-3: tv.append(librosa.estimate_tuning(y=y, sr=sr))  # fraction of a semitone
        cents = int(round(100 * float(np.mean(tv)))) if tv else 0
        y = sum(librosa.load(stem(W, s), sr=22050)[0] * g for s, g in (("other", 1), ("bass", .7), ("vocals", .7)))
        ch = librosa.feature.chroma_cqt(y=y, sr=22050).mean(1)
        k, sc, k2 = key_of(ch)
        dur = librosa.get_duration(path=f"{W}/audio.wav")
        update_meta(W, tuning_cents=cents, key=k, key_score=round(sc, 3), key_runner_up=k2, duration=round(dur, 2),
                    song=os.path.abspath(a.song), lyrics=os.path.abspath(a.lyrics) if a.lyrics else None)
        print(f"  tuning {cents:+d} cents, key {k} (runner-up {k2}), {dur:.1f}s")

# ---------------------------------------------------------------- lead f0 (torchcrepe)
if need("f0", f"{W}/lead_f0.npy"):
    step("f0 (torchcrepe)")
    import torch, torchcrepe, librosa
    y, sr = librosa.load(stem(W, "lead"), sr=16000)
    x = torch.tensor(y)[None]
    f0, per = torchcrepe.predict(x, sr, 160, 65, 1100, "full" if DEV == "cuda" else "tiny", return_periodicity=True,
                                 batch_size=1024, device=DEV, decoder=torchcrepe.decode.viterbi)
    per = torchcrepe.filter.median(per, 3); f0 = torchcrepe.filter.mean(f0, 3)
    f0 = f0[0].cpu().numpy(); per = per[0].cpu().numpy()
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=160, center=True)[0][:len(f0)]
    m = librosa.hz_to_midi(f0) - tuning(W); m[(per < 0.45) | (rms < 0.01)] = np.nan
    np.save(f"{W}/lead_f0.npy", m)
    print(f"  {len(m)} frames, range {np.nanmin(m):.1f}-{np.nanmax(m):.1f}")

# ---------------------------------------------------------------- words (Whisper)
if need("words", f"{W}/words.json"):
    step("words (Whisper)")
    import whisper, difflib, re
    model = whisper.load_model(a.whisper or ("medium" if DEV == "cuda" else "small"), device=DEV)
    # no initial_prompt: prompting with the lyrics makes Whisper skip whole verses
    r = model.transcribe(stem(W, "vocals"), word_timestamps=True, fp16=False, condition_on_previous_text=False,
                         temperature=0)
    words = [[round(w["start"], 3), round(w["end"], 3), w["word"].strip()] for s in r["segments"] for w in s["words"]]
    if a.lyrics:  # respell recognised words with the lyrics file (timing kept from Whisper)
        norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower())
        lw = open(a.lyrics).read().split()
        sm = difflib.SequenceMatcher(a=[norm(w[2]) for w in words], b=[norm(x) for x in lw], autojunk=False)
        fixed = 0
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    fixed += words[i][2] != lw[j]; words[i][2] = lw[j]
        print(f"  respelled {fixed} words from the lyrics file")
    save_json(words, f"{W}/words.json"); update_meta(W, language=r.get("language"))
    print(f"  {len(words)} words, language {r.get('language')}")

# ---------------------------------------------------------------- drum grid
if need("drums", f"{W}/drumgrid.json"):
    step("drums")
    import librosa
    B = Bars(W); sr = 22050; hop = 128
    y, _ = librosa.load(stem(W, "drums"), sr=sr)
    M = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=1024)

    def band(lo, hi):
        e = np.log1p(100 * M[(f >= lo) & (f < hi)].sum(0) / M.sum(0).max())
        o = np.maximum(0, np.diff(e, prepend=e[0])); return o / (np.percentile(o, 99.5) + 1e-9)
    bands = dict(K=band(30, 120), S=band(1000, 4000), h=band(7000, 11000))
    grid = {}
    for n in B.numbers:
        rows = {}
        for k, o in bands.items():
            r = ""
            for s in range(B.L):
                t0, t1 = B.t(n, s - 0.4), B.t(n, s + 0.5)
                seg = o[max(0, int(t0 * sr / hop)):max(1, int(t1 * sr / hop))]
                v = seg.max() if seg.size else 0
                r += "X" if v > 0.6 else ("x" if v > 0.3 else ".")
            rows[k] = r
        grid[str(n)] = rows
    save_json(grid, f"{W}/drumgrid.json")

# ---------------------------------------------------------------- basic-pitch (optional)
if a.basic_pitch and need("bp", f"{W}/midi/other.csv"):
    step("bp (basic-pitch)")
    import warnings; warnings.filterwarnings("ignore")
    from basic_pitch.inference import predict, Model
    from basic_pitch import ICASSP_2022_MODEL_PATH
    model = Model(ICASSP_2022_MODEL_PATH); os.makedirs(f"{W}/midi", exist_ok=True)
    for s in ("lead", "backing", "other", "bass"):
        lo, hi = (30, 400) if s == "bass" else (80, 2000)
        _, midi, notes = predict(stem(W, s), model, onset_threshold=0.5, frame_threshold=0.3, minimum_note_length=80,
                                 minimum_frequency=lo, maximum_frequency=hi)
        with open(f"{W}/midi/{s}.csv", "w") as fo:
            for s_, e, p, amp, _ in sorted(notes, key=lambda n: n[0]): fo.write(f"{s_:.3f},{e:.3f},{p},{amp:.2f}\n")

# ---------------------------------------------------------------- report
if need("report", f"{W}/report.md") or FORCE & {"bars", "f0", "words", "drums", "tune"}:
    step("report")
    print(run([PY, f"{HERE}/report.py", W]).stdout[-1500:])
print("done:", W)
