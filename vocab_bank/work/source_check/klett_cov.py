import re, json
from goethe_cov2 import *
txt = open(TXT + '/Kontext_B2-1_Gr-Glossar.txt', encoding='utf-8').read()
items = []
prev = ''
for line in txt.replace('\f', '\n').split('\n'):
    if not line.strip(): prev = ''; continue
    left = line[:56]
    if re.search(r'[Ͱ-Ͽ]', left): left = re.split(r'\s{3,}', left.strip())[0]
    left = re.sub(r'^\s*\d+[a-z]?(\s+ÜB)?\s+', '', left)   # label
    left = re.split(r'\s{3,}', left.strip())[0].strip()
    if not left or re.match(r'^(Lektion|Modul|Kursbuch|Übungsbuch|Kontext|Klett|Übersetzt|Alexandra|Athen|©|Von dieser|Die Kopier|Wiederholung|Einstieg|Training|Fokus|Projekt|Test)', left): prev = left; continue
    if re.search(r'[Ͱ-Ͽ]', left): prev = left; continue
    if prev.endswith(',') or re.match(r'^(hat|ist) ', left) or re.search(r', (hat|ist|war|wurde) ', left) and not re.match(r'^(der|die|das|sich)\b', left) and ',' in left and re.search(r'\b(hat|ist) \w+$', left):
        prev = left; continue
    if left.endswith(('.', '!', '?')) and len(left.split()) > 3: prev = left; continue
    prev = left
    items.append(left)
print(len(items)); print(items[:30])
cands = []
for t in items:
    t2 = t.replace('|', '')
    for c in clean_head(t2): cands.append((t, c))
miss = [(t, c) for t, c in cands if not resolved(c)]
print(len(cands), 'unresolved', len(miss)); print(miss[:150])
json.dump({'items': items, 'miss': miss}, open(OUT + '/klett_pdf.json', 'w'), ensure_ascii=False)
