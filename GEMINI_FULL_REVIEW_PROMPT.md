You are a senior German language teacher (CEFR A1 to C1, Goethe-Zertifikat) and a meticulous proofreader and data auditor.

I attached a zip of my German vocabulary project. Another AI (Claude) helped write it. I want a FULL ERROR REPORT. Check every minor error: spelling, umlauts, ß, capitalization, articles, plurals, grammar, punctuation, English wording, and data consistency. Do not skip files because they are large. If you cannot read everything, say exactly what you did and did not check.

## Start here
Read README.md and REVIEW_PROMPT.md. The project has these parts:
- anki_cards/W01_deck_source_readable.json: 70 words for week 1 with sentences, declension/conjugation, collocations, synonyms, word families.
- vocab_bank/input/vocabulary_input.csv, phrases_input.csv, redemittel_plan.csv: the word, phrase and Redemittel bank (about 6,500 + 1,000 rows). vocab_bank/input/README_input.txt explains the columns.
- analysis_and_plan/anki/words/W*_words.txt and chunks/W*_chunks.txt: the weekly lists.
- analysis_and_plan/anki/study_order_words.csv and study_order_chunks.csv: the plan with levels, themes, example sentences.
- analysis_and_plan/REPORT.md and the other CSVs in analysis_and_plan/.
Ignore: archive/, data/ngram_batches/, and the PDFs.

## What to check in every German entry
1. Spelling: ä ö ü ß (never ae/oe/ue/ss as substitutes), capitalization of nouns, old spelling (daß, gewiß), typos, stray spaces or characters, broken encoding (Ã¼ etc.).
2. Nouns: article (der/die/das), plural, genitive singular, dative plural, n-declension nouns, nouns that are singular-only or plural-only.
3. Verbs: infinitive, er/sie Präsens (vowel change), Präteritum, Partizip II, haben vs sein, separable/inseparable prefix, reflexive, case government (Akk./Dat./Gen./prepositions).
4. Adjectives and adverbs: wrong word class, comparative/superlative, irregular forms.
5. Example sentences: grammar, word order, case, natural wording, level fit (A1 to B2), the target word really appears, and the sentence matches the meaning.
6. English meanings and English sentences: wrong, too vague, missing a main sense, false friend, unnatural, spelling.
7. Collocations, synonyms (are they truly synonyms? is the CEFR level right?), antonyms, word families (do they really belong to the word?).
8. Level labels (A1/A2/B1/B2) that look wrong, wrong themes, wrong part of speech tags.
9. Register labels (formal/informal/spoken) that are wrong.
10. Standard German (Germany). Flag Austrian/Swiss-only forms.

## What to check in the data and plan
- Duplicate words or phrases (same word in two rows, or in two weeks).
- Rows with missing required values, empty cells, wrong column counts, shifted columns.
- IDs that repeat or skip, ordering errors.
- Numbers in REPORT.md and README files that do not match the real files (count them yourself).
- Contradictions between files.
- Words in weekly lists that are missing from study_order_*.csv, or the other way round.
- Folder structure: misplaced or confusing files.

## Rules
- Report only REAL problems, but report ALL of them, including tiny ones.
- Never guess. If unsure, write "UNSURE" and give the reason. Do not invent errors.
- For every error give the exact file and the exact row (ID or line number) so I can find it.
- Do not rewrite the project. Give the fix for each error.

## Output format
Part A. Coverage: which files and how many rows you really checked, and what you could not check.
Part B. Error table, one row per error, sorted by severity:
Severity | File | Row/ID/line | Field | Current text | Problem | Correct text
Severity: HIGH = wrong German or wrong meaning that would teach a mistake. MEDIUM = unnatural, imprecise, inconsistent. LOW = typo, punctuation, style.
Part C. Patterns: mistakes that repeat (for example "all plurals of nouns in -er are missing the umlaut"). One line each, with a count.
Part D. Counts: total errors by severity and by file.
Part E. Top 20 fixes to do first.
Part F. Verdict: German quality of the W01 cards (1 to 10) and of the vocab bank (1 to 10), with one sentence each.
If your answer is too long for one message, split it into numbered parts and tell me when you are done.
