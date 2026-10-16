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
- **Repeats and jumps** (for a short score with repeats, written from the full written-out build by a song-specific script; a generic tool is planned):
  - MuseScore 4.7 imports these MusicXML elements correctly and plays them back: `<barline><repeat direction="forward|backward"/>` and `<ending number="1" type="start|stop|discontinue">`.
  - It imports D.C., To Coda and Coda directions as plain StaffText, even with `<sound dacapo="yes"/>`, `tocoda` or `coda`, so they don't play.
  - Fix in the `.mscx`: remove that StaffText and put a `<Jump>` (`<style>repeat_right</style><text>D.C. al Coda</text><jumpTo>start</jumpTo><playUntil>coda</playUntil><continueAt>codab</continueAt>`) or a `<Marker>` (`<label>coda</label>` for "To Coda", `<label>codab</label>` for the ⊕ Coda) directly inside `<Measure>`, before its first `<voice>`. Inside `<voice>` they are dropped.
  - To check: the MIDI exported from the repeat score has the same length and notes as the written-out build.

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
