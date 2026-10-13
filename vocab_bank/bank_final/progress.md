# Progress - German bank build

(Auto status block below is rewritten by `python work/bank_tools.py status --write`.)

<!--AUTO-->
## Status (auto, 2026-10-13 03:45)
- vocab: rows=6524 complete=586 reviewed=458 flagged=356 empty_cells={'topic': 3067, 'example_en': 5434, 'meaning_en': 1463, 'example_de': 3020, 'collocations': 376, 'pos': 909, 'pres_3sg': 387, 'preterite': 578, 'perfect': 387, 'level': 758, 'article': 380, 'plural': 574, 'gov': 7}
- phrase: rows=1016 complete=0 reviewed=0 flagged=1 empty_cells={'meaning_en': 928, 'level': 1016, 'example_de': 979, 'example_en': 1001, 'function': 82, 'register': 59}
- redemittel: rows=0 complete=0 reviewed=0 flagged=0 empty_cells={}
- redemittel total 0/1116 min; categories done 0/55
- redemittel open categories: 55 (first: B1-01 0/18, B1-02 0/18, B1-03 0/18, B1-04 0/14)
- patches applied: 8
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
BLOCK 1 started. Next: `next vocab 100 --from 1 --to 800`.

## Decisions
- Environment: cloud Linux container; root = repo folder vocab_bank/ (input/, bank_final/, work/). Work is committed to git branch claude/intelligent-maxwell-ubz9a4.
- 3-sense limit for meaning_en is enforced by the tool (prefilled rows with more senses are shortened when reached).

## Open issues
(none yet)
