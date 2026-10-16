---
name: south-american-arranger
description: Arrange a pop/rock song from a recording (MP3/WAV) for the user's 5-piece band in a South American style. It does either a full genre transplant far from the original (the band's DNA), or the original's vibe (form, groove, arc, language) with South American touches. Styles include the mainstream bossa, samba, Cuban son/salsa and tango, plus landó, festejo, cumbia, chicha, baião, joropo, chacarera, zamba, huayno, candombe and vals criollo. The band is percussion (cajón, güiro, hang, shaker, snare), small drums (djembé, bongos, cuíca, shakers), autoharp (optional), guitar/ukulele and bass, with 2 mezzos and 3 baritones who all sing. The skill re-times the tune into the new meter, reharmonises within the hang's scale and the autoharp's chord bars, and writes vocals, strums, bass and percussion. It delivers a MuseScore score (guitar and bass with tablature), PDF, MIDI, audio mock-ups, groove cards and a lead sheet. Use it when the user wants a song covered or re-genred for the band, or asks for a Latin / South American version of a song.
argument-hint: "<song.mp3|wav> [style(s)] [lyrics.txt]"
---

# Pop song → South American band arrangement

The band's DNA: **keep the tune and the words, change everything else**. a metal anthem as a waltz, a folk song as reggae, a rock classic as samba. This skill sits on [arranger-core](../arranger-core/SKILL.md), which handles analysis, transcription, engine, build, render and QA, and adds three things:
- the band layer `scripts/band.py`: parts, kits, strums, bass, percussion, hang, constraints;
- the style library [references/styles.md](references/styles.md);
- the transplant method [references/transplant.md](references/transplant.md).

The band, its ranges and constraints: [references/band.md](references/band.md).

```bash
C=${CLAUDE_SKILL_DIR}/../arranger-core/scripts     # analysis, build, render, qa
B=${CLAUDE_SKILL_DIR}/scripts                       # band.py, sheets.py
PY=${ACAP_PY:-$HOME/.cache/acappella/venv/bin/python}
A=$PWD/arrangements/<song>
```

## 1. Brief (ask only what the request leaves open; one round of questions)
- **How far** ([transplant.md §0](references/transplant.md#0-how-far-transplant-or-touches)):
  - **transplant** (the DNA): a new meter and genre;
  - **touches**: the original's form, 4/4, tempo and drum arc, played by the band with South American grooves and colours.

  Ask when the user hasn't said. If they send the original recording, or react to a transplant with "I prefer the original vibe", do touches.
- **Style(s)**:
  - Propose 3-4 that fit the song's energy and form (transplant.md §2), each with a one-line why and a groove preview.
  - **Pick styles the audience knows.** For an audience in France or Europe, start with bossa, samba, Cuban son / salsa / cha-cha-chá ([styles.md 4.23](references/styles.md)), rumba flamenca and tango. Offer landó, festejo, chicha, huayno or chacarera only when asked: the user found them too little known.
  - A style with no card in styles.md: research it with [style-research.md](../arranger-core/references/style-research.md) and write the card before any note.
  - Two styles are fine when the song has two energies (landó verses → festejo choruses).
  - The user may let you pick after the analysis.
- **Language**: as recorded, or the original. Ask for a lyrics file: Whisper mishears names and English words in other languages. Without one, get a second opinion with `$PY $C/words.py $A/work <bar ranges>` (Whisper on the lead stem, section by section), and list the doubtful lines.
- **Leads**: one singer, a duet (trade verses, share choruses), or rotating. Coros come from the other singers.
- Defaults you don't need to ask: the band in band.md, full deliverables (§6), length close to the record.

## 2. Analyse and transcribe (arranger-core §1-2)
`$PY $C/analyze.py song.mp3 $A/work [--lyrics lyrics.txt]` runs in the background. Read `report.md` fully and write the form table. Note:
- the loop(s), the tempo, the key;
- the dramatic moments (screams, stops, pickups);
- the hook.

Then transcribe `$A/song.py` **in the arrangement's key** (§3 decides it), keeping the record's 4/4 rhythm (the warp re-times it later):
- one note per syllable, on the 8th grid, with the contour of the f0 (`look.py f0`, `look.py roll lead --f0`);
- check it with a lead-only build: aim for at least 70% same pitch class against the singer.

## 3. Plan the transplant (fill the table in [templates/arrangement.py](templates/arrangement.py) before any note)
Follow [transplant.md](references/transplant.md) and the style cards in [styles.md](references/styles.md). For **touches**, follow the recipe in §0 instead of the meter and form surgery: keep the record's section lengths and drum arc.
For a **transplant**:
- **Style per section, meter and warp, tempo per section**. Budget the total length (±15% of the record); cut instrumentals.
- **Key**:
  1. the singers' ranges;
  2. the hang (D Kurd = F major / D minor) and the autoharp bars;
  3. the style's mode.

  Set `rec_shift` = new key − record key.
- **Harmony**: the record's loop, recoloured. Use the relative-minor reading, the style's cadences and turnarounds, modal colour; keep every melody note.
- **Form**: a new intro in the style, transitions on the song's dramatic moments (remate + shout), instrumentals turned into contrapunteo or call-and-response, a breakdown before the last chorus, an ending in the style.
- **Roles**: who leads each section, coros, which instrument each player is on per section (switch only at breaks), and the energy arc.

## 4. Write `$A/arrangement.py` with the band layer
```python
from band import *                      # arranger-core engine + the band writers
import song as S
setup(title="...", composer="...", arranger="...", meter=(12, 8), rec_shift=-1, name="song_style")
s = section("Verse 1", "Dm", 4, VERSE_CH, S.V1, S.V1_LYR, warp="swing", tempo=76, style="landó")
lead(s, "W1", dyn="mp")
arp(s, "GTR", "1.3 4.3 2.3 4.3", text="landó arpeggio")
bassline(s, "1-- --- 5-- ---")                     # landó-canción bass (styles.md 1.6)
perc(s, "P1", cajon="B.T .BB .TB .TB", dyn="p")      # landó cajón base A (styles.md 1.3)
```
API and pattern grammar: [band.md](references/band.md#writing-parts-from-band-import-). Patterns come from styles.md: copy the grid string without its ` # ` comment, then adapt it to the song. The published worked example is the Creative Commons song in `examples/code-monkey/` at the repository root (band versions planned). Your own earlier arrangements in `arrangements/*/arrangement*.py` are examples too; they stay local. Earlier arrangements used, by distance:
- **a transplant**: the plan table, landó → festejo pivots, hook blocks, a hang + djembé verse, contrapunteo and an ending;
- **touches**: the record's groove on the cajón, a cumbia layer, a güiro in the drumless choruses, chicha leads, and chorus variants written once each in `song.py`;
- **touches in a mainstream style** (Cuban son / salsa, no autoharp): shell + cowbell drops, the djembé as a conga, a tumbao bass, a 3+3+2 strum with mutes (the "figuetta"), a chorus over percussion only, solos in turn, a montuno outro and a cha-cha-chá ending.

## 5. Build → check → listen → iterate (2-4 rounds)
```bash
$PY $C/build.py $A/arrangement.py $A/out --work $A/work --lib $B --png --scaling 4.2 --staff-distance 40 \
  && $PY $C/qa.py $A/out > $A/out/qa.txt && $PY $C/render.py $A/out && $PY $B/sheets.py $A/out
```
- **QA targets**:
  - every part in range, singers' tessitura below about 15% in the top 3 semitones;
  - lead vs chord symbols: no unintended long clash a semitone above a chord tone;
  - the hang 0 notes off its scale; the autoharp 0 chords without a bar;
  - no player on two parts at once; no percussion switch shorter than a beat;
  - the activity table builds to the last chorus;
  - lead vs the recorded singer stays at transcription level (it is computed through the warp and `rec_shift`).

  Bass and chroma vs the recording drop on purpose after a reharmonisation.
- `--scaling 4.2 --staff-distance 40` fits 11 staves at 2 systems of 4 bars per A4 page (about 14 pages for a 4-5 minute song).
- **Look at 2-3 PNG pages** (Read): slashes, chord symbols on the guitar/autoharp/bass staves, the percussion lines, lyrics under the warped tune, rehearsal marks, tempos.
- **Renders**: `score_full.wav` (the arrangement at its tempos), `score_no_vocals.wav` (sing-along), `real_lead_over_backgrounds.wav` (the recorded singer over the new band, aligned through the warp, in the record's key: does the new harmony work under the real voice?).

## 6. Deliver
- In `$A/out`: `.mscz` (master), `.pdf`, `.musicxml`, `.mid`, `audio/`, `lead_sheet.md`, `grooves.md`, and `README.md` from [templates/README.md](templates/README.md) with:
  - the section plan;
  - who sings and plays what;
  - the key and tempo map;
  - the QA numbers;
  - the lyric doubts;
  - things to try in rehearsal.
- In the reply, point to `audio/score_full.wav` and `grooves.md` first. Say plainly what is transcription and what is arrangement; list uncertain bars and words. Never claim it "sounds good": report the checks.
- Offer to publish `lead_sheet.md` + `grooves.md` as a page the band can open on their phones. If the band uses [TroubaStack](https://github.com/yoda-jm/troubastack), offer instead to send them there as charts: the lead sheet as chords over lyrics, the grooves as tab blocks. They can then be annotated, put in a setlist and read on stage. See [troubastack.md](../arranger-core/references/troubastack.md).

## Pitfalls
- `from band import *` copies `BAR` at import: use `E.BAR` (`import engine as E`) in arrangement code.
- The autoharp plays its *bar*, not the symbol: Dm7 sounds Dm, F/A sounds F, and Bm has no bar at all.
- The hang has no C# / F# / B: over A7 or D7 it plays A, E, G or rests. Don't write hang melodies outside D Kurd.
- One player, one instrument: the percussionist can't play cajón and hang together. Put instrument changes at section breaks with at least a beat of rest.
- A slower style for verses makes them longer. Check the total length before writing the whole score.
- Spanish lyrics: one note per syllable after sinalefa (vowels joined across words: "za‿a"). Count syllables, not letters.
- **A rhythm told in words is counted against the bar before it is written.** "Down-up-mute, down-up-mute, down (ring)" is 7 strokes plus a ring: 8 cells, so one bar of 8ths (3+3+2), not 16ths. Writing it in 16ths made it sound "very strange". Show the reading under a count line (`1 & 2 & 3 & 4 &`) and ask the player to confirm it by ear.
- **The mock-up is what the band judges.** A part that carries the style must be audible in `score_full.wav`, like the guitar's strum in a Cuban chorus. Compare the RMS of `score_part_*.wav` over that section, and keep the part within a few dB of the lead. A soft GM nylon guitar under five voices came across as "we don't hear the guitar".
