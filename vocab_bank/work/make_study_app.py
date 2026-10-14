#!/usr/bin/env python3
"""make_study_app.py - builds STUDY_HERE/German_Study.html (one file, works offline) from the CSV banks.

  python3 work/make_study_app.py
"""
import csv, json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_util import AudioLookup  # noqa: E402
from studylist import mark_not_in_list  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BANKS = ROOT / "bank_final"
OUT = ROOT.parent / "STUDY_HERE" / "German_Study.html"


def rd(name):
    with open(BANKS / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def topic(t):
    return t.split(" ", 1)[1] if t and " " in t else t


AUDIO = AudioLookup()  # native recordings from download_audio.py (empty if none were downloaded)


def word_rec(r, kind):
    pos, art = r["pos"], (r.get("article") or "").strip()
    t = f"{art} {r['lemma']}" if pos == "noun" and art in ("der", "die", "das") else r["lemma"]
    f = []
    if pos == "noun" and r.get("plural"):
        f.append("Plural: " + r["plural"])
    if pos == "verb":
        forms = ", ".join(x for x in (r.get("pres_3sg"), r.get("preterite"), r.get("perfect")) if x)
        if forms:
            f.append(forms)
        if r.get("reflexive"):
            f.append("reflexive")
        if r.get("gov"):
            f.append("+ " + r["gov"])
    if r.get("extra_forms"):
        f.append(r["extra_forms"])
    if r.get("note"):
        f.append(r["note"])
    return dict(i=r["id"], k=kind, t=t, m=r["meaning_en"], p=pos, f=" · ".join(f), d=r.get("example_de", ""), e=r.get("example_en", ""),
                c=r.get("collocations", ""), l=r.get("level", ""), g=topic(r["topic"]), s=1 if r.get("skip") else 0,
                md=1 if (r.get("medical") or r["topic"].startswith("M")) else 0, a=AUDIO.get(r["lemma"]))


def main():
    recs = []
    m = mark_not_in_list(rd("vocabulary_bank.csv"))
    m.sort(key=lambda r: int(r["study_order"]) if r.get("study_order", "").isdigit() else 10**9)
    recs += [word_rec(r, "M") for r in m]
    recs += [word_rec(r, "B") for r in rd("b2_vocabulary_bank.csv")]
    for r in sorted(rd("phrase_bank.csv"), key=lambda r: int(r["order_hint"]) if r["order_hint"].isdigit() else 10**9):
        recs.append(dict(i=r["id"], k="P", t=r["phrase_de"], m=r["meaning_en"], p="", f=r.get("grammar_note", ""), d=r["example_de"], e=r["example_en"],
                         c=r.get("variants", ""), l=r.get("level", ""), g=r["function"].split(" (")[0], s=0, md=0))
    for r in rd("redemittel_bank.csv"):
        recs.append(dict(i=r["id"], k="R", t=r["redemittel_de"], m=r["meaning_en"], p="", f=r.get("grammar_note", ""), d=r["example_de"], e=r["example_en"],
                         c=r.get("variants", ""), l=r.get("level", ""), g=f"{r['cat_id']} {r['category']}", s=0,
                         md=1 if r.get("speaker") in ("Arzt", "Patient", "Pflege") else 0))
    for c in recs:  # drop empty / zero fields to save space
        for k in [k for k, v in c.items() if v in ("", 0)]:
            del c[k]
    data = json.dumps(recs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")
    html = (ROOT / "work" / "study_app_template.html").read_text(encoding="utf-8").replace("__DATA__", data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{sum(1 for c in recs if c.get('a'))} cards with native audio")
    print(f"{len(recs)} cards -> {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
