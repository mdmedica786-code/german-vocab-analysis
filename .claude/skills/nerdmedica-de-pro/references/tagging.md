# Tag conventions

Every card produced by this skill carries a consistent tag set so Medica can
filter, suspend, or reschedule by any dimension in Anki's Browse window.

## Auto-added on every card

| Tag | Meaning |
|---|---|
| `pro_v3`         | Marks all cards built by this skill. Filter to see everything the skill has produced across chapters. |
| `pos::noun`      | Word is a der/die/das noun |
| `pos::verb`      | Word is a verb |
| `pos::other`     | Adjective, adverb, expression, interjection |
| `pos::prep`      | Preposition |
| `type::core`     | Core note (both DE → EN and EN → DE cards) |
| `type::cloze_sentence` | Sentence production card |
| `type::cloze_grammar`  | Forms drill card |
| `type::cloze_usage`    | Collocation chunk card |
| `type::expand`   | Synonym / antonym CEFR-ladder card |
| `type::word_family` | Derivative-forms card |

## Preserved from the input `words.json`

Any tag in a word's `tags` list is copied verbatim onto every card generated
from that word. `from_apkg.py` automatically forwards tags that start with:

- `netzwerk::`    (e.g. `netzwerk::A1::kap05`)
- `thema::`       (e.g. `thema::family`)
- `goethe::`      (for Goethe-sourced words)

Non-matching tags from the source .apkg are dropped — this keeps the tag
tree clean.

## Practical Browse queries

- `tag:pro_v3` — everything this skill ever built
- `tag:type::expand tag:pos::noun` — synonym drills for nouns only
- `tag:netzwerk::A1::kap04 tag:type::cloze_grammar` — grammar drills from kap04
- `tag:thema::family` — every card thematically tagged "family" across all chapters
- `tag:pro_v3 -tag:type::core` — every card that is NOT recognition

## Suspending a whole card type

If Medica decides Expand cards are too much, in Browse:
1. Search `tag:type::expand`
2. Select all → Right-click → **Toggle suspend**

That mutes all Expand cards without deleting them. Re-enabling later is the
same action.

## Subdecks vs tags

Pacing is controlled by **subdecks** (`::1_Core` … `::6_Family`), each with its own
deck-options preset. Tags are for searching and suspending. Suggested presets:

| Subdeck | New/day (start) | When to raise |
|---|---|---|
| 1_Core | 15 | — |
| 2_Production | 0 → 10 | once Core reviews feel easy |
| 3_Grammar | 0 → 5 | when studying cases / tenses |
| 4_Chunks | 0 → 10 | when speaking/writing practice starts |
| 5_Breadth | 0 → 5 | A2+ |
| 6_Family | 0 → 5 | A2+ |
