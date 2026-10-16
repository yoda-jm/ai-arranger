# Evaluation: the Code Monkey transcription against the master tracks

The sheets in [`../sheets/`](../sheets/) are left exactly as the agent produced them. This folder measures them against two references:
- the song's **official unmixed tracks**, which are a ground truth;
- **fan transcriptions** (chord charts, tabs, the JoCo wiki lyrics).

It then explains each error by its cause. The method fixes it led to are in the skill: `arranger-core/references/transcription.md` §8.

## Summary
| Part | Score | Against |
|---|---|---|
| Lead vocal | **78.8%** of 16ths exact, no octave errors | `master-tracks/Lead Vox.mp3` |
| Bass | **89.5%** right pitch class (pre-chorus 99%, verses 76%) | `Bass.mp3` |
| Backing vocals (octave double) | **84.5%** exact | `Octave Vox.mp3` |
| Drums | kick **F 88%**, snare **F 90%**, cymbals **F 76%** (precision 97-99%) | `Drums.mp3` |
| Lyrics | **49 of 51** lines | `lyrics_reference.txt` (JoCo wiki) |
| Tempo, meter, form | 160 bpm, 4/4, 125 bars: **right** | the tracks' readme: "160 BPM" |
| Instruments | **wrong**: 5 electric guitars written as 1 electric + 1 acoustic; a harmony vocal missing | who-plays-when map below |

## Files
| File | What |
|---|---|
| `master-tracks/` | the official unmixed tracks of "Code Monkey" (11 MP3s + the original `readme.txt`). Source: the *JoCo Looks Back* source tracks, uploaded to the Internet Archive (item `JonathanCoultonJoCoLooksBackSourceTracks`) by Jonathan Coulton's team, CC BY-NC 4.0 |
| `lyrics_reference.txt` | the lyrics as the JoCo wiki had them in 2011 (CC BY-NC 3.0) |
| `groundtruth.txt` | output of `arranger-core/scripts/groundtruth.py`: alignment, who plays when, scores per part |
| `extra_checks.py`, `extra_checks.txt` | the checks the general tool doesn't cover: the lyrics diff, the guitar riff, A against A minor, the harmony vocal |
| `report/index.html` | the same evaluation as an illustrated page, in red-pen correction style: sheet previews (they open the PDFs), the record and the render side by side, a who-plays-when map. Open it in a browser |

## Reproduce
After a fresh clone, first make the analysis and the written-out build the scripts read (`../work/`, `../out/`, not in git; see `../GENERATED.md`): run `examples/code-monkey/regenerate.sh`, which ends with these two commands.
```bash
PY=.venv/bin/python; A=examples/code-monkey; E=$A/evaluation
$PY arranger-core/scripts/groundtruth.py $A/out $A/work $E/master-tracks \
    --map V="Lead Vox" BV="Octave Vox" BASS=Bass:bass DR=Drums:drums --activity > $E/groundtruth.txt
$PY $E/extra_checks.py > $E/extra_checks.txt
```
The tracks start 1.03 s into the mix; both scripts find the offset by cross-correlation. The scores compare each part of the written-out score (`../out/events.json`) with its own isolated track, 16th by 16th:
- pitch from torchcrepe (pyin for the bass);
- drum hits classified by the spectrum of each hit.

## 1. Against the master tracks

### Who plays when
One character per bar, bars 1-124. `master` rows are the official tracks; `score` rows are the transcription's staves (EGTR = electric guitar, GTR = acoustic guitar).
```
                            |    ·    1    ·    2    ·    3    ·    4    ·    5    ·    6    ·    7    ·    8    ·    9    ·    0    ·    1    ·    2    |
master Bass                 |                #################################=#####=#############################=###=#######=########################==.|
master Double Vox           |        ###.#####################  #####        ###=#####################  ###=             ###=#####################  ##### |
master Drums                |       ##################################################################################################################    |
master Electric Guitar 1    |################                    ###################=                   .########################                         |
master Electric Guitar 2    |       .#=###=#=#########################=###=###=###=#=#############################=###=###=###=#=######################## |
master Electric Guitar 3    |                                       .################                           .################                         |
master Electric Guitar 4    |               =########################=              =############################=              =#########################|
master Electric Guitar 5    |               =#########################              =#############################              =#########################|
master Harmony Vox          |                       ##########  #####                       ##########  ###=                            ##########  ##### |
master Lead Vox             |#######=###.#####################  ########=###=###=#####################  ###=     ###=###=###=#####################  ##### |
master Octave Vox           |                       ##########  #####                       ##########  ###=.                           ##########  ##### |
score  V                    |#################################  ######################################  ####     #################################  ##### |
score  BV                   |                       ##########  #####                       ##########  ###                             ##########  ##### |
score  EGTR                 |#########################################################################################################################    |
score  GTR                  |############################################################################################################################ |
score  BASS                 |               ############################################################################################################# |
score  DR                   |       ##################################################################################################################    |
```
- **Right**:
  - the bass enters at the end of bar 16;
  - the drums enter at bar 8 and stop at 121;
  - the octave double is in exactly the right bars;
  - the palm-muted guitar (Electric Guitar 1) plays E on the D string, 2nd fret, as tabbed.
- **Wrong**:
  - Electric Guitar 1 plays only in the verses, but the transcription's electric guitar plays everywhere.
  - Guitars 4 and 5 (a doubled pair for pre-choruses and choruses) and guitar 3 (verses 2-3) are not written.
  - The harmony vocal is not written.
  - The "acoustic guitar" (GTR) doesn't exist.

### Lead vocal: 78.8% exact
The pitch tracked on the separated stem was right 89.8% of the time; the written part scores 78.8%. The gap is notation:
- **Slides** are written as their target ("cof-fee", "front desk" slide F → F#).
- **Blue notes** are bent into the key. The singer sings C, D and G natural where E major has C#, D# and G#: bars 42, 20, 87.
- **Notes are held through breaths**: 176 16ths where the score holds a note and the singer is silent.

The worst bars are 42, 70, 87, 2 and 20.

### Bass: 89.5%
- **Pre-chorus**: 99%.
- **Interludes**: 99%.
- **Chorus**: 90%. E "pushes" were written where the record jumps up an octave to B instead.
- **Verses**: 76%. The walk E . B . A | A . C# C B is close, but the chromatic C sits in the wrong bars, and an E pickup is written that isn't played.

### Drums: precision 97-99%, recall 63-83%
- **Correct**:
  - kick on 1 and 3, snare on 2 and 4, hi-hat on every beat in the verses;
  - kick 1, 1&, 3 in the choruses;
  - 8th cymbals in the pre-choruses and choruses;
  - stops and fills.
- **Left out**: the ghost kicks on the "e" of beats 2 and 4, pickup and fill notes, and part of the cymbal detail.

### Chords (`extra_checks.txt` §2-4)
- **Right**: the pre-chorus, A B G#/B# C#m-B A A B (guitar 4: A, B, G#, C#m-B, A, A, B).
- **The verse riff**, bars 43-44 (guitar 2, per 8th):
```
count            1   &   2   &   3   &   4   &  |  1   &   2   &   3   &   4   &
guitar (record)  E   .   .   B   B   .   .   A  |  A   .   .   C#m C#m B   B   .
chords (score)   E                              |  A               B
bass (record)    E   E   F   B   B   B   B   A  |  A   A   .   C#  C#  C   B   B
bass (score)     E   E   E   B   B   B   B   A  |  A   A   A   C#  C#  C#  B   B
```
  The bass line the agent wrote follows the riff; its chord symbols don't.
- **Bar 26**: the guitars play E over a D# bass (Emaj7/D#); the score says B/D#.
- **Bars 75 and 79**: C is stronger than C# in guitars 2, 4 and 5, so these are A minor (as the fan charts write "D A Am E"). The score says A.

### Harmony vocal (`extra_checks.txt` §5)
In every chorus a harmony sings mostly a 5th above the lead (42% of the time), otherwise a 3rd or a 4th. The score has no harmony part.

## 2. Against fan transcriptions
Sources:
- four chord charts, two guitar tabs and a bass tab on chords-and-tabs.net (one chart came from Coulton's forum);
- the JoCo wiki lyrics.

The fans work by ear, so they hear what measurements miss, and the reverse.
| Point | Fans | Score | Master tracks |
|---|---|---|---|
| Tempo, meter | ~160, common time | 160.01 bpm, 4/4 | both right |
| Verse harmony | E B/E A/E on every line | E, A/E E | fans right |
| "Code Monkey like..." (bar 26) | Emaj7 | B/D# | fans right |
| End of chorus 2 | D A Am E | D A A A E | fans right |
| Instruments | "two guitars, both overdriven" | one electric, one acoustic | five electric guitars: fans closer |
| Bass | "Jonathan doesn't actually use a bass" (the tab invents one) | a bass from bar 16 | score right |
| "login page" | G# (3 charts), E (1 chart) | G#/B# | score and most charts right |
| "Code Monkey like you..." (chorus 2) | "a lot" | "lots" | fans right: two sung notes |
| Verse 3 | "See your soft pretty face" | "To see your soft..." | fans right |
| Bar-by-bar form, melody, drums | not written | complete, 125 bars | score only |

## 3. Why it went wrong: four families
**1. The tools hear a mix.**
- Four stems hold everything, so five overdriven guitars land in one stem. The agent counted guitars from mixed spectra and read the broadband attacks of distorted 8ths as an acoustic guitar strumming.
- A palm-muted E rings through every verse bar and hides chord stabs shorter than half a bar.
- Power chords have no third, so A against A minor rests on a faint note, and distortion adds false partials.
- Distortion can fake a bass: an overdriven fifth makes a difference tone an octave below its root. Here a real bass track exists.

**2. The method stopped too early or decided too coarsely.**
- Chords were labelled per half bar from the loudest pitches, while the bass line in the same score had the right riff.
- The search for backing voices stopped at the octave double.
- Lyric conflicts were settled by trusting one source instead of counting the sung notes.
- Nothing was cross-checked before delivery. Four fan charts would have flagged the verse harmony, both A minors and both lyric errors.

**3. Notation choices were made silently.**
- Blue notes were bent into the key and slides written as their target.
- Notes were held through breaths.
- Ghost notes and fills were left out.

Each choice is defensible for a sheet a musician reads; together they cost about 10 points of pitch agreement and 20-35 points of drum recall. The error is that the sheets don't say so.

**4. Checking needs the same care.** The first drum check used plain frequency bands on the master track and counted the snare's low end as kicks. It reported 58% kick recall instead of 79%. Even with master tracks, measure the yardstick.

| Error | Family | Now in the skill |
|---|---|---|
| A non-existent acoustic guitar; guitars 3-5 missing; the verse guitar carried into choruses | 1 | confirm the line-up with the person; count instruments by stereo position and the 6-stem model |
| Verse riff written E, A E | 1, 2 | label chords at the bass's attacks, per 8th; read past a pedal note |
| Emaj7/D# written B/D# | 2 | name the upper chord from the guitar's notes |
| Two A minors written A | 1 | flag major/minor calls on power chords; cross-check published charts |
| Harmony vocal missed | 2 | after the first backing voice, subtract it and search for the next |
| "lots", "To see" | 2 | when sources disagree, the number of sung notes decides |
| Blue notes, slides, held breaths, dropped ghost notes | 3 | keep chromatic notes that recur; end notes where the voice stops; list simplifications in the README |
| Kick recall first measured at 58% | 4 | `groundtruth.py` classifies drum hits by spectrum |
| Bars invented by the beat tracker | 1 | `barmap.py --grid` for records made on a click |

## 4. Time and cost
Claude Opus 5.5 in Claude Code, on a Linux machine with a 6 GB GPU (GTX 1660 SUPER). Prices are Anthropic's list prices per million tokens: input $4, 1-hour cache write $8, cache read $0.20, output $20. Token counts come from the session transcript.
| Phase | Wall-clock | Requests | Cost |
|---|---|---|---|
| Choose the song, check the licence, fetch it | ~10 min | 32 | $2.55 |
| Transcription, sheets, short sheets | ~58 min | 107 | $16.45 |
| This evaluation (tracks, fan charts, scores, this report) | ~40 min | 63 | $12.54 |

Cache reads are about 58% of the cost, because each request re-read a long session (about 450k tokens). A fresh session reads far less.

## Sources and licences
- "Code Monkey", words and music by Jonathan Coulton, <https://www.jonathancoulton.com>, CC BY-NC 3.0.
- The master tracks are CC BY-NC 4.0, from the Internet Archive item `JonathanCoultonJoCoLooksBackSourceTracks` (*JoCo Looks Back* source tracks, 2008). Their `readme.txt` is kept as published.
- Lyrics reference: the JoCo wiki page "Code Monkey/Lyrics", last modified 12 August 2011, CC BY-NC 3.0. Read through the Internet Archive; the wiki now requires a login.
- Fan transcriptions, quoted only as single chord names: <https://www.chords-and-tabs.net/song/name/jonathan-coulton-code-monkey-3> and the other versions on that site (chords ver. 1-4, tabs, bass).
- Pricing: <https://platform.claude.com/docs/en/about-claude/pricing>.

Everything in this folder is shared under CC BY-NC, for non-commercial use, crediting Jonathan Coulton.
