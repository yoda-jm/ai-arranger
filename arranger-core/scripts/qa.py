"""Automatic checks of a built arrangement (OUTDIR/events.json), optionally against the recording.

usage: qa.py OUTDIR [--work W] [--top 12]
  score-only: ranges of every pitched part, tessitura (time in the top 3 semitones of a range), leaps > a 6th in
              background voices, semitone / minor-9th clashes between background voices, lead onsets without a syllable,
              lead vs chord symbols (long notes a semitone above a chord tone = clash; useful after a reharmonisation),
              part constraints declared by a style layer (notes outside a fixed scale such as a hang drum's, chords an
              autoharp has no bar for), one player on two instruments at once, instrument switches with no time to
              change, and a section x part activity table (the energy arc)
  vs recording (W/bars.json): lead vs sung pitch (lead f0) per bar  -> transcription errors
                              bass vs recorded bass pitch class per 8th
                              chroma similarity of the whole arrangement vs the recording per bar
  The lead is part "L" or, in band arrangements, the voice each section names as lead. Re-timed sections are compared
  through their warp; a transposed arrangement (META rec_shift) is moved back into the record's key first.
Prints the worst bars (recording numbers, measure numbers in brackets) for each check.
"""
import sys, os, json, collections, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acap import Bars, Layout, nm, stem
from engine import chord

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--work"); ap.add_argument("--top", type=int, default=12)
a = ap.parse_args()
J = json.load(open(f"{a.out}/events.json")); META, EV = J["meta"], J["events"]
W = a.work or META.get("work"); BAR = META["bar"]; TOP = a.top; BEAT = META.get("beat", 4)
KITS = META.get("kits", {}); KINDS = META.get("kinds", {}); SHIFT = META.get("rec_shift", 0)
LAY = Layout(META)


def kind(v): return KINDS.get(v) or ("perc" if v == "VP" or v in KITS else "voice")


SUNG = [v for v in EV if kind(v) == "voice"]
PITCHED = [v for v in EV if kind(v) != "perc"]


def lead_of(meas):
    """(voice, octave) singing the tune in this measure: 'L', or the section's lead map."""
    s = LAY.of.get(meas)
    x = s and s.get("lead", {}).get(str(meas - s["measure"]))
    return tuple(x) if x else (("L", 0) if "L" in EV else (None, 0))


def is_lead(v, meas): return lead_of(meas)[0] == v


def pitches(m): return m if isinstance(m, list) else [m]


# ---------------------------------------------------------------- ranges, tessitura, leaps
print("== ranges: lowest-highest note (* = outside the part's range) | % of sounding time in the top 3 semitones")
for v in PITCHED:
    evs = EV[v]
    if not evs: print(f"  {v:4s} (silent)"); continue
    ps = [p for e in evs for p in pitches(e[3])]; lo, hi = META["ranges"].get(v) or (0, 127)
    out = [(e[6], nm(p)) for e in evs for p in pitches(e[3]) if not lo <= p <= hi]
    tot = sum(e[2] for e in evs); top = sum(e[2] for e in evs if max(pitches(e[3])) > hi - 3)
    bg = [e for e in evs if not is_lead(v, e[6]) and not isinstance(e[3], list)]
    leaps = sum(1 for x, y in zip(bg, bg[1:]) if abs(x[3] - y[3]) > 9) if kind(v) == "voice" and v != "L" else 0
    hi_txt = f"high {100 * top / tot:4.1f}%" if kind(v) == "voice" else "          "
    print(f"  {v:4s} {nm(min(ps))}-{nm(max(ps))} {'*' if out else ' '} {hi_txt}  "
          f"leaps>6th {leaps:3d}  {('out of range (measure, note): ' + str(out[:6])) if out else ''}")

# ---------------------------------------------------------------- sounding grid: (measure, pos) -> {voice: (midi, onset, dur, rec)}
grid = collections.defaultdict(dict)
for v in PITCHED:
    for rec, st, du, m, vel, tie, meas, *_ in EV[v]:
        for k in range(du):
            p = st + k; grid[(meas + p // BAR, p % BAR)][v] = (m, k == 0 and not tie, du, rec)
clash = collections.Counter(); ex = collections.defaultdict(list)
for (meas, pos), d in sorted(grid.items()):
    vs = [v for v in d if v in SUNG and not is_lead(v, meas) and not isinstance(d[v][0], list)]
    for i in range(len(vs)):
        for j in range(i + 1, len(vs)):
            (x, _, dx, _), (y, _, dy, _) = d[vs[i]], d[vs[j]]
            if abs(x - y) % 12 == 1 and min(dx, dy) >= 3:
                clash[meas] += 1
                if len(ex[meas]) < 2: ex[meas].append(f"{vs[i]} {nm(x)}/{vs[j]} {nm(y)} @{pos}")
print(f"== semitone / minor-9th rubs between background voices (both notes >= dotted 8th): total {sum(clash.values())}")
for meas, c in sorted(clash.items(), key=lambda x: -x[1])[:TOP]: print(f"  m{meas:3d}: {c:3d}  {ex[meas]}")

# ---------------------------------------------------------------- lyrics
LEAD = [(v, e) for v in SUNG for e in EV[v] if is_lead(v, e[6])]
if LEAD and len(LEAD[0][1]) > 7:
    miss = collections.Counter(e[6] for v, e in LEAD if not e[5] and not e[7])
    many = [m for m, c in sorted(miss.items()) if c >= 3]
    print(f"== lead: {len(LEAD)} notes, {sum(miss.values())} onsets without a syllable (melismas are fine)"
          + (f"; measures with >= 3: {many}" if many else ""))

# ---------------------------------------------------------------- lead vs chord symbols
if LAY.secs and LEAD:
    on = tot = 0; bad = []
    for v, e in LEAD:
        rec, st, du, m, vel, tie, meas = e[:7]
        s = LAY.of.get(meas)
        if s is None or isinstance(m, list) or du < 2: continue
        row = s["chords"][meas - s["measure"]]; c = chord(row[min(len(row) - 1, st * len(row) // BAR)])
        tot += du; pc = m % 12
        if pc in c["tones"]: on += du
        elif du >= 4 and any((pc - t) % 12 == 1 for t in c["tones"]): bad.append((meas, nm(m), c["sym"], du))
    print(f"== lead vs chord symbols: {100 * on / max(tot, 1):.0f}% of the lead's 8ths-or-longer on chord tones; "
          f"{len(bad)} long notes a semitone above a chord tone (clash unless it is the colour you want)")
    if bad: print("  ", ", ".join(f"m{m} {n}/{c}" for m, n, c, _ in bad[:TOP * 2]))

# ---------------------------------------------------------------- constraints declared by the style layer
for v, allowed in META.get("pitchset", {}).items():
    if v not in EV: continue
    off = [(e[6], nm(p)) for e in EV[v] for p in pitches(e[3]) if p not in allowed]
    print(f"== {v}: {len(off)} notes outside its fixed notes {[nm(p) for p in allowed]}" + (f": {off[:TOP]}" if off else ""))
for v, rows in META.get("chordset", {}).items():
    miss = [(m, s) for m, s, play, exact in rows if play is None]
    approx = sorted({(s, play) for m, s, play, exact in rows if play and not exact})
    print(f"== {v}: {len(rows)} chord slots played; {len(miss)} with no playable chord"
          + (f" {miss[:TOP]}" if miss else "") + (f"; played as: {', '.join(f'{s}->{p}' for s, p in approx)}" if approx else ""))

# ---------------------------------------------------------------- players: one instrument at a time, time to switch
active = collections.defaultdict(set)
for v in EV:
    for e in EV[v]:
        if e[3] is not None: active[e[6]].add(v)
for player, vs in META.get("players", {}).items():
    over = [m for m in sorted(active) if len(active[m] & set(vs)) > 1]
    if len(vs) > 1:
        print(f"== player {player} ({' / '.join(vs)}): {len(over)} measures with two of their parts at once"
              + (f": {over[:TOP]}" if over else ""))
for v, kit in KITS.items():
    if v not in EV or v == "VP": continue
    inst = lambda snd: kit[snd][2].split()[0].split("-")[0]   # "snare-stand cowbell" belongs to the snare setup
    hits = [((e[6] - 1) * BAR + e[1], {inst(x) for x in e[3]}) for e in EV[v]]
    both = sorted({t // BAR + 1 for t, i in hits if len(i) > 1})
    fast = []
    for (t0, i0), (t1, i1) in zip(hits, hits[1:]):
        if i0 != i1 and len(i0 | i1) > 1 and t1 - t0 < BEAT: fast.append((t1 // BAR + 1, "/".join(sorted(i0)), "/".join(sorted(i1))))
    print(f"== {v}: {len(both)} measures hitting two instruments at once" + (f" {both[:TOP]}" if both else "")
          + f"; {len(fast)} switches with less than a beat to change" + (f" {fast[:TOP]}" if fast else ""))

# ---------------------------------------------------------------- activity per section (the energy arc)
if LAY.secs:
    print("== activity per section: parts playing (notes per measure)")
    for s in LAY.secs:
        ms = range(s["measure"], s["measure"] + s["nbars"])
        cnt = {v: sum(1 for e in EV[v] if e[6] in ms and e[3] is not None and not e[5]) for v in EV}
        on = [f"{v}:{c / s['nbars']:.0f}" for v, c in cnt.items() if c]
        print(f"  m{s['measure']:3d} {s['name'][:22]:22s} {len(on):2d} parts  " + " ".join(on))

if not (W and os.path.exists(f"{W}/bars.json")):
    print("(no W/bars.json: skipping the checks against the recording)"); sys.exit(0)
B = Bars(W); LAY = Layout(META, B)


def rt(rec, meas, pos): return B.t(rec, LAY.rec(meas, pos))


# ---------------------------------------------------------------- lead vs sung pitch
if LEAD and os.path.exists(f"{W}/lead_f0.npy"):
    f0 = np.load(f"{W}/lead_f0.npy")
    per = collections.defaultdict(lambda: [0, 0, 0])
    for v, e in LEAD:
        rec, st, du, m, vel, tie, meas = e[:7]
        if rec is None or rec not in B or isinstance(m, list): continue
        octave = lead_of(meas)[1]
        for k in range(du):
            t0, t1 = rt(rec, meas, st + k), rt(rec, meas, st + k + 1)
            seg = f0[int(t0 * 100):int(t1 * 100)]; seg = seg[~np.isnan(seg)]
            if len(seg) < 3: continue
            sung = float(np.median(seg)); mm = m - SHIFT - octave
            per[(rec, meas)][2] += 1
            per[(rec, meas)][0] += abs(sung - mm) < 0.6
            per[(rec, meas)][1] += abs((sung - mm + 6) % 12 - 6) < 0.6
    tot = sum(x[2] for x in per.values()); ok = sum(x[0] for x in per.values()); okpc = sum(x[1] for x in per.values())
    print(f"== lead vs recorded lead (16ths where the singer is voiced): exact {100 * ok / max(tot, 1):.1f}%, "
          f"same pitch class {100 * okpc / max(tot, 1):.1f}%  (low bars = transcription to check; timing slop is normal)")
    worst = sorted(((x[1] / x[2], k) for k, x in per.items() if x[2] >= 4), key=lambda z: z[0])[:TOP]
    print("  worst bars (rec bar [measure]: pitch-class agreement):",
          ", ".join(f"{r}[m{m}]: {s:.2f}" for s, (r, m) in worst))

import librosa
sr = 22050; hop = 512
# ---------------------------------------------------------------- bass vs recorded bass
BV = next((v for v in ("B", "BASS") if v in EV), None)
if BV and os.path.exists(stem(W, "bass")):
    y = librosa.load(stem(W, "bass"), sr=sr)[0]
    Cq = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.midi_to_hz(28), n_bins=36, bins_per_octave=12))
    agree = tot = 0; bad = collections.Counter()
    for rec, st, du, m, vel, tie, meas, *_ in EV[BV]:
        if m is None or rec is None or rec not in B or isinstance(m, list): continue
        for k in range(du):
            pos = st + k
            if pos % 2: continue
            t0, t1 = rt(rec, meas, pos), rt(rec, meas, pos + 2)
            x = Cq[:, int(t0 * sr / hop) + 1:int(t1 * sr / hop) + 1]
            if x.size == 0 or x.max() < 1e-3 * Cq.max(): continue
            pc = (28 + int(np.argmax(x.mean(1)))) % 12
            tot += 1; agree += pc == (m - SHIFT) % 12
            if pc != (m - SHIFT) % 12: bad[(rec, meas)] += 1
    print(f"== {BV} = recorded bass pitch class: {agree}/{tot} = {100 * agree / max(tot, 1):.1f}% of 8ths"
          + ("  (a reharmonisation lowers this on purpose)" if META.get("score_render") else ""))
    print("  most differences:", ", ".join(f"{r}[m{m}]: {c}" for (r, m), c in bad.most_common(TOP)))

# ---------------------------------------------------------------- harmony vs the recording
if os.path.exists(stem(W, "other")):
    yo = sum(librosa.load(stem(W, s), sr=sr)[0] * g for s, g in (("other", 1), ("bass", .5), ("vocals", .5))
             if os.path.exists(stem(W, s)))
    Co = librosa.feature.chroma_cqt(y=yo, sr=sr, hop_length=hop)
    bars = collections.defaultdict(lambda: np.zeros(12)); recof = {}
    for (meas, pos), d in grid.items():
        for v, (m, on, du, rec) in d.items():
            if rec is None: continue
            for p in pitches(m):
                bars[meas][(p - SHIFT) % 12] += 1.5 if v in ("B", "BASS") else 1.0
            recof[meas] = rec
    sims = {}
    for meas, ch in bars.items():
        rec = recof[meas]
        if rec not in B or ch.sum() == 0: continue
        r = Co[:, int(B.start(rec) * sr / hop):int((B.start(rec) + B.length(rec)) * sr / hop)].mean(1)
        sims[(rec, meas)] = float(ch @ r / (np.linalg.norm(ch) * np.linalg.norm(r) + 1e-9))
    vals = np.array(list(sims.values()))
    if len(vals):
        print(f"== chroma similarity arrangement vs recording per bar: median {np.median(vals):.2f}, "
              f"10th pct {np.percentile(vals, 10):.2f}  (< 0.6 = probably a wrong chord or key"
              + ("; a reharmonisation lowers it on purpose)" if META.get("score_render") else ")"))
        print("  lowest:", ", ".join(f"{r}[m{m}]: {s:.2f}" for (r, m), s in sorted(sims.items(), key=lambda x: x[1])[:TOP]))
