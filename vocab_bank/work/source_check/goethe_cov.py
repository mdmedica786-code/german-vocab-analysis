from goethe2 import *
import sys, json
strict, loose, main, b2, phr = build_universe()
SPEC = [('A1', TXT + '/A1_SD1_Wortliste_02.bbox.html', 9, 27, False),
        ('A2', TXT + '/Goethe-Zertifikat_A2_Wortliste.bbox.html', 8, 31, True),
        ('B1', TXT + '/Goethe-Zertifikat_B1_Wortliste.bbox.html', 8, 102, True)]
res = {}
for lv, fn, a, b, two in SPEC:
    heads = head_entries(fn, a, b, two)
    items = []
    for pg, t in heads:
        if re.search(r'^(ALPHABETISCHER|Alphabetische|\d+(\.\d+)*\s)', t) or len(t) < 2: continue
        for c in clean_head(t):
            items.append((pg, t, c))
    res[lv] = items
    miss_s, miss_l = [], []
    for pg, t, c in items:
        keys = {fold(c), deumlaut(c)}
        toks = [x for x in re.split(r'[\s/…]+', c) if len(x) > 1]
        ok_s = bool(keys & strict) or all((fold(x) in strict or deumlaut(x) in strict) for x in toks) if toks else True
        ok_l = bool(keys & loose) or all((fold(x) in loose or deumlaut(x) in loose) for x in toks) if toks else True
        if not ok_s: miss_s.append((pg, t, c))
        if not ok_l: miss_l.append((pg, t, c))
    print(f'{lv}: {len(items)} items; not as entry/alias: {len(miss_s)} ; not anywhere in bank text: {len(miss_l)}')
    json.dump({'miss_strict': miss_s, 'miss_loose': miss_l, 'n': len(items)}, open(f'{OUT}/goethe_{lv}.json', 'w'), ensure_ascii=False)
