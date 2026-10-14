# B2 bank - QA report

Files: `b2_vocabulary_bank.csv` (UTF-8 with BOM) and `German_B2_Bank.xlsx`.

## Content
- 4,684 rows (3,683 after the beyond_goethe step, then 1,001 more from the Klett Kontext B2 glossary, see COVERAGE_REPORT.md), all level B2, topics T01-T16 (no medical topics). The first 2,379 were chosen by frequency and topic; the other 1,304 were added from the source list `beyond_goethe_B2.csv` (every useful lemma in it that was not yet in a bank; skipped items are in `work/b2_source_skipped.txt`: medical, archaic, vulgar, participle forms and very rare words).
- Words: 1,221 nouns, 421 verbs, 337 adjectives, 323 phrases (Nomen-Verb-Verbindungen, idioms, fixed expressions), 65 adverbs, 7 prepositions, 5 conjunctions.
- Every row has an English meaning, a German example with an English translation, 2-3 collocations and exam-use tags.
- Only words that are NOT in the main `vocabulary_bank.csv` were added (lemma check is automatic), so the two banks do not overlap.

## Checks
- `python3 work/b2.py validate`: 0 errors (required fields, articles, plurals, verb forms, topic and exam-use codes, example length, lemma visible in example, no duplicates).
- Automatic clean-up: 139 rows had a collocation that only repeated the lemma; these were removed. 5 near-duplicate phrases were removed.
- Proof-reading by independent review agents: all 2,379 rows were read once (a 600-row random sample first, then the remaining 1,779 rows). About 3 percent of the rows had a real problem (mostly non-idiomatic or tautological collocations, a few examples that did not show the lemma, a few wrong translations). All reported problems were fixed.
- Rows added after the review (2 corrections) were fixed by hand.

- The 1,304 rows added from the source list were read once more by six independent review agents (218 rows each). About 3 percent (40 corrections: wrong spellings of separable adverbs, unidiomatic collocations, a few wrong examples or meanings) were fixed.

## Limits
- The check was done by language-model reviewers, not by a native speaker. Medica should treat rare words and idioms with care and report anything odd.
- Collocation lists are short (2-3 items) and are meant as examples, not complete lists.
- The `check` column is empty because no uncertain facts were left in the bank.
