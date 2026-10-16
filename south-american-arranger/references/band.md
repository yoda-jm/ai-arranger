# The band and the band layer (`scripts/band.py`)

## Who plays and sings what
Five players, all singing: **2 mezzo-sopranos and 3 baritones** (no soprano, tenor or bass voice).

| player | instruments (one at a time) | parts | notes |
|---|---|---|---|
| percussionist | cajón, güiro, shaker, snare, hang drum (D Kurd) | `P1`, `HANG` | the groove anchor. Hang = melodic colour, so no cajón meanwhile |
| small-drum player (a mezzo) | shakers, cuíca, djembé, bongos | `P2` | answers and colour around the cajón |
| autoharpist | 21-chord chromatic autoharp | `AH` | chords only from its bars (below). **Optional**: leave `AH` out of `parts` when there is no autoharpist |
| guitarist | guitar or ukulele (one per song, or switch at a section break) | `GTR` / `UKE` | the harmonic engine of most styles |
| bassist | electric bass | `BASS` | written in bass clef 8vb with a 4-string TAB staff |

Vocal parts: `W1` `W2` (Mezzo 1, 2) and `M1` `M2` `M3` (Baritone 1, 2, 3). Who sings which part is decided per song. Write it in the README, and remember the small-drum player is a mezzo.

| part | written | sounding range in `band.py` | comfortable | role |
|---|---|---|---|---|
| W1 Mezzo 1 | treble | G3–F5 (55–77) | A3–D5; belt to D5, A3–C4 is chest | lead / top coro |
| W2 Mezzo 2 | treble | G3–E5 (55–76) | A3–C5 | coro, 3rd below W1, descant |
| M1 Baritone 1 | treble 8vb | G2–G4 (43–67) | A2–E4, F4 for a short climax | lead / top male coro |
| M2 Baritone 2 | treble 8vb | G2–F#4 (43–66) | A2–D4 | coro |
| M3 Baritone 3 | bass clef | F2–E4 (41–64) | G2–C4 | low coro, sung bass in breakdowns |

- A mezzo melody sung **by a baritone at the same pitch** is in the top of his range (A3–F4 is ideal). A chorus belted to D5 goes down an octave for the men.
- Coros (backing vocals) in South American styles are mostly **parallel 3rds/6ths** ("segunda voz"), **unison hooks**, and **call-and-response** with the lead. With 2 + 3 voices, the classic blocks are:
  - a mezzo 3rd above the lead;
  - men in octaves;
  - a 5-voice block on the hook word only.
- **Singing while playing**: the cajón and bass grooves are usually automatic enough to sing coros over. Busy bongo/cuíca parts and guitar riffs are not. Give the busy player rests or a simple pattern where they sing.

## Fixed-pitch instruments (constraints checked by qa.py)
**Hang, D Kurd 9**: D3 (ding) | A3 Bb3 C4 D4 E4 F4 G4 A4. That is the D natural minor / F major scale.
- **Home keys** are F major and D minor (natural minor; dorian needs B, which the hang lacks).
- Modal neighbours, where the hang's notes give the mode's colour:
  - G dorian (E natural, no Eb);
  - Bb lydian (E natural);
  - C mixolydian (Bb, no B);
  - A phrygian (Bb: the Andean / flamenco colour).
- Any song in G minor, Bb, C or A minor works if the hang avoids the scale note it lacks.
- The hang can't play a C# (A7's 3rd) or an F# (D7's 3rd): over those chords `hang_arp` uses the tones it has (A, E, G over A7).
- Use it for intros, ostinati under verses, answers in the gaps, breakdowns. It is soft, so drop the cajón or play it lightly underneath.
- In another key: keep the hang tacet, or let it play only a drone on notes it shares with the key.

**Autoharp, Oscar Schmidt 21-chord** standard bars (AutoharpStore chart; bars can be rearranged, so check the instrument): Eb Bb F C G D A · F7 C7 G7 D7 A7 E7 B7 · Ab Bb7 Cm Gm Dm Am Em. No E, B or F# major, no Bm F#m C#m Fm, no maj7 or m7 bars.
- `autoharp_chord(sym)` maps every symbol to a bar:
  - maj7 / add9 / 6 / sus → the triad;
  - m7 / m9 → the minor;
  - 9 / 7sus → the 7.

  A missing 7 bar falls back to the triad and vice versa. `qa.py` lists the approximations and any chord with no bar (Bm, F#m, C#m, E major…).
- **Best keys**: F, C, G, Bb, D minor, G minor, A minor; then D, Eb.
- The autoharp strums all strings of the bar, so it is loud in the low-mid range. Strum patterns (`strum`) for chops and rolls; picked patterns (`arp`) for harp-like lines (the arpa llanera role, landó arpeggios).

## Writing parts (`from band import *`)
```python
setup(title=..., composer=..., arranger=..., meter=(12, 8), rec_shift=-1,      # semitones record -> arrangement
      parts=None,                                   # default: W1 W2 M1 M2 M3 GTR AH HANG BASS P1 P2 ("UKE" for ukulele; drop AH for now)
      tab=True,                                     # TAB staves under guitar (6 strings), ukulele and bass (4 strings)
      ranges=None)                                  # e.g. {"W1": (55, 76)}
s = section("Verse 1", "Dm", 4, chords, S.V1, S.V1_LYR, warp="swing", tempo=76, style="landó", note="...")
```
| writer | what it writes |
|---|---|
| `lead(s, "W1", octave=0)` | the section's tune in a singer's part, remembered as the lead per bar (`octave=-12`: a man singing the women's chorus) |
| `coro(s, voices, tokens, lyrics, local=...)` | a sung answer voiced as a block under its top line |
| engine: `harm`, `put_block`, `put_pad`, `put_comp`, `put_follow`, `put` | 3rds/6ths with the lead, blocks, pads, comping (see arranger-core engine.md) |
| `strum(s, part, "D.u D.u ...")` | strums as rhythm slashes (`D U d u x A`); the guitar plays real shapes (open chords, E/A-shape barres, from `fretboard.py`), shown fret by fret on the TAB staff; uke 4 strings, autoharp all strings of its bar |
| `arp(s, part, "1.32.43.2.3.")` | fingerpicked notes: digit = note of the instrument's chord shape from the bottom, `b` = bass an octave lower |
| `bassline(s, "1....5 1..>..")` | chord degrees: `1` (the chord's bass) `2 3 4 5 6 7 8`, `<` fifth below, `>` half step below the next chord, `N` the next chord's bass played early (the tumbao's anticipation) |
| `perc(s, "P1", cajon="B..TS.", shaker="xxXxxX")` | percussion lanes; one call per player and bar range (one instrument at a time, unless the second is a foot or a shaker in the free hand) |
| `perc_bar("P1", cajon="BSSBSS...")` | one hand-written bar (fills, remates, final hit): `s["parts"]["P1"][i] = perc_bar(...)` |
| `hang_arp(s, "0.1.2.0.1.2.")` | hang notes: `0` = ding, `k` = k-th chord tone the hang has |

- **Pattern grammar**:
  - one character per `unit` 16ths: default 8ths in 6/8 and 12/8 (12 cells = one 12/8 bar), 16ths in 2/4 and 4/4;
  - spaces and `|` are ignored;
  - short patterns repeat, long ones span bars;
  - `.` = rest (strums and arpeggios ring through it unless `ring=False`), `-` = hold (a bar starting with `-` ties over).
- **Every writer** takes `local=` (section bar indices), `text=` (italic direction at its first bar) and `dyn=`. It records its pattern for the groove cards (`sheets.py`).
- **Hand edits after a writer**: `s["parts"][part][i]` is a list of event dicts. Rebuild a bar with `parse_line([...])[0]` (pitched) or `perc_bar(...)`.

**Percussion strokes** (staff position in brackets):
- **P1**:
  - cajón `B` bass (F4) `T` tone (A4) `S` slap (C5) `g` ghost (C5, parenthesised)
  - güiro `L` long `s` short (G5 ×) `t` tap
  - shaker `X` accent `x` soft (E5 ×)
  - snare `X` `x` `g` ghost `R` rim `r` roll, `K` `k` a stick on the shell (accent / soft)
  - cowbell `O` `o` (accent / soft), clamped to the snare stand and played with the other stick. `qa.py` counts it as part of the snare setup, because its label starts with "snare-"
- **P2**:
  - djembé `B` bass `T` tone `S` slap `g` ghost
  - bongos `M` macho `m` macho finger `H` hembra `S` slap `p` thumb
  - cuíca `H` high `L` low `m` muted (◇ heads)
  - shaker `X` `x` (G5 ×)
- **Instrument changes**: write the new instrument as `text=` where it starts ("→ güiro"). `qa.py` flags switches with less than a beat to change.

**Renders** (GM): Mezzo 1 = flute, Baritone 1 = clarinet (the leads stand out), the coros = voice oohs, guitar = steel-string acoustic (muted chops `x` on GM muted electric guitar), uke = nylon guitar, autoharp = harp, hang = steel drums, bass = electric bass (finger). The kits use GM congas, bongos, güiro, maracas, cuíca, snare and kick. It is a sketch for checking the arrangement, not a production.
