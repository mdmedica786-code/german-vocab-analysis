#!/usr/bin/env python3
"""inc.py [N] [skip=no|yes] -> compact view of next N incomplete vocab rows (study_order)."""
import csv, sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
sk = sys.argv[2] if len(sys.argv) > 2 else ""
r = list(csv.DictReader(open("bank_final/vocabulary_bank.csv", encoding="utf-8-sig", newline="")))
inc = [x for x in r if x["todo"] and x["skip"] == sk]
inc.sort(key=lambda x: int(x["study_order"] or 99999))
print(len(inc), "incomplete")
K = [("pos","pos"),("article","art"),("plural","pl"),("pres_3sg","ps"),("preterite","pt"),("perfect","pf"),("sep_prefix","sp"),("reflexive","rf"),("gov","g"),("meaning_en","m"),("level","lv"),("topic","tp"),("medical","med"),("example_de","ex"),("example_en","en"),("check","ck"),("note","nt"),("skip_reason","why"),("nw_chapter","ch")]
for x in inc[:N]:
    s = f"{x['id']} | {x['lemma']}"
    for k, a in K:
        v = x[k]
        if k == "topic": v = v[:3]
        if v: s += f" | {a}={v}"
    s += f" | todo={x['todo']}"
    print(s[:330])
