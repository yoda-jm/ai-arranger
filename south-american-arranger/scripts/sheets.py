"""Rehearsal sheets of a built band arrangement (OUTDIR/events.json) -> OUTDIR/lead_sheet.md and OUTDIR/grooves.md.

usage: sheets.py OUTDIR
  lead_sheet.md  per section: style, tempo, key, who sings lead; per measure the chords and the lead's words
  grooves.md     per section: every pattern the arrangement wrote (strum, arpeggio, bass, percussion, hang) on a count
                 grid, with the measures it covers and its performance note, plus the percussion stroke legend
"""
import sys, os, json, collections

OUT = sys.argv[1]
J = json.load(open(f"{OUT}/events.json")); META, EV = J["meta"], J["events"]
BAR = META["bar"]; BEAT = META.get("beat", 4); INFO = META["info"]
SECS = META.get("sections") or []


def words(evs):
    """Syllables 'Dash-' '-ing' -> words; a word cut by the barline keeps its hyphen ('quie-' | '-res')."""
    toks = [e[7] for e in evs if len(e) > 7 and e[7] and not e[5]]
    out = ""
    for i, s in enumerate(toks):
        core = s.strip("-")
        if s.startswith("-") and i > 0: out = out.rstrip(" ") + core
        else: out += ("-" if s.startswith("-") else "") + core
        out += ("-" if i == len(toks) - 1 else "") if s.endswith("-") else " "
    return out.strip()


def lead_of(s, bi):
    x = s.get("lead", {}).get(str(bi))
    return (x[0], x[1]) if x else (None, 0)


by_meas = collections.defaultdict(list)
for v, evs in EV.items():
    for e in evs: by_meas[(v, e[6])].append(e)

# ---------------------------------------------------------------- lead sheet
L = [f"# {META['title']}: lead sheet", "",
     f"{META['meter'][0]}/{META['meter'][1]}; tempos are in {'dotted quarters' if BEAT == 6 else 'quarters'}. "
     "Chords per measure (a measure split evenly when it has several). Words are the lead's.", ""]
for s in SECS:
    leads = sorted({lead_of(s, bi)[0] for bi in range(s["nbars"])} - {None})
    head = f"## {s['name']}" + (f" ({s['style']})" if s.get("style") else "")
    L += [head, "", f"key {s['key']}" + (f", tempo {s['tempo']}" if s.get("tempo") else "")
          + (", lead: " + " / ".join(f"{INFO[v][0]} ({v})" for v in leads) if leads else ", instrumental"), "",
          "| m. | chords | words |", "|---|---|---|"]
    for bi in range(s["nbars"]):
        m = s["measure"] + bi; row = s["chords"][bi]
        ch = " ".join(c for i, c in enumerate(row) if i == 0 or c != row[i - 1])
        v = lead_of(s, bi)[0]
        L.append(f"| {m} | {ch} | {words(by_meas.get((v, m), [])) if v else ''} |")
    L.append("")
open(f"{OUT}/lead_sheet.md", "w").write("\n".join(L))


# ---------------------------------------------------------------- grooves
def counts(n, unit):
    """Count line for n cells of `unit` 16ths."""
    cells = []
    for k in range(n):
        t = (k * unit) % BAR
        if t % BEAT == 0: cells.append(str(t // BEAT + 1))
        elif BEAT == 4 and t % 2 == 0: cells.append("&")
        else: cells.append(".")
    return " ".join(cells)


def ranges(ms):
    ms = sorted(ms); out = []; a = b = None
    for m in ms:
        if a is None: a = b = m
        elif m == b + 1: b = m
        else: out.append((a, b)); a = b = m
    if a is not None: out.append((a, b))
    return ", ".join(f"{x}" if x == y else f"{x}-{y}" for x, y in out)


G = [f"# {META['title']}: groove cards", "",
     "One character per cell; the count line shows the beats. `.` rest, `-` hold. Strums: D down, U up, d/u soft, "
     "x muted chop, A rolled. Arpeggios: 1 = lowest note of the chord shape. Bass: chord degrees (1 3 5 ...; "
     "< fifth below, > half step below the next chord, N the next chord's bass played early). Hang: 0 = ding (D3), k = k-th chord tone on the hang.", ""]
kits = META.get("kits", {})
for v, kit in kits.items():
    if v == "VP": continue
    inst = collections.OrderedDict()                 # instrument -> ["`B` bass", ...]  (the stroke letter ends the key)
    for k, (gm, vel, lab) in kit.items():
        name, _, desc = lab.partition(" ")
        inst.setdefault(name, []).append(f"`{k[-1]}` {desc}")
    G.append(f"- **{INFO[v][0]}**: " + "; ".join(f"{n}: " + ", ".join(x) for n, x in inst.items()))
G.append("")
for s in SECS:
    cards = s.get("cards") or []
    if not cards: continue
    G += [f"## {s['name']}" + (f" ({s['style']})" if s.get("style") else "")
          + (f", tempo {s['tempo']}" if s.get("tempo") else ""), ""]
    for c in cards:
        ms = [s["measure"] + b for b in c["bars"]]
        G.append(f"**{INFO[c['part']][0]}**, {c['kind']}, measures {ranges(ms)}" + (f": *{c['text']}*" if c.get("text") else ""))
        G.append("```")
        for name, pat in c["patterns"].items():
            if pat is None: continue
            toks = pat.replace("|", " ").split() if c["kind"] == "hang" and " " in pat.strip() \
                else [ch for ch in pat if ch not in " |"]     # hang lines are note tokens; the rest one char per cell
            per = BAR // c["unit"]                     # cells per bar: a longer pattern prints one bar per line
            w = max(len(t) for t in toks)
            G.append(f"{'count':8s} " + " ".join(x.ljust(w) for x in counts(min(per, len(toks)), c["unit"]).split()))
            for k in range(0, len(toks), per):
                lab = name if k == 0 else ""
                bar_no = f" (bar {k // per + 1})" if len(toks) > per else ""
                G.append(f"{lab:8s} " + " ".join(t.ljust(w) for t in toks[k:k + per]) + bar_no)
        G.append("```")
    G.append("")
open(f"{OUT}/grooves.md", "w").write("\n".join(G))
print(f"written: {OUT}/lead_sheet.md, {OUT}/grooves.md")
