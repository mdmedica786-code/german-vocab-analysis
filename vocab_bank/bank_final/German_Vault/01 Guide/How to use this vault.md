---
title: "How to use this vault"
type: "guide"
tags: ["guide"]
---
<!-- bank:start -->
# How to use this vault

This vault is generated from the CSV banks in `bank_final/`. Open the folder `bank_final/German_Vault` in Obsidian ("Open folder as vault").

## What is where

| Folder | Content |
|---|---|
| `00 Home` | Entry point with counts and links |
| `01 Guide` | These help notes |
| `02 MOCs` | Maps of content: one per topic (T01-T16, M1-M4), phrases, Redemittel, medical |
| `03 Dashboards` | Dataview queries and `.base` files (tables you can filter and edit) |
| `10 Vocabulary` | Main bank, one note per word, sorted by topic |
| `20 B2 Vocabulary` | B2 bank, one note per word, sorted by topic |
| `30 Phrases` | 1,016 phrases grouped by function (agree, give reasons, ...) |
| `40 Redemittel` | 1,176 speaking and writing expressions, one note per category |
| `90 Templates` | Template for your own new word notes |

## Everyday use

1. Press `Ctrl/Cmd+O` and type a word, a plural or a verb form (aliases are included), for example `Prüfungen` or `hat abgelegt`.
2. In your own notes write `[[Prüfung]]` to link to the word. Hover to preview, or open the backlinks pane to see where you used it.
3. Change the property `status` to `learning` or `known` while you study. The dashboards use it.
4. Write your own text under `## My notes` in a word note. It is kept when the vault is rebuilt.
5. Use the graph view filtered by `tag:#level/B2` or `path:"20 B2 Vocabulary"` to see clusters.

## Rebuilding after the banks change

Run `python3 work/make_vault.py` in the `vocab_bank` folder. It rewrites only the generated block of each note.
Your text below the block, your `status`, `next_review`, `last_review` and `mnemonic` values and the tags you added yourself are kept.

## Plugins

Nothing is needed to read the notes. For tables and counts, use the built-in **Bases** (Obsidian 1.9 or newer): open the `.base` files in `03 Dashboards`.
The **Dataview** queries in [[Dashboards]] need the community plugin Dataview.
<!-- bank:end -->

## My notes

