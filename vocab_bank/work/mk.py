#!/usr/bin/env python3
"""mk.py <bank> [NNN] < compact lines  ->  work/patches/NNN.json (+ NNN.txt) and applies it.
Line: id¦key=value¦key=value   ('¦' separates fields; value '-' clears a cell; NEW (or empty id) = new Redemittel row)
Redemittel: a line '@B1-01' sets wave/cat_id/category for following NEW lines.
Aliases (vocab): pl plural, art article, ps pres_3sg, pt preterite, pf perfect, sp sep_prefix, rf reflexive, ef extra_forms,
 m meaning_en, os other_senses, nt note, rg register, lv level, lb level_basis, tp topic, med medical, ex example_de, en example_en,
 es example_source, col collocations, ck check.  (phrase) ph phrase_de, pat pattern, fn function, gn grammar_note, v variants.
 (redemittel) fn function, sp speaker, au audience, de redemittel_de, gn grammar_note, v variants, eu exam_use, pr priority.
Auto: ex given while example_de empty -> example_source=claude (vocab); level newly set -> level_basis=estimated if empty."""
import sys, json, csv, subprocess, os
from pathlib import Path
W = Path(__file__).resolve().parent; ROOT = W.parent
bank = sys.argv[1]
AL = {"vocab": dict(pl="plural", art="article", ps="pres_3sg", pt="preterite", pf="perfect", sp="sep_prefix", rf="reflexive", ef="extra_forms",
                    m="meaning_en", os="other_senses", nt="note", rg="register", lv="level", lb="level_basis", tp="topic", med="medical",
                    ex="example_de", en="example_en", es="example_source", col="collocations", ck="check", g="gov", ps_="pres_3sg"),
      "phrase": dict(ph="phrase_de", pat="pattern", fn="function", rg="register", lv="level", m="meaning_en", ex="example_de", en="example_en",
                     gn="grammar_note", v="variants", ck="check"),
      "redemittel": dict(fn="function", sp="speaker", au="audience", de="redemittel_de", m="meaning_en", lv="level", rg="register", ex="example_de",
                         en="example_en", gn="grammar_note", v="variants", eu="exam_use", pr="priority", ck="check", cat="cat_id")}[bank]
FILES = {"vocab": "vocabulary_bank.csv", "phrase": "phrase_bank.csv", "redemittel": "redemittel_bank.csv"}
cur = {}
PFN = []
if bank == "phrase":
    with open(ROOT / "bank_final" / "phrase_bank.csv", encoding="utf-8-sig", newline="") as f_:
        PFN = sorted({r_["function"] for r_ in csv.DictReader(f_) if r_["function"]})
if bank != "redemittel":
    with open(ROOT / "bank_final" / FILES[bank], encoding="utf-8-sig", newline="") as f:
        cur = {r["id"]: r for r in csv.DictReader(f)}
plan = {}
with open(ROOT / "input" / "redemittel_plan.csv", encoding="utf-8-sig", newline="") as f:
    plan = {r["cat_id"]: r for r in csv.DictReader(f)}
rows, cols, src, dflt = [], [], [], {}
for line in sys.stdin.read().splitlines():
    line = line.strip()
    if not line or line.startswith("#"): continue
    src.append(line)
    if line.startswith("@"):
        c = plan[line[1:]]; dflt = {"wave": c["wave"], "cat_id": c["cat_id"], "category": c["category_de"]}; continue
    if line.startswith("%"):  # defaults for following NEW rows: %sp=Beide¦au=Alle¦lv=B1
        for p_ in line[1:].split("¦"):
            k_, _, v_ = p_.partition("="); dflt[AL.get(k_.strip(), k_.strip())] = v_.strip()
        continue
    parts = line.split("¦"); rid = parts[0].strip()
    d = {}
    if bank == "redemittel":
        if rid in ("NEW", ""):
            rid = ""; d.update(dflt)
    for p in parts[1:]:
        k, _, v = p.partition("=")
        k = AL.get(k.strip(), k.strip()); v = v.strip()
        d[k] = "__CLEAR__" if v == "-" else v
        if bank == "phrase" and k == "function" and v != "-":
            m_ = [f for f in PFN if f.split(" (")[0].lower().startswith(v.lower())]
            if len(m_) == 1: d[k] = m_[0]
    if bank == "vocab" and rid in cur:
        r = cur[rid]
        if d.get("example_de") and not r["example_de"] and "example_source" not in d: d["example_source"] = "claude"
        if d.get("level") and not r["level"] and "level_basis" not in d and not r["level_basis"]: d["level_basis"] = "estimated"
    if bank == "redemittel" and rid == "" :
        d.setdefault("source", "claude")
    d["id"] = rid; rows.append(d)
    for k in d:
        if k not in cols: cols.append(k)
cols = ["id"] + [c for c in cols if c != "id"]
pd = W / "patches"; pd.mkdir(exist_ok=True)
n = int(sys.argv[2]) if len(sys.argv) > 2 else len(list(pd.glob("*.json"))) + 1
patch = {"bank": bank, "cols": cols, "rows": [[r.get(c, "") for c in cols] for r in rows]}
(pd / f"{n:03d}.json").write_text(json.dumps(patch, ensure_ascii=False), encoding="utf-8")
(pd / f"{n:03d}.txt").write_text("\n".join(src) + "\n", encoding="utf-8")
env = dict(os.environ, PYTHONUTF8="1")
sys.exit(subprocess.call([sys.executable, str(W / "bank_tools.py"), "apply", str(pd / f"{n:03d}.json")], env=env))
