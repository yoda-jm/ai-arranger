"""SONG FILE (transcription): the record's melody, lyrics and chords, one list entry per bar.
Fill it from W/draft.py (copy, then fix by ear and with look.py), one block per distinct phrase type;
derive repeats / transposed repeats with tr_tokens / tr_chords instead of re-transcribing.

Tokens: PITCH:DUR in 16ths (r = rest, ~ = tie into the next same pitch), concert pitch (male solo sounds as written
an octave below the treble-8 clef). Lyrics: one string per bar, one syllable per note onset; 'Dash-' starts a word,
'-ing' ends it, '-ra-' is a middle syllable, '_' = no syllable (melisma).
"""
from engine import tr_tokens, tr_chords

# ---------------------------------------------------------------- verse (recording bars 1-8)
V1 = [
    "r:16",            # bar 1  <- paste LEAD[1][0] from draft.py and fix
]
V1_LYR = [
    "",                # bar 1  <- LEAD[1][1]
]
V1_CH = [
    ["C", "C"],        # bar 1  <- CHORDS[1], checked against BASS[1]
]

# ---------------------------------------------------------------- chorus
CH = []
CH_LYR = []
CH_CH = []

# ---------------------------------------------------------------- derived sections (examples)
# V2 = V1 with other words:          V2, V2_LYR = V1, [...]
# Chorus up a whole step:            CH2 = tr_tokens(CH, 2, "D"); CH2_CH = tr_chords(CH_CH, 2, "D")

# ---------------------------------------------------------------- instrument hooks and backing lines heard on the record
HOOK = ""          # e.g. intro riff from draft OTHER_TOP / look.py roll other
BASSLINE = {}      # optional: hand-checked bass tokens per recording bar (from BASS draft), sung an octave up if needed
