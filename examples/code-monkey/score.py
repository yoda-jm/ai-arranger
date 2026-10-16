"""CODE MONKEY (Jonathan Coulton, 2006; CC BY-NC 3.0): the recording written out for a band. This is a
TRANSCRIPTION, not an arrangement: every part is what the record plays, read from the stems (see README.md for how
each part was read and how sure it is). Words, tune and chords: song.py.

The same file builds the full score and the single sheets (environment variable CM_SHEET):
    full (default)  lead vocal, backing vocals, electric guitar, acoustic guitar, bass, drums
    lead            the lead sheet: melody, words, chord symbols
    drums | guitar | bass   one player's sheet (guitar = both guitars; guitars and bass with TAB)

Build (from the repository root):
    PY=.venv/bin/python; C=arranger-core/scripts; B=south-american-arranger/scripts; A=examples/code-monkey
    $PY $C/build.py $A/score.py $A/out --work $A/work --lib $B --png --scaling 4.6 --staff-distance 45
    CM_SHEET=lead $PY $C/build.py $A/score.py $A/out-lead --work $A/work --lib $B --png

| bars    | section        | voices                         | guitars                       | bass                 | drums                         |
|---------|----------------|--------------------------------|-------------------------------|----------------------|-------------------------------|
| 1-15    | Verse 1        | lead                           | E chug (P.M. 8ths) + strum 8ths | -                  | from bar 9 (fill in 8)        |
| 16-23   | Pre-chorus 1   | lead                           | roots 8ths + strum            | quarters, from 16 4& | stop on 16; 8th hats          |
| 24-40   | Chorus 1       | lead + 8va double (backing)    | roots 8ths + strum            | quarters, pushes, tag walks | backbeat, kick 1 1& 3 3&, ride |
| 41-55   | Verse 2        | lead                           | E chug + strum                | E..B.A | A...(C#)B    | verse groove, fill in 48      |
| 56-63   | Pre-chorus 2   | lead                           | as pre 1                      | as pre 1             | as pre 1                      |
| 64-84   | Chorus 2 + interlude | lead + double; ends on D ("like you... lots") | roots + strum | as chorus 1, D A | chorus, verse groove from 73 |
| 85-99   | Verse 3        | lead                           | as verse 2                    | as verse 2           | as verse 2, fill in 92        |
| 100-107 | Pre-chorus 3   | lead                           | as pre 1                      | as pre 1             | as pre 1                      |
| 108-125 | Chorus 3, ending | lead + double, "you" held    | roots + strum, last strum rings | as chorus 1, E held | chorus; hit on 121, then out |
"""
import os
from band import *
import band as BD
import engine as E
import song as S

SHEET = os.environ.get("CM_SHEET", "full")
PARTS = {"full": ["V", "BV", "EGTR", "GTR", "BASS", "DR"], "lead": ["V"], "drums": ["DR"],
         "guitar": ["EGTR", "GTR"], "bass": ["BASS"]}[SHEET]

# ---------------------------------------------------------------- the line-up (names choose the MuseScore instrument)
BD.BAND["V"] = ("Lead Vocal", "Vo.", ("G", 2, -1), (45, 67), 0, 100)
BD.BAND["BV"] = ("Backing Vocals", "BV", ("G", 2, 0), (55, 79), 15, 70)
BD.BAND["GTR"] = ("Acoustic Guitar", "A.Gtr", ("G", 2, 0), (40, 83), 30, 80)
BD.BAND["EGTR"] = ("Electric Guitar", "E.Gtr", ("G", 2, 0), (40, 76), -30, 85)
BD.BAND["DR"] = ("Drums", "Dr.", ("percussion", 2, 0), None, 0, 90)
BD.INSTRUMENTS.add("EGTR")
BD.PROGRAMS.update(V=52, BV=53, EGTR=28, GTR=25)          # GM: choir aahs, voice oohs, muted electric, steel guitar
BD.SOUNDS["EGTR"] = "pluck.guitar.electric"
BD.TRANSPOSE["EGTR"] = 12
BD.TABS["EGTR"] = "guitar"
BD.PLAYERS["guitar 2"] = ["EGTR"]
BD.PLAYERS["drums"] = ["DR"]
BD.KITS["DR"] = {
    "bdX": BD._s("F", 4, 36, stem="down", label="kit kick"),
    "bdx": BD._s("F", 4, 36, stem="down", vel=0.6, label="kit kick (soft)"),
    "sX": BD._s("C", 5, 38, mark="accent", label="kit snare (accent)"),
    "sx": BD._s("C", 5, 38, vel=0.8, label="kit snare"),
    "sg": BD._s("C", 5, 38, mark="ghost", vel=0.3, label="kit snare ghost"),
    "hhx": BD._s("G", 5, 42, "x", vel=0.5, label="kit hi-hat"),
    "hhX": BD._s("G", 5, 42, "x", mark="accent", vel=0.75, label="kit hi-hat (accent)"),
    "rdx": BD._s("F", 5, 51, "x", vel=0.5, label="kit ride"),
    "rdX": BD._s("F", 5, 51, "x", mark="accent", vel=0.7, label="kit ride (accent)"),
    "crX": BD._s("A", 5, 49, "x", mark="accent", vel=0.85, label="kit crash"),
}
BD.INSTR.update(kick="bd", hat="hh", ride="rd", crash="cr")

setup(title="Code Monkey", composer="Jonathan Coulton (2006), CC BY-NC 3.0",
      arranger="transcribed from the recording with ai-arranger",
      subtitle={"full": "as recorded: full score", "lead": "lead sheet", "drums": "drums", "guitar": "guitars",
                "bass": "bass"}[SHEET],
      name={"full": "code_monkey", "lead": "code_monkey_lead_sheet"}.get(SHEET, f"code_monkey_{SHEET}"),
      meter=(4, 4), rec_shift=0, parts=PARTS)
if SHEET == "drums": E.CHORD_PARTS[:] = ["(none)"]        # no chord symbols on the drum sheet: the form is in the marks

# ---------------------------------------------------------------- grooves (16 cells = the bar's 16ths)
STRUM8 = "D.U.D.U.D.U.D.U."
HIT = "D..............."
VERSE = dict(kick="X.......X.......", snare="....x.......x...", hat="x...x...x...x...")
PRE = dict(kick="X.......X.X.....", snare="....x.......x...", hat="x.x.x.x.x.x.x.x.")
CHO = dict(kick="X.X.....X.X.....", snare="....x.......x...", ride="x.x.x.x.x.x.x.x.")
FILL = dict(kick="X.......X...X...", snare="....x.......xx.x", hat="x...x...x.......")
STOP = dict(kick="X...............", crash="X...............")
INTRO_FILL = dict(kick="..........X...X.", snare="..........x.x...")
ROOT_OCT = {4: 52, 9: 45, 11: 47, 0: 48, 1: 49, 3: 51, 2: 50, 8: 56}     # chug roots: E3 A2 B2 C3(B#) C#3 D#3 D3 G#3
NAMES = "C C# D D# E F F# G G# A A# B".split()


def mname(m): return f"{NAMES[m % 12]}{m // 12 - 1}"


def bar_range(s, a, b): return [x - s["first"] for x in range(a, b + 1)]


def sec(name, a, b):
    lyr = [S.MEL[x][1] for x in range(a, b + 1)]
    prev = S.MEL.get(a - 1, ("r:16", ""))[0].split()[-1]
    if "~" in prev and S.MEL[a][0].split()[0].startswith(prev.split("~")[0] + "~:") or \
            "~" in prev and S.MEL[a][0].split()[0].split(":")[0] == prev.split("~")[0]:
        lyr[0] = ("_ " + lyr[0]).strip()       # a note tied over from the previous section: no syllable (build re-ties it)
    s = section(name, "E", a, [S.CH[x] for x in range(a, b + 1)], [S.MEL[x][0] for x in range(a, b + 1)], lyr,
                tempo=160 if a == 1 else None)
    if "V" in PARTS: lead(s, "V", dyn="mf" if a == 1 else None)
    return s


def drums(s, bars_, text=None, **lanes):
    if "DR" in PARTS: perc(s, "DR", local=bar_range(s, *bars_) if isinstance(bars_, tuple) else bars_, text=text, **lanes)


def chug(s, bars_, pedal=None, text=None):
    """The electric guitar's palm-muted 8ths: the E pedal in the verses, the chord's bass note elsewhere."""
    if "EGTR" not in PARTS: return
    rows = []
    for x in range(bars_[0], bars_[1] + 1):
        toks = []
        for half in S.CH[x] if len(S.CH[x]) == 2 else S.CH[x] * 2:
            pc = pedal if pedal is not None else E.chord(half)["bass"]
            toks += [f"{mname(ROOT_OCT[pc])}:2"] * 4
        rows.append(" ".join(toks))
    put(s, "EGTR", [rest_bar() for _ in range(bars_[0] - s["first"])] + parse_line(rows), local=bar_range(s, *bars_),
        text=text)


def hit(s, x, tokens, text=None):
    """One electric-guitar bar written by hand (the stops)."""
    if "EGTR" in PARTS: put(s, "EGTR", [rest_bar()] * (x - s["first"]) + parse_line([tokens]), local=[x - s["first"]],
                            text=text)


def bass(s, a, rows, text=None):
    if "BASS" in PARTS: put(s, "BASS", [rest_bar() for _ in range(a - s["first"])] + parse_line(rows),
                            local=range(a - s["first"], a - s["first"] + len(rows)), text=text)


def backing(s, bars_):
    """The chorus double-track an octave up (the record's backing stem follows the lead at +12)."""
    if "BV" in PARTS: put(s, "BV", shift(s["parts"]["V"], 12), local=bar_range(s, *bars_))


# bass figures (sounding pitches)
B_PRE = ["A1:4 A1:4 A1:4 A1:4", "B1:4 B1:4 B1:4 B1:4", "C2:4 C2:4 C2:4 C2:4", "C#2:8 B1:8",
         "A1:4 A1:4 A1:4 A1:4", "A1:4 A1:4 A1:4 A1:4", "B1:4 B1:4 B1:4 B1:4"]
B_CHO = ["B1:4 B1:4 B1:4 B1:2 E2~:2", "E2:4 E2:4 E2:4 E2:4", "D#2:4 D#2:4 D#2:4 D#2:4",
         "C#2:4 C#2:4 C#2:4 C#2:2 B1~:2", "B1:4 B1:4 B1:4 B1:2 A1~:2", "A1:4 A1:4 A1:4 A1:4", "A1:4 A1:4 A1:4 A1:4",
         "B1:4 B1:4 B1:4 B1:4", "B1:4 B1:4 B1:4 B1:2 E2:2"]
B_TAGS = ["E2:6 B1:6 A#1:2 A1:2", "A1:6 C#2:4 C2:2 B1:4", "E2:6 B1:6 A#1:2 A1:2", "A1:6 C#2:4 B1:6"]
B_E8 = "E2:2 E2:2 E2:2 E2:2 E2:2 E2:2 E2:2 E2:2"
B_VE, B_VAE, B_VAB = "E2:6 B1:8 A1:2", "A1:6 r:8 E2:2", "A1:6 C#2:6 B1:4"
B_VERSE = [B_VE, B_VAE, B_VE, B_VAB] * 3 + [B_VE, B_VAE, B_VE]

# ---------------------------------------------------------------- the sections (built in bar order: the score follows)
def verse_1():
    s = sec("Verse 1", 1, 15)                       # no bass; drums from bar 9 (fill at the end of bar 8)
    chug(s, (1, 15), pedal=4, text="P.M. (palm-muted 8ths)")
    strum(s, "GTR", STRUM8, text="strum 8ths")
    drums(s, [7], **INTRO_FILL)
    drums(s, (9, 15), text="verse groove: hi-hat quarters", **VERSE)


def pre(name, a):
    s = sec(name, a, a + 7)
    hit(s, a, "E3:2 r:14" if a == 16 else "A2:2 r:14")
    chug(s, (a + 1, a + 7), text="roots, P.M. 8ths")
    strum(s, "GTR", HIT, local=[0]); strum(s, "GTR", STRUM8, local=range(1, 8))
    bass(s, a, ["r:14 A1:2" if a == 16 else "A1:4 r:10 A1:2"] + B_PRE)
    drums(s, [0], text="stop", **STOP)
    drums(s, [1], **dict(PRE, crash="X..............."))
    drums(s, range(2, 8), **PRE)


def chorus(name, a, last):
    s = sec(name, a, last)
    n = last - a + 1
    chug(s, (a, last), text="roots, P.M. 8ths")
    strum(s, "GTR", STRUM8)
    drums(s, [0], **dict(PRE, crash="X...............", snare="....x.......x..x"))
    drums(s, [1], **PRE)
    drums(s, range(2, 8), **CHO)
    drums(s, [8], **dict(CHO, snare="....x.......x..x"))
    backing(s, (a, a + 9))
    if name == "Chorus 2":                          # ends on D: "like you ... lots"
        bass(s, a, B_CHO + ["D2:4 D2:4 D2:4 A1:4", "A1:4 A1:4 A1:4 A1:4", "A1:4 A1:4 A1:4 A1:2 D2:2",
                            "D2:4 D2:4 E2:4 E2:4", "D2:4 D2:4 D2:4 D2:2 A1:2", "A1:4 A1:4 A1:4 A1:4",
                            "A1:4 A1:4 A1:4 A1:4"])
        drums(s, range(9, n), **VERSE)
        backing(s, (a + 12, a + 14))
        return
    bass(s, a, B_CHO + B_TAGS + ([B_E8] * 4 if name == "Chorus 1" else ["E2~:16"]))
    drums(s, range(9, 13), **CHO)
    backing(s, (a + 12, last))
    if name == "Chorus 1":
        drums(s, range(13, 16), **VERSE)
        drums(s, [16], **FILL)
    else:
        drums(s, [13], **STOP)
        strum(s, "GTR", HIT, local=[13])
        hit(s, last, "E3:2 r:14")


def interlude():
    s = sec("Interlude", 80, 84)
    chug(s, (80, 84), text="P.M. 8ths")
    strum(s, "GTR", STRUM8)
    bass(s, 80, ["A1:4 A1:4 A1:4 A1:2 E2:2", B_E8, B_E8, B_E8, B_E8])
    drums(s, [0], **FILL)
    drums(s, range(1, 5), **VERSE)


def verse(name, a, fill):
    s = sec(name, a, a + 14)
    chug(s, (a, a + 14), pedal=4, text="P.M. E pedal")
    strum(s, "GTR", STRUM8)
    bass(s, a, B_VERSE, text="E . B . | A . (C#) B")
    drums(s, range(0, 15), **VERSE)
    drums(s, [fill - a], **FILL)


def outro():
    s = sec("Outro", 122, 125)
    strum(s, "GTR", STRUM8, local=[0, 1]); strum(s, "GTR", HIT, local=[2], text="let ring")
    bass(s, 122, ["E2~:16", "E2~:16", "E2:16", "r:16"])
    backing(s, (122, 124))


verse_1(); pre("Pre-chorus 1", 16); chorus("Chorus 1", 24, 40)
verse("Verse 2", 41, 48); pre("Pre-chorus 2", 56); chorus("Chorus 2", 64, 79); interlude()
verse("Verse 3", 85, 92); pre("Pre-chorus 3", 100); chorus("Chorus 3", 108, 121); outro()
assert [x["first"] for x in E.SECS] == [a for _, a, _ in S.SECTIONS], "sections out of bar order"
finish()
