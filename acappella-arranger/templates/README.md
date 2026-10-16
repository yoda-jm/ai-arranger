# {Title}: a cappella arrangement ({voicing, e.g. Solo + SSATBarB + VP})

{N} sung parts{ + vocal percussion}, {bars} bars, keys {…}. Arranged from the recording "{file}".

## Files
| File | What |
|---|---|
| `{name}.mscz` | MuseScore 4 score. Voices play back as piano, the VP staff as a drum kit; chord symbols don't play |
| `{name}.pdf` | engraved score ({pages} pages) |
| `{name}.musicxml` / `.mid` | exchange formats |
| `audio/mix_with_original.wav` | **listen first**: the arrangement (piano + drums) over the original, time-aligned |
| `audio/real_lead_over_backgrounds.wav` | the real singer over your backgrounds: does it work under the solo? |
| `audio/acappella_full.wav`, `audio/score_tempo.wav` | the arrangement alone (aligned / at score tempo) |
| `audio/part_*.wav` | one file per part (rehearsal) |

## Section plan
| Bars | Section | Key | Texture |
|---|---|---|---|
| 1–8 | Verse 1 | | |

## How to sing the syllables
- pads: "Oo" (dark), "Ah" (open, builds)
- keys: "jen" / "jah" (short, staccato) · brass: "Bah", "dah", "dat" · flute: "doo", "dl"
- bass: "doom" on long notes, "dm" on short ones

## Vocal percussion key
| Staff position | Sound | Syllable |
|---|---|---|
| bottom space | kick | **B** |
| 3rd space | snare | **Pf** |
| 3rd space, × | rim | **k** |
| above, × | closed hat | **t** |
| above, × (last bar) | crash | **Ksh** |

## Automatic checks (qa.py)
- ranges: … · sung bass = recorded bass on …% of 8ths · harmony similarity median … · clashes: …

## Things to check by ear
- transcription doubts (bars …), words not in the lyrics file, high tessitura, optional ornaments

## Regenerate
```
C=<skills>/arranger-core/scripts
$ACAP_PY $C/build.py arrangement.py OUT --work W --png && $ACAP_PY $C/render.py OUT && $ACAP_PY $C/qa.py OUT
```
