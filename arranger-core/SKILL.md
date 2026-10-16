---
name: arranger-core
description: Base toolkit for transcribing ("repiquer") and re-arranging songs from recordings and videos. It analyses a recording or a live-concert/phone video (MP3/WAV/MP4/MTS) into stems, a bar map, tempo, key, form, melody, bass, chords, drum grid and word timings, and transcribes a song into a song.py file, or ONE PART note by note (a bass line, the low notes a guitarist plays, a riff filmed on a phone) into a tab or text chart with patterns and the song structure. It also builds, renders and checks any arrangement written with its engine (MuseScore score, PDF, MIDI, audio, QA against the recording). Use it directly when the user wants a song analysed, a part transcribed or checked against a recording, a tab or bass chart written, or the form/grid/lyrics extracted. Style skills such as acappella-arranger and south-american-arranger run on top of it.
argument-hint: "<song.mp3|wav> [lyrics.txt]"
---

# Arranger core: analysis, transcription, build, render, QA

Style skills (`acappella-arranger`, `south-american-arranger`) decide *what* to write. This toolkit does everything around that:
- **analysis** of the recording;
- **transcription** of the record into `song.py`;
- the **engine** that arrangement files are written with;
- **build** (MusicXML → MuseScore → PDF/MIDI/PNG), **render** (fluidsynth audio) and **QA** (checks, including against the recording).

You can't listen, so verify with the tools: `look.py` piano rolls and text views, `partscope.py` note-level tests, and `qa.py` numbers. The rule: **the recording is the truth**. The user's draft, the original record and your own earlier answer are all hypotheses to test against it.

**What to use for what:**

| The user wants... | Path |
|---|---|
| a part written down: a bass line from a live video, a guitarist's low notes, a riff from a phone video, a tab or chart checked/continued | §1, then §2b + [references/transcription.md](references/transcription.md) |
| a song's grid, lyrics, form, melody (as a lead sheet or a base to re-arrange) | §1-§2 (`song.py`) |
| an a cappella cover (SATB to 8 voices, a Pentatonix-style lineup with beatbox) | `acappella-arranger` |
| a re-genred band cover (bossa, samba, son, tango...) | `south-american-arranger` |
| a style, group or lineup the skills have no card for ("like Pentatonix", "a chacarera") | [references/style-research.md](references/style-research.md): research it, then write the card in the style skill |

```bash
C=${CLAUDE_SKILL_DIR}/scripts                 # (from a style skill: ${CLAUDE_SKILL_DIR}/../arranger-core/scripts)
PY=${ACAP_PY:-$HOME/.cache/acappella/venv/bin/python}
A=$PWD/arrangements/<song>                    # per-song folder: audio + lyrics, $A/work, $A/song.py, $A/arrangement.py, $A/out*
```

## 0. Setup (once per machine, about 5 min plus 3.5 GB of models)
`$PY $C/check_env.py`. If anything is MISSING, run `bash $C/setup.sh` (Python side), then install ffmpeg, MuseScore 4, fluidsynth + a GM soundfont and poppler as in [references/install.md](references/install.md). Existing venv: `export ACAP_PY=/path/to/python`.

## 1. Analyse (about 6-8 min on a GPU, 30 on CPU; run it in the background)
```bash
$PY $C/analyze.py song.mp3 $A/work --lyrics lyrics.txt [--anchor 4.52=1] [--meter 3/4] [--basic-pitch]
```
- Writes stems (Demucs + karaoke lead/backing split), `bars.json`, f0, words, the drum grid, `report.md` and `draft.py`. Every step is cached; `--force step` redoes one.
- **Read `$A/work/report.md` fully.** It is the map of the song:
  - tempo runs and irregular bars;
  - key regions and per-bar stem levels (`LKdbo`);
  - chords per half bar, and `≈rep` (repeats with transposition);
  - the drum grid, instrument quotes of the tune, and backing-vocal pitches.

  How to read each column, and how accurate it is: [references/analysis.md](references/analysis.md).
- **Fix the bar map first.** Bar 1 = the first downbeat of the first sung phrase (`--anchor TIME=1`). Pin rubato bars with `barmap.py $A/work --fix 53=93.8,...`, then `analyze.py ... --force drums,report`.
- **Write down the form**: a section table with recording bars, keys and which sections repeat (from levels + `≈rep` + words). Songs often run on one loop; say so, it makes reharmonising easy.
- No lyrics file? Whisper's words are used.
  - Get a second opinion section by section: `$PY $C/words.py $A/work 12-19 35-43 [--stem vocals] [--language en]`. Short clips on the lead stem fix most mishearings.
  - Keep the reading most passes agree on, mark the rest in `song.py`, and ask the user for the lyrics.

## 2. Transcribe into `$A/song.py` (start from [templates/song.py](templates/song.py))
- One instance of each distinct section: `LEAD` tokens + syllables, chords, keys. Repeats come from `tr_tokens` / `tr_chords`.
- The drafts are about 65% exact for the melody, 80% for chords and 82% for the bass. Check every phrase:
  - melody: `look.py $A/work f0 N-M` (pitch per 16th, onsets `*`, words) and `look.py $A/work roll lead N-M --f0 --lo 43 --hi 76` (open the PNG);
  - bass: `look.py ... nnls bass N-M --lo 28 --hi 60`;
  - chords: `look.py ... chords N-M --div 4` (root from the bass, quality from the chroma, push long notes an 8th early).
- Notate the intended music: the 8th/16th grid, chord-tone pitches rather than scoops, one note per syllable.
- You may write `song.py` in the arrangement's key. Then set `rec_shift` (semitones from the record's key) in the arrangement, so renders and QA compare in the record's key.
- **Verify early.** A lead-only build is enough for `qa.py` to score the melody against the recorded singer. Aim for 70% or more same-pitch-class 16ths; investigate bars below about 50%.

## 2b. Transcribe one part for a musician (repiquage)
Full method, chart conventions and the mistakes already made: [references/transcription.md](references/transcription.md).
- **Material**: cut the song from a long concert file at the user's timestamp, with margins (`ffmpeg -ss ... -t ... -vn`), and note the offset so you can quote video times. Grab frames (`-vf yadif`) to see who plays what. No bassist means the bass role is in a guitar's low strings (the `other` stem; `bass` stays near −70 dB).
- **Analyse**: run `analyze.py` on the extract. On a slow live song the tracker often counts 8ths, so 1 real bar = 2 tracker bars (`partscope --tb 2`, the default).
- **Settle the notes with `partscope.py W ...`**:
  - `lowest`: the line per 8th;
  - `stack`: the same bar from every pass. The figure all passes share is the pattern; a pass that differs is a slip, and a figure heard in at least one pass belongs in the chart;
  - `onsets`: strum or bass note (plain bins);
  - `repluck`: a doubled note, using a 2048-point FFT; a held note is the flat-line control;
  - `glide`: slide or pluck, E or F;
  - `profile`: chord quality, e.g. a live Dm where the record has E7.
- **Octave**: a guitarist's bass role goes exactly one octave down, every note the same way. On phone audio the 2nd harmonic is the loudest partial.
- **Write** the tab in the house style:
  - one chord per bar, 2 characters per 16th, `¦` at the half bar;
  - patterns A/B/C, with variant endings as small extra staves;
  - page 2 = the structure, one section per heading with its first lyric line;
  - remarks in footnotes.
- **Send it** to the band's [TroubaStack](https://github.com/yoda-jm/troubastack) server if they use one: the tab becomes a chart in its dialect, saved through its API with a preview first. See [references/troubastack.md](references/troubastack.md).
- **Report**: per-beat tables with video timestamps and a counting ruler over the tab. Confirm how the user counts bars (at double tempo their "bar 7" is a half bar).

## 3. Arrange (the style skill's job), then build → check → listen
```bash
$PY $C/build.py $A/arrangement.py $A/out --work $A/work --png [--lib <style skill>/scripts]
$PY $C/qa.py $A/out && $PY $C/render.py $A/out
```
- `build.py` writes musicxml, mscz (chord symbols muted, rhythm slashes silent), pdf, mid, `events.json` and `png/page-NN.png`. Python errors point at the bar. Tall scores: `--scaling 4.2 --staff-distance 40`.
- **Tablature**: a part listed in `engine.TAB` (open strings, max fret) gets a TAB staff under its notation staff. `fretboard.py` picks the string and fret of every note along the shortest path for the hand, and shows strums as full chord shapes (the top four strings on an up-stroke). The TAB staff is silent in MuseScore so the part does not play twice. Its notation staff uses an octave clef (treble 8vb, bass 8vb) instead of a transposition, because MuseScore recomputes frets from the written pitch of a transposed part.
- **Part names choose the MuseScore instrument** on import, before the instrument sound: a part called "Bass" becomes a bass *singer*. Name a bass guitar "Electric Bass".
- `qa.py` checks:
  - ranges, tessitura, leaps and rubs;
  - lead vs the recorded singer, bass vs the recorded bass, and chroma vs the recording;
  - lead vs the chord symbols (long notes a semitone above a chord tone);
  - fixed-pitch and chord-bar constraints, one player on two instruments, and instrument switches without time;
  - the energy arc per section.
- `render.py` writes the files listed in [references/engine.md](references/engine.md#build--render--qa):
  - renders aligned to the recording;
  - with `META["score_render"]`, a set at the arrangement's own tempos (full, no vocals, vocals, per part).
- Engine API, registries for instrument parts, meter warps: [references/engine.md](references/engine.md). Score-format details: [references/notation.md](references/notation.md).

## Hard-won pitfalls
- Don't prompt Whisper with the lyrics: it skips verses. (`analyze.py` handles this.) Whisper still mishears names and English words in a Spanish song ("West Hollywood" came out as "black honey pot"): check them against the meaning.
- Constant-tempo beat trackers drift; check the tempo runs. A rubato intro (tempo jumping 54 → 87 → 124) is not a bar map to trust: start the transcription at the first steady bar.
- basic-pitch invents overtones. Use NNLS and the bass stem for harmony.
- Instrumentals often replay the tune transposed: check `≈rep` and the quote list.
- MuseScore needs absolute paths and `QT_QPA_PLATFORM=offscreen` (build.py does both).
- Bars must sum to `BAR` (16 in 4/4, 24 in 12/8). In an arrangement file, read `E.BAR` (`import engine as E`): `from engine import *` copies `BAR` before `setup()` changes it.
- **Window length decides what you can hear.** A 16th at 65 bpm lasts 0.23 s. A CQT at 36 bins/octave uses about 0.5 s windows at A2, and a 4096-point FFT about 0.19 s; both merge two plucks into one. Use `partscope repluck` (FFT 2048) for doublings.
- **Never decide "is this note played" from octave-summed salience.** A strummed A3 then reads as a bass A2. Use plain per-pitch bins.
- **Barlines come from the music**: roots on downbeats, the most notes on beats. A draft had every barline three 16ths late because it took the start of a repeating figure as beat 1.
- **When the user doubts a note, re-test with a finer tool** rather than defending the first reading. Their ear was right every time.

## Files
- `scripts/`:
  - analysis: `analyze.py` · `barmap.py` · `report.py` · `look.py` · `words.py` (lyrics second opinion) · `acap.py` (shared helpers, `Bars`, `Layout`)
  - part transcription: `partscope.py` (lowest / stack / rows / onsets / repluck / glide / profile)
  - arranging: `engine.py` · `build.py` · `render.py` · `qa.py` · `fretboard.py` (guitar chord shapes, string/fret placement for TAB staves)
  - install: `setup.sh` · `check_env.py`
- `references/`: install · analysis · transcription (one part → tab/chart) · troubastack (send charts and tabs to a band's TroubaStack server) · engine · notation · style-research (how to find what is core to a new style or lineup, with a worked log)
- `templates/song.py`
