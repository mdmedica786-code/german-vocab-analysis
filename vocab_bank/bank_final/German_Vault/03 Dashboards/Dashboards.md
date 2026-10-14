---
title: "Dashboards"
type: "dashboard"
tags: ["guide", "dashboard"]
---
<!-- bank:start -->
# Dashboards

Two ways to get tables. Bases is built in; Dataview is a community plugin.

## Bases (no plugin)

- [[Vocabulary.base]] - views: all words, to learn, learning, B2 bank, medical, skipped
- [[Phrases and Redemittel.base]] - sets with counts and levels

## Dataview (plugin needed)

Words you are learning right now:

```dataview
TABLE level, topic, meaning
FROM #vocab
WHERE status = "learning"
SORT level ASC
```

How many words per level and status:

```dataview
TABLE length(rows) AS Words
FROM #vocab
WHERE !skip
GROUP BY level + " / " + status
SORT rows.file.name ASC
```

B2 words for writing tasks:

```dataview
TABLE pos, topic
FROM #exam/Schreiben
WHERE status != "known"
SORT file.name ASC
LIMIT 50
```

Words to review today or earlier (when you fill `next_review`):

```dataview
LIST
FROM #vocab
WHERE next_review AND next_review <= date(today)
```
<!-- bank:end -->

## My notes

