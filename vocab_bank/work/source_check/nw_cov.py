import json, re, collections
from goethe_cov2 import *
strict, loose, main, b2, phr = build_universe()
bykey = collections.defaultdict(list)
for s in strict:
    bykey[(s[:1], len(s))].append(s)

def lev1(a, b):
    if a == b: return True
    if abs(len(a) - len(b)) > 1: return False
    if len(a) == len(b):
        return sum(1 for x, y in zip(a, b) if x != y) <= 1
    if len(a) > len(b): a, b = b, a
    for i in range(len(b)):
        if a == b[:i] + b[i + 1:]: return True
    return False

def fuzzy(c):
    d = deumlaut(c).replace('|', '').replace(' ', '')
    d0 = deumlaut(c)
    for L in (len(d0) - 1, len(d0), len(d0) + 1):
        for s in bykey.get((d0[:1], L), []):
            if lev1(d0, s): return s
    return None

def german_lines(pages):
    out = []
    for p, boxes in sorted(pages.items(), key=lambda kv: int(kv[0])):
        col = sorted([b for b in boxes if 200 <= b[0] < 600 and b[1] > 150], key=lambda b: (b[1], b[0]))
        open_par = 0
        since = 0
        for x0, y0, x1, y1, t, c in col:
            t = t.strip()
            cont = open_par > 0 or (')' in t and '(' not in t)
            if open_par > 0:
                since += 1
                if since > 2: open_par = 0; cont = False; since = 0
            open_par = max(0, open_par + t.count('(') - t.count(')'))
            if open_par == 0: since = 0
            if cont or not t: continue
            out.append((int(p), t, c))
    return out

res = {}
for n in ('a1', 'a2', 'b1'):
    pages = json.load(open(f'{HERE}/ocr/{n}.json'))
    lines = german_lines(pages)
    items = []
    for p, t, c in lines:
        if re.match(r'^(Kapitel|Glossar|Deutsch|Lektion|Seite|Netzwerk|©|Alle Rechte|Von dieser|eigenen)', t): continue
        t2 = re.sub(r'\([^)]*\)?', ' ', t)
        for cand in clean_head(t2.replace('|', '')):
            cand = re.sub(r'^[^A-Za-zÄÖÜäöüß]+', '', cand)
            if len(cand) >= 2: items.append((p, t, cand))
    miss = []
    for p, t, cand in items:
        if cand.lower() in ('der', 'die', 'das'): continue
        if resolved(cand): continue
        f = fuzzy(cand)
        if f: continue
        miss.append((p, t, cand))
    print(n, 'lines', len(lines), 'items', len(items), 'unmatched', len(miss))
    res[n] = (items, miss)
    json.dump({'items': items, 'miss': miss}, open(f'{OUT}/nw_{n}.json', 'w'), ensure_ascii=False)
