# Anki deck plan (to start later)

Skill saved here: `.claude/skills/nerdmedica-de-pro/` (unpacked, so Claude Code in this repo finds it) and `vocab_bank/skills/nerdmedica-de-pro.skill` (original file).

Goal: build NerdMedica DE PRO `.apkg` decks (6 sub-decks: Core, Production, Grammar, Chunks, Breadth, Family) from
- the main vocabulary bank (`bank_final/vocabulary_bank.csv`, 6,524 rows, levels A1-C1)
- the B2 bank (`bank_final/b2_vocabulary_bank.csv`, 3,683 rows)
- the phrase bank (`bank_final/phrase_bank.csv`, 1,016 rows)

How the bank columns map to the skill's `words.json` (see `.claude/skills/nerdmedica-de-pro/references/word-schema.md`):

| words.json | bank column |
|---|---|
| de_word / article / gender_class | lemma, article (verb -> `verb`, adjective -> `adj`, preposition -> `prep`) |
| en_meaning | meaning_en |
| de_sentence / en_sentence | example_de (wrap the word in `<b>`), example_en |
| collocations | collocations (split on ` | `) |
| declension (nouns) | only nominative singular/plural from `article`, `plural`; other cases are NOT in the bank, so leave them out (never invent) |
| conjugation (verbs) | pres_3sg, preterite, perfect, gov |
| tags | level, topic, bank name |

Decisions to take when we start:
1. One parent deck per level (A1, A2, B1, B2, C1) plus B2 plus, or one big deck with level tags.
2. Phrases: the skill has no phrase note type; use Core (phrase front) or the `nerdmedica-german-ngram` skill.
3. Audio: run `--audio edge` on Medica's own laptop (Microsoft blocks it from the cloud).
4. Deck IDs: `2002001<number>`; keep them fixed so re-imports update instead of duplicating.
