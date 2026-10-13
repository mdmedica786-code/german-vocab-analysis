#!/usr/bin/env python3
"""b2chk.py 'w1, w2, ...'  -> prints which candidates already exist (main bank or B2 bank); prints the NEW ones last."""
import sys, csv
sys.path.insert(0, "work")
import b2
have = b2.main_lemmas() | {r["lemma"].lower() for r in b2.load()}
c = [x.strip() for x in " ".join(sys.argv[1:]).split(",") if x.strip()]
old = [x for x in c if x.lower() in have]; new = [x for x in c if x.lower() not in have]
print("EXIST (%d):" % len(old), ", ".join(old)); print("NEW (%d)" % len(new))
