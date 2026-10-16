# Contemporary a cappella arranging: the craft, condensed

This page collects the working rules this skill relies on, so the agent doesn't need to research arranging each time. They are distilled from Deke Sharon & Dylan Bell, *A Cappella Arranging* (2012); Deke Sharon, *The Heart of Vocal Harmony* (2016); Sharon's interviews; the CASA arranging resources; and an 8-voice cartoon-theme arrangement made with this toolkit.

## 0. Method in ten steps (after Sharon)
1. **Choose the song and the group.** Number of voices, real ranges, whether there is a beatboxer, the soloist's key, the style (pop/doo-wop/jazz/choral) and the difficulty.
2. **Listen and transcribe**: the form, the chords, the bass line, the solo, the backing vocals and the **instrumental hooks**. `analyze.py` and `report.py` do most of this. Every section of the arrangement should be traceable to something in the record.
3. **Decide the key.** Use the soloist's best key, then check that the bass part isn't too low (the lowest note around D2/E2 at most for amateur basses) and the top isn't too high (a sustained top below about A5).
4. **Map the form** into a table of sections × textures (see §4). Plan the energy arc before writing any notes.
5. **Write the melody** first, as sung (simplify fussy rhythms; keep the singer's signature licks).
6. **Write the bass**. It is the "second melody": copy the record's bass line, keep its rhythm, and give it singable syllables.
7. **Write the vocal percussion**: copy the record's drum pattern (kick and snare positions, fills), simplified for a mouth.
8. **Write the backgrounds**: pads, comping, instrument hooks, counter-melodies and lyric blocks. Hand the defining instrumental hooks to voices. Keep the record's own backing-vocal lines.
9. **Refine**: voice leading, spacing, breath, syllables and dynamics. Remove anything that fights the solo.
10. **Test**: sing or play it, listen under the original (`render.py` mix), fix, and simplify.

## 1. Roles in a pop a cappella group
| role | job | typical voices |
|---|---|---|
| Solo | the melody and lyrics, free phrasing | L |
| Bass | roots, the record's bass line, the groove with the VP | B (+ B2 for low doubling) |
| VP | kick, snare and hats; fills mark the sections | VP |
| Backgrounds | the chords, as pads, comping or lyric blocks | S1 S2 A T Br |
| Hook / counter-line | the instrument riffs and answers: flute, brass, guitar, strings, synth | the brightest available voice (S1 or T) |
| Descant | a high line in the last chorus | S1 |

**Voicing by group size**
- **4 voices (SATB)**: melody in S or T, bass in B, the other two harmonise. Use more lyric/homophonic writing, since there are fewer voices to imitate the band.
- **5 voices**: the 4 above + VP, or Solo + SATB.
- **6 voices**: Solo + SATB + VP, the most common pop format. The backgrounds are three voices (close triads) over a bass.
- **8 voices**: Solo + S1 S2 A T Bar B + VP. This gives five background voices, enough for a full 4-way block plus an independent hook or counter-line, or two textures at once (pads + comping).
- **A known group's lineup** (barbershop's tenor / lead / baritone / bass, Pentatonix's trio + bass + beatbox, VoicePlay's 4 men + VP): see the style cards in [styles.md](styles.md).

## 2. Voicing rules (what `engine.voicings`, `block` and `harm` enforce, and what to check by eye)
- **Keep the 3rd and the 7th.** They define the chord. The root is in the bass, so the backgrounds don't need it. Don't double the 3rd or 7th.
- **Colour.** Add the 9th in pads of 4+ voices (`add9` on major chords; the 11th/sus colour on minor chords sparingly). Use 6ths in retro/doo-wop styles.
- **Avoid minor 9ths and semitones between sustained voices** unless the clash *is* the record's sound. A semitone at the top of a sus chord can be lovely; one between the alto and tenor is usually mud.
- **Spacing.** Place the voices close (within an octave) in the middle and upper registers. Below about C3, keep intervals of a 5th or wider; 3rds down there sound muddy. There should be a big gap between the bass and the lowest background voice, about an octave.
- **Close vs open.** Use close position (4-way close) for bright, punchy brass or jazz sections. Use drop-2 (the 2nd voice from the top dropped an octave) for fuller, warmer horn sections and lyric blocks. Use open / spread voicings for ballads and big final chords.
- **Voice leading.** Move each voice by step or by a common tone; pad voices should hold common tones. Avoid parallel octaves and 5ths between the outer voices in lyric blocks, though in pop pads and brass stacks parallel motion is the style. Avoid voice crossing within a texture.
- **Doubling the melody.** Doubling the tune an octave above (or below) in one background voice is a strong, simple texture for choruses and hooks.
- **Harmony a 3rd above or below the melody** (`harm`) is the classic duet and backing-vocal sound. A 6th below is the same pitch classes, an octave lower.
- **Tessitura beats range.** A part can touch the top of its range, but it shouldn't *sit* there. `qa.py` reports the percentage of time spent in the top three semitones; over about 15% for a non-solo part is tiring. Basses tire on long low notes, and sopranos tire on sustained D5–G5.

## 3. The background palette (texture → engine call → syllables)
| texture | when | engine | syllables |
|---|---|---|---|
| **Pads** (strings, organ, synth pad) | verses, ballads, under busy solos | `put_pad` | "Oo" (dark, soft), "Ah" (open, builds), "Mm" (very soft), "Ooh" (descant) |
| **Comping** (keys, guitar) | grooves; they fill the rhythm the drums leave | `put_comp` with `off8` (reggae/pop upstrokes), `back` (2 and 4), `tres` (3+3+2 latin/pop), `push`, `bell` | keys "jen" / "jah", guitar "jen" / "jow", plucks "dn", "bm" |
| **Lyric block** (homophony) | chorus hooks, titles, the last chorus | `put_block` (drop2) + `put_follow` | the words. Use them only on the hook words, or for a whole chorus when that chorus is the climax |
| **Echo / answer** | between solo phrases, tags | `merge` + `parse_line` | a repeat of the last words or the title |
| **Counter-melody** | 2nd verse, instrumental, last chorus | `harm`, hand-written tokens, `OTHER_TOP` draft | flute "doo / dl", violin "nee", soft "loo" |
| **Instrument hooks** | intros, fills, instrumentals | copy the riff from `OTHER_TOP`, `look.py roll other` | brass "Bah / dah / dat", sax "dwee / dah", flute "doo / dl", bells "din / ding", synth "nee / now", guitar riff "nin / now" |
| **Bass** | always | `put_bass` (pattern) or the transcribed line | "doom" on long notes, "dm" on short ones, "bm", "dn". Use "doo" / "dah" for walking lines and "Oo" for ballads |
| **VP** | everywhere the record has drums | `vp` from the drum grid | see §5 |

The syllables are part of the sound:
- Plosives and dental attacks (b, d, j, t) give punch and short notes.
- Liquids and nasals (l, m, n) give soft and legato notes.
- An "n" ending ("jen", "dn") lets a short note ring like a keyboard. An "m" ending ("doom", "bm") gives a bass a round tail.
- Open vowels (ah) project; closed vowels (oo, mm) blend and stay soft.
- Change the syllable to change the dynamic before reaching for more notes.

## 4. Form and energy
- **Every repeated section gets a new texture**, and the energy keeps building toward the last chorus. A typical arc:
  - Intro: the hook.
  - V1: sparse (bass + pads, a light VP or rim).
  - Ch1: groove and hooks.
  - V2: add a counter-line.
  - Ch2: fuller, words in the backgrounds.
  - Bridge or breakdown: a contrast (drop the VP, change the texture or key).
  - Last chorus: everything plus a descant.
  - Tag / ending: an echo, then the final chord.
- **Layer entrances.** Bring a part in at a phrase start, never all at once (unless that's the point).
- **Make the breakdown real.** Remove the VP, or the bass, or both, for 4–8 bars before the final build. If the record already has a ballad section, that is the breakdown.
- **Key changes.** If the record modulates, keep it. A half-step "truck driver" modulation can be added before the last chorus if the record has none. Check the ranges afterwards.
- **Endings.** Use a tag on the title (repeat the last line two or three times, the group answering the solo), then a big chord. Spread the final chord wide: the bass on the root, the 3rd high, the 9th or 6th for colour, a fermata, and a VP crash ("Ksh").
- **Leave space for the solo.** Under lyric lines, backgrounds sustain or comp. Fills and answers go in the gaps between solo phrases.

## 5. Vocal percussion (Standard Beatbox Notation basics)
| sound | written | how | staff (this toolkit) |
|---|---|---|---|
| kick drum | **B** | lip "b" with a burst of air | bottom space (F4) |
| snare | **Pf** / **Pff** | lip "p" + "f" (or a K-snare "Kh") | 3rd space (C5) |
| rim / side stick | **k** | tongue click "k" | 3rd space, × head |
| closed hat | **t** | tongue "t" | above the staff, × head |
| open hat | **ts** | "tss" | above the staff, ⊗ head |
| crash | **Ksh** | "ksh" | above the staff, × head |

- Copy the record's **kick and snare** (`W/drumgrid.json`) and simplify busy hats.
- Keep the fills that mark section changes. Drop the VP where the record has no drums.
- Use a lighter VP (rim + kick, no hats) in the first verse and the full kit in choruses.
- Write a VP key in the score or README. Write the syllables in the first bar of each groove change.
- The beatboxer breathes in on "k" or inward sounds. Avoid 16th-note hats for more than a few bars.
- Bass and VP form the rhythm section: the bass's attacks should line up with the kick.

## 6. Singer-friendliness checklist
- Every part has breaths: at least an 8th rest every 2–4 bars in moving parts. Stagger breathing in pads.
- No leaps larger than a 6th in background parts, except octave jumps at phrase starts. `qa.py` counts them.
- Pitches should be findable: a new entrance starts on a chord tone, preferably one already sounding.
- Rhythms are at most as hard as the solo's. Prefer 8ths over 16ths in pads.
- Text: background lyrics are the hook words, sung together, and match the solo's vowels.
- Mark the dynamics at every texture change, plus *cresc.* into choruses.
- Give the instrument imitations a short performance note: "flute (airy 'doo')", "keys on 2 & 4", "brass, punchy".
- The tempo and feel are written on the score. Tempo changes come from the record (`bars.json` tempo runs).

## 7. Copy the record, then improve
The best source material is already on the record:
- **Bass line**: the `BASS` draft, checked with `look.py nnls bass` and copied an octave up into singing range if needed.
- **Backing vocals**: the report's backing table. These are the arranger's own harmonies, so keep them.
- **Instrument hooks and counter-melodies**: the `OTHER_TOP` draft, the "instrument lines that quote a vocal phrase" list and `look.py roll other`. Instrumentals often replay the verse or chorus tune in another key, as in one cartoon theme, where the flute plays the verse in E♭ and the horns play the chorus in A.
- **Drum pattern and fills**: `drumgrid.json`.
- **Chords**: take them from the bass plus the chroma, never from the melody alone. A long note an 8th before a chord change usually belongs to the new chord (the "push").

Where the record has nothing (a long sustained guitar chord, say), invent a pad or a comping figure in the record's style.
