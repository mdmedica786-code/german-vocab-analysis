"""export_anki.py - Export vocabulary bank to Anki-ready CSV with [sound:file] and video links."""
import csv
import json
import shutil
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINAL = ROOT / "bank_final"
MANIFEST_PATH = ROOT / "work" / "audio_manifest.json"

def main():
    manifest = {}
    if MANIFEST_PATH.is_file():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            for entry in json.load(f):
                if entry.get("file"):
                    manifest[entry["word"].casefold()] = entry["file"]

    rows_out = []
    for bank_file in ["vocabulary_bank.csv", "b2_vocabulary_bank.csv"]:
        p = FINAL / bank_file
        if not p.is_file():
            continue
        with open(p, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                lemma = (r.get("lemma") or "").strip()
                if not lemma:
                    continue
                art = (r.get("article") or "").strip()
                pos = (r.get("pos") or "").strip()
                level = (r.get("level") or "").strip()
                german_display = f"{art} {lemma}" if (pos == "noun" and art in ("der", "die", "das")) else lemma
                afile = manifest.get(lemma.casefold(), "")
                anki_audio = f"[sound:{afile}]" if afile else ""
                q_clean = urllib.parse.quote(lemma)
                yg_link = f"https://youglish.com/pronounce/{q_clean}/german"
                pp_link = f"https://www.playphrase.me/#/search?q={q_clean}&language=de"
                tag = f"{level} {bank_file.split('_')[0]}"

                rows_out.append({
                    "id": r.get("id", ""),
                    "german": german_display,
                    "lemma": lemma,
                    "article": art,
                    "pos": pos,
                    "plural": (r.get("plural") or "").strip(),
                    "meaning_en": (r.get("meaning_en") or "").strip(),
                    "other_senses": r.get("other_senses", ""),
                    "audio": anki_audio,
                    "audio_file": afile,
                    "example_de": (r.get("example_de") or "").strip(),
                    "example_en": (r.get("example_en") or "").strip(),
                    "youglish": yg_link,
                    "playphrase": pp_link,
                    "level": level,
                    "topic": (r.get("topic") or "").strip(),
                    "tags": tag
                })

    out_csv = FINAL / "anki_ready_vocabulary.csv"
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    study_csv = ROOT.parent / "STUDY_HERE" / "Anki_Ready_Vocabulary.csv"
    shutil.copy2(out_csv, study_csv)
    print(f"Exported {len(rows_out)} rows to {study_csv} with Anki [sound:file] tags.")

if __name__ == "__main__":
    main()
