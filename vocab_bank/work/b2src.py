#!/usr/bin/env python3
"""b2src.py - work list for the B2 bank taken from Medica's own source file beyond_goethe_B2.csv (source_lists/ at the repo top level).

  python3 work/b2src.py next [N]          next N source lemmas that are not yet in the main bank, the B2 bank or the skip list
  python3 work/b2src.py skip "w1, w2" [reason]    put lemmas on the skip list (work/b2_source_skipped.txt)
  python3 work/b2src.py status            how many are covered / skipped / still open
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / "source_lists" / "beyond_goethe_B2.csv"
SKIP = ROOT / "work" / "b2_source_skipped.txt"


def rd(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(s):
    s = s.lower().strip()
    s = re.sub(r"^(der|die|das)\s+", "", s)
    return re.sub(r"^sich\s+", "", s).strip()


def state():
    have = set()
    for f in ("vocabulary_bank.csv", "b2_vocabulary_bank.csv"):
        have |= {norm(r["lemma"]) for r in rd(ROOT / "bank_final" / f)}
    have |= {norm(r["phrase_de"]) for r in rd(ROOT / "bank_final" / "phrase_bank.csv")}
    skipped = {}
    if SKIP.exists():
        for ln in SKIP.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith("#"):
                w, _, why = ln.partition("|")
                skipped[norm(w)] = why.strip()
    src = rd(SRC)
    open_ = [r for r in src if norm(r["lemma"]) not in have and norm(r["lemma"]) not in skipped]
    return src, have, skipped, open_


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    src, have, skipped, open_ = state()
    if cmd == "status":
        covered = sum(1 for r in src if norm(r["lemma"]) in have)
        print(f"source lemmas {len(src)} | covered {covered} | skipped {len(skipped)} | open {len(open_)}")
    elif cmd == "next":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        for r in open_[:n]:
            ch = " ; ".join(r[f"chunk_{i}"] for i in (1, 2, 3) if r[f"chunk_{i}"])
            print(f"{r['lemma']} | {r['pos'].split(' ')[0]} | {r['theme'][:3]} | {r['usefulness_estimate'][:1]} | {'K' if r['in_klett_b2_list'] else '-'} | {ch}")
    elif cmd == "skip":
        words = [w.strip() for w in sys.argv[2].split(",") if w.strip()]
        why = sys.argv[3] if len(sys.argv) > 3 else "not useful"
        with open(SKIP, "a", encoding="utf-8") as f:
            for w in words:
                f.write(f"{w}|{why}\n")
        print("skipped", len(words))


if __name__ == "__main__":
    main()
