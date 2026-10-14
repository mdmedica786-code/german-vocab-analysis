import csv, re, unicodedata, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BANKS = ROOT / 'vocab_bank' / 'bank_final'
SRC = ROOT / 'source_lists'
import os, tempfile
HERE = str(Path(__file__).resolve().parent)
# scratch folder for text extracted from the PDFs and for result files (not part of the repo)
TXT = os.environ.get('SOURCE_CHECK_DIR') or os.path.join(tempfile.gettempdir(), 'source_check')
OUT = TXT
os.makedirs(TXT, exist_ok=True)

def rd(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def fold(s):
    s = unicodedata.normalize('NFC', s).casefold()
    return s

def deumlaut(s):
    return fold(s).replace('ä', 'a').replace('ö', 'o').replace('ü', 'u').replace('ß', 'ss')

ART = re.compile(r'^(der|die|das|ein|eine|einen|dem|den|des)\s+', re.I)

def clean_head(s):
    """German headword text -> list of plain candidate lemmas (no article, no plural code, no parentheses)."""
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'\([^)]*\)?', ' ', s)          # (sich), (Sg.), (Pl.) ...
    s = re.sub(r'\[[^\]]*\]', ' ', s)
    out = []
    for part in re.split(r'\s*/\s*(?=(?:der|die|das)\b)', s):  # "der Frühling/das Frühjahr"
        part = part.split(',')[0].strip()
        part = re.sub(r'^(sich|\(sich\))\s+', '', part)
        part = ART.sub('', part)
        part = re.sub(r'^(der/die|die/der)\s+', '', part)
        part = part.strip(' .;:-–!?…"\'„“')
        if part:
            out.append(part)
    return out

def build_universe():
    main = rd(BANKS / 'vocabulary_bank.csv')
    b2 = rd(BANKS / 'b2_vocabulary_bank.csv')
    phr = rd(BANKS / 'phrase_bank.csv')
    red = rd(BANKS / 'redemittel_bank.csv')
    strict, loose = set(), set()
    def add(w, to=strict):
        w = w.strip()
        if w:
            to.add(fold(w)); to.add(deumlaut(w))
    for r in main + b2:
        for c in clean_head(r['lemma']):
            add(c)
            for t in re.split(r'[\s/]+', c):
                pass
        for alt in re.split(r'\s*/\s*', re.sub(r'\([^)]*\)', ' ', r['lemma'])):
            alt = re.sub(r'^sich\s+', '', alt.strip()); add(alt)
        for f in (r.get('plural', ''), r.get('extra_forms', '')):
            for x in re.split(r'[|,;·]', f):
                x = re.sub(r'^(auch|also|pl\.?):?\s*', '', x.strip(), flags=re.I)
                if x and x not in ('–', '-', '(Pl.)'):
                    add(x); add(ART.sub('', x))
        for f in (r.get('pres_3sg', ''), r.get('preterite', ''), r.get('perfect', '')):
            toks = [t for t in f.split() if t not in ('sich', 'hat', 'ist', 'wurde')]
            for t in toks: add(t)
            if r.get('sep_prefix') and toks:
                add(toks[0] + ' ' + toks[-1])
        if r.get('sep_prefix') and r['lemma']: add(r['lemma'])
    for r in phr:
        p = re.sub(r'\.\.\.|…', ' ', r['phrase_de'])
        add(re.sub(r'\s+', ' ', p))
        for v in re.split(r'\s*\|\s*', r.get('variants', '')):
            add(re.sub(r'\.\.\.|…', ' ', v))
    # loose: every word that occurs anywhere in the bank text
    for r in main + b2 + phr + red:
        for k, v in r.items():
            if k in ('lemma', 'example_de', 'collocations', 'phrase_de', 'variants', 'redemittel_de', 'extra_forms', 'plural', 'note', 'meaning_en'):
                for t in re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß-]*", v or ''):
                    add(t, loose)
    return strict, loose, main, b2, phr
