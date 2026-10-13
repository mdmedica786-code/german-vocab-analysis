GERMAN BANK - INPUT README
==========================
Read this file completely before you start. It is the single source of truth for columns, allowed values,
writing rules and the "todo" logic. The RULES blocks (between "### RULES:..." and "### END") must be printed by
the tool command `next` before every batch, so the rules stay in front of you.

Owner: Medica - final-year MBBS student who wants to work as a doctor in Germany (Goethe B1 Dec 2026, B2 spring 2027,
then the Fachsprachprüfung = FSP). English is her working language. Pack created 2026-10-13.
All CSV files: UTF-8 with BOM, comma-separated, standard CSV quoting. Always open with encoding="utf-8-sig".


1. FILES
--------
input\vocabulary_input.csv   6,524 rows: single words and word-like items. 6,140 are scheduled for study
                             (study_order 1..6,140), 384 have skip=yes (still part of the bank).
input\phrases_input.csv      1,016 rows: multi-word chunks, fixed expressions, glossary phrases (greetings etc.).
input\redemittel_plan.csv    55 categories in 3 waves, minimum 1,116 rows in total. There is NO input list:
                             you write the Redemittel yourself from this plan.
input\reference\netzwerk_entries.csv   5,469 raw entries of the Netzwerk neu glossaries A1, A2, B1 with the raw scan text
                             (de_raw, en_raw). Look-up only. Column i = column nw_entry of the vocabulary file.

Results go to bank_final\ : vocabulary_bank.csv (= vocabulary_input.csv, completed), phrase_bank.csv (= phrases_input.csv,
completed), redemittel_bank.csv (new), German_Bank.xlsx, progress.md, changes.csv, QA_report.md.
Scratch goes to work\ . Never change anything in input\ .


2. HOW THE DATA WAS MADE (how far to trust it)
----------------------------------------------
- The Netzwerk neu A1/A2/B1 glossaries (scanned PDFs) were read by OCR: about 97 % of the entries are right. Rows with
  check=ocr? are the doubtful ones: verify spelling, article, plural and meaning first (compare reference\netzwerk_entries.csv).
- English meanings exist only for Netzwerk words. Goethe-only and frequency-only words have none yet.
- Goethe A1-B1 word lists gave levels and many German example sentences (no translations yet).
- Frequency words come from Medica's own German n-gram corpus (freq_rank 1 = most frequent). freq_basis=zipf_estimate means
  a rough estimate from a general list; a value of 5000 or more means "rare or unknown".
- Printed grammar (plural, Präteritum, Partizip II, government) is only partly available. Treat everything prefilled as a good
  seed that may contain scan errors: verify, correct real errors, log them (the tool does this).
- topic (T01-T16) was assigned earlier for about half of the words.
- Glossary phrases such as "guten Tag" or "zu Hause" were moved out of the vocabulary list into the phrase list
  (column old_bank_id keeps the old id). Multi-word verbs/nouns such as "fertig sein" or "Small Talk" stay in the vocabulary list.


3. WORK ORDER AND "todo" LOGIC
------------------------------
Work order inside a bank: vocabulary by study_order ascending (rows without study_order last, by id); phrases in file order;
Redemittel by plan order (wave 1, then 2, then 3).
The tool computes the column todo (pipe-separated names of required columns that are still empty). Empty todo = row complete.

Vocabulary - required for every row: pos, meaning_en, level, register, topic; level_basis whenever level is set.
  kind=noun: article and plural.            (kind=noun_noart, e.g. language names: neither)
  pos=verb: pres_3sg, preterite, perfect.
  pos=preposition: gov.
  skip empty: example_de and example_en.
  skip empty and (key_word=yes or medical=core) and pos in noun/verb/adjective/adverb: collocations.
Phrases - required: meaning_en, function, level, register, example_de, example_en.
Redemittel - every column except variants and check must be filled; at least 70 % of rows should also have variants.
Rows with check=drop? or check=dup:<id> count as complete once their other required cells are filled.


4. VOCABULARY COLUMNS  (vocabulary_input.csv -> bank_final\vocabulary_bank.csv)
-------------------------------------------------------------------------------
[L] = LOCKED: the tool must refuse changes.
id [L]             B0001... stable id
study_order [L]    1 = first word of Medica's default study order; blank = not scheduled (skip=yes)
batch [L]          group of about 25 words (one study day)
lane [L]           book (Netzwerk/Goethe order) or frequency (her n-gram frequency list)
order_freq_first [L]  alternative study order (frequency words first)
skip [L]           yes = not scheduled for active study (already known, cognate/proper name, closed-class function word,
                   transparent compound, prefix/suffix, Swiss/Austrian variant ...), but still part of the bank
skip_reason [L]    why
kind [L]           source structure: noun, noun_noart (noun without article, e.g. language names), verb, word (adjective/adverb/
                   other), prep, affix
pos                part of speech (allowed values below). Prefilled for about 85 %, fill the rest.
lemma              headword without article; verbs in the infinitive; separable verbs unbroken (aufstehen)
article            der / die / das ("der/das" only if both are standard with the same meaning); nouns only
plural             full plural form without article ("Äpfel"); "–" (en dash) = no plural / uncountable;
                   "(Pl.)" = the lemma itself is a plural-only noun; nouns only
pres_3sg           er/sie/es present: "fährt", "steht auf"; verbs only
preterite          er/sie/es Präteritum: "fuhr", "stand auf"; verbs only
perfect            auxiliary + Partizip II: "ist gefahren", "hat gemacht", "hat/ist gewohnt" (both only if both are standard)
sep_prefix         separable prefix (auf, mit, zurück ...); blank if inseparable or none
reflexive          "sich" or "sich (Dat.)"; blank if not reflexive
gov                government in this notation: "+ Akk.", "+ Dat.", "+ Gen.", "+ Akk. | + Dat.", "auf + Akk.", "mit + Dat.",
                   "an + Akk./Dat." Verbs: only when more than a plain accusative object; adjectives with fixed preposition
                   (stolz auf + Akk.); prepositions: the case(s) they take (required)
extra_forms        exceptions only: irregular/umlaut comparison ("besser – am besten"), n-declension ("den/dem/des Studenten"),
                   adjective nouns ("der/die Angestellte; ein Angestellter"), irregular genitive
meaning_en         main English meaning (rules below)
other_senses       further senses, short; optional
note               grammar/usage/false-friend/regional note, max 120 characters; optional
register           allowed values below; prefilled "neutral"
level              CEFR level where learners normally meet the word (A1-C1)
level_basis        netzwerk | goethe | estimated
topic              exactly one allowed topic (list below)
medical            core | related | blank
key_word [L]       yes = frequent A2+ content word or medical core word: needs collocations
example_de, example_en    one example sentence and its translation
example_source     netzwerk | goethe (existing sentence) | claude (written by you)
collocations       typical combinations, German only, separated by " | "
nw_ref [L]         where Netzwerk first shows the word, e.g. "A1 K3 3b" (level, chapter, lesson label)
nw_chapter [L]     title of that chapter (hint for the topic)
nw_entry [L]       row number i in reference\netzwerk_entries.csv
goethe_level [L]   level in the Goethe A1-B1 lists
freq_rank [L]      rank in Medica's frequency list
freq_basis [L]     ngram | zipf_estimate
check              your flags, space-separated (see allowed values)
todo               computed by the tool

Columns the command `next vocab` shows (only non-empty cells, as key=value, to save tokens):
id lemma kind pos article plural pres_3sg preterite perfect sep_prefix reflexive gov meaning_en other_senses note register level
level_basis topic medical key_word skip example_de example_en nw_chapter(only if topic is empty) freq_rank check todo


5. PHRASE COLUMNS  (phrases_input.csv -> bank_final\phrase_bank.csv)
--------------------------------------------------------------------
id [L]  P0001...        order_hint [L]  position in Medica's earlier chunk study plan (1-795), blank for others
phrase_de               the phrase in clean citation form (rules below)
pattern                 fixed | frame (has an open slot)
words [L]               number of words
source [L]              ngram | goethe | netzwerk (combined with +)
function                allowed values below (23)
register                allowed values below
level                   A1-C1 (level at which a learner can use it actively)
level_hint [L]          hint only (B1/B2, or the Goethe/Netzwerk level)
meaning_en  example_de  example_en  grammar_note  variants
exam_use                prefilled hint about exam tasks; keep (blank for glossary phrases)
goethe_level [L]  corpus_freq [L]  quality [L] (earlier usefulness rating A, A*, B or "Goethe list")  rater_note [L] (earlier
remark, e.g. "needs ich" = the chunk lacks "ich")  nw_ref [L]  old_bank_id [L]
check  todo

Columns the command `next phrase` shows: id phrase_de pattern function register level_hint meaning_en example_de example_en
rater_note check todo


6. REDEMITTEL COLUMNS  (new file bank_final\redemittel_bank.csv, written by you)
--------------------------------------------------------------------------------
id [L]        R0001... assigned by the tool when a row is created (patch row with empty id)
wave, cat_id  wave (1, 2 or 3) and category id from the plan (B1-01, B2-01, FSP-01 ...): set when the row is created, locked afterwards
category      German category name from the plan
function      specific sub-function, 2-5 words, e.g. "Vorschlag annehmen", "Schmerzqualität erfragen"
speaker       Arzt | Patient | Pflege | Beide
audience      allowed values below
redemittel_de the expression or sentence frame ("..." marks an open slot)
meaning_en    what it means / does in English
level         A2-C1          register  allowed values below
example_de    a concrete sentence with the slot filled      example_en  natural translation
grammar_note  word order / case / mood that follows, max 100 characters
variants      1-3 alternatives, German, separated by " | "
exam_use      e.g. "Goethe B1 Sprechen Teil 1", "Goethe B2 Schreiben Teil 2", "FSP Anamnese", "FSP Arzt-Arzt", "FSP Arztbrief"
priority      core | extra
source        claude
check
Header line of redemittel_bank.csv (exactly this order):
id,wave,cat_id,category,function,speaker,audience,redemittel_de,meaning_en,level,register,example_de,example_en,grammar_note,variants,exam_use,priority,source,check

redemittel_plan.csv columns: cat_id, wave, group, category_de, category_en, cover (what the category must cover), exam_tasks,
level_range, speaker, audience (defaults), min_count.


7. ALLOWED VALUES
-----------------
pos:       noun, verb, adjective, adverb, preposition, conjunction, pronoun, determiner, numeral, particle, interjection, affix, proper noun
level:     A1, A2, B1, B2, C1
register:  neutral, formal, informal, colloquial, technical, dated, regional, vulgar
level_basis: netzwerk, goethe, estimated        example_source: netzwerk, goethe, claude        medical: core, related
pattern:   fixed, frame
speaker:   Arzt, Patient, Pflege, Beide
audience:  Patient, Angehörige, Kollegen, Prüfer/Publikum, Freunde/Bekannte, Behörde/Firma, Alle
priority:  core, extra
topic (vocabulary) - copy exactly:
  T01 Person, Familie & Beziehungen
  T02 Wohnen
  T03 Arbeit & Beruf
  T04 Ausbildung, Schule & Studium
  T05 Gesundheit & Körper
  T06 Essen & Trinken
  T07 Einkaufen, Kleidung & Geld
  T08 Reisen, Verkehr & Orte
  T09 Behörden, Post & Dienstleistungen
  T10 Freizeit, Sport, Kultur & Medien
  T11 Natur, Umwelt, Wetter & Tiere
  T12 Gesellschaft, Politik, Recht & Geschichte
  T13 Zeit, Zahlen, Maße & Mengen
  T14 Gefühle, Charakter & Meinungen
  T15 Sprache, Kommunikation & Denken
  T16 Allgemein (Funktionswörter, abstrakter Wortschatz)
  M1 Medizin: Anatomie & Körpersysteme
  M2 Medizin: Symptome & Krankheiten
  M3 Medizin: Untersuchung, Diagnostik & Therapie
  M4 Medizin: Klinik, Pflege & Recht
function (phrases) - copy exactly:
  Meinung äußern (give an opinion)
  Zustimmen / Widersprechen (agree, disagree)
  Gründe nennen (cause, reason)
  Folgen (consequence)
  Gegensatz / Einräumung (contrast, concession)
  Bedingung / Zweck (condition, purpose)
  Vergleichen (comparison)
  Sicherheit / Zweifel (certainty, doubt)
  Vorschlagen / Raten (suggest, advise)
  Höflich bitten / fragen (polite request)
  Hilfe anbieten / Service (offer help)
  Entschuldigen / Bedauern (apology, regret)
  Gefühle ausdrücken (feelings)
  Probleme / Beschwerden beschreiben (problem, symptom, complaint)
  Berichten (reporting)
  Gliedern / Verknüpfen (structuring, discourse markers)
  Zeit / Reihenfolge (time, sequence)
  Ort / Richtung (location, direction)
  Menge / Häufigkeit (quantity, frequency)
  Können / Müssen / Dürfen (modal frames)
  Begrüßen / Verabschieden / Danken (greetings, thanks)
  Feste Verbindung / Redewendung (fixed expression, idiom, verb phrase)
  Sonstige nützliche Wendung (other useful expression)
check flags (free text, space-separated): ocr? article? paren? ?plural ?forms ?meaning ?example dup:<id> drop? not-a-phrase?


### RULES:vocab
- German must be flawless. Unsure about a fact -> give your best answer AND add a flag to check (?plural ?article ?forms ?meaning). Never invent.
- Prefilled cells: verify them. Typical scan errors: missing/wrong letters, words glued together ("athome"), wrong gender, cut-off meanings. Correct real errors only (the tool logs it).
- meaning_en: shortest natural English equivalent; max 3 senses, most useful first, separated by "; ". Verbs start with "to ". Nouns without article. Add "≠ ..." in note for false friends (Gift: poison ≠ gift). Medical-only sense: "(med.)". Function words: say what they do ("the (definite article)", "because (conjunction)").
- Nouns: article + full plural form ("Äpfel"); "–" if no plural; "(Pl.)" if plural-only; n-declension / adjective nouns / irregular genitive -> extra_forms. Compounds take the article of the last part.
- Verbs: pres_3sg, preterite, perfect for EVERY verb (separable verbs split: "steht auf", "stand auf", "ist aufgestanden"); sep_prefix; reflexive ("sich" / "sich (Dat.)"); gov when not simply transitive-accusative. Modal and auxiliary verbs too.
- Adjectives: extra_forms only for irregular/umlaut comparison. Prepositions: gov = case(s) ("an + Akk./Dat.").
- level: lowest CEFR level where learners normally meet the word. Empty -> estimate (freq_rank <= 1500 B1, <= 4000 B2, else C1; adjust for obviously easy/hard words) and set level_basis=estimated.
- register: prefilled neutral; change it when the word is clearly formal, informal, colloquial, technical, dated, regional or vulgar.
- topic: exactly one allowed topic. Keep a prefilled topic unless clearly wrong (nw_chapter is a hint). M1-M4 only for clearly medical vocabulary; everyday body/health words stay T05.
- medical: core = used daily in anamnesis/examination/diagnosis/therapy (Schmerz, Fieber, Blutdruck); related = health/hospital vocabulary around it. Add flags for obvious cases; never remove a prefilled flag without a reason.
- Examples (only when skip is empty): 6-14 words, natural spoken or written German, grammar and words at or below the word's level, the word itself in a normal form (separable verbs split correctly), no real people, vary subject/tense/context (don't start every sentence with "Ich"). Medical words (medical=core/related or topic M1-M4): a realistic clinical sentence ("Der Schmerz strahlt in den linken Arm aus."). Keep existing Netzwerk/Goethe sentences (fix scan typos only) and add example_en; write both when both are empty (example_source=claude). example_en natural, not word for word.
- collocations (key_word=yes or medical=core): 2-4 typical combinations, German only, " | " separated, with articles/prepositions ("eine Entscheidung treffen | vor einer Entscheidung stehen").
- note: max 120 characters, only if useful. Keep prefilled notes that are still right.
- skip=yes rows: only the cheap fields (pos, meaning, grammar, level, register, topic); no example or collocations needed.
### END

### RULES:phrase
- phrase_de: clean citation form. Complete fragments ("ich weiß, dass" -> "ich weiß, dass ..."; rater_note "needs ich" means the chunk lacks "ich"). Lower-case start unless it is a full sentence or a greeting; "..." marks an open slot; max 8 words; keep the idea of the original chunk. Fix scan typos in glossary phrases ("athome" -> "zu Hause").
- Garbled or useless chunk -> check=drop? and fill the minimum.
- meaning_en: what it means or does, max 12 words. function: one allowed value (change a prefilled one only if clearly wrong). level: where a learner can use it actively (level_hint is only a hint). register: allowed value.
- example_de: one natural sentence that contains the phrase exactly as written (B1/B2 grammar); example_en natural. Glossary phrases that already have an example keep it.
- grammar_note max 100 characters ("dass-Satz: Verb am Ende", "+ Dat.", "Konjunktiv II = höflicher"); variants: 1-3 near-equivalents, German, " | " separated.
- exam_use is prefilled: keep.
### END

### RULES:redemittel
- One row = one reusable expression or sentence frame for one communicative function. Original, natural, native-level German; "..." marks the slot; 3-14 words (clinical questions up to 16).
- Cover everything in the category's "cover" list and write at least min_count distinct rows (up to +25 % if natural). Include both sides of the dialogue where relevant (speaker Arzt / Patient / Pflege / Beide), formal and informal variants, openers and closers. No near-duplicates (same frame, different noun): put those into variants.
- Fill: wave, cat_id, category, function (2-5 words), speaker, audience, redemittel_de, meaning_en, level (A2-C1), register, example_de (concrete, slot filled), example_en, grammar_note (what follows: "+ dass-Satz: Verb am Ende", "Konjunktiv II"), variants (1-3), exam_use, priority (core = must master, about 60 %, else extra), source=claude.
- B1 categories: B1 grammar (Perfekt, Nebensätze, simple Konjunktiv II). B2 categories: Passiv, Nominalisierung, Konjunktiv II of politeness.
- FSP categories: realistic German clinical practice; Sie-form for adults (du for children); patient-friendly wording when audience=Patient, technical wording when audience=Kollegen; no real patient data; no medical advice beyond neutral illustration.
- Original wording only; do not copy textbook text.
### END


8. COMPLETE EXAMPLE ROWS (style calibration)
--------------------------------------------
Vocabulary, noun:
  lemma=Adjektiv | pos=noun | article=das | plural=Adjektive | meaning_en=adjective | register=neutral | level=A1 | level_basis=netzwerk |
  topic=T15 Sprache, Kommunikation & Denken | example_de=Im Satz fehlt noch ein Adjektiv. | example_en=The sentence still needs an adjective. | example_source=claude
Vocabulary, separable verb:
  lemma=einkaufen | pos=verb | pres_3sg=kauft ein | preterite=kaufte ein | perfect=hat eingekauft | sep_prefix=ein | meaning_en=to shop; to buy groceries |
  register=neutral | level=A1 | topic=T07 Einkaufen, Kleidung & Geld | example_de=Ich kaufe samstags immer im Supermarkt ein. |
  example_en=I always shop at the supermarket on Saturdays. | example_source=claude
Vocabulary, medical key word:
  lemma=Schmerz | pos=noun | article=der | plural=Schmerzen | meaning_en=pain; ache | register=neutral | level=A2 | topic=M2 Medizin: Symptome & Krankheiten |
  medical=core | key_word=yes | example_de=Der Schmerz strahlt in den linken Arm aus. | example_en=The pain radiates into the left arm. |
  collocations=starke Schmerzen haben | über Schmerzen klagen | Schmerzen lindern | der Schmerz strahlt aus
Phrase:
  phrase_de=ich weiß, dass ... | pattern=frame | function=Sicherheit / Zweifel (certainty, doubt) | register=neutral | level=B1 | meaning_en=I know that ... |
  example_de=Ich weiß, dass das nicht einfach ist. | example_en=I know that this is not easy. | grammar_note=dass-Satz: Verb am Ende |
  variants=ich bin sicher, dass ... | mir ist klar, dass ...
Redemittel:
  cat_id=FSP-03 | wave=3 | category=Schmerzanamnese | function=Schmerzqualität erfragen | speaker=Arzt | audience=Patient |
  redemittel_de=Wie würden Sie den Schmerz beschreiben? Eher ... | meaning_en=How would you describe the pain? More like ... | level=B1 | register=neutral |
  example_de=Wie würden Sie den Schmerz beschreiben? Eher stechend oder eher drückend? | example_en=How would you describe the pain? More stabbing or more pressing? |
  grammar_note=Konjunktiv II (würden) = höflich | variants=Können Sie den Schmerz näher beschreiben? | Was für ein Schmerz ist das? |
  exam_use=FSP Anamnese | priority=core | source=claude


9. EXCEL EXPORT (German_Bank.xlsx)
----------------------------------
Sheets: Vocabulary, Phrases, Redemittel, Summary. Header row bold with a fill colour per sheet, frozen header row, autofilter, sensible column
widths, wrapped text for example/meaning/note/collocations columns, ids stored as text. Group (collapse) the provenance columns in
Vocabulary: lane, order_freq_first, skip_reason, kind, level_basis, nw_ref, nw_chapter, nw_entry, goethe_level, freq_rank, freq_basis,
example_source, todo; in Phrases: order_hint, words, source, level_hint, goethe_level, corpus_freq, quality, rater_note, nw_ref, old_bank_id, todo.
Summary: row counts and complete rows per bank; vocabulary by level and by topic; Redemittel by wave and category (rows vs min_count);
number of rows with check flags; date of export.
