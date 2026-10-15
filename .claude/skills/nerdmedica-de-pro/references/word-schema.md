# Word schema — `words.json`

`build_deck.py` reads a JSON list of word dicts. Every dict follows the shape
below.  Fields marked **required** must be present. Everything else is
optional and drives which of the 4 non-mandatory card types get generated.

## Minimum viable word (produces ONLY the Core card)

```json
{
  "en_meaning":   "apartment; flat",
  "de_word":      "Wohnung",
  "gender_class": "die"
}
```

## Full word — all 5 card types possible

```json
{
  "en_meaning":    "apartment; flat",
  "de_word":       "Wohnung",
  "article":       "die",
  "gender_class":  "die",
  "pronunciation": "VOH-nung",
  "de_sentence":   "Ich wohne in einer kleinen <b>Wohnung</b> im Zentrum.",
  "en_sentence":   "I live in a small apartment in the city center.",
  "note":          "One of the most common A1 words. Distinguish from das Haus (house).",
  "declension": {
    "nom_sing": "die Wohnung",
    "nom_plur": "die Wohnungen",
    "dat_sing": "der Wohnung"
  },
  "conjugation": {},
  "case_government": "",
  "collocations": [
    "eine Wohnung mieten",
    "die Wohnung putzen",
    "in einer WG wohnen"
  ],
  "synonyms": { "A1": "das Zuhause",   "C2": "das Domizil" },
  "antonym":  "",
  "tags":     ["netzwerk::A1::kap05", "thema::wohnen"]
}
```

## Field reference

| Field | Type | Required | Drives |
|---|---|---|---|
| `en_meaning`     | str  | ✓  | Core front, all cloze identifiers |
| `de_word`        | str  | ✓  | Core back (word after article), tag basis |
| `gender_class`   | str  | ✓  | Color, POS tag. One of: `der`, `die`, `das`, `verb`, `adj`, `prep` |
| `article`        | str  | opt | Core back. `""` for non-nouns |
| `pronunciation`  | str  | opt | Core back — plain phonetic like `VOH-nung`, no IPA |
| `de_sentence`    | str  | opt | Core back **and** Cloze-Sentence. Must wrap the target in `<b>…</b>` for Cloze-Sentence to trigger |
| `en_sentence`    | str  | opt | Core back + Cloze-Sentence identifier |
| `note`           | str  | opt | Core back — false-friend / register / usage note |
| `declension`     | dict | opt | **Nouns only.** Keys: `nom_sing`, `nom_plur`, `akk_sing`, `akk_plur`, `dat_sing`, `dat_plur`, `gen_sing`, `gen_plur`. Needs any 2 case rows to build the full-declension Cloze-Grammar card |
| `conjugation`    | dict | opt | **Verbs only.** Keys: `praesens_ich`, `praesens_er`, `praeteritum`, `perfekt` (e.g. `"hat gerufen"`), `konjunktiv_ii`, `imperativ`. Needs any 2 rows to build Cloze-Grammar |
| `case_government`| str  | opt | Verb Cloze-Grammar note. Empty string when N/A |
| `collocations`   | list | opt | First item becomes the Cloze-Usage chunk |
| `synonyms`       | dict | opt | CEFR-keyed dict: any of `A1`, `A2`, `A2/B1`, `B1`, `B2`, `C1`, `C2`. Expand card renders every level provided, in that order. Dedupes across levels. Needs ≥ 2 non-empty levels (or 1 level + antonym) to build the card |
| `antonym`        | str  | opt | Expand row (skipped if empty or `"—"`) |
| `word_family`    | list / str | opt | Derivatives — list of strings like `["familiär (adj.)", "der Familienname (n.)", "die Großfamilie (n.)"]` or a comma-separated string. Needs ≥ 2 entries (not equal to target) for the Word Family card |
| `tags`           | list | opt | Extra tags preserved on every generated card |
| `audio_word`, `audio_sentence` | str | auto | Filled by `--audio` as `[sound:file.mp3]`. Leave out of hand-made JSON |

## Which cards are generated when

| Card type | Generated if… |
|---|---|
| Core            | always (needs only the 3 required fields) |
| Cloze-Sentence  | `de_sentence` contains `<b>…</b>` |
| Cloze-Grammar   | Noun with any 2 case rows (nom/akk/dat/gen × sing/plur)  · **or**  Verb with any 2 conjugation forms |
| Cloze-Usage     | `collocations` has at least one item |
| Expand          | At least 2 of {A1, A2, A2/B1, B1, B2, C1, C2, antonym} pass dedup (a piece is dropped if it equals the target or duplicates another row) |
| Word Family     | `word_family` has at least 2 entries that aren't the target itself |

If none of the optional data is present, the word still gets a valid Core
card. **A thin word is never an error.**

## Gender class → color / POS tag

| `gender_class` | Word color (dark / light) | Card POS tag |
|---|---|---|
| `der`  | blue-400 / blue-800   | NOUN |
| `die`  | pink-400 / pink-700   | NOUN |
| `das`  | green-400 / green-700 | NOUN |
| `verb` | purple-400 / violet-700 | VERB |
| `adj`  | cyan-400 / cyan-700   | WORD |
| `prep` | yellow-400 / amber-700 | PREPOSITION |

## Sentence markup — the one non-obvious rule

For Cloze-Sentence to trigger, wrap the target word (or its inflection, or
the separable-verb split) inside `<b>…</b>`.  Multiple `<b>…</b>` in one
sentence become **one** cloze (same c1) — this is exactly what separable
verbs need:

```
"Ich <b>rufe</b> dich morgen <b>an</b>."
   → cloze:  Ich {{c1::rufe}} dich morgen {{c1::an}}.
```

## Automatic input cleaning (`prepare_words`)

Before building, every word is:
- Unicode-NFC normalized (so `ü` typed two different ways never makes two notes)
- Validated for the 3 required fields — invalid entries are skipped with a warning
- De-duplicated on (de_word, gender_class, en_meaning). The first copy wins; tags of
  later copies are merged into it. Netzwerk sources often list a word twice in one
  chapter — this prevents double cards.
