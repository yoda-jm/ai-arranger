# Transcribing one part ("repiquage"): a bass line, a riff, a tab, a chart

Use this page when the goal is to write down what someone plays, not to arrange: a bass part, the low notes of a guitarist, a riff filmed on a phone, a chord grid, a song structure. The output is usually a tab or text chart that a musician reads, sometimes a `song.py` for an arrangement.

The rule that governs everything: **the recording is the truth.** The user's draft, the original record and your own earlier answer are all hypotheses to test against it.

## 1. Situations this covers (anonymised real cases)

| Situation | Input | What to deliver |
|---|---|---|
| A cover band takes on a new bassist. Before, the guitarist played the bass role on his low strings. | a live concert video: a multi-hour camcorder file plus a timestamp | the bass part per section (patterns), checked against every pass, plus the song structure |
| A bassist films himself playing a riff for another bassist. | a phone video (image + audio) at a practice tempo | a tab with the positions seen in the image, octave and re-plucks checked on the audio |
| A musician drafted a tab and asks you to continue or check it. | their draft + a recording | corrections explained per note, their layout kept |
| Verify or complete a section ("the chorus", "the verse into the chorus"). | the same recording | the section fixed, the transitions, and the one pass that differs |
| Grid + lyrics + form of a pop song, as a base for a re-arrangement (bossa, a cappella...). | the record | `song.py` (see SKILL.md §2), then a style skill |

## 2. Getting the material
- **Long concert files** (camcorder `.MTS`, 1-2 h): the user gives a timestamp. Extract the audio with a margin, starting a few seconds before the song and cutting well after it (`ffmpeg -ss 58:40 -t 420 -i X.MTS -vn -ac 2 -ar 44100 song.wav`). Record the offset: every time the tools print is relative to the extract, and the user wants video timestamps.
- **Who plays what**: grab a few frames (`ffmpeg -ss T -i X -frames:v 1 -vf "yadif,scale=960:-1" f.jpg`; `yadif` because camcorder video is interlaced) and look. Don't assume a bassist: a missing bass player means the bass role is in a guitar, a keyboard left hand, or nowhere.
- **Contact sheets of the hands**: 4 frames/s cropped on the neck, tiled with timestamps (PIL). Far camera shots only show the hand position (low or high on the neck), not frets. A close phone video shows strings and frets: first note which string is on top in the image and which side the headstock is.
- **Find where the song ends**: the guitar stem drops, applause starts, or the next song starts in another key (a 3 s chord scan shows it).

## 3. Analysis order for a part inside a band (live or record)
1. `analyze.py song.wav W --lyrics lyrics.txt`, then read `report.md`. Live, the beat tracker often locks onto the 8th note of a slow song (130 bpm for a 65 bpm song). One real bar is then **2 tracker bars**; partscope's default `--tb 2` assumes that.
2. **Form** from the levels and the words: vocal entry, drums dropping out (a quiet verse), `≈rep`, and the lyrics the band uses. Whisper is poor on live audio (it may even pick the wrong language), so trust section energy and the band's lyrics sheet.
3. **Which stem holds the part?** Print per-stem levels every few seconds. If `bass` is near −70 dB, there is no bass instrument and the guitarist's low notes are in `other`.
4. **First pass**: `partscope.py W lowest other BAR NBARS --labels F,C,...` for the line, then `stack` with the same bar from every pass. The passes agree: that is the pattern. One pass differs: a slip, or the one deliberately different section. The user's rule: "always the same, except when the guitarist makes a mistake". A figure heard in at least one pass belongs in the chart.
5. **Look at the whole line as a picture first**: `rows --fs 0.6` over 4-6 bars (all passes of a section, one row each) shows where the line moves (walks, rising endings, stops) far better than tables.
6. **Then settle every note with the right test**:
   - strum or bass note: `onsets` (plain bins);
   - doubled note: `repluck` (FFT 2048 on the note's own bin);
   - slide or pluck, E or F: `glide`;
   - chord quality: `profile`, against a bar whose chord you know.
7. **Octave mapping**: a guitarist's bass role goes down **exactly one octave** for the bass, every note the same way (his A2 is the bass's E string, 5th fret; his E3 is the A string, 7th fret). Don't move a note to another octave for nicer voice-leading. That changes what the recording says.
8. **Picked line or strummed chord?** Decide this before writing a busy line.
   - If the tables look like chord roots only, the player may be picking a busy pattern: run `partscope picked` over every pass.
   - But a 16th **strum** also gives a note start on every 16th. Its "lowest note" then jumps between the strings of the chord: C# and G# showed up between the A roots.
   - Test it: a strum attacks the low and the high strings together on every stroke. A picked line moves on its own, and its notes are not all chord tones.
   - When it is a strum, write the **bottom notes of the chord** in the strum's pulse (often 8ths). The user's sketch usually names them.
   - A second recording (another concert, a rehearsal) settles what one night's playing can't. Verify roots and harmony with `profile`.
9. **A user's sketch may have no rhythm**: one note every 2 characters plus remarks ("double each note before changing", "the 4 in 8ths, crescendo"). Translate it into the grid with the rhythm the recording shows, and keep their frets when the pitches agree.
10. **Phrase ends and transitions are separate questions**: the last bar of each phrase (players put their fill there: an arpeggio, a walk-up), verse into verse, verse into chorus, chorus into verse, and the ending. Check each on every pass where it occurs.

## 4. A solo instrument on a phone (the bassist-films-a-riff case)
- **Phone microphones barely record a bass's fundamental. The 2nd harmonic is usually the loudest partial.** Read every octave the same way. A high C on the G string (5th fret) was first misread as the A string because of this.
- **Repeated note**: a re-pluck shows the level dropping 4 to 17 dB and coming back up at least about 4 dB, often with a pitch flicker. A level that only falls is a note ending. A rise-only test missed a real second note, which the user heard.
- **Not notes**: weak pitched sounds at about −27 to −35 dB while the hand moves along the neck, and the noise of the hand leaving the neck at the end. Don't write a "ghost" that is really fretting-hand noise. A false start before the take isn't part of the riff either.
- **Practice tempo** can differ from the record (60 bpm against 74). Transcribe at the video's tempo.
- **Positions**: take the string and fret from the frames (finger flat across two strings, etc.). The audio alone gives the pitch, not the string.

## 5. Bar lines and counting
- **Find beat 1 from the music**: where the chord roots land and which positions carry the most notes. A draft whose barlines sat three 16ths late had treated the start of a repeating figure as beat 1 (29 notes on the beats against 19 the other way).
- **Musicians count differently**: a user counting at 120 calls each half of a chart bar "a bar", so their "bar 7" is the first half of chart bar 4. Confirm the counting before discussing "bar N", and answer with the lyric line too ("the Dm under 'Such a lovely place'").

## 6. Writing the tab or chart
House style (it came from the users and works well on a tablet):
- **Bars**: one chord per bar. The chord row sits over the strings, starting at the bar's first column.
- **Grid**: 2 characters per 16th. `¦` splits each bar into halves of 16 + 17 characters; 4 characters make an 8th.
- **Articulations**: slide `/5` at the target note, hammer-on `3h5`, pull-off `8p7`.
- **Patterns** are named A, B, C (intro/verse, chorus, the different verse...). Each stave carries its chords.
- **Transitions**: a variant ending is a small extra stave under the bar it replaces, labelled with its target (`F (to the chorus)`).
- **Page 2 = the structure**: one `## Section - Pattern X` heading per section, with the first lyric line under it, and the endings noted ("last bar to F"). Intro variants go here too ("Pattern A, bass alone; Pattern A, band").
- **Remarks go in a footnote, not in a chord row.** A `(...)` at the end of a chord row reads as if it belonged to the last chord.
- **To explain a passage**, put a counting ruler over the tab lines (`1 e & a 2 e & a`), plus a per-beat table: what is heard, then what is written.

**When the band keeps its charts on [TroubaStack](https://github.com/yoda-jm/troubastack)**, write the tab in its chart dialect (`{sot}`/`{eot}` tab blocks, `{fn}` footnotes, `{np}` before the structure page, ASCII/Latin-1 only). Then save it through its API: re-fetch, preview, save with the base revision, verify, and keep a local copy of each revision. Details: [troubastack.md](troubastack.md).

## 7. Mistakes made, and what prevents them

| Mistake | Fix |
|---|---|
| Barlines shifted by three 16ths (beat 1 taken where a figure starts) | count notes on beats, roots on downbeats |
| Octave errors on phone audio | 2nd harmonic loudest; read all notes the same way |
| Missed re-plucked note (rise-only test) | dip-and-recovery test |
| A strummed A3 counted as a bass A2 ("doubled" notes that weren't there) | decide attacks on plain per-pitch bins (`onsets`), never on octave-summed salience |
| Then the opposite: real 16th doublings erased, because 0.5 s CQT windows (36 bins/octave at A2) and 4096-point FFTs merge two plucks 0.23 s apart | `repluck` with a 2048-point FFT; check a held note as a control (flat line) |
| A note moved an octave for voice-leading (open E instead of the guitarist's E3) | map one octave down, uniformly |
| A note at −30 dB written as a ghost note | it was the hand moving; not a note |
| Defending a first reading when the user doubted it | re-test with a finer tool; the user's ear was right three times |
| Assuming the cover keeps the record's chords | a live guitarist played Dm where the record has E7, in all 3 choruses. Show it with `profile`, report it, and let the user decide. Here they kept the live version. |
| Annotation placed at the end of a chord row (looked like it belonged to the wrong chord) | footnote |
| Answering "bar 7" in chart bars when the user counts half-bars | confirm the counting, cite the lyric |
| Read the user's remark "double each note before changing" as a double at the start of each note, from a dip right after the onset | the repeat was at the **end** of each note (on the & of its last beat), just before the line goes down. Take the remark literally ("before changing"). A dip 60-130 ms after an onset is not evidence of a double (a fading neighbour note, beating or a strum make the same shape) |
| Read two semitones from the same FFT bin (A2/A#2/B2 at 2048 points) and drew conclusions | check that the columns differ; use `notes16` (FFT 4096) for chromatic bass lines |
| Wrote a picked chorus as roots in half notes, from the user's 5-note sketch ("completely broken... not enough notes, listen to the guitar") | a guitarist playing the bass role often picks continuously in 16ths. Use `partscope picked` over every pass and write the consensus (the notes in 2+ passes). A short sketch (A E E B A) can be the skeleton of a busy line, not its rhythm |
| Then the opposite: wrote a strummed chorus as a busy picked line ("still not convinced"). `picked` took the lowest started note per 16th of a 16th strum, so other strings of the chord (C#, G#, B) came out as passing notes | compare low-band (75-190 Hz) and high-band attacks per 16th: a strum hits both together. List all the notes that start in the low register for every pass, on two recordings if possible (8 choruses here). The bottom of the chord (A+E, E+B) in the strum's 8th pulse was the part, and it matched the user's 4-note sketch |
| Stopped a rising line too early (the user: "a little higher than you think") | follow a moving line until it really stops: it went A# B, C# D#, E, F#. Check the semitone and the note above the last one you found |
| Missed the figure the player puts at the end of each phrase (a down-and-up arpeggio) although the user's sketch had it, and the "moving up" at the end of the chorus | look at the **last bar of every phrase** and the last bars of every chorus in every pass with `notes16` and `rows --fs 0.6`. The user's sketch often already holds the figure; the player "doesn't always succeed", so one clean pass is enough |

## 8. A whole band from a record: error families and the rules that prevent them
A full-band transcription (`examples/code-monkey/`) was scored against the song's official master tracks and against fan transcriptions. The scores: lead 79% of 16ths exact, bass 90% right pitch, drums F 88/90/76 (kick/snare/cymbals), lyrics 49/51 lines. The errors fell into four families. The **method** ones are rules now; follow them.

**1. The tools hear a mix (signal limits).** Work around them; say when you can't.
- **Four stems merge instruments.** The record had five overdriven guitars; they were written as one electric plus one *acoustic*, because the broadband attacks of distorted 8ths look like strumming.
  - Count instruments per section using stereo position (a doubled part is a left/right pair) and the 6-stem Demucs model (`htdemucs_6s`, guitar stem).
  - Ask the user to confirm the line-up before writing parts.
- **A loud pedal masks short chords.** A palm-muted E ringing through the verse hid B and C#m stabs shorter than half a bar.
- **Power chords have no third.** Major against minor (A or Am) rests on a faint note, and distortion adds false partials.
- **Distortion fakes a bass.** An overdriven fifth (A2 + E3) makes a difference tone at A1. Sub-guitar energy alone doesn't prove a bass; look for its own attacks. On this record there was a real bass, and a fan tab had claimed there wasn't.

**2. The method stopped too early or decided too coarsely.** These are rules now.
- **Label chords at the bass's attacks** (per 8th), not per half bar. When a pedal dominates the chroma, read the chord from the other pitches. In the record, the bass line written by the same session had the riff right (E B A | A C#m B) while the chord symbols said "E | A E".
- **Name the upper chord from the guitar's notes**, not from the bass plus chroma alone: E over D# (Emaj7/D#) was written B/D#.
- **After finding one backing voice, look for the next.** The backing stem held a unison double, an octave double *and* a harmony a 5th above. Only the octave was found and written.
  - Subtract the lead and the octave partials and search what remains.
  - Report the intervals found, per section.
- **When sources disagree on a word, count the sung notes.** "Lots" is sung on two notes, so it is "a lot". "To see" has no note for "To", so it is "See". Both errors came from trusting one source (the recogniser, or a single fan comment) over the audio.
- **Before delivering, cross-check what already exists**: chord charts and tabs (Ultimate Guitar, chords-and-tabs), lyrics wikis, and official multitracks or stems. Many CC artists publish them, and game stems exist for some songs. List the disagreements, then settle each one on the audio.
  - Here the fan charts would have flagged the verse harmony, both A minors and both lyric errors before delivery.

**3. Notation choices were made silently.** State them, or don't make them.
- **Blue notes**: the singer sang C, D and G natural where the key has C#, D# and G#. Writing them into the key costs about 10 points of pitch agreement (pitch track 89.8% → written lead 78.9%). Keep a chromatic pitch that recurs across passes; normalise only a one-off.
- **Slides and scoops** are written as their target note, which is right for a singer. Say so in the README.
- **Note lengths** end where the singer stops (the voiced end), not at the next syllable. Holding through breaths added 176 wrong 16ths.
- **Simplifications** (ghost kicks, fill notes, cymbal detail: drum recall 63-83%) go in the README's "not written" list, with the bars.

**4. Checking needs care too.**
- With master tracks, `groundtruth.py OUT W TRACKS --map V="Lead Vox" BASS=Bass:bass DR=Drums:drums --activity` does the checking:
  - it aligns them by cross-correlation (here 1.032 s);
  - it shows who plays when;
  - it scores each part on its own track: pitch per 16th (torchcrepe; pyin for the bass), drum hits classified by each hit's spectrum.
- A first drum check used plain frequency bands and counted the snare's low end as kicks, which reported 58% kick recall instead of 79%. Measure the yardstick before trusting the score.

**Before delivering a full-band transcription**:
1. The line-up confirmed by the user.
2. Chords re-read at the bass's attacks.
3. Backing voices searched after the first one.
4. Lyric conflicts settled by the sung notes.
5. Published transcriptions and any official stems cross-checked.
6. Notation choices and simplifications listed in the README.

## 9. Let the user decide by ear: audition pages (`audition.py`)
When a part has several defensible readings, don't describe them: **let the musician hear each one inside the band**. `audition.py` synthesizes each option on the recording's own bar map and plays it in sync over the real recording, in a page where the user:
- switches options while the band keeps playing;
- loops the spot and reads each option's tab;
- marks bars that still need work;
- saves the picks.

Claude reads them back (`read_db`, collection `decisions`) and writes the next revision. Full guide: [audition.md](audition.md).

Several text-only revisions had left the user "still not convinced". Eight audition rounds settled every open point of the same chart, and the user asked to keep the technique as the way to decide.

```bash
cp $C/../templates/audition_spec.py $A/audition_<topic>.py    # edit: clips (bar ranges + chord labels), questions, part()
$PY $C/audition.py $A/audition_<topic>.py $A/out_audition --check other   # --check prints the timing offset
```

The rules that made it work (details in audition.md):
- **Ground every option in evidence**, and say which in the option's text. For example: "the guitarist plays it in both concerts (10 passes)", "both online tabs of the record", "your sketch".
  - Mark the version now on the chart.
  - Put the measured version among the options.
- **Small rounds**: 1-3 questions on one passage, with `layers` when they sit on different bars of a long passage or recur over the whole song. Then save, revise, and do the next round.
- **A whole-song listen-through** between rounds catches what short clips miss. The user marks bars on it, and the marks become the next round.
- **Check the timing** (`--check`) and the bar map (`BAR_FIX` for a rubato intro) before publishing.
- Say plainly that the part is synthesized and that you can't hear it.

## 10. Reporting
- Lead with what was found and what changed.
- For each claim: the video timestamp, and what is heard per beat.
- Separate "the pattern" from "slips in one pass".
- Say plainly when a previous answer of yours was wrong and why (which tool failed).
- Put decisions that are the user's in a question (record chord or live chord? fill an empty stave?), not in silent edits. When the answer is a matter of ear, build an audition page (§9) instead of describing the options in text.
