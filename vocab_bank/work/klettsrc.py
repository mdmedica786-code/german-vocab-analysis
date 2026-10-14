#!/usr/bin/env python3
"""klettsrc.py - work list for the words of the Klett 'Kontext B2' glossary (source_lists/German_B2_Wordlist_from_Klett_Kontext.csv
plus a few PDF-only items in work/klett_extra.txt) that are still NOT an entry of the banks.

  python3 work/klettsrc.py next [N]      next N open words:  lemma | article | plural | forms | English gloss from the list
  python3 work/klettsrc.py skip "w1, w2" [reason]   put words on the skip list (work/klett_skipped.txt)
  python3 work/klettsrc.py status
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_lib import ROOT, SRC, Universe, deumlaut, fold, rd  # noqa: E402

CSV = SRC / "German_B2_Wordlist_from_Klett_Kontext.csv"
EXTRA = ROOT / "work" / "klett_extra.txt"
SKIP = ROOT / "work" / "klett_skipped.txt"
UMLAUT = {"a": "ä", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö", "U": "Ü"}


def plural_from_code(lemma, code):
    c = code.replace("&quot;", '"').replace("¨", '"').replace(" ", "")
    if not c or c in ("-", "–") and False:
        return ""
    um = c.startswith('"')
    c = c.lstrip('"')
    suffix = c[1:] if c.startswith("-") else c
    if c == "-" or c == "":
        suffix = ""
    stem = lemma
    if um:
        for i in range(len(stem) - 1, -1, -1):
            m = re.match(r"(au|[aouAOU])", stem[i:i + 2]) if False else None
        # umlaut the last stressed vowel: last occurrence of a/o/u/au (before the final consonants)
        mm = list(re.finditer(r"au|[aou]", stem))
        if mm:
            m = mm[-1]
            rep = "äu" if m.group(0) == "au" else UMLAUT[m.group(0)]
            stem = stem[:m.start()] + rep + stem[m.end():]
    if suffix in ("se", "nen", "ssen") and lemma.endswith(("is", "in", "us")):
        base = lemma + suffix[-2:] if suffix == "se" and lemma.endswith("is") else lemma + suffix
        return base if suffix != "se" else lemma + "se"
    return stem + suffix


def parse(g):
    g = g.replace("&quot;", '"').strip()
    raw = g
    refl = bool(re.search(r"\(sich[^)]*\)|^sich ", g))
    g2 = re.sub(r"\(\d\)", "", g)
    g2 = re.sub(r"\([^)]*\)", " ", g2)
    parts = [p.strip() for p in g2.split(",")]
    head = re.sub(r"^sich\s+", "", parts[0]).replace("|", "")
    if re.search(r"[a-zäöü]-[a-zäöü]", head):
        head = head.replace("-", "")
    head = re.sub(r"\s+", " ", head).strip()
    art = ""
    for p in parts[1:3]:
        if p in ("der", "die", "das", "der/die", "der/das", "die/das"):
            art = p
    mm = re.match(r"^(der|die|das)\s+(.*)$", head)
    if mm:
        art, head = mm.group(1), mm.group(2)
    code = next((p for p in parts[1:] if re.match(r'^[-¨"]', p)), "")
    pl_note = "(Pl.)" if re.search(r"\(Pl\.?\)", raw) else ("(Sg.)" if re.search(r"\(Sg\.?\)", raw) else "")
    forms = ", ".join(p for p in parts[1:] if re.search(r"\b(hat|ist)\b|\w+t\s", p) and not re.match(r'^[-¨"]', p) and p not in ("der", "die", "das"))
    return dict(raw=raw, lemma=head, art=art, plural=plural_from_code(head, code) if code and art else "", code=code, note=pl_note, forms=forms, refl=refl)


def load_skip():
    out = {}
    if SKIP.exists():
        for ln in SKIP.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith("#"):
                w, _, why = ln.partition("|")
                out[fold(w.strip())] = why.strip()
    return out


def items():
    res = []
    for r in rd(CSV):
        d = parse(r["German"])
        d["en"] = r["English"]
        res.append(d)
    if EXTRA.exists():
        for ln in EXTRA.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith("#"):
                g, _, en = ln.partition("|")
                d = parse(g)
                d["en"] = en.strip() or "(PDF only)"
                res.append(d)
    return res


def open_items():
    U = Universe()
    skip = load_skip()
    seen, out = set(), []
    allitems = items()
    for d in allitems:
        w = d["lemma"]
        if not w or w.startswith("-") or fold(w) in seen:
            continue
        seen.add(fold(w))
        if U.is_entry(w) or fold(w) in skip:
            continue
        out.append(d)
    return allitems, out, skip


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    allitems, open_, skip = open_items()
    if cmd == "status":
        print(f"klett words {len(allitems)} | skipped {len(skip)} | open {len(open_)}")
    elif cmd == "next":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        for d in open_[:n]:
            print(f"{d['lemma']} | {d['art']} | {d['plural'] or d['note']} | {d['forms']} | {d['en'][:60]}{' | refl' if d['refl'] else ''}")
    elif cmd == "skip":
        words = [w.strip() for w in sys.argv[2].split(",") if w.strip()]
        why = sys.argv[3] if len(sys.argv) > 3 else "not useful"
        with open(SKIP, "a", encoding="utf-8") as f:
            for w in words:
                f.write(f"{w}|{why}\n")
        print("skipped", len(words))


if __name__ == "__main__":
    main()
