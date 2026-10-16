#!/usr/bin/env python3
"""make_download_zips.py - builds the few zip files Medica actually downloads, into ../DOWNLOAD_THESE.

  python3 work/make_download_zips.py

Run make_word_lists.py and make_level_workbook.py first (it zips what they wrote into ../WORD_LISTS).
  1_Words_to_learn.zip      the study words by exam stage + phrases + Redemittel + Excel (no duplicates, no 'not in list')
  2_Obsidian_Vault.zip      the Obsidian vault (open the unzipped folder as vault)
  3_Anki_JSON_for_AI.zip    the same words as JSON for the nerdmedica-de-pro skill
The native audio is not zipped: it stays in vocab_bank/bank_final/audio (about 370 MB, already on the computer).
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WL = ROOT / "WORD_LISTS"
VAULT = ROOT / "vocab_bank" / "bank_final" / "German_Vault"
OUT = ROOT / "DOWNLOAD_THESE"

README_WORDS = """YOUR WORDS TO LEARN
===================

Learn in this order (your plan: Goethe B1 in December 2026, B2 in spring 2027, then FSP):

  1_B1_exam_Dec2026/     A1.csv  ->  A2.csv  ->  B1.csv           (5,457 words)
  2_B2_exam_2027/        B2.csv  (359 core B2 words)  then  B2_extra.csv (4,684 more B2 words)
  3_C1_later/            C1.csv                                    (252 words)
  4_Phrases_and_Redemittel/   phrases.csv (1,016) and redemittel.csv (1,176: ready-made sentences for speaking and writing)

Other files
  Word_Lists_by_Level.xlsx   the same words in Excel (filter by level, topic, type)
  ALL_WORDS.csv              everything in one file (10,752 words); give this to an AI model

How to read a CSV: open with Excel ("Data > From text/CSV", encoding UTF-8) or give it to your AI model.
Columns: id, level, topic, type, german, word, article, plural, forms, grammar, meaning_en, example_de,
example_en, collocations, exam_use, register, medical, bank, note.

The 456 words that were left out on purpose (country names, duplicates, Austrian/Swiss-only words) are NOT in
these files. You do not need to learn them.
"""


def zip_files(dst, items):
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc, src in items:
            if isinstance(src, bytes):
                z.writestr(arc, src)
            else:
                z.write(src, arc)
    print(f"{dst.name}: {dst.stat().st_size / 1e6:.1f} MB")


def main():
    OUT.mkdir(exist_ok=True)
    bl = WL / "by_level"
    words = [
        ("README_START_HERE.txt", README_WORDS.encode("utf-8")),
        ("1_B1_exam_Dec2026/A1.csv", bl / "A1.csv"),
        ("1_B1_exam_Dec2026/A2.csv", bl / "A2.csv"),
        ("1_B1_exam_Dec2026/B1.csv", bl / "B1.csv"),
        ("2_B2_exam_2027/B2.csv", bl / "B2.csv"),
        ("2_B2_exam_2027/B2_extra.csv", bl / "B2_extra.csv"),
        ("3_C1_later/C1.csv", bl / "C1.csv"),
        ("4_Phrases_and_Redemittel/phrases.csv", WL / "phrases.csv"),
        ("4_Phrases_and_Redemittel/redemittel.csv", WL / "redemittel.csv"),
        ("Word_Lists_by_Level.xlsx", WL / "Word_Lists_by_Level.xlsx"),
        ("ALL_WORDS.csv", WL / "ALL_WORDS.csv"),
    ]
    zip_files(OUT / "1_Words_to_learn.zip", words)

    vault = [(f"German_Vault/{p.relative_to(VAULT).as_posix()}", p) for p in sorted(VAULT.rglob("*")) if p.is_file()]
    zip_files(OUT / "2_Obsidian_Vault.zip", vault)

    anki = [(f"anki_json/{p.name}", p) for p in sorted((WL / "anki_json").glob("*.json"))]
    anki.append(("README.txt", ("Input files for the nerdmedica-de-pro skill (one per level).\n"
                                "Example: python scripts/build_deck.py --words anki_json/A1.json --name \"German_PRO_v3::bank::A1\" "
                                "--deck-id 2002001001 --out German_PRO_A1.apkg --audio native+edge\n"
                                "Do not change any German in the files.\n").encode("utf-8")))
    zip_files(OUT / "3_Anki_JSON_for_AI.zip", anki)


if __name__ == "__main__":
    main()
