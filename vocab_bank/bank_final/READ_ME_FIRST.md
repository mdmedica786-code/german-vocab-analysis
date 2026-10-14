# bank_final - what is in this folder

If you only want to learn: go to `STUDY_HERE` (one level up, then `STUDY_HERE`). This folder is the finished DATA.

| File | What it is |
|---|---|
| `vocabulary_bank.csv` | main vocabulary, 6,524 words, levels A1-C1 (some medical) |
| `b2_vocabulary_bank.csv` | 4,684 extra B2 words (no medical), not in the main bank |
| `phrase_bank.csv` | 1,016 useful phrases |
| `redemittel_bank.csv` | 1,176 expressions for speaking and writing |
| `German_Bank.xlsx`, `German_B2_Bank.xlsx` | the same data as Excel. First sheet "READ ME FIRST" explains every column. |
| `German_Vault/` | the Obsidian vault (open this folder as a vault; start with `00 Home`) |
| `audio/` | native audio files (only after `work/download_audio.py` was run on a computer with internet) |
| `QA_report.md`, `B2_QA_report.md` | what was checked |
| `progress.md`, `B2_progress.md`, `changes.csv` | build history |

CSV files open in Excel by double-click; if umlauts look wrong, use Data > From Text/CSV and choose UTF-8.

## The columns in plain words (vocabulary files)
`lemma` the word | `article` der/die/das | `plural` | `pos` type of word | `pres_3sg`, `preterite`, `perfect` verb forms | `meaning_en` English | `example_de`, `example_en` example sentence | `collocations` typical word combinations (separated by |) | `level` A1-C1 | `topic` T01-T16 everyday, M1-M4 medical | `skip` yes = not in the study list | `check` flag for review (`dup:B123` same word as B123, `drop?` Austrian/Swiss word) | `exam_use` where the word helps (Lesen, Hören, Schreiben, Sprechen, Alltag). The remaining columns are working data and can be ignored.
