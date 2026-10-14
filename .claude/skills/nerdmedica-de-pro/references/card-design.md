# Card design — 6 note types, 7 card templates

The whole point of this skill: **one word → up to 6 cards, each testing a
different thing.** Enabled by Anki's "bury siblings" + a **separate subdeck per
card type** so Medica can set independent daily new-card limits per tier.

## Guiding rules (do not violate)

1. **CORE is reversible.** DE → EN shows the gender-coloured lemma on the front (reading direction — the article is context, not the answer). EN → DE shows only English on the front; the article + word is the answer. Both live on one note.
2. **No gender leak on CLOZE fronts.** For every non-Core card (Cloze Sentence / Grammar / Usage / Expand / Family), no article or gender-colored word on the FRONT when the article is being tested. The Grammar card clozes articles; the Usage card clozes the whole chunk; the Sentence card clozes the target.
3. **Every cloze card front has an English identifier** — the recognition hook. Never a bare `[...]`. If you can't tell which word is being tested without seeing the answer, the card is broken.
4. **Cards are skipped, never faked.** If a word has no collocation, no usage card. If it has no synonym ladder, no expand card. Never invent German data to fill a row.
5. **Palette adapts.** All CSS respects Anki's `.nightMode` class → looks correct in both light and dark.
6. **One subdeck per card type.** `::1_Core`, `::2_Production`, `::3_Grammar`, `::4_Chunks`, `::5_Breadth`, `::6_Family`. Each subdeck has independent daily limits.

## Type 1 — CORE (reversible: DE → EN and EN → DE)

Subdeck `::1_Core`. Only mandatory note. One note, **two templates → two cards**.
Bury siblings shows only one direction per day.

**Card 1 · DE → EN (reading / recognition)**
```
Front:  [POS]  article de-word            ← gender-coloured lemma
Back:   [POS]  article de-word  /phonetic/
        ─────────
        ENGLISH MEANING                    ← big, the answer
        German sentence (target bold) · English translation · [note] · [audio]
```

**Card 2 · EN → DE (production)**
```
Front:  [POS]  english meaning            ← no article, no gender colour
Back:   [POS]  english meaning
        ─────────
        article de-word  /phonetic/        ← gender-coloured, the answer
        German sentence · English translation · [note] · [audio]
```

Pronunciation line is hidden when empty. Audio fields stay empty unless the
deck was built with `--audio`.

## Type 2 — CLOZE-SENTENCE (production in context)

Skipped if `de_sentence` has no `<b>…</b>` markup.

**Front:**
```
[SENTENCE]
"English translation of the whole sentence"    ← identifier
German sentence with target replaced by [...]
💡 short POS hint
```

**Back:** same layout, target revealed in amber, sentence audio if built with `--audio`.

The hint says only `noun` / `verb` / `adjective / expression` — never the article.

## Type 3 — CLOZE-GRAMMAR (forms drill)

For **nouns**: 4-case × 2-number table. Cloze grouped per case → **4 review cards per noun**, each testing "recall both singular and plural articles for this case". Bury-siblings keeps only one on screen per day.

For **verbs**: all available tenses. `{{c1}}` covers the Präsens block (ich + er together), then c2..cN for Präteritum · Perfekt · Konjunktiv II · Imperativ as data provides. Typically 3–5 review cards per verb.

For **adj / prep / other**: not generated.

**Front (noun example — full declension):**
```
[GRAMMAR · NOUN]
english meaning                     ← header (no article shown)

              Singular      Plural
Nom:      [...] Wohnung   [...] Wohnungen
Akk:      [...] Wohnung   [...] Wohnungen
Dat:      [...] Wohnung   [...] Wohnungen
Gen:      [...] Wohnung   [...] Wohnungen
```

Each `[...]` row-pair is one cloze number → the card being reviewed shows *only its case's articles* blanked, the other three rows fully filled.

**Front (verb example — full conjugation):**
```
[GRAMMAR · VERB]
infinitive — english meaning        ← header (base form, no conjugations)

Präsens:        ich [...] · er/sie [...]
Präteritum:     [...]
Perfekt:        hat [...]
Konjunktiv II:  [...]
Imperativ:      [...]
```

**Back:** clozes filled in amber. Optional red note explains the rule.

## Type 4 — CLOZE-USAGE (one real-world chunk)

Uses the first collocation. **Clozes the whole chunk** — no gender leak from
words like `eine` / `der` / `im` in the frame.

**Front:**
```
[USAGE]
"english meaning"       ← identifier (same string as Core front)
[...]
```

**Back:**
```
[USAGE]
"english meaning"
eine DE-Word mieten     ← whole chunk revealed
```

## Type 5 — EXPAND (vocabulary breadth, full CEFR ladder)

Subdeck `::5_Breadth`. Reads whichever CEFR levels the source populated, in order
A1 → A2 → A2/B1 → B1 → B2 → C1 → C2, then antonym. Each level gets its own
cloze so Medica drills them separately.

Dedupes across the whole ladder — if a B2 synonym duplicates the A1, the B2
row is dropped. If one level has `"X / Y"` and `X` appeared in a prior level,
only `Y` survives.

Card is skipped entirely if fewer than 2 clean rows remain.

**Front:**
```
[EXPAND]
english meaning

A1 (everyday):      [...]
A2 (common):        [...]
B1 (standard):      [...]
B2 (advanced):      [...]
C1 (academic):      [...]
C2 (upgrade):       [...]
antonym:            [...]
```

Only rows the source provides appear. Current `netzwerk::A1` source has
A1 / A2/B1 / C2 populated. B2 and C1 appear only when added to the source
file — the skill will NEVER invent German synonyms it isn't sure of.

**Back:** amber-highlighted answers, each a different cloze so review is spaced.

## Type 6 — WORD FAMILY (derivational knowledge)

Subdeck `::6_Family`. Tests the derivatives of a word, so once Medica knows
*Familie* she can also recognize *familiär*, *Familienname*, *Großfamilie*.

Reads the source `word_family` field: a comma-separated list like
`familiär (adj.), der Familienname (n.), die Großfamilie (n.)`. Each entry
becomes one cloze line. POS annotations in parens are kept because they help
the user categorize the derivative when it's revealed.

**Front:**
```
[FAMILY]
die Familie — family

  • [...]
  • [...]
  • [...]
```

**Back:** each item revealed in amber.

Skipped if the field has fewer than 2 genuine entries, or if all entries are
the target word itself.

## Color palette (both modes)

| Role | Dark | Light |
|---|---|---|
| Page/card BG      | `#1F1F23`  | `#FAFAF9` |
| Body text         | `#E5E7EB`  | `#1F2937` |
| Muted / identifier| `#9CA3AF`  | `#6B7280` |
| Cloze accent      | `#FBBF24`  | `#B45309` |
| der (masculine)   | `#60A5FA`  | `#1E40AF` |
| die (feminine)    | `#F472B6`  | `#BE185D` |
| das (neuter)      | `#34D399`  | `#047857` |
| verb              | `#C084FC`  | `#6D28D9` |

## The layout constants that matter

- Card padding: `24px 18px` desktop, `16px 12px` on narrow (<500px) screens.
- POS tag is a small pill, letter-spaced, uppercase, muted color.
- Identifier is centered italic under the tag, quote marks are half-opacity.
- Notes are a red-tinted box with a 3px left border, muted red text.

These are frozen in `scripts/nerdmedica_de_pro.py::CSS`. Only edit if the
user asks for a design change.
