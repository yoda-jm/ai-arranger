"""Roadmap for the full score and the lead sheet: every measure in playing order (the vocal changes in every verse),
with the section marks; compact.py adds one-bar repeat signs in the instrument staves and multi-measure rests."""
MARKS = {1: "Verse 1", 16: "Pre-chorus 1", 24: "Chorus 1", 41: "Verse 2", 56: "Pre-chorus 2", 64: "Chorus 2",
         80: "Interlude", 85: "Verse 3", 100: "Pre-chorus 3", 108: "Chorus 3", 122: "Outro"}
R = [dict(m=m, **({"mark": MARKS[m]} if m in MARKS else {})) for m in range(1, 126)]
R[-1]["final"] = True
