# Worked example: "Code Monkey" (Jonathan Coulton)

The repository's proof of concept. Every kind of job the skills do will be shown on this one recording:
- the analysis and the transcription;
- a lead sheet;
- a single part transcribed for a musician;
- an a cappella version;
- band versions in other styles.

## The recording
| | |
|---|---|
| Song | "Code Monkey", words and music by Jonathan Coulton |
| Recording | Jonathan Coulton, first released on 14 April 2006 as Thing a Week #29; this file is the 2008 compilation release (*JoCo Looks Back*, track 1) |
| File | `code-monkey.mp3`: 3:10, 320 kbps, 44.1 kHz stereo. SHA-256 `f159c00e11865bea255f4004f55edfbe4a16d8372684e5d47ab6a6de99b5d885` |
| Licence | [Creative Commons Attribution-NonCommercial 3.0 Unported](https://creativecommons.org/licenses/by-nc/3.0/) |
| Author's site | <https://www.jonathancoulton.com> (buy the song there: it's a dollar) |

**Why the licence holds.**
- The author's FAQ says: "All my music is released under an Attribution-NonCommercial Creative Commons license that allows any kind of non-commercial re-use provided you: 1) credit me and link to this site, and 2) don't use it to make money". The exception is songs containing material he doesn't own (covers, mashups, remixes). "Code Monkey" is his own song.
- The file's ID3 comment carries the same licence: "Creative Commons Attribution-Noncommercial 3.0 Unported".

**Where the file comes from.** The Thing a Week podcast's original MP3 links now return 404. This copy of the official 2008 release comes from the Internet Archive item `jonathan-coulton-code-monkey`, which a third party uploaded in 2024. The licence comes from the author, not the uploader. The embedded cover picture was removed, because its licence isn't stated; the audio and tags are unchanged.

**What the licence asks of this repository.**
- Credit Jonathan Coulton and link to his site wherever the song or a derived work appears.
- No commercial use, of the recording or of anything derived from it (stems, transcriptions, arrangements, renders).
- Publish everything derived from this song under the same CC BY-NC 3.0 licence. BY-NC doesn't strictly require that, but it keeps the terms clear.

**Why this song.**
- It is his best-known song that he owns outright. "Still Alive" and "Want You Gone" belong to Valve, and "Baby Got Back" is a cover.
- It is an internet classic: linked from Slashdot and Penny Arcade in 2006, with fan videos and covers.
- Musically it is a short pop-rock song with a lead vocal, backing-vocal answers, bass, guitars and drums. That gives material for every use case:
  - a bass part to transcribe;
  - backing vocals for an a cappella version;
  - a straight groove to re-genre (bossa, samba, son).

## Layout (same as any `arrangements/<song>/` folder; everything here is tracked by git)
```
examples/code-monkey/
  code-monkey.mp3      the recording (tracked)
  lyrics.txt           to add: the author's lyrics (same licence)
  work/                the analysis: stems, bar map, report.md
  song.py              the transcription
  arrangement_*.py     one file per version (a cappella, band...)
  out-*/               scores, PDFs, MIDI, audio renders
```

## Next steps
```bash
PY=.venv/bin/python; C=arranger-core/scripts; A=examples/code-monkey
$PY $C/analyze.py $A/code-monkey.mp3 $A/work --lyrics $A/lyrics.txt     # about 6-8 min on a GPU
```
Then read `work/report.md` and follow arranger-core §1-§2 for `song.py`. The planned versions are:
- a lead sheet;
- the bass part as a tab, checked against the recording;
- an a cappella version, one of the lineups in `acappella-arranger/references/styles.md`;
- a band version from `south-american-arranger`.
