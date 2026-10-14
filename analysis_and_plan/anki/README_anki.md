# Anki study files: how to use them

This folder is the daily part of the plan. Every word and chunk in it comes from your own files: your n-gram lists, the Goethe-Zertifikat word lists (A1, A2, B1) and your Klett Kontext B2 list. Nothing was invented.

**Start here:** week 1 begins today, Mon 5 Oct 2026. Use `words/W01_words.txt` and `chunks/W01_chunks.txt`. The week-by-week plan, the coverage numbers and the limits are in `../REPORT.md` (section 12 = this week).

## The rhythm

- **15 new cards per day = 105 per week.** Day 1 of every week is a Monday. The plan starts today, 5 Oct 2026.
- **W1–W10 (5 Oct – 13 Dec 2026): Goethe B1 preparation.** 70 words + 35 chunks per week (10 + 5 per day) = 700 words + 350 chunks.
- **W11 (14–20 Dec 2026): exam week, no new cards.** Only Anki reviews, speaking aloud and timed writing. (Move the whole plan if your exam date is different; nothing else depends on the dates.)
- **W12–W29 (21 Dec 2026 – 25 Apr 2027): B2 preparation.** 80–81 words + 24–25 chunks per week = 1,445 words + 445 chunks.
- If you miss days, do not cram. Continue from the first undone `seq` number in the two `study_order_*.csv` files. Only the dates shift.

## Files

| File | What it is |
|---|---|
| `words/W01_words.txt` … `W29_words.txt` (no W11) | One word per line, in study order, ready to paste into your **14-field card skill** ("anki from this list"). Nouns carry article and plural exactly as Goethe prints them, for example `die Apotheke, -n`; verbs carry their principal parts; `(Sg.)` / `(Pl.)` mean singular-only / plural-only. |
| `chunks/W01_chunks.txt` … `W29_chunks.txt` (no W11) | One chunk per line, in study order, ready to paste with **"de gram"** (the 8-field cloze skill). Two- to four-word chunks from your n-gram files plus Goethe multi-word items such as `weh tun`, `je … desto …`. |
| `study_order_words.csv` | The same words with week, day, date, source pool, why it is scheduled now, theme, frequency band, lemma rank, Zipf, Goethe example sentence and an overlap flag. |
| `study_order_chunks.csv` | The same chunks with week, day, communicative function, register, quality, frequency band, words beyond A1 and the Goethe exam task where the chunk is useful. |
| `redemittel_5grams.csv` | 174 five-word frames (`ich glaube nicht, dass` …) sorted by communicative function. **No cards:** use them as speaking and writing frames (complete the frame aloud, then in writing). |
| `selfcheck_assumed_known.txt` | Words the plan assumes you know: 155 A1 words that are rare in your data and 219 A2/B1 words from the top 500 of your data. Scan it once; add any word you cannot translate in two seconds. |
| `backlog_goethe_words_not_scheduled.csv` | 1,129 Goethe A2/B1 words that did not fit into the 28 weeks, grouped by theme. Use it to continue after April or to swap a word you already know. |

## How to run a day

1. Open `words/Wxx_words.txt` and take today's block. In B1 weeks that is 10 consecutive lines (Monday = lines 1–10, Tuesday = 11–20 …); in B2 weeks 11–12 lines per day. The `day` column in `study_order_words.csv` gives the exact split.
2. Paste the block into the chat with your 14-field skill. Do the same with today's 3–5 lines from `chunks/Wxx_chunks.txt` and "de gram". You can also generate a whole week at once, in batches of 25 as you do now.
3. Import the cards into Anki and study them. In weeks 1–10, also read the two graded passages of the week (file `../reading/passages_B1_W01-W10.md`) after day 4 and day 7. Passages for the B2 weeks (W12–W29) are not written yet.

## Choices the plan makes (change them if they do not fit you)

- **A1 is assumed known.** Goethe A1 words that are missing from your data are in the self-check list, not in the plan.
- **Top-500 words are assumed known.** Goethe A2/B1 words whose lemma is in the top 500 of your 1-gram data (`als`, `dass`, `wenn`, `wieder`, `lassen` …) are not scheduled.
- **Austrian/Swiss-only variants are skipped** (listed as priority P4 in `goethe_missing.csv`).
- **Week themes drive the Goethe words.** Week 1 is Wohnen, week 3 is Praxis/Apotheke/Krankenhaus, week 2 is Behörden and Post, and so on. The general-theme words (time, numbers, feelings, language, function words) are spread over all weeks.
- **Chunks are chosen by function, not by theme.** Requests, apologies, complaints, opinions, agreeing and disagreeing, advice and structuring come first because the B1 Sprechen and Schreiben tasks need them. Cause, contrast, consequence and condition follow, then the more frequent time and quantity chunks.
- **Chunk lengths are mixed inside every week.** A typical B1 week has about 15 two-word, 12 three-word and 8 four-word chunks. The column `freq_band_in_length` (F1 = most frequent quarter of its length, F4 = least frequent) shows the order: the early weeks are mostly F1 and F2, the late weeks mostly F3 and F4, but every week mixes 2-, 3- and 4-word chunks.
- **Nouns beyond the Goethe lists have no article in the word files**, because your n-gram files are case-folded and carry no gender. The card skill adds article and plural when it builds the card.

## Overlap with cards you already have

- `card_in_your_1gram_master = y` in `study_order_words.csv` means your `1grams_master.tsv` already holds a cloze card for one of the word's forms. The 14-field card is richer (gender colour, declension, collocations), so doing both is fine; skip the duplicate if you prefer.
- Seven shortlisted chunks (`vor allem`, `ein paar`, `nicht mehr`, `noch nicht`, `nicht nur`, `aber auch`, `gar nicht`) are already among your 100 existing 2-gram cards and were left out of the weekly files.
- Where a Goethe multi-word item is also a frequent chunk in your data (`zum Beispiel`, `auf jeden Fall`, `noch mal`, `als ob`, `ein bisschen` …), it appears once, in the week of its theme, with the chunk information attached.

## Things to know before you trust it blindly

- Your n-gram corpus is book-heavy, so everyday exam words such as `die Apotheke`, `die Briefmarke` or `das Formular` are missing from it. That is why the plan treats "absent from your data" as exam priority, not as "rare German".
- `lemma_rank` and `freq_band` describe your corpus. `zipf_de_wordfreq` is an outside modern-German frequency measure, used only as a tie-breaker.
- The n-gram data are thin on polite requests, offering help, describing a problem and apologising (a handful of chunks each). Take extra Redemittel from the dialogues in the B1 reading passages (`../reading/passages_B1_W01-W10.md`) and from the Goethe Modellsätze linked in `../reading/external_resources.md`.
- The communicative function, register and quality of each chunk and the medical flags of beyond-Goethe words were assigned by a language model and spot-checked, not hand-verified.
