"""Audio renders of a built arrangement with fluidsynth (General MIDI).

usage: render.py OUTDIR [--work W] [--sf2 FILE] [--gain 0.6] [--seed 1]
  aligned to the recording (needs W/bars.json; sections with first=None are skipped; re-timed sections are lined up
  through their warp; pitches are moved back into the record's key when META rec_shift is set):
    <p>_full, backgrounds_only, mix_with_original (original at 0.45),
    real_lead_over_backgrounds (karaoke lead stem + everything except the lead)  -> "does it work under the singer"
    part_<voice> (only when there is no score-tempo set)                            (p = acappella, or aligned)
  at the arrangement's own tempos (when the arrangement sets META["score_render"], as the band layers do):
    score_full, score_no_vocals (play-along / karaoke), score_vocals, score_part_<voice>
  from MuseScore's MIDI export (score tempo, every bar): score_tempo
Parts play their GM program (voices: piano unless the style layer sets one); percussion kits use their GM notes; chords
(tuples) are strummed: D/d low->high, U/u high->low on the top 4 notes, x = muted chop (GM muted guitar), A = slow roll.
"""
import sys, os, json, subprocess, argparse, glob, shutil, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pretty_midi
from acap import Bars, Layout

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--work"); ap.add_argument("--sf2"); ap.add_argument("--gain", default="0.6")
ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()
OUT = a.out
J = json.load(open(f"{OUT}/events.json"))
META, EV = J["meta"], J["events"]
W = a.work or META.get("work")
AUD = f"{OUT}/audio"; os.makedirs(AUD, exist_ok=True)
random.seed(a.seed)


def find_sf2():
    c = [a.sf2, os.environ.get("ACAP_SF2"), "/usr/share/sounds/sf2/FluidR3_GM.sf2", "/usr/share/soundfonts/FluidR3_GM.sf2",
         "/usr/share/sounds/sf2/default-GM.sf2", "/usr/share/soundfonts/default.sf2", "/usr/share/sounds/sf2/TimGM6mb.sf2",
         os.path.expanduser("~/.cache/acappella/GeneralUser.sf2"), "/opt/homebrew/share/soundfonts/default.sf2"]
    c += glob.glob("/usr/share/sounds/sf2/*.sf2") + glob.glob("/usr/share/soundfonts/*.sf2")
    c += glob.glob("/usr/share/mscore*/sound/*.sf3") + glob.glob("/Applications/MuseScore*/Contents/Resources/sound/*.sf3")
    for p in c:
        if p and os.path.exists(p): return p
    raise SystemExit("no General MIDI soundfont found: install one (references/install.md) or pass --sf2")


SF = find_sf2()
if not shutil.which("fluidsynth"): raise SystemExit("fluidsynth not found (references/install.md)")
DRUM = {"B": 36, "Pf": 38, "k": 37, "t": 42, "ts": 46, "Ksh": 49}
NAME = {v: META["info"][v][0].lower().replace(" ", "").replace("(", "").replace(")", "") for v in EV}
PAN = {v: 64 + META.get("pan", {}).get(v, 0) for v in EV}
KITS = META.get("kits", {}); PROG = META.get("programs", {}); KINDS = META.get("kinds", {})
SHIFT = META.get("rec_shift", 0)


def perc(v): return v == "VP" or v in KITS


def kind(v): return KINDS.get(v) or ("perc" if perc(v) else "voice")


def is_lead(v, meas):
    if v == "L": return True
    s = LAY.of.get(meas)
    return bool(s) and s.get("lead", {}).get(str(meas - s["measure"]), [None])[0] == v


def synth(insts, name, gain=None):
    pm = pretty_midi.PrettyMIDI(); pm.instruments += [x for i in insts for x in [i] + [e for e in getattr(i, "extra", []) if e.notes]]
    mid = f"{AUD}/{name}.mid"; wav = f"{AUD}/{name}.wav"; pm.write(mid)
    subprocess.run(["fluidsynth", "-ni", "-g", gain or a.gain, "-r", "44100", "-F", wav, SF, mid], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav


def mix(inputs, out, vols):
    f = ";".join(f"[{k}:a]volume={v}[x{k}]" for k, v in enumerate(vols))
    f += ";" + "".join(f"[x{k}]" for k in range(len(vols))) + f"amix=inputs={len(vols)}:duration=longest:normalize=0"
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for p in inputs: cmd += ["-i", p]
    subprocess.run(cmd + ["-filter_complex", f, out], check=True)


def instrument(v, when, keep=lambda e: True, shift=0, hold=0.0):
    """One part as a pretty_midi instrument. when(rec, measure, pos) -> seconds or None (skip the event)."""
    inst = pretty_midi.Instrument(program=PROG.get(v, 0), is_drum=perc(v), name=v)
    chop = pretty_midi.Instrument(program=28, name=v)        # muted chops ('x'): GM electric guitar (muted)
    inst.extra = [chop]
    inst.control_changes.append(pretty_midi.ControlChange(10, max(0, min(127, PAN[v])), 0))
    chop.control_changes.append(pretty_midi.ControlChange(10, max(0, min(127, PAN[v])), 0))
    if META.get("score_render") and v in META.get("vol", {}):      # part balance (band layers set it per part)
        for x_ in (inst, chop): x_.control_changes.append(pretty_midi.ControlChange(7, max(0, min(127, META["vol"][v])), 0))
    evs = EV[v]; i = 0; kitmap = KITS.get(v) if v != "VP" else None
    while i < len(evs):
        e = evs[i]; rec, st, du, m, vel, tie_in, meas = e[:7]; x = e[8] if len(e) > 8 else {}
        j = i + 1; end = (rec, meas, st + du); xe = x
        while j < len(evs) and evs[j][5] and evs[j][3] == m and not perc(v):
            end = (evs[j][0], evs[j][6], evs[j][1] + evs[j][2]); xe = evs[j][8] if len(evs[j]) > 8 else xe; j += 1
        if not keep(e): i = j; continue
        s = when(rec, meas, st); t1 = when(*end)
        if s is None or t1 is None: i = j; continue
        if xe.get("art") == "fermata": t1 += hold
        if perc(v):
            if kitmap: s += random.uniform(-0.006, 0.006)
            for d in m:
                if kitmap:
                    gm, vs, _ = kitmap[d]
                    inst.notes.append(pretty_midi.Note(velocity=max(1, min(127, int(vel * vs * 1.25))), pitch=gm,
                                                       start=max(0, s), end=s + 0.15))
                else:
                    inst.notes.append(pretty_midi.Note(velocity=min(127, vel + (25 if d in ("B", "Pf", "Ksh") else -5)),
                                                       pitch=DRUM[d], start=s, end=s + 0.12))
        elif isinstance(m, list):
            ps = sorted(p + shift for p in m); stroke = x.get("stroke")
            if stroke in ("U", "u"): ps = ps[-4:][::-1]
            gap = 0.035 if stroke == "A" else (0.009 if stroke else 0.0)
            ln = 0.07 if stroke == "x" else None
            vv = vel * (0.55 if stroke == "x" else 1.0)
            s += random.uniform(-0.004, 0.004) if stroke else 0
            for k, p in enumerate(ps):
                a0 = s + k * gap
                if stroke == "x":      # a percussive "chk": every string, damped
                    chop.notes.append(pretty_midi.Note(velocity=max(1, min(127, int(vel * 0.8))), pitch=p, start=a0,
                                                       end=a0 + 0.05))
                    continue
                inst.notes.append(pretty_midi.Note(velocity=max(1, min(127, int(vv))), pitch=p, start=a0,
                                                   end=a0 + ln if ln else max(t1 - 0.02, a0 + 0.08)))
        else:
            inst.notes.append(pretty_midi.Note(velocity=min(127, vel), pitch=m + shift, start=s, end=max(t1 - 0.03, s + 0.06)))
        i = j
    return inst


made = []
B = Bars(W) if W and os.path.exists(f"{W}/bars.json") else None
LAY = Layout(META, B)
SCORE = META.get("score_render")

if B:
    def aligned(rec, meas, pos):
        if rec is None or rec not in B: return None
        return B.t(rec, LAY.rec(meas, pos))

    pre = "aligned" if SCORE else "acappella"
    allv = [instrument(v, aligned, shift=-SHIFT) for v in EV]
    full = synth(allv, f"{pre}_full"); made.append(full)
    bg = [instrument(v, aligned, keep=lambda e, v=v: not is_lead(v, e[6]), shift=-SHIFT) for v in EV]
    has_lead = any(is_lead(v, e[6]) for v in EV for e in EV[v])
    if has_lead: made.append(synth(bg, "backgrounds_only"))
    if not SCORE:
        for x in allv: made.append(synth([x], f"part_{NAME[x.name]}", "0.8"))
    if os.path.exists(f"{W}/audio.wav"):
        mix([f"{W}/audio.wav", full], f"{AUD}/mix_with_original.wav", [0.45, 1.0]); made.append("mix_with_original.wav")
    if os.path.exists(f"{W}/stems/lead.wav") and has_lead:
        mix([f"{W}/stems/lead.wav", f"{AUD}/backgrounds_only.wav"], f"{AUD}/real_lead_over_backgrounds.wav", [1.0, 0.9])
        made.append("real_lead_over_backgrounds.wav")
else:
    print("no bars.json: skipping the renders aligned to the recording")

if SCORE:
    def score(rec, meas, pos): return LAY.time(meas, pos) + 0.5

    allv = [instrument(v, score, hold=1.5) for v in EV]
    made.append(synth(allv, "score_full"))
    made.append(synth([x for x in allv if kind(x.name) != "voice"], "score_no_vocals"))
    made.append(synth([x for x in allv if kind(x.name) == "voice"], "score_vocals"))
    for x in allv: made.append(synth([x], f"score_part_{NAME[x.name]}", "0.8"))
mid = f"{OUT}/{META['name']}.mid"
if os.path.exists(mid) and not SCORE:
    subprocess.run(["fluidsynth", "-ni", "-g", a.gain, "-r", "44100", "-F", f"{AUD}/score_tempo.wav", SF, mid], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    made.append("score_tempo.wav")
print("rendered:", ", ".join(os.path.basename(m) for m in made))
