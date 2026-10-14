# German banks (vocabulary, phrases, Redemittel, B2)

Everything for Medica's German study banks. The finished data is in `bank_final/`.

## What to open

| Goal | Open |
|---|---|
| Study with flashcards (easiest) | `../STUDY_HERE/German_Study.html` (double-click) |
| Word lists as a table, one sheet per level | `../STUDY_HERE/Word_Lists_by_Level.xlsx` |
| Study and take notes in Obsidian | folder `bank_final/German_Vault` (Obsidian: "Open folder as vault"), start with `00 Home`; words are in folders A1, A2, B1, B2, C1 |
| Look at the data in Excel | `bank_final/German_Bank.xlsx` (main banks), `bank_final/German_B2_Bank.xlsx` (B2 bank) |
| Use the data in other tools | the CSV files in `bank_final/` (UTF-8 with BOM) |

## Banks (`bank_final/`)

| File | Rows | Content |
|---|---|---|
| `vocabulary_bank.csv` | 6,524 | main vocabulary, all levels in one file (column `level`: A1 1,936 · A2 1,413 · B1 2,526 · B2 377 · C1 272), including about 290 medical-tagged words |
| `b2_vocabulary_bank.csv` | 3,683 | extra B2 words (the first 2,379 chosen by frequency and topic, the rest added from the source list `beyond_goethe_B2.csv`), no medical, none that are in the main bank |
| `phrase_bank.csv` | 1,016 | useful phrases grouped by function |
| `redemittel_bank.csv` | 1,176 | speaking and writing expressions in 55 sets |
| `German_Vault/` | 10,316 notes | the same content as Obsidian notes (generated) |
| `QA_report.md`, `B2_QA_report.md` | | what was checked and what is left |
| `progress.md`, `B2_progress.md`, `changes.csv` | | build history |

## Tools (`work/`)

| Script | Use |
|---|---|
| `bank_tools.py` | main banks: status, validate, export to `German_Bank.xlsx` |
| `b2.py` | B2 bank: add, edit, validate, export to `German_B2_Bank.xlsx` |
| `b2chk.py` | check a list of candidate words against both vocabulary banks |
| `make_vault.py` | rebuild the Obsidian vault from the CSV files (keeps your own notes) |
| `make_level_workbook.py` | rebuild `STUDY_HERE/Word_Lists_by_Level.xlsx` (one sheet per level) |
| `make_study_app.py` | rebuild `STUDY_HERE/German_Study.html` from the CSV files |

Folders `work/audit`, `work/b2_patches` and `work/patches` keep the review samples and the saved input of every batch.
`input/` holds the original source files and must not be changed. `anki/` is not part of this project.

## After changing a bank

```
python3 work/b2.py validate        # or: python3 work/bank_tools.py validate --final
python3 work/make_vault.py         # refresh the Obsidian notes
python3 work/make_study_app.py     # refresh the flashcard page
python3 work/make_level_workbook.py  # refresh the Excel file with one sheet per level
```
