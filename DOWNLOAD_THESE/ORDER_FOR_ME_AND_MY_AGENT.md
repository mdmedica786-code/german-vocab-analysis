# Which list, in which order (for Medica and for the AI agent)

Goal: Goethe B1 in December 2026, then B2 in spring 2027, then FSP.
All files are inside `DOWNLOAD_THESE/1_Words_to_learn.zip` (words, phrases) and `4_Redemittel_up_to_B1.zip`.

## A. Reading / learning order (what Medica studies)

| Step | List | How many | Goal |
|---|---|---|---|
| 1 | `1_B1_exam_Dec2026/A1.csv` | 1,746 words | skim; most are known, only learn the new ones |
| 2 | `1_B1_exam_Dec2026/A2.csv` | 1,293 | same |
| 3 | `1_B1_exam_Dec2026/B1.csv` | 2,418 | main list for the B1 exam |
| 4 | `Redemittel_A2.csv` then `Redemittel_B1.csv` | 93 + 549 | speaking and writing parts of Goethe B1 |
| 5 | `phrases.csv` rows with level A1, A2, B1 | 82 + 163 + 340 | fixed phrases |
| 6 | `2_B2_exam_2027/B2.csv` | 359 | after the B1 exam |
| 7 | `phrases.csv` level B2 + `redemittel.csv` level B2 | 289 + 464 | B2 speaking and writing |
| 8 | `2_B2_exam_2027/B2_extra.csv` | 4,684 | in blocks of about 500 |
| 9 | `3_C1_later/C1.csv`, phrases and Redemittel of level C1 | 252 + 142 + 70 | last, optional |

FSP (medical): the Redemittel marked "FSP" (199 of the 642 up to B1) can be moved forward after the B1 exam.

## B. Card-making order (what the AI agent builds)

Same order as the reading order, one deck at a time. Do not build everything at once.

1. Words A1, then A2, then B1 (input: `3_Anki_JSON_for_AI.zip` -> `anki_json/A1.json`, `A2.json`, `B1.json`). Split B1 into parts of 300-500 words.
2. Phrases (A1, A2, B1) and Redemittel (A2, B1). There is no ready JSON for these; the agent builds the cards from the CSV columns (`phrase_de` or `redemittel_de`, `meaning_en`, `example_de`, `example_en`, `variants`, `grammar_note`).
3. After the B1 exam: `anki_json/B2.json`, then B2 phrases and Redemittel, then `B2_extra.json` in blocks of 500, then C1.

Rules for the agent
- Use the skill `.claude/skills/nerdmedica-de-pro`. Never change any German in the files.
- Audio: `--audio native+edge` (native recordings from `vocab_bank/bank_final/audio`, computer voice only where no recording exists).
- One deck per file, deck name `German_PRO_v3::bank::A1` and so on, a different `--deck-id` for each deck.
- Report the card counts after each deck, and report words without audio.
- Do not use `not_in_study_list.csv` (456 words left out on purpose).
