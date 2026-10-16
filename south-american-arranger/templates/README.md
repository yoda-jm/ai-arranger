# {Title}: {style(s)} version for the band

{One paragraph: the idea of the transplant (which style where, why, the key and tempo map), and the length.}
Arranged from the recording "{file}". The recording is in {key}; this arrangement is in {key} (rec_shift {n}).

## Listen first
| File | What |
|---|---|
| `audio/score_full.wav` | the arrangement at its own tempos (GM mock-up: leads on flute/clarinet, coros on "oohs") |
| `audio/score_no_vocals.wav` | the band only: sing along |
| `audio/real_lead_over_backgrounds.wav` | the recorded singer over the new band, lined up bar by bar (in the record's key): does the new harmony work under the real voice? |
| `audio/score_part_*.wav` | one file per part |

## Files
| File | What |
|---|---|
| `{name}.mscz` | MuseScore 4 score (the master: rebuilding from `arrangement.py` overwrites it) |
| `{name}.pdf` | engraved score ({pages} pages); MuseScore → File → Parts makes one PDF per player |
| `{name}.musicxml` / `.mid` | exchange formats |
| `lead_sheet.md` | chords + words per measure, per section |
| `grooves.md` | every pattern each player plays, on a count grid, with the stroke legend |

## Section plan
| Measures | Rec. bars | Section | Style, tempo | Key / harmony | Lead | What happens |
|---|---|---|---|---|---|---|

## Who plays and sings what
| Player | Instruments by section | Sings |
|---|---|---|

## Automatic checks (qa.py)
- ranges / tessitura: …
- lead vs chord symbols: …% on chord tones; clashes: …
- hang notes off its scale: … · autoharp chords without a bar: … (approximations: …)
- player overlaps: … · fast instrument switches: …
- melody vs the recorded singer: …% same pitch class (through the warp)

## To check by ear / in rehearsal
- lyrics: words Whisper may have misheard (…)
- transcription doubts: measures …
- tempos: …; the transitions at measures …
- things to try: …

## Regenerate
```
C=<skills>/arranger-core/scripts; B=<skills>/south-american-arranger/scripts
$ACAP_PY $C/build.py arrangement.py out --work work --lib $B --png && $ACAP_PY $C/qa.py out \
  && $ACAP_PY $C/render.py out && $ACAP_PY $B/sheets.py out
```
