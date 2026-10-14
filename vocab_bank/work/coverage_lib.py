"""coverage_lib.py - shared matching helpers: is a source word an entry (lemma / form / phrase) of the bank?"""
import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANKS = ROOT / "bank_final"
SRC = ROOT.parent / "source_lists"


def rd(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fold(s):
    return unicodedata.normalize("NFC", s).casefold()


def deumlaut(s):
    return fold(s).replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")


ART = re.compile(r"^(der|die|das|ein|eine|einen|dem|den|des)\s+", re.I)


def clean_head(s):
    """headword text -> plain candidate lemmas (no article, plural code, parentheses)."""
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\([^)]*\)?", " ", s)
    s = re.sub(r"\[[^\]]*\]", " ", s)
    out = []
    for part in re.split(r"\s*/\s*(?=(?:der|die|das)\b)", s):
        part = part.split(",")[0].strip()
        part = re.sub(r"^sich\s+", "", part)
        part = ART.sub("", part)
        part = re.sub(r"^(der/die|die/der)\s+", "", part)
        part = part.strip(" .;:-–!?…\"'„“")
        if part:
            out.append(part)
    return out


class Universe:
    """strict = every lemma, plural, verb form, extra form and phrase of the banks; loose = every word anywhere in the bank text."""

    def __init__(self):
        main, b2 = rd(BANKS / "vocabulary_bank.csv"), rd(BANKS / "b2_vocabulary_bank.csv")
        phr, red = rd(BANKS / "phrase_bank.csv"), rd(BANKS / "redemittel_bank.csv")
        self.strict, self.loose = set(), set()
        add = self._add
        for r in main + b2:
            for c in clean_head(r["lemma"]):
                add(c)
            for alt in re.split(r"\s*/\s*", re.sub(r"\([^)]*\)", " ", r["lemma"])):
                add(re.sub(r"^sich\s+", "", alt.strip()))
            for f in (r.get("plural", ""), r.get("extra_forms", "")):
                for x in re.split(r"[|,;·]", f):
                    x = re.sub(r"^(auch|also|pl\.?):?\s*", "", x.strip(), flags=re.I)
                    if x and x not in ("–", "-", "(Pl.)"):
                        add(x)
                        add(ART.sub("", x))
            for f in (r.get("pres_3sg", ""), r.get("preterite", ""), r.get("perfect", "")):
                toks = [t for t in f.split() if t not in ("sich", "hat", "ist", "wurde")]
                for t in toks:
                    add(t)
                if r.get("sep_prefix") and toks:
                    add(toks[0] + " " + toks[-1])
        for r in phr:
            add(re.sub(r"\s+", " ", re.sub(r"\.\.\.|…", " ", r["phrase_de"])))
            for v in re.split(r"\s*\|\s*", r.get("variants", "")):
                add(re.sub(r"\.\.\.|…", " ", v))
        for r in main + b2 + phr + red:
            for k, v in r.items():
                if k in ("lemma", "example_de", "collocations", "phrase_de", "variants", "redemittel_de", "extra_forms", "plural", "note", "meaning_en"):
                    for t in re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß-]*", v or ""):
                        self._add(t, self.loose)

    def _add(self, w, to=None):
        w = w.strip()
        if w:
            (self.strict if to is None else to).update({fold(w), deumlaut(w)})

    def is_entry(self, w):
        return fold(w) in self.strict or deumlaut(w) in self.strict

    def in_text(self, w):
        return fold(w) in self.loose or deumlaut(w) in self.loose
