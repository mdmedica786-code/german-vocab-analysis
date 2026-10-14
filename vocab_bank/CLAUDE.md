# German bank build (Medica)

This folder holds a long-running build of three German banks: vocabulary, phrases, Redemittel.

- Full task and rules: `CLAUDE_CODE_PROMPT.txt` (read it at the start of every session). Data dictionary and writing rules: `input\README_input.txt`.
- Resume rule: if `bank_final\progress.md` exists, read it first and continue with the next unfinished step. Never restart and never redo finished blocks.
- Hard rules: `input\` is read-only. Write only to `bank_final\` and `work\`. Never delete files. Never touch `anki\` or any other folder. CSV files are UTF-8 with BOM (`encoding="utf-8-sig"`). Never print whole data files. German must be flawless; unsure facts get a flag in the `check` column. Do not ask questions.
- Tools: `work\bank_tools.py` (status, next, apply, validate, export), `work\b2.py` and `work\b2chk.py` (B2 bank), `work\make_vault.py` (Obsidian vault in `bank_final\German_Vault`). `work\make_study_app.py` (flashcard page `..\STUDY_HERE\German_Study.html`). See `README.md` for the file map.
