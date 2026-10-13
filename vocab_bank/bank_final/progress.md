# Progress - German bank build

(Auto status block below is rewritten by `python work/bank_tools.py status --write`.)

<!--AUTO-->
## Status (auto, 2026-10-13 03:49)
- vocab: rows=6524 complete=925 reviewed=800 flagged=347 empty_cells={'example_en': 5133, 'collocations': 328, 'topic': 2830, 'example_de': 2907, 'meaning_en': 1439, 'pos': 850, 'preterite': 544, 'pres_3sg': 369, 'perfect': 369, 'level': 747, 'article': 377, 'plural': 571, 'gov': 6}
- phrase: rows=1016 complete=0 reviewed=0 flagged=1 empty_cells={'meaning_en': 928, 'level': 1016, 'example_de': 979, 'example_en': 1001, 'function': 82, 'register': 59}
- redemittel: rows=0 complete=0 reviewed=0 flagged=0 empty_cells={}
- redemittel total 0/1116 min; categories done 0/55
- redemittel open categories: 55 (first: B1-01 0/18, B1-02 0/18, B1-03 0/18, B1-04 0/14)
- patches applied: 14
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
BLOCK 1 DONE (vocab study_order 1-800, all complete). Now BLOCK 2: Redemittel wave 1 (B1-01..B1-20), one category per step via `work/nx.sh`-style `python3 work/bank_tools.py next redemittel 40 --wave 1`, write with `python3 work/mk.py redemittel` (compact lines: '@B1-01' sets cat; '%sp=..¦au=..¦lv=..¦rg=..¦eu=..' sets defaults; 'NEW¦fn=..¦de=..¦m=..¦ex=..¦en=..¦gn=..¦v=..¦pr=core|extra'). After wave 1: run export, then BLOCK 3 (vocab 801-2500).

## Decisions
- Environment: cloud Linux container; root = repo folder vocab_bank/ (input/, bank_final/, work/). Work is committed to git branch claude/intelligent-maxwell-ubz9a4.
- 3-sense limit for meaning_en is enforced by the tool (prefilled rows with more senses are shortened when reached).

## Open issues
- Helpers: work/mk.py (compact patch writer; auto example_source=claude / level_basis=estimated), work/nx.sh (compact `next`).
- Example warnings from apply (target not in example) are heuristic; false positives for inflected plurals/separable verbs.
