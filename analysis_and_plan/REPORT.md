# German vocabulary analysis: your n-gram lists against the Goethe-Zertifikat lists

*Made on 5 Oct 2026 for Medica. Goethe A1, A2, B1 word lists (the official PDFs) + your five frequency files + the Klett Kontext B2 list as a B2 proxy. The plan starts today and runs to 25 Apr 2027.*

## 1. The short version

- **How much of the Goethe vocabulary your data covers.** Of the 3,402 Goethe word items (A1 + A2 + B1), 72.2 % occur somewhere in your 10,000 most frequent word forms. Per level: A1 85.0 %, A2 71.3 %, B1 67.3 %. Only 62.8 % are frequent (lemma rank ≤ 4000).
- **The gap.** 871 Goethe words (A1 99, A2 190, B1 582) do not occur in your data at all, and 319 more are rare. Your n-gram corpus is book-heavy, so everyday exam words such as the ones in section 5 are simply not in it. These are your **exam-priority list** (`goethe_missing.csv`, 1,301 rows).
- **Beyond Goethe.** 3,285 lemmas in your data are not in any Goethe A1–B1 list (`beyond_goethe_B2.csv`), 270 of them medical. Against the Klett Kontext B2 list, only 35.1 % of its words occur in your data; 1,393 Klett words are new for you.
- **Chunks.** 934 reusable chunks are shortlisted and tagged by communicative function and Goethe task (`chunk_shortlist.csv`): 287 two-word, 288 three-word, 185 four-word, 174 five-word frames.
- **The plan.** 29 weeks, 15 new cards a day (105 a week): **2,145 words + 795 chunks**. W1–W10 (5 Oct – 13 Dec) prepare Goethe B1, W11 (14–20 Dec) is exam week without new cards, W12–W29 (21 Dec – 25 Apr 2027) prepare B2. The files are in `anki/`, ready for your two card skills.
- **Reading.** Graded passages (2 per week, with questions) exist for **W1–W10**. B2 passages are not written yet. `reading/external_resources.md` has verified links for every level.
- **Honest limits.** See section 9. The biggest ones: the lists are only as good as the n-gram corpus; the chunk ratings and medical flags were made by a language model; only about half of the Goethe A2/B1 words that are new for you fit into the 28 weeks (the rest are in `backlog_goethe_words_not_scheduled.csv`).

## 2. What went in

| Input | Rows | Used for |
|---|---|---|
| `1grams_german.csv` | 10,000 word forms | lemmatised, matched against Goethe words |
| `2grams_german.csv` | 5,000 | chunks (2 words) |
| `3grams_german.csv` | 3,000 | chunks (3 words) |
| `4grams_german.csv` | 1,000 | chunks (4 words) |
| `5grams_german.csv` | 1,000 | speaking and writing frames (no cards) |
| Goethe A1, A2, B1 Wortlisten (PDF) | 3,402 word items, 58 multi-word items | the exam vocabulary |
| Klett Kontext B2 word list (CSV) | 2,340 entries | B2 proxy (there is no official Goethe B2 word list) |
| `1grams_master.tsv` (your cards) | 9,983 valid cards | overlap flag only; never changed |

## 3. Cleaning your n-gram files

**1-grams.** 10,000 word forms became **5,763 lemmas**: forms of the same word were merged and the best rank was kept (`data/1grams_lemmatized.csv` shows every merged form and its rank). 296 forms were removed on purpose (`data/1grams_removed.csv`): 119 English/foreign word, 82 proper noun / place or person name (spaCy), 41 proper noun / surname, 18 abbreviation, 17 interjection/filler, 11 archaic/OCR variant, 8 fragment (compound part / suffix). Everything is written with real umlauts.

**2–5-grams.** Every row got a status (`data/ngrams_2to5_normalized.csv`). Only the rows marked *kept* can become chunks; 4- and 5-grams survive only as complete reusable frames (for example *ich glaube nicht, dass*), not as cut-off pieces.

| File | Rows after merging spelling variants | kept as reusable chunk | only function words (in der, und die …) | cut-off fragment | free combination, not a chunk | story-specific (names, plot) | proper noun | book boilerplate / licence text | junk / OCR |
|---|---|---|---|---|---|---|---|---|---|
| 2-grams | 4,975 | 903 | 2,768 | 342 | 872 | 48 | 25 | 8 | 9 |
| 3-grams | 2,956 | 735 | 1,678 | 395 | 0 | 118 | 13 | 15 | 2 |
| 4-grams | 988 | 323 | 314 | 245 | 0 | 61 | 6 | 37 | 2 |
| 5-grams | 991 | 331 | 106 | 275 | 0 | 79 | 23 | 172 | 5 |

The shortlist (`chunk_shortlist.csv`) is the subset of the kept chunks that a language model rated as a useful building block (quality A: 191; quality B with a clear function and non-literary register: 703), plus 40 function-word chunks added by hand (A*). Spelling variants are merged.

## 4. Extracting the Goethe lists, and how it was checked

The three PDFs were parsed entry by entry: article, plural code, verb forms, reflexive marks, separable verbs, regional marks (A/CH), and the Goethe example sentences. Result: **3,402 word items** (A1 788, A2 705, B1 1,909), 58 multi-word items, 10 institution names, and 59 further items that cannot be matched in a frequency list (abbreviations, word stems, “particle + sein”; `data/goethe_not_testable.csv`). The clean table is `data/goethe_wortlisten.csv`.

Quality control:

- **Spot checks.** Five random samples of 30 entries each (stratified: 4 nouns, 3 verbs, 3 other words per list) were compared with the PDF page images while the parser was being built; the parser was corrected wherever a sample showed an error. A final independent check of 30 random entries from the finished table (lemma, and the first words of the first example sentence, against the text of the stated PDF page): **30 of 30 found**. The finished table is identical to the checked units except for the one deliberate correction below.
- **Automatic check of everything.** After the last correction, every extracted unit was compared with the text of its PDF page: the lemma was found for 4,863 of 4,867 units (**99.92 %**) and all 7,545 example sentences were found (**100 %**). The four misses are notation quirks, not extraction errors: *anziehen* (printed as “(an-)/(aus)ziehen”), *entweder … oder*, *Hendl* (Austrian) and *wie viel(e)*.
- **One error in the PDF itself.** The B1 list prints “der Hinweise, -e”. The correct word is *der Hinweis, -e*. It is corrected in the data and flagged there (`lemma_korrigiert`).

## 5. Coverage per Goethe level

“Found” means the Goethe lemma occurs in your data after lemmatisation. “Frequent” means lemma rank ≤ 4000; “rare” means rank above 4000. *Uncertain* means the spelling occurs in your case-folded file only as another word class (for example *die Essen* vs *essen*), so a match could be a false friend.

| Goethe list | Word items | In your data, frequent (lemma rank ≤ 4000) | In your data but rare (rank > 4000) | Uncertain (spelling occurs only as another word class) | Absent from your 10,000 forms | Found (frequent + rare) | Found and frequent |
|---|---|---|---|---|---|---|---|
| A1 | 788 | 614 | 56 | 19 | 99 | 85.0 % | 77.9 % |
| A2 | 705 | 433 | 70 | 12 | 190 | 71.3 % | 61.4 % |
| B1 | 1,909 | 1,091 | 193 | 43 | 582 | 67.3 % | 57.2 % |
| **A1+A2+B1** | 3,402 | 2,138 | 319 | 74 | 871 | 72.2 % | 62.8 % |

Multi-word items (for example *zum Beispiel*, *auf jeden Fall*, *je … desto …*):

| Goethe list | Multi-word items | Present as 2–5-gram in your data | Absent | Not testable in a frequency list |
|---|---|---|---|---|
| A1 | 12 | 3 | 5 | 4 |
| A2 | 17 | 5 | 12 | 0 |
| B1 | 29 | 9 | 20 | 0 |

**B2 proxy (Klett Kontext).** Of 2,314 Klett words, 395 are in your data and in Goethe, 418 are in your data but not in Goethe, 108 are in Goethe only, and **1,393 are in neither**. That last group is the B2 gap (`data/klett_b2_proxy_coverage.csv`).

## 6. The ten biggest gaps, by Goethe theme

Gap = Goethe A2/B1 word that is absent from your data (P1) or rare (P2). The A1 words you should know already are a separate self-check list (P3, 160 words). Counts are per theme of `goethe_missing.csv`; examples are the most common absent words (zipf = outside frequency measure).

| # | Goethe theme | Exam words missing or rare in your data | Most common examples (absent, A2 first) |
|---|---|---|---|
| 1 | T10 Freizeit, Sport, Kultur & Medien | 142 (102 absent + 40 rare) | die Homepage (A2), der/das Blog (A2), das Festival (A2), die Gitarre (A2), das Tennis (A2), der Club (A2), der Basketball (A2), der Zoo (A2) |
| 2 | T03 Arbeit & Beruf | 115 (96 absent + 19 rare) | die Schauspielerin (A2), bewerben (A2), die Bewerbung (A2), die Sängerin (A2), der Rentner (A2), die Künstlerin (A2), Techniker (A2), der Chef (A2) |
| 3 | T08 Reisen, Verkehr & Orte | 111 (92 absent + 19 rare) | unterwegs sein (A2), Österreicher (A2), Luxemburg (A2), der Führerschein (A2), die Baustelle (A2), die Verspätung (A2), die Ampel (A2), parken (A2) |
| 4 | T06 Essen & Trinken | 73 (55 absent + 18 rare) | die Wurst (A2), die Süßigkeiten (A2), die Torte (A2), die Zitrone (A2), das Rind (A2), das Mineralwasser (A2), die Cafeteria (A2), die Nudel (A2) |
| 5 | T07 Einkaufen, Kleidung & Geld | 62 (43 absent + 19 rare) | das T-Shirt (A2), das Einkaufszentrum (A2), leihen (A2), der Pullover (A2), die Creme (A2), das Taschengeld (A2), der Flohmarkt (A2), die Kosmetik (A2) |
| 6 | T02 Wohnen | 56 (36 absent + 20 rare) | die Heizung (A2), das Erdgeschoss (A2), die Schere (A2), aufräumen (A2), schmutzig (A2), die Seife (A2), renovieren (A2), der Vermieter (A2) |
| 7 | T13 Zeit, Zahlen, Maße & Mengen | 50 (41 absent + 9 rare) | um Mitternacht (A2), Ostern (A2), sonntags (A2), der Karneval (A2), Neujahr/Silvester (A2), ein Gramm / ein Kilogramm (A2), der Feiertag (A2), freitags (A2) |
| 8 | T05 Gesundheit & Körper | 50 (38 absent + 12 rare) | fit sein (A2), die Apotheke (A2), die Grippe (A2), schädlich (A2), ausruhen (A2), die Sprechstunde (A2), erkältet sein (A2), aufwachen (B1) |
| 9 | T16 Allgemein (Funktionswörter, abstrakter Wortschatz) | 48 (29 absent + 19 rare) | fertig sein (A2), einzel- (A2), lila (A2), aufmachen (A2), zumachen (A2), sowohl … als auch (B1), weder … noch (B1), entweder ... oder (B1) |
| 10 | T04 Ausbildung, Schule & Studium | 48 (41 absent + 7 rare) | das Abitur (A2), der Workshop (A2), Latein (A2), das Plakat (A2), der Student (A2), das Stipendium (A2), Sekretariat (A2), Stundenplan (A2) |

All priorities in `goethe_missing.csv`: P1 734 exam words absent from your data · P2 258 rare in your data · P3 160 A1 self-check · P4 76 Austrian/Swiss variant only · P5 73 uncertain homograph (check by hand). Rows are grouped by Goethe theme (T01–T16) and sorted by priority.

## 7. Files and what is in them

| File | Rows | What it is |
|---|---|---|
| `matched.csv` | 2,548 | Goethe items found in your data, with level, plural, lemma rank, your gloss, match type and confidence, and up to **3 most frequent chunks** per word (783 items have at least one, 435 have three). It includes the rare and uncertain items, which also appear in `goethe_missing.csv` (by design: found, but weak) |
| `goethe_missing.csv` | 1,301 | Goethe items absent, rare or uncertain in your data, by theme, with priority, example sentences and the nearest chunk. One row per word: where a Goethe entry lists two words (der Bäcker / die Bäckerin) each word has its own row, so the printed text repeats |
| `beyond_goethe_B2.csv` | 3,285 | lemmas in your data beyond Goethe A1–B1, ranked by frequency, with medical flag (117 core, 153 related), usefulness estimate, Klett flag and chunks |
| `chunk_shortlist.csv` | 934 | reusable chunks tagged by communicative function and mapped to the Goethe Sprechen/Schreiben tasks |
| `anki/words/W01…W29_words.txt` | 2,145 | 28 files, one word per line, for the 14-field card skill |
| `anki/chunks/W01…W29_chunks.txt` | 795 | 28 files, one chunk per line, for the “de gram” skill |
| `anki/study_order_*.csv` | 2,145 + 795 | the same items with week, day, date, reason, frequency band, Goethe example, overlap flag |
| `anki/redemittel_5grams.csv` | 174 | five-word frames for speaking and writing (no cards) |
| `anki/backlog_goethe_words_not_scheduled.csv` | 1,129 | Goethe A2/B1 words that did not fit into the 28 weeks |
| `anki/selfcheck_assumed_known.txt` | 374 words | words the plan assumes you know (155 A1 + 219 A2/B1 top-500) |
| `reading/passages_B1_W01-W10.md` | 20 passages | graded passages with questions for weeks 1–10 |
| `reading/external_resources.md` | – | verified links and exam facts for A1–B2 |
| `data/…` | 8 files | clean Goethe table, item status, lemma table, removed forms, normalised n-grams, Klett proxy, items not testable, beyond words dropped |

## 8. The study plan, week by week

**Rhythm.** 15 new cards a day: 10 words + 5 chunks in B1 weeks (day 1 of every week is a Monday). W1–W10 = 70 words + 35 chunks a week; W12–W29 = 80–81 words + 24–25 chunks a week; W11 = exam week with no new cards. If you miss a day, continue from the first undone `seq` number; only the dates move.

**What is in a B1 week (70 words).** 38 Goethe exam words that are absent or rare in your data plus 32 Goethe words that are frequent in your data. 50 of the 70 follow the week's theme (Wohnen, Behörden, Praxis/Apotheke/Krankenhaus …); the other 20 are general words (time, numbers, feelings, language, function words) spread over all weeks. Inside a week the two kinds are interleaved.

**What is in a B2 week (80–81 words).** 24 Goethe words that are still new (14 exam words + 10 frequent), 10 medical words (14 in W12 and W27), 6 connectors / pronominal adverbs for B2 writing (*dazu, darauf, sowie* …), 10 words from the Klett Kontext list that are not in your data, and about 30 frequent words beyond Goethe. Themes: Medizin, Arbeit, Bildung, Umwelt, Medien, Gesellschaft, Wirtschaft, Wohnen, Reisen, Familie, Recht & Behörden (Approbation, Ausländerbehörde), Sprache, Ernährung, Psychologie, Zukunft, Krankenhaus & Patientengespräch (Fachsprachprüfung), Argumentation.

**What is in the chunks.** Over the whole plan: 744 chunks from your n-gram shortlist (2–4 words) and 51 Goethe multi-word items (*weh tun*, *je … desto …* …). Chunks are chosen by function: requests, apologies, complaints, opinions, agreeing/disagreeing, advice and structuring first (the Sprechen/Schreiben tasks need them), then cause, contrast, consequence and condition, then time and quantity. **Frequency bands go from F1 (the most frequent quarter of each length) in the early weeks to F4 (the least frequent) in the late weeks; every week mixes 2-, 3- and 4-word chunks** (see the table). The 174 five-word frames are a separate speaking and writing list, no cards.

| Week | Dates | Theme | Words / chunks | 2- / 3- / 4-word chunks | Main chunk bands | Exam focus of the week (optional Sunday task) | Reading passages (A · B) |
|---|---|---|---|---|---|---|---|
| 1 (B1) | 5 Oct – 11 Oct 2026 | Wohnen & Wohnungssuche | 70 / 35 | 12 / 14 / 9 | F1 + F2 | Sprechen Aufgabe 1 (gemeinsam einen Umzug/eine Besichtigung planen) · Schreiben Aufgabe 1 (persönliche E-Mail über die neue Wohnung) | Die Wohnung besichtigen · Eine E-Mail an Tim |
| 2 (B1) | 12 Oct – 18 Oct 2026 | Behörden, Post & Dienstleistungen | 70 / 35 | 13 / 13 / 9 | F1 + F2 | Schreiben Aufgabe 3 (formelle E-Mail: Termin, Anfrage) · Hören: Durchsagen und Ansagen | Im Amt: Das Visum verlängern · Eine E-Mail über einen langen Tag |
| 3 (B1) | 19 Oct – 25 Oct 2026 | Gesundheit: Praxis, Apotheke, Krankenhaus | 70 / 35 | 13 / 12 / 10 | F1 + F2 | Sprechen Aufgabe 2 (Thema präsentieren: Gesundheit) · Lesen: Gesundheitsinformationen · Fachsprache-Einstieg | Beim Hausarzt · Ein Unfall beim Fußball |
| 4 (B1) | 26 Oct – 1 Nov 2026 | Arbeit & Beruf | 70 / 35 | 15 / 11 / 9 | F1 + F2 | Schreiben Aufgabe 2 (Forumsbeitrag: Meinung) · Lesen: Stellenanzeigen | Das Vorstellungsgespräch · Eine Bewerbung schreiben |
| 5 (B1) | 2 Nov – 8 Nov 2026 | Reisen, Verkehr & Orte | 70 / 35 | 17 / 9 / 9 | F1 + F2 | Sprechen Aufgabe 1 (Ausflug planen) · Hören: Bahnhofsdurchsagen und Reiseberichte | Wie komme ich zum Hauptbahnhof? · Neulich auf dem Weg zur Insel |
| 6 (B1) | 9 Nov – 15 Nov 2026 | Einkaufen, Kleidung & Geld | 70 / 35 | 16 / 10 / 9 | F1 + F2 | Schreiben Aufgabe 3 (Beschwerde/Umtausch) · Lesen: Anzeigen und Preise | Den Pullover tauschen · Eine Beschwerde schreiben |
| 7 (B1) | 16 Nov – 22 Nov 2026 | Essen & Trinken | 70 / 35 | 12 / 14 / 9 | F2 + F1 | Sprechen Aufgabe 3 (Feedback geben, Fragen stellen) · Hören: Einladung, Restaurant | Am Samstag koche ich · Das Rezept für Tim |
| 8 (B1) | 23 Nov – 29 Nov 2026 | Freizeit, Sport, Kultur & Medien | 70 / 35 | 17 / 9 / 9 | F1 + F2 | Schreiben Aufgabe 2 (Meinung zu Medien/Freizeit) · Lesen: Kurztexte | Was machen wir am Wochenende? · Ein Forumsbeitrag: Das Smartphone |
| 9 (B1) | 30 Nov – 6 Dec 2026 | Familie, Schule & Studium | 70 / 35 | 18 / 12 / 5 | F2 + F4 | Modelltest Teil 1: Lesen + Hören mit Zeitlimit · Schreiben Aufgabe 1 | Ein Referat vorbereiten · Eine E-Mail an meine Cousine |
| 10 (B1) | 7 Dec – 13 Dec 2026 | Natur, Umwelt, Gesellschaft & Recht | 70 / 35 | 14 / 13 / 8 | F2 + F3 | Kompletter Modellsatz unter Prüfungsbedingungen (Schreiben + Sprechen) · Aufgabe 2 Forumsbeitrag | Eine Umfrage zum Umweltschutz · Ein Ausflug mit Gewitter |
| 12 (B2) | 21 Dec – 27 Dec 2026 | Gesundheit & Medizin | 80 / 25 | 9 / 9 / 7 | F1 + F4 | B2 Schreiben 1 (Forumsbeitrag: Gesundheitssystem) · Hören B2 | not written yet |
| 13 (B2) | 28 Dec – 3 Jan 2027 | Arbeit & Karriere | 80 / 25 | 9 / 9 / 7 | F1 + F2 | B2 Vortrag: Aufbau und Verknüpfungen · Lesen B2 | not written yet |
| 14 (B2) | 4 Jan – 10 Jan 2027 | Bildung & Wissenschaft | 80 / 25 | 6 / 12 / 7 | F1 + F4 | B2 Schreiben 2 (formelle Nachricht) · Lesen B2 | not written yet |
| 15 (B2) | 11 Jan – 17 Jan 2027 | Umwelt & Klima | 80 / 25 | 10 / 10 / 5 | F1 + F2 | B2 Diskussion: Pro und Contra, Einwände aufgreifen · Hören B2 | not written yet |
| 16 (B2) | 18 Jan – 24 Jan 2027 | Medien, Technik & Freizeit | 80 / 25 | 9 / 12 / 4 | F2 + F1 | B2 Schreiben 1 (Forumsbeitrag: Medien) · Lesen B2 | not written yet |
| 17 (B2) | 25 Jan – 31 Jan 2027 | Gesellschaft & Politik | 80 / 25 | 7 / 11 / 7 | F2 + F1 | B2 Vortrag mit Diskussion · Hören B2 | not written yet |
| 18 (B2) | 1 Feb – 7 Feb 2027 | Wirtschaft, Geld & Konsum | 80 / 25 | 11 / 11 / 3 | F2 + F1 | B2 Schreiben 2 (Beschwerde, Anfrage) · Lesen B2 | not written yet |
| 19 (B2) | 8 Feb – 14 Feb 2027 | Wohnen & Stadt | 80 / 25 | 10 / 8 / 7 | F2 + F3 | B2 Diskussion: Wohnen und Stadtentwicklung · Hören B2 | not written yet |
| 20 (B2) | 15 Feb – 21 Feb 2027 | Reisen & Mobilität | 80 / 25 | 11 / 9 / 5 | F2 + F3 | Erster B2-Modellsatz (ein Modul pro Woche ab jetzt) · Vortrag: Reisen | not written yet |
| 21 (B2) | 22 Feb – 28 Feb 2027 | Familie & Beziehungen | 80 / 25 | 8 / 12 / 5 | F3 + F2 | B2 Schreiben 1 (Forumsbeitrag: Familie) · Lesen B2 | not written yet |
| 22 (B2) | 1 Mar – 7 Mar 2027 | Recht & Behörden (Approbation, Ausländerbehörde) | 80 / 25 | 9 / 11 / 5 | F3 + F2 | B2 Schreiben 2 (formelle Nachricht an eine Behörde) · Hören B2 | not written yet |
| 23 (B2) | 8 Mar – 14 Mar 2027 | Sprache, Kommunikation & Denken | 80 / 25 | 7 / 11 / 7 | F3 + F4 | B2 Diskussion: Argumente strukturieren · Lesen B2 | not written yet |
| 24 (B2) | 15 Mar – 21 Mar 2027 | Ernährung & Sport | 80 / 25 | 10 / 11 / 4 | F3 + F4 | B2 Vortrag: Ernährung · Hören B2 | not written yet |
| 25 (B2) | 22 Mar – 28 Mar 2027 | Psychologie, Gefühle & Charakter | 81 / 24 | 11 / 7 / 6 | F4 + F3 | Zweiter B2-Modellsatz · Schreiben 1 (Forumsbeitrag) | not written yet |
| 26 (B2) | 29 Mar – 4 Apr 2027 | Gesellschaft & Zukunft | 81 / 24 | 8 / 10 / 6 | F4 + F3 | B2 Diskussion unter Zeitlimit · Lesen B2 | not written yet |
| 27 (B2) | 5 Apr – 11 Apr 2027 | Krankenhaus & Patientengespräch (Fachsprache-Vorbereitung) | 81 / 24 | 11 / 10 / 3 | F4 | Anamnese-Rollenspiel (Fachsprachprüfung) · Hören B2 | not written yet |
| 28 (B2) | 12 Apr – 18 Apr 2027 | Argumentation & formelle Texte | 81 / 24 | 10 / 9 / 5 | F4 | Dritter B2-Modellsatz · Schreiben 2 | not written yet |
| 29 (B2) | 19 Apr – 25 Apr 2027 | Wiederholung & Prüfungsstrategie | 81 / 24 | 8 / 8 / 8 | F4 | Komplette B2-Simulation (Schreiben, Sprechen) · Fehlerliste durcharbeiten | not written yet |

**Overlap with your own deck.** 1,571 of the 2,145 planned words already have a cloze card in your `1grams_master.tsv` (column `card_in_your_1gram_master`). The 14-field card is richer (gender colour, declension, collocations), so doing both is fine; skip the duplicate if you prefer. Seven chunks that are already among your 100 existing 2-gram cards were left out.

## 9. Assumptions and limits, honestly

- **The corpus decides what counts as “missing”.** Your n-gram files come from books. Words like *die Apotheke*, *die Briefmarke*, *das Formular* are absent although they are everyday German. Absent from your data = exam priority, not = rare German.
- **Case-folded 1-grams.** Your 1-gram file has no capital letters, so nouns and verbs with the same spelling cannot always be told apart. Such matches are marked *uncertain* (74 items, almost all listed under P5 for checking).
- **Hyphenated and split Goethe items** (for example *E-Mail*, *Fernseher*) match less well; two multi-word items matched only as split chunks.
- **B2 is a proxy.** Goethe publishes no B2 word list. The Klett Kontext list is a coursebook list, not an exam list.
- **Assumed known (not scheduled):** all A1 words; Goethe A2/B1 words in the top 500 of your data (219 words); regional (Austrian/Swiss-only) variants. Check `selfcheck_assumed_known.txt` once.
- **Capacity.** At 15 cards a day only 2,145 words fit into the plan; 1,129 Goethe A2/B1 words are in the backlog file. Use it after April or to swap in words you do not know.
- **Made by a language model, spot-checked but not hand-verified:** the English glosses (`your_gloss`, sometimes the wrong sense of a homograph), the medical flags, the chunk function / register / quality ratings, the usefulness estimate of beyond-Goethe words. Word frequency from an outside source (zipf, `wordfreq`) is only a tie-breaker.
- **Your `1grams_master.tsv` has defects** (138 lines that are not cards, 16 rows with 9 instead of 8 fields). It was read only, never changed.
- **Thin areas in the chunk data:** polite requests (32 chunks), offering help (3), describing a problem (8), apologising (10). Take extra Redemittel from the Goethe Modellsätze linked in `reading/external_resources.md` and from the dialogues in the reading passages.
- **Reading passages** are original practice texts, not exam texts; their familiarity figures are estimates from word lists.

## 10. How to run a week

1. Open `anki/words/Wxx_words.txt` and take the day's block (B1 weeks: 10 lines per day; B2 weeks: 11–12). Paste it into the chat with your 14-field skill (“anki from this list”). Do the same with the day's 5 lines of `anki/chunks/Wxx_chunks.txt` and “de gram”.
2. Import into Anki, do your reviews and the new cards.
3. After day 4 read passage A of the week, after day 7 passage B (`reading/passages_B1_W01-W10.md`).
4. Optional, once a week: say the 5-word frames of one function from `redemittel_5grams.csv` aloud and finish them with your own sentence.
5. Optional, Sunday: one timed task from the week's exam focus (last-but-one column of the plan table).

## 11. Exam facts the plan relies on (from goethe.de; sources in `reading/external_resources.md`)

- **B1 Schreiben:** 60 min. Aufgabe 1 = e-mail (about 80 words), Aufgabe 2 = opinion in a forum (about 80 words), Aufgabe 3 = short e-mail (about 40 words).
- **B1 Sprechen:** about 15 min as a pair. Aufgabe 1 plan something together, Aufgabe 2 present a topic (five slides), Aufgabe 3 give feedback and ask a question.
- **B2:** Schreiben 75 min (forum contribution + formal message); Sprechen 15 min (Vortrag + Diskussion).

## 12. This week: W1, Mon 5 – Sun 11 Oct 2026 (Wohnen & Wohnungssuche)

1. **Today, 5 minutes:** scan `anki/selfcheck_assumed_known.txt`. Any word you cannot translate in two seconds: add it to a later day.
2. **Each day:** 10 lines from `anki/words/W01_words.txt` (Mon = lines 1–10 … Sun = lines 61–70) into your 14-field skill, and 5 lines from `anki/chunks/W01_chunks.txt` (Mon = lines 1–5 …) into “de gram”. The `day` column in the two `study_order_*.csv` files gives the exact split.
3. **Thursday (day 4):** read passage 1A, *Die Wohnung besichtigen* (`reading/passages_B1_W01-W10.md`). **Sunday (day 7):** read passage 1B, *Eine E-Mail an Tim*.
4. **Optional, Sunday:** the exam focus of W1: Sprechen Aufgabe 1 (plan a flat viewing or a move together with a partner, 3 minutes) and Schreiben Aufgabe 1 (a personal e-mail of about 80 words about your new flat, using 5 words from this week).
5. **Next week, Mon 12 Oct:** W2, Behörden, Post & Dienstleistungen: `W02_words.txt`, `W02_chunks.txt`, passages 2A and 2B.

**Next steps (not done yet):** B2 reading passages for W12–W29, a hand check of the medical flags, and, if you want, a second plan that uses the backlog.
