import json, re
from common import *
strict, loose, main, b2, phr = build_universe()
lemmas = [fold(re.sub(r'\([^)]*\)', '', r['lemma'])).strip() for r in main + b2] + [fold(p['phrase_de']) for p in phr]
lemset = set(lemmas)
def resolved(c):
    c0 = c.strip()
    f = fold(c0); d = deumlaut(c0)
    if f in strict or d in strict or f in loose or d in loose: return 'ok'
    toks = [x for x in re.split(r'[\s/…,;:]+', c0) if x]
    if toks and all(fold(x) in loose or deumlaut(x) in loose for x in toks): return 'ok-tokens'
    # stem entries / hyphen fragments
    if len(f) >= 2 and any(l.startswith(f) or l.endswith(f) for l in lemmas): return 'fragment'
    return ''
if __name__ == '__main__':
    for lv in ('A1', 'A2', 'B1'):
        d = json.load(open(f'{OUT}/goethe_{lv}.json'))
        rest = []
        for pg, t, c in d['miss_strict']:
            if not resolved(c): rest.append((pg, c))
        print(lv, len(rest)); print(rest)
