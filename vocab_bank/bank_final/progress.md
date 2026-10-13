# Progress - German bank build

(Auto status block below is rewritten by `python work/bank_tools.py status --write`.)

<!--AUTO-->
## Status (auto, 2026-10-13 04:20)
- vocab: rows=6524 complete=2595 reviewed=2499 flagged=277 empty_cells={'example_en': 3562, 'topic': 1943, 'example_de': 2312, 'preterite': 337, 'meaning_en': 1320, 'plural': 546, 'pos': 583, 'level': 691, 'pres_3sg': 258, 'perfect': 258, 'article': 358, 'collocations': 98, 'gov': 3}
- phrase: rows=1016 complete=0 reviewed=0 flagged=1 empty_cells={'meaning_en': 928, 'level': 1016, 'example_de': 979, 'example_en': 1001, 'function': 82, 'register': 59}
- redemittel: rows=408 complete=408 reviewed=0 flagged=0 empty_cells={}
- redemittel total 408/1116 min; categories done 20/55
- redemittel open categories: 35 (first: B2-01 0/24, B2-02 0/24, B2-03 0/18, B2-04 0/18)
- patches applied: 66
<!--/AUTO-->

## How to resume
Run `PYTHONUTF8=1 python3 work/bank_tools.py status`, then continue with the NEXT STEP below. Never restart.
Tool notes: patch value `__CLEAR__` empties a cell; `""` leaves it unchanged. A vocab/phrase row included in a patch counts as *reviewed*
(`next` lists only unreviewed rows; `next ... --incomplete` lists reviewed rows that still have a todo). topic accepts codes (T05, M2);
function accepts the German head (e.g. "Meinung äußern"). Patches are in work/patches/NNN.json (001.. in order).

## Work order
BLOCK 1 vocab study_order 1-800 | BLOCK 2 Redemittel wave 1 + export | BLOCK 3 vocab 801-2500 | BLOCK 4 phrases + export |
BLOCK 5 Redemittel wave 2, 3 + export | BLOCK 6 remaining vocab, then skip=yes rows + export | BLOCK 7 QA + final export

## Current block / NEXT STEP
BLOCK 1 DONE (vocab study_order 1-800). BLOCK 2 DONE (Redemittel wave 1, B1-01..B1-20: 408 rows, min 366; export run).
NEXT: BLOCK 3 DONE (vocab 801-2500 complete, 0 errors). BLOCK 4 = phrase bank: `work/nx.sh phrase 100`, write with `python3 work/mk.py phrase`, repeat until 1016 rows complete, then export. After that BLOCK 5 (Redemittel waves 2+3), BLOCK 6 (vocab 2501+), BLOCK 7 (QA).
Then BLOCK 4 phrases (`work/bank_tools.py next phrase 100`), BLOCK 5 Redemittel wave 2 then 3, BLOCK 6 remaining vocab then skip=yes, BLOCK 7 QA.

## Decisions
- Environment: cloud Linux container; root = repo folder vocab_bank/ (input/, bank_final/, work/). Work is committed to git branch claude/intelligent-maxwell-ubz9a4.
- 3-sense limit for meaning_en is enforced by the tool (prefilled rows with more senses are shortened when reached).

## Open issues
- Helpers: work/mk.py (compact patch writer; auto example_source=claude / level_basis=estimated), work/nx.sh (compact `next`).
- Example warnings from apply (target not in example) are heuristic; false positives for inflected plurals/separable verbs.
- B3126 meaning_en has >3 senses (prefilled): shorten when reached.
- Duplicate lemmas created by correcting scan errors (earlier rows were fixed, flag the LATER row with dup:<id> when reached): B3661 dup:B5159 (veröffentlichen), B5624 dup:B0608 (Öl), B5851 dup:B0262 (Café).
- patch 019 and 032 files exist but were REJECTED (fixed and re-applied as 020 and 033). state.json counts only applied patches.
