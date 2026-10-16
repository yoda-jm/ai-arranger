# Audition spec: options of a part, superposed on the real recording, for the user to pick by ear.
# Guide: arranger-core/references/audition.md
#
# This template runs as-is on the repository's worked example ("Code Monkey" by Jonathan Coulton, CC BY-NC 3.0,
# see examples/code-monkey/README.md) once examples/code-monkey/regenerate.sh has made its analysis:
#   $PY arranger-core/scripts/audition.py arranger-core/templates/audition_spec.py examples/code-monkey/out-audition --check other
# For a real job: copy it to $A/audition_<topic>.py, point W at $A/work, and rewrite the clips, questions and part().
# Publish OUT/<ID>.html with the Artifact tool and capabilities {"db": {}}; when the user says the picks are saved,
# read them with Artifact action "read_db", collection "decisions", doc_id = ID, and write the next revision.
import os, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, '..', '..', 'examples', 'code-monkey')

ID = 'code-monkey-chorus-bass'          # also the db document name: one per round of questions
TITLE = 'Code Monkey bass choices'      # keep the same title when a later round replaces the page
INTRO = ('Chorus 1 of the record without its bass, with a synthesized bass laid on the song\'s own bar grid. Switch '
         'options while it plays; the band keeps going and only the bass changes. Tick Loop and click a bar to repeat two bars.')
W = os.path.join(EX, 'work')            # analyze.py output: bars.json, audio.wav, stems/
BAND_STEMS = ['drums', 'other', 'vocals']   # the record has a bass: play the band without it (AUDIO = '...' for another file)
TB = 1                                  # tracker bars per real bar (2 when the tracker counted 8ths)
PROGRAM = 33                            # GM program: 33 fingered bass, 32 acoustic bass, 25 steel guitar, 0 piano
TUNING = [28, 33, 38, 43]               # open strings, low to high (bass E A D G), for the tabs
NAMES = 'EADG'
SHIFT = 0.025                           # seconds; check it with --check (synth notes against the stem's onsets)

# One clip per passage. labels: one (chord, section) per bar; 'E/B B' = two chords in the bar (a space splits them).
# questions: the questions heard in this clip. Without layers every combination is rendered (keep it to 2-3).
# layers={qid: (first_bar, last_bar)} or {qid: [(first, last), ...]}: each option is rendered only over its own bars,
# as short segments swapped alone while the rest plays; the ranges of different questions must not overlap.
CH = runpy.run_path(os.path.join(EX, 'song.py'))['CH']      # the transcription's chords: CH[bar] = [chord, ...]
CLIPS = [dict(id='chorus', title='Chorus 1', src='Code Monkey, 0:34-0:51 · bars 23-33', bars=(23, 33),
              why='Code Monkey is in E, at 160 bpm. The options only change bars 24-32.',
              labels=[(' '.join(CH[b]), 'chorus' if b == 24 else '') for b in range(23, 34)],
              questions=['groove', 'fill'], layers={'groove': (24, 31), 'fill': (32, 32)})]

QUESTIONS = {
    'groove': dict(
        label='Bass groove under the chorus',
        why='What the evidence says, in one or two sentences: who plays what, in which passes.',
        default='eighths',
        options=[dict(id='eighths', name='Roots in 8ths', tag='now on the chart', text='The chord root on every 8th.'),
                 dict(id='halves', name='Roots on 1 and 3', text='Half notes: more space under the voice.'),
                 dict(id='fifths', name='Root and fifth', text='Quarter notes, root on 1 and 3, fifth on 2 and 4.')]),
    'fill': dict(
        label='Fill into the second half',
        why='One bar of B before the chorus repeats.',
        default='none',
        options=[dict(id='none', name='B in 8ths', text='No fill.'),
                 dict(id='walk', name='Walk-up B C# D#', text='B on 1-2, then C# and D# leading to the E.'),
                 dict(id='octave', name='Octaves', text='B and its octave in turn.')]),
}

KEPT = ['Points already settled, with the evidence (shown under the players).']

PC = {n: i for i, n in enumerate('C C# D D# E F F# G G# A A# B'.split())}


def bass(chord):
    """The bass note of a chord symbol (the slash note if any), in the bass's lowest octave E1-D#2."""
    name = chord.split('/')[-1] if '/' in chord else chord
    pc = PC[name[:2] if name[1:2] == '#' else name[:1]]
    return 28 + (pc - 4) % 12


def n(k, midi, d, pos=None):            # k = 16th index 0-15 in the bar, d = length in 16ths (past 16 ties over)
    return (k, midi, d, pos) if pos else (k, midi, d)


def part(clip, choice):
    """Notes of the part for one combination: {bar: [(k16, midi, dur16[, (string, fret)]), ...]}."""
    out = {}
    for b in range(23, 34):
        chords = CH[b]; half = 16 // len(chords)
        notes = []
        for i, ch in enumerate(chords):
            r = bass(ch); start = i * half
            g = 'eighths' if b in (23, 33) else choice['groove']
            if g == 'eighths': notes += [n(start + k, r, 2) for k in range(0, half, 2)]
            elif g == 'halves': notes += [n(start + k, r, 8) for k in range(0, half, 8)]
            else: notes += [n(start + k, r if (start + k) % 8 == 0 else r + 7, 4) for k in range(0, half, 4)]
        out[b] = notes
    B, Cs, Ds = bass('B'), bass('C#'), bass('D#')
    out[32] = {'none': [n(k, B, 2) for k in range(0, 16, 2)],
               'walk': [n(0, B, 4), n(4, B, 4), n(8, Cs, 4), n(12, Ds, 4)],
               'octave': [n(k, B if k % 4 == 0 else B + 12, 2) for k in range(0, 16, 2)]}[choice['fill']]
    return out
