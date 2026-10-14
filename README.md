# German vocabulary project: map

Start with the folder you need. Each folder has one job.

| Folder | What is in it | Open this first |
|---|---|---|
| `analysis_and_plan/` | **Your daily study plan** and the analysis behind it. | `anki/README_anki.md`, then `anki/words/W01_words.txt` and `anki/chunks/W01_chunks.txt` |
| `anki_cards/` | Card-generation prompt and the `.apkg` backup (German PRO v3). The old 1-gram deck is in `archive/old_1grams_deck/`. | `prompt-for-other-models.md` |
| `vocab_bank/` | The long-running bank build (vocabulary, phrases, Redemittel). **Used by your agent; do not rename.** | `CLAUDE.md` |
| `audio/` | Audio files for each vocabulary item. | `README.md` in that folder |
| `data/` | Raw inputs, read-only: n-gram counts, n-gram batch text files, Goethe/Klett/Netzwerk word lists (PDF/CSV). | – |
| `archive/` | Old 1-gram deck (`old_1grams_deck/`) and old one-off scripts. Kept for history only. | – |

## Inside `analysis_and_plan/`

- `REPORT.md`: full report with the week-by-week plan (section 12 = this week).
- `anki/words/`, `anki/chunks/`: weekly word and chunk lists (W01–W29, no W11).
- `anki/study_order_*.csv`: the same items with week, day, source, theme.
- `reading/`: graded reading passages and external resources.
- `data/`: cleaned and matched data tables.
- `matched.csv`, `goethe_missing.csv`, `beyond_goethe_B2.csv`, `chunk_shortlist.csv`: analysis results.

## Inside `data/`

- `ngrams/`: raw 1- to 5-gram frequency lists.
- `ngram_batches/`: the lists cut into batches of 25 (`1grams/` … `5grams/`).
- `reference_lists/`: official word lists and glossaries.

Note: the scripts in `archive/` contain old `d:/ngram` paths. They will not run as they are.
