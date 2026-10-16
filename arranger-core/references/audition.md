# Audition pages: let the musician decide by ear (`audition.py`)

An audition page plays the **real recording** with each candidate version of a part **synthesized on the recording's own bar map** and laid over it. The musician:
- switches options while the band keeps playing;
- loops the spot;
- reads the tab of each option;
- marks bars that still need work;
- presses "Save for Claude".

Claude reads the saved picks back and writes the next revision of the chart.

It replaces describing options in text. On a bass chart that had gone through several text-only revisions and left the user "still not convinced", eight rounds of audition pages settled every open point, and the user asked to keep the technique as the way to decide.

```bash
C=arranger-core/scripts; PY=${ACAP_PY:-python}
cp arranger-core/templates/audition_spec.py $A/audition_<topic>.py      # edit W, the clips, the questions, part()
$PY $C/audition.py $A/audition_<topic>.py $A/out_audition --check other   # renders, embeds, checks the timing
# publish $A/out_audition/<ID>.html with the Artifact tool, capabilities {"db": {}}
# picks saved: Artifact action "read_db", collection "decisions", doc_id "<ID>"
```

The template runs as-is on the repository's worked example once `examples/code-monkey/regenerate.sh` has made its analysis:

```bash
$PY $C/audition.py arranger-core/templates/audition_spec.py examples/code-monkey/out-audition --check other
```

## 1. When to use it
- **A choice of the musician's ear.** Use it whenever a part has more than one defensible reading:
  - the record's line or the live player's;
  - where a double falls (the & or the last 16th);
  - which octave;
  - how a fill or an arpeggio ends;
  - a groove written in straight 8ths or in the record's rhythm;
  - a note the user doubts.
- **A note from the user** ("I don't like the end of the arpeggio, make suggestions", "try a low E as the last note"): answer it with the next round.
- **A last check.** Play the whole chart over the whole recording, with no questions (a *listen-through*). The user marks the bars that still sound wrong, and each marked area becomes the next round.

Don't use it for facts the measurements settle on their own. Write those, and list them under "Already settled".

## 2. The cycle
1. **Measure first.** Each option should come from evidence. Typical sources:
   - what the player does in each pass, from `partscope.py` (the re-pluck test, `notes16`, fine-bin checks);
   - what a second recording does;
   - what the published tabs or chord sheets of the record say;
   - the user's own sketch or remark.

   Say which in the option's text, and tag the option ("now on the chart", "what the band plays", "your round-3 pick").
2. **Write the spec.** Make one clip per passage: a stretch of the recording where the part can be heard. Then:
   - put in the questions and their options;
   - write `part()`, the notes of each option;
   - start the page on the option the evidence favours (`default`).
3. **Render with `--check STEM`.** Every render prints the offset between the synthesized notes and the onsets of the player's stem. Anything beyond a few milliseconds means `SHIFT` or the bar map needs fixing (a bass that drifts off the band makes every option sound wrong).
4. **Publish** the HTML with the Artifact tool and `capabilities: {"db": {}}`.
   - Keep **one artifact per song**: republish to the same file path, and keep the page title across rounds.
   - Give **each round its own `ID`**, so earlier picks stay in the store.
5. **The user listens, picks and saves.** The page writes `decisions/<ID>`, which holds:
   - one key per question (the option id);
   - `note`: free text;
   - `marks`: `{clip: [{from, to, chords, note}]}`, the areas the user marked;
   - `savedAt`.
6. **Read the picks** (`read_db`). Apply the clear ones to the chart and save it as a new revision. Turn the note and the marks into the next round.
7. **Report** in a few lines: the picks, the revision saved, and what the next round asks.

## 3. The spec
Plain Python, run with `runpy`. Every key, as `audition.py --help` prints it:

| Key | Meaning |
|---|---|
| `ID`, `TITLE`, `INTRO` | page id (also the db document name), title (keep it across rounds), one paragraph shown at the top |
| `W` | the analysis dir of `analyze.py`: `bars.json`, `audio.wav`, `stems/` |
| `AUDIO` / `BAND_STEMS` | the band track: a file, or a mix of stems such as `['drums', 'other', 'vocals']` to **drop the record's own part** (a record with a real bass) |
| `TB` | tracker bars per real bar (2 when the tracker counted 8ths) |
| `PROGRAM` | GM program of the synthesized part: 33 fingered bass, 32 acoustic bass, 25 steel guitar, 0 piano |
| `TUNING`, `NAMES` | open strings low to high and their names, for the tabs (bass `[28, 33, 38, 43]`, `'EADG'`) |
| `SHIFT` | seconds added to every note; measured with `--check` (0.025 on the live recordings this was built on) |
| `BAR_FIX` | `{bar: start time}`: re-place bars the tracker got wrong, 4 even beats each (see §5) |
| `BAND_KBPS`, `PART_KBPS` | AAC bitrates, default 112 / 80; 96 / 64 keeps a 5-minute song near 8 MB |
| `CLIPS` | `[dict(id, title, src, why, bars=(first, last), labels=[(chord, section), ...], questions=[...], layers=..., tab_bars=[...], pre=0.6, post=1.2)]` |
| `QUESTIONS` | `{qid: dict(label, why, default, options=[dict(id, name, text, tag)])}` |
| `KEPT` | points already settled, with their evidence, listed under the players |
| `CHART` | the chart text, shown under the players (for a listen-through) |
| `part(clip_id, choice)` | returns `{bar: [(k16, midi, dur16[, (string, fret)[, tech]]), ...]}` for one combination of options |

Notes on `part()`:
- `k16` is the 16th-note index 0-15 in the bar.
- A `dur16` running past 16 **ties over the barline**, for a push. In that option, drop the next bar's downbeat note.
- `(string, fret)` is optional, e.g. `('G', 4)`. Without it, the tab takes the lowest fret.
- `tech` is optional: `'h'` hammer-on, `'p'` pull-off, `'/'` or `'\\'` slide, as written in the tab. The note is then played **legato** from the previous note: no new attack, and the pitch steps (h, p) or glides into the beat (slides), with MIDI pitch bend. A synth playing each tab digit as a new attack makes ornaments sound wrong; render them legato, or give the player a "removed" option to compare by ear.
- `choice` maps each question of the clip to an option id.

Labels: one `(chord, section)` per bar. A space splits the bar into two chords (`'E E/D#'`), so don't put spaces inside a chord name. The section goes on the bar where it starts and stays `''` elsewhere.

## 4. Questions, clips and layers
- **A clip without layers** renders every combination of its questions. Keep it to 2-3 questions; questions on the same bars can then be heard together (where the double falls + which E starts bar 4).
- **Layers**, `layers={q: (first, last)}` or `{q: [(first, last), ...]}`:
  - each option is rendered only over its question's bars, as short segments scheduled at their time;
  - the rest of the part is one base layer;
  - N questions × M options cost N·M small renders, not Mᴺ full ones;
  - the page swaps one question's segments while everything else keeps playing.

  Several ranges per question cover a figure that recurs, such as every chorus entry or every E bar of every chorus. One whole-song page held 3 questions over 13 ranges in 62 small files and stayed at 11 MB. Ranges of different questions must not overlap; `audition.py` checks this.
- **Pick the passage on purpose.**
  - A quiet pass (no drums) makes the part easy to judge; a full pass shows how it sits in the groove.
  - Use a stretch where the band does not play the part itself, or drop it with `BAND_STEMS`.
- **A listen-through** is a clip with no questions over the whole song, with `CHART` set. Write the form of *that* recording in `part()`. A concert can differ from the chart (a verse played in time in one concert, in free time in the other). Follow the recording and report the differences.

## 5. The recording's bar map
- The notes are placed on `bars.json`, so they follow the live tempo, its pushes and its slowing down.
- **A rubato intro the tracker got wrong.** Measure where the pattern's notes really fall. In one case they fell half a bar after the tracker's bars, with one 7-beat bar absorbing the shift. Re-place those bars with `BAR_FIX = {3: 8.27, 4: 11.24, 5: 14.16, 6: 17.3}`.
- **The last bar** ends at `bars.json`'s `end`. `audition.py` adds a closing bar for it, so a final note can be held to the end.
- A clip that starts at bar 1 is clamped to 0 s. Before that fix, a negative start shifted the whole part by the pre-roll.

## 6. The page
Generated from `templates/audition_page.html`, with all the audio embedded (AAC). It needs no network and no library.

**Player:**
- Play, From the start, the time, and Band and Part volume sliders.
- "Loop 2 bars from the clicked bar".
- The bar strip: click a bar to jump there. Long clips wrap into rows that scroll to follow the playhead.
- The player stays pinned at the top of its section while the options scroll under it.

**Questions:**
- Each question has its colour. The bars it changes light up in that colour, and a 16th ruler under each bar marks the exact beats where its options differ. `audition.py` computes these from the notes.
- The heading names the bars and beats; "Hear this spot" starts one bar before.
- Selecting an option swaps it in while the band keeps playing, and the bars it changes flash.

**Tabs:** the tab of the selected option (for layers, the first range of each question: list the most telling range first), 4 bars per stave.

**Marking:** "Mark bars" (click bars), or M / "Mark the bar playing now" while it plays. Marked areas are listed with their chords, a note box, "Hear it" and "Remove".

**Save:**
- The page writes to the artifact's store and restores the picks, marks and note on the next visit.
- Without a store (a local file, a viewer without access), it prints a line to paste to Claude instead.

## 7. Size and performance
- AAC bitrates of 112/80 kbps cost about 1 MB per 30 s of clip.
- The Artifact limit is 16 MB per page; `audition.py` warns above 15 MB.
- Mostly silent full-length layers are small to download (0.15 MB) but **decode to about 50 MB each** in the browser. That is why layers are short segments.
- Rendering runs fluidsynth once per option and segment, about a second each. `--check` loads the stem once.

## 8. Requirements
- fluidsynth with a GM soundfont (`ACAP_SF2` to point at one).
- ffmpeg with its AAC encoder. Some builds have no MP3 encoder; AAC is what the page decodes everywhere.
- `pretty_midi`, `soundfile`, `numpy`, and `librosa` for `--check`. All are in the toolkit's venv.

## 9. Lessons from the first real use
These come from eight rounds on a live cover's bass part.
- **Measure, then offer.** The measured version was among the options every time. The user picked it most often, but not always: once they kept the chart's version after hearing the alternatives, and once they asked for a note no recording had. Both are the user's call.
- **The user's ear finds what the tables missed.** It found a doubled note at the end of a bar, a walk-down starting one note earlier, an ending on the tonic, and an intro that follows the verse pattern. Re-test each remark with a finer tool (the re-pluck test, a long FFT to tell G# from A); it was right each time.
- **Keep rounds small.** 1-3 questions, each with 2-6 options, then save, revise, and do the next round. A whole-song listen-through between rounds catches what the small clips miss.
- **Report the version in one line.** Say which revision went to the band's server, and what the next round asks.
- **Say plainly that the part is synthesized** and that you can't hear it yourself. Ask the user to report anything that sounds off.
