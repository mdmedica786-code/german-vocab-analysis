#!/usr/bin/env python3
"""make_word_lists.py - builds the clean word lists in WORD_LISTS/ (repo top level) from the CSV banks.

  python3 work/make_word_lists.py

WORD_LISTS/
  ALL_WORDS.csv              every word of the study list (main bank + B2 extra bank), simple columns, UTF-8
  by_level/A1.csv ...        the same, one file per level (B2 = main-bank B2 words, B2_extra = extra B2 bank)
  not_in_study_list.csv      words left out on purpose, with the reason
  phrases.csv, redemittel.csv
  anki_json/A1.json ...      the same words as a JSON list in the input format of the nerdmedica-de-pro Anki skill
  German_Vault.zip           the Obsidian vault (open the unzipped folder as a vault)
  Word_Lists_by_Level.xlsx   Excel: All words + one sheet per level  (built by make_level_workbook.py)
"""
import csv
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from studylist import mark_not_in_list  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BANKS = ROOT / "bank_final"
OUT = ROOT.parent / "WORD_LISTS"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]
COLS = ["id", "level", "topic", "type", "german", "word", "article", "plural", "forms", "grammar", "meaning_en", "example_de", "example_en",
        "collocations", "exam_use", "register", "medical", "bank", "note"]


def rd(name):
    with open(BANKS / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def topic(t):
    return t.split(" ", 1)[1] if t and " " in t else t


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")).strip("-")


def german(r):
    art = (r.get("article") or "").strip()
    if r["pos"] == "noun" and art in ("der", "die", "das", "der/die", "der/das", "die/das"):
        return f"{art} {r['lemma']}"
    if r["pos"] == "noun" and art == "(Pl.)":
        return f"{r['lemma']} (Pl.)"
    return r["lemma"]


def forms(r):
    out = []
    if r["pos"] == "noun" and r.get("plural") and r["plural"] not in ("–", "-", "(Pl.)"):
        out.append("Pl.: " + r["plural"])
    if r["pos"] == "verb":
        f = ", ".join(x for x in (r.get("pres_3sg"), r.get("preterite"), r.get("perfect")) if x)
        if f:
            out.append(f)
    if r.get("extra_forms"):
        out.append(r["extra_forms"])
    return " · ".join(out)


def grammar(r):
    g = []
    if r.get("reflexive"):
        g.append("reflexive")
    if r.get("sep_prefix"):
        g.append(f"separable ({r['sep_prefix']}-)")
    if r.get("gov"):
        g.append(r["gov"] if r["gov"].startswith("+") else "+ " + r["gov"])
    return " · ".join(g)


def row(r, bank):
    return {"id": r["id"], "level": r["level"], "topic": topic(r["topic"]), "type": r["pos"], "german": german(r), "word": r["lemma"],
            "article": r.get("article", ""), "plural": r.get("plural", ""), "forms": forms(r), "grammar": grammar(r), "meaning_en": r["meaning_en"],
            "example_de": r.get("example_de", ""), "example_en": r.get("example_en", ""), "collocations": r.get("collocations", ""),
            "exam_use": r.get("exam_use", ""), "register": r.get("register", ""),
            "medical": "yes" if (r.get("medical") or r["topic"].startswith("M")) else "", "bank": bank,
            "note": r.get("note", "")}


# ------------------------------------------------------------------ Anki JSON (input of the nerdmedica-de-pro skill)
GC = {"verb": "verb", "adjective": "adj", "adverb": "adv", "pronoun": "pron", "determiner": "pron", "conjunction": "conj",
      "preposition": "prep", "particle": "adv", "interjection": "adv", "numeral": "adj"}


def plural_dat(pl):
    return pl if pl.endswith(("n", "s")) else pl + "n"


def declension(r):
    """Only forms that follow from the bank data with certainty: feminine (4 cases) and neuter (nom/acc/dat); never masculine."""
    art, lemma, pl = (r.get("article") or "").strip(), r["lemma"], (r.get("plural") or "").strip()
    d = {}
    if art in ("die", "das"):
        d["nom_sing"] = f"{art} {lemma}"
        d["akk_sing"] = f"{art} {lemma}"
        d["dat_sing"] = f"der {lemma}" if art == "die" else f"dem {lemma}"
        if art == "die":
            d["gen_sing"] = f"der {lemma}"
    else:
        return {}
    if pl in ("–", "-"):
        d["nom_plur"] = "—"
    elif pl and pl != "(Pl.)" and "|" not in pl:
        d["nom_plur"] = f"die {pl}"
        d["akk_plur"] = f"die {pl}"
        d["dat_plur"] = f"den {plural_dat(pl)}"
        if art == "die":
            d["gen_plur"] = f"der {pl}"
    return d


def bold_target(r, sentence):
    """Wrap the word (or both parts of a separable verb) in <b>; no <b> if it cannot be found with certainty."""
    if not sentence:
        return sentence, False
    lemma = re.sub(r"^sich\s+", "", re.sub(r"\s*\(.*?\)", "", r["lemma"])).strip()
    pos, cands = r["pos"], []
    if pos == "noun":
        cands = [lemma] + ([r["plural"].split("|")[0].strip()] if r.get("plural") and r["plural"] not in ("–", "-", "(Pl.)") else [])
        rx = [rf"\b{re.escape(c)}(?:s|es|n|en)?\b" for c in cands if c]
    elif pos == "verb":
        toks = []
        for f in (r.get("pres_3sg"), r.get("preterite")):
            t = [x for x in (f or "").split() if x != "sich"]
            if t:
                toks.append(t[0])
        part = (r.get("perfect") or "").split()
        if part:
            toks.append(part[-1])
        stem = re.sub(r"(en|n)$", "", lemma.split()[-1])
        rx = [rf"\b{re.escape(t)}\b" for t in toks if t] + [rf"\b{re.escape(lemma.split()[-1])}\b"]
        if len(stem) >= 4:
            rx.append(rf"\b{re.escape(stem)}(?:e|st|t|en|et|n)?\b")
    elif pos in ("adjective", "adverb"):
        rx = [rf"\b{re.escape(lemma)}(?:e|en|er|em|es)?\b"]
    else:
        rx = [rf"\b{re.escape(lemma)}\b"]
    for pat in rx:
        m = re.search(pat, sentence, re.I)
        if m:
            out = sentence[:m.start()] + "<b>" + m.group(0) + "</b>" + sentence[m.end():]
            sp = (r.get("sep_prefix") or "").strip()
            if pos == "verb" and sp:
                m2 = re.search(rf"\b{re.escape(sp)}\b(?![^<]*</b>)", out)
                if m2 and m2.start() > m.start():
                    out = out[:m2.start()] + "<b>" + m2.group(0) + "</b>" + out[m2.end():]
            return out, True
    return sentence, False


def anki_word(r, bank):
    pos, art = r["pos"], (r.get("article") or "").strip()
    if pos == "noun":
        gc = "pl" if art == "(Pl.)" else (art.split("/")[0] if art else "")
        if gc not in ("der", "die", "das", "pl"):
            gc = "adj"
    else:
        gc = GC.get(pos, "adv" if pos == "phrase" else "adj")
    de_sent, found = bold_target(r, r.get("example_de", ""))
    w = {"en_meaning": r["meaning_en"], "de_word": re.sub(r"\s*\(.*?\)", "", r["lemma"]).strip(), "article": art if art != "(Pl.)" else "",
         "gender_class": gc, "de_sentence": de_sent, "en_sentence": r.get("example_en", ""), "note": r.get("note", ""),
         "case_government": r.get("gov", ""), "collocations": [c.strip() for c in r.get("collocations", "").split("|") if c.strip()],
         "tags": [f"level::{r['level']}", f"thema::{slug(topic(r['topic']))}", f"bank::{bank}", f"id::{r['id']}"] + (["medical"] if r["topic"].startswith("M") else [])}
    if pos == "noun":
        dc = declension(r)
        if dc:
            w["declension"] = dc
    if pos == "verb":
        conj = {k: v for k, v in (("praesens_er", r.get("pres_3sg")), ("praeteritum", r.get("preterite")), ("perfekt", r.get("perfect"))) if v}
        if len(conj) >= 2:
            w["conjugation"] = conj
    return w, found


# ------------------------------------------------------------------ writers
def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\r\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def build_vault_zip():
    vault = BANKS / "German_Vault"
    dst = OUT / "German_Vault.zip"
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(vault.rglob("*")):
            if p.is_file() and p.name != ".DS_Store":
                z.write(p, p.relative_to(vault.parent).as_posix())
    return dst


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    main_rows = mark_not_in_list(rd("vocabulary_bank.csv"))
    main_rows.sort(key=lambda r: int(r["study_order"]) if r.get("study_order", "").isdigit() else 10**9)
    b2_rows = sorted(rd("b2_vocabulary_bank.csv"), key=lambda r: (r["topic"], r["lemma"].casefold()))

    study = [(r, "main") for r in main_rows if not r.get("skip")] + [(r, "b2") for r in b2_rows]
    study.sort(key=lambda t: (LEVELS.index(t[0]["level"]) if t[0]["level"] in LEVELS else 9, t[1] != "main"))
    all_rows = [row(r, b) for r, b in study]
    write_csv(OUT / "ALL_WORDS.csv", COLS, all_rows)

    per = defaultdict(list)
    for (r, b), x in zip(study, all_rows):
        per["B2_extra" if b == "b2" else r["level"]].append(x)
    for k, v in per.items():
        write_csv(OUT / "by_level" / f"{k}.csv", COLS, v)

    left = [dict(row(r, "main"), reason=r.get("skip_reason", "")) for r in main_rows if r.get("skip")]
    write_csv(OUT / "not_in_study_list.csv", COLS + ["reason"], left)

    P = rd("phrase_bank.csv")
    write_csv(OUT / "phrases.csv", ["id", "level", "function", "phrase_de", "meaning_en", "example_de", "example_en", "variants", "grammar_note", "register"],
              [{"id": r["id"], "level": r["level"], "function": r["function"], "phrase_de": r["phrase_de"], "meaning_en": r["meaning_en"],
                "example_de": r["example_de"], "example_en": r["example_en"], "variants": r["variants"], "grammar_note": r["grammar_note"],
                "register": r["register"]} for r in sorted(P, key=lambda r: (r["function"], r["level"]))])
    R = rd("redemittel_bank.csv")
    write_csv(OUT / "redemittel.csv", ["id", "cat_id", "category", "function", "speaker", "level", "priority", "redemittel_de", "meaning_en", "example_de",
                                       "example_en", "variants", "grammar_note", "exam_use"], R)

    # Anki JSON per level
    stats = Counter()
    groups = defaultdict(list)
    for r, b in study:
        w, found = anki_word(r, b)
        key = "B2_extra" if b == "b2" else r["level"]
        groups[key].append(w)
        stats["words"] += 1
        stats["sentence_marked"] += found
        stats["with_declension"] += "declension" in w
        stats["with_conjugation"] += "conjugation" in w
    for k, v in groups.items():
        (OUT / "anki_json").mkdir(parents=True, exist_ok=True)
        (OUT / "anki_json" / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    z = build_vault_zip()
    print(f"{len(all_rows)} words in ALL_WORDS.csv; per file: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(per.items())))
    print(f"not in study list: {len(left)}; phrases {len(P)}; redemittel {len(R)}")
    print("anki json:", dict(stats), f"vault zip {z.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
