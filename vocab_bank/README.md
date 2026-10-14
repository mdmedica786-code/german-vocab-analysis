# German banks (vocabulary, phrases, Redemittel, B2)

Everything for Medica's German study banks. The finished data is in `bank_final/`.

## What to open

| Goal | Open |
|---|---|
| Study and take notes in Obsidian | folder `bank_final/German_Vault` (Obsidian: "Open folder as vault"), start with `00 Home` |
| Look at the data in Excel | `bank_final/German_Bank.xlsx` (main banks), `bank_final/German_B2_Bank.xlsx` (B2 bank) |
| Use the data in other tools | the CSV files in `bank_final/` (UTF-8 with BOM) |

## Banks (`bank_final/`)

| File | Rows | Content |
|---|---|---|
| `vocabulary_bank.csv` | 6,524 | main vocabulary A1 to C1, including about 290 medical-tagged words |
| `b2_vocabulary_bank.csv` | 2,379 | new B2 words, no medical, none that are in the main bank |
| `phrase_bank.csv` | 1,016 | useful phrases grouped by function |
| `redemittel_bank.csv` | 1,176 | speaking and writing expressions in 55 sets |
| `German_Vault/` | 9,007 notes | the same content as Obsidian notes (generated) |
| `QA_report.md`, `B2_QA_report.md` | | what was checked and what is left |
| `progress.md`, `B2_progress.md`, `changes.csv` | | build history |

## Tools (`work/`)

| Script | Use |
|---|---|
| `bank_tools.py` | main banks: status, validate, export to `German_Bank.xlsx` |
| `b2.py` | B2 bank: add, edit, validate, export to `German_B2_Bank.xlsx` |
| `b2chk.py` | check a list of candidate words against both vocabulary banks |
| `make_vault.py` | rebuild the Obsidian vault from the CSV files (keeps your own notes) |

Folders `work/audit`, `work/b2_patches` and `work/patches` keep the review samples and the saved input of every batch.
`input/` holds the original source files and must not be changed. `anki/` is not part of this project.

## After changing a bank

```
python3 work/b2.py validate        # or: python3 work/bank_tools.py validate --final
python3 work/make_vault.py         # refresh the Obsidian notes
```
