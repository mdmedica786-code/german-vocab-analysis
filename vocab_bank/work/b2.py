#!/usr/bin/env python3
"""b2.py - builder for the B2 vocabulary bank (bank_final/b2_vocabulary_bank.csv).

  python3 work/b2.py add  < compact lines   validate + append rows (all-or-nothing); saves work/b2_patches/NNN.txt
  python3 work/b2.py add NNN < file         re-apply a saved patch number after fixing it
  python3 work/b2.py status                  counts
  python3 work/b2.py validate                full check of the CSV
  python3 work/b2.py export                  writes bank_final/German_B2_Bank.xlsx

Compact line formats ('¦' separates fields; optional trailing key=value pairs: sp= rf= g= rg= nt= ck=):
  N¦Lemma¦art¦plural¦meaning¦T03¦example_de¦example_en¦collocations¦use
  V¦lemma¦pres_3sg¦preterite¦perfect¦meaning¦T03¦example_de¦example_en¦collocations¦use
  A¦lemma¦meaning¦T03¦example_de¦example_en¦collocations¦use          (adjective)
  D¦lemma¦meaning¦...                                                (adverb)
  C¦lemma¦meaning¦...                                                (conjunction)
  P¦lemma¦gov¦meaning¦T03¦example_de¦example_en¦collocations¦use    (preposition)
  F¦phrase¦meaning¦T03¦example_de¦example_en¦collocations¦use       (fixed phrase / Nomen-Verb-Verbindung)
  O¦lemma¦pos¦meaning¦...                                            (other: pronoun, particle ...)
use = tokens from USE joined by '; '   (e.g. Schreiben; Sprechen)
"""
import csv, re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "bank_final" / "b2_vocabulary_bank.csv"
MAIN = ROOT / "bank_final" / "vocabulary_bank.csv"
PATCHES = ROOT / "work" / "b2_patches"
XLSX = ROOT / "bank_final" / "German_B2_Bank.xlsx"
COLS = "id lemma pos article plural pres_3sg preterite perfect sep_prefix reflexive gov meaning_en note register level topic example_de example_en collocations exam_use check".split()
TOPICS = {"T01": "T01 Person, Familie & Beziehungen", "T02": "T02 Wohnen", "T03": "T03 Arbeit & Beruf",
          "T04": "T04 Ausbildung, Schule & Studium", "T05": "T05 Gesundheit & Körper", "T06": "T06 Essen & Trinken",
          "T07": "T07 Einkaufen, Kleidung & Geld", "T08": "T08 Reisen, Verkehr & Orte",
          "T09": "T09 Behörden, Post & Dienstleistungen", "T10": "T10 Freizeit, Sport, Kultur & Medien",
          "T11": "T11 Natur, Umwelt, Wetter & Tiere", "T12": "T12 Gesellschaft, Politik, Recht & Geschichte",
          "T13": "T13 Zeit, Zahlen, Maße & Mengen", "T14": "T14 Gefühle, Charakter & Meinungen",
          "T15": "T15 Sprache, Kommunikation & Denken", "T16": "T16 Allgemein (Funktionswörter, abstrakter Wortschatz)"}
USE = {"Lesen", "Hören", "Schreiben", "Sprechen", "Alltag", "Grammatik", "Medien", "Wissenschaft"}
REG = {"neutral", "formal", "informal", "colloquial", "technical", "regional"}
POS = {"noun", "verb", "adjective", "adverb", "preposition", "conjunction", "pronoun", "particle", "phrase", "numeral"}
ART = {"der", "die", "das", "der/die", "der/das", "die/das", "(Pl.)"}
BAD = re.compile(r"<\s*/?\s*[A-Za-z!][^>]*>|\*\*|`|\t|\n|\r|¦|&[a-z]+;")
KIND = {"N": "noun", "V": "verb", "A": "adjective", "D": "adverb", "C": "conjunction", "P": "preposition", "F": "phrase"}


def load():
    if not BANK.exists():
        return []
    with open(BANK, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save(rows):
    with open(BANK, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def main_lemmas():
    with open(MAIN, encoding="utf-8-sig", newline="") as f:
        return {r["lemma"].strip().lower() for r in csv.DictReader(f)}


def parse(line):
    p = [x.strip() for x in line.split("¦")]
    k = p[0]
    extra = {}
    # trailing key=value pairs
    while len(p) > 1 and re.match(r"^(sp|rf|g|rg|nt|ck)=", p[-1]):
        a, _, b = p.pop().partition("=")
        extra[a] = b
    r = {c: "" for c in COLS}
    r["level"] = "B2"
    r["register"] = extra.get("rg", "neutral")
    r["sep_prefix"] = extra.get("sp", ""); r["reflexive"] = extra.get("rf", ""); r["gov"] = extra.get("g", "")
    r["note"] = extra.get("nt", ""); r["check"] = extra.get("ck", "")
    try:
        if k == "N":
            _, lem, art, pl, m, t, ex, en, col, use = p
            r.update(lemma=lem, pos="noun", article=art, plural=pl, meaning_en=m, topic=t, example_de=ex, example_en=en, collocations=col, exam_use=use)
        elif k == "V":
            _, lem, ps, pt, pf, m, t, ex, en, col, use = p
            r.update(lemma=lem, pos="verb", pres_3sg=ps, preterite=pt, perfect=pf, meaning_en=m, topic=t, example_de=ex, example_en=en, collocations=col, exam_use=use)
        elif k in "ADC":
            _, lem, m, t, ex, en, col, use = p
            r.update(lemma=lem, pos=KIND[k], meaning_en=m, topic=t, example_de=ex, example_en=en, collocations=col, exam_use=use)
        elif k == "P":
            _, lem, g, m, t, ex, en, col, use = p
            r.update(lemma=lem, pos="preposition", gov=g, meaning_en=m, topic=t, example_de=ex, example_en=en, collocations=col, exam_use=use)
        elif k == "F":
            _, lem, m, t, ex, en, col, use = p
            r.update(lemma=lem, pos="phrase", meaning_en=m, topic=t, example_de=ex, example_en=en, collocations=col, exam_use=use)
        elif k == "O":
            _, lem, pos, m, t, ex, en, col, use = p
            r.update(lemma=lem, pos=pos, meaning_en=m, topic=t, example_de=ex, example_en=en, collocations=col, exam_use=use)
        else:
            return None, f"unknown kind '{k}'"
    except ValueError:
        return None, f"wrong number of fields for kind {k} ({len(p)})"
    return r, None


def check_row(r):
    e, w = [], []
    for c in COLS:
        if BAD.search(r[c]):
            e.append(f"{c}: forbidden character/markup")
    if r["topic"] not in TOPICS:
        e.append(f"topic '{r['topic']}' not T01-T16")
    else:
        r["topic"] = TOPICS[r["topic"]]
    if r["pos"] not in POS: e.append(f"pos '{r['pos']}'")
    if r["register"] not in REG: e.append(f"register '{r['register']}'")
    toks = [t.strip() for t in r["exam_use"].split(";") if t.strip()]
    if not toks or any(t not in USE for t in toks): e.append(f"exam_use '{r['exam_use']}'")
    if r["pos"] == "noun":
        if r["article"] not in ART: e.append(f"article '{r['article']}'")
        if not r["plural"]: e.append("plural missing")
        if r["lemma"][:1].islower(): e.append("noun lemma must be capitalised")
    if r["pos"] == "verb":
        for c in ("pres_3sg", "preterite", "perfect"):
            if not r[c]: e.append(f"{c} missing")
        if r["perfect"] and not re.match(r"^(hat|ist|hat/ist|ist/hat|hat sich|ist sich)\b", r["perfect"]): e.append(f"perfect '{r['perfect']}'")
        if not r["meaning_en"].startswith("to "): e.append("verb meaning must start with 'to '")
    if r["pos"] == "preposition" and not r["gov"]: e.append("gov missing")
    m = r["meaning_en"]
    if not m: e.append("meaning missing")
    if len([s for s in m.split(";") if s.strip()]) > 3: e.append("meaning: more than 3 senses")
    ex = r["example_de"]; en = r["example_en"]
    if not ex or not en: e.append("example missing")
    else:
        n = len(ex.split())
        if n < 4 or n > 25: e.append(f"example_de length {n} words")
        if not re.search(r"[.?!]$", ex): e.append("example_de must end with . ? !")
        if not re.search(r"[.?!]$", en): e.append("example_en must end with . ? !")
        words = [re.sub(r"[^a-zäöüß]", "", x.lower()) for x in r["lemma"].split()]
        words = [x for x in words if len(x) >= 4 and x not in ("sich", "eine", "einen", "einem", "einer")]
        stem = r["sep_prefix"] and r["lemma"][len(r["sep_prefix"]):] or r["lemma"]
        if r["pos"] == "phrase" or len(r["lemma"].split()) > 1:
            ok = any(x[:4] in ex.lower() for x in words) if words else True
        else:
            key = re.sub(r"[^a-zäöüß]", "", stem.lower())[:4]
            ok = (not key) or key in ex.lower().replace("-", "") or bool(r["sep_prefix"] and r["sep_prefix"] in ex.lower())
        if not ok: w.append("lemma not visible in example")
    cols = [x for x in r["collocations"].split(" | ") if x.strip()]
    if r["pos"] in ("noun", "verb", "adjective") and len(cols) < 2: e.append("collocations: need at least 2 (separated by ' | ')")
    if r["pos"] == "phrase" and len(cols) < 1: e.append("collocations missing")
    return e, w


def cmd_add(num=None):
    text = sys.stdin.read()
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    rows = load()
    have = {x["lemma"].strip().lower() for x in rows}
    main = main_lemmas()
    ids = [int(x["id"][1:]) for x in rows]
    nxt = max(ids) + 1 if ids else 1
    new, errs, skipped, warns = [], [], [], []
    for ln in lines:
        r, err = parse(ln)
        if err:
            errs.append(f"{ln[:50]}: {err}"); continue
        lk = r["lemma"].strip().lower()
        if lk in main or lk in have:
            skipped.append(f"{r['lemma']} ({'main bank' if lk in main else 'B2 bank'})"); continue
        e, w = check_row(r)
        if e: errs.append(f"{r['lemma']}: " + "; ".join(e))
        if w: warns.append(f"{r['lemma']}: " + "; ".join(w))
        have.add(lk)
        new.append(r)
    if errs:
        print(f"REJECTED: {len(errs)} error(s), nothing written")
        for x in errs[:40]: print("  -", x)
        PATCHES.mkdir(exist_ok=True)
        n = int(num) if num else len(list(PATCHES.glob("*.txt"))) + 1
        (PATCHES / f"{n:03d}.txt").write_text(text, encoding="utf-8")
        print(f"saved as patch {n:03d} (fix, then: python3 work/b2.py add {n:03d} < work/b2_patches/{n:03d}.txt)")
        return
    for r in new:
        r["id"] = f"D{nxt:04d}"; nxt += 1
    save(rows + new)
    PATCHES.mkdir(exist_ok=True)
    n = int(num) if num else len(list(PATCHES.glob("*.txt"))) + 1
    (PATCHES / f"{n:03d}.txt").write_text(text, encoding="utf-8")
    print(f"added {len(new)} rows (total {len(rows)+len(new)}), skipped duplicates: {len(skipped)}; patch {n:03d}")
    if skipped: print("  skipped:", ", ".join(skipped[:40]))
    if warns: print(f"  warnings ({len(warns)}):", "; ".join(warns[:12]))


def cmd_edit():
    """ID or lemma ¦ key=value ... (keys: m ex en col use art pl ps pt pf g rg nt ck t lv). Value '-' clears."""
    AL = dict(m="meaning_en", ex="example_de", en="example_english", col="collocations", use="exam_use", art="article", pl="plural",
              ps="pres_3sg", pt="preterite", pf="perfect", g="gov", rg="register", nt="note", ck="check", t="topic", sp="sep_prefix", rf="reflexive")
    AL["en"] = "example_en"
    rows = load(); idx = {r["id"]: r for r in rows}; byl = {r["lemma"]: r for r in rows}; n = 0; errs = []
    for ln in sys.stdin.read().splitlines():
        if not ln.strip() or ln.startswith("#"): continue
        p = [x.strip() for x in ln.split("¦")]
        r = idx.get(p[0]) or byl.get(p[0])
        if not r: errs.append(f"not found: {p[0]}"); continue
        for kv in p[1:]:
            k, _, v = kv.partition("=")
            k = AL.get(k, k)
            if k not in COLS: errs.append(f"{p[0]}: bad key {k}"); continue
            r[k] = "" if v == "-" else (TOPICS.get(v, v) if k == "topic" else v)
        rr = dict(r); rr["topic"] = r["topic"][:3]
        e, _ = check_row(rr)
        if e: errs.append(f"{p[0]}: " + "; ".join(e))
        n += 1
    if errs:
        print("REJECTED (nothing written):"); [print("  -", x) for x in errs[:30]]; return
    save(rows); print("edited", n)


def cmd_validate():
    rows = load(); bad = 0; seen = set(); main = main_lemmas()
    for r in rows:
        rr = dict(r); rr["topic"] = r["topic"][:3]
        e, _ = check_row(rr)
        lk = r["lemma"].lower()
        if lk in seen: e.append("duplicate lemma")
        if lk in main: e.append("also in main bank")
        seen.add(lk)
        if e: bad += 1; print(r["id"], r["lemma"], e)
    print(f"validate: {len(rows)} rows, {bad} with errors")


def cmd_status():
    from collections import Counter
    rows = load()
    print("rows", len(rows)); print("pos", dict(Counter(r["pos"] for r in rows)))
    print("topic", sorted(Counter(r["topic"][:3] for r in rows).items()))
    print("use", Counter(t.strip() for r in rows for t in r["exam_use"].split(";")).most_common())
    print("flagged", sum(1 for r in rows if r["check"]))


def cmd_export():
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    rows = load()
    wb = Workbook(); ws = wb.active; ws.title = "B2 Vocabulary"
    ws.append(COLS)
    for r in rows: ws.append([r[c] for c in COLS])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F4E78")
    widths = dict(id=8, lemma=24, pos=11, article=8, plural=16, pres_3sg=16, preterite=16, perfect=18, sep_prefix=9, reflexive=9, gov=14, meaning_en=34, note=24, register=10, level=6, topic=26, example_de=52, example_en=48, collocations=48, exam_use=18, check=10)
    for i, c in enumerate(COLS, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = widths[c]
    ws.freeze_panes = "C2"; ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(XLSX)
    print("exported", XLSX.name, len(rows))


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "status"
    if a == "add": cmd_add(sys.argv[2] if len(sys.argv) > 2 else None)
    elif a == "status": cmd_status()
    elif a == "validate": cmd_validate()
    elif a == "edit": cmd_edit()
    elif a == "export": cmd_export()
