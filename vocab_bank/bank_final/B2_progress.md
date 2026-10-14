# B2 bank – progress (new task: B2 only, no medical, for exams + daily life)
- Output: `bank_final/b2_vocabulary_bank.csv` (UTF-8 BOM) and `bank_final/German_B2_Bank.xlsx`. Tool: `work/b2.py` (add / edit / validate / status / export), `work/b2chk.py` (checks candidates against the main bank). Patches: `work/b2_patches/`.
- Rule: only words NOT already in `vocabulary_bank.csv` (lemma check is automatic). Topics T01-T16 only (no M1-M4). Level B2.
- Target about 2,400 new rows. Batches of at most 100 rows. Plan (theme -> approx rows):
  1 connectors/adverbs/prepositions (done 39) | 2 Nomen-Verb-Verbindungen (done 165) | 3 abstract verbs 250 | 4 abstract nouns 300 | 5 adjectives 250 |
  6 work/economy 200 | 7 society/politics/law 200 | 8 media/digital/tech 180 | 9 environment/energy 150 | 10 education/science 150 |
  11 consumer/finance/housing 150 | 12 culture/leisure/sport/travel 150 | 13 family/feelings/character 150 | 14 admin/services/traffic 120 | 15 verbs with prepositions 100.
- STATUS: DONE. 4,684 rows, 0 validation errors, full-bank review done and all findings fixed (see B2_QA_report.md). Export: German_B2_Bank.xlsx.
- Optional later: add more themes (use work/b2chk.py to find new words, work/b2.py add to append).
