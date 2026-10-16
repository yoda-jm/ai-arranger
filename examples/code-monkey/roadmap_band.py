"""Roadmap for the band's sheets (drums, bass, guitars): the short score. compact.py checks every merge.

Verses 2 and 3, their pre-choruses and the first 9 bars of their choruses are played the same, so they are written
once between repeat barlines. The 1st ending is chorus 2's end (on D) and the interlude; the 2nd ending is the last
chorus's tags and the ending. 125 written-out measures -> 93 printed."""
MARKS = {1: "Verse 1", 16: "Pre-chorus 1", 24: "Chorus 1", 41: "Verse 2 / 3", 56: "Pre-chorus 2 / 3",
         64: "Chorus 2 / 3", 80: "Interlude", 122: "Outro"}
R = [dict(m=m) for m in range(1, 41)]
R += [dict(m=m, same=[m + 44]) for m in range(41, 73)]          # pass 2 (41-72) = pass 3 (85-116)
R += [dict(m=m) for m in range(73, 85)]                          # 1st ending
R += [dict(m=m) for m in range(117, 126)]                        # 2nd ending
for r in R:
    if r["m"] in MARKS: r["mark"] = MARKS[r["m"]]
at = {r["m"]: r for r in R}
at[41]["fwd"] = True
at[73]["ending"] = (1, "start"); at[73]["text"] = "chorus 2 ending"
at[84].update(ending=(1, "stop"), back=True)
at[117]["ending"] = (2, "start"); at[117]["text"] = "last chorus"
at[125].update(ending=(2, "discontinue"), final=True)
