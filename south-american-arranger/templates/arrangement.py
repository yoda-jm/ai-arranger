"""ARRANGEMENT FILE (band). Build with:
    C=<skills>/arranger-core/scripts; B=<skills>/south-american-arranger/scripts
    $ACAP_PY $C/build.py arrangement.py OUT --work W --lib $B --png && $ACAP_PY $C/qa.py OUT \
        && $ACAP_PY $C/render.py OUT && $ACAP_PY $B/sheets.py OUT
API: references/band.md (band writers) + arranger-core/references/engine.md (engine). Styles: references/styles.md.

Plan (fill this in before writing notes; one row per section):
| section | rec bars | style / tempo | key / harmony move | lead | coros | GTR | AH | BASS | P1 | P2 | HANG |
|---------|----------|---------------|--------------------|------|-------|-----|----|------|----|----|------|
| Intro   | -        | landó 76      | Dm ostinato        | -    | -     | arp | -  | in m3| cajón m3 | - | ostinato |
| Verse 1 | 4-11     | landó 76      | rel. minor Dm Gm Dm Bb-A7 | W1 | - | arp | - | 1..5 | cajón p | shaker | answers |
| ...     |          |               |                    |      |       |     |    |      |    |    |      |
Length budget: ... bars at ... + ... bars at ... = m:ss (record m:ss).
"""
from band import *
import engine as E                      # E.BAR, E.BEAT (BAR from `import *` is stale after setup)
import song as S

setup(title="Song", composer="Writer(s)", arranger="arr. ...", subtitle="(style) version", name="song_style",
      meter=(12, 8), rec_shift=0)       # rec_shift = semitones from the record's key to this key

# ================================================================= INTRO (bars not in the recording: first=None)
s = section("Intro", "Dm", None, [["Dm"], ["Gm"], ["Dm"], ["Bb", "Bb", "Bb", "A7"]], tempo=76, style="landó")
hang_arp(s, "0.2.3.0.2.3.", local=[0, 1], dyn="mp", text="hang")
arp(s, "GTR", "1.3 4.3 2.3 4.3", local=[2, 3], dyn="mp", text="landó arpeggio")
perc(s, "P1", cajon="B.T .BB .TB .TB", local=[2, 3], dyn="p")

# ================================================================= VERSE 1
s = section("Verse 1", "Dm", 4, [["Dm"], ["Gm"], ["Dm"], ["Bb", "Bb", "Bb", "A7"]] * 2, S.V1, S.V1_LYR,
            warp="swing", tempo=76, style="landó")
lead(s, "W1", dyn="mp", text="lead")
arp(s, "GTR", "1.3 4.3 2.3 4.3")
bassline(s, "1-- --- 5-- ---")
perc(s, "P1", cajon="B.T .BB .TB .TB", dyn="p")
perc(s, "P2", shaker="X.x X.x X.x X.x", dyn="p")

# ================================================================= ENDING: last section's final hit
# fermata_last(s); s["parts"]["P1"][-1] = perc_bar("P1", cajon="B...........")
