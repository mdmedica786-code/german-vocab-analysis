# WORD_LISTS - your vocabulary, ready to use

All of it is the same vocabulary, in the shape you need. **10,752 study words** (6,068 main-bank words A1-C1 + 4,684 extra B2 words), **1,016 phrases**, **1,176 Redemittel**.

| File | Use it for |
|---|---|
| `Word_Lists_by_Level.xlsx` | **see the whole bank in Excel**: sheet "All words" (filter by level, topic, type), then one sheet per level, Phrases, Redemittel, "Not in list" |
| `ALL_WORDS.csv` | the same list as one plain file (UTF-8). Give it to any AI model or import it anywhere. Columns: id, level, topic, type, german, word, article, plural, forms, grammar, meaning_en, example_de, example_en, collocations, exam_use, register, medical, bank, note |
| `by_level/A1.csv` ... `C1.csv`, `B2_extra.csv` | one file per level (smaller files are easier for an AI model; B2 = the 359 B2 words of the main bank, B2_extra = 4,684 extra B2 words) |
| `anki_json/A1.json` ... | **for Anki**: the same words in the input format of your `nerdmedica-de-pro` skill (see below) |
| `phrases.csv`, `redemittel.csv` | the phrases and the speaking/writing expressions |
| `not_in_study_list.csv` | 456 words left out on purpose (country names, duplicates, Austrian/Swiss-only words) with the reason |
| `German_Vault.zip` | **for Obsidian**: unzip, then in Obsidian choose "Open folder as vault" and pick the `German_Vault` folder; start with `00 Home` |

## Make Anki cards with your AI model
Give the model the skill (the folder `.claude/skills/nerdmedica-de-pro`) and one level file, for example:

> Use the nerdmedica-de-pro skill. Build the deck from `WORD_LISTS/anki_json/A1.json` (`python scripts/build_deck.py --words ... --name "German_PRO_v3::bank::A1" --deck-id 2002001001 --out German_PRO_A1.apkg`). Do not change any German in the file. Report the card counts.

Notes about the JSON files:
- Every entry has meaning, example sentence (the word is already marked with `<b>`), collocations and tags (`level::A1`, `thema::...`, `bank::main`, `id::B0123`).
- Declension is included only where it is certain from the data: all four cases for feminine nouns, nominative/accusative/dative for neuter nouns. Masculine nouns have no declension table (add it only if you are sure).
- Verbs have er-form, Präteritum and Perfekt. Cards that need more data (synonym ladder, word family) are simply not created.
- Do big levels in parts if the model is slow: split the JSON list in chunks of 300-500 words.

## Use with any AI model (not only Anki)
Paste a level CSV or a part of `ALL_WORDS.csv` and ask, for example: "Make me a 20-word quiz from this list" or "Group these words into a 7-day plan". Everything the model needs (article, plural, forms, meaning, example) is in the columns.

## Rebuild after changes
`python3 vocab_bank/work/make_word_lists.py` (CSV, JSON, vault zip) and `python3 vocab_bank/work/make_level_workbook.py` (Excel).
