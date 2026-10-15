---
name: nerdmedica-de-pro
description: Generate Medica's NerdMedica DE PRO 6-card-type Anki deck (.apkg) from any German vocabulary source — an existing 14-field .apkg, a Netzwerk / Goethe PDF chapter, a textbook photo, or a plain vocab list. ALWAYS use when Medica says 'de pro', 'de anki pro', 'nerdmedica de pro', 'german pro', 'pro cards', 'pro anki', 'convert my kap X to pro', 'rebuild this chapter as pro', 'the new format', 'the 6-card system', or attaches a German .apkg / vocab source and asks for pro / bury-siblings / subdeck cards. Also use to rebuild an existing PRO deck while keeping study progress, or to add native TTS audio to German cards. Output is a downloadable .apkg with 6 subdecks (reversible Core, Production, Grammar, Chunks, Breadth, Family), light+dark theme, tags preserved. Do NOT use for the old 14-field TSV format (nerdmedica-german-anki), German grammar teaching (deutsch-meister), medical Anki (nerdmedica-anki), or n-gram phrase cards (nerdmedica-german-ngram).
---

# NerdMedica DE PRO

Build Medica's German vocab deck as a real `.apkg`: one word → up to 6 notes, each in its own subdeck so she controls the daily pace of every tier separately.

## Output at a glance

```
<Parent deck>
├── 1_Core        reversible: DE → EN and EN → DE (2 cards per word)
├── 2_Production  sentence cloze
├── 3_Grammar     full declension (4 cases × sing/plur) or full conjugation
├── 4_Chunks      one collocation, whole chunk clozed
├── 5_Breadth     CEFR synonym ladder (A1 … C2) + antonym
└── 6_Family      word-family derivatives
```

Design rules, layouts and palette: `references/card-design.md`. Input format: `references/word-schema.md`. Tags and Browse queries: `references/tagging.md`.

## Setup (first run in a session)

```bash
pip install genanki --break-system-packages
cd <skill-dir>          # the folder containing this SKILL.md
```

Optional, only when audio is requested: `pip install edge-tts gTTS --break-system-packages`.

## Workflow

### Path A — Medica attaches a 14-field DE VOCAB V2 .apkg (most common)

1. See which chapters exist:
   ```bash
   python scripts/from_apkg.py --apkg <source.apkg> --list-tags
   ```
2. If she didn't say which chapter, show the list and ask. Never build every chapter unasked.
3. Extract (repeat `--filter-tag` for several chapters; order is kept):
   ```bash
   python scripts/from_apkg.py --apkg <source.apkg> \
       --filter-tag netzwerk::A1::kap05 --out /tmp/words.json
   ```
4. Build:
   ```bash
   python scripts/build_deck.py --words /tmp/words.json \
       --name "German_PRO_v3::netzwerkA1::kap05" --deck-id 2002001005 \
       --out /mnt/user-data/outputs/German_PRO_kap05.apkg
   ```

### Path B — PDF / photo / plain word list

Extract every headword yourself into `/tmp/words.json` following `references/word-schema.md` exactly, then run step 4. Rules:
- Process every word. Never skip words to save effort.
- Preserve ä ö ü ß. Never write ae/oe/ue/ss.
- Only fill declension, conjugation, synonyms, word family when certain. A missing field just skips that card; a wrong form teaches Medica a mistake.
- Wrap the target word in `<b>…</b>` inside `de_sentence` (both parts of a separable verb).

### Path C — Medica gives pre-shaped JSON

Go straight to step 4.

## Naming and IDs (keep stable — this is what makes re-imports update instead of duplicate)

| Thing | Rule | Example |
|---|---|---|
| Parent deck | `German_PRO_v3::<source>::<chapter>` | `German_PRO_v3::netzwerkA1::kap05` |
| Several chapters in one file | `…::_ALL` | `German_PRO_v3::netzwerkA1::_ALL` |
| `--deck-id` | `2002001<chapter>`, `2002001099` for _ALL | `2002001005` |
| Note-type IDs | fixed in the library — never change | 2001001001–006 |

Note GUIDs are content hashes, so the same word always maps to the same note.

## Keeping study progress (rebuilds)

Whenever Medica already studies a PRO deck and wants it rebuilt or upgraded, ask her to attach her current deck export, then add:

```bash
--preserve-progress-from /mnt/user-data/uploads/<her_current_deck>.apkg
```

The migrator matches old → new notes by content and copies each card's scheduling (queue, due, interval, ease, reps, lapses). Standard cards are matched by direction name (her old `EN → DE` progress lands on the new `EN → DE` card); cloze cards by cloze number. Cards she never saw stay new. Report the "scheduling migrated" numbers back to her.

Skip this for chapters she has never studied.

## Native recordings from the bank (preferred when the files exist)
Medica downloads real native-speaker audio (Lingua Libre / Wikimedia Commons) with `vocab_bank/work/download_audio.py`. The files are in `vocab_bank/bank_final/audio/` and listed in `vocab_bank/work/audio_manifest.json`. Attach them to the cards with:
```
--audio native            # recordings only; words without one get no audio
--audio native+edge       # recordings first, Edge TTS fills the gaps (and the example sentences)
--vocab-bank <path>       # only needed outside the repo
```
The recording goes into the word-audio field as `[sound:<file>]` and is packed into the .apkg. Example sentences have no native recordings; they only get audio with `native+edge` / `native+gtts`. If the audio folder is empty the build stops with a clear message.

## Native audio (optional — only when Medica asks)

```bash
--audio edge --voice katja --rate -10%      # Microsoft neural voices (best)
--audio gtts                                 # Google fallback (robotic)
--no-sentence-audio                          # word audio only
```

Voices: `katja` (default, female, clear), `conrad` (male), `florian` (male, most natural), `amala`, `killian`, or any full Edge voice id. Audio plays on the back of Core cards (word + sentence) and Production cards (sentence). Files are cached by content hash in `/tmp/nmdepro_audio`, so rebuilds don't re-download.

Microsoft blocks Edge TTS from cloud/datacenter IPs. In this sandbox `--audio edge` will usually report `failed`; the deck is still built without audio. When that happens, tell Medica plainly and offer either `--audio gtts`, or the same command to run on her own laptop where Edge works.

## After the build — what to tell Medica

Keep it short:
- The file (via `present_files`).
- Words, notes, per-subdeck counts, any skipped counts and input warnings (e.g. merged duplicates).
- If progress was migrated: how many cards kept their scheduling.
- Import steps, once per conversation only:
  1. Anki → File → Import → choose the .apkg.
  2. Keep "Update existing notes" and "Merge note types" enabled (Anki 2.1.55+ shows these in the import screen).
  3. Deck options per subdeck: `1_Core` new/day ≈ 15; other subdecks new/day 0 until she wants them. Bury siblings ON (new + review).

Don't explain the card types again unless asked.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/nerdmedica_de_pro.py` | Library: CSS, 6 note types, builders, `prepare_words` (validation, Unicode NFC, duplicate merging), `build_deck` |
| `scripts/build_deck.py` | CLI: words.json → .apkg; flags for progress and audio |
| `scripts/from_apkg.py` | Extract words (full declension/conjugation, CEFR ladder, word family, tags) from a 14-field .apkg; `--list-tags` |
| `scripts/progress_migrator.py` | Old-deck matching + scheduling injection |
| `scripts/audio.py` | Edge / gTTS audio with cache and retries |

## Never

- Never overwrite her existing decks or change note-type IDs.
- Never show an article or gender colour on the front of the EN → DE card or any cloze card where gender is the answer.
- Never invent German forms, synonyms or derivatives you aren't sure of.
- Never output TSV — this skill makes `.apkg` only (TSV → `nerdmedica-german-anki`).
- Never substitute ae/oe/ue/ss for umlauts and ß.
- Never ask permission to run the scripts — run them and deliver.
