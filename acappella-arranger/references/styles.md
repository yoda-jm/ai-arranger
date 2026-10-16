# Lineups and styles of known groups: style cards

Use a card when the user names one of these styles or groups. Otherwise the defaults in [SKILL.md §1](../SKILL.md) are the right choice for a choir or a mixed group: SATB, Solo + SATB + VP, or 8-part pop.

Each card gives:
- the lineup mapped to engine voice keys;
- the core features, with their sources (the letters in brackets, listed at the end of each card);
- how to write the style with the engine;
- what the engine can't do yet;
- what to listen to.

How the cards were made, and how to make one for a new style: [style-research.md](../../arranger-core/references/style-research.md).

**Status**: these three cards are **web-sourced (October 2026) and not yet measured on recordings** (step 7 of the method). Measure 2–3 reference tracks before relying on a number.

| style | voices | VP | the sound in one line |
|---|---|---|---|
| **Barbershop** | 4: tenor, lead, baritone, bass | no | homophonic close harmony that "rings": a 4-part chord on every melody note, many dominant 7ths |
| **Pentatonix** | 5: three upper voices sharing the lead, a very low bass, a beatboxer | yes | electronic pop: tight trio harmony with runs, the beatbox as the drum machine |
| **VoicePlay** | 5 men: tenor 1, tenor 2, baritone, bass, VP, plus guest soloists | yes | "a full band" from voices; theatrical covers (Disney, Broadway, Halloween); the lead switches within a song |

## 1. Barbershop (close-harmony quartet)
**Lineup**: men's quartets and choruses. Women's barbershop uses the same part names with every range a 4th higher [G].

| part | role | range (sounding, men) [G] | engine key |
|---|---|---|---|
| Tenor | harmony **above** the lead (light, head voice) | B♭3–D5 (58–74) | `T1`, renamed |
| Lead | **the melody**, always | D3–F4 (50–65) | `L`, renamed |
| Baritone | the chord tone that is left; crosses above and below the lead | C3–E4 (48–64) | `Br` |
| Bass | roots and fifths only | F2–C4 (41–60) | `B` |

**Core features** (a rulebook exists, so these are firm):
- **Homophony**: a 4-part chord on every melody note, unaccompanied, in close harmony [W1].
  - Tenor and bass don't take the melody, except for a note in a tag or to avoid awkward voice leading [W1].
  - Brief passages may use fewer than four parts [W1].
- **The barbershop seventh** is the cornerstone [B]. It is a dominant 7th: root, major 3rd, 5th, minor 7th.
  - Dominant and secondary-dominant 7ths make up **at least 1/3 of the song's duration** [W1, G].
  - The root moves mostly **around the circle of fifths** [W1, G].
  - Feature at least one chord beyond I, IV and V, such as II7 or VI7 [G].
  - Other common chords: the diminished 7th, the augmented 6th and the added 6th [W1].
  - Major keys ring more than minor keys [G].
  - Replace diminished or augmented chords with barbershop 7ths where the tune allows [G].
- **Voicing** [G]:
  - on triads, augmented chords and 6th chords, the bass and one other part both have the root, an octave apart;
  - every other chord has four different notes;
  - close spacing: for women's voices, a 10th sounds better than a 13th or two octaves.
- **Embellishments**, with restraint. Embellish each long melody note; the lead doesn't embellish, so the tune stays clear [G]. Each needs "metrical room" and room for breaths [G].
  - **Swipe**: two or more chords on one syllable, often near the end [B, W1].
  - **Echo**: the other parts repeat the lead's words [G names it].
  - **Bell chord**: the parts enter one after another [B].
  - **Tiddly**: a brief ornament in one voice while the others hold, often the baritone [B, W1].
- **Tag**: the ending or coda, a short repeated close [B, W2].
- **Form and tempo** [G]:
  - plan the blocks: intro, verses, choruses, repeats, tag;
  - the tempo is a ballad sung ad lib (rubato), a swing, or an uptune;
  - a **key lift** helps many songs.
- **Tuning**: the 7ths are sung in just intonation so the chord "rings" with overtones [W2]. Neither the GM render nor MuseScore can show this; tell the user.
- **Song choice** [G]:
  - the melody spans a 10th or less, with few big leaps and few accidentals;
  - the lyrics rhyme;
  - change the melody as little as possible;
  - "stay out of the way of the song".

**With the engine**:
```python
import engine as E
from engine import *
E.VOICE_INFO.update({                         # (staff name, abbreviation, clef, range, pan, volume)
    "T1": ("Tenor", "Tn", ("G", 2, -1), (58, 74), -20, 72),
    "L":  ("Lead", "Ld", ("G", 2, -1), (50, 65), 0, 90),
    "Br": ("Baritone", "Bari", ("F", 4, 0), (48, 64), 20, 72),
    "B":  ("Bass", "Bs", ("F", 4, 0), (41, 60), 0, 85)})
setup(voices=["T1", "L", "Br", "B"], ranges={"T1": (58, 74), "L": (50, 65), "Br": (48, 64), "B": (41, 60)}, ...)
s = section("Chorus", "Bb", 12, CHORDS, S.CH, S.CH_LYR)      # the lead ("L") gets the tune and the words
put(s, "T1", harm(s["mel"], s, +1, R()["T1"]))                # a first tenor: a 3rd above, chord tones on long notes
```
- Write the chords per beat (four per bar) where the tune moves. Barbershop changes chord far more often than pop.
- To check the 1/3 rule: add up the duration of the `7` chords in `chords` across the sections.

**Gaps** (not in the engine yet):
- There is no barbershop voicer: one that keeps the tune in the second voice, puts the tenor above it, the bass on roots and 5ths in the lead's rhythm and words, and the baritone on the missing tone, doubling the root only on triads. `block` and `put_block` put the tune on top.
- Until such a voicer exists, write the baritone and bass with tokens, or ask for a `barbershop()` helper.
- QA doesn't report the share of barbershop 7ths.

**Listen / material**:
- the BHS "Barberpole Cat" songbook: 12 standard songs every barbershopper knows [B];
- barbershoptags.com, a library of tags.

**Sources**:
- [W1] Wikipedia, "Barbershop arranging";
- [W2] Wikipedia, "Barbershop music";
- [B] Barbershop Harmony Society, "Learning the language of barbershop" (glossary);
- [G] Don Gray, *Making a basic barbershop arrangement from sheet music* (2004, arranging class notes, Spokane Community College).

## 2. Pentatonix (pop / electronic a cappella)
**Lineup**: five singers since 2011 [PW]. The bass changed in 2017 [PW]. The ranges aren't published, so take them from your singers. The three upper ranges overlap, so any of the three can take the tune or the top line.

| part | role | engine key |
|---|---|---|
| countertenor | lead or top harmony [SOS] | `T1`, renamed, with a high range |
| woman (soprano/alto) | lead or harmony [SOS] | `A` |
| baritone | lead or harmony [SOS] | `Br`, with a high top |
| bass | a very low bass: the original was a basso profondo [PW] | `B`, extended down |
| beatboxer | the drums; also plays cello [PW] | `VP` |

**Core features**:
- **The lead passes between the three upper voices**, often at a section change. In one session the baritone sang the verse lead, then the countertenor took the chorus, sung as a duet [SOS].
- **Tight harmony** in the trio, with **riffing** (runs) and **scat** [PW].
- **Beatbox as the drum machine** [PW]. Influences include dubstep, electro and hip hop [PW], so use electronic kicks and snares. A busier pattern comes in for the chorus "to move it along" [SOS]: VP density is the energy control.
- **Body percussion**: snaps, claps and stomps [SOS].
- **Covers, often as medleys** (Daft Punk, Beyoncé), and Christmas albums [PW].
- Their two arrangement Grammys were for the Daft Punk medley and "Dance of the Sugar Plum Fairy", an instrumental piece [PW]. So **voices imitating instruments and synths** belong to the style.
- **Incidental, studio only; don't write these** [SOS]:
  - each backing vocal recorded four times;
  - the beatbox blended with samples;
  - harmonics added to the bass so that it carries on small speakers.

  Live, the five parts must stand on their own.

**With the engine**: rotate the lead the way the band layer's `lead()` does:
```python
put(s, "T1", s["mel"]); s["lead"] = {i: ("T1", 0) for i in range(s["nbars"])}   # T1 sings the tune here
put(s, "A", harm(s["mel"], s, -1, R()["A"]))                                    # trio harmony under it
put_bass(s, ...); vp(s, hats="8")                                                # the bass + VP rhythm section
```
- QA and the renders follow `s["lead"]` bar by bar.
- Leave "L" out of `voices`: the lead is whichever of the three sings the tune.

**Gaps and things to measure**:
- The runs need hand-written tokens (16ths, 32nds).
- There are no syllables yet for a synth bass, wobbles, risers or other electronic VP sounds.
- **Measure on recordings first**: the "drops" (VP and bass alone), the key changes and the medley seams. Fans mention them; the sources above don't.

**Listen** [PW]: the Daft Punk medley, "Dance of the Sugar Plum Fairy", the Christmas albums.

**Sources**:
- [PW] Wikipedia, "Pentatonix";
- [SOS] Sound On Sound, "Inside Track: Pentatonix" (a mix session: lead changes, beatbox overdubs, body percussion, studio processing).

## 3. VoicePlay (theatrical male a cappella with VP)
**Lineup**: five men [VW]. The group began as a barbershop quartet and then added a vocal percussionist [VW], which gives barbershop close harmony plus VP. Its membership has changed often, and its videos add guest singers and duplicate members digitally, so a video can have more parts than five singers [VW].

| part | engine key |
|---|---|
| tenor 1 / tenor 2 | `T1` / `T2` |
| baritone | `Br` |
| bass: very low notes, with a subharmonic register blended with the chest voice [CV] | `B`, extended down to what the singer has |
| vocal percussion | `VP` |
| guest soloist | `L` (`setup(solo="female")` for a woman) |

**Core features** [VW unless marked]:
- They aim to **sound like a full band**, and they **switch the lead within a song**.
- Many genres with a contemporary pop sound. A special love for **Disney, Broadway and Halloween** songs, often with a guest soloist (a *Moana* medley with a guest singer).
- **Theatrical**: the shows mix singing with humour and skits, and the videos are staged. Writing for characters means giving each character's lines to one voice.
- At times a member plays an instrument (piano, violin).

**With the engine**: as for Pentatonix.
- Rotate the lead with `put` + `s["lead"]`, one voice per character.
- The guest takes `L`.
- The four sung parts can switch between band imitation (comping, a horn block with `put_block(..., mode="drop2")`) and barbershop-like lyric blocks.

**Gaps**: the sources say little about how they arrange. This card most needs measuring on recordings (style-research.md, step 7) before you rely on it.

**Sources**:
- [VW] Wikipedia, "VoicePlay";
- [CV] *The Charismatic Voice* podcast, episode 005, "Geoff Castellucci: Beyond Basso Profundo, Part I" (episode page).
