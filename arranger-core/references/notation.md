# Score output: MusicXML and MuseScore details that `build.py` handles

`build.py` writes MusicXML 4.0 itself, without music21, so every detail below is controlled directly. Read this page when you change the output or debug an import.

## What MuseScore needs to get right
- **Voices play as piano.** Each sung part declares `<score-instrument>` with `<instrument-sound>keyboard.piano</instrument-sound>` and a `<midi-instrument>` with `<midi-program>1</midi-program>`, plus volume and pan. MuseScore 4 then imports the part as a Piano instrument, so its mixer shows piano instead of choir "oo/ah" samples. Choir sounds smear the harmony; piano makes wrong notes obvious. The staff names stay "Soprano 1", "Alto" and so on.
- **The VP staff is a drum kit.** It is a percussion part with one `<score-instrument>` per sound and `<midi-unpitched>` = GM note + 1 on channel 10. The notes use `<unpitched><display-step/octave>` and `<instrument id=...>`, with × noteheads for rim, hats and crash. MuseScore imports it as `drum.group.set`.
- **Chord symbols don't play.** MuseScore 4 plays chord symbols by default, through hidden piano chords. The MusicXML has no per-symbol play flag, so build.py imports the file, unzips the `.mscz`, inserts `<play>0</play>` into every `<Harmony>` of the `.mscx`, re-zips it and exports PDF/MIDI from the patched file. To verify, the note count of the exported MIDI equals the number of sung events. Use `--play-chords` to keep them playing.
- **Chord symbols are positioned with `<harmony><offset>`** in divisions (4 per quarter), placed before the notes of the measure. Writing them between notes pushed notes past the barline in an earlier version.
- **Lyrics**: `<lyric><syllabic>begin|middle|end|single</syllabic>`. A hyphenated token such as `Dash-` / `-ing` maps onto these. Lyric font 8.5 pt and `lyricsMinDistance` 0.6 sp are patched into `score_style.mss`, so eight staves of lyrics stay readable.
- **Layout**: a new system every 4 bars (`--bars-per-system`), except that the final bar joins the previous system. The scaling is 5.2 mm per staff space (`--scaling`), the page is A4-ish with 70-tenth margins, the staff distance is 55 and the system distance is 90. Eight staves plus lyrics give about 2 systems per page, so 80 bars is about 12 pages.
- **Durations**: notes are split at beat and half-bar boundaries so the beat stays visible (dotted 8th + 16th, ties across beat 3). The 4/4 rules are in `ok()`/`split()`; other meters split at the beat.
- **Spelling**: by key signature (sharps in sharp keys, flats in flat keys, C major: C# Eb F# Ab Bb). Change `spell()` for special cases such as a chromatic line in a sharp key.
- **Ties** are rebuilt across the whole part after generation: a tie survives only between equal pitches, and the continuation note loses its syllable.
- **Rehearsal marks, tempo, notes**: `section(name, tempo=..., note=...)` goes on the top staff. `<sound tempo>` makes MuseScore's MIDI follow the tempo changes. Dynamics and italic directions come from `sec["dyn"]` / `sec["text"]`.
- **Headless conversion**: run `QT_QPA_PLATFORM=offscreen mscore -o out.mscz in.musicxml`, then `mscore -o out.pdf in.mscz`. Always use absolute paths.
- **Short scores: `compact.py`** writes a built score the short way. Players read a short score more easily (the users asked for it).
  - Command: `compact.py OUT/x.musicxml ROADMAP.py OUT/short/x [--multirest]`.
  - `ROADMAP.py` lists the printed measures in order. Each entry gives the written-out measure (`m`), the other passes it stands for (`same`), the words of other passes to stack (`lyr`), and the marks: rehearsal mark, repeat barlines, 1st/2nd endings, segno, coda, D.C., D.S.
  - It refuses a merge whose passes differ in any part.
  - It adds a one-bar repeat sign (%) where an instrument bar equals the printed bar before it. Sung parts, the first bar of a section and tied bars never get one.
  - `--multirest` adds multi-measure rests (single-instrument sheets).
  - It checks that the short score's MIDI plays the same notes as the written-out build.
  - Worked roadmaps: `examples/code-monkey/roadmap_band.py` (repeats + endings, 125 → 93 measures) and `roadmap_written.py` (playing order, % and rests only).
  - **What can merge**: the band parts usually repeat exactly; a transcribed vocal rarely does (each verse is phrased differently). Shorten the band sheets with repeats, and keep the vocal and full score in playing order, unless the vocal is normalised on purpose.
- **Repeats and jumps** (what `compact.py` relies on):
  - MuseScore 4.7 imports these MusicXML elements correctly and plays them back: `<barline><repeat direction="forward|backward"/>` and `<ending number="1" type="start|stop|discontinue">`.
  - It imports D.C., To Coda and Coda directions as plain StaffText, even with `<sound dacapo="yes"/>`, `tocoda` or `coda`, so they don't play.
  - Fix in the `.mscx`: remove that StaffText and put a `<Jump>` (`<style>repeat_right</style><text>D.C. al Coda</text><jumpTo>start</jumpTo><playUntil>coda</playUntil><continueAt>codab</continueAt>`) or a `<Marker>` (`<label>coda</label>` for "To Coda", `<label>codab</label>` for the ⊕ Coda) directly inside `<Measure>`, before its first `<voice>`. Inside `<voice>` they are dropped.
  - To check: the MIDI exported from the repeat score has the same length and notes as the written-out build (`compact.py` does it).
  - MuseScore 4.7 imports `<measure-style><measure-repeat type="start">1</measure-repeat>` as a one-bar repeat and plays it. The `stop` goes on the first measure that is not a repeat; a part with a TAB staff needs one `measure-style` per staff (`number="1"`, `"2"`). A % under a tie breaks the tie in playback, so tied bars stay written.

## Viewing the result (the agent can't hear)
- `build.py ... --png` renders each page at 50 dpi to `OUT/png/page-NN.png`. Read 2–3 pages with the Read tool to check:
  - collisions
  - lyrics under the right notes
  - dynamics and text
  - the VP staff
  - the system breaks

  For a sharper look at a single page: `pdftoppm -r 110 -f 3 -l 3 -png OUT/x.pdf /tmp/p`.
- `look.py W roll STEM BARS --part OUT:VOICE` overlays any arranged voice on the recording's spectrogram.
- `qa.py OUT` checks the numbers. `render.py OUT` makes the files the human listens to, starting with `mix_with_original.wav` and `real_lead_over_backgrounds.wav`.

## Hand-editing after delivery
The user can edit the `.mscz` in MuseScore. Rebuilding from the arrangement file overwrites it, so tell them which one is the master. If they re-import the MusicXML by hand, the chord symbols will play again: Select all chord symbols → Properties → untick "Play".

## Part extraction / rehearsal
- MuseScore: File → Parts → generate all parts for per-singer PDFs.
- `render.py` writes `audio/part_<voice>.wav` per voice. A classic rehearsal mix (the voice loud, the others soft) can be made with ffmpeg `amix` from these files.
