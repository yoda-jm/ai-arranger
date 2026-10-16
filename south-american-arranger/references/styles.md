# South-American styles: grids, roles and switching rules

Working reference for the arranging engine. Sections 1–3 cover landó, festejo and switching
between them in full depth (an earlier arrangement used them: landó verses, festejo choruses). Section 4 has short style
cards for 23 other styles. Section 5 is a guide to which style suits which song, and section 6
lists the sources. To add a style, research it with
[arranger-core/references/style-research.md](../../arranger-core/references/style-research.md), then write its card here.

---

## 0. Conventions used in this file

**Grids.** One string per instrument per bar, one character per subdivision. Spaces are for
readability only. ` | ` separates consecutive bars of a multi-bar pattern. ` # ` (hash with a
space on both sides) starts a comment, so sharps such as `G#2` are safe.
Every grid block opens with a `# grid N` line, where N is the number of characters per bar:

| meter | `grid` | one char = | spacing used here |
|---|---|---|---|
| 12/8 | 12 (or 24) | 8th (16th) | groups of 3 (6) = one dotted-quarter beat |
| 6/8 | 6 | 8th | groups of 3 |
| 3/4 | 6 | 8th | groups of 2 = one quarter beat |
| 4/4 | 16 | 16th | groups of 4 = one quarter |
| 2/4 | 16 | 16th of the 2/4 bar | **16 chars = two 2/4 bars** (= one 4/4-length bar); groups of 4 = one 2/4 beat |

**Tempo for 2/4 styles** is given as the 2/4 beat (4 chars, the surdo or bass pulse). Many BPM
databases and US-style charts write the same music in 4/4 with doubled note values, and so report
**twice** that number for bossa, samba-canção and similar. 12/8 and 6/8 tempos are given as the
dotted quarter (♩.).

**Symbols** are exactly those of the engine:
cajón `B T S g` · güiro `L s t` · shaker `X x` · snare `X x g R r` · djembé `B T S g` ·
bongos `M m H S p` · cuíca `H L m` · strum `D U d u x A` · fingerpick digits `1-4` ·
bass `1 3 5 6 7 8 < > - .` · hang = note-name tokens from D Kurd.

**Afro-Peruvian cajón mapping.** Peruvian sources write two sounds: *grave* (bass, centre) = `B`,
and *agudo* (high, top edge, open) = `T`. Use `S` for a sharper, brighter agudo on accents and
choruses, and for the ⊗ (muffled or slap) noteheads in transcriptions. A flam on an agudo is
written `gT` in a 24-char grid. On a 12-char grid the flam is implied: just play `T` with a grace
note. Peruvian cajones have no snare wires, so on a flamenco cajón, keep slaps sparse.

**Hang lines** are space-separated tokens, one per subdivision, using `.` and `-`.
**Riffs written as note names** (for example the Toro Mata bordón) are melodic input. A degree
or digit approximation is always given next to them.

**Mixed guitar lines (thumb + chord).** Some styles need a single bass note followed by a short
chord (vals tundete, bossa). Those lines are marked `MIXED`: a digit is a single note (`1` = bass)
and a letter is a strum or pinch. If the engine cannot mix the two, use the fallback line given,
or hand the thumb part to the bassist.

**Confidence tags** (after a grid or table row):
- `[S]` transcribed from a cited source (rhythm checked against the notation in that source).
- `[C]` common teaching pattern, consistent with the sources but not transcribed from one.
- `[A]` approximate or constructed for this band. Check it by ear against the listening references.
- Tempo ranges in the style cards are approximate (by ear and general knowledge) unless a source
  is named next to them.

**Band defaults.** Everyone plays exactly one instrument at a time.
- P1: cajón | güiro | hang (D Kurd) | shaker | snare
- P2: shakers | cuíca | djembé | bongos
- Autoharp (21-chord Oscar Schmidt)
- Guitar **or** ukulele, chosen per song
- Bass

Every card states who plays what.

**Instrument limits that drive key choice**
- Autoharp 21-chord standard bars (AutoharpStore chart): row 1 `Eb Bb F C G D A` · row 2
  `F7 C7 G7 D7 A7 E7 B7` · row 3 `Ab Bb7 Cm Gm Dm Am Em`. There is no E, B or F# major, no Bm,
  F#m, C#m or Fm, and no maj7 or m7. Comfortable keys: F, C, G, Bb, D (no Bm/F#m), Dm, Am, Gm,
  Em (no Bm), Cm (no Fm).
- Hang D Kurd 9: `D3 | A3 Bb3 C4 D4 E4 F4 G4 A4`, the notes of D aeolian (= F major,
  C mixolydian, G dorian). **D minor / F major is the one key family where hang and autoharp
  are both fully usable.** Over A7 the hang avoids C (it has no C#). Over G7 it avoids Bb.
- Ukulele is re-entrant and has no bass strings. It covers cuatro, charango, cavaquinho and tiple
  roles well, but cannot play *bordones* (bass-string runs). When the uke is chosen, the bassist
  takes the bordón.

---

## 1. LANDÓ (Afro-Peruvian, slow)

### 1.1 Identity in one paragraph
A slow-to-medium, sensual, minor-key Afro-Peruvian song form. It was "reconstructed" in Lima in
the 1960s-70s by Nicomedes and Victoria Santa Cruz, Caitro Soto and Chabuca Granda, so its
"tradition" is a 20th-century construction (Feldman; Elías Llanos & Wolff). The basic ensemble is
cajón, two guitars (one strums, one plays *bordones* on the bass strings and *repiques* up high),
voice and chorus. Perú Negro-style versions add bongó, cencerro (campana), tumbadora and vibraslap.
The core of the style is a **constant 12/8 cajón ostinato with flammed agudos**, a **repeating
bass-string guitar archetype** (the *Toro mata* figure), and a **call-and-response vocal over i–V7**.

### 1.2 Meter and tempo
- Written in **12/8** (Feldman; León Quirós; the PUCP harmony thesis, which found 12/8 constant
  1960-1990). Tompkins writes it as **6/4 = 4+2/4**. Thomann writes it as 6/4, and Demera
  transcribes some songs in **3/4**: one 12-eighth cycle = two 3/4 bars, with the same pattern
  (see 1.3).
- It is felt in three ways at once: 4 dotted quarters (12/8), 6 quarters (6/4 hemiola), and
  singers who phrase almost freely over it (Chabuca's "Landó": voice in simple 4, guitar in
  compound 4, oboe in compound 2). **This built-in hemiola is the hinge for switching to festejo
  (section 3).**
- Two sub-types (Elías Llanos & Wolff):
  - **landó-canción**: ♩. ≈ 60–80, chamber-like, the voice leads.
  - **landó-danza**: ♩. ≈ 88–100, heavy percussion, Cuban-influenced, antiphonal, built on the
    Toro mata archetype.

| reference recording | ♩. (approx.) | key | note |
|---|---|---|---|
| Nicomedes Santa Cruz / Cumanana, "Samba malató" (1964; reissues cited as 1970/71) | ≈ 80 | Dm (i–V7: Dm–A7) | first landó on record; cajón follows the guitar |
| Caitro Soto (cajón) / Cecilia Barraza, "Toro mata" (1971) | ≈ 60 | Cm–G7 (Caitro); Am in other versions | set the landó cajón style and the bordón archetype |
| Lucila Campos, "(A) saca' camote con el pie" (1974) | ≈ 75–80 | C minor | cyclic V7 (call) → i (response), heavy percussion |
| Chabuca Granda, "Landó" (Tarimba negra, 1978) | ≈ 75–79 | E minor → E major | polymetric landó-canción |
| Andrés Soto, "Negra presuntuosa" (1981) | ≈ 58–60 | G minor | "extremely heavy", near-spoken verses |
| Pepe Vásquez, "No, Valentín" (2002) | ≈ 85–88 | A minor, IV major (D) replaces V | landó-danza, disco-octave bass |
| Susana Baca, "María Landó" (1995) | slow (not measured) | minor | auto-detected "115 BPM" on SongBPM is not a reliable ♩. value |

Tempos are from Elías Llanos & Wolff 2019 (Tab. 1, Figs. 1, 4, 5). Their own warning: the values
are didactic, not rigorous.

### 1.3 Cajón

The flammed agudos fall on eighths 3, 8 and 11 (in 6/4 counting: "2", "4+" and "6", as Thomann
puts it). The bass strokes sit around them.

```
# grid 12   (12/8, one char = 8th)
cajón.A     B.T .BB .TB .TB      # [S] base A: Cotito / Hnos. Santa Cruz "Toro mata" / Feldman var.2 / Wikipedia
cajón.B     B.T .BB .T. T.B      # [S] base B: Caitro Soto / Feldman var.1 / Wikipedia "alternative"
cajón.init  BBB BBB .T. BT.      # [S] 1964 "patrón inicial" (Samba malató): cajón = guitar rhythm
```
```
# grid 24   (12/8, one char = 16th; flams written g+T)
cajón.A24   B..gT. ..B.B. .gT.B. .gT.B.   # [S] base A as written in Demera's Toro mata transcription
```
Written in 3/4 (Valentín, Negra presuntuosa transcriptions), base A becomes `B.T.BB | .TB.TB`.
That is the same cycle, so only the downbeat label moves. In Demera's "Negra presuntuosa", the
second half (`.TB.TB`) is written first.

**Variations**
```
# grid 12
cajón.v1    BgT gBB gTB gTB      # [A] ghosted, for verse 2 and more motion
cajón.v2    B.S .BB .SB .SB      # [A] chorus: slaps for the agudos
cajón.v3    B.T .BB .TB TTT      # [A] last-beat pick-up into the next phrase
```

**Remates and llamadas** (section markers). Landó fills are short "repiques" (finger rolls). The
big markers are unison cortes with the guitar.
```
# grid 12
rem.1       B.T .BB .TB TTT                   # [A] 1-beat fill, end of each 4- or 8-bar phrase
rem.2       B.T .BB TTT SSS | B.. ... ... ... # [A] 2-beat fill + unison downbeat, then silence (corte)
rem.3       BBB BBB .T. BT.                   # [S] use the 1964 initial pattern as a 1-bar "call" before the groove
# grid 24
rem.4       B..... ...... TgTgTg TgTgSS       # [A] 16th repique over the last 2 beats
```
Practice from Demera's arrangements: the intro has cortes on cajón and congas under the guitar
riff, and the cajón plays "repiques interpretativos" in the spaces of an a-cappella opening chorus.

### 1.4 Cajita, quijada, campana: what the band does instead
Classic landó uses **no quijada or cajita** (those are festejo colours). Its extra metal is the
**campana (cencerro)**, plus a vibraslap in Lucila Campos's version.
- Samba malató campana `[S]` (Elías Llanos & Wolff Fig. 1): groups of 4 eighths, `HHL.` ×3 per
  bar, a 3-against-4 cross rhythm.
  → P2 bongos: `MMH. MMH. MMH.` (12 chars, written in 4s), or autoharp damped chops on the same
  rhythm.
- The güiro (as vibraslap or quijada) is **only a colour at section ends**: P1 leaves the cajón for
  1 bar, or P1 is free in an intro: `t.. ... ... ...` (one hit) or `L-- --- ... ...` (one long
  rasp).

### 1.5 Guitar
**Toro mata bordón archetype** `[S]` (Elías Llanos & Wolff Fig. 5, Caitro Soto version). It is
played on the bass strings and repeats through the whole song. The same figure appears in the
voice (Cecilia Barraza) and in an ornamented 8th-note form (Susana Baca).
Rhythm: `long-short | short-long | short-long | short-long` = attacks on 1 3 4 5 7 8 10 11.
```
# grid 12   tokens = notes (melodic input), sounding pitch
gtr.riff.Am   A2 . C3 E3 D3 . E3 C3 . D3 B2 .      # [S] over Am  (transpose: i)
gtr.riff.E7   G#2 . B2 E3 D3 . E3 C3 . D3 B2 .     # [S] over E7  (V7)
```
Degree/digit approximation for the engine (chord tones only, so D and B become chord tones):
```
# grid 12
gtr.bord      1.2 32. 32. 21.      # [A] fingerpick digits: 1=root 2=3rd 3=5th, archetype rhythm and contour
gtr.rasg      D.u dD. uD. uD.      # [A] strummed version of the archetype rhythm (2nd guitar)
gtr.arp       1.3 4.3 2.3 4.3      # [A] landó-canción arpeggio (Chabuca/Casaverde style: sparse, lets voice breathe)
```
- 2-guitar texture (PUCP "Cada canción con su bordón"): guitar 1 = bordones and repiques,
  guitar 2 = rasgueo. Our band has one guitarist, so: **guitar = bordón**, **autoharp = the
  rasgueo or pad role**.
- **Ukulele**: works for `gtr.rasg` and `gtr.arp`, but cannot play the bordón. If the uke is
  chosen, the **bass plays the riff** (bass.A).

### 1.6 Bass
```
# grid 12
bass.A      1-3 58- 53- 5<-      # [A] doubles the Toro mata bordón rhythm (degrees approximate the riff)
bass.B      1-- --- 5-- ---      # [A] landó-canción: half-bar root / fifth, very sparse
bass.C      1-5 -1- 5-1 -5-      # [A] 6/4 hemiola reading (quarters): use for the festejo pivot (sec. 3)
bass.D      1-- 1-8 --5 --<      # [A] "No, Valentín" disco-octave flavour (landó-danza)
```

### 1.7 Harmony, melody, vocals, form
- **Harmony**: minor key throughout 1960-1990 (PUCP). The base is **i ↔ V7** (Toro mata Cm–G7,
  Samba malató Dm–A7), often **one chord per bar or per 2 bars, as a cycle**. V7 is the "call" and
  i the "answer" (A saca' camote). Later landós add secondary dominants and tritone subs. A
  **major IV substituting for V** (Am–D, "No, Valentín") gives a dorian colour. Chabuca's "Landó"
  modulates from minor to the parallel major.
- **Melody**: minor-pentatonic phrases plus chord tones. Contours are wave-shaped and stay
  singable. Call phrases tend to fall and response phrases rise, and the call often starts a 5th
  above the response's first note (Demera on Toro mata). Some songs use only 4 notes by step
  (Re–Mib–Fa–Sol, A saca' camote). The vocal rhythm is "spaced and laid back" and seems to "evade
  the bar line" (Tompkins via Feldman).
- **Call and response**: solista vs coro is the defining device (Santa Cruz's landós). A typical
  form (Toro mata, Hnos. Santa Cruz): **Intro 8 → [Estribillo/coro 8 + Estrofa/solo 8] ×3–4 →
  Interludio 12 → final open "pregón"** (54 bars of solo/coro exchange) → fade or corte.
- **Typical starts**: (1) guitar riff alone 2–4 bars, then cajón (with a corte) and bass;
  (2) a-cappella coro line with cajón repiques in the gaps (Demera's "Negra presuntuosa").
- **Typical ends**: the pregón fades, or a unison corte on i after rem.2, or the riff alone, ritardando.
- **Shouts and jaleo**: landó is sung, not shouted. Keep interjections soft and sparse:
  "¡Ahí nomá!", "¡Eso!", "¡Uy!", "¡Ay, ay, ay!" (or the "ayayay" inserted into verses that
  Santa Cruz describes for criollo forms). Hums and "mmm" answers in the coro work. "¡Toma que toma!"
  is a flamenco/Cuban flavour, not typically Afro-Peruvian, so use it only as a deliberate
  crossover.
- **Pase** (short transition): the guitar riff alone for 1–2 bars, or a unison corte
  (`rem.2`), between estribillo and estrofa.

### 1.8 P2, autoharp and hang in landó (without breaking the style)
```
# grid 12
P2.bongos     MMH MMH MMH MMH | MH. MH. MH. MH.   # [S rhythm] Samba malató bongó (pitches approx.)
P2.shaker     X.x X.x X.x X.x                     # [A] soft, dotted-quarter accents
P2.djembé     B.. .TT ... .TT                     # [A] tumbadora role: answers the cajón, no slaps
autoharp      A-- --- A-- ---                     # [A] rolled chord on beats 1 and 3 (pad)
autoharp.v    d.u dd. ud. ud.                     # [A] soft archetype-rhythm strum (2nd-guitar role)
```
```
# grid 12   hang tokens (D minor: Dm–A7)
hang.Dm       D3 . A3 . D4 F4 . A3 D3 . E4 F4     # [A] follows cajón.A attack points
hang.A7       A3 . E4 . G4 A4 . E4 A3 . G4 E4     # [A] no C over A7
```
- **Cuíca**: avoid as a groove instrument, because it codes "samba" instantly. At most, one
  long low glide (`L`) at a section end.
- **Hang**: ideal for landó-canción verses, but only in Dm/F (or with a re-harmonisation into Dm).
- Keep P2 **under the cajón**: landó's percussion is cajón-led. P2 joins in choruses or pregón,
  not in the first verse.

### 1.9 Landó groove, assembled
```
# grid 12   verse (landó-canción, ♩. ≈ 70, Dm–A7 one chord per bar)
cajón       B.T .BB .TB .TB
gtr         1.2 32. 32. 21.
bass        1-- --- 5-- ---
autoharp    A-- --- A-- ---
P2.shaker   X.x X.x X.x X.x
```

---

## 2. FESTEJO (Afro-Peruvian, fast)

### 2.1 Identity
The best-known Afro-Peruvian genre. It is fast, festive and syncopated, with dancing and
call-and-response choruses. It was standardised in the 1970s by **Perú Negro**, who raised tempo
and percussion intensity, used several cajones, and added Cuban congas, bongó and cencerro
(Descalzo 2019). Early festejos (Cumanana 1964: "No me cumben", "Ingá", "Cumanana") already had
cajita, quijada, cajón, guitar and bass, but a different cajón pattern. Alcázar and Alegría agree
there is **no constant clave**: the cajón and the singers lead, and the guitar accompanies
"spontaneously".

### 2.2 Meter and tempo
- Written in **12/8** (Alcázar: "all compositions and percussion are written in 12/8"; Descalzo;
  Morales) **or 6/8** (Thomann; many popular sources). One 12/8 bar = two 6/8 bars, so this file
  uses 12/8. Count the **dotted quarter** as the beat.
- Tempo: **♩. ≈ 110–115** as a didactic average (Elías Llanos & Wolff), with a practical range
  of about 100–130 (by ear). Eva Ayllón's "Raíces del festejo" is about 10 bpm faster than
  Perú Negro's "Ollita" (Descalzo).
- Listening references (tempos not measured unless stated):
  - Perú Negro, "Ollita no ma" (title as given by Descalzo; album *Sangre de un don*). Cajón
    "ollita" base, congas in rumba ternaria, bongó solo.
  - Eva Ayllón, "Raíces del festejo / Le dije a papá". Guitar+bass unison riff, coros
    "para pa para pa", a batá percussion break.
  - Perú Negro, "Mayoral" ("Saca tu machete, Cipriano"). No guitar, a campana llamada,
    responsorial coro.
  - Perú Negro, "Alcatraz" (alcatraz-family festejo): SongBPM lists 127, probably the ♩. value.
  - Nicomedes Santa Cruz y Cumanana, "No me cumben" / "Ingá" (1964): the older, lighter sound
    with cajita and quijada.
  - Eva Ayllón, "Azúcar de caña": festejo per reviews.

### 2.3 Cajón
Core feature (Descalzo): **the graves fall on beats 1 and 2 of the bar** (eighths 1, 3, 4, 5),
with "an impulse toward beat 1" (graves on 11–12). The **2nd eighth of each beat** is accented by
the agudos and by the coro ("ey, ey, ey, ey").
```
# grid 12   (12/8)
cajón.A     B.B BB. TT. TBB      # [S] "base típica de festejo", Eva Ayllón "Raíces del festejo", bar 1
cajón.A2    B.B BB. .BB BBB      # [S] same, bar 2 (bass answer)
cajón.A3    B.B BB. TT. T.T      # [S] same, bar 3
cajón.A4    TTB BB. TTB BBB      # [S] same, bar 4 (busiest)
cajón.M     TSB BB. TT. .BB      # [S] Perú Negro "Mayoral" (more agudos; S = ⊗ stroke)
cajón.M2    TTB BB. TT. .BT      # [S] Mayoral, next bar
cajón.M3    TTB BB. TT. T..      # [S] Mayoral, phrase end
```
```
# grid 24
cajón.O     BBB.B. B.T... B.T.B. B.T...   # [S] Perú Negro "Ollita": verse base (16th pick-up in beat 1)
```
```
# grid 12
cajón.Ch    BBB BTT TT. TT. | BBB BTT TTT TT.   # [S] Ollita chorus variant (flagged estribillos)
```
A 4-bar cycle to loop: **A, A2, A3, A4** (the transcription is exactly that).

**Llamadas, remates, cortes** (section markers)
```
# grid 12
llam.O      TT. TTT TT. TTT | TT. TTT TT. TTT   # [S] Ollita intro llamada (agudos only, 2 bars) before the base
llam.M      ... ... .TS TST                     # [S] Mayoral cajón entry: pick-up in agudos
rem.M       ... .BB BBB BB.                     # [S] Mayoral: graves run that lands on beat 1 of the estrofa
corte       ... ... .S. S..                     # [S] Eva Ayllón guitar+bass "corte" before each new section; whole band plays it
fin         S.. ... ... ...                     # [A] final unison hit (after llam.O or corte)
```

### 2.4 Cajita, quijada, campana → band
- **Campana / cajita line** `[S]` (Morales Chart 27 = the Mayoral campana in Descalzo):
  ```
  # grid 12
  bell        X.X XX. XX. X.X     # rhythm (Morales "festejo cowbell"; a variant of the 6/8 bell)
  bell.LH     L.H HH. LL. H.H     # Mayoral pitches (L low, H high)
  snare       R.R RR. RR. R.R     # → P1 snare rim (cajita substitute), only when P1 is NOT on cajón
  P2.bongos   H.M MM. HH. M.M     # → P2 bongos (hembra=low, macho=high)
  autoharp    d.d dd. dd. d.d     # → autoharp damped chord chops (very effective)
  ```
  Morales also gives a "fuga" bell (same rhythm, different high/low distribution) for choruses
  and the final fuga.
- **Mayoral campana llamada** `[S]` (before the estribillo): `.XX .XX X.X X..` (`# grid 12`).
- **Quijada** (struck rattle and rasp, especially in festejo and son de los diablos per
  Afropop) → güiro: `t` = strike, `L` = rasp. Use it **sparsely**: a hit on beat 1 every 2 bars
  and a rasp into section changes. `t.. ... ... ... | t.. ... L-- ...` `[A]`. Because P1 owns
  both cajón and güiro, the quijada only sounds (a) in an intro or break, or (b) in a section
  where **P2's djembé covers the cajón base** (djembé `B`/`T`/`S` stand in for cajón `B`/`T`/`S`).

### 2.5 Guitar
```
# grid 12
gtr.rasgA   dU. dU. dU. dU.      # [A] accent on the 2nd eighth of each beat (the festejo accent)
gtr.rasgB   D.D DD. xx. xUU      # [A] locks to cajón.A: chords on its graves, chops on its agudos
gtr.punteo  .43 434 343 434      # [S rhythm] Ollita "punteo agudo": constant 8ths after a downbeat rest
gtr.corte   ... ... .D. D..      # [S] Eva Ayllón corte (with bass)
```
- Riffs: festejos often open with a **melodic guitar+bass unison riff** of 4 bars, repeated with
  the cajón added (Eva Ayllón), and the second guitar plays counter-melodies (Ollita). The riff is
  free, built from the key's scale on the 12/8 grid. Land on eighths 1, 3, 4, 5 or 11, 12 to agree
  with the cajón.
- **Ukulele works well** for rasgA, rasgB and punteo (high, bright). The festejo guitar is less
  bass-string-centred than the landó guitar.

### 2.6 Bass
```
# grid 12
bass.A      1-5 -8- -5- -<-      # [S rhythm] Perú Negro "Mayoral" intro: attacks 1 3 5 8 11 (degrees [A])
bass.B      1.5 58. ... .5>      # [A] doubles the cajón graves (1 3 4 5 | 11 12)
bass.C      ... ... .1. 5..      # [S rhythm] with the corte
```
In "Raíces del festejo" the bass locks with the congas "as one instrument". In "Mayoral" it
returns to the bass.A figure whenever the percussion gets freer (choruses).

### 2.7 Harmony, melody, vocals, form
- **Harmony**: short cycles, **I–V7** or **i–V7**, sometimes **I–IV–V7**. Major and minor are
  both common, unlike landó, which is almost always minor. Harmony is simple so the rhythm and the
  coro carry the song. A new section can change harmony over the same rhythm (Eva Ayllón strophe B).
- **Coros**: vocables are central: "para pa para pa", "papa pa pa pa pa", "ey ey ey ey" (on the
  2nd-eighth accent). **Exact-repeat response** is the norm: in Mayoral the soloist sings
  "Saca tu machete, Cipriano" and the coro answers "Saca tu machete"; then "Afila tu lampa, José"
  → "Afila tu lampa". The response repeats the **first half** of the call.
- **Shouts**: "¡Ahí nomá!", "¡Eso es!", "¡Sabroso!", "¡Ahora!", "¡Toma!", "¡Uy!" and the dancers'
  "¡Wepa!" (pan-Caribbean). Use them over cortes and llamadas.
- **Form** (Descalzo's transcriptions): **Intro (riff, then llamada, then base, 8–12 bars) → Coro
  or vocables 8 → Estribillo (call/response) 16 → Estrofa 8 → ... → percussion section (bongó or
  cajón solo, or a break into another groove, 12–20 bars) → final estribillo/montuno or "fuga"
  (repeated call/response, fuga bell) → coda/corte.** Every change is announced by the **corte**
  or a **llamada**.
- **Start**: guitar(+bass) riff alone, a corte, then the cajón joins (`llam.O` or `llam.M`).
  **End**: the last estribillo repeats, then `corte` → `fin` on I. Or a cajón remate (`rem.M`)
  into a unison hit.

### 2.8 P2, autoharp, hang in festejo
```
# grid 12
P2.bongos    SM. SM. SM. SM.      # [S rhythm] Mayoral bongó: marks "la tierra" (each beat) on the high head
P2.bongos.2  H.M MM. HH. M.M      # [S] bell line on bongos (see 2.4)
P2.djembé    TTB Tgg ggB Tgg      # [S rhythm, strokes approx.] two-conga "chacha lokafun" adaptation (Mayoral)
P2.shaker    xXx xXx xXx xXx      # [A] accent the 2nd eighth
autoharp     d.d dd. dd. d.d      # [A] bell-rhythm chops (choruses); verses: A-- --- A-- ---
```
```
# grid 12   hang tokens (sparse, on the 2nd-eighth accents; Dm or F)
hang         . D4 . . F4 . . A4 . . G4 .     # [A]
```
- Bongos are idiomatic (Perú Negro): they mark the beat with accents on the high head and
  improvise (quinteo) in percussion sections. A **bongo solo section** is authentic.
- **Cuíca**: no.
- **Hang**: optional and decorative. Festejo's identity is percussive, so drop the hang in full
  choruses.

---

## 3. Switching landó → festejo inside one song

**Ratio rule.** Festejo ♩. ≈ 1.5 × landó ♩. (landó-canción 70 → festejo 105; 74 → 111). The
landó's own **6/4 reading** (quarter = 2 eighths) is exactly the new dotted quarter. That gives a
clean **metric modulation**: *old quarter = new dotted quarter* (3:2).

**Option A: metric modulation (recommended, seamless).** In the last landó bar, eighths 5–12 play
four even quarter-pulses. These are the four beats of the first festejo bar's count-in at the new
tempo.
```
# grid 12   last landó bar (pivot), ♩. = L
cajón       B.T .B. B.B .B.      # [A] landó beat 1, then 4 quarter hits = new festejo beats
bass        1-5 -1- 5-1 -5-      # [A] bass.C (hemiola), last 4 attacks = new beats
P2.shaker   X.x .X. X.X .X.      # [A] accents land on eighths 5 7 9 11 → the new pulse
gtr         D.u .D. D.D .D.      # [A] same accents, full chords
# next bar: festejo at ♩. = 1.5 × L, start with cajón.A (or llam.O over 2 bars if a bigger lift is wanted)
```
The singer can phrase the last landó line in quarters (6/4) so that the modulation is heard as an
acceleration of the same pulse.

**Option B: break and llamada (most traditional sound).** The landó ends with `rem.2` (a unison
corte on 1, then silence). The cajón alone plays `llam.O` (2 bars of agudos) **at the new tempo**.
The band enters on festejo `cajón.A` with the guitar `corte` on the bar before the coro. This
matches how festejos open: a riff or corte, then a llamada, then the base.

**Option C: same tempo, pattern swap.** Only for small contrasts: landó-danza ♩. ≈ 90–100 →
festejo ♩. ≈ 100. It keeps the click, but the chorus lift is weaker.

**Back to landó** (festejo → verse 2): `corte` + `fin`, then the guitar bordón riff **alone** for
1–2 bars at the landó tempo. This is the landó's own typical opening, so it reads as "new section".

**Applied: a 4/4 pop anthem at ≈ 107 bpm in F♯ major** (tempo and key from SongBPM; verify by ear)
- Choruses, festejo: ♩. = 107 (the original quarter becomes the dotted quarter; one 4/4 bar = one
  12/8 bar).
- Verses, landó: ♩. ≈ 71 (= 2/3 × 107, landó-canción range). Option A pivot into each chorus.
- Key: **F major** (−1 semitone) makes the hang (D Kurd = F major notes) and the autoharp (F, Bb,
  C, C7, Dm, Gm, Am) fully usable. For a darker landó colour, **re-harmonise the verses around Dm
  (vi) with A7 as dominant**: Dm–A7 is pure landó i–V7. Then go to F major in the festejo chorus.
- Rhythm transfer: straight-8th syllables → long-short (♩♪) pairs; dense lines → three eighths
  per beat; chorus hooks start on the **2nd eighth** of the beat for the festejo accent.

---

## 4. Style cards

Each card lists its fields in this order: meter and tempo · feel · band setup · grids · harmony ·
vocals and form · listening references. Grid tags apply as in section 0.

### 4.1 Vals criollo (Peruvian waltz)
- **Meter / tempo**: 3/4 with a superposed 6/8. ♩ ≈ 120 (up to 180) (Pacheco 2018). Elías
  Llanos gives ♩. ≈ 75–85, the same range.
- **Feel**: guitar *tundete* ("tun" = bass, "de-te" = chord) and cajón: the cajón graves mark
  beats 2–3 of 3/4 while the agudos mark the 6/8.
- **Band**: P1 cajón · P2 shaker (light) or tacet · guitar essential (tundete + bordones) ·
  autoharp = 2nd guitar (arpeggio or pinched chords) · bass · hang intro only.
```
# grid 6   (3/4, 8ths, spaced per quarter)
cajón        T. BT B.        # [S] basic (Hugo Bravo via Pacheco): agudo 1 & 4 (6/8), grave 3 & 5 (3/4 beats 2-3)
cajón.v1     TT BT B.        # [S] two agudo 8ths on beat 1
cajón.v2     TT BT BT        # [S] + agudo on the last 8th
cajón.v3     TT BT BB        # [S] two graves on beat 3 ("more dramatic")
gtr MIXED    1- d. d.        # [S] tundete: bass rings on 1, staccato chords on 2 and 3 (fallback strum: D. d. d.)
gtr.v MIXED  14 d4 d4        # [S] Carlos Hayre: high "pedal" note on every offbeat
bass         1- .. 5.        # [A]
bass.run     1. 3. 5. | 6. 5. >.   # [A] bordón run between phrases (guitar or bass)
autoharp     A. d. d.        # [A]
```
- **Harmony**: major or minor. I–IV–V7 / i–iv–V7 with secondary dominants (V7/IV, V7/V),
  relative-key moves between parts, chromatic descending *bordones* into cadences.
- **Vocals / form**: solo or duet in thirds (primera y segunda voz). Strophic, with a guitar intro
  and guitar runs between lines. Ends on a guitar run and a hit on I.
- **Listen**: Chabuca Granda, "La flor de la canela". Los Morochucos, "Alma, corazón y vida".
  Óscar Avilés (guitar).

### 4.2 Marinera limeña / zamacueca
- **Meter / tempo**: 6/8 with a 3/4 hemiola. ♩. ≈ 65–100. The first three parts are slow, the
  resbalosa is a little faster, and the fuga is fastest (Santa Cruz).
- **Feel**: the same "family" accent logic as vals, zamba and chacarera: agudos on the dotted
  quarters and graves on beats 2–3 of 3/4, plus palmas.
- **Band**: P1 cajón · P2 palmas (hands; notate like a shaker) · guitar essential (it *calls* the
  cajón) · autoharp chords · bass light · hang no.
```
# grid 6   (6/8)
cajón        T.B TB.         # [C] family base (same accent logic as vals; not a marinera-specific transcription)
cajón.v      TgB TBB         # [A]
redoble      BBB B..         # [S] answer to the guitar's opening bordón: "3 or 4 strokes at the centre"
palmas       X.. X..         # [A] dotted quarters (or X.X .X. for the 3/4 layer)
gtr          D.u Du.         # [A]
bass         1.. 5..         # [A]
```
- **Harmony**: major or minor, but **the whole marinera keeps one mode** (never start in major
  and end in minor). Simple I–IV–V7.
- **Form** (Santa Cruz): guitar bordón calls → cajón redoble → palmas → sing after 8–12 bars.
  **Primera, segunda, tercera de jarana** (the tercera ends with a *remate*) → 12–16 bars of
  guitar+cajón → **resbalosa** (puesta y contestación; ends repeating the last words + "ja ja") →
  8–12 bars → **fuga(s)**, each preceded by a **llamada**. The final fuga closes with the formula
  "Para gusto ya'stá bueno". Duets sing in two voices (A melody, B "segunda"). Shouts: "¡Jarana!",
  "¡Ahí nomá!". "¡Aro, aro!" is the pause call best known from the Chilean cueca, so treat it as
  borrowed.
- **Listen**: Abelardo Núñez, "La concheperla". Augusto Ascuez & Nicomedes Santa Cruz (canto de
  jarana). Perú Negro (zamacueca).

### 4.3 Cumbia (Colombian)
- **Meter / tempo**: 2/4 (cut time). 2/4 beat ≈ 85–110.
- **Feel**: a steady guacharaca "chaaa-ka-ka", llamador on the offbeat, an improvising tambor
  alegre, a shuffling maraca.
- **Band**: **P1 güiro (guacharaca)** · P2 bongos (llamador + alegre fills) or djembé (tambora +
  alegre) · guitar or uke offbeat · autoharp offbeat or pad · bass · hang fills (Dm/F only).
```
# grid 16   (two 2/4 bars)
güiro        L.ss L.ss L.ss L.ss     # [C] guacharaca
P2.bongos    ..M. ..M. ..M. ..M.     # [C] llamador on every offbeat 8th; add H fills as tambor alegre
P2.djembé    B... T.T. B..T .TS.     # [A] tambora/alegre composite
shaker       x.X. x.X. x.X. x.X.     # [A] maraca (if P2 is free)
gtr/uke      ..U. ..U. ..U. ..U.     # [C] offbeat upstroke (or ..x. chops)
autoharp     ..d. ..d. ..d. ..d.     # [C]
bass         1... 5... 1... 5...     # [C]
bass.v       1..1 5... 1..1 5..>     # [A]
```
- **Harmony**: I–V7 vamps, I–IV–V7. Minor cumbias use i–iv–V7.
- **Vocals / form**: verse/coro call and response, instrumental (gaita or accordion) breaks.
  Shouts "¡Wepa!", "¡Epa je!", "¡Sabroso!".
- **Listen**: Los Gaiteros de San Jacinto (traditional). "La pollera colorá" (Wilson Choperena /
  Juan Madera). Totó la Momposina.

### 4.4 Chicha (Peruvian / Amazonian cumbia)
- **Meter / tempo**: 2/4. 2/4 beat ≈ 90–110.
- **Feel**: a cumbia pulse with güiro and timbales or bongos. Up to three electric guitars play
  Andean-pentatonic melodies (often in parallel), with offbeat rhythm guitar, Farfisa/Moog organ
  with echo, and surf/rock solos (Wikipedia, Peruvian cumbia).
- **Band**: **P1 güiro** · P2 bongos (martillo) · **guitar = lead melody** (the uke can only do
  the offbeat) · autoharp = organ-like pad or offbeat · bass · hang = pentatonic hooks
  (Dm pentatonic = D F G A C, all on the Kurd).
```
# grid 16
güiro        L.ss L.ss L.ss L.ss     # [C]
P2.bongos    MpmpMpHp MpmpMpHp       # [C] Cuban-style martillo (Hijos del Sol use bongó + cencerro)
gtr.rhythm   ..x. ..x. ..x. ..x.     # [C] offbeat chop
gtr.lead     1.3.4.3. 2.3.4.3.       # [A] picked broken-chord line; real chicha leads are melodies (write as tokens)
autoharp     ..d. ..d. ..d. ..d.     # [A]
bass         1... 5... 1... 5.>.     # [A]
```
- **Harmony**: mostly minor (huayno-derived), i–VII–III–V7. Andean pentatonic melodies.
- **Vocals**: plaintive lead, unison coros, spoken shout-outs/dedications over intros `[C]`.
- **Listen**: Los Hijos del Sol, "Cariñito". Juaneco y su Combo, "Mujer hilandera". Los Mirlos,
  "La danza de los Mirlos". Los Destellos, "Elsa".

### 4.5 Vallenato
- **Aires**: **paseo** (2/4, 2/4 beat ≈ 95–125, binary), **son** (2/4, slow ≈ 70–90, heavy
  bass), **merengue** (6/8, same meter as puya but slower, ♩. ≈ 90–120), **puya** (6/8, fast,
  ♩. ≈ 130–160). The binary/ternary split is from the Toloza and Unireformada sources. The
  tempos are approximate.
- **Band**: **P1 güiro (guacharaca)** · P2 djembé or bongos (caja vallenata) · autoharp or uke =
  accordion chord role · guitar = arpeggiated "punteo" (modern romantic vallenato) · bass essential
  · hang no.
```
# grid 16   paseo
güiro        L.ss L.ss L.ss L.ss     # [A]
P2.djembé    B..T .TS. B..T .TS.     # [A] caja
bass         1..1 ..5. 1..1 ..5.     # [A] 3-3-2 figure
autoharp     ..d. ..d. ..d. ..d.     # [A]
gtr          1.3. 4.3. 1.3. 4.3.     # [A]
# grid 6    merengue / puya (6/8)
güiro        L.s L.s                 # [A]
P2.djembé    B.T .TS                 # [A]
bass         1.. 5..                 # [A]
```
- **Harmony**: I–IV–V7 major, diatonic. The accordion plays intros and *contracantos*.
- **Vocals**: storytelling verse, *piquería* (improvised verse duels), spoken *saludos*, the
  shout **"¡Ay hombe!"**.
- **Listen**: Rafael Escalona, "La casa en el aire" (paseo). "La gota fría" (Emiliano Zuleta;
  merengue; Carlos Vives version).

### 4.6 Currulao (Colombian Pacific)
- **Meter / tempo**: 6/8 (often read as 12/8). ♩. ≈ 95–125 `[A]`.
- **Feel**: a marimba de chonta ostinato (bordón + tiple hands), bombo golpeador (head + wood),
  cununos (macho/hembra), guasá (shaker), and an overlapping call-and-response.
- **Band**: P1 cajón (bombo: `B` head, `S` = wood/rim) **or** hang (marimba role) · P2 bongos
  (cununos) or shaker (guasá) · **hang or autoharp = marimba** · guitar/uke = marimba-like picking
  · bass.
```
# grid 6   (6/8)
cajón        B.S .SB                 # [A] bombo golpeador
P2.bongos    M.H MMH                 # [A] cununo
shaker       Xxx Xxx                 # [A] guasá
autoharp     123 432                 # [A] marimba arpeggio
bass         1.. .5<                 # [A]
hang         D3 A3 D4 F4 A3 D4       # [A] marimba-style ostinato (Dm)
```
- **Harmony**: I–V7 alternation, pentatonic and modal marimba lines.
- **Vocals**: a *glosador/glosadora* leads and *respondedoras* (women's chorus) answer and
  overlap. This **fits the band's 2 women + 3 men**.
- **Listen**: Grupo Bahía. Herencia de Timbiquí. Festival Petronio Álvarez recordings.

### 4.7 Bambuco (Colombian Andes)
- **Meter / tempo**: written in **3/4 or 6/8, a long debate**. Spanish Wikipedia says it is
  written in 6/8 and playing it in 3/4 "turns it into a waltz". ♩ ≈ 100–140 `[A]`.
- **Feel**: melodies start off the beat. Guitar "golpe" with *bajos y contestantes*, a tiple
  *tendido* behind, and the bandola carrying the melody.
- **Band**: guitar (golpe) · **uke = tiple** · autoharp = chords or bandola-like arpeggio · bass ·
  P1 shaker or very light cajón · P2 shaker or tacet · hang melodic fills.
```
# grid 6   (3/4)
gtr MIXED    1. xU d.                # [A] bass, chop, chord
uke          Du xu Du                # [A] tiple tendido
bass         1- .5 >-                # [A] beat-3 approach note leads into the next chord (real bambuco often anticipates the next root here)
cajón        B. T. TS                # [A]
```
- **Harmony**: major or minor, I–IV–V7, moves to the relative key, colonial-Andean cadences.
- **Vocals**: the classic **duet in thirds** (dueto bambuquero).
- **Listen**: "La guaneña" (traditional). Pelón Santamarta, "Antioqueñita". Garzón y Collazos.

### 4.8 Joropo llanero (Colombia / Venezuela)
- **Meter / tempo**: 3/4 with 6/8 superposed ("the hemiola is the rule"). **Pasaje ♩ ≈ 152**,
  **golpe ♩ ≈ 176–192** (Spanish Wikipedia).
- **Feel**: arpa llanera (bass and melody), cuatro rhythm with apagados, virtuosic maracas.
- **Band**: **autoharp = arpa** · **uke = cuatro** · **P2 maracas (shakers, both hands)** ·
  bass · P1 tacet, very light cajón, or hang in pasajes · guitar takes the cuatro role if there is
  no uke.
```
# grid 6   (3/4)
uke(cuatro)  DU DU xU                # [A] apagado on beat 3 (accent placement varies by golpe)
P2.maracas   Xx xX xx                # [A]
autoharp     12 34 32                # [A] arpa-style arpeggio
bass         1. .5 .1                # [A]
cajón        B. T. T.                # [A] optional
```
- **Harmony**: pasaje = free, 2 parts. **Golpes** have fixed cycles: *seis por derecho* (major),
  *pajarillo* (minor), *gaván* (both).
- **Vocals**: high, strong *recio* singing. *Contrapunteo* / zumba que zumba (sung duel) over a
  golpe. Llanero *gritos*.
- **Listen**: "Alma llanera" (Pedro Elías Gutiérrez). "Pajarillo" (traditional golpe).

### 4.9 Samba
- **Meter / tempo**: 2/4. 2/4 beat ≈ 90–110 (samba de roda, pagode); ≈ 130–145 (samba-enredo).
- **Feel**: two layers (Ginga). The **surdo** plays quarters with the **accent on beat 2**. The
  **tamborim** plays syncopated 16ths. Chords anticipate by one 16th.
- **Band**: P1 cajón (surdo + pandeiro composite) **or** snare (caixa) · **P2 cuíca** (signature)
  or bongos (tamborim) or shaker (ganzá) · **uke = cavaquinho** (excellent) · guitar = thumb on
  the surdo, fingers on the tamborim · autoharp comp on the tamborim rhythm · bass.
```
# grid 16   (two 2/4 bars)
cajón.surdo  g... B... g... B...     # [S] Ginga: quarters, accent on 2 (B), beat 1 muted (g)
cajón.pand   ggTg BgTg ggTg BgTg     # [A] pandeiro-ish composite
tamborim.a   X.X. .X.X ...X .X..     # [S] Ginga example a → P2 bongos M, or P1 snare R
tamborim.b   .X.X ..X. X.X. .X.X     # [S] Ginga example b (offbeat start)
P2.cuíca     L..H .H.. L..H .H..     # [A]
shaker       xxxX xxxX xxxX xxxX     # [A] ganzá (some players accent the 1st 16th instead)
uke(cavaco)  DuDu dUdU dudU dUdu     # [A] 16ths, accents on tamborim.a positions
gtr.thumb    1... 5... 1... 5...     # [S] Ginga: thumb = surdo (drop it if the bass covers)
gtr.fingers  d.d. .d.d ...d .d..     # [S] fingers = tamborim.a
autoharp     d.d. .d.d ...d .d..     # [A]
bass         1..5 5... 1..5 5...     # [C] "dum-da-DUM"
```
- **Harmony**: ii–V–I, secondary dominants, passing diminished chords, many minor sambas.
  Anticipate chord changes by a 16th.
- **Vocals**: syncopated melodies that rarely start on 1. Coro refrains, partido-alto call and
  response, "laiá laiá" vocables.
- **Listen**: Cartola, "O mundo é um moinho". Zeca Pagodinho. Jorge Ben Jor, "Mas que nada"
  (samba-rock).

### 4.10 Bossa nova
- **Meter / tempo**: 2/4 (or 4/4). 2/4 beat ≈ 55–75 (= 110–150 in most 4/4 BPM listings).
- **Feel**: samba made intimate: the guitar thumb is the surdo, the fingers syncopate, the voice
  is quiet.
- **Band**: guitar essential (not uke) · P1 snare rim clicks (R) or brushes (x) · P2 shaker,
  very soft · autoharp very sparse (it has no maj7 or m7 chords) · **hang = colour** · bass.
```
# grid 16
gtr.fingers  d..d ..d. ..d. .d..     # [C] bossa "clave" (attacks 1 4 7 11 14)
gtr.thumb    1... 5... 1... 5...     # [C] thumb (or bassist)
snare        R..R ..R. ..R. .R..     # [C] cross-stick on the same clave
P2.shaker    xxxx xxxx xxxx xxxx     # [C] soft 16ths
bass         1..5 -... 1..5 -...     # [C]
autoharp     A... .... A... ....     # [A] one rolled chord per bar, at most
```
- **Harmony**: maj7, m7, 7(9), m7b5, dim, chromatic ii–V. Re-voice to autoharp triads/7ths, or
  leave the autoharp out.
- **Vocals**: soft unison or close harmony, no shouts.
- **Listen**: João Gilberto, "Chega de saudade" (1959). Getz/Gilberto, "Garota de Ipanema" (1963).

### 4.11 Baião
- **Meter / tempo**: 2/4. 2/4 beat ≈ 90–130.
- **Feel**: a syncopated low **zabumba 3-3-2** (mallet on the top head), the bacalhau (stick on
  the bottom head) on offbeats, triangle 16ths, and mixolydian melodies with accents on the 4th
  eighth.
- **Band**: **P1 cajón = zabumba** (B mallet, S bacalhau) · P2 shaker = triangle · guitar or uke
  on the zabumba rhythm · autoharp same · bass · hang works (the D Kurd = C mixolydian notes).
```
# grid 16
cajón        B..B ..S. B..B ..S.     # [S] Ginga zabumba (3-3-2; S = bacalhau)
cajón.v      B.SB g.SB B.SB g.SB     # [S] Ginga combination: accented bacalhau offbeats + mallet 1, 4, 8
P2.shaker    xxXx xxXx xxXx xxXx     # [C] triangle: open (X) on the "&"
gtr/uke      D..D ..U. D..D ..U.     # [C]
autoharp     D..D ..u. D..D ..u.     # [A]
bass         1..5 ..8. 1..5 ..8.     # [C]
```
- **Harmony**: one-chord dominant-7 vamps, I7–IV7, C6–G7. Mixolydian (b7) and lydian-dominant
  (#4) melodies.
- **Vocals**: unison or thirds, *aboio*-like calls, repeated-note melodies.
- **Listen**: Luiz Gonzaga, "Baião" (1946), "Asa branca", "Juazeiro".

### 4.12 Xote / forró
- **Meter / tempo**: 2/4. 2/4 beat ≈ 70–95 (xote is the slow, swaying forró).
- **Band**: like baião (P1 cajón = zabumba, P2 shaker = triangle). The accordion role goes to
  the autoharp or uke.
```
# grid 16
cajón        B..B B.S. ..S. B.S.     # [A] xote zabumba "dum..da-dum" with bacalhau
P2.shaker    x.X. x.X. x.X. x.X.     # [A] triangle, swung
gtr/uke      D..D D.u. ..u. D.u.     # [A]
bass         1..5 5... 1..5 5...     # [A]
```
- **Harmony / vocals**: I–IV–V7, mixolydian touches, love-song lyrics, unison or thirds.
- **Listen**: Luiz Gonzaga, "Xote das meninas". Dominguinhos.

### 4.13 Maracatu (de baque virado)
- **Meter / tempo**: 2/4 or 4/4. 2/4 beat ≈ 85–110. Heavy and processional.
- **Feel**: the **gonguê** (single bell) as timeline, a wall of **alfaias** (bass drums) with
  syncopated accents, snares (caixa/tarol) rolling, and a puxador answered by the coro.
- **Band**: P2 djembé or P1 cajón = alfaia · P2 bongos = gonguê (or the autoharp chops it) ·
  P1 snare = caixa · bass doubles the alfaia · guitar or uke chords on the gonguê rhythm · hang no.
```
# grid 16
alfaia(djembé/cajón)  B... .B.. .B.. .B..   # [S] Ginga: strong 1, then 16th-offset hits
P2.bongos(gonguê)     H.M. H.M. HM.M H.M.   # [S] Ginga gonguê (H low, M high)
snare(caixa)          X.r. X.r. X.r. X.r.   # [A] buzz rolls between accents
bass                  1... .5.. .1.. .5..   # [A]
gtr/uke               D.U. D.U. DU.U D.U.   # [A] gonguê rhythm
```
- **Harmony**: major-chord arpeggio melodies, modal. Little harmonic motion.
- **Vocals**: *loas*: call by the puxador, answer by the coro.
- **Listen**: Nação Estrela Brilhante. Chico Science & Nação Zumbi, "Maracatu atômico".

### 4.14 Ijexá
- **Meter / tempo**: 4/4. ♩ ≈ 80–100 (Alfred's conga exercise uses ♩ = 85). It became a slower
  sung style in MPB from the 1970s (Gil, Caetano).
- **Feel**: an **agogô timeline**, lê and rumpi in dotted-8th + 16th, a rum with quarter / two-8ths.
  Swaying, devotional (Oxum).
- **Band**: P2 bongos (agogô line or lê/rumpi) **or** djembé (rum) · P1 shaker (agbê/caxixi)
  **or hang** (beautiful here) · guitar levada · autoharp soft rolled chords · bass on the rum
  rhythm.
```
# grid 16
agogô        XX.X .XX. X.X. X.X.     # [S] Cardoso 2006 via Silva & Madeira (rhythm); → P2 bongos (M/H, pitches [A]) or snare R
lê/rumpi     T..T T..T T..T T..T     # [S] → P2 bongos (M) or djembé T
rum          B... T.T. B... T.T.     # [S] → P2 djembé
P1.shaker    x.x. x.x. x.x. x.x.     # [A] agbê/caxixi
gtr.pick     1.1. 4.13 .1.1 4.13     # [S] Gil "Tartaruguê" levada (TUBS): thumb 1 3 7 10 12 15, fingers 5 8 13 16
bass         1... 5.5. 1... 5.8.     # [A] rum rhythm
```
- **Harmony**: I–IV, ii–V, modal vamps. Gentle, major-leaning.
- **Vocals**: hymn-like refrains in unison or thirds, call and response.
- **Listen**: Gilberto Gil, "Filhos de Gandhi". Vevé Calazans & Gerônimo, "É d'Oxum".

### 4.15 Chacarera (Argentina)
- **Meter / tempo**: 6/8 and 3/4 **superposed** (not alternating). ♩. ≈ 95–125 `[A]`.
- **Feel**: the **"dos-tres"**. Aro (rim) and guitar *chasquido* mark each dotted quarter (6/8,
  high register). Parche (head) and bass strings land on **beats 2 and 3 of 3/4** (low register).
  The main support is "tumbado" on beat 3 (Taján).
- **Band**: P1 cajón **or** P2 djembé = bombo legüero (`B` parche, `S` aro) · guitar rasgueo with
  chasquido (the uke works, thinner) · bass on the dos-tres · autoharp chops · hang no.
```
# grid 6   (6/8 written; 3/4 layer = eighths 1 3 5)
bombo(cajón) S.B SB.                 # [S principle, Taján/Ábalos] aro 1 & 4, parche 3 & 5
bombo.v      S.B SBB                 # [A]
gtr          xuU xDu                 # [S principle] chasquido 1 & 4; bass-string stroke on 3 (often up) and 5 (support)
bass         1.1 .5.                 # [A]
autoharp     x.d xd.                 # [A]
```
- **Harmony**: minor or major, i–iv–V7 / I–IV–V7, short phrases.
- **Form / vocals**: fixed dance form with intro, estrofas, estribillo and interludes. The second
  half repeats ("¡Se va la segunda!"). Shouts: "¡Adentro!", "¡Se va la segunda!", "¡Aura!".
  Duets in thirds.
- **Listen**: Atahualpa Yupanqui, "Chacarera de las piedras". "Añoranzas" (Julio A. Jerez).

### 4.16 Zamba (Argentina)
- **Meter / tempo**: 6/8 (with 3/4). Slow: ♩. ≈ 55–75 `[A]`.
- **Feel**: a stately handkerchief dance. The bombo is sparse and the guitar rasgueo gentle, or
  arpeggiated.
- **Band**: guitar (rasgueo or arpeggio) · P1 cajón (sparse bombo) · P2 tacet or shaker · autoharp
  arpeggio · bass · hang fine (in Dm/F).
```
# grid 6
bombo(cajón) B.. .S.                 # [A]
gtr          D.u Du.                 # [A] rasgueo
gtr.arp      1.3 4.3                 # [A] arpeggio version
bass         1.. 5..                 # [A]
autoharp     A.. .d.                 # [A]
```
- **Harmony**: minor or major, i–iv–V7, relative-major excursions.
- **Vocals / form**: two parts ("¡Se va la segunda!"), lyrical, duets in thirds.
- **Listen**: Mercedes Sosa, "Alfonsina y el mar". "Zamba de mi esperanza" (Luis Profili).

### 4.17 Candombe (Uruguay)
- **Meter / tempo**: 4/4 (some teach the piano drum in 2/4). ♩ ≈ 105–135 `[A]`.
- **Feel**: a cuerda of **chico** (timekeeper), **repique** (improviser, plays the *madera*
  clave on the shell) and **piano** (low base). The 3-2 clave is played in unison as the
  organiser (Mola).
- **Band**: P2 bongos = chico **or** djembé = piano · P1 cajón = repique + madera (S on the corner)
  · bass follows the piano · guitar chops · autoharp chops · hang no.
```
# grid 16
madera       X..X ..X. ..X. X...     # [S] Mola: "clave 3-2", the candombe clave → P1 cajón S or snare R
chico        .mMM .mMM .mMM .mMM     # [S rhythm] Mola: 16th rest + three 16ths per beat → P2 bongos
piano        B..T S... B..T S...     # [S approx.] Mola "piano en 2/4" (head, open, stick) → P2 djembé
bass         1..5 -... 1..5 -...     # [A] follows the piano
gtr          ..x. x.x. ..x. x.x.     # [A]
```
- **Harmony**: candombe-pop (Rada, Mateo, Roos) uses jazzy minor 7ths and I–vi–ii–V.
- **Vocals**: murga-style choral refrains, call and response.
- **Listen**: Rubén Rada. Jaime Roos, "Brindis por Pierrot".

### 4.18 Milonga (Argentina / Uruguay)
- **Meter / tempo**: 2/4. Milonga campera (slow) ≈ 60–80; milonga ciudadana ≈ 100–130.
- **Feel**: the **3-3-2** (habanera-derived) cell.
- **Band**: guitar (essential) · bass · P1 cajón (3-3-2) · P2 tacet or bongos · autoharp sparse ·
  hang fine in campera.
```
# grid 16
cajón        B..B ..T. B..B ..T.     # [C] 3-3-2
gtr          1..3 ..4. 1..3 ..4.     # [C] thumb 3-3-2 arpeggio
bass         1..3 ..5. 1..3 ..5.     # [C]
autoharp     d..d ..d. d..d ..d.     # [A]
```
- **Harmony**: I–V7, i–V7, often minor. *Payada* (improvised décimas) over a one- or two-chord cycle.
- **Listen**: Atahualpa Yupanqui (milonga campera). "Milonga sentimental" (Piana/Manzi).

### 4.19 Tango
- **Meter / tempo**: 4/4 (old guardia 2/4). Dance tangos ♩ ≈ 110–130.
- **Feel**: *marcato* (all four beats, accents on 1 and 3), the *arrastre* (drag into the beat),
  and the 3-3-2 for contrast (Piazzolla).
- **Band**: guitar or autoharp marcato · bass · P1 cajón **very** light or hang (tango is
  traditionally percussion-free) · P2 tacet · the uke is weak here.
```
# grid 16
gtr.marcato  D... d... D... d...     # [C] marcato in 4
gtr.332      D..D ..D. D..D ..D.     # [C] 3-3-2 (Piazzolla, "Libertango")
bass         1... 5..> 1... 5...     # [A] with an approach note (arrastre feel)
cajón        B... g... B... g...     # [A] only if needed
```
- **Harmony**: minor keys, i–iv–V7, diminished passing chords, chromatic bass.
- **Vocals**: dramatic, rubato, no shouts.
- **Listen**: Carlos Gardel, "Por una cabeza". Astor Piazzolla, "Libertango".

### 4.20 Huayno (Peru / Bolivia Andes)
- **Meter / tempo**: 2/4. 2/4 beat ≈ 100–140. The final *fuga* is faster.
- **Feel**: the **long-short-short** cell (8th + two 16ths) per beat.
- **Band**: **uke = charango** · guitar (strum + bass runs) · **autoharp = Andean harp** ·
  P1 cajón or shaker · P2 shaker or bongos · bass · **hang = pentatonic melody** (D minor
  pentatonic sits on the Kurd).
```
# grid 16
uke/gtr      D.DU D.DU D.DU D.DU     # [C]
cajón        B.TT S.TT B.TT S.TT     # [A]
shaker       X.xx X.xx X.xx X.xx     # [C]
bass         1.11 5.55 1.11 5.55     # [A] (or 1... 5... for a lighter feel)
autoharp     1.34 2.34 1.34 2.34     # [A] harp-like
```
- **Harmony**: minor pentatonic melodies. i–III–VII–i with V7 cadences and relative-major moves.
- **Form**: strophic repeats, then a **fuga** (a faster, contrasting closing section). This is a
  great structural device for a pop cover's outro.
- **Vocals**: high, bright, often female lead. Unison or thirds, falsetto cries.
- **Listen**: Daniel Alomía Robles, "El cóndor pasa" (fox incaico + huayno closing section).
  Max Castro.

### 4.21 Saya (Afro-Bolivian)
- **Meter / tempo**: 4/4 or 2/4, moderate. ♩ ≈ 90–110 `[A]`.
- **Feel**: bombos with a *cuancha* scraper and cascabeles. Women lead coplas answered by the
  chorus. Its rhythm differs from caporales (Wikipedia, sources thin).
- **Band**: **P1 güiro = cuancha** · P2 djembé = bombos · guitar or uke strum · autoharp ·
  bass · hang no.
```
# grid 16
güiro        L.s. L.s. L.s. L.s.     # [A] cuancha
P2.djembé    B..B ..B. B... B.T.     # [A]
gtr/uke      D.DU .UDU D.DU .UDU     # [A]
bass         1..1 ..5. 1... 5...     # [A]
```
- **Harmony**: simple major I–IV–V7.
- **Vocals**: **call and response led by women** (good for the two female voices).
- **Listen**: Afro-Bolivian saya from the Yungas (e.g. Movimiento Cultural Saya Afroboliviana).
  Los Kjarkas, "Llorando se fue" (the neo-folk "saya" label).

### 4.22 Caporales (Bolivia)
- **Meter / tempo**: 4/4 (brass-band march-dance). ♩ ≈ 90–110 `[A]`.
- **Feel**: created in 1969 (Estrada Pacheco brothers) from the saya character of the caporal.
  Brass, big bombo, and snare fills that cue the dancers' jumps.
- **Band**: **P1 snare** (tarola) · P2 djembé (bombo) · guitar or uke strum · autoharp = brass
  pads · bass · all voices in unison refrains.
```
# grid 16
snare        x.xx X.xx x.xx X.xx     # [A] fill-heavy; r rolls into section changes
P2.djembé    B... B.B. B... B.B.     # [A]
gtr/uke      D.DU D.DU D.DU D.DU     # [A]
bass         1... 5.5. 1... 5.8.     # [A]
```
- **Harmony**: major or minor, I–IV–V7. Anthem-like refrains.
- **Listen**: Los Kjarkas (caporales songs). Bolivian brass bands at the Carnaval de Oruro.

### 4.23 Son / salsa (Cuba): the mainstream choice for a European audience
Not South American, but what a French or European audience hears as "Latin": Buena Vista Social Club, salsa classes. It suits a 4/4 pop song at 95–115 with no re-timing.
- **Meter / tempo**: write it in the record's 4/4 at its tempo, on the **16th grid**. One record bar = two salsa bars (salsa at double speed: ♩ 105 ≈ salsa ♩ 210). The clave spans one record bar: son clave 3-2 = `X..X...X..X.X...`. Write the patterns so they agree with it, or leave the clave implied.
- **Feel**: the cowbell and the güiro drive; the bass **anticipates** (tumbao); the congas answer on the "4"; the coro calls and the lead answers (montuno).
- **Band**:
  - **P1 with sticks**: a stick on the snare's shell (the timbales' *cáscara* role) plus a cowbell clamped to the snare stand. This is one setup played with two sticks. P1 plays the güiro in drumless sections.
  - **P2**: bongos (offbeats while the player sings, martillo when not) or the djembé as a conga.
  - **Guitar**: the strum in the tres / guajeo role.
  - **Bass**: the tumbao, with `N` for the next chord's root played early.
  - **Hang**: solos and intros.
```
# grid 16   (one record bar = two salsa bars)
snare.shell  K.kk K.kk K.kk K.kk     # [A] "tch-ts-ts": stick on the shell, the güiro's rhythm (drops)
cowbell      ..O. ..O. ..O. ..O.     # [A] offbeats; montuno: o.O. o.O. o.O. o.O.
guiro        L.ss L.ss L.ss L.ss     # [A] drumless sections
djembe       B.S. B.TT B.S. B.TT     # [C] conga tumbao: bass, slap, bass, two open tones
djembe.pop   B... S..B B.B. S.B.     # [A] the record's kick/snare at the drop
bongos       ..M. ..M. ..M. ..M.     # [A] offbeats, easy to sing over
gtr          D.U. x.D. U.x. D...     # [A] the "figuetta" strum: down-up-mute twice, then a ringing down (3+3+2 in 8ths)
bass         1..5 ..1- ...5 ..N-     # [C] tumbao; the next bars start "-..5" (tied anticipation)
```
- **Form tools**:
  - a chorus sung over percussion only;
  - solos in turn (descarga): guitar as a tres, bass, hang, then the percussionists trading bars;
  - a montuno outro: the coro repeats the title and the lead ad-libs between;
  - the **cha-cha-chá** ending: hits on 4 and 4&, then 1.
- **Listen**: Buena Vista Social Club, "Chan Chan" and "El cuarto de Tula". Celia Cruz, "La vida es un carnaval".

---

## 5. Which style for which song

### 5.1 By song type

| original song | strong transplants | meter / tempo mapping |
|---|---|---|
| **Ballad** (4/4, 60–85 bpm, intimate) | landó-canción, bossa nova, zamba, vals criollo (slow), milonga campera, ijexá | landó: ♩ → ♩. at the same bpm (60–80). Bossa: 2/4 beat = original ♩. Zamba: ♩. ≈ bpm |
| **Mid-tempo anthem** (4/4, 90–120, big chorus) | **festejo**, cumbia/chicha, ijexá, baião, candombe, chacarera, saya/caporales, samba (pagode) | festejo: ♩ → ♩. at the same bpm. Cumbia/baião: 2/4 beat = ♩. Chacarera: ♩. = ♩ |
| **Fast rocker** (4/4, 130–180) | samba(-enredo), festejo (fast), joropo, puya vallenata, huayno/fuga, maracatu (half-time heavy) | samba: surdo = ♩. Joropo: 3/4 ♩ = ♩ (waltzify, 5.2). Maracatu: 2/4 beat = ♩/2 |
| **Verse-quiet, chorus-loud** | **landó → festejo** (section 3), huayno → fuga, zamba → chacarera, bossa → samba | use a 3:2 metric modulation or break + llamada. Bossa→samba = same 2/4 beat ×2 |
| **3/4 or 6/8 song** | vals criollo, bambuco, joropo, marinera, chacarera, zamba, currulao, landó/festejo | 6/8 bar = half a 12/8 bar. 3/4 → 6/8 by regrouping 2+2+2 → 3+3 |
| **Shuffle / swung 4/4** | landó, festejo, chacarera, currulao | swing 8ths are already ternary: one bar = one 12/8 bar |
| **Dark / minor** | landó, chicha, huayno, zamba, tango, milonga, maracatu | |
| **Bright / major** | festejo, samba, baião, cumbia, vallenato, joropo (seis por derecho), caporales | |

### 5.2 Meter conversion rules
1. **4/4 → 12/8** (landó, festejo, currulao, chacarera as 12/8): one bar → one bar. ♩ → ♩.
   Straight 8th pairs → **♩♪ (long-short)**, or **♪♪♪** when a lyric needs three syllables.
   16ths → 8ths. An "and" anticipation → the 3rd eighth of the previous beat. For festejo
   flavour, put hook syllables on the **2nd eighth**.
2. **4/4 → 6/8**: as rule 1, but one 4/4 bar → two 6/8 bars.
3. **4/4 → 3/4 ("waltzify": vals, bambuco, joropo)**: each **half bar → one 3/4 bar**. Two beats
   become half + quarter (long-short), so one 4/4 bar = two 3/4 bars, at a faster bpm
   (3/4 ♩ ≈ 1.5 × the original ♩ keeps the bar-pair duration). Alternatively, squeeze one 4/4 bar
   into one 3/4 bar by merging beats 3–4. That needs a melodic rewrite.
4. **4/4 → 2/4 Latin** (samba, cumbia, baião, huayno, milonga): one 4/4 bar → two 2/4 bars (the
   same 16-char grid) at the **same beat** (2/4 beat = original ♩). For a slow ballad, use
   **double-time**: one 4/4 bar → four 2/4 bars (2/4 beat = 2 × the original ♩), with the
   melody now in half-time over the groove (e.g. a 75-bpm ballad as a 150 samba).
5. **3/4 song → 12/8**: two 3/4 bars = one 12/8 bar, using the landó 6/4 reading. The original
   quarters become the 12/8 quarter-pairs (hemiola), which is very idiomatic in landó.
6. **Tempo sanity windows** (from the sources above): landó 58–100 (♩.) · festejo 100–130 (♩.) ·
   vals 110–180 (♩) · marinera 65–100 (♩.) · joropo 150–192 (♩) · samba 90–145 (2/4 beat) ·
   bossa 55–75 (2/4 beat) · cumbia 85–110 (2/4 beat). If a mapping lands outside its window, use
   rule 1's 3:2 alternative (♩. = 2/3 × ♩) or the double/half-time options.

### 5.3 Band-specific tips
- Pick the key for the **hang and autoharp first**: D minor / F major covers both. C, G, Am and
  Dm are fine for the autoharp alone.
- Styles that need **P1 on the güiro** (cumbia, chicha, vallenato, saya) lose the cajón. P2 then
  carries the drum role (djembé or bongos).
- Styles that free **P1 for the hang** (ijexá, currulao, zamba, bossa) suit intimate songs.
- Ukulele-first styles: samba (cavaquinho), joropo (cuatro), huayno (charango), bambuco (tiple),
  festejo. Guitar-first: landó (bordón), vals criollo (tundete), bossa, tango, chicha lead.
- Coros for the **2 women** (respondedoras, saya coplas, festejo vocables). Duets in thirds for
  vals, bambuco and zamba. Pregón or puxador calls for a man, answered by everyone.

---

## 6. Sources

Afro-Peruvian (landó, festejo, vals, marinera)
- Elías Llanos, F. & Wolff, D. (2019). "El landó y sus posibilidades en la guitarra." *Revista Vórtex* 7(3). Tempos, Samba malató/Toro mata transcriptions, landó-canción vs landó-danza. https://periodicos.unespar.edu.br/vortex/article/download/3204/2088/8162
- Descalzo, M. L. (2019). *Elementos cubanos en el ritmo afroperuano festejo* (tesis, UNLP). Festejo cajón, bongó, conga, campana and bass transcriptions (Ollita, Raíces del festejo, Mayoral). http://sedici.unlp.edu.ar/bitstream/handle/10915/131310/Documento_completo.pdf-PDFA.pdf?sequence=1&isAllowed=y
- Demera Zambrano, G. M. (2017). *América al compás de África: andarele, landó y samba* (tesis, UDLA). Feldman's landó cajón variations, Toro mata/Valentín patterns, i–V7 harmony. https://dspace.udla.edu.ec/bitstream/33000/7136/1/UDLA-EC-TLMU-2017-29.pdf
- Wikipedia, "Landó (music)" (cajón and bell patterns). https://en.wikipedia.org/wiki/Land%C3%B3_(music)
- Wikipedia, "Afro-Peruvian music". https://en.wikipedia.org/wiki/Afro-Peruvian_music
- Thomann Online Expert, "Cajón: traditional and modern grooves" (landó flams on 2, 4+, 6). https://www.thomannmusic.com/onlineexpert_page_cajon_traditional_and_modern_grooves.html
- Morales, H. *The Afro-Peruvian Percussion Ensemble* (Sher Music): book page and sample charts (festejo cowbell, fuga cowbell, drum-set landó). https://www.shermusic.com/products/afro-peruvian-percussion-ensemble · https://cdn.shopify.com/s/files/1/0684/9524/5503/files/Afro-Peruvian_Percussion_Ensemble_-_Cowbell_Patterns.pdf?v=1781638086 · https://cdn.shopify.com/s/files/1/0684/9524/5503/files/Afro-Peruvian_Percussion_Ensemble_-_Drum_Set_Lando_Patterns.pdf?v=1781638086
- Alcázar, H. (2008). "Patrón básico de festejo (análisis)" (12/8, no constant clave). http://hugoalcazar.blogspot.com/2008/04/j.html
- Cruise Ship Drummer, "Page o' coordination: Afro-Peruvian 01" (6/8 vs 12/8 vs 6/4; Alegría: no clave). https://cruiseshipdrummer.com/2017/04/02/page-o-coordination-afro-peruvian-01/
- Benavides Castro, M. A. (2022). *El desarrollo del lenguaje armónico en el landó 1960–1990* (tesis PUCP; abstract: minor key and 12/8 constant). https://tesis.pucp.edu.pe/handle/20.500.12404/22491
- *Cada canción con su bordón: el desarrollo del estilo de la guitarra en el landó* (PUCP; abstract: bordones and rasgueos). https://repositorio.pucp.edu.pe/index/handle/123456789/187913
- Pacheco, C. (2018). "Patrones rítmicos del vals criollo peruano y su adaptación al cuarteto de cuerdas." UNM. https://repositorio.unm.edu.pe/handle/20.500.12767/135
- Santa Cruz, N. "Ensayo sobre la marinera" (repr. Sonidos del Norte). https://sonidosdelnorte.blogspot.com/2015/12/ensayo-sobre-la-marinera-por-nicomedes.html
- Wikipedia, "Marinera". https://en.wikipedia.org/wiki/Marinera
- Afropop Worldwide, "Donkey jaws" (quijada in festejo and son de los diablos). https://afropop.org/articles/donkey-jaws-percussion-nothing-like-it

Colombia / Venezuela / Peru-Amazon / Bolivia
- Wikipedia (es), "Bambuco". https://es.wikipedia.org/wiki/Bambuco
- Wikipedia (es), "Joropo" (pasaje ♩≈152, golpe ♩≈176–192, hemiola). https://es.wikipedia.org/wiki/Joropo
- Wikipedia (es), "Currulao". https://es.wikipedia.org/wiki/Currulao
- *Acompañamiento para bajo eléctrico en los ritmos paseo y merengue* (Unireformada; merengue = 6/8 like puya but slower). https://repository.unireformada.edu.co/bitstreams/235e80db-ab95-4fed-be63-fb1fa7493731/download
- Toloza Velandia, F. (2015). Vallenato airs manual (UIS): record only. https://noesis.uis.edu.co/items/48c24f31-b14c-49cf-887e-f32ec371f850/full
- Wikipedia, "Peruvian cumbia" (chicha). https://en.wikipedia.org/wiki/Peruvian_cumbia
- Wikipedia, "Caporales". https://en.wikipedia.org/wiki/Caporales · "Saya (art form)". https://en.wikipedia.org/wiki/Saya_(art_form)
- Wikipedia, "Huayno". https://en.wikipedia.org/wiki/Huayno

Brazil
- "Ginga: a Brazilian approach to swing" (course handout, UVic): samba surdo/tamborim, baião zabumba/bacalhau, maracatu gonguê/alfaia, 3-3-2. https://web.uvic.ca/~aschloss/course_mat/MU320/Global%20Rhtyhm%20and%20Human%20Consciousness/ARTICLES%20AND%20REFS%20FOR%20320/Brazilian_groove_ginga.pdf
- Silva, F. C. & Madeira, B. (2021). "O ijexá nas levadas de violão." *Per Musi* 41 (Cardoso's agogô/lê/rumpi/rum grid; Gil's levada). https://periodicos.ufmg.br/index.php/permusi/article/download/26666/27629/102164
- Wikipedia, "Ijexá". https://en.wikipedia.org/wiki/Ijex%C3%A1 · Aventura do Brasil, "Rhythms of Brazil: afoxé and ijexá". https://www.aventuradobrasil.com/blog/rhythms-of-brazil-afox-and-ijex/
- Not found: a readable transcription source for cumbia, vallenato caja/guacharaca, currulao, saya or caporales. Those cards are `[C]`/`[A]` only, so check them against the listening references.

Argentina / Uruguay
- Taján, O. "El rasgueo de la chacarera en la guitarra" (UNLP; dos-tres, chasquido, aro/parche). https://jornadassecyt.fba.unlp.edu.ar/Jidap_pdf/eje_3/Tajan.pdf
- Mola, S. (2022). Candombe method paper (JIDAP, UNLP): claves, chico, piano, repique. https://www4.fba.unlp.edu.ar/jidap2022/wp-content/uploads/sites/4/2022/11/9.-MOLA.pdf
- Wikipedia, "Candombe drums". https://en.wikipedia.org/wiki/Candombe_drums
- Smithsonian Folkways lesson, "Dance traditions of Argentina" (chacarera 6/8 vs 3/4). https://folkways-media.si.edu/docs/lesson_plans/FLP10012_argentina_dance.pdf

Instruments and tempo look-ups
- AutoharpStore, "Chord bar arrangements for Oscar Schmidt autoharps" (21-chord layout). https://www.autoharpstore.com/pdfs/chordlayout.pdf
- Elderly Instruments, Oscar Schmidt OS21C (chord list). https://www.elderly.com/products/oscar-schmidt-os21c-autoharp
- Sela Nomo D Kurd 9 handpan (note layout). https://www.kirstein.de/en/Drums-Percussion/Meditation-and-Music-Therapy/Handpans-Tongue-Drums/Sela-SEHP401-Nomo-Handpan-D-Kurd-9-3-Stainless-Steel.html
- SongBPM, tempo and key look-ups for the song being arranged. https://songbpm.com · "María Landó" (auto-detected 115; not trusted as ♩.). https://songbpm.com/@susana-baca/maria-lando
