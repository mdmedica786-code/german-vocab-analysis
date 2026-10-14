# Coverage report: is everything from my PDFs and word lists in the bank?

Checked on 2026-10-14. Short answer: **yes**. One real gap was found (the Klett *Kontext B2* glossary) and it is now filled. The rest was already complete.

## Result per source

| Source | Entries checked | Result |
|---|---|---|
| Goethe-Zertifikat **A1** Wortliste (`A1_SD1_Wortliste_02.pdf`) | 690 | Complete. 1 leftover = the abbreviation "z. B." |
| Goethe-Zertifikat **A2** Wortliste | 1,221 | Complete. 11 leftovers are PDF layout noise (example sentences, prefix fragments such as `her-/hin-`). |
| Goethe-Zertifikat **B1** Wortliste | 2,766 | Complete. 76 leftovers are page numbers, headings, times, "CH:/A:" regional notes (Swiss/Austrian variants of words that are in the bank, e.g. Glacé = Glace, Rüebli = Karotte) and cut-off lines. Znüni was added. |
| **Netzwerk neu A1** glossary (scanned, read by OCR) | 2,105 | Complete. The 66 non-matches are OCR misreadings of words that are in the bank (checked). |
| **Netzwerk neu A2** glossary (OCR) | 1,600 | Complete. 93 non-matches, all OCR garble or page furniture. |
| **Netzwerk neu B1** glossary (OCR) | 2,290 | Complete. 220 non-matches, all OCR garble, names or page furniture. The adjective "diätisch" is in the bank as the standard spelling "diätetisch". |
| **Klett Kontext B2** glossary (`Kontext_B2-1_Gr-Glossar.pdf` and its CSV) | 2,340 words | **Was missing about 1,000 words. All added.** 15 entries skipped on purpose (fragments and prefixes such as "irgend-", spelling variants; list in `work/klett_skipped.txt`). Also added the idioms and phrases that the CSV lacked. |
| Old Anki deck (`German_PRO_v3`, chapters 1-5) | all words | Complete. |
| `beyond_goethe_B2.csv` corpus list | all | Added earlier (bank 2,379 to 3,683 B2 words). 341 words skipped on purpose (archaic, vulgar, participles, very rare). List in `work/b2_source_skipped.txt`. |

## What was added today
- 1,001 new B2 rows (bank went from 3,683 to **4,684** B2 words), each with article, plural or verb forms, English meaning, example sentence with translation, and collocations.
- All new rows were proofread by six independent reviewers; the confirmed errors (wrong case in collocations, unnatural phrases, translation mismatches) were fixed. Doubtful spellings carry a `check` flag (`?Schreibung ...`) instead of being guessed.

## Totals now
- Main vocabulary bank (A1-B1 and more): 6,524 words
- B2 bank: 4,684 words
- Phrases: 1,016, Redemittel: 1,176

## How to re-run the check yourself
`python3 work/source_check/run_all.py` (needs `pdftotext`). It re-reads every PDF in `source_lists/pdf` and prints the leftovers per source. `python3 work/klettsrc.py status` shows the Klett state (open = 0).

## Honest limits
- The three Netzwerk glossaries are scanned pictures. They were read by OCR, so a handful of misread words could hide a real gap. The matching is tolerant of small misspellings; the leftovers were looked through, not trusted blindly.
- Words are matched by lemma. A word that appears in the PDF only inside an example sentence is not required to be a separate entry.
