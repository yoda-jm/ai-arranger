# Researching a new style or lineup

Use this when the user names a style, group or lineup the skills have no card for: "like Pentatonix", "barbershop", "a VoicePlay-style video", "a chacarera". The goal is a **style card** stating what an arranger must do for listeners to recognise the style, mapped onto the engine. The cards in `acappella-arranger/references/styles.md` were made this way. The worked log in §3 shows the method in practice.

## 1. The method
1. **Name the target and the question.** Decide whether it is a group (Pentatonix), a tradition with rules (barbershop) or a genre (festejo). Then write down what you need to find:
   - the lineup;
   - the core features;
   - what the engine can and can't do.
2. **The lineup first**, from the group's Wikipedia page or official site:
   - list the members with their voice parts and any instruments they double;
   - note when each part changed. Lineups change and sources disagree, so date every claim and trust the most recent dated source.
   - Map each part to an engine voice key and range. If a part has no key, add a `VOICE_INFO` entry (staff name, clef, range).
3. **Rulebooks before opinions.** Some styles have a governing body or a contest category, whose rules give hard numbers. Examples:
   - the Barbershop Harmony Society: at least 1/3 barbershop sevenths;
   - Sweet Adelines;
   - samba-school judging;
   - folk-dance federations.

   Next come arranging manuals and teaching handouts, which give ranges and voicing rules.
4. **For a group, ask the people who made the records.**
   - Trade-press production articles: Sound On Sound "Inside Track", Mix.
   - Interviews with the arranger, and award credits (the Grammy for Best Arrangement names the arranger).
   - The best primary source is a published arrangement by the group's own arranger (Hal Leonard, Sheet Music Direct, Alfred). Read it if the user can get it.
5. **Filter the sources.**
   - **Keep**: Wikipedia (for facts, and for its references), official organisation and group sites, trade press, publishers, academic articles.
   - An academic article whose abstract is all you could read can be listed, but not cited for findings you didn't read.
   - **Reject**:
     - SEO or aggregator pages that clone one another (the same "vocal coach reacts" article appeared on several unrelated domains);
     - generated "complete guide" pages;
     - fan wikis for any fact that only they state;
     - any page naming people no other source names.
   - **A search summary is not a source.** Open the page (WebFetch) before writing a claim, and keep its URL. A login page or a binary PDF is not a dead end: try another URL, or save the PDF and run `pdftotext`.
6. **Core or incidental.** A feature is **core** when one of these holds:
   - a rulebook requires it;
   - two independent sources name it;
   - it shows on every reference recording you measure (step 7).

   Studio production that can't be sung live is **incidental**: note it, but don't write it. Examples: quadruple-tracked backing vocals, beatbox layered with samples, an exciter on the bass.
7. **Measure on reference recordings.** The recording is the truth; the web gives hypotheses. Take 2–3 representative tracks: the user supplies them, and they stay out of the repository. Run `analyze.py`, then turn each feature into a number:

   | feature | how to measure |
   |---|---|
   | number of voices and their spread | `look.py roll` on the stems |
   | the bass's lowest notes and how much time it spends there | `look.py nnls bass` |
   | the chord vocabulary (e.g. the share of dominant 7ths by duration) | the chords column of `report.md` |
   | VP presence and density per section | the drum grid and levels |
   | who sings the tune and where the lead changes | `look.py f0`: register jumps |
   | key changes | key regions |
   | medley seams | `≈rep` and the form table |

8. **Write the card.** It has:
   - the lineup → voice keys and ranges (as code);
   - the core features, most important first, each with its source;
   - the engine recipe;
   - the **gaps**: what the engine can't do yet;
   - what to listen to;
   - the sources, with the date you read them.

   Until step 7 is done, label the card "web-sourced, not measured".
9. **Ask the user what they hear in it.** "Pentatonix style" may mean the bass drops and the beatbox to them, not the medleys. One question, with the card's core list as options.

## 2. Where cards go
- A cappella lineups and group styles: `acappella-arranger/references/styles.md`.
- Band grooves (South American, Cuban…): `south-american-arranger/references/styles.md`. Its card format puts patterns on a 16th grid.
- Anything that becomes a rule for every style (a QA check, a voicing helper) goes into the engine and its reference. A card only points to it.

## 3. Worked log: barbershop, Pentatonix, VoicePlay (October 2026)

**Barbershop.**
- What worked:
  - Wikipedia's "Barbershop arranging" page states the contest rules: barbershop sevenths for at least 1/3 of the duration, the circle of fifths, which chords are allowed, and the part roles.
  - The BHS glossary defined the embellishments.
  - A college arranging handout (a PDF that came back as binary, read with `pdftotext`) gave the ranges per part, the voicing rules and the song-choice criteria.
- What was dropped: a search summary claimed "35–60%" barbershop sevenths. No page that was opened said so.

**Pentatonix.**
- What worked:
  - Wikipedia gave the lineup, the 2017 bass change, the style keywords and the two arrangement Grammys.
  - A Sound On Sound "Inside Track" gave session facts: who leads where (the lead changes hands at the chorus), the overdubbed chorus beatbox, body percussion, and the studio-only layering (marked incidental).
- What failed:
  - the Grammy interview link led to a login page;
  - "vocal coach reacts" pages were cloned across domains and named a bassist no other source knows. They were rejected.
- A search summary called the current bassist "unverified"; Wikipedia confirmed him. Opening the page settles it.
- **Still to measure**: "drops", key changes and medley seams. Fans mention them; the sources above don't.

**VoicePlay.**
- What worked:
  - Wikipedia gave the lineup, dated members, the barbershop-quartet origins, the aims ("sound like a full band", lead switching), the repertoire and the theatrical shows.
  - A podcast page about the bass gave the subharmonic register.
- Two older articles listed a past lineup. The most recent dated source wins.
- The sources say little about arranging, so this card most needs step 7.
