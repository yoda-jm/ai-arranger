"""SONG FILE (transcription) of code-monkey.mp3: "Code Monkey", words and music by Jonathan Coulton (2006),
CC BY-NC 3.0 (see README.md). E major, 4/4, quarter = 160 (click-exact: 160.01 bpm), 124 bars + the last ring.

Bar 1 = the first downbeat (1.07 s); the voice comes in on beat 2. Bars are the recording's bars (work/bars.json),
so every number below can be checked with look.py / partscope.py.

How it was read: lead = torchcrepe f0 on the lead stem (the vocal stem where the double-tracked chorus left the lead
stem empty), rhythm on the 8th grid from the f0 onsets and the Whisper word times; chords = recorded bass +
accompaniment chroma (look.py chords); words = the fan lyrics under the author's Thing a Week post, checked against
Whisper line by line (chorus 2 ends "like you... lots").

MEL[bar] = (tokens, syllables). Tokens: PITCH:16ths, '~' ties into the next bar, r = rest. One syllable per onset;
'_' = a note on the same syllable. CH[bar] = chord symbols splitting the bar evenly.
"""

MEL, CH = {}, {}


def bars(first, rows):
    for i, row in enumerate(rows):
        MEL[first + i] = row


# ---------------------------------------------------------------- verse 1 (bars 1-15): two-bar lines
bars(1, [
    ("r:4 F#3:2 G#3:2 G#3:2 F#3:2 F#3:4", "Code Mon- -key get up"),
    ("r:2 E3:4 F#3:4 C#3:4 r:2", "get cof- -fee"),
    ("r:4 F#3:2 G#3:2 G#3:4 F#3:2 E3:2", "Code Mon- -key go to"),
    ("E3:6 r:10", "job"),
    ("r:4 F#3:2 G#3:2 G#3:4 F#3:4", "Code Mon- -key have"),
    ("F#3:2 E3:4 F#3:4 C#3:4 r:2", "bor- -ing meet- -ing"),
    ("r:2 E3:2 F#3:2 G#3:2 G#3:2 F#3:2 E3:2 E3~:2", "with bor- -ing man- -a- -ger Rob"),
    ("E3:4 r:12", ""),
    ("r:2 E3:2 G#3:2 B3:4 G#3:4 A3:2", "Rob say Code Mon- -key"),
    ("r:2 G#3:2 A3:4 A3:2 G#3:2 G#3:4", "ve- -ry dil- -i- -gent"),
    ("r:2 F#3:2 G#3:2 F#3:4 D#3:4 E3~:2", "But his out- -put stink"),
    ("E3:2 r:14", ""),
    ("r:2 G#3:4 B3:4 G#3:4 A3:2", "His code not func-"),
    ("A3:2 G#3:2 A3:4 A3:2 G#3:2 G#3:4", "-tion- -al or el- -e- -gant"),
    ("r:2 F#3:2 G#3:2 F#3:4 E3:2 E3:2 E3~:2", "What do Code Mon- -key think"),
])
# ---------------------------------------------------------------- pre-choruses (8 bars each, same tune)
bars(16, [
    ("E3:2 r:2 E3:4 E3:2 F#3:2 G#3:2 G#3:2", "Code Mon- -key think may-"),
    ("A3:8 A3:2 G#3:2 G#3:2 G#3~:2", "-be man- -a- -ger want"),
    ("G#3:2 F#3:2 F#3:4 F#3:2 F#3:2 A3:2 B3~:2", "to write god- -damn log- -in"),
    ("B3:2 A3:4 F#3:2 G#3:2 A3:2 E3~:4", "page him- _ _ -self"),
    ("E3:2 r:2 D#3:4 E3:2 E3:2 D#3:4", "Code Mon- -key not"),
    ("D#3:2 C#3:2 r:6 C#3:4 r:2", "say it out"),
    ("A3:4 D#3:4 E3:2 E3:2 E3:2 E3:2", "loud Code Mon- -key not cra-"),
    ("D#3:8 r:2 B2:4 A3~:2", "-zy just proud"),
])
bars(56, [
    ("E3:2 r:2 E3:4 E3:2 F#3:2 G#3:2 G#3:2", "Code Mon- -key have long"),
    ("A3:8 A3:4 G#3:4", "walk back to"),
    ("G#3:2 F#3:2 F#3:4 F#3:2 A3:2 B3~:4", "cu- -bi- -cle He sit down"),
    ("B3:4 A3:2 F#3:2 G#3:4 F#3:2 E3~:2", "pre- -tend _ to work"),
    ("E3:2 r:2 D#3:4 E3:2 E3:2 D#3:2 D#3:2", "Code Mon- -key not think-"),
    ("D#3:2 C#3:4 r:4 C#3:4 r:2", "-ing _ so"),
    ("A3:4 D#3:4 E3:2 E3:2 E3:4", "straight Code Mon- -key not"),
    ("E3:2 D#3:6 r:2 B2:4 A3~:2", "feel- -ing so great"),
])
bars(100, [
    ("E3:2 r:2 E3:4 E3:2 F#3:2 G#3:2 G#3:2", "Code Mon- -key think some-"),
    ("A3:8 A3:4 G#3:4", "-day he have"),
    ("G#3:2 F#3:2 F#3:4 F#3:2 F#3:2 A3:2 B3~:2", "ev- -ery- -thing e- -ven pret- -ty"),
    ("B3:2 A3:4 F#3:2 G#3:2 A3:2 E3~:4", "girl _ _ like you"),
    ("E3:2 r:2 D#3:4 E3:2 E3:2 D#3:4", "Code Mon- -key just"),
    ("D#3:2 C#3:2 r:6 C#3:4 r:2", "wait- -ing for"),
    ("A3:4 D#3:4 E3:2 E3:2 E3:2 E3:2", "now Code Mon- -key say some-"),
    ("D#3:8 r:2 B2:4 A3~:2", "-day some- -how"),
])
# ---------------------------------------------------------------- choruses (the voice is double-tracked here)
CHORUS = [
    ("A3:4 A3:2 B3:2 B3:2 A3:2 A3:4", "Code Mon- -key like Fri-"),
    ("G#3:6 r:10", "-tos"),
    ("r:4 A3:2 B3:2 B3:2 A3:6", "Code Mon- -key like"),
    ("A3:4 G#3:2 G#3:2 F#3:2 G#3:6", "Tab and Moun- -tain Dew"),
    ("r:4 G#3:2 G#3:2 G#3:2 A3:2 B3:2 B3:2", "Code Mon- -key ve- -ry sim-"),
    ("B3:2 A3:6 r:8", "-ple man"),
    ("r:2 C#3:2 G#3:2 A3:4 A3:2 A3:2 G#3:2", "With big warm fuz- -zy se-"),
    ("G#3:2 F#3:6 r:8", "-cret heart"),
]
TAG_HI = ("r:4 D#3:4 D#3:2 E3:2 E3:4", "Code Mon- -key like")              # "Code Monkey like you", from D#
TAG_LO = ("r:4 C#3:4 D#3:2 E3:2 E3:2 F#3:2", "Code Mon- -key like _")    # the same, from C#
REST = ("r:16", "")
bars(24, CHORUS + [TAG_HI, ("E3:6 r:10", "you"), REST, REST, TAG_LO,
                   ("E3~:16", "you"), ("E3~:16", ""), ("E3~:16", ""), ("E3:14 r:2", "")])
bars(64, CHORUS + [TAG_LO, ("E3:12 r:4", "you"), REST, REST,
                   ("r:4 D#3:4 D#3:2 E3:2 E3:2 F#3:2", "Code Mon- -key like _"),
                   ("E3~:16", "you"), ("E3:10 D3:2 B2~:4", "lots _"), ("B2:2 r:14", ""), REST, REST, REST, REST, REST])
bars(108, CHORUS + [TAG_LO, ("E3:14 r:2", "you"), REST, REST, TAG_LO,
                    ("r:2 E3~:14", "you"), ("E3~:16", ""), ("E3~:16", ""), ("E3:14 r:2", ""), REST])
# ---------------------------------------------------------------- verse 2 (41-55) and verse 3 (85-99)
bars(41, [
    ("r:4 F#3:2 G#3:2 G#3:2 G#3:2 F#3:2 E3:2", "Code Mon- -key hang a- -round"),
    ("r:2 E3:4 F#3:4 C#3:4 r:2", "at front desk"),
    ("r:4 F#3:2 G#3:2 G#3:2 F#3:2 E3:2 E3~:2", "Tell you sweat- -er look nice"),
    ("E3:4 r:12", ""),
    ("r:4 F#3:2 G#3:2 G#3:2 F#3:2 F#3:2 F#3:2", "Code Mon- -key of- -fer buy"),
    ("r:2 E3:4 F#3:4 C#3:4 r:2", "you so- -da"),
    ("r:2 F#3:2 G#3:2 G#3:4 F#3:2 E3:2 r:2", "Bring you cup bring you"),
    ("E3:4 r:12", "ice"),
    ("r:2 G#3:4 B3:4 G#3:4 A3:2", "You say no thank"),
    ("A3:4 A3:2 G#3:2 A3:2 G#3:2 G#3:4", "you for the so- -da 'cause"),
    ("r:2 F#3:2 G#3:2 F#3:4 D#3:4 E3~:2", "So- -da make you fat"),
    ("E3:2 r:12 G#3:2", "An-"),
    ("r:2 G#3:4 B3:4 G#3:4 A3:2", "-y- -way you bus-"),
    ("A3:2 G#3:2 A3:4 A3:2 G#3:2 G#3:4", "-y with the tel- -e- -phone"),
    ("r:2 F#3:4 F#3:4 D#3:4 E3~:2", "No time for chat"),
])
bars(85, [
    ("r:4 F#3:2 G#3:2 G#3:2 F#3:2 F#3:2 F#3:2", "Code Mon- -key have ev- -ery"),
    ("r:2 E3:4 F#3:4 C#3:4 r:2", "rea- _ -son"),
    ("r:4 F#3:2 G#3:2 F#3:2 D#3:4 E3~:2", "To get out this place"),
    ("E3:2 r:14", ""),
    ("r:4 F#3:2 G#3:4 F#3:2 F#3:4", "Code Mon- -key just"),
    ("F#3:2 E3:4 F#3:4 C#3:4 C#3:2", "keep on work- -ing To"),
    ("r:2 F#3:2 G#3:2 G#3:4 F#3:2 E3:2 E3~:2", "see your soft pret- -ty face"),
    ("E3:2 r:12 G#3:2", "Much"),
    ("r:2 G#3:4 B3:4 G#3:4 A3~:2", "rath- -er wake up"),
    ("A3:4 A3:2 G#3:2 A3:2 G#3:2 G#3:4", "eat a cof- -fee cake"),
    ("r:2 F#3:4 F#3:4 D#3:4 E3~:2", "Take bath take nap"),
    ("E3:2 r:14", ""),
    ("r:2 G#3:4 B3:4 G#3:4 A3:2", "This job ful- -fill-"),
    ("A3:2 G#3:2 A3:4 A3:2 G#3:2 G#3:4", "-ing in cre- -a- -tive way"),
    ("r:2 F#3:2 G#3:2 F#3:4 D#3:4 E3~:2", "Such a load of crap"),
])

# ---------------------------------------------------------------- chords
def chords(first, rows):
    for i, row in enumerate(rows):
        CH[first + i] = row if isinstance(row, list) else [row]


VERSE_1 = ["E"] * 8 + ["E", ["A/E", "E"], "E", ["A/E", "E"], "E", ["A/E", "E"], "E"]
VERSE = ["E", ["A", "E"], "E", ["A", "B"]] * 3 + ["E", ["A", "E"], "E"]
PRE = ["A", "B", "G#/C", ["C#m", "B"], "A", "A", "B"]                      # G#/C = G# major over B# (written C)
CHORUS_CH = ["B", "E", "B/D#", "C#m", ["E/B", "B"], "A", "A", "B", "B"]
TAGS = [["E", "B"], ["A", "B"], ["E", "B"], ["A", "B"]]
chords(1, VERSE_1)
chords(16, ["A/E"] + PRE)
chords(24, CHORUS_CH + TAGS + ["E"] * 4)
chords(41, VERSE)
chords(56, ["A"] + PRE)
chords(64, CHORUS_CH + [["D", "A"], "A", "A", ["D", "E"], "D", "A", "A", "A"] + ["E"] * 4)
chords(85, VERSE)
chords(100, ["A"] + PRE)
chords(108, CHORUS_CH + TAGS + ["E"] * 5)

NBARS = 125
SECTIONS = [  # (rehearsal mark, first bar, last bar)
    ("Verse 1", 1, 15), ("Pre-chorus 1", 16, 23), ("Chorus 1", 24, 40),
    ("Verse 2", 41, 55), ("Pre-chorus 2", 56, 63), ("Chorus 2", 64, 79), ("Interlude", 80, 84),
    ("Verse 3", 85, 99), ("Pre-chorus 3", 100, 107), ("Chorus 3", 108, 121), ("Outro", 122, 125),
]
assert sorted(MEL) == list(range(1, NBARS + 1)), [b for b in range(1, NBARS + 1) if b not in MEL]
assert sorted(CH) == list(range(1, NBARS + 1)), [b for b in range(1, NBARS + 1) if b not in CH]
