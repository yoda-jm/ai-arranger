# Arranging engine reference (`scripts/engine.py`)

An arrangement is a plain Python file that `build.py` executes:

```python
from engine import *          # build.py puts scripts/ and the arrangement's own folder on sys.path
import song as S              # your transcription file (melody, lyrics, chords), next to the arrangement

setup(voices=["L", "S1", "S2", "A", "T", "Br", "B", "VP"], title="Song", composer="Writer",
      arranger="a cappella arr. ...", name="song_acappella", solo="male")   # work= comes from build.py --work
s = section("Verse 1", "Bb", 1, S.V1_CH, S.V1, S.V1_LYR)      # name, key, first recording bar, chords, melody, lyrics
put_pad(s, ["S2", "A", "T"], "Oo", R(), dyn="p", text="warm pads")
put_bass(s, [(1, 0, 6), (1, 6, 2), (2, 8, 6), (2, 14, 2)], dyn="mf")
vp(s, hats="8")
```

## Units and data

- Time is in **16ths**: a 4/4 bar has `BAR = 16`, 3/4 has 12, 6/8 has 12 (beat `BEAT = 6`). Set the meter with `setup(meter=(3, 4))`.
- An **event** is `dict(start, dur, midi, lyr, tie_in, tie_out, art)`. `midi=None` is a rest. For VP, `midi` is a tuple of sounds such as `("B", "t")`. `art` is one of `staccato`, `accent`, `tenuto` or `fermata`.
- A **bar** is a list of events that covers exactly `BAR` 16ths. A **part** is a list of bars.
- A **section** is a dict: `name, key, first, nbars, chords, parts{voice: bars}, text{(voice, bar): str}, dyn{(voice, bar): str}, tempo, note`.
- **Voice keys** (`VOICE_INFO`) give the name, clef, default range, pan and volume:

| key | part | default range | key | part | default range |
|---|---|---|---|---|---|
| `L` | Solo (male: tenor clef G2–D5; `solo="female"`: G3–G5) | 43–74 | `T` | Tenor | D3–G4 (50–67) |
| `S` | Soprano | C4–G5 (60–79) | `T1`/`T2` | Tenor 1/2 | E3–A4 / C3–F4 |
| `S1` | Soprano 1 | D4–A5 (62–81) | `Br` | Baritone | A2–D4 (45–62) |
| `S2` | Soprano 2 | B♭3–D5 (58–74) | `B` | Bass | D2–A3 (38–57) |
| `A` | Alto | G3–C5 (55–72) | `B1`/`B2` | Bass 1/2 | F2–C4 / C2–G3 |
| `A1`/`A2` | Alto 1/2 | A♭3–C5 / F3–A4 | `VP` | Vocal percussion | (drum staff) |

  To add a voice, add an entry to `VOICE_INFO` before `setup()`. `RANGE` holds the active ranges, and `R(**over)` returns a copy with overrides, e.g. `R(S1=(70, 77))`. Narrow ranges are the main tool for placing pads and comping.
- **Chord symbols** are root + quality + optional `/bass`. The qualities are `"" m 7 m7 maj7 sus4 (sus) 7sus (7sus4) dim 6 m6 add9 madd9 sus2 aug dim7 m7b5 9 m9 maj9`, for example `"Eb/Bb"`, `"F7sus"` or `"Bbadd9"`. `chords` has one list per bar, and each list splits the bar evenly: `["C"]` is the whole bar, `["C", "G/B"]` is two halves, and 4 entries make quarters.
- **Keys** are `"Bb"`, `"F#"`, `"Gm"` and so on. A minor key uses its relative major's signature and scale, which is natural minor.

## Token lines

`parse_line(bars, lyrics=None, art=None)`. Each bar is a string of tokens `PITCH:DUR`:
- `D3:3` is a dotted 8th, `r:2` an 8th rest, `C4~:4` ties into the next note, which must have the same pitch.
- `Bb2:2=doo` gives that note its own syllable.
- `lyrics` is one string per bar with one syllable per **onset** (a tied continuation is not an onset). `_` means no syllable (melisma). The hyphen rules are `Dash-` (word start), `-ing` (word end) and `-ra-` (middle). A mismatch raises an error that shows the bar.
- `take(D, a, b)` reads bars a..b from `W/draft.py` dicts. `LEAD` returns `(tokens, lyrics)`, while `BASS`, `OTHER_TOP` and `CHORDS` return lists.
- `tr_tokens(bars, k, key)` transposes token bars and `tr_chords(rows, k, key)` transposes chord rows, both spelled for `key`.
- `shift(bars, k)` transposes event bars, typically ±12 for octaves. `relyric(bars, fn)` replaces syllables, where `fn(event, index_in_phrase)` gives the syllable.
- Syllable functions: `horn` (Bah / dah / dat), `flute` (doo / dl), `strings`, `guitar`, and `syl_seq([...])` for a fixed sequence.
- `merge(a, b, at)` combines bar lists: a before 16th `at`, b from `at` onward. Use it for echoes and answers.

## Generators (return parts; the `put_*` wrappers write them)

| function | what it makes |
|---|---|
| `harm(ref, sec, ±1, rng)` | A parallel diatonic 3rd above (+1) or below (−1) a line, moved to a chord tone on long notes. Use it for duets, "the record's harmony" and tags. |
| `block(top, sec, n_below, mode="close"/"drop2", double=False)` | Block voicing under a top line. Chord tones get chord tones below. Short passing tones get parallel 3rds. Tied notes are re-voiced when the chord changes. Use `drop2` for brass/horn sections and open lyric blocks. |
| `voicings(sec, voices, ranges, prev)` | A voice-leading search per chord slot. It keeps the 3rd and 7th, adds the 9th colour in 4+ voices, and penalises doubled 3rds/7ths, semitone and minor-9th rubs, and low close intervals. Used by `pad` and `comp`. |
| `pad(sec, voices, ranges, prev, syl)` | Sustained chords that hold common tones (tied). |
| `comp(sec, voices, ranges, prev, pattern, syl, art)` | Rhythmic chord hits. `PATTERNS` (4/4) are `off8` (offbeats), `back` (2 and 4), `tres` (3+3+2), `push`, `half`, `whole`, `bell` (straight 8ths), `charleston` and `sixteens`, or pass a list of `(start, dur)`. |
| `follow(sec, rhythm, voice, rng, prev, pref)` | One voice sings the rhythm and lyrics of a line on chord tones (`root`, `third`, `fifth`, `sev`). Use it to add a baritone to a lyric block. |
| `bass_pat(sec, pattern, rng, prev, syl)` | A per-bar bass pattern of `(selector, start, dur)`. The selector is 1 for the first chord's bass, 2 for the second chord's, or a pitch name. The pattern can also be a function of the bar index. |
| `turns(bars, sec)` | Flute turns (upper / main / lower 16ths) at phrase ends (every 2nd bar) on notes of a half note or longer. |

## Writing into a section

- `section(name, key, first, chords, mel=None, lyr=None, tempo=None, note=None)`: the solo (`L`) gets `mel`. `first` is the recording bar of the section's first bar; use `None` for bars that don't exist in the recording, such as an invented intro. Those bars are then skipped in the aligned renders and QA, and `vp()` needs a `groove` there.
- `put(sec, voice, bars, local=None, text=None, dyn=None)`: copies bars into a voice. `local` is a list of section-bar indices, and only those bars are written. A background part that enters in the middle of a word loses the leading hyphen. `LAST[voice]` remembers the last pitch so later pads lead smoothly.
- `put_pad(sec, voices, syl, ranges, local, color, text, dyn)`
- `put_comp(sec, voices, pattern, syl, ranges, local, text, dyn, art)`
- `put_block(sec, voices, top, local, mode, double, text, dyn, syl)`: `voices` are listed high to low, and `voices[0]` sings `top`.
- `put_follow(sec, voice, rhythm, rng, local, pref, text, dyn)`
- `put_bass(sec, pattern, local, syl, text, dyn, rng, voice="B")`
- `vp(sec, hats="8"|"4"|"16"|None, rim=False, crash=(), local=None, label=True, groove=None)`: copies kick and snare from `W/drumgrid.json`, fills included, and adds hats only where the record has drums. `rim` replaces the snare with a rim click (`k`) for soft verses. `crash` lists bar indices that start with `Ksh`. `groove=dict(K="X.......X.......", S="....X.......X...")` is used for bars that aren't in the recording.
- `vp_bar({0: "B/Ksh"})`: hand-written VP bar. The sounds are `B` (kick), `Pf` (snare), `k` (rim), `t` (closed hat), `ts` (open hat) and `Ksh` (crash).
- `fermata_last(sec)`: fermatas on the last bar.
- To edit by hand after a generator, change `sec["parts"][voice][bar]` directly; it is a list of event dicts. Rebuild a bar with `parse_line([...])[0]`.
- `sec["text"][(voice, bar)] = "flute (airy 'doo')"` and `sec["dyn"][(voice, bar)] = "mf"` add performance directions. `build.py` prints rehearsal marks, tempo (`tempo=`) and `note=` on the top staff.

## Typical recipes (from an 8-voice pop arrangement)

```python
# soft verse: string pads + rim-click VP, then flute + keys backbeat
put_pad(s, ["S2", "A", "T"], "Oo", R(S1=(70, 77), S2=(65, 74), A=(62, 69), T=(58, 65)), local=range(4), dyn="p")
put_pad(s, ["S1"], "doo", R(S1=(70, 77)), local=range(4, 8), text="flute (airy 'doo')")
put_comp(s, ["S2", "A", "T"], "back", "jah", R(S2=(65, 74), A=(62, 69), T=(58, 65)), local=range(4, 8), text="keys on 2 & 4")
s["parts"]["S1"] = turns([b or rest_bar() for b in s["parts"]["S1"]], s)
vp(s, hats=None, rim=True, local=range(4)); vp(s, hats="8", local=range(4, 8))

# chorus: hook words in a 6-part block (tune 8va on top), pads + offbeat keys between the hooks
top = shift(s["mel"], 12)
put_block(s, ["S1", "S2", "A", "T"], top, local=[0, 2, 4, 5, 6], mode="drop2", dyn="f")
put_follow(s, "Br", s["mel"], (46, 57), local=[0, 2, 4, 5, 6])
put_pad(s, ["S1", "S2", "A"], "Ah", R(), local=[1, 3]); put_comp(s, ["T", "Br"], "off8", "jen", R(), local=[1, 3])

# instrument hook copied from the record (here the intro brass), sung as a block with brass syllables
HOOK = "F4:2 G4:1 A4:1 C5:2 Bb4:1 A4:1 F4:8"
put_block(s, ["S1", "S2", "A", "T"], parse_line(["r:16", HOOK]), local=[1], syl=syl_seq(["Bah", "da", "da", "dah", "da", "da", "Bah!"]))

# the record's backing-vocal harmony under the solo: double the tune 8va + a 3rd below it
up = shift(s["mel"], 12); put(s, "S2", up); put(s, "A", harm(up, s, -1, R()["A"]))

# instrumental: the flute plays the verse tune in Eb -> S1 flute + S2 2nd flute in 3rds
fl = relyric(shift(parse_line(["r:16"] + S.V1[:4]), 17), flute)
put(s, "S1", fl, local=range(1, 5)); put(s, "S2", harm(fl, s, -1, R()["S2"]), local=range(1, 5))

# call and response tag: the group answers the solo
echo = parse_line(["r:16", "r:8 B4:2 C#5:2 D5:4"], ["", "Gum- -mi Bears!"])
top = harm(s["mel"], s, +1, (64, 79)); top[1] = merge([top[1]], [echo[1]], 8)[0]

# final chord with fermata and a crash
for v, t in {"S1": "F#5:16", "S2": "D5:16", "A": "A4:16", "T": "E4:16", "Br": "A3:16", "B": "D2:16"}.items():
    put(s, v, [None, parse_line([t])[0]], local=[1])
fermata_last(s); s["parts"]["VP"][1] = vp_bar({0: "B/Ksh"})
```

## Instrument parts, kits and constraints (registries for style layers)
The engine was born a cappella; style layers (e.g. `south-american-arranger/scripts/band.py`) add instruments by filling these dicts after `setup()`. Empty registries give the plain a cappella behaviour.

| registry | meaning | read by |
|---|---|---|
| `VOICE_INFO[k]` | (staff name, abbreviation, clef, sounding range, pan, volume) | build, qa |
| `KITS[part]` | percussion part → `{sound: dict(step, octave, gm, head, stem, mark, vel, label)}`; `mark` = `accent` / `ghost` (parenthesised) / `roll` | build (unpitched notes), render, qa |
| `PROGRAM[part]` | GM program (0-based) for the renders and the MusicXML instrument | build, render |
| `SOUND[part]` | MusicXML instrument-sound (`pluck.guitar.nylon-string`, `pluck.autoharp`...); MuseScore picks its instrument from it | build |
| `TRANSPOSE[part]` | written = sounding + k (12 for guitar and bass guitar: plain clef, sounds 8vb) | build |
| `KIND[part]` | `voice` / `pitched` / `perc` (QA treats only voices as singers) | qa, render |
| `CHORD_PARTS` | staves that print chord symbols (default: the top staff) | build |
| `PITCHSET[part]` | allowed MIDI pitches (a hang drum's notes) | qa |
| `CHORDSET[part]` | `fn(symbol) -> (playable, exact)` or None (autoharp chord bars) | build evaluates, qa reports |
| `PLAYERS` | player → [parts] played by one person, one at a time | qa |
| `META["score_render"]` | render a set at the arrangement's own tempos | render, qa |
| `META["rec_shift"]` | semitones from the record's key to the arrangement's key | render (aligned set), qa |

**Events beyond single notes**:
- `midi` may be a **tuple of MIDI numbers**: a chord on one staff.
- An event may carry:
  - `slash=True`: written as one rhythm slash on the middle line, silent in MuseScore;
  - `stroke` = `D U d u x A`: strum direction / muted chop / roll; the render strums the chord with it;
  - `show=True`: print the stroke marks;
  - `vel`: a velocity factor;
  - `spell` = `sharp` / `flat`: force the spelling.
- Spelling of chromatic notes follows the chord sounding under them: the 3rd/7th of the chord are spelled from its root (C# in A7, Ab in Bb7). A minor key's leading tone is sharp.

## Meter transplant (warps)
`section(..., warp="swing")` re-times a 4/4 transcription into the current meter. `warp_tokens(bars, how)` does the same on token bars. A warp maps every 16th of the source bar to a 16th of the target bar, so notes keep their syllables and ties.

| warp | from → to | effect |
|---|---|---|
| `swing` | 4/4 → 12/8 | quarter → dotted quarter; 8th pairs → quarter + 8th (long-short); 16ths → 8th 8th 16th 16th. The standard way to sing a straight pop line in 6/8 or 12/8 |
| `duplet` | 4/4 → 12/8 | 8ths → dotted-8th duplets (3+3), the hemiola feel against the 12/8 |
| `even` | 4/4 → 12/8 | 16ths kept close; 8ths as duplets |
| `waltz` | 4/4 → 3/4 | beats 1-2 kept, beats 3-4 squeezed into beat 3 (16ths in beats 3-4 may collide: the error names the bar) |
| a list | any | `src+1` target positions, monotonic |

The section remembers its warp: the renders aligned to the recording and `qa.py` (lead vs singer, bass, chroma) map each position back through it. One meter per piece; landó (12/8) and festejo (6/8) share 12/8, with tempos in dotted quarters (`tempo=` is in beats: dotted quarters in compound meters).

`acap.Layout(meta, bars)` gives the two clocks of a built score: `time(measure, pos)` at score tempo, and `rec(measure, pos)` → the position in the recording bar.

## build / render / qa

- `build.py ARR.py OUT --work W [--png] [--name base] [--bars-per-system 4] [--play-chords] [--no-mscore] [--lib DIR] [--scaling 5.2] [--staff-distance 55]` writes the files below. The page stays A4 at any `--scaling` (mm per staff space); tall scores (a band of 11 staves) fit 2 systems per page with `--scaling 4.2 --staff-distance 40`. With a subtitle, the title, composer and arranger are written as page credits:
  - `OUT/<name>.musicxml` and `.mscz` (voices on piano unless `SOUND` says otherwise, percussion parts on drum kits, chord symbols and rhythm slashes muted);
  - `.pdf`, `.mid`, `events.json` (with the section list, warps, lead map, kits, programs and constraints) and `png/page-NN.png`.

  `--lib` (or `$ARRANGER_LIBS`) puts a style layer's scripts on the import path.
- `render.py OUT [--work W]` writes `OUT/audio/*.wav`:
  - **aligned to the recording** (in the record's key):
    - `acappella_full` (or `aligned_full` when `score_render`);
    - `backgrounds_only` (everything except the lead of each bar);
    - `mix_with_original`;
    - `real_lead_over_backgrounds` (the karaoke lead stem over your backgrounds: does the new harmony work under the singer?);
  - **at score tempo** (with `META["score_render"]`): `score_full`, `score_no_vocals` (play-along), `score_vocals`, `score_part_<x>`. The part volumes (`VOICE_INFO` 6th field) set the balance;
  - without `score_render`: `part_<x>` aligned, plus `score_tempo` from MuseScore's MIDI.
- `qa.py OUT [--work W]` checks:
  - ranges (every pitched part), tessitura (singers), leaps and rubs (background singers);
  - lead syllables; lead vs chord symbols;
  - `PITCHSET` / `CHORDSET`, players on two parts, percussion instrument switches shorter than a beat;
  - the activity per section;
  - against the recording: lead vs singer, bass vs recorded bass, chroma similarity.
- Score limits:
  - One meter per piece.
  - No tuplets or swing notation: write straight 8ths and add a "swing" text, or use a compound meter.
  - One voice per staff: write divisi as extra parts. A chord tuple is one voice.
