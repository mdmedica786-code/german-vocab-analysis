import re, collections
from common import *

def load_pages(fn):
    t = open(fn, encoding='utf-8').read()
    for m in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', t, re.S):
        W, H = float(m.group(1)), float(m.group(2))
        words = [(float(a), float(b), float(c), float(d), re.sub(r'&amp;', '&', re.sub(r'&quot;', '"', re.sub(r'&apos;', "'", w))))
                 for a, b, c, d, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', m.group(3))]
        yield W, H, words

def segments(words, H):
    rows = collections.defaultdict(list)
    for x0, y0, x1, y1, w in words:
        if y0 < 55 or y0 > H - 48: continue
        rows[round(y0 / 3)].append((x0, x1, w, y0))
    segs = []
    for k in sorted(rows):
        ws = sorted(rows[k]); cur = [ws[0]]
        for a in ws[1:]:
            if a[0] - cur[-1][1] > 9: segs.append(cur); cur = [a]
            else: cur.append(a)
        segs.append(cur)
    return [(s[0][0], s[0][3], ' '.join(w[2] for w in s)) for s in segs]

def head_entries(fn, first_page, last_page, two_col):
    out = []
    for pi, (W, H, words) in enumerate(load_pages(fn), 1):
        if pi < first_page or pi > last_page: continue
        segs = segments(words, H)
        h = collections.Counter(round(s[0] / 4) * 4 for s in segs)
        peaks = sorted(x for x, c in h.items() if c >= 5)
        if not peaks: continue
        heads = []
        if two_col:
            L = [x for x in peaks if x < W / 2 - 20]; R = [x for x in peaks if x >= W / 2 - 20]
            if L: heads.append(min(L))
            if R and sum(h[x] for x in R) >= 8: heads.append(min(R))
        else:
            heads.append(min(peaks))
        prev = {}
        for x0, y0, text in sorted(segs, key=lambda s: (s[0] >= W / 2 - 20 if two_col else 0, s[1])):
            col = [hx for hx in heads if abs(x0 - hx) <= 7]
            if not col: continue
            key = col[0]
            if re.fullmatch(r'[A-ZÄÖÜ]', text.strip()): continue
            if prev.get(key, '').endswith(',') or re.match(r'^(hat|ist) ', text):
                prev[key] = text; continue
            prev[key] = text
            out.append((pi, text))
    return out
