"""partscope.py — zoom tools for transcribing ONE PART (bass line, guitar bass notes, riff) note by note.

Built for parts that the stems don't isolate: a guitarist playing the bass role on his low strings (it lands in
the `other` stem), a solo bass filmed on a phone, a riff under a full band. Work on an analysis dir W made by
analyze.py (uses W/bars.json and W/stems/*.wav). A "real bar" below = 2 tracker bars when beat_this locked on the
8th note (slow songs; check the report's bpm) — pass --tb 1 if one tracker bar is one real bar.

  partscope.py W lowest STEM BAR NBARS [--labels F,C,..]       lowest salient pitch per 8th (+ '*' = new attack)
  partscope.py W stack STEM OUT.png LO HI lab:BAR,lab:BAR ...  the same bar from several passes, stacked (CQT)
  partscope.py W rows STEM OUT.png T0 T1 [--row 9 --lo E2 --hi E4]   plain CQT in rows of N seconds (any time span)
  partscope.py W onsets STEM BAR [BAR...]                      per 16th: which pitches START (plain bins, no octave sum)
  partscope.py W repluck STEM NOTE BAR I0 I1 [BAR I0 I1 ...]   the note's own bin every 12 ms (FFT 2048): re-pluck test
  partscope.py W glide STEM T0 T1 [--notes E2,F2,G2,A2,..]     fine bins (FFT 8192) every 23 ms: slide vs pluck, E vs F
  partscope.py W profile STEM lab:BAR,BAR lab:BAR,...          pitch-class profile of groups of bars (chord check)
  partscope.py W notes16 STEM E3,B2,C#3,.. BAR [BAR...]       each note's level per 16th + '+' attacks (arpeggios, walks)
  partscope.py W picked STEM NBARS --passes 16,40,86            a PICKED (busy) part: lowest note started per 16th, every pass + consensus

How to read them (details and the mistakes they prevent: references/transcription.md):
- lowest/stack: first pass, what the line is. stack = compare every pass of a section: same figure = the pattern,
  a pass that differs = a slip (the user's rule: "always the same except when the player makes a mistake").
- onsets: decides strum vs bass note. A strum on the high strings shows A3/C4/E4 starting with NO low pitch; a bass
  note shows its own low pitch starting. Never decide this with an octave-summed salience (a strummed A3 then looks
  like a bass A2).
- repluck: a re-picked note = attack, a sharp drop, a second attack, AWAY from the note's onset (e.g. on the & of
  its last beat). A dip 60-130 ms after an onset is NOT proof of a 16th double: a neighbour semitone fading out,
  beating, or a strum make the same shape (a "double on the beat" seen this way was not there). A held note = a
  flat line (control). FFT 2048 cannot separate adjacent semitones below ~150 Hz (A2/A#2/B2 share a bin): use
  notes16 (FFT 4096) for chromatic lines and check that the columns differ.
- glide: a slide shows the energy moving bin to bin (G2 -> G#2 -> A2 in ~0.1 s) with no new attack.
- picked: when the player picks the part continuously (a chorus in 16ths), the other tables come out far too thin.
  This one reads every note start (basic-pitch) and keeps what most passes agree on. Write the consensus.
  BUT first rule out a STRUM: a 16th strum also starts notes on every 16th, and its "lowest note" hops between
  the chord's strings (a C# or G# between A roots), which reads as a fake busy line. If the low strings and the
  high strings attack together, it is a strum: write the chord's bottom notes in its pulse instead.
- notes16: a whole figure per 16th (the down-and-up arpeggio at a phrase end, a walk-up). Check its every pass.
- rows (filter_scale 0.6): several bars as a picture — the best overview of where a line moves (a rising chorus end).
- profile: e.g. "is this bar Dm or E7?" — D A F strong and E/B/G# weak = Dm. Compare with a bar of known chord.
Times printed are relative to the analysed file; add your extract's start offset for the video timestamp.
"""
import sys, os, json, argparse
import numpy as np
import librosa

LAB16 = ['1', '1e', '1&', '1a', '2', '2e', '2&', '2a', '3', '3e', '3&', '3a', '4', '4e', '4&', '4a', 'X']
NAMES = 'C C# D D# E F F# G G# A A# B'.split()


def stem_path(W, stem):
    if os.path.exists(stem): return stem
    return f'{W}/audio.wav' if stem == 'audio' else f'{W}/stems/{stem}.wav'


def bars_of(W):
    d = json.load(open(f'{W}/bars.json')); bars = d['bars']
    last = max(int(k) for k in bars)          # a closing bar at the song's end, so the last real bar has an end too
    if 'end' in d and str(last + 1) not in bars: bars[str(last + 1)] = {'t': d['end'], 'nbeats': 4, 'beats': []}
    return bars


def grid8(bars, b, tb):
    """8 grid points (8ths if tb=2 on an 8th-locked tracker) of the real bar starting at tracker bar b, + end."""
    pts = []
    for k in range(tb):
        bb = bars[str(b + k)]
        if bb['nbeats'] == 4: pts += bb['beats'][:4]
        else: pts += list(np.linspace(bb['t'], bars[str(b + k + 1)]['t'], 5)[:4])
    end = bars[str(b + tb)]['t']
    if len(pts) == 4:   # quarter-note tracker (--tb 1): add the 8ths between the beats
        q = pts + [end]
        pts = [x for i in range(4) for x in (q[i], (q[i] + q[i + 1]) / 2)]
    return pts, end


def grid16(bars, b, tb):
    p, end = grid8(bars, b, tb); p = p + [end]
    g = []
    for i in range(len(p) - 1): g += [p[i], (p[i] + p[i + 1]) / 2]
    return g + [end]


def nm(m): return librosa.midi_to_note(int(m), unicode=False)


# ---------------------------------------------------------------- lowest
def cmd_lowest(a):
    bars = bars_of(a.W); labels = a.labels.split(',') if a.labels else []
    pts = []
    for bi in range(a.nbars):
        p, end = grid8(bars, a.bar + a.tb * bi, a.tb); pts += p
    pts.append(end); pts = np.array(pts)
    t0, t1 = pts[0] - 0.6, pts[-1] + 0.6
    y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=t0, duration=t1 - t0)
    lo = 36
    C = np.abs(librosa.cqt(y, sr=sr, hop_length=256, fmin=librosa.midi_to_hz(lo - 1 / 3), n_bins=144, bins_per_octave=36))
    C = C.reshape(48, 3, -1).max(1)
    ft = librosa.frames_to_time(np.arange(C.shape[1]), sr=sr, hop_length=256) + t0
    ref = np.percentile(C, 99)
    def sal(v):
        s = v.copy()
        for k, w in ((12, .5), (19, .35), (24, .25)): s[:-k] += w * v[k:]
        return s
    rows = []
    for i in range(len(pts) - 1):
        s0 = pts[i]
        on = (ft >= s0 - 0.03) & (ft < s0 + 0.18); pre = (ft >= s0 - 0.16) & (ft < s0 - 0.04)
        v = C[:, on].mean(1); vp = C[:, pre].mean(1) if pre.any() else v * 0
        s = sal(v)[:28]; rise = (v - vp)[:28]; mx = s.max()
        cands = [m for m in range(1, 27) if s[m] >= 0.45 * mx and s[m] >= s[m - 1] and s[m] >= s[m + 1] and v[m] > 0.25 * v[:28].max()]
        lowm = cands[0] if cands else None
        lvl = 20 * np.log10(v[:28].max() / ref + 1e-9)
        rows.append((lowm, lvl, lowm is not None and rise[lowm] > 0.25 * v[lowm]))
    for bi in range(a.nbars):
        cells = []
        for j in range(8):
            lowm, lvl, new = rows[bi * 8 + j]
            if lvl < -32: cells.append('   .   '); continue
            s = (nm(lo + lowm) if lowm is not None else '?') + ('*' if new else ' ')
            cells.append(f'{s:<4}{lvl:3.0f}')
        lab = labels[bi] if bi < len(labels) else ''
        print(f'{a.bar + a.tb * bi:>4} {lab:<4} ' + ' '.join(cells))


# ---------------------------------------------------------------- stack / rows (images)
def _plt():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    return plt


def cmd_stack(a):
    plt = _plt(); bars = bars_of(a.W)
    LO, HI = librosa.note_to_midi(a.lo) if not a.lo.isdigit() else int(a.lo), librosa.note_to_midi(a.hi) if not a.hi.isdigit() else int(a.hi)
    specs = [s.split(':') if ':' in s else ('', s) for s in a.specs]
    fig, axs = plt.subplots(len(specs), 1, figsize=(14, 2.3 * len(specs))); axs = np.atleast_1d(axs)
    for ax, (lab, b) in zip(axs, specs):
        b = int(b); g = grid16(bars, b, a.tb); t0, t2 = g[0], g[-1]; pad = 0.5
        y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=t0 - pad, duration=t2 - t0 + 2 * pad)
        C = np.abs(librosa.cqt(y, sr=sr, hop_length=128, fmin=librosa.midi_to_hz(LO - 0.5), n_bins=(HI - LO + 1) * 3, bins_per_octave=36))
        D = np.clip(librosa.amplitude_to_db(C, ref=np.percentile(C, 99.5)), -30, 0)
        ax.imshow(D, aspect='auto', origin='lower', extent=[-pad, t2 - t0 + pad, LO - 0.5, HI + 0.5], cmap='magma', interpolation='nearest')
        for k, x in enumerate(g):
            ax.axvline(x - t0, color='w' if k % 4 == 0 else 'c', lw=1.2 if k % 8 == 0 else 0.4, alpha=0.8)
        ax.set_yticks(range(LO, HI + 1)); ax.set_yticklabels([nm(m) for m in range(LO, HI + 1)], fontsize=6)
        ax.set_xticks([x - t0 for x in g[:-1:2]]); ax.set_xticklabels([str(k + 1) for k in range(len(g[:-1:2]))], fontsize=7)
        ax.set_ylabel(f'{lab} b{b}', fontsize=8)
    plt.tight_layout(); plt.savefig(a.out, dpi=a.dpi); print(a.out)


def cmd_rows(a):
    plt = _plt()
    LO, HI = librosa.note_to_midi(a.lo), librosa.note_to_midi(a.hi)
    n = int(np.ceil((a.t1 - a.t0) / a.row))
    fig, axs = plt.subplots(n, 1, figsize=(14, 2.4 * n)); axs = np.atleast_1d(axs)
    y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=a.t0, duration=a.t1 - a.t0)
    C = np.abs(librosa.cqt(y, sr=sr, hop_length=128, fmin=librosa.midi_to_hz(LO - 0.5), n_bins=(HI - LO + 1) * 3, bins_per_octave=36, filter_scale=a.fs))
    D = np.clip(librosa.amplitude_to_db(C, ref=np.percentile(C, 99.5)), -30, 0); fr = 128 / sr
    for i, ax in enumerate(axs):
        x0, x1 = i * a.row, min((i + 1) * a.row, a.t1 - a.t0)
        ax.imshow(D[:, int(x0 / fr):int(x1 / fr)], aspect='auto', origin='lower', extent=[a.t0 + x0, a.t0 + x1, LO - .5, HI + .5], cmap='magma')
        ax.set_yticks(range(LO, HI + 1)); ax.set_yticklabels([nm(m) for m in range(LO, HI + 1)], fontsize=6)
        ax.set_xticks(np.arange(np.ceil(a.t0 + x0), a.t0 + x1, 1.0)); ax.grid(axis='x', color='w', alpha=.3)
    plt.tight_layout(); plt.savefig(a.out, dpi=a.dpi); print(a.out)


# ---------------------------------------------------------------- onsets
def cmd_onsets(a):
    bars = bars_of(a.W); LO, HI = librosa.note_to_midi(a.lo), librosa.note_to_midi(a.hi)
    for b in a.bars:
        g = grid16(bars, b, a.tb); t0, t2 = g[0], g[-1]; pad = 0.3
        y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=t0 - pad, duration=t2 - t0 + 2 * pad)
        C = np.abs(librosa.cqt(y, sr=sr, hop_length=64, fmin=librosa.midi_to_hz(LO - 1 / 3), n_bins=(HI - LO + 1) * 3, bins_per_octave=36))
        C = C.reshape(HI - LO + 1, 3, -1).max(1); D = 20 * np.log10(C / C.max() + 1e-7)
        ft = librosa.frames_to_time(np.arange(C.shape[1]), sr=sr, hop_length=64) + t0 - pad
        print(f'== bar {b}  start {t0:.2f}s')
        for k, s in enumerate(g[:-1]):
            pre = (ft >= s - 0.07) & (ft < s - 0.01); post = (ft >= s - 0.02) & (ft < s + 0.08)
            rise = D[:, post].max(1) - D[:, pre].min(1); lvl = D[:, post].max(1)
            hits = [f'{nm(LO + i)}({rise[i]:.0f})' for i in range(HI - LO + 1) if rise[i] >= a.rise and lvl[i] >= a.lvl]
            loud = [nm(LO + i) for i in range(HI - LO + 1) if lvl[i] >= -12][:6]
            if hits or a.all: print(f'  {LAB16[k]:<3} {s:7.2f}  new: {" ".join(hits):<58} loud: {" ".join(loud)}')


# ---------------------------------------------------------------- repluck
def cmd_repluck(a):
    bars = bars_of(a.W); h0 = librosa.note_to_hz(a.note); sp = a.specs
    for i in range(0, len(sp), 3):
        b, i0, i1 = int(sp[i]), int(sp[i + 1]), int(sp[i + 2])
        g = grid16(bars, b, a.tb); x0, x1 = g[i0] - 0.1, g[i1] + 0.05
        y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=x0 - 0.3, duration=x1 - x0 + 0.6)
        hop = 256
        S = np.abs(librosa.stft(y, n_fft=a.nfft, hop_length=hop))
        fr = librosa.fft_frequencies(sr=sr, n_fft=a.nfft)
        tt = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop) + x0 - 0.3
        e = 20 * np.log10(S[np.argmin(np.abs(fr - h0))] + 1e-9)
        sel = np.where((tt >= x0) & (tt <= x1))[0]; ref = e[sel].max()
        nxt = [k for k in range(len(g)) if x0 <= g[k] <= x1]; row = ''
        for j in sel:
            while nxt and tt[j] >= g[nxt[0]] - hop / sr / 2:
                row += f' [{LAB16[nxt[0]]}]'; nxt.pop(0)
            row += f' {e[j] - ref:.0f}'
        print(f'bar {b:>3} {a.note}:{row}')


# ---------------------------------------------------------------- glide
def cmd_glide(a):
    notes = a.notes.split(','); hz = [librosa.note_to_hz(n) for n in notes]
    y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=a.t0 - 0.2, duration=a.t1 - a.t0 + 0.4)
    S = np.abs(librosa.stft(y, n_fft=8192, hop_length=256))
    fr = librosa.fft_frequencies(sr=sr, n_fft=8192)
    tt = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=256) + a.t0 - 0.2
    band = (fr > min(hz) * 0.9) & (fr < max(hz) * 1.1); ref = S[band].max()
    def lvl(i, h):
        m = (fr > h * 0.972) & (fr < h * 1.028)
        return 20 * np.log10(S[m, i].max() / ref + 1e-6)
    print('  time  ' + ' '.join(f'{n:>5}' for n in notes) + '   peak')
    for i in range(len(tt)):
        if tt[i] < a.t0 or tt[i] > a.t1: continue
        pk = fr[band][np.argmax(S[band, i])]
        print(f'{tt[i]:7.3f} ' + ' '.join(f'{lvl(i, h):5.0f}' for h in hz) + f'   {pk:6.1f} {librosa.hz_to_note(pk, unicode=False)}')


# ---------------------------------------------------------------- profile
def cmd_profile(a):
    bars = bars_of(a.W)
    for spec in a.groups:
        lab, bl = spec.split(':'); prof = np.zeros(12)
        for b in bl.split(','):
            g = grid16(bars, int(b), a.tb)
            y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=g[0], duration=g[-1] - g[0])
            c = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512, bins_per_octave=36).mean(1)
            prof += c / c.max()
        prof /= prof.max()
        print(f'{lab:<8}', ' '.join(f'{NAMES[i]}:{prof[i]:.2f}' for i in np.argsort(-prof)[:8]))


# ---------------------------------------------------------------- notes16
def cmd_notes16(a):
    """Level of each listed note's own bin (FFT 4096: 5.4 Hz bins, so neighbouring semitones above ~E2 separate)
    at every 16th of each bar, '+' = a rise of >= 4 dB over the previous 16th (a new attack). Reads a whole
    figure at once: arpeggios, walks, fills at phrase ends."""
    bars = bars_of(a.W); notes = a.notes.split(',')
    for b in a.bars:
        g = grid16(bars, b, a.tb)
        y, sr = librosa.load(stem_path(a.W, a.stem), sr=22050, offset=g[0] - 0.5, duration=g[-1] - g[0] + 1.0)
        S = np.abs(librosa.stft(y, n_fft=4096, hop_length=64)); fr = librosa.fft_frequencies(sr=sr, n_fft=4096)
        tt = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=64) + g[0] - 0.5
        rows = {n: 20 * np.log10(S[np.argmin(np.abs(fr - librosa.note_to_hz(n)))] + 1e-9) for n in notes}
        top = max(r[(tt >= g[0]) & (tt <= g[-1])].max() for r in rows.values())
        print(f'== bar {b}    ' + ''.join(f'{l:>7}' for l in LAB16[:16]))
        for n in notes:
            e = rows[n]; cells = []
            for k in range(16):
                m = (tt >= g[k] - 0.02) & (tt < g[k] + 0.07); pm = (tt >= g[k] - 0.12) & (tt < g[k] - 0.02)
                v = e[m].max() - top; rise = e[m].max() - e[pm].min()
                cells.append(f'{v:5.0f}{"+" if rise >= 4 and v > -22 else " "} ')
            print(f'   {n:>4}  ' + ''.join(cells))


# ---------------------------------------------------------------- picked
def cmd_picked(a):
    """A guitarist who PICKS the bass part continuously (16ths): basic-pitch note starts on the stem, lowest started
    note per 16th for each pass, then the consensus (notes found in >= --min passes). The tables of the other tools
    are too thin here; this is what reads the busy part."""
    import tempfile, soundfile as sf
    from basic_pitch.inference import predict
    bars = bars_of(a.W); starts = [int(x) for x in a.passes.split(',')]
    lo, hi = librosa.note_to_midi(a.lo), librosa.note_to_midi(a.hi)
    y, sr = sf.read(stem_path(a.W, a.stem)); y = y.mean(1) if y.ndim > 1 else y
    from collections import Counter
    table = {}
    for s0 in starts:
        t0 = bars[str(s0)]['t'] - 0.3; t1 = bars[str(s0 + a.nbars * a.tb)]['t'] + 0.3
        with tempfile.NamedTemporaryFile(suffix='.wav') as f:
            sf.write(f.name, y[int(t0 * sr):int(t1 * sr)], sr)
            _, _, notes = predict(f.name, onset_threshold=0.5, frame_threshold=0.3, minimum_note_length=60,
                                  minimum_frequency=60, maximum_frequency=800)
        for k in range(a.nbars):
            g = grid16(bars, s0 + k * a.tb, a.tb); d = (g[-1] - g[0]) / 16
            row = []
            for x in g[:-1]:
                ns = [n[2] for n in notes if abs(n[0] + t0 - x) < d / 2 and n[3] >= a.vel and lo <= n[2] <= hi]
                row.append(nm(min(ns)) if ns else '.')
            table[(s0, k)] = row
    print('          ' + ''.join(f'{l:<5}' for l in LAB16[:16]))
    for k in range(a.nbars):
        for s0 in starts:
            print(f'b{s0 + k * a.tb:<4}    ' + ''.join(f'{x:<5}' for x in table[(s0, k)]))
        cons = []
        for j in range(16):
            c = Counter(table[(s0, k)][j] for s0 in starts if table[(s0, k)][j] != '.').most_common(1)
            cons.append(c[0][0] if c and c[0][1] >= a.min else '.')
        print('  =>      ' + ''.join(f'{x:<5}' for x in cons) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('W'); ap.add_argument('--tb', type=int, default=2, help='tracker bars per real bar (default 2)')
    ap.add_argument('--dpi', type=int, default=80)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('lowest'); p.add_argument('stem'); p.add_argument('bar', type=int); p.add_argument('nbars', type=int); p.add_argument('--labels')
    p = sub.add_parser('stack'); p.add_argument('stem'); p.add_argument('out'); p.add_argument('lo'); p.add_argument('hi'); p.add_argument('specs', nargs='+')
    p = sub.add_parser('rows'); p.add_argument('stem'); p.add_argument('out'); p.add_argument('t0', type=float); p.add_argument('t1', type=float)
    p.add_argument('--row', type=float, default=9); p.add_argument('--lo', default='E2'); p.add_argument('--hi', default='E4')
    p.add_argument('--fs', type=float, default=0.6, help='CQT filter_scale: < 1 = sharper in time (0.6 shows a moving line clearly)')
    p = sub.add_parser('onsets'); p.add_argument('stem'); p.add_argument('bars', nargs='+', type=int)
    p.add_argument('--rise', type=float, default=7); p.add_argument('--lvl', type=float, default=-22)
    p.add_argument('--lo', default='E2'); p.add_argument('--hi', default='E4'); p.add_argument('--all', action='store_true')
    p = sub.add_parser('repluck'); p.add_argument('stem'); p.add_argument('note'); p.add_argument('specs', nargs='+'); p.add_argument('--nfft', type=int, default=2048)
    p = sub.add_parser('glide'); p.add_argument('stem'); p.add_argument('t0', type=float); p.add_argument('t1', type=float)
    p.add_argument('--notes', default='E2,F2,G2,G#2,A2,B2,C3,D3,E3')
    p = sub.add_parser('profile'); p.add_argument('stem'); p.add_argument('groups', nargs='+')
    p = sub.add_parser('picked'); p.add_argument('stem'); p.add_argument('nbars', type=int); p.add_argument('--passes', required=True)
    p.add_argument('--lo', default='E2'); p.add_argument('--hi', default='F#3'); p.add_argument('--vel', type=float, default=0.3); p.add_argument('--min', type=int, default=2)
    p = sub.add_parser('notes16'); p.add_argument('stem'); p.add_argument('notes'); p.add_argument('bars', nargs='+', type=int)
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
