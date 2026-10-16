#!/usr/bin/env bash
# Create the toolkit's Python environment and (optionally) pre-download the models.
#   bash setup.sh [VENV_DIR] [--cpu] [--prefetch]
# VENV_DIR defaults to $ACAP_VENV or ~/.cache/acappella/venv. System programs (ffmpeg, MuseScore 4, fluidsynth +
# a GM soundfont, poppler) are NOT installed here: see references/install.md for your OS.
set -euo pipefail
VENV="${ACAP_VENV:-$HOME/.cache/acappella/venv}"; CPU=0; PREFETCH=0
for a in "$@"; do
  case "$a" in --cpu) CPU=1 ;; --prefetch) PREFETCH=1 ;; *) VENV="$a" ;; esac
done
PYBIN="${PYTHON:-python3}"
"$PYBIN" -c 'import sys; assert sys.version_info >= (3, 10), "python >= 3.10 needed"'
[ -x "$VENV/bin/python" ] || "$PYBIN" -m venv "$VENV"
PY="$VENV/bin/python"; PIP="$VENV/bin/pip"
"$PIP" install -q --upgrade pip wheel
if [ "$CPU" = 1 ] || ! command -v nvidia-smi >/dev/null 2>&1; then
  "$PIP" install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu || "$PIP" install -q torch torchaudio
else
  "$PIP" install -q torch torchaudio --index-url https://download.pytorch.org/whl/cu126
fi
"$PIP" install -q numpy scipy librosa soundfile matplotlib pretty_midi pyphen demucs torchcrepe openai-whisper \
  "audio-separator[gpu]" audioread standard-aifc standard-sunau 2>/dev/null \
  || "$PIP" install -q numpy scipy librosa soundfile matplotlib pretty_midi pyphen demucs torchcrepe openai-whisper \
       audio-separator audioread standard-aifc standard-sunau
"$PIP" install -q "beat_this @ https://github.com/CPJKU/beat_this/archive/main.zip" || echo "beat_this failed: librosa beat tracking will be used"
"$PIP" install -q basic-pitch || echo "basic-pitch failed (optional)"
if [ "$PREFETCH" = 1 ]; then
  "$PY" - <<'EOF'
import os, subprocess, sys
from demucs.pretrained import get_model; get_model("htdemucs_ft")
import whisper; whisper.load_model("medium", device="cpu")
try:
    from beat_this.inference import File2Beats; File2Beats(checkpoint_path="final0", device="cpu")
except Exception as e: print("beat_this prefetch skipped:", e)
m = os.path.expanduser(os.environ.get("ACAP_MODELS", "~/.cache/acappella/models")); os.makedirs(m, exist_ok=True)
from audio_separator.separator import Separator
s = Separator(model_file_dir=m); s.load_model("mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt")
print("models cached")
EOF
fi
echo "venv ready: $PY"
echo "export ACAP_PY=$PY"
"$PY" "$(dirname "$0")/check_env.py" || true
