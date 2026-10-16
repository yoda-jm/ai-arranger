---
name: acappella-arranger
description: Turn a song recording (MP3/WAV, optional lyrics file) into a 4-8 part a cappella arrangement, from SATB up to Solo + SSATBarB + vocal percussion, delivered as a MuseScore score, PDF, MIDI and rehearsal audio aligned to the original. Bundled tools separate the stems, track bars, and draft the melody, bass, chords, drums, lyrics and repeats. An arranging engine writes pads, block harmony, instrument imitations (brass, flute, keys) and beatbox from the record's drums, then checks the result against the recording. It also writes in the style of known lineups (barbershop quartet, Pentatonix, VoicePlay) and has a method to research a new one. Use it when the user wants a vocal, a cappella or choir arrangement, a barbershop or Pentatonix-style version, a beatbox part, or a transcription of a song's vocal harmonies from an audio file.
argument-hint: "<song.mp3> [lyrics.txt] [voicing: SATB | Solo+SATB+VP | 8-part pop | barbershop | Pentatonix | VoicePlay]"
---

# A cappella arrangement from a recording

The scripts do the heavy lifting: separation, transcription drafts, voicing, engraving, renders and QA. Your job:
- check the drafts against the recording;
- make the musical decisions (form, textures, voicing);
- write two small Python files, `song.py` (the transcription) and `arrangement.py` (the arrangement);
- iterate on the QA numbers and the page images.

You can't listen, so verify with the tools: `look.py` piano rolls, `qa.py` against the recording, and PNG pages.

```bash
S=${CLAUDE_SKILL_DIR}/../arranger-core/scripts   # the shared toolkit (analysis, engine, build, render, qa)
PY=${ACAP_PY:-$HOME/.cache/acappella/venv/bin/python}
A=$PWD/arrangements/<song>             # per-song folder: the audio + lyrics, $A/work (analysis), $A/song.py, $A/arrangement.py, $A/out
```

## 0. Setup (once per machine, about 5 min plus 3.5 GB of models)
`$PY $S/check_env.py`. If anything is MISSING, run `bash $S/setup.sh` (the Python side), then install the system programs (ffmpeg, MuseScore 4, fluidsynth + a GM soundfont, poppler) as described in [install.md](../arranger-core/references/install.md) for the OS. If the user already has a venv with these packages, `export ACAP_PY=/path/to/python`.

## 1. Decide the brief (ask only what the request leaves open)
- **Voicing**:
  - SATB (4)
  - Solo + SATB + VP (6, the default for pop)
  - Solo + S1 S2 A T Bar B + VP (8, "full pop": hooks and pads at once)
  - SSAA / TTBB via voice keys `S1 S2 A1 A2` / `T1 T2 B1 B2`
  - **the style of a known group or lineup**: barbershop quartet (tenor, lead, baritone, bass; no VP), Pentatonix (three upper voices trading the lead, a very low bass, beatbox), VoicePlay (5 men with VP, theatrical, guest soloists). See the style cards in [references/styles.md](references/styles.md). For a style with no card, research it with [style-research.md](../arranger-core/references/style-research.md) and write the card first.
- **Soloist**: male (default, tenor clef) or female (`setup(solo="female")`); the key of the record unless asked otherwise.
- **Style and difficulty**: pop with VP (default); choral (no VP, more lyric writing); easy (pads, fewer 16ths).
- **Output**: always the score files plus aligned renders and a README. Keep earlier versions; write to a new out folder.

## 2. Analyse (one command, about 6-8 min on a GPU, about 30 min on CPU)
```bash
$PY $S/analyze.py song.mp3 $A/work --lyrics lyrics.txt [--anchor 4.52=1] [--meter 3/4] [--basic-pitch]
```
This writes stems, `bars.json`, f0, words, the drum grid, `report.md` and `draft.py` (all steps cached; `--force step` to redo). Run it in the background, since separation takes minutes.
- **Read `$A/work/report.md` fully**. It is the map of the song: tempo runs, irregular bars, key regions, per-bar stem levels, chord guesses, drums, `≈rep` repeats with transposition, instrument quotes of the tune, and backing-vocal pitches. How to read each column, and its accuracy: [analysis.md](../arranger-core/references/analysis.md).
- **Fix the bar map first**. Bar 1 should be the first downbeat of the first sung phrase: `--anchor TIME=1`. Check that bar lengths are steady inside sections, and look at irregular bars with `look.py ... roll audio N-M`. To pin rubato bars, run `$PY $S/barmap.py $A/work --anchor ... --fix 53=93.8,54=95.9`, then `analyze.py ... --force drums,report`.
- From levels + `≈rep` + words, **write down the form**: a section table with recording bar ranges, keys, and which sections repeat or transpose which.

## 3. Transcribe into `$A/song.py` (start from [song.py](../arranger-core/templates/song.py); details in [arranger-core](../arranger-core/SKILL.md))
- Copy `LEAD` (tokens + syllables), `CHORDS` and `KEYS` for **one instance of each distinct section**. Derive repeats with `tr_tokens` / `tr_chords` (the `≈rep` column gives the transposition).
- The drafts are about 65% exact for the melody, 80% for chords and 82% for the bass. Check every phrase you use:
  - melody: `look.py $A/work f0 N-M` and `look.py $A/work roll lead N-M --f0 --lo 43 --hi 76` (open the PNG with Read);
  - bass: `look.py ... nnls bass N-M --lo 28 --hi 60`;
  - chords: `look.py ... chords N-M` (root from the bass, quality from the chroma, push long notes an 8th early);
  - riffs: `look.py ... roll other N-M --lo 55 --hi 96`.
- Notate the intended music: notes on the 8th/16th grid, the chord-tone pitch rather than the scoop, words from the lyrics file. Verify the transcription early. One build containing just the solo (and bass) is enough for `qa.py` to report the solo vs the recorded lead per bar. A hand-checked melody reached 72% exact per 16th on the example; investigate bars below about 50%.

## 4. Plan, then write `$A/arrangement.py` (start from [templates/arrangement.py](templates/arrangement.py))
Fill the plan table in the template's docstring before writing notes. Craft rules, the texture palette, syllables, VP notation and the energy arc are in [references/arranging.md](references/arranging.md); the engine API is in [engine.md](../arranger-core/references/engine.md). The typical recipes in engine.md come from an 81-bar, 8-voice pop arrangement; the published worked example will be `examples/code-monkey/` at the repository root. Core rules:
- **Copy the record first**:
  - the bass sings the recorded bass line;
  - the VP copies the recorded kick/snare and fills (`vp()`);
  - the record's backing-vocal lines stay;
  - instrument hooks and instrumentals are sung with imitation syllables (brass "Bah-dah", flute "doo-dl", keys "jen", bells "din", strings "Oo").
- **Never compete with the solo.** Under lyric lines use pads or short comping. Use lyric blocks only on hook words, or in the climactic chorus. Answers go in the gaps.
- **Every repeat gets a new texture**, and the energy builds to the last chorus (add a descant there). Use a breakdown (drop the VP) before the final build if the song allows, then a tag, then a wide final chord with a fermata and "Ksh".
- **Singability**: tessitura below about 15% in the top 3 semitones, leaps of a 6th or less in backgrounds, breaths every 2-4 bars, entrances on sounding chord tones. Narrow `R(...)` ranges to place pads.

## 5. Build → check → iterate (usually 2-4 rounds)
```bash
$PY $S/build.py $A/arrangement.py $A/out --work $A/work --png && $PY $S/qa.py $A/out && $PY $S/render.py $A/out
```
- `build.py` writes musicxml, mscz (voices on piano, VP on drums, chord symbols muted), pdf, mid, `events.json` and `png/page-NN.png`. Python errors point at the bar: a token bar that doesn't sum to 16, or a syllable count that doesn't match the onsets.
- **QA targets**:
  - every part within range;
  - solo vs recorded lead ≥ about 70% pitch class (lower bars = transcription errors);
  - sung bass = recorded bass ≥ about 75%;
  - chroma similarity median ≥ 0.8, with no bar below 0.6 (a wrong chord or key);
  - semitone rubs only on passing tones.

  Fix the worst bars listed, rebuild, and re-run QA.
- **Look at 2-3 PNG pages** (Read) for collisions, lyrics, dynamics and system breaks. To see an arranged part over the recording: `look.py $A/work roll other 37-40 --part $A/out:S1`.
- If you need different ranges, voices or meter, change `setup(...)`. Don't patch the engine for one song.

## 6. Deliver
- Write `$A/out/README.md` from [templates/README.md](templates/README.md): files, section plan, syllable guide, VP key, QA numbers, things to check by ear, regenerate commands.
- In the reply, point the user to `audio/mix_with_original.wav` and `audio/real_lead_over_backgrounds.wav` first. Say plainly what is transcription and what is arrangement, and list the bars that are uncertain.
- Never claim it "sounds good": you haven't heard it. Report the measured checks.

## Hard-won pitfalls
- Don't prompt Whisper with the lyrics: it skips verses. (`analyze.py` handles this.)
- Constant-tempo beat trackers drift through tempo changes. Check the tempo runs; a slow section may be a real tempo change, not fermatas.
- basic-pitch invents overtone notes. Use NNLS (`look.py nnls`) and the bass stem for harmony.
- Instrumentals often replay the tune transposed (in one cartoon theme: flute = verse +17, horns = chorus −1). Check `≈rep` and the quote list before inventing material.
- MuseScore needs absolute paths and `QT_QPA_PLATFORM=offscreen` (build.py does both). Re-importing the MusicXML by hand re-enables chord playback.
- Event bars must sum to `BAR` (16 in 4/4). Use `rest_bar()` / `"r:16"` for silent bars; `finish()` fills the gaps.

## Files
- Scripts, install, analysis, engine and notation references live in the shared [arranger-core](../arranger-core/SKILL.md) skill (`../arranger-core/scripts/`: `analyze.py` · `barmap.py` · `report.py` · `look.py` · `engine.py` · `build.py` · `render.py` · `qa.py` · `acap.py` · `setup.sh` / `check_env.py`).
- `references/arranging.md`: the a cappella craft (roles, voicing, textures, syllables, VP, energy arc).
- `references/styles.md`: style cards for known lineups (barbershop, Pentatonix, VoicePlay): lineup → voice keys, core features with sources, engine recipe, gaps.
- `templates/`: arrangement.py · README.md (song.py is in arranger-core/templates)
- worked example: `examples/code-monkey/` at the repository root, a Creative Commons song (arrangements planned)
