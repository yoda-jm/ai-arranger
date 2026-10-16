# Sending charts and tabs to TroubaStack

[TroubaStack](https://github.com/yoda-jm/troubastack) is a self-hosted platform for bands. It covers sheet music and lyrics, annotation, setlists, and an offline stage presenter. Its server renders a plain-text **chart dialect** (chords over lyrics, sections, tablature blocks, footnotes) to a PDF. That PDF then enters the song's files, so the band can annotate it, put it in a setlist and read it on stage.

When the band uses TroubaStack, the texts this toolkit writes can go straight onto the band's server:
- tabs and bass charts from a part transcription (SKILL.md §2b);
- lead sheets (chords and words per section);
- groove cards.

## What maps to what
| This toolkit writes | In the chart dialect |
|---|---|
| a tab in the house style (transcription.md §6) | a `{sot}` … `{eot}` block: drawn verbatim in Courier, one stave per blank-line-separated group, the chord row over the strings drawn bold |
| the song structure (page 2 of a tab) | `{np}` (page break), then one `## Section - Pattern X` per section with its first lyric line |
| remarks | a `{fn}` footnote block, never inside a chord row |
| a lead sheet (`lead_sheet.md`, `song.py`) | `# Title`, the artist on the next line, `## Section`, then chord rows over lyric lines |
| a groove card (`grooves.md`) | a `{sot}` block per instrument, with a counting ruler (`1 e & a 2 e & a`) as its first line |

**Dialect rules that bite.** The full spec is in the header comment of `core/internal/chartpdf/chart.go` in the TroubaStack repository.
- Text must be **ASCII or Latin-1 only**. Write `#` and `b`, not ♯ and ♭; use `-`, not an en dash. A character outside that set is refused with an error that names it.
- A tab line can be at most about **125 characters** at the smallest size. A longer line is refused, not clipped. Aim for 97 or fewer, so the tab keeps a readable size.
- A stave is never split across pages. A blank line inside a tab block starts a new stave and can push the chart to another page, so check the page count in the preview.
- Transposing a chart moves the chord rows, never the tab lines. Write `{sot original=G}` so a transposed bake notes the tab's key in the margin.

## The API (TroubaCore)
The server's address and the login are the user's. Ask for them, keep them out of the repository, and pass them in environment variables (`TROUBA_URL`, `TROUBA_USER`, `TROUBA_PASSWORD`).

| Call | Use |
|---|---|
| `POST /api/auth/login` `{"username","password"}` | sets a session cookie for the calls below |
| `GET /api/bands/{band}/songs/{song}/files/{file}/chart-source` | the chart's text and its revision |
| `PUT …/files/{file}/chart-source` `{"source","baseRevision"}` | saves a new revision. A stale `baseRevision` gets `409`: re-fetch and merge |
| `POST /api/bands/{band}/songs/{song}/text-charts:preview` `{"source"}` | renders the PDF without saving it |
| `POST …/files/{file}/chart-source:transpose` `{"targetKey" or "semitones", "baseRevision", "dryRun"}` | transposes the chords; `dryRun` returns the new text without saving |

**Workflow** (the musicians edit the same charts, so treat each save as shared work):
1. **Re-fetch** the source and compare it with your last save. If the user edited it in between, keep their edits. Add your bars after theirs rather than rewriting them.
2. **Preview** the PDF. Read it, and check the page count and the tab size.
3. **Save** with the `baseRevision` you fetched.
4. **Re-fetch** and check that the stored text equals what you sent.
5. **Keep a local copy** of each revision you write (`<file>_revNN.txt` plus the preview PDF) in the song's folder.
6. **Tell the user** the new revision number and what changed, bar by bar.
