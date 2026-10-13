# QA report – German bank (final)

## Result
- `validate --final`: **0 errors**, 0 incomplete rows (vocab 6,524 / phrase 1,016 / Redemittel 1,176).
- Redemittel: 55/55 categories at or above their minimum, 1,176 rows (minimum 1,116), 100% with variants, core share 64% (target about 60%, allowed 50–70%).
- Row ids, row order and locked columns are unchanged. No row was deleted or merged. Every change to an existing cell is logged in `changes.csv`.

## Audits (independent read of random samples, fixed afterwards)
| Bank | Sample | Real errors found | Unsure | Fixed |
|---|---|---|---|---|
| Vocabulary | 150 | 8 (about 5%) | 4 | all 12 |
| Phrases | 60 | 1 | 1 | both |
| Redemittel | 80 | 2 | 1 | all 3 |

Typical vocab findings: missing plural, a missing meaning sense, reflexive `sich` missing in the perfect, level one step too low.
Because about 5% of the sampled vocab rows had a real error, expect roughly 200–300 similar small errors in the whole vocab bank. Sampled errors only were fixed.

## Rows still carrying a check flag
- Vocabulary: 20 rows – 12 `dup:` (homographs or variants, kept on purpose), 3 `spelling?` (Start-Up, Europäische Parlament, zuviel), 2 `ocr?` (kleinmachen, diätisch), `?plural` Beisl, `article?` Like, `?article` Bord.
- Phrases: 226 rows – 224 `dup:<id>` (duplicate or near-duplicate expressions, kept because rows cannot be merged) and 2 `drop?` (P0830 Heavy Metal, P0839 Confoederatio Helvetica: not useful as phrases).
- Redemittel: 0 rows.
- Total flagged rows: 246.

## Known deviations from the working rules
- Three steps went over the size limit: one Redemittel step had 50 rows (FSP-17 + FSP-18), and two vocab steps had 114 and 100+ rows.
- Some rows were only touched for topic or part of speech (the skip=yes rows). Their meanings are the short original ones, not re-written.
- The tool prints "target not in example?" warnings for many examples. Almost all are false positives: inflected forms, hyphenated compounds, slot phrases.
- Regional words (Austrian, Swiss) are marked `register=regional`. They are not needed for Germany.
- Austrian/Swiss school terms (AHS, BHS, Neue Mittelschule) are described briefly; check them if you ever need them.

## Suggested follow-ups
1. **Second full proof-read of the vocab bank (about 5% error rate in the sample).** Start with the medical topics M1–M4 and the C1 rows that were filled last (ids B5xxx–B6xxx), then the rest.
2. **Native check of the FSP Redemittel (FSP-01 to FSP-22)** by a German doctor or an FSP trainer. Medical wording, register toward patients and the Arzt-Arzt tone matter most there.
3. **Prune and prioritise phrases.** Decide for the 224 `dup:` and 2 `drop?` phrase rows which one to keep. Mark about 300 phrases as core, so the study load per week stays realistic for B1 in Dec 2026 and B2 in spring 2027.
