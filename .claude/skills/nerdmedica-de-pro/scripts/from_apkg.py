#!/usr/bin/env python3
"""
from_apkg.py — extract words from an existing 14-field German .apkg into
words.json ready for build_deck.py.

Designed for Medica's DE VOCAB V2 note type with fields:
  Domain, Front_EN, Target, IPA, GenderClass, GenderColor,
  Full_Declension, Verb_Conjugation, Case_Government, Collocations,
  Register_Nuance, Synonym_Ladder, Antonym, Word_Family

USAGE:
    python from_apkg.py \\
        --apkg   /path/to/source.apkg \\
        --filter-tag "netzwerk::A1::kap05" \\
        --out    /tmp/kap05_words.json
"""
import argparse, json, re, sqlite3, sys, tempfile, zipfile
from pathlib import Path

FIELD_NAMES = [
    "Domain","Front_EN","Target","IPA","GenderClass","GenderColor",
    "Full_Declension","Verb_Conjugation","Case_Government","Collocations",
    "Register_Nuance","Synonym_Ladder","Antonym","Word_Family",
]

# ---------- helpers to parse the mini-HTML packed into fields ----------

def _strip_span(s: str) -> str:
    return re.sub(r"<span[^>]*>(.*?)</span>", r"\1", s or "").strip()

def _parse_ipa(html: str) -> dict:
    """
    IPA field format:
      [ipa]<div class="phon-simple">SIMPLE</div>
      <div class="ex-de">German sentence with <b>target</b></div>
      <div class="ex-en">English translation</div>
    """
    out = {}
    if not html: return out
    m = re.search(r'<div class="phon-simple">(.*?)</div>', html, re.DOTALL)
    if m: out["pronunciation"] = m.group(1).strip()
    m = re.search(r'<div class="ex-de">(.*?)</div>', html, re.DOTALL)
    if m: out["de_sentence"] = m.group(1).strip()
    m = re.search(r'<div class="ex-en">(.*?)</div>', html, re.DOTALL)
    if m: out["en_sentence"] = m.group(1).strip()
    return out

def _parse_html_table(html: str) -> dict:
    """Generic <table><tr><th>K</th><td>V</td></tr>...</table> → {K: V}."""
    if not html or html.strip() == "—": return {}
    out = {}
    for row in re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL):
        cells = re.findall(r"<t[hd]>(.*?)</t[hd]>", row, re.DOTALL)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        if len(cells) >= 2:
            out[cells[0]] = cells[1]
    return out

def _parse_declension(html: str) -> dict:
    """
    Declension table into flat keys:  nom_sing, nom_plur, dat_sing, ...
    Source table layout:
      <tr><th></th><th>Singular</th><th>Plural</th></tr>
      <tr><th>Nom</th><td>der X</td><td>die Xs</td></tr>
      ...
    """
    if not html or html.strip() == "—": return {}
    rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)
    if not rows: return {}
    header = re.findall(r"<t[hd]>(.*?)</t[hd]>", rows[0], re.DOTALL)
    header = [re.sub(r"<[^>]+>", "", h).strip() for h in header]
    cols = header[1:]  # skip empty top-left
    out = {}
    for row in rows[1:]:
        cells = re.findall(r"<t[hd]>(.*?)</t[hd]>", row, re.DOTALL)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        if not cells: continue
        case = cells[0].lower()
        for i, val in enumerate(cells[1:]):
            if i < len(cols):
                col_raw = cols[i].lower()
                # "Singular (kein Plural)" → sing, not plur
                if "sing" in col_raw or "kein plural" in col_raw:
                    col = "sing"
                elif "plur" in col_raw:
                    col = "plur"
                else:
                    col = col_raw
                out[f"{case}_{col}"] = val
    return out

def _parse_verb_conj(html: str) -> dict:
    """
    Conjugation table into flat keys used by build_cloze_grammar:
      praesens_ich, praesens_er, praeteritum, perfekt
    Source table row for Präsens usually looks like: 'ich rufe · er ruft'.
    """
    raw = _parse_html_table(html)
    out = {}
    pres = raw.get("Präsens") or raw.get("Presens") or ""
    if "·" in pres:
        left, right = [p.strip() for p in pres.split("·", 1)]
        out["praesens_ich"] = re.sub(r"^ich\s+", "", left)
        out["praesens_er"]  = re.sub(r"^er\s+", "", right)
    elif pres:
        out["praesens_ich"] = pres
    prt = raw.get("Präteritum") or raw.get("Preteritum")
    if prt and prt != "—":
        out["praeteritum"] = prt
    prf = raw.get("Perfekt")
    if prf and prf != "—":
        out["perfekt"] = prf
    kii = raw.get("Konjunktiv II") or raw.get("Konjunktiv 2") or raw.get("Konjunktiv")
    if kii and kii != "—":
        out["konjunktiv_ii"] = kii
    imp = raw.get("Imperativ")
    if imp and imp != "—":
        out["imperativ"] = imp
    return out

def _parse_syn_ladder(html: str) -> dict:
    """A1 / A2/B1 / C2 keys."""
    raw = _parse_html_table(html)
    return {k: v for k, v in raw.items() if v and v != "—"}

def _split_article(target: str, gender_class: str) -> tuple[str, str]:
    if gender_class in ("der", "die", "das"):
        parts = target.split(None, 1)
        if len(parts) == 2 and parts[0].lower() in ("der", "die", "das"):
            return parts[0], parts[1]
    return "", target

# ---------- main extraction ----------

def list_tags(apkg_path: Path) -> dict:
    """Return {tag: note_count} for netzwerk/thema/goethe tags — helps pick chapters."""
    from collections import Counter
    words = extract(apkg_path, None)
    cnt = Counter(t for w in words for t in w["tags"] if not t.startswith("thema::"))
    return dict(sorted(cnt.items()))


def extract(apkg_path: Path, filter_tags) -> list[dict]:
    if isinstance(filter_tags, str):
        filter_tags = [filter_tags]
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(apkg_path) as z:
            z.extractall(tmp)
        # Anki packages can be in .anki2 or .anki21 — try both
        for name in ("collection.anki21", "collection.anki2"):
            db = Path(tmp) / name
            if db.exists():
                try:
                    c = sqlite3.connect(db)
                    cur = c.cursor()
                    cur.execute("SELECT COUNT(*) FROM notes")
                    if cur.fetchone()[0] > 0:
                        break
                except sqlite3.OperationalError:
                    continue
        else:
            raise SystemExit("No populated notes table found in the .apkg")

        cur = c.cursor()
        cur.execute("SELECT flds, tags FROM notes ORDER BY id")
        rows = cur.fetchall()
        if filter_tags:
            # keep the order of the tags given (kap03 before kap04 …)
            ordered = []
            for ft in filter_tags:
                ordered += [r for r in rows if ft in r[1].split()]
            rows = ordered

        words = []
        for flds, tags in rows:
            fs = flds.split("\x1f")
            if len(fs) < 14:          # not a DE VOCAB V2 note — skip
                continue
            note = {n: (fs[i] if i < len(fs) else "") for i, n in enumerate(FIELD_NAMES)}

            target_raw = _strip_span(note["Target"])
            gc = note["GenderClass"]
            article, de_word = _split_article(target_raw, gc)
            ipa = _parse_ipa(note["IPA"])

            colls = [x.strip() for x in note["Collocations"].split(",") if x.strip() and x.strip() != "—"]

            reg = note["Register_Nuance"].strip()
            if reg in ("—", ""): reg = ""

            # Word Family — comma-separated derivatives like
            #   "familiär (adj.), der Familienname (n.), die Großfamilie (n.)"
            wf_raw = note["Word_Family"].strip()
            if wf_raw and wf_raw != "—":
                wf = [x.strip() for x in wf_raw.split(",")
                      if x.strip() and x.strip() != "—"]
            else:
                wf = []

            word = {
                "en_meaning":   note["Front_EN"].strip(),
                "de_word":      de_word,
                "article":      article,
                "gender_class": gc,
                "pronunciation": ipa.get("pronunciation", ""),
                "de_sentence":  ipa.get("de_sentence", ""),
                "en_sentence":  ipa.get("en_sentence", ""),
                "note":         reg,
                "declension":   _parse_declension(note["Full_Declension"]),
                "conjugation":  _parse_verb_conj(note["Verb_Conjugation"]),
                "case_government": note["Case_Government"].strip() if note["Case_Government"].strip() != "—" else "",
                "collocations": colls,
                "synonyms":     _parse_syn_ladder(note["Synonym_Ladder"]),
                "antonym":      note["Antonym"].strip(),
                "word_family":  wf,
                "tags":         [t for t in tags.strip().split()
                                 if t.startswith(("netzwerk::", "thema::", "goethe::"))],
            }
            words.append(word)

        return words


def main():
    ap = argparse.ArgumentParser(description="Extract words from a 14-field .apkg into words.json")
    ap.add_argument("--apkg", required=True, help="Source .apkg path")
    ap.add_argument("--filter-tag", action="append", default=None,
                    help="Exact tag to include, e.g. netzwerk::A1::kap05. Repeat for several chapters.")
    ap.add_argument("--out", help="Output words.json path")
    ap.add_argument("--list-tags", action="store_true", help="Only print chapter tags and counts")
    args = ap.parse_args()

    if args.list_tags:
        for t, n in list_tags(Path(args.apkg)).items():
            print(f"  {n:5d}  {t}")
        return
    if not args.out:
        sys.exit("--out is required unless --list-tags")
    words = extract(Path(args.apkg), args.filter_tag)
    if not words:
        sys.exit("No matching notes. Run with --list-tags to see available chapter tags.")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"✓ Extracted {len(words)} words → {args.out}")


if __name__ == "__main__":
    main()
