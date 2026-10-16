# Installation and where to look

## What is needed
| component | why | size / notes |
|---|---|---|
| Python 3.10–3.13 + venv | all scripts | 3.13 needs `standard-aifc standard-sunau` (setup.sh installs them) |
| PyTorch (CUDA if possible) | demucs, karaoke model, crepe, whisper, beat_this | CPU works, about 5–10× slower |
| demucs 4 | 4-stem separation (`htdemucs_ft`) | model ~320 MB, downloaded on first run to `~/.cache/torch/hub/checkpoints` |
| audio-separator | karaoke lead/backing split (Mel-RoFormer) | model ~870 MB, downloaded to `$ACAP_MODELS` (default `~/.cache/acappella/models`) |
| beat_this | beats + downbeats with tempo changes | 78 MB checkpoint; installed from GitHub (not on PyPI) |
| torchcrepe | lead pitch | model ships with the package |
| openai-whisper | word timestamps | `medium` 1.5 GB (`small` on CPU / small GPUs) in `~/.cache/whisper` |
| librosa, scipy, numpy, soundfile, matplotlib, pretty_midi, pyphen | analysis, images, MIDI, syllables | |
| basic-pitch (optional) | polyphonic note CSVs for `look.py bp` | needs onnxruntime or TF; warnings at import are harmless |
| **ffmpeg** | decoding, mixing | system package |
| **MuseScore 4** (`mscore`) | MusicXML → mscz / PDF / MIDI | system package, AppImage, Flatpak or macOS app. MuseScore 3 works too, but it has no chord playback, so there is nothing to mute |
| **fluidsynth** + a General MIDI soundfont | audio renders | FluidR3_GM, GeneralUser GS, or MuseScore's own `MS Basic.sf3` |
| poppler (`pdftoppm`) | PNG previews of the PDF pages | optional |

Disk: about 3.5 GB of models, plus about 150 MB per analysed song (stems). GPU memory: 4–6 GB is enough (demucs `--segment 7`; whisper medium uses ~5 GB, so use `--whisper small` on 4 GB cards).

## Python environment (any OS)
```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup.sh                 # venv in ~/.cache/acappella/venv (or $ACAP_VENV / first argument)
bash ${CLAUDE_SKILL_DIR}/scripts/setup.sh --cpu           # no NVIDIA GPU
bash ${CLAUDE_SKILL_DIR}/scripts/setup.sh --prefetch      # also download all models now
export ACAP_PY=~/.cache/acappella/venv/bin/python
$ACAP_PY ${CLAUDE_SKILL_DIR}/scripts/check_env.py         # prints ok / MISSING for every component
```
To install by hand: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu126` (use `cu121`/`cu118` for older drivers, or `/whl/cpu`), then `pip install demucs "audio-separator[gpu]" torchcrepe openai-whisper librosa soundfile matplotlib pretty_midi pyphen audioread standard-aifc standard-sunau "beat_this @ https://github.com/CPJKU/beat_this/archive/main.zip"`. Optionally add `basic-pitch`.

## System packages
| OS | command | soundfont path |
|---|---|---|
| Debian / Ubuntu | `sudo apt install ffmpeg fluidsynth fluid-soundfont-gm poppler-utils python3-venv` + MuseScore 4 AppImage or Flatpak (the apt `musescore3` is version 3) | `/usr/share/sounds/sf2/FluidR3_GM.sf2` |
| Fedora | `sudo dnf install ffmpeg fluidsynth fluid-soundfont-gm poppler-utils` (ffmpeg from RPM Fusion) + Flatpak MuseScore | `/usr/share/soundfonts/FluidR3_GM.sf2` |
| Arch | `sudo pacman -S ffmpeg fluidsynth soundfont-fluid poppler musescore` | `/usr/share/soundfonts/FluidR3_GM.sf2` |
| Gentoo | `emerge media-video/ffmpeg media-sound/fluidsynth media-sound/fluid-soundfont app-text/poppler media-sound/musescore` | `/usr/share/sounds/sf2/FluidR3_GM.sf2` |
| macOS | `brew install ffmpeg fluid-synth poppler python@3.12` and `brew install --cask musescore` | download FluidR3_GM or GeneralUser GS, or use `/Applications/MuseScore 4.app/Contents/Resources/sound/MS Basic.sf3` |
| Windows | use WSL2 (Ubuntu) and follow the Debian line. Native Windows works but paths and the MuseScore binary differ | |

**MuseScore binary.** The scripts look for `mscore`, `mscore4`, `musescore4`, `musescore`, `MuseScore4`, `~/Applications/MuseScore*.AppImage` and the macOS app. Otherwise set `ACAP_MSCORE`, for example:
- `export ACAP_MSCORE="/opt/MuseScore-Studio-4.5.2-x86_64.AppImage"` (add `--appimage-extract-and-run` if FUSE is missing)
- `export ACAP_MSCORE="flatpak run org.musescore.MuseScore"`. The sandbox must see your files: `flatpak override --user --filesystem=home org.musescore.MuseScore`.
- `export ACAP_MSCORE="/Applications/MuseScore 4.app/Contents/MacOS/mscore"`

It always runs headless with `QT_QPA_PLATFORM=offscreen` and **absolute paths** (relative paths fail silently).

**Soundfont.** Set `ACAP_SF2=/path/to/file.sf2` when it's not in a standard place.

## Environment variables
| var | default | meaning |
|---|---|---|
| `ACAP_PY` | `~/.cache/acappella/venv/bin/python` | the Python that runs every script |
| `ACAP_VENV` | `~/.cache/acappella/venv` | where setup.sh creates the venv |
| `ACAP_MODELS` | `~/.cache/acappella/models` | audio-separator model folder |
| `ACAP_KARAOKE` | `mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt` | karaoke model name (`audio-separator -l` lists the others) |
| `ACAP_MSCORE` | auto | MuseScore command (may contain spaces / arguments) |
| `ACAP_SF2` | auto | General MIDI soundfont |
| `TORCH_HOME` | `~/.cache/torch` | demucs / beat_this checkpoint cache |

## Troubleshooting
| symptom | fix |
|---|---|
| `audio-separator`: `No module named 'aifc'` / `'sunau'` | `pip install audioread standard-aifc standard-sunau` (Python 3.13) |
| demucs CUDA out of memory | `--device cpu`, or keep `--segment 7` and close other GPU jobs |
| Whisper OOM / slow | `--whisper small` |
| `beat_this` import fails | the librosa fallback is used automatically: check the bar map carefully (no tempo-change tracking) |
| MuseScore writes nothing | use absolute paths and `QT_QPA_PLATFORM=offscreen`; run `mscore -o out.pdf in.musicxml` by hand to see the error |
| MuseScore plays the chord symbols | the `.mscz` must come from `build.py` (it adds `<play>0</play>` to every `<Harmony>`); re-export after editing in the GUI if you re-imported the MusicXML |
| renders are silent | no soundfont found (set `ACAP_SF2`), or `fluidsynth` is missing |
| NNPACK / basic-pitch "Coremltools/TF not installed" warnings | harmless |

## Where to look (documentation and models)
- **Demucs** (stems): https://github.com/adefossez/demucs (models: `htdemucs`, `htdemucs_ft` = best 4-stem, `htdemucs_6s` adds guitar and piano stems)
- **audio-separator** (UVR models from the CLI): https://github.com/nomadkaraoke/python-audio-separator. List the models with `audio-separator -l`. Karaoke models: `mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt` (used here), the `UVR_MDXNET_KARA_2` family, `5_HP-Karaoke-UVR.pth`.
- **beat_this** (beats/downbeats): https://github.com/CPJKU/beat_this (paper: Foscarin et al., ISMIR 2024)
- **torchcrepe**: https://github.com/maxrjones/torchcrepe. **Whisper**: https://github.com/openai/whisper
- **librosa** (CQT, chroma, onsets, tuning): https://librosa.org/doc/latest/
- **basic-pitch**: https://github.com/spotify/basic-pitch
- **MusicXML 4.0** reference: https://www.w3.org/2021/06/musicxml40/ (percussion: https://www.w3.org/2021/06/musicxml40/tutorial/percussion)
- **MuseScore command line**: https://handbook.musescore.org/appendix/command-line-usage
- **Arranging**:
  - Deke Sharon & Dylan Bell, *A Cappella Arranging* (Hal Leonard, 2012)
  - Deke Sharon, *The Heart of Vocal Harmony* (2016)
  - the interview at https://blog.arrangeme.com/blog/interview-with-deke-sharon
  - https://www.finalemusic.com/?p=12969
  - CASA (Contemporary A Cappella Society) resources: https://casa.org
- **Beatbox notation** (Standard Beatbox Notation): https://wiki.ubc.ca/Course:PHYS341/2022/Project18, https://bouncemetronome.com/features/sounds/beatboxing-syllables
