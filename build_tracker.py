"""Build tracker.html: a self-contained vocabulary progress tracker from the study-order CSVs."""
import csv, json

def rows(f):
    return list(csv.DictReader(open(f, encoding="utf-8-sig")))

words = [[int(r["seq"]), int(r["week"]), int(r["day"]), r["date"], r["word_for_card"],
          r["level"], r["theme"], r["goethe_example"], r["phase"], r["week_theme"]]
         for r in rows("study_order_words.csv")]
chunks = [[int(r["seq"]), int(r["week"]), int(r["day"]), r["date"], r["chunk_for_card"],
           r["function_label"], r["phase"]] for r in rows("study_order_chunks.csv")]

html = open("tracker_template.html", encoding="utf-8").read()
html = html.replace("/*WORDS*/[]", json.dumps(words, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*CHUNKS*/[]", json.dumps(chunks, ensure_ascii=False, separators=(",", ":")))
open("tracker.html", "w", encoding="utf-8").write(html)
print("tracker.html written:", len(words), "words,", len(chunks), "chunks")
