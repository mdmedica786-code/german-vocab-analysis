# B2 bank - QA report

Files: `b2_vocabulary_bank.csv` (UTF-8 with BOM) and `German_B2_Bank.xlsx`.

## Content
- 2,379 rows, all level B2, topics T01-T16 (no medical topics).
- Words: 1,221 nouns, 421 verbs, 337 adjectives, 323 phrases (Nomen-Verb-Verbindungen, idioms, fixed expressions), 65 adverbs, 7 prepositions, 5 conjunctions.
- Every row has an English meaning, a German example with an English translation, 2-3 collocations and exam-use tags.
- Only words that are NOT in the main `vocabulary_bank.csv` were added (lemma check is automatic), so the two banks do not overlap.

## Checks
- `python3 work/b2.py validate`: 0 errors (required fields, articles, plurals, verb forms, topic and exam-use codes, example length, lemma visible in example, no duplicates).
- Automatic clean-up: 139 rows had a collocation that only repeated the lemma; these were removed. 5 near-duplicate phrases were removed.
- Proof-reading by independent review agents: all 2,379 rows were read once (a 600-row random sample first, then the remaining 1,779 rows). About 3 percent of the rows had a real problem (mostly non-idiomatic or tautological collocations, a few examples that did not show the lemma, a few wrong translations). All reported problems were fixed.
- Rows added after the review (2 corrections) were fixed by hand.

## Limits
- The check was done by language-model reviewers, not by a native speaker. Medica should treat rare words and idioms with care and report anything odd.
- Collocation lists are short (2-3 items) and are meant as examples, not complete lists.
- The `check` column is empty because no uncertain facts were left in the bank.
