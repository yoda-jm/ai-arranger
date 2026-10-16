# Analysis tools: what they do, how good they are, how to read them

The accuracy figures come from one cartoon-theme recording (male lead, band, backing vocals, a tempo change), scored against a hand-checked transcription.

## Pipeline (`analyze.py SONG W --lyrics L.txt [--anchor T=1] [--basic-pitch]`)
| step | tool | output | time (2.5-min song, GTX 1660 6 GB) | notes |
|---|---|---|---|---|
| wav | ffmpeg | `audio.wav` | 1 s | |
| sep | Demucs **htdemucs_ft** | `stems/{vocals,drums,bass,other}.wav` | ~75 s (CPU: ~8 min) | Fine-tuned 4-stem model. "other" = everything except voice, drums and bass (keys, guitars, brass, flute, strings). |
| kara | audio-separator, **Mel-RoFormer karaoke** (aufr33/viperx) | `stems/lead.wav`, `stems/backing.wav` | ~2 min | Runs on the vocal stem. Lead = the main voice; backing = harmonies and doubles. Double-tracked leads and unison backing often stay in "lead". |
| bars | **beat_this** (CPJKU, ISMIR 2024), librosa fallback | `beats.json`, `bars.json` | 10 s | Beats and downbeats; follows tempo changes. Bars match a hand map within 0.13 s, the tempo change included. |
| tune | librosa `estimate_tuning` | `meta.json: tuning_cents` | | The offset is applied to f0 and every CQT. |
| f0 | **torchcrepe** full + Viterbi, on the lead stem | `lead_f0.npy` (10 ms frames, MIDI) | 20 s | Unvoiced = periodicity < 0.45 or quiet. |
| words | **Whisper** medium, word timestamps, on the vocal stem | `words.json` | ~90 s | No prompt; words respelled from the lyrics file afterwards (see pitfalls). |
| drums | band-limited onset envelopes of the drum stem | `drumgrid.json` | 5 s | K = 30–120 Hz, S = 1–4 kHz, h = 7–11 kHz. `X` strong, `x` weak. |
| bp | basic-pitch (optional) | `midi/*.csv` | 1 min | Polyphonic notes. It invents overtones, so prefer NNLS for chords. |
| report | `report.py` | `report.md`, `draft.py` | 45 s | Re-run alone after changing the bar map: `analyze.py ... --force drums,report`. |

## Reading `report.md`
- **Header**: tuning, tempo runs and **irregular bars**. An irregular bar means the tracker counted 3, 5 or 6 beats. The beats are re-spread evenly; check the bar *starts* (`look.py W roll audio N-M`). In the example the slow reprise was tracked at 6 beats per bar but the bar starts were right.
- **Levels `LKdbo`** (lead, backing, drums, bass, other: ` .:=#`): the instrumentation per bar at a glance. Use it to find the sections: where the drums stop, where the backing vocals enter, an instrumental (lead blank).
- **Chords**: one per half bar, from the accompaniment chroma plus the recorded bass. `X|Y` means a close runner-up. Accuracy: root 81%, root + major/minor 80%. Typical errors:
  - `sus4` instead of a triad or m7 (melody notes leak into the chroma).
  - `Dm7` for `Bb/D` (the bass decides the root).
  - `maj7` vs triad.

  Fix these with the bass line and `look.py chords` (top-3 candidates), and hear the chord in context.
- **≈rep**: `17+2` means these 2 bars repeat the harmony of bars 17–18 a whole step up. This is the fastest way to map the form and the key changes. On that recording it found: the verse 2 half in C = verse 2 +2; the flute section = verse +5; the horn section = chorus −1; the reprise = the brass section +2.
- **Key regions**: from the chords (the major key whose scale fits most chords in an 8-bar window, tonic and dominant favoured). Correct on 73/81 bars; errors only in the first bar or two after a modulation. Minor-key songs show up as their relative major, so check the tonic chord.
- **Instrument lines that quote a vocal phrase**: the top line of the "other" stem matched against the lead draft, transposition-aware, ±1 16th. These are *hints*: in the example it found the flute playing the verse tune +29 and the reprise doubling at the octave, but also some false matches. Confirm each one with `look.py roll other`.
- **Backing vocals per 8th**: NNLS pitches of the backing stem, high to low, in bars where backing is present. Read the parallel lines out of it (e.g. a constant 3rd under the lead).

## `draft.py`: editable transcriptions (one entry per recording bar)
- `LEAD = {bar: (tokens, syllables)}`. Pitch per 16th = median f0. Note boundaries come from lead onsets + word starts, or from a pitch change lasting ≥ 2 16ths (scoops absorbed). Pitches are snapped to the local key's scale unless the sung pitch is within 25 cents of a chromatic note. **65% of 16ths exact** vs the hand transcription (the hand transcription itself scores 72% against the f0, so the draft is close to the ceiling). It is weakest on speech-like verses and on ornaments.
  - Syllables: Whisper words split with pyphen hyphenation and spread over the note onsets inside each word. `_` marks a note with no syllable found.
  - **Always check**: repeated notes on one pitch (they need onsets), notes split by vibrato, octave of the first note, pickups that belong to the previous bar, and syllable counts on melismas.
- `BASS = {bar: tokens}`: NNLS per 16th on the bass stem plus bass onsets. **82% of 8ths have the right pitch class.** The octave is the recorded one (often E1–C3), so sung basses usually go up an octave.
- `CHORDS = {bar: [sym, sym]}`: the report's chords. `KEYS = {bar: key}`: the key regions.
- `OTHER_TOP = {bar: tokens}`: the highest NNLS pitch per 16th of the "other" stem. It mixes the hook instrument with keyboard chords; useful to read riffs, but noisy.

## Zoom tools (`look.py W ...`)
- `roll STEM BARS [--f0] [--part OUT:VOICE]`: piano-roll PNG (harmonic salience, 3 bins per semitone, lines at bar / beat / 16th). **The best way to verify a transcription**: overlay your arranged part (`--part`) and the lead f0 (`--f0`). Open the PNG with the Read tool. Use `--lo/--hi` to zoom the pitch range (bass 28–60, lead 43–76, flute/brass 55–96).
- `nnls STEM BARS [--div 8|16]`: text multi-pitch. Use it for bass lines, backing chords and brass voicings. `--thr` 0.2 shows more voices, 0.5 fewer.
- `f0 BARS`: lead pitch per 16th with the cents offset (`F4-0.2`) and onsets (`*`). Use it to settle a doubtful note.
- `chords BARS [--div 4]`: top-3 chord candidates with scores, plus the bass.
- `drums BARS`, `bp STEM BARS`, and `clip BARS` (cut audio for the human to listen to).

## Pitfalls (each one cost time on the first song)
1. **Don't prompt Whisper with the lyrics.** `initial_prompt` made it skip the whole first verse. `analyze.py` transcribes unprompted, then respells the words from the lyrics file with a sequence alignment.
2. **Beat trackers that assume one tempo** (`librosa.beat_track`) silently drift through tempo changes and rubato. beat_this follows them. Still check the tempo runs. To pin bars by hand: `barmap.py W --fix 53=93.80,54=95.90 ...`, then `analyze.py ... --force drums,report`.
3. **Bar 1** should be the first downbeat of the first sung phrase (or the song's real bar 1). Set it with `--anchor TIME=1`. Intro bars then get 0, −1, …, which keeps the score's numbering readable against the lyrics.
4. **basic-pitch is not a chord detector**: it reports overtones and bleed as notes. Use NNLS (harmonic templates) for multi-pitch, and the bass stem for roots.
5. **The karaoke split is imperfect**: backing vocals in unison or an octave with the lead stay in "lead", and lead ad-libs can land in "backing". Cross-check with `vocals`.
6. **Chords from the melody alone are wrong** on passing tones. Take the root from the bass, the quality from the accompaniment chroma, and push long notes an 8th early.
7. **Transposed repeats are everywhere** (key changes, instrumental quotes). Check `≈rep` before transcribing a section from scratch. Copy with `tr_tokens` / `tr_chords`.
8. **Tuning**: recordings are often 10–40 cents off A440. It is corrected automatically; check `tuning_cents` if pitches look a semitone off throughout.
9. **The f0 is of the singer, not the score**: scoops, falls and blue notes are real. Notate the intended pitch (the chord tone or scale tone) and the intended rhythm (usually on the 8th grid).
10. **Separation artefacts**: reverb tails and bleed create ghost notes at −30 dB. All tools gate at 3–5% of the stem maximum; raise `--thr` if needed.
