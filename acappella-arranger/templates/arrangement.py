"""ARRANGEMENT FILE. Build with:
    $ACAP_PY ${CLAUDE_SKILL_DIR}/../arranger-core/scripts/build.py arrangement.py OUT --work W --png
API: arranger-core/references/engine.md. Worked example: examples/code-monkey/ at the repository root.

Plan (fill this in before writing notes; one row per section, one texture per voice group):
| section  | rec bars | key | solo | upper backgrounds (S1 S2 A) | lower (T Br) | bass | VP |
|----------|----------|-----|------|-----------------------------|--------------|------|----|
| Intro    | -1..0    |     | -    | hook (brass block)          | swell        | pedal| count-in |
| Verse 1  | 1..8     |     | yes  | Oo pads                     | Oo pads      | record's line | rim + kick |
| Chorus 1 | 9..16    |     | yes  | hook words block            | keys off8    | record's line | full |
| ...      |          |     |      |                             |              |      |    |
"""
from engine import *
import song as S

setup(voices=["L", "S1", "S2", "A", "T", "Br", "B", "VP"],      # SATB: ["S", "A", "T", "B"]; 6: ["L","S","A","T","B","VP"]
      title="Song Title", composer="Writer(s)", arranger="a cappella arr. ...", name="song_acappella",
      solo="male")                                               # "female" -> treble clef, G3-G5
BG = ["S1", "S2", "A", "T", "Br"]
PV = [(1, 0, 6), (1, 6, 2), (2, 8, 6), (2, 14, 2)]               # bass rhythm: root . . 8th | 2nd chord . . 8th
PH = [(1, 0, 8), (2, 8, 8)]                                       # half notes

# ================================================================= VERSE 1
s = section("Verse 1", "C", 1, S.V1_CH, S.V1, S.V1_LYR, tempo=120)
s["dyn"][("L", 0)] = "mf"; s["text"][("L", 0)] = "Solo"
put_pad(s, ["S2", "A", "T"], "Oo", R(S2=(64, 72), A=(60, 67), T=(55, 62)), dyn="p", text="warm, like strings")
put_bass(s, PV, dyn="mf", text="bass")
vp(s, hats=None, rim=True)

# ================================================================= CHORUS 1 (uncomment once S.CH is filled)
# s = section("Chorus 1", "C", 9, S.CH_CH, S.CH, S.CH_LYR)
# put_block(s, ["S1", "S2", "A", "T"], shift(s["mel"], 12), mode="drop2", dyn="f")
# put_follow(s, "Br", s["mel"], (45, 57))
# put_bass(s, PV, dyn="f")
# vp(s, hats="8")

# ================================================================= ENDING: last section's final chord
# fermata_last(s); s["parts"]["VP"][-1] = vp_bar({0: "B/Ksh"})
