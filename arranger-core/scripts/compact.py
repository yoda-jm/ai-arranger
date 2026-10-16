"""Write a built (written-out) score the short way: repeat barlines, 1st/2nd endings, D.C./D.S. al Coda, other passes'
words stacked under one staff, one-bar repeat signs (%) and multi-measure rests. MusicXML -> MuseScore -> PDF/MIDI.

usage: compact.py SRC.musicxml ROADMAP.py OUT_BASE [--no-repeat-signs] [--multirest] [--per-system 4]

SRC is a build.py output (every measure written out, in playing order). ROADMAP.py defines R, the score in printed
order: one dict per printed measure,
    m        the written-out measure printed here (1-based)
    same     [measures, ...]   other passes this printed measure stands for: checked identical in every part
             (lyrics, marks and layout ignored), so the merge cannot hide a difference
    lyr      {line: measure}   words of another pass stacked as lyric line `line` under the same notes (verses)
    mark     rehearsal mark;  text  italic direction above the top staff
    fwd / back                 forward / backward repeat barline (left / right side)
    ending   (number, "start"|"stop"|"discontinue"|"both")   1st/2nd ending bracket; "both" = a one-measure ending
    segno / coda / tocoda / dc / ds / final / break   jumps (D.C./D.S. al Coda are made playable), final barline,
             a forced system break before this measure
and optionally R_CHECK = [(measure, measure), ...] extra pairs that must be identical (e.g. a chorus played twice).

The tool checks the merges, writes OUT_BASE.{musicxml,mscz,pdf,mid}, and compares the exported MIDI with SRC's
(same notes, same count) so the short score plays exactly the written-out music.
Repeat signs (%): an instrument measure equal to the printed measure before it (same notes and chord symbols) becomes
a one-bar repeat, except the first measure of a section, of an ending or after a repeat sign; sung parts never do.
"""
import os, re, sys, shutil, subprocess, zipfile, argparse, runpy
from xml.sax.saxutils import escape

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("roadmap"); ap.add_argument("out_base")
ap.add_argument("--no-repeat-signs", action="store_true"); ap.add_argument("--multirest", action="store_true")
ap.add_argument("--per-system", type=int, default=4)
a = ap.parse_args()
SRC, OUT = os.path.abspath(a.src), os.path.abspath(a.out_base)
RM = runpy.run_path(os.path.abspath(a.roadmap)); R = RM["R"]

X = open(SRC).read()
head = X.split("<part id=", 1)[0]
PX = {pid: re.findall(r"<measure[^>]*>.*?</measure>", body, re.S)
      for pid, body in re.findall(r'<part id="(P\d+)">(.*?)</part>', X, re.S)}
PIDS = list(PX)
NW = len(PX[PIDS[0]])
assert all(len(v) == NW for v in PX.values()), {k: len(v) for k, v in PX.items()}
SUNG = {pid for pid in PIDS if "<lyric" in "".join(PX[pid])}
STAVES = {pid: int((re.search(r"<staves>(\d+)</staves>", PX[pid][0]) or [0, 1])[1]) for pid in PIDS}


def inner(mx): return re.sub(r"^<measure[^>]*>|</measure>$", "", mx)


def music(mx, harmony=True):
    """What the players play: no words, marks or layout."""
    x = re.sub(r"<lyric.*?</lyric>|<direction.*?</direction>|<print[^>]*/>", "", inner(mx), flags=re.S)
    if not harmony: x = re.sub(r"<harmony>.*?</harmony>", "", x, flags=re.S)
    return re.sub(r"\s+", "", x)


# ---------------------------------------------------------------- checks: merged passes are the same music
errors = []
pairs = [(r["m"], s) for r in R for s in r.get("same", [])] + list(RM.get("R_CHECK", []))
pairs += [(r["m"], m2) for r in R for m2 in r.get("lyr", {}).values() if m2 != r["m"]]
for m1, m2 in pairs:
    for pid in PIDS:
        if music(PX[pid][m1 - 1]) != music(PX[pid][m2 - 1]):
            errors.append(f"{pid}: written measures {m1} and {m2} differ")
if errors: raise SystemExit("cannot merge:\n  " + "\n  ".join(errors[:30]))
covered = sorted({r["m"] for r in R} | {s for r in R for s in r.get("same", [])})
missing = [m for m in range(1, NW + 1) if m not in covered]
if missing: print(f"warning: written measures not in the roadmap: {missing}")


# ---------------------------------------------------------------- stacked words
def sung_spans(mx):
    return [(n.start(), n.end()) for n in re.finditer(r"<note>.*?</note>", mx, re.S)
            if "<rest" not in n.group(0) and "<chord/>" not in n.group(0)]


def stack(pid, r):
    mx = PX[pid][r["m"] - 1]
    if not r.get("lyr") or pid not in SUNG: return mx
    other = {k: [re.findall(r"<lyric.*?</lyric>", PX[pid][m - 1][s:e], re.S) for s, e in sung_spans(PX[pid][m - 1])]
             for k, m in r["lyr"].items()}
    out, cur = [], 0
    for j, (s, e) in enumerate(sung_spans(mx)):
        note = mx[s:e]
        for k in sorted(other):
            for ly in other[k][j]:
                note = note.replace("</note>", re.sub(r'number="\d+"', f'number="{k}"', ly) + "</note>")
        out.append(mx[cur:s] + note); cur = e
    return "".join(out) + mx[cur:]


# ---------------------------------------------------------------- layout, marks, repeats
def direction(x, place="above"): return f'<direction placement="{place}">{x}</direction>'


def words(t, bold=False):
    st = ' font-weight="bold"' if bold else ' font-style="italic"'
    return f"<direction-type><words{st}>{escape(t)}</words></direction-type>"


BREAKS = set()          # a new system at each section, then every --per-system measures; a lone last measure joins
starts = [i for i, r in enumerate(R) if i == 0 or r.get("mark") or r.get("break")] + [len(R)]
for s0, s1 in zip(starts, starts[1:]):
    cuts = list(range(s0, s1, a.per_system))
    if len(cuts) > 1 and s1 - cuts[-1] == 1: cuts.pop()
    BREAKS.update(c for c in cuts if c)

REPEAT = {pid: [False] * len(R) for pid in PIDS}
if not a.no_repeat_signs:
    for pid in [p for p in PIDS if p not in SUNG]:
        for i in range(1, len(R)):
            r, q = R[i], R[i - 1]
            if r.get("mark") or r.get("fwd") or r.get("ending") or q.get("back"): continue
            cur = PX[pid][r["m"] - 1]
            sounds = "<pitch>" in cur or "<unpitched>" in cur          # an empty bar is a rest, not a repeat
            tied = "<tie " in cur or "<tie " in PX[pid][q["m"] - 1]    # a % under a tie breaks the tie in playback
            REPEAT[pid][i] = sounds and not tied and music(cur) == music(PX[pid][q["m"] - 1])


def mstyle(pid, kind):
    body = '<measure-repeat type="start">1</measure-repeat>' if kind == "start" else '<measure-repeat type="stop"/>'
    return "".join(f'<measure-style number="{s}">{body}</measure-style>' if STAVES[pid] > 1 else
                   f"<measure-style>{body}</measure-style>" for s in range(1, STAVES[pid] + 1))


def edit(pid, i, r, mx, top):
    x = inner(mx)
    x = re.sub(r"<print[^>]*/>", "", x)
    x = re.sub(r"<direction[^>]*>\s*<direction-type>\s*<rehearsal>.*?</direction>", "", x, flags=re.S)
    if i: x = re.sub(r"<direction[^>]*>\s*<direction-type>\s*<metronome>.*?</direction>", "", x, flags=re.S)
    pre, post, left, right = [], [], [], []
    if top and i in BREAKS: pre.append('<print new-system="yes"/>')
    if r.get("fwd"): left.append('<bar-style>heavy-light</bar-style><repeat direction="forward"/>')
    if r.get("ending"):
        n, kind = r["ending"]
        if kind in ("start", "both"): left.append(f'<ending number="{n}" type="start">{n}.</ending>')
        if kind in ("stop", "discontinue", "both"):
            right.append(f'<ending number="{n}" type="{"discontinue" if kind == "discontinue" else "stop"}"/>')
    if r.get("back"): right[:0] = ["<bar-style>light-heavy</bar-style>"]; right.append('<repeat direction="backward"/>')
    if r.get("final"): right.append("<bar-style>light-heavy</bar-style>")
    if top:
        if r.get("segno"): pre.append(direction("<direction-type><segno/></direction-type>" + '<sound segno="segno"/>'))
        if r.get("coda"): pre.append(direction("<direction-type><coda/></direction-type>" + words("Coda", True)
                                               + '<sound coda="coda"/>'))
        if r.get("mark"): pre.append(direction(f'<direction-type><rehearsal enclosure="rectangle">{escape(r["mark"])}'
                                               "</rehearsal></direction-type>"))
        if r.get("text"): pre.append(direction(words(r["text"])))
        if r.get("tocoda"): post.append(direction(words("To Coda") + "<direction-type><coda/></direction-type>"
                                                  '<sound tocoda="coda"/>'))
        if r.get("dc"): post.append(direction(words("D.C. al Coda", True) + '<sound dacapo="yes"/>'))
        if r.get("ds"): post.append(direction(words("D.S. al Coda", True) + '<sound dalsegno="segno"/>'))
    ms = ""
    if REPEAT[pid][i] and not (i and REPEAT[pid][i - 1]): ms = mstyle(pid, "start")
    elif not REPEAT[pid][i] and i and REPEAT[pid][i - 1]: ms = mstyle(pid, "stop")
    m = re.match(r"(\s*<attributes>.*?</attributes>)?(.*)", x, re.S)
    attrs, rest = m.group(1) or "", m.group(2)
    if ms: attrs = attrs.replace("</attributes>", ms + "</attributes>") if attrs else f"<attributes>{ms}</attributes>"
    bl = f'<barline location="left">{"".join(left)}</barline>' if left else ""
    br = f'<barline location="right">{"".join(right)}</barline>' if right else ""
    return f'<measure number="{i + 1}">' + attrs + bl + "".join(pre) + rest + "".join(post) + br + "</measure>"


body = "".join(f'<part id="{pid}">' + "".join(edit(pid, i, r, stack(pid, r), pid == PIDS[0]) for i, r in enumerate(R))
               + "</part>" for pid in PIDS)
xml = head + body + "</score-partwise>\n"

# ---------------------------------------------------------------- MuseScore: convert, make jumps playable, silence
JUMPS = {
    "To Coda": "<Marker>\n<style>repeat_right</style>\n<text>To Coda <sym>coda</sym></text>\n<label>coda</label>\n</Marker>",
    "D.C. al Coda": "<Jump>\n<style>repeat_right</style>\n<text>D.C. al Coda</text>\n<jumpTo>start</jumpTo>\n"
                    "<playUntil>coda</playUntil>\n<continueAt>codab</continueAt>\n</Jump>",
    "D.S. al Coda": "<Jump>\n<style>repeat_right</style>\n<text>D.S. al Coda</text>\n<jumpTo>segno</jumpTo>\n"
                    "<playUntil>coda</playUntil>\n<continueAt>codab</continueAt>\n</Jump>",
    "Coda": "<Marker>\n<style>repeat_left</style>\n<text><sym>coda</sym> Coda</text>\n<label>codab</label>\n</Marker>",
}


def jumps(t):
    """MuseScore 4.7 imports MusicXML jumps as plain text: turn them into Marker / Jump elements (they then play)."""
    pat = re.compile(r"<StaffText>\s*<eid>[^<]*</eid>\s*<text>((?:(?!</text>).)*)</text>\s*</StaffText>\s*", re.S)
    for mm in list(pat.finditer(t))[::-1]:
        plain = re.sub(r"<sym>coda</sym>|<[^>]+>", "", mm.group(1)).strip()
        if plain not in JUMPS: continue
        t = t[:mm.start()] + t[mm.end():]
        k = t.rfind("<Measure>", 0, mm.start()); v = t.find("<voice>", k)
        t = t[:v] + JUMPS[plain] + "\n" + t[v:]
    return t


def silence(t):
    """As build.py: chord symbols, rhythm slashes and TAB staves do not play (the notation staff does)."""
    t = t.replace("<Harmony>", "<Harmony>\n<play>0</play>")
    t = re.sub(r"<Note>((?:(?!</Note>).)*?<head>slash</head>)", r"<Note>\n<play>0</play>\1", t, flags=re.S)
    n_staff, tab_ids = 0, set()
    for part in re.findall(r"<Part\b.*?</Part>", t, flags=re.S):
        for st in re.findall(r"<Staff\b.*?</Staff>", part, flags=re.S):
            n_staff += 1
            if 'group="tablature"' in st: tab_ids.add(str(n_staff))
    cuts = [(mm.start(), mm.group(1)) for mm in re.finditer(r'<Staff id="(\d+)">', t)] + [(len(t), None)]
    segs = [t[:cuts[0][0]]]
    for (p0, sid), (p1, _) in zip(cuts, cuts[1:]):
        seg = t[p0:p1]
        segs.append(seg.replace("<Note>", "<Note>\n<play>0</play>") if sid in tab_ids else seg)
    return "".join(segs)


ms_bin = shutil.which("mscore") or shutil.which("mscore4") or shutil.which("musescore")
env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
fx, mz, pdf, mid = OUT + ".musicxml", OUT + ".mscz", OUT + ".pdf", OUT + ".mid"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(fx, "w").write(xml)
for f in (mz, pdf, mid):
    if os.path.exists(f): os.remove(f)
subprocess.run([ms_bin, "-o", mz, fx], env=env, capture_output=True, text=True)
if not os.path.exists(mz): raise SystemExit("MuseScore could not import " + fx)
with zipfile.ZipFile(mz) as z: files = {n: z.read(n) for n in z.namelist()}
STYLE = {"lyricsMinDistance": "1.0", "createMultiMeasureRests": "1" if a.multirest else "0", "minEmptyMeasures": "2"}
for n in list(files):
    if n.endswith(".mscx"): files[n] = jumps(silence(files[n].decode())).encode()
    if n.endswith(".mss"):
        st = files[n].decode()
        for k, v in STYLE.items():
            st = re.sub(f"<{k}>[^<]*</{k}>", f"<{k}>{v}</{k}>", st) if f"<{k}>" in st else \
                st.replace("</Style>", f"<{k}>{v}</{k}>\n  </Style>", 1)
        files[n] = st.encode()
with zipfile.ZipFile(mz, "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items(): z.writestr(n, b)
for target in (pdf, mid): subprocess.run([ms_bin, "-o", target, mz], env=env, capture_output=True, text=True)
pages = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1)
n_rep = sum(sum(v) for v in REPEAT.values())
print(f"{len(R)} printed measures (written out: {NW}) -> {pdf}  ({pages} pages, {n_rep} one-bar repeat signs)")

# ---------------------------------------------------------------- the short score must play the written-out music
src_mid = os.path.splitext(SRC)[0] + ".mid"
if os.path.exists(src_mid):
    try:
        import mido

        def notes(f):
            out, t = [], 0.0
            for msg in mido.MidiFile(f):
                t += msg.time
                if msg.type == "note_on" and msg.velocity > 0: out.append((round(t, 2), msg.note))
            return sorted(out)
        A_, B_ = notes(src_mid), notes(mid)
        same = len(A_) == len(B_) and all(x[1] == y[1] and abs(x[0] - y[0]) < 0.05 for x, y in zip(A_, B_))
        print(f"playback check: written-out {len(A_)} notes, short score {len(B_)} notes -> "
              + ("the same music" if same else "DIFFERENT: check the roadmap (repeats, endings, jumps)"))
    except ImportError:
        print("playback check skipped (mido not installed)")
