# Generated files that are not in git

Building this example produced 115 more files (658 MB). They are AI-made byproducts of the production:
- the stems and analysis of the recording;
- the written-out builds the short sheets are made from;
- the MIDI and the audio renders of each part;
- the MuseScore masters and page previews.

Git keeps only what a musician uses, plus what is needed to check it:
- `sheets/`: the five short sheets as PDF and MusicXML, the full score rendered as `.m4a`, and the complete written-out score as `code_monkey_written_out.pdf`;
- the sources: `song.py`, `score.py`, the roadmaps and `lyrics.txt`;
- `evaluation/`.

`regenerate.sh` makes them all again from `code-monkey.mp3` (about 15 minutes with a GPU). The analysis runs on neural
models (Demucs, Mel-RoFormer, Whisper), so stems made again are close to these but not the same bytes. The checksums
identify the files the committed sheets and evaluation were made from.

| File | Size | SHA-256 (first 16) | Made by |
|---|---|---|---|
| `out-sheets/bass/code_monkey_bass.mid` | 3 KB | `cebe5b8985444140` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/code_monkey_bass.mscz` | 0.1 MB | `a91ee972eb958be4` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/code_monkey_bass.musicxml` | 0.2 MB | `3bdb14e507536a8f` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/code_monkey_bass.pdf` | 0.1 MB | `3b061db31eb753b6` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/events.json` | 20 KB | `ba0f9094c47fe8ea` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/png/page-1.png` | 26 KB | `3b7bce9e8ee3a34a` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/png/page-2.png` | 29 KB | `57107d6b4ad857e8` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/png/page-3.png` | 26 KB | `2d63b6c6e7450ee1` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/bass/png/page-4.png` | 26 KB | `a4f874248a2b0ac2` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/code_monkey_drums.mid` | 23 KB | `09caf67cc7fb1c2b` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/code_monkey_drums.mscz` | 0.1 MB | `c3101a3bb248a819` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/code_monkey_drums.musicxml` | 0.3 MB | `f8e87880da0b1115` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/code_monkey_drums.pdf` | 81 KB | `3cc0da403e8aab6c` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/events.json` | 43 KB | `08dafe17e8739202` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/png/page-1.png` | 26 KB | `cc63c6c16fa547be` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/png/page-2.png` | 24 KB | `7c572697dec3dfee` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/drums/png/page-3.png` | 8 KB | `37b52f5903e13bde` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/code_monkey_guitar.mid` | 7 KB | `4b67ce889b128194` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/code_monkey_guitar.mscz` | 0.3 MB | `0c2eb3f699ea44fd` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/code_monkey_guitar.musicxml` | 1.5 MB | `d32fec7fda234864` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/code_monkey_guitar.pdf` | 0.3 MB | `29a9e4a01e4a6e47` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/events.json` | 0.1 MB | `a46553bad42fb78f` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-01.png` | 28 KB | `2b4f094ef0288c4e` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-02.png` | 26 KB | `4723ba0117767537` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-03.png` | 28 KB | `a23b0fce935e4a30` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-04.png` | 23 KB | `fe72dd68ba509536` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-05.png` | 26 KB | `1118f0eb72f16d04` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-06.png` | 23 KB | `2953358ceaa55831` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-07.png` | 23 KB | `ed3ac1e08ddb1824` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-08.png` | 21 KB | `1c6a748e6fbf82eb` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-09.png` | 27 KB | `6b20400d72541f0c` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/guitar/png/page-10.png` | 22 KB | `07c53f3d70ea88f5` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/code_monkey_lead_sheet.mid` | 7 KB | `c87cee3e105dba4f` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/code_monkey_lead_sheet.mscz` | 0.1 MB | `d959f98d9e72e423` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/code_monkey_lead_sheet.musicxml` | 0.1 MB | `eae6476ae5677abf` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/code_monkey_lead_sheet.pdf` | 97 KB | `ba6d2fd9400eb91f` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/events.json` | 24 KB | `5e2ebac1ff665502` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/png/page-1.png` | 47 KB | `7b0fdfc5f291c12a` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/png/page-2.png` | 47 KB | `7a99e65412788dc5` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out-sheets/lead/png/page-3.png` | 28 KB | `fd3810a0073fc865` | build.py score.py with CM_SHEET = lead, drums, guitar or bass (written out) |
| `out/audio/aligned_full.mid` | 45 KB | `b43f811e25e1d98f` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/aligned_full.wav` | 33.5 MB | `1e618ea37b81a138` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/backgrounds_only.mid` | 42 KB | `2480e84938126bb7` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/backgrounds_only.wav` | 33.5 MB | `dbc5eedbe6812e00` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/mix_with_original.wav` | 33.5 MB | `3d2fdd4bf48e6a01` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/real_lead_over_backgrounds.wav` | 33.5 MB | `70282c888e52ec98` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_full.mid` | 45 KB | `927c2f6217e0d32e` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_full.wav` | 33.4 MB | `4c000b99adcd18ce` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_no_vocals.mid` | 41 KB | `a5441b43330686b5` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_no_vocals.wav` | 33.4 MB | `cfabc48fbbf11f3b` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_acousticguitar.mid` | 26 KB | `a811c1d475aae77f` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_acousticguitar.wav` | 33.4 MB | `ad2b87bfca3a036b` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_backingvocals.mid` | 1 KB | `8be92637ec393358` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_backingvocals.wav` | 31.8 MB | `66ccc86273556bc6` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_drums.mid` | 7 KB | `232af5aa7e3fe1ba` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_drums.wav` | 32.1 MB | `0d431ff368f3026c` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_electricbass.mid` | 3 KB | `f55f209d730c62c6` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_electricbass.wav` | 31.7 MB | `4a9a3c461d8262d1` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_electricguitar.mid` | 6 KB | `4403403a0f233bea` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_electricguitar.wav` | 30.8 MB | `44be6663c9881cda` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_leadvocal.mid` | 3 KB | `7767dd54ce14ae3b` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_part_leadvocal.wav` | 32.1 MB | `9f298d20ca6959a7` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_vocals.mid` | 4 KB | `48926135d2e982c1` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/audio/score_vocals.wav` | 32.1 MB | `b91b4860b0dcb337` | render.py: fluidsynth + FluidR3 GM, seed 1 |
| `out/code_monkey.mid` | 42 KB | `2665c35161888b4b` | build.py score.py (the written-out full score) |
| `out/code_monkey.mscz` | 0.4 MB | `89aa7bfb5b7dd039` | build.py score.py (the written-out full score) |
| `out/code_monkey.musicxml` | 2.0 MB | `4eff4e04e49e6525` | build.py score.py (the written-out full score) |
| `out/code_monkey.pdf` | 0.4 MB | `ac315b5c526790f2` | build.py score.py (the written-out full score) |
| `out/events.json` | 0.2 MB | `082585c08d647e63` | build.py score.py (the written-out full score) |
| `out/grooves.md` | 13 KB | `f37df7b3c2fe7dc2` | south-american-arranger sheets.py |
| `out/lead_sheet.md` | 4 KB | `67e411e1fceab66f` | south-american-arranger sheets.py |
| `out/png/page-01.png` | 29 KB | `a56c578d850dbb55` | build.py --png |
| `out/png/page-02.png` | 24 KB | `d38aba926265db36` | build.py --png |
| `out/png/page-03.png` | 28 KB | `4ae97f257a5501d4` | build.py --png |
| `out/png/page-04.png` | 25 KB | `4f9fae298a9eeb06` | build.py --png |
| `out/png/page-05.png` | 23 KB | `fd9f7d6672d5d099` | build.py --png |
| `out/png/page-06.png` | 26 KB | `8c2435028e23cd13` | build.py --png |
| `out/png/page-07.png` | 26 KB | `864e15fcc604ce8e` | build.py --png |
| `out/png/page-08.png` | 28 KB | `a06384d11451d0c9` | build.py --png |
| `out/png/page-09.png` | 25 KB | `246567be94e2da1c` | build.py --png |
| `out/png/page-10.png` | 24 KB | `7428b6045a357d6a` | build.py --png |
| `out/png/page-11.png` | 23 KB | `b41117638036efab` | build.py --png |
| `out/png/page-12.png` | 25 KB | `b60d0961b9a73314` | build.py --png |
| `out/png/page-13.png` | 28 KB | `85a815ebff726b9f` | build.py --png |
| `out/png/page-14.png` | 27 KB | `56eaa0fdfd52c72f` | build.py --png |
| `out/png/page-15.png` | 25 KB | `7185d62830359fba` | build.py --png |
| `out/png/page-16.png` | 15 KB | `884f67efffeb8e26` | build.py --png |
| `out/qa.txt` | 3 KB | `3c60622799a21879` | qa.py |
| `sheets/code_monkey_bass.mid` | 3 KB | `8d0805535325b19a` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_bass.mscz` | 86 KB | `6590ec3db3a21bd1` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_drums.mid` | 23 KB | `8589dd2fac2ad91b` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_drums.mscz` | 66 KB | `c1f12573ae8f598d` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_full_score.mid` | 42 KB | `2665c35161888b4b` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_full_score.mscz` | 0.3 MB | `2187d693914f5660` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_guitar.mid` | 7 KB | `42112a24a1ae4677` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_guitar.mscz` | 0.2 MB | `87ed1913a963a2dd` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_lead_sheet.mid` | 7 KB | `c87cee3e105dba4f` | compact.py (MuseScore master / playback check of the short sheet) |
| `sheets/code_monkey_lead_sheet.mscz` | 0.1 MB | `d1d55a21bd01511a` | compact.py (MuseScore master / playback check of the short sheet) |
| `work-analyze.log` | 4 KB | `0ed8bb1d23316f1d` | analyze.py log |
| `work/audio.wav` | 32.1 MB | `7fab166e5afd2c3b` | analyze.py: ffmpeg decode of code-monkey.mp3 (44.1 kHz stereo) |
| `work/bars.json` | 11 KB | `1cc756944243477f` | barmap.py --grid --anchor 1.07=1: the fitted click grid (160.01 bpm) |
| `work/bars.tracker.json` | 9 KB | `6ec5cb5e35333215` | analyze.py: the beat tracker's bars, before the fix |
| `work/beats.json` | 6 KB | `e1fb2873ed6e59bd` | analyze.py: beat_this |
| `work/draft.py` | 23 KB | `40fecc9287c62c8b` | analyze.py (report.py) |
| `work/drumgrid.json` | 11 KB | `7837ed793975aa27` | analyze.py: drum onsets |
| `work/lead_f0.npy` | 0.1 MB | `d17d477c4bcdb426` | analyze.py: torchcrepe on the lead stem |
| `work/meta.json` | 1 KB | `780f0adc7d6b05dd` | analyze.py |
| `work/report.md` | 22 KB | `58a67ea04ad0d091` | analyze.py (report.py) |
| `work/stems/backing.wav` | 32.1 MB | `d6095544523969de` | analyze.py: Mel-RoFormer karaoke split of the vocal stem |
| `work/stems/bass.wav` | 32.1 MB | `d41fdf2fad91df4a` | analyze.py: Demucs htdemucs_ft |
| `work/stems/drums.wav` | 32.1 MB | `0b4536df56b40c9d` | analyze.py: Demucs htdemucs_ft |
| `work/stems/lead.wav` | 32.1 MB | `144b21c67a6cdf54` | analyze.py: Mel-RoFormer karaoke split of the vocal stem |
| `work/stems/other.wav` | 32.1 MB | `f9ea4107e06c6268` | analyze.py: Demucs htdemucs_ft |
| `work/stems/vocals.wav` | 32.1 MB | `29b3c29ddeaec7b9` | analyze.py: Demucs htdemucs_ft |
| `work/words.json` | 10 KB | `2f28a1f1dd2c6932` | analyze.py: Whisper, respelled from lyrics.txt |
