# AI Arranger: transcribe, re-arrange and arrange songs with Claude Code

A set of [Claude Code](https://claude.com/claude-code) skills plus a Python toolkit that let an AI agent work like an arranger's assistant:
- **transcribe** ("repiquer") a song, a section or a single part from a recording or a video: a bass line, a riff, a chord grid, lyrics, the form;
- **check** a musician's draft against the recording;
- **re-arrange** a song for a band in another style;
- **arrange** it for voices.

The agent can't hear, so the toolkit gives it instruments to look with:
- stem separation and a bar map;
- piano rolls, note-level attack tests and chord profiles;
- QA against the recording;
- renders for the humans to listen to.

The deliverables are what musicians use: MuseScore scores (with TAB staves), PDFs, MIDI, audio mock-ups, and text tabs/charts.

The rule behind everything: **the recording is the truth**. Drafts, the original record and the agent's own earlier answers are hypotheses to check against it.

## What it can do (real use cases)

| Use case | Input | Output |
|---|---|---|
| **A bossa cover band takes on a new bassist.** Until now the guitarist played the bass role on his low strings; write the bass part from a live concert video. | a 1-2 h concert video (image + audio) + a timestamp | bass patterns per section (tab), checked against every pass of each section, with the passes where the guitarist slipped told apart; the transitions; the song structure on page 2 |
| **A bassist films a riff for another bassist.** | a phone video at a practice tempo | a tab with the string/fret positions read from the image; octaves and repeated notes checked on the audio |
| **Check or continue a musician's draft tab.** | the draft + the recording | note-by-note corrections with timestamps (wrong barlines, octaves, ghost notes), with their own layout kept |
| **Pop song → bossa (or samba, son, tango...) for a 5-piece band.** | the record (+ lyrics) | grid, lyrics and form, re-timed into the new groove; score with vocals, guitar/bass TAB and percussion; audio mock-up; lead sheet |
| **Cartoon theme → a cappella**: SATB, 8 voices, a barbershop quartet, or a Pentatonix- or VoicePlay-style lineup (upper voices trading the lead, a very low bass, beatbox). | the theme's recording | a voiced score with beatbox taken from the record's drums, rehearsal audio aligned to the original |
| **Your own demo → a finished song**: align the verses' prosody, add a bridge, a key change, an outro. | a demo track | a lyrics sheet with a prosody table, and a short score using repeats and D.C. al Coda |

## Skills

| Skill | Role |
|---|---|
| [`arranger-core`](arranger-core/SKILL.md) | The base everything runs on. **Analysis** (Demucs stems, karaoke lead/backing split, beat_this bar map, key, chords, drum grid, Whisper words → `report.md`). **Transcription**: a whole song into `song.py`, or one part note by note with `partscope.py` (see [transcription.md](arranger-core/references/transcription.md)). The **engine**, **build** (MusicXML → MuseScore → PDF/MIDI/PNG), **render** (fluidsynth) and **QA**. |
| [`acappella-arranger`](acappella-arranger/SKILL.md) | 4-8 part vocal arrangements, from SATB up to Solo + SSATBarB + vocal percussion. Pads, block harmony, instrument imitations, beatbox. [Style cards](acappella-arranger/references/styles.md) for barbershop, Pentatonix and VoicePlay. |
| [`south-american-arranger`](south-american-arranger/SKILL.md) | Re-genres a song for a 5-piece band (percussion, small drums, guitar/ukulele, bass, 5 singers) in bossa, samba, son, tango and a dozen other South American styles, as a full transplant or as touches. The band profile is a file you can adapt to your own lineup. |

## Works with TroubaStack

[TroubaStack](https://github.com/yoda-jm/troubastack) is a self-hosted platform where a band shares its sheet music and lyrics, annotates them together, builds setlists and reads them on stage. The tabs, bass charts, lead sheets and groove cards made here can be sent to a band's TroubaStack server as charts in its text dialect, through its API: preview first, then a save that never overwrites a musician's newer edit. See [arranger-core/references/troubastack.md](arranger-core/references/troubastack.md).

## How a job runs

```
recording / video ──► analyze.py ──► report.md (form, tempo, keys, chords, levels, words)
                                         │
       ┌─────────────────────────────────┼──────────────────────────────┐
       ▼                                 ▼                              ▼
 one part → tab/chart              song.py (tune, lyrics,         style skill writes
 partscope: lowest, stack,         chords), verified with         arrangement.py
 onsets, repluck, glide,           look.py + qa.py                       │
 profile → patterns + structure                                         ▼
                                                     build.py → score/PDF/MIDI → qa.py → render.py (audio)
```

Lessons that shaped the tools are written into the skills (see each SKILL.md's pitfalls and [transcription.md §7](arranger-core/references/transcription.md)). For example:
- Phone microphones lose a bass's fundamental, so the 2nd harmonic is the loudest partial. Octaves must all be read the same way.
- A strummed A3 is not a bass A2. Decide whether a note is played from plain per-pitch onsets, never from octave-summed salience.
- Two plucks a 16th apart at a slow tempo are 0.23 s apart. Long analysis windows merge them, so the re-pluck test uses a short FFT, plus a held note as a control.
- Find beat 1 from where the chord roots land, not from where a repeating figure starts.
- A live cover can change the record's chords (a Dm where the record has E7). Show the evidence and let the musician decide.
- When the musician doubts a note, re-test it with a finer tool.

New styles and lineups are researched with a written method ([style-research.md](arranger-core/references/style-research.md)):
- the lineup first;
- rulebooks before opinions;
- pages actually opened rather than search summaries;
- core features told apart from studio tricks;
- every claim measured on reference recordings before it becomes a rule.

## Install

Python 3.10–3.13 with the packages from `arranger-core/scripts/setup.sh`, plus ffmpeg, MuseScore 4, fluidsynth with a GM soundfont, and poppler. Details per OS: [arranger-core/references/install.md](arranger-core/references/install.md). Check with `python arranger-core/scripts/check_env.py`. A GPU makes the analysis about 4× faster (6-8 min per song instead of about 30).

Install the skills by linking the three folders into `.claude/skills/` of your project (or `~/.claude/skills/`), then ask in plain words, for example:
- "Transcribe the bass part the guitarist plays in this concert at 14:08, and make a tab with patterns and the structure."
- "Here is a phone video of a riff: write the tab with the positions he uses."
- "Make a bossa version of this song for the band."
- "Arrange this theme for 8 voices with beatbox."

## Examples and copyright

The recordings, scores and lyrics of other people's songs are not included in this repository. Your own per-song work goes in `arrangements/`, which git ignores.

The one exception is the worked example, [`examples/code-monkey/`](examples/code-monkey/README.md). It is "Code Monkey" by Jonathan Coulton ([jonathancoulton.com](https://www.jonathancoulton.com)), which its author released under [CC BY-NC 3.0](https://creativecommons.org/licenses/by-nc/3.0/). Everything derived from it in this repository (transcriptions, arrangements, scores) is shared under the same licence, for non-commercial use only. It will show every kind of job on one source:
- the transcription and a lead sheet;
- a single part checked against the recording;
- an a cappella version;
- band versions in other styles.

## Status

Working and used by a real band; the APIs of the scripts may still change. Roadmap:
- the worked example on "Code Monkey" (the recording is in; the versions are to do);
- a generic band profile, so the band skill isn't tied to one lineup;
- a video tool that reads fret positions from close-up footage;
- more styles.

## Layout

```
arranger-core/            base skill: scripts/, references/, templates/
acappella-arranger/       vocal arranging skill
south-american-arranger/  band re-genre skill
examples/code-monkey/     the worked example: a CC BY-NC recording and everything made from it
arrangements/<song>/      your per-song work (audio, analysis, song.py, arrangement.py, outputs); ignored by git
.claude/skills/           links to the three skills, so Claude Code finds them when opened in this folder
```
