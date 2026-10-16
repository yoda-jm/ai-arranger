"""Check that everything the toolkit needs is installed. Run with the toolkit's Python:
    $ACAP_PY scripts/check_env.py          (exit code 1 if something required is missing)
"""
import importlib, shutil, os, sys, glob, subprocess, logging, warnings
logging.disable(logging.WARNING); warnings.filterwarnings("ignore")

ok = True


def row(name, good, info="", required=True):
    global ok
    if required and not good: ok = False
    print(f"  [{'ok' if good else ('MISSING' if required else 'optional')}] {name:22s} {info}")


print(f"python {sys.version.split()[0]} at {sys.executable}")
if sys.version_info < (3, 10): row("python >= 3.10", False)
print("python packages:")
for mod, req, why in [("numpy", 1, ""), ("scipy", 1, ""), ("librosa", 1, "analysis"), ("soundfile", 1, ""),
                      ("torch", 1, "models"), ("torchaudio", 1, "demucs"), ("demucs", 1, "stem separation"),
                      ("audio_separator", 1, "karaoke lead/backing split"), ("beat_this", 0, "beat + downbeat tracking (else librosa)"),
                      ("torchcrepe", 1, "lead pitch"), ("whisper", 1, "lyrics timing (openai-whisper)"),
                      ("pyphen", 0, "syllables in drafts"), ("matplotlib", 1, "piano-roll images"),
                      ("pretty_midi", 1, "renders"), ("basic_pitch", 0, "optional note transcription")]:
    try:
        m = importlib.import_module(mod); row(mod, True, getattr(m, "__version__", "") + ("  " + why if why else ""), req)
    except Exception as e:
        row(mod, False, f"{why}  ({type(e).__name__}: {str(e)[:60]})", bool(req))
try:
    import torch
    cuda = torch.cuda.is_available()
    row("GPU (CUDA)", cuda, torch.cuda.get_device_name(0) if cuda else "CPU only: analysis ~5-10x slower (still works)",
        required=False)
    if not cuda and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        print("        Apple MPS available: demucs/whisper may use --device mps; crepe runs on CPU")
except Exception:
    pass
print("programs:")
row("ffmpeg", bool(shutil.which("ffmpeg")), shutil.which("ffmpeg") or "")
ms = os.environ.get("ACAP_MSCORE") or next((shutil.which(c) for c in ("mscore", "mscore4", "musescore4", "musescore",
                                                                      "MuseScore4") if shutil.which(c)), None)
info = ms or "set ACAP_MSCORE to the MuseScore 4 executable / AppImage"
if ms:
    try:
        r = subprocess.run(ms.split() + ["--version"], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
        info = f"{ms}  {(r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else ''}"
    except Exception as e:
        info = f"{ms} (version check failed: {e})"
row("MuseScore 4", bool(ms), info)
row("fluidsynth", bool(shutil.which("fluidsynth")), shutil.which("fluidsynth") or "audio renders")
row("pdftoppm", bool(shutil.which("pdftoppm")), "page previews (poppler)", required=False)
sf = [p for p in [os.environ.get("ACAP_SF2"), "/usr/share/sounds/sf2/FluidR3_GM.sf2", "/usr/share/soundfonts/FluidR3_GM.sf2"]
      + glob.glob("/usr/share/sounds/sf2/*.sf2") + glob.glob("/usr/share/mscore*/sound/*.sf3") + glob.glob("/usr/share/soundfonts/*.sf2")
      + glob.glob(os.path.expanduser("~/.cache/acappella/*.sf2")) + glob.glob("/opt/homebrew/share/soundfonts/*.sf2") if p and os.path.exists(p)]
row("GM soundfont", bool(sf), sf[0] if sf else "e.g. FluidR3_GM.sf2 (set ACAP_SF2)")
print("model caches (downloaded on first use):")
hub = os.path.expanduser("~/.cache/torch/hub/checkpoints")
models = os.path.expanduser(os.environ.get("ACAP_MODELS", "~/.cache/acappella/models"))
row("demucs htdemucs_ft", bool(glob.glob(f"{hub}/*.th")), hub + " (or $TORCH_HOME)", False)
row("karaoke roformer", bool(glob.glob(f"{models}/mel_band_roformer_karaoke*.ckpt")), models, False)
row("beat_this final0", os.path.exists(f"{hub}/beat_this-final0.ckpt"), "", False)
row("whisper medium", os.path.exists(os.path.expanduser("~/.cache/whisper/medium.pt")), "~/.cache/whisper", False)
print("ALL REQUIRED OK" if ok else "SOMETHING REQUIRED IS MISSING: see references/install.md")
sys.exit(0 if ok else 1)
