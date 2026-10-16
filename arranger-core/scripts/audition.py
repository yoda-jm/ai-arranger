"""audition.py — let the musician DECIDE BY EAR: each candidate version of a part, synthesized on the recording's own
bar map and superposed on the real recording, in one page with a player per passage and a save button.

  audition.py SPEC.py OUTDIR [--check STEM]

Use it whenever a part has several plausible readings and the user has to choose (the record's line or the live
player's, where a double falls, which octave, how a fill ends), and for a last listen-through of a whole chart. The
user hears each option inside the band, switches options while the band keeps playing, marks bars that still need
work, and saves; Claude reads the picks back with the Artifact tool (`read_db`, collection "decisions", doc = ID).
Full guide: arranger-core/references/audition.md. Spec template: arranger-core/templates/audition_spec.py.

SPEC.py is plain Python:
  ID, TITLE, INTRO            page id (also the db doc name: one per round), title (keep it across rounds), intro
  W                           analysis dir of analyze.py (bars.json, audio.wav, stems/)
  AUDIO = '...'               (optional) the band audio, default W/audio.wav
  BAND_STEMS = ['drums', ...] (optional) mix these stems as the band instead: drop the record's own part
                              (a record with a real bass: ['drums', 'other', 'vocals'])
  TB = 1                      tracker bars per real bar (2 when the tracker counted 8ths)
  PROGRAM = 33                GM program of the synthesized part (33 fingered bass, 32 acoustic bass, 25 guitar, 0 piano)
  TUNING = [28, 33, 38, 43]   open strings low to high, for the tabs (bass E A D G); NAMES = 'EADG'
  SHIFT = 0.025               seconds added to every note (measure it with --check)
  BAR_FIX = {bar: seconds}    (optional) re-place bars the tracker got wrong (a rubato intro); 4 even beats each
  BAND_KBPS, PART_KBPS        (optional) AAC bitrates, default 112 / 80 (96 / 64 keeps a whole song near 8 MB)
  CLIPS = [dict(id, title, src, bars=(first, last), labels=[(chord, section), ...] one per bar,
                questions=[qid, ...], tab_bars=[bar, ...], pre=0.6, post=1.2)]
      chord 'E E/D#' = two chords in the bar (the space splits the halves); section '' when nothing starts there.
      Without layers, every combination of the clip's questions is rendered: keep it to 2-3 questions.
      layers={qid: (first, last)} or {qid: [(first, last), ...]}: each option is rendered as short segments over
      its own bars only (the rest is one base layer), so N questions x M options cost N*M small renders, even on a
      whole song, and the page swaps one question's segments while everything else keeps playing.
      A clip with no questions is a plain listen-through.
  QUESTIONS = {qid: dict(label, why, default, options=[dict(id, name, text, tag?)])}
  KEPT = ['already settled, with the evidence', ...]           (optional)
  CHART = '...'                                                  (optional) chart text shown under the players
  def part(clip_id, choice) -> {bar: [(k16, midi, dur16[, (string, fret)]), ...]}
      choice maps each question of the clip to an option id. k16 = 16th index 0-15 in the bar; a dur16 running past
      16 ties over the barline (a push). (string, fret) is optional, e.g. ('G', 4); else the lowest fret is used.

Output: OUTDIR/<ID>.html (publish it with the Artifact tool and capabilities {"db": {}}), plus the .mid/.m4a files.
--check STEM prints, per render, the offset between the synthesized notes and the onsets of STEM (e.g. other):
anything beyond a few ms means SHIFT or the bar map needs fixing.
"""
import sys, os, json, base64, html as htmlmod, itertools, runpy, subprocess, argparse
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from partscope import grid16, bars_of

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', 'templates', 'audition_page.html')
SF2S = [os.environ.get('ACAP_SF2'), '/usr/share/sounds/sf2/FluidR3_GM.sf2', '/usr/share/soundfonts/FluidR3_GM.sf2',
        '/usr/share/sounds/sf2/default-GM.sf2', '/usr/share/soundfonts/default.sf2', '/usr/share/sounds/sf2/TimGM6mb.sf2']
MAX_MB = 15.0   # the Artifact page limit is 16 MB


def sh(*a):
    subprocess.run([str(x) for x in a], check=True, capture_output=True)


def aac(src, dst, ch, kbps, af=None):
    sh('ffmpeg', '-v', 'error', '-y', *src, *(['-af', af] if af else []), '-ac', ch, '-c:a', 'aac', '-b:a', f'{kbps}k', dst)


def duration(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout)


def position(midi, tuning, names, given=None):
    """(string index, fret): the given one (string index or name), else the lowest fret (ties: the higher string)."""
    if given:
        s, f = given
        return (names.index(s) if isinstance(s, str) else s), f
    best = None
    for s, o in enumerate(tuning):
        f = midi - o
        if 0 <= f <= 24 and (best is None or f <= best[1]): best = (s, f)
    return best


def tab(barnotes, bar_list, labels, first, tuning, names):
    """House-style tab: 2 chars per 16th, ¦ at the half bar, chord row from the clip labels ('E E/D#' = two halves)."""
    rows = {s: names[s] + '|' for s in range(len(tuning))}
    head = '   '
    for b in bar_list:
        cells = [['-'] * 16 for _ in tuning]
        for n in barnotes.get(b, []):
            pos = position(n[1], tuning, names, n[3] if len(n) > 3 else None)
            if pos: cells[pos[0]][n[0]] = str(pos[1])
        for s in range(len(tuning)):
            c = cells[s]
            rows[s] += ''.join(('-' + x)[-2:] for x in c[:8]) + '¦' + ''.join(('-' + x)[-2:] for x in c[8:]) + '-|'
        ch = labels[b - first][0].split(' ')
        head += (ch[0].ljust(17) + (ch[1] if len(ch) > 1 else '')).ljust(35)
    return '\n'.join([head.rstrip()] + [rows[s] for s in reversed(range(len(tuning)))])


def ranges(r):
    return [tuple(r)] if isinstance(r[0], int) else [tuple(x) for x in r]


def validate(S, TB):
    """Catch spec mistakes before minutes of rendering."""
    for key in ('ID', 'TITLE', 'W', 'CLIPS', 'QUESTIONS', 'part'):
        if key not in S: sys.exit(f'spec: {key} is missing')
    Q = S['QUESTIONS']
    for q, d in Q.items():
        ids = [o['id'] for o in d['options']]
        if len(ids) != len(set(ids)): sys.exit(f'spec: question {q} has duplicate option ids')
        if d.get('default', ids[0]) not in ids: sys.exit(f'spec: question {q}: default {d.get("default")} is not an option')
    for c in S['CLIPS']:
        first, last = c['bars']
        nb = (last - first) // TB + 1
        if len(c['labels']) != nb: sys.exit(f"spec: clip {c['id']} has {len(c['labels'])} labels for {nb} bars ({first}-{last})")
        for q in c.get('questions', []):
            if q not in Q: sys.exit(f"spec: clip {c['id']} asks unknown question {q}")
        if c.get('layers'):
            if set(c['layers']) != set(c.get('questions', [])): sys.exit(f"spec: clip {c['id']}: layers must cover exactly its questions")
            spans = sorted((lo, hi, q) for q, r in c['layers'].items() for lo, hi in ranges(r))
            for (lo, hi, q), (lo2, hi2, q2) in zip(spans, spans[1:]):
                if lo2 <= hi: sys.exit(f"spec: clip {c['id']}: layers {q} and {q2} overlap (bars {lo2}-{hi})")
            for lo, hi, q in spans:
                if lo < first or hi > last: sys.exit(f"spec: clip {c['id']}: layer {q} ({lo}-{hi}) is outside the clip")


def band_audio(S, W, out):
    """The band track: AUDIO, W/audio.wav, or a mix of BAND_STEMS (to drop the record's own part)."""
    stems = S.get('BAND_STEMS')
    if not stems: return S.get('AUDIO', f'{W}/audio.wav')
    mixed = f'{out}/band_mix.wav'
    ins = sum([['-i', f'{W}/stems/{s}.wav'] for s in stems], [])
    sh('ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f'amix=inputs={len(stems)}:normalize=0', mixed)
    return mixed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec'); ap.add_argument('out'); ap.add_argument('--check')
    a = ap.parse_args()
    S = runpy.run_path(a.spec)
    TB = S.get('TB', 1)
    validate(S, TB)
    W = S['W']; bars = bars_of(W)
    last = max(int(k) for k in bars)          # a closing bar so the last real bar has an end (the song's end time)
    bars[str(last + 1)] = {'t': json.load(open(f'{W}/bars.json')).get('end', bars[str(last)]['t'] + 3.0), 'nbeats': 4, 'beats': []}
    fix = S.get('BAR_FIX', {})                # {bar: start time}: re-place bars the tracker got wrong (a rubato intro)
    for b, t in fix.items(): bars[str(b)]['t'] = float(t)
    for b in sorted({x for f in fix for x in (f - 1, f)}):
        if str(b) in bars and str(b + 1) in bars:
            bars[str(b)].update(nbeats=4, beats=list(np.linspace(bars[str(b)]['t'], bars[str(b + 1)]['t'], 5)[:4]))
    tuning, names = S.get('TUNING', [28, 33, 38, 43]), S.get('NAMES', 'EADG')
    shift, program = S.get('SHIFT', 0.0), S.get('PROGRAM', 33)
    sf2 = next((p for p in SF2S if p and os.path.exists(p)), None)
    if not sf2: sys.exit('no GM soundfont found (set ACAP_SF2)')
    os.makedirs(a.out, exist_ok=True)
    audio = band_audio(S, W, a.out)
    import pretty_midi
    bk, pk = S.get('BAND_KBPS', 112), S.get('PART_KBPS', 80)
    Q = S['QUESTIONS']
    data = {'id': S['ID'], 'title': S['TITLE'], 'intro': S.get('INTRO', ''), 'kept': S.get('KEPT', []), 'chart': S.get('CHART', ''),
            'questions': Q, 'clips': [], 'tabs': {}, 'marks': {}}
    audio_ids = []
    check_y = {}

    for c in S['CLIPS']:
        first, last = c['bars']
        t0 = max(0.0, bars[str(first)]['t'] - c.get('pre', 0.6))   # never before the file starts
        t1 = bars[str(last + TB)]['t'] + c.get('post', 1.2)
        band = f"{a.out}/band_{c['id']}.m4a"
        aac(['-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', audio], band, 2, bk,
            'afade=t=in:d=0.3,afade=t=out:st=%.3f:d=1.0' % (t1 - t0 - 1.0))
        audio_ids.append((f"band_{c['id']}", band))
        qs = c.get('questions', [])
        layers = {q: ranges(r) for q, r in c['layers'].items()} if c.get('layers') else None
        defaults = {q: Q[q].get('default', Q[q]['options'][0]['id']) for q in qs}
        data['tabs'][c['id']] = {}
        pending = []

        def render(notes, name, seg=None):   # seg = (start, end) in clip seconds: render only that span
            z = seg[0] if seg else 0.0
            span = (seg[1] - seg[0]) if seg else (t1 - t0)
            pm = pretty_midi.PrettyMIDI(); ins = pretty_midi.Instrument(program=program)
            for b, ns in notes.items():
                g = grid16(bars, b, TB)
                for n in ns:
                    k, p, d = n[0], n[1], n[2]
                    e0 = (g[k + d] if k + d <= 16 else grid16(bars, b + TB, TB)[min(k + d - 16, 16)]) - 0.025   # may tie over the barline
                    ins.notes.append(pretty_midi.Note(velocity=100 if k % 4 == 0 else 88, pitch=p,
                                                      start=g[k] - t0 - z + shift, end=e0 - t0 - z + shift))
            pm.instruments.append(ins)
            stem = f"{a.out}/part_{c['id']}_{name}"
            pm.write(stem + '.mid')
            sh('fluidsynth', '-ni', '-g', '0.9', '-r', '44100', '-F', stem + '.wav', sf2, stem + '.mid')
            y, sr = sf.read(stem + '.wav'); y = y.mean(1) if y.ndim > 1 else y
            L = int(span * sr); y = np.pad(y, (0, max(0, L - len(y))))[:L]
            sf.write(stem + '.wav', y, sr)
            pending.append((stem, float(np.abs(y).max())))   # encoded after the clip, with one gain for all its renders
            if a.check and ins.notes:
                import librosa
                if a.check not in check_y:
                    check_y[a.check] = librosa.load(f"{W}/stems/{a.check}.wav", sr=22050)[0]
                yy = check_y[a.check]; o0 = int((t0 + z) * 22050)
                env = librosa.onset.onset_strength(y=yy[o0:o0 + int(span * 22050)], sr=22050, hop_length=64)
                tt = librosa.frames_to_time(np.arange(len(env)), sr=22050, hop_length=64)
                ons = [x.start for x in ins.notes]
                sc = [(np.mean([env[np.argmin(abs(tt - (o + off)))] for o in ons]), off) for off in np.arange(-0.1, 0.101, 0.005)]
                print(f"check {c['id']} {name}: best extra shift {max(sc)[1]:+.3f} s")

        data['marks'][c['id']] = {}
        for q in qs:   # where the options of q differ (others at their default): {bar: [16th, ...]}, drawn on the page
            sets = [S['part'](c['id'], dict(defaults, **{q: o['id']})) for o in Q[q]['options']]
            mk = {}
            for b in sorted(set().union(*[x.keys() for x in sets])):
                for k in range(16):
                    at = [sorted((x[1], x[2]) for x in st.get(b, []) if x[0] == k) for st in sets]
                    if any(v != at[0] for v in at): mk.setdefault(str(b), []).append(k)
            data['marks'][c['id']][q] = mk
        segs = None
        if layers:
            inlayer = lambda b: any(lo <= b <= hi for rs in layers.values() for lo, hi in rs)
            render({b: ns for b, ns in S['part'](c['id'], dict(defaults)).items() if not inlayer(b)}, 'base')
            segs = {}
            for q, rs in layers.items():
                segs[q] = []
                for i, (lo, hi) in enumerate(rs):
                    z0 = max(0.0, bars[str(lo)]['t'] - t0 - 0.15); z1 = min(t1 - t0, bars[str(hi + TB)]['t'] - t0 + 1.5)
                    segs[q].append({'lo': lo, 'hi': hi, 't': round(z0, 3)})
                    for o in Q[q]['options']:
                        notes = {b: ns for b, ns in S['part'](c['id'], dict(defaults, **{q: o['id']})).items() if lo <= b <= hi}
                        render(notes, f"{q}_{o['id']}_{lo}", (z0, z1))
                        if i == 0:
                            data['tabs'][c['id']][f"{q}={o['id']}"] = tab(notes, list(range(lo, hi + 1)), c['labels'], first, tuning, names)
        else:
            for combo in list(itertools.product(*[[o['id'] for o in Q[q]['options']] for q in qs])) or [()]:
                key = '|'.join(combo) or 'only'
                notes = S['part'](c['id'], dict(zip(qs, combo)))
                render(notes, key.replace('|', '_'))
                if c.get('tab_bars'):
                    data['tabs'][c['id']][key] = tab(notes, c['tab_bars'], c['labels'], first, tuning, names)
        # one gain for every render of the clip, from their common peak: options keep their relative level, and a
        # silent base layer (all bars in questions) can't blow the gain up into clipping
        gain = 0.89 / max([pk_ for _, pk_ in pending] + [1e-6])
        for stem, _ in pending:
            y, sr = sf.read(stem + '.wav')
            sf.write(stem + '.wav', np.clip(y * gain, -1, 1), sr)
            aac(['-i', stem + '.wav'], stem + '.m4a', 1, pk)
            audio_ids.append((os.path.basename(stem), stem + '.m4a'))
        data['clips'].append({'id': c['id'], 'title': c['title'], 'src': c.get('src', ''), 'why': c.get('why', ''),
                              'questions': qs, 'layers': {q: [list(x) for x in r] for q, r in layers.items()} if layers else None,
                              'segs': segs, 'first': first, 'dur': round(duration(band), 3),
                              'bars': [round(bars[str(first + i * TB)]['t'] - t0, 3) for i in range(len(c['labels']))],
                              'end': round(bars[str(first + len(c['labels']) * TB)]['t'] - t0, 3),
                              'labels': [{'ch': ch, 'sec': sec} for ch, sec in c['labels']]})

    page = open(TEMPLATE, encoding='utf-8').read()
    page = page.replace('__TITLE__', htmlmod.escape(S['TITLE'])).replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    page = page.replace('__AUDIO__', '\n'.join(f'<script id="a_{i}" type="text/plain">{base64.b64encode(open(f, "rb").read()).decode()}</script>'
                                               for i, f in audio_ids))
    out = f"{a.out}/{S['ID']}.html"
    open(out, 'w', encoding='utf-8').write(page)
    mb = len(page.encode('utf-8')) / 1e6
    print(f'{out}  ({mb:.1f} MB, {len(audio_ids)} audio files)')
    if mb > MAX_MB:
        print(f'WARNING: over {MAX_MB} MB; the page limit is 16 MB. Use layers, shorter clips or lower BAND_KBPS/PART_KBPS.')
    print(f'Publish it with the Artifact tool and capabilities {{"db": {{}}}}; read the picks with read_db, '
          f'collection "decisions", doc_id "{S["ID"]}".')


if __name__ == '__main__':
    main()
