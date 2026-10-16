# Genre transplant: taking a pop song far from home

The band's DNA is to keep the song and change everything else: a metal anthem as a waltz, a folk song as reggae, a rock classic as samba. What survives is the **tune and the words**. The meter, groove, tempo, harmony colour, form, intro, ending and instruments all belong to the new style. This page is the method. The styles themselves (grooves, tempos, idioms) are in [styles.md](styles.md); the band's constraints are in [band.md](band.md).

## 0. How far: transplant or touches
Distance is a per-song choice. Agree it in the brief, or offer both.
- **Transplant** (the default DNA, everything below): a new meter, groove, tempo, harmony colour and form. The tune and the words survive. An earlier arrangement used landó verses and festejo choruses in 12/8.
- **Touches** ("the original's vibe, played by this band"): keep what makes the record the record and change what the band sounds like.
  - **Keep**: the meter, the tempo, the form and section lengths, the dynamic arc (where the drums drop in and out), the record's hooks and riffs (moved to band instruments), and the original language.
  - **Key**: the nearest key the hang and autoharp allow, usually a semitone or a tone away.
  - **Change**:
    - the record's instruments become the band's (piano → autoharp + guitar, drum kit → cajón, synth riff → hang or guitar);
    - the drum grooves become a South American groove **in the same meter and tempo**: cumbia or chicha for 4/4 pop at 90-115, ijexá or candombe for gentler or faster grooves, a bossa feel for ballads;
    - South American colours appear at the song's seams: a hang intro, a cajón llamada into a chorus, a contrapunteo instead of the instrumental, coros in 3rds, a shout;
    - one bolder moment is welcome, such as a half-time or 12/8 bridge, or a festejo or cumbia double-time tag, as long as the song comes back home.
  - The checks are the same, plus the activity table should follow the record's arc (compare with the report's `d b o` levels per bar).
  - **Recipe** that worked:
    1. Read the report's `d b o` columns. Write down where the record's drums play, then copy the kick/snare grid onto the cajón (`B` = kick, `S` = snare).
    2. Use the drumless sections for the SA instruments that don't sound like a kit: hang, güiro, shaker.
    3. Copy the record's bass rhythm (`look.py nnls bass`), and put the style's bass figure only where the record's bass is loose.
    4. Turn the record's instrumental riffs into guitar or hang leads.
  - An earlier arrangement in this mode kept the original's 4/4 and its drum arc. The cajón played the record's groove, with a cumbia layer, a güiro in the drumless choruses, the hang, and chicha guitar leads.

## 1. Read the song as material
From the analysis report and `song.py`:
- **the tune**: its range, where it sits (speech-like verse vs belted chorus), and its rhythm (straight 8ths, 16th runs, long holds);
- **the loop**: many pop songs are one 4-chord loop. That is good news: the harmony is free to reinvent;
- **the form and energy arc**: soft verse → lift → big chorus; breakdown; last chorus;
- **the dramatic moments** to hang a transition on: a scream, a stop, a held note, a pickup ("Dios!" before the chorus);
- **the hook**: the 3-5 notes everybody knows. It must come out recognisable in the new style.

## 2. Choose the style(s): match the energy, not the surface
- One style per energy level. Two styles in one song are good when the song has two energies, switching at the song's own dramatic moments. Pairs from one tradition:
  - landó → festejo (Afro-Peruvian);
  - bossa → samba;
  - zamba → chacarera;
  - huayno → saya/caporales;
  - vals criollo → marinera.
- Further is better (the DNA), as long as the tune stays singable and the hook audible. A choice that changes the **meter** (4/4 → 6/8 or 3/4) is the strongest transplant. It must be done with a warp (below), not by squeezing.
- Quick guide (details in styles.md):

| original | transplants well into |
|---|---|
| ballad, 60-80 bpm | landó, zamba, bolero, bossa nova, milonga campera, vals criollo |
| mid-tempo 90-115 bpm | festejo, cumbia, chicha, baião, ijexá, candombe, huayno, saya |
| fast rocker 120+ | samba, maracatu, chacarera, joropo, frevo, caporales, tango (half-time) |
| 3/4 or 6/8 song | vals criollo, chacarera, zamba, joropo, bambuco |

## 3. Meter and tempo
- **Re-time the tune with a warp**, never by hand bar by bar. `section(..., warp="swing")`: 4/4 → 12/8, quarter → dotted quarter, 8th pairs → long-short. Use `duplet` for a hemiola feel, `waltz` for 4/4 → 3/4 (then fix colliding 16ths by hand). Cut-time styles (cumbia, samba, baião, huayno) keep 4/4: no warp needed.
- **Tempo**:
  - If the target style's range includes the record's beat rate, keep it: the singers keep the phrasing they know (festejo at dotted quarter = 106 for a 106 bpm song).
  - A slower style for some sections makes them longer: 76 instead of 106 is 40% longer. **Budget the total length** and cut instrumentals, repeats and outros to stay near the original (±15%).
- One meter per piece: landó and festejo share 12/8 with different tempos. If two styles need different meters, pick the one meter that notates both (12/8 holds 6/8 and 3/4 hemiolas).

## 4. Key
1. **The lead singer first**: the transcription's range in the new key must sit in the singer's comfortable zone (band.md).
2. **Then the fixed-pitch instruments**: the hang's scale and the autoharp's bars. For this band F major / D minor is home; a semitone or a whole tone away is usually fine for the singers.
3. **Then the style**: minor for landó, zamba, huayno, tango; major for festejo, samba, cumbia, joropo (both appear in all).
- Write `song.py` directly in the new key and set `rec_shift`. The checks against the recording then still work.

## 5. Harmony: new colour, same tune
Every move below keeps the melody notes. After each move, check `qa.py`'s *lead vs chord symbols*: a long note a semitone above a chord tone is a clash to fix.
- **Relative-minor reading** of a major loop: I → vi, IV → ii (F Gm Dm Bb → Dm Gm Dm Bb). The melody's 3rd and 5th over I become the minor's root area and 3rd. It instantly turns a pop verse into landó / zamba / tango territory.
- **The style's cadence on a rest**: put the minor's V7 (A7 in D minor) on the last beat of a phrase where the tune rests. In an Afro-Peruvian or Andean minor, a b9 over it (Bb over A7) is idiomatic.
- **Turnarounds**: add V7 to the 2nd half of ii and IV bars in festejo / cumbia / samba (F | Gm C7 | Dm | Bb C7).
- **Modal colour**:
  - ii as dorian (Gm6);
  - IV as maj7 or lydian;
  - phrygian (A Bb) for Andean and flamenco colour;
  - a pedal or ostinato (bass or hang ding) under the loop for hypnotic styles (huayno, ijexá, candombe).
- **Light and shade across the form**: e.g. verses minor (relative-minor reading), pre-chorus back to the record's major (a lift), chorus major in the faster style.
- The autoharp plays only its bars: write chord symbols it has, or accept its approximation (maj7 → triad).

## 6. Form surgery
- **Intro**: the groove first, built one instrument at a time, then the hook on an instrument (the hang, the autoharp or the guitar plays the chorus tune). The record's intro is usually not worth keeping.
- **Transitions between styles**:
  - a percussion **remate** (break) plus a shout ("¡Ahí nomá!") into a downbeat at the new tempo;
  - or a **metric modulation** (12/8 dotted quarter → new tempo).
  - Put them on the song's dramatic moments.
- **Instrumentals**: cut them, or turn them into something the style owns:
  - a cajón vs djembé/bongos **contrapunteo** (call and response);
  - a coro call-and-response on the hook;
  - a short guitar/autoharp solo on the verse tune.
- **Breakdown before the last chorus**: voices plus palmas (claps) or plus hang, then everybody in.
- **Ending in the style**: festejo/cumbia: stop on a hit after a shout. Landó/zamba: the ostinato fades or a rolled final chord. Samba: a batucada-style break.

## 7. Voices
- **Lead**: one singer per verse; duets trade verses and share choruses (the man an octave down on a high chorus).
- **Coros**:
  - answers in the gaps of the lead, on the hook words or the style's shouts;
  - parallel 3rds/6ths with the lead (segunda voz);
  - unison/octave hooks;
  - a 5-voice block only on the title words.
- **Pads** ("Oo", "Mm") for landó / zamba / bossa verses, quietly. Rhythmic syllables only where the percussion leaves room.
- **Shouts** and **jaleo** belong to the style: put them in the score as text or as short notes, and keep them few.

## 8. Instruments get the style's roles
| style role | band member |
|---|---|
| cajón / bombo / zabumba / surdo / tambora | cajón (P1), djembé (P2) |
| quijada / guacharaca / guache / triangle / ganzá / maracas | güiro, shakers (P1 or P2) |
| bongos / congas / cajita / repique / chico | bongos, djembé (P2) |
| cuíca, whistles | cuíca (P2) |
| guitar / requinto / tres / cuatro / charango | guitar or ukulele (uke = cuatro / charango colour) |
| harp (arpa llanera / paraguaya / andina), accordion stabs, piano montuno | autoharp (picked = harp, chops = accordion / piano) |
| marimba / kalimba / bells / flute riff | hang (and the coros) |
| bass / bajo | bass |

## 9. Checklist before building
- [ ] Every section has a style, tempo, key, lead singer and texture in the plan table.
- [ ] The tune is warped, not rewritten; the hook is recognisable.
- [ ] The total length is within ±15% of the record, or the user agreed.
- [ ] The harmony moves are checked against the lead (qa: lead vs chords).
- [ ] The hang plays only its notes; the autoharp only its bars.
- [ ] Each player plays one instrument at a time, with switches at section breaks.
- [ ] The energy arc builds to the last chorus (qa activity table), with one real breakdown.
- [ ] The intro, transitions and ending belong to the new style.
