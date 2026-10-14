#!/usr/bin/env python3
"""make_vault.py - builds the Obsidian vault `German_Vault/` from the CSV banks in bank_final/.

  python3 work/make_vault.py            build / refresh the vault
  python3 work/make_vault.py --check    build into a temp folder and run the consistency checks only

One note per word (main bank + B2 bank), one note per phrase group, one note per Redemittel category,
plus topic MOCs, a Home note, guides, templates and Bases dashboards.

Safe to run again: each word note has a generated block between <!-- bank:start --> and <!-- bank:end -->.
Only that block and the managed properties are rewritten. Your own text below the block, your `status`,
`next_review`, `last_review`, `mnemonic` properties and any extra tags you added are kept.
Nothing is ever deleted; notes that no longer exist in the CSV files are only reported.
"""
import csv, json, re, sys, shutil, tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_util import AUDIO_DIR, EXTS, AudioLookup  # noqa: E402
from studylist import mark_not_in_list  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BANKS = ROOT / "bank_final"
VAULT = BANKS / "German_Vault"

LEVELS = ["A1", "A2", "B1", "B2", "C1"]
START, END = "<!-- bank:start -->", "<!-- bank:end -->"
USER_KEYS = ["status", "next_review", "last_review", "mnemonic"]
MANAGED_TAG_PREFIX = ("vocab", "level/", "topic/", "pos/", "bank/", "exam/", "medical", "skipped", "phrase", "redemittel", "moc")
NO_LINK_POS = {"preposition", "determiner", "pronoun", "conjunction", "particle", "numeral", "affix", "interjection", "adverb"}

D_VOCAB, D_B2, D_PHR, D_RED = "10 Words by level", "20 B2 extra words", "30 Phrases", "40 Redemittel"
OLD_VOCAB, OLD_B2 = "10 Vocabulary", "20 B2 Vocabulary"  # earlier layout, migrated automatically
D_MOC, D_GUIDE, D_TPL, D_DASH = "02 MOCs", "01 Guide", "90 Templates", "03 Dashboards"
D_AUDIO = "95 Audio"  # native audio copied here when bank_final/audio exists (see download_audio.py)


# ---------------------------------------------------------------- helpers
def read_csv(name):
    with open(BANKS / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe(name):
    s = name.replace(":", " -").replace("/", "-")
    s = re.sub(r'[\\*?"<>|#^\[\]]', "", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    return s or "unnamed"


def y(v):
    """YAML scalar / flow list written as JSON (valid YAML)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(y(x) for x in v) + "]"
    return json.dumps(str(v), ensure_ascii=False)


def split_note(text):
    """-> (frontmatter lines dict key->list of raw lines, body)"""
    if not text.startswith("---\n"):
        return {}, text
    i = text.find("\n---\n", 4)
    if i < 0:
        return {}, text
    fm, body = text[4:i], text[i + 5:]
    d, key = {}, None
    for ln in fm.split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):(.*)$", ln)
        if m:
            key = m.group(1)
            d[key] = [ln]
        elif key is not None:
            d[key].append(ln)
    return d, body


def parse_list(lines):
    """items of a YAML list given as flow ([a, b]) or block (- a)"""
    first = lines[0].split(":", 1)[1].strip()
    items = []
    if first.startswith("["):
        try:
            items = json.loads(first)
        except Exception:
            items = [x.strip().strip('"\'') for x in first.strip("[]").split(",") if x.strip()]
    else:
        for ln in lines[1:]:
            m = re.match(r"^\s*-\s*(.*)$", ln)
            if m:
                items.append(m.group(1).strip().strip('"\''))
    return [str(x) for x in items if str(x)]


def user_tags(lines):
    return [t for t in parse_list(lines) if not t.startswith(MANAGED_TAG_PREFIX)]


class Vault:
    def __init__(self, root):
        self.root = Path(root)
        self.written = set()
        self.stats = Counter()

    def put(self, rel, fm, body, preserve=True, old_rel=None):
        """fm: ordered list of (key, value) ; body: generated body (string, no trailing marker handling)"""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if old_rel and not path.exists() and (self.root / old_rel).exists():
            (self.root / old_rel).rename(path)  # keep the user's edits when the folder layout changes
            self.stats["moved"] += 1
        old_fm, old_user = {}, ""
        if preserve and path.exists():
            old = path.read_text(encoding="utf-8")
            old_fm, old_body = split_note(old)
            j = old_body.find(END)
            if j >= 0:
                old_user = old_body[j + len(END) + 1:]
        fm = [(k, v) for k, v in fm if not (v == "" or v == [])]
        keys = [k for k, _ in fm]
        # keep user properties
        for k in USER_KEYS:
            if k in old_fm:
                raw = old_fm[k]
                fm = [(kk, vv) for kk, vv in fm if kk != k] + [(k, ("__raw__", raw))]
        if "tags" in old_fm and "tags" in keys:
            extra = user_tags(old_fm["tags"])
            if extra:
                fm = [(k, (v + [t for t in extra if t not in v]) if k == "tags" else v) for k, v in fm]
        out = ["---"]
        for k, v in fm:
            if isinstance(v, tuple) and v and v[0] == "__raw__":
                out.extend(v[1])
            else:
                out.append(f"{k}: {y(v)}")
        out.append("---")
        text = "\n".join(out) + "\n" + START + "\n" + body.rstrip("\n") + "\n" + END + "\n"
        text += ("\n" + old_user.lstrip("\n")) if old_user.strip() else "\n## My notes\n\n"
        if not (path.exists() and path.read_text(encoding="utf-8") == text):
            path.write_text(text, encoding="utf-8")
            self.stats["written"] += 1
        else:
            self.stats["unchanged"] += 1
        self.written.add(path)

    def copy_file(self, src, rel):
        """Copy a binary file (audio) into the vault if it is missing or changed."""
        dst = self.root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_size != Path(src).stat().st_size:
            shutil.copy2(src, dst)
            self.stats["audio copied"] += 1
        self.written.add(dst)

    def put_plain(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not (path.exists() and path.read_text(encoding="utf-8") == text):
            path.write_text(text, encoding="utf-8")
            self.stats["written"] += 1
        else:
            self.stats["unchanged"] += 1
        self.written.add(path)


def topic_code(t):
    return t.split(" ", 1)[0] if t else ""


def lvl_key(l):
    return LEVELS.index(l) if l in LEVELS else 9


# ---------------------------------------------------------------- build
def build(root, copy_audio=True):
    V = Vault(root)
    audio = AudioLookup()
    main = mark_not_in_list(read_csv("vocabulary_bank.csv"))
    b2 = read_csv("b2_vocabulary_bank.csv")
    phr = read_csv("phrase_bank.csv")
    red = read_csv("redemittel_bank.csv")

    # ---- registry of word notes (case-insensitive unique file names)
    entries = []
    for r in main:
        entries.append(dict(bank="main", r=r, lemma=r["lemma"], pos=r["pos"]))
    for r in b2:
        entries.append(dict(bank="b2", r=r, lemma=r["lemma"], pos=r["pos"]))
    order = sorted(range(len(entries)), key=lambda i: (0 if entries[i]["pos"] == "noun" else 1, 0 if entries[i]["bank"] == "main" else 1, i))
    used, lemma_map = {}, {}
    for i in order:
        e = entries[i]
        base = safe(e["lemma"])
        name = base
        if name.lower() in used:
            name = f"{base} ({e['pos']})"
        if name.lower() in used:
            name = f"{base} ({e['pos']}, {e['r']['id']})"
        used[name.lower()] = i
        e["fname"] = name
        lemma_map.setdefault(e["lemma"], i)
    topics = {}
    for e in entries:
        t = e["r"]["topic"]
        topics[topic_code(t)] = t
    topic_files = {c: safe(t) for c, t in topics.items()}

    def link(i, text=None):
        e = entries[i]
        if text is None or text == e["fname"]:
            return f"[[{e['fname']}]]"
        return f"[[{e['fname']}|{text}]]"

    def related(e):
        cols = [c.strip() for c in e["r"].get("collocations", "").split("|") if c.strip()]
        found, seen = [], {e["lemma"]}
        for c in cols:
            for tok in re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß-]+", c):
                if tok in seen or len(tok) < 4:
                    continue
                j = lemma_map.get(tok)
                if j is None:
                    continue
                t = entries[j]
                if t["pos"] in NO_LINK_POS or (t["pos"] == "verb" and t["r"]["level"] in ("A1", "A2")) or tok in ("haben", "sein", "werden"):
                    continue
                seen.add(tok)
                found.append(j)
        return found[:6]

    for e in entries:
        r, pos, bank = e["r"], e["pos"], e["bank"]
        art, plural = (r.get("article") or "").strip(), (r.get("plural") or "").strip()
        lemma = e["lemma"]
        topic_c = topic_code(r["topic"])
        exam = [x.strip() for x in (r.get("exam_use") or "").split(";") if x.strip()]
        skipped = bool(r.get("skip"))
        aliases = []
        if pos == "noun":
            for a in art.split("/"):
                if a in ("der", "die", "das"):
                    aliases.append(f"{a} {lemma}")
            if plural and plural not in ("–", "-", lemma):
                aliases.append(plural)
        elif pos == "verb":
            aliases += [x for x in (r.get("pres_3sg"), r.get("preterite"), r.get("perfect")) if x]
        aliases = [a for a in dict.fromkeys(aliases) if a.lower() != e["fname"].lower()]
        tags = ["vocab", f"bank/{bank}", f"level/{r['level']}", f"topic/{topic_c}", f"pos/{pos}"]
        tags += [f"exam/{x}" for x in exam]
        if r.get("medical") or topic_c.startswith("M"):
            tags.append("medical")
        if skipped:
            tags.append("skipped")
        fm = [("title", lemma), ("type", "word"), ("aliases", aliases), ("lemma", lemma), ("meaning", r["meaning_en"]), ("pos", pos)]
        if pos == "noun":
            fm += [("article", art), ("plural", plural)]
        fm += [("level", r["level"]), ("topic", f"[[{topic_files[topic_c]}]]"), ("register", r.get("register", "")),
               ("bank", bank), ("id", r["id"])]
        if exam:
            fm.append(("exam_use", exam))
        if bank == "main":
            if r.get("goethe_level"):
                fm.append(("goethe_level", r["goethe_level"]))
            if r.get("nw_ref"):
                fm.append(("netzwerk", r["nw_ref"]))
            if r.get("freq_rank", "").isdigit():
                fm.append(("freq_rank", int(r["freq_rank"])))
        fm += [("skip", skipped)]
        if skipped:
            fm.append(("skip_reason", r.get("skip_reason", "")))
        if r.get("check"):
            fm.append(("check", r["check"]))
        afile = audio.get(lemma)
        if afile:
            fm.append(("audio", afile))
        fm += [("status", "new"), ("tags", tags)]

        # ---- body
        head = f"{art} {lemma}" if (pos == "noun" and art in ("der", "die", "das")) else lemma
        b = [f"# {head}", ""]
        if afile:
            b += [f"![[{afile}]]", ""]
            if copy_audio:
                V.copy_file(AUDIO_DIR / afile, f"{D_AUDIO}/{afile}")
        b.append(f"**Meaning:** {r['meaning_en']}")
        if r.get("other_senses"):
            b.append(f"**Other senses:** {r['other_senses']}")
        if pos == "noun" and plural:
            b.append(f"**Plural:** {plural}")
        if pos == "verb":
            forms = " · ".join(x for x in (r.get("pres_3sg"), r.get("preterite"), r.get("perfect")) if x)
            if forms:
                b.append(f"**Forms:** {forms}")
            extras = []
            if r.get("reflexive"):
                extras.append("reflexive")
            if r.get("sep_prefix"):
                extras.append(f"separable ({r['sep_prefix']}-)")
            if r.get("gov"):
                extras.append(f"+ {r['gov']}" if not r["gov"].startswith("+") else r["gov"])
            if extras:
                b.append("**Grammar:** " + " · ".join(extras))
        elif r.get("extra_forms"):
            b.append(f"**Forms:** {r['extra_forms']}")
        if pos == "preposition" and r.get("gov"):
            b.append(f"**Case:** {r['gov']}")
        b.append(f"**Level:** {r['level']} · **Topic:** [[{topic_files[topic_c]}]] · **Register:** {r.get('register', '')}")
        if r.get("note"):
            b.append(f"**Note:** {r['note']}")
        if skipped:
            b += ["", "> [!info] Not in the study list", f"> {r.get('skip_reason', '')}"]
        if r.get("check"):
            b += ["", "> [!warning] Check", f"> {r['check']}"]
        if r.get("example_de"):
            b += ["", "> [!example] Beispiel", f"> {r['example_de']}", f"> *{r['example_en']}*"]
        cols = [c.strip() for c in r.get("collocations", "").split("|") if c.strip()]
        if cols:
            b += ["", "**Collocations**"] + [f"- {c}" for c in cols]
        rel = related(e)
        if rel:
            b += ["", "**Related:** " + " · ".join(link(j, entries[j]["lemma"]) for j in rel)]
        if exam:
            b += ["", "**Exam use:** " + ", ".join(exam)]
        if bank == "main" and (r.get("nw_ref") or r.get("goethe_level")):
            ref = []
            if r.get("nw_ref"):
                ref.append(f"Netzwerk neu {r['nw_ref']}" + (f" ({r['nw_chapter']})" if r.get("nw_chapter") else ""))
            if r.get("goethe_level"):
                ref.append(f"Goethe word list {r['goethe_level']}")
            b += ["", "**Source:** " + " · ".join(ref)]
        if bank == "b2":
            V.put(f"{D_B2}/{topic_files[topic_c]}/{e['fname']}.md", fm, "\n".join(b),
                  old_rel=f"{OLD_B2}/{topic_files[topic_c]}/{e['fname']}.md")
        else:
            V.put(f"{D_VOCAB}/{r['level']}/{topic_files[topic_c]}/{e['fname']}.md", fm, "\n".join(b),
                  old_rel=f"{OLD_VOCAB}/{topic_files[topic_c]}/{e['fname']}.md")

    # ---- topic MOCs
    by_topic = defaultdict(lambda: defaultdict(list))
    for i, e in enumerate(entries):
        by_topic[topic_code(e["r"]["topic"])][e["bank"]].append(i)
    for c in sorted(by_topic):
        t = topics[c]
        n_main, n_b2 = len(by_topic[c]["main"]), len(by_topic[c]["b2"])
        body = [f"# {t}", "", f"Map of content. {n_main} words in the main bank, {n_b2} in the B2 bank.", "",
                "Back to [[00 Home]]", ""]
        for bank, title in (("main", "Main bank"), ("b2", "B2 bank")):
            idx = by_topic[c][bank]
            if not idx:
                continue
            body += [f"## {title}", ""]
            for lv in LEVELS:
                sel = [i for i in idx if entries[i]["r"]["level"] == lv]
                if not sel:
                    continue
                body += [f"### {lv} ({len(sel)})", ""]
                for i in sorted(sel, key=lambda k: entries[k]["lemma"].lower()):
                    r = entries[i]["r"]
                    body.append(f"- {link(i)} — {r['meaning_en']}")
                body.append("")
        V.put(f"{D_MOC}/Topics/{topic_files[c]}.md",
              [("title", t), ("type", "moc"), ("tags", ["moc", f"topic/{c}"])], "\n".join(body))

    # ---- level MOCs
    for lv in LEVELS:
        idx = [i for i, e in enumerate(entries) if e["r"]["level"] == lv and not e["r"].get("skip")]
        n_main = sum(1 for i in idx if entries[i]["bank"] == "main")
        body = [f"# Level {lv}", "", f"{len(idx)} words to study: {n_main} from the main bank" +
                (f" and {len(idx) - n_main} from the B2 extra bank." if lv == "B2" else "."),
                "", "Back to [[00 Home]]", ""]
        for c in sorted(topics):
            sel = [i for i in idx if topic_code(entries[i]["r"]["topic"]) == c]
            if not sel:
                continue
            body += [f"## {topics[c]} ({len(sel)})", ""]
            for i in sorted(sel, key=lambda k: entries[k]["lemma"].lower()):
                body.append(f"- {link(i)} — {entries[i]['r']['meaning_en']}")
            body.append("")
        V.put(f"{D_MOC}/Levels/Level {lv}.md", [("title", f"Level {lv}"), ("type", "moc"), ("tags", ["moc", f"level/{lv}"])], "\n".join(body))

    # ---- medical MOC
    med = [i for i, e in enumerate(entries) if e["r"].get("medical") or topic_code(e["r"]["topic"]).startswith("M")]
    body = ["# MOC Medical vocabulary", "", f"{len(med)} words from the main bank that are tagged medical (core or related).", "", "Back to [[00 Home]]", ""]
    for c in sorted({topic_code(entries[i]["r"]["topic"]) for i in med}):
        sel = [i for i in med if topic_code(entries[i]["r"]["topic"]) == c]
        body += [f"## {topics[c]} ({len(sel)})", ""]
        for i in sorted(sel, key=lambda k: entries[k]["lemma"].lower()):
            body.append(f"- {link(i)} — {entries[i]['r']['meaning_en']}")
        body.append("")
    V.put(f"{D_MOC}/MOC Medical vocabulary.md", [("title", "MOC Medical vocabulary"), ("type", "moc"), ("tags", ["moc", "medical"])], "\n".join(body))

    # ---- phrases (grouped by function)
    groups = defaultdict(list)
    for r in phr:
        groups[r["function"]].append(r)
    phr_files = {}
    for fn in sorted(groups, key=lambda k: -len(groups[k])):
        name = safe(fn)
        phr_files[fn] = name
        rows = sorted(groups[fn], key=lambda r: (lvl_key(r["level"]), r["phrase_de"].lower()))
        lv = Counter(r["level"] for r in rows)
        fm = [("title", fn), ("type", "phrase-group"), ("count", len(rows)),
              ("levels", [f"{l} ({lv[l]})" for l in LEVELS if lv[l]]), ("tags", ["phrase", "moc"])]
        b = [f"# {fn}", "", f"{len(rows)} phrases. Back to [[MOC Phrases]]", ""]
        cur = None
        for r in rows:
            if r["level"] != cur:
                cur = r["level"]
                b += [f"## {cur}", ""]
            b.append(f"- **{r['phrase_de']}** — {r['meaning_en']}")
            if r.get("example_de"):
                b.append(f"  - {r['example_de']} *({r['example_en']})*")
            if r.get("grammar_note"):
                b.append(f"  - Grammar: {r['grammar_note']}")
            if r.get("variants"):
                b.append(f"  - Variants: {r['variants']}")
            if r.get("exam_use"):
                b.append(f"  - Exam: {r['exam_use']}")
        V.put(f"{D_PHR}/{name}.md", fm, "\n".join(b))
    body = ["# MOC Phrases", "", f"{len(phr)} useful phrases grouped by function. Back to [[00 Home]]", ""]
    for fn in sorted(groups, key=lambda k: -len(groups[k])):
        body.append(f"- [[{phr_files[fn]}]] ({len(groups[fn])})")
    V.put(f"{D_MOC}/MOC Phrases.md", [("title", "MOC Phrases"), ("type", "moc"), ("tags", ["moc", "phrase"])], "\n".join(body))

    # ---- Redemittel (grouped by category)
    cats = {}
    for r in red:
        cats.setdefault(r["cat_id"], []).append(r)
    red_files = {}
    for cid in sorted(cats):
        rows = cats[cid]
        cname = rows[0]["category"]
        name = safe(f"{cid} {cname}")
        red_files[cid] = (name, len(rows), cname)
        lv = sorted({r["level"] for r in rows}, key=lvl_key)
        med_cat = any(r["speaker"] in ("Arzt", "Patient", "Pflege") for r in rows)
        fm = [("title", f"{cid} {cname}"), ("type", "redemittel-set"), ("cat_id", cid), ("count", len(rows)), ("levels", lv),
              ("tags", ["redemittel"] + [f"level/{l}" for l in lv] + (["medical"] if med_cat else []))]
        b = [f"# {cid} {cname}", "", f"{len(rows)} expressions. Back to [[MOC Redemittel]]", ""]
        fcur = None
        for r in rows:
            if r["function"] != fcur:
                fcur = r["function"]
                b += [f"## {fcur}", ""]
            tag = " ⭐" if r.get("priority") == "core" else ""
            b.append(f"- **{r['redemittel_de']}**{tag} — {r['meaning_en']}")
            b.append(f"  - {r['example_de']} *({r['example_en']})*")
            meta = [f"{r['level']}", r["register"], f"speaker: {r['speaker']}", f"to: {r['audience']}"]
            b.append("  - " + " · ".join(m for m in meta if m))
            if r.get("grammar_note"):
                b.append(f"  - Grammar: {r['grammar_note']}")
            if r.get("variants"):
                b.append(f"  - Variants: {r['variants']}")
            if r.get("exam_use"):
                b.append(f"  - Exam: {r['exam_use']}")
        V.put(f"{D_RED}/{name}.md", fm, "\n".join(b))
    body = ["# MOC Redemittel", "", f"{len(red)} speaking and writing expressions in {len(cats)} sets (⭐ = core). Back to [[00 Home]]", ""]
    for cid in sorted(cats):
        name, n, cname = red_files[cid]
        body.append(f"- [[{name}]] ({n})")
    V.put(f"{D_MOC}/MOC Redemittel.md", [("title", "MOC Redemittel"), ("type", "moc"), ("tags", ["moc", "redemittel"])], "\n".join(body))

    # ---- Home
    lv_main = Counter(e["r"]["level"] for e in entries if e["bank"] == "main")
    n_skip = sum(1 for e in entries if e["r"].get("skip"))
    body = ["# German vocabulary vault", "",
            f"- Main vocabulary: **{len(main)}** notes ({len(main) - n_skip} to study, {n_skip} marked as skipped)",
            f"- B2 vocabulary: **{len(b2)}** notes (new words, no medical)",
            f"- Phrases: **{len(phr)}** in {len(groups)} groups",
            f"- Redemittel: **{len(red)}** in {len(cats)} sets", "",
            "## Start here", "",
            "- [[How to use this vault]]", "- [[Properties and tags]]", "- [[Dashboards]]", "",
            "## Words by level", "",
            " · ".join(f"[[Level {l}]] ({sum(1 for e in entries if e['r']['level'] == l and not e['r'].get('skip'))})" for l in LEVELS), "",
            "## Maps", "",
            "- [[MOC Phrases]] · [[MOC Redemittel]] · [[MOC Medical vocabulary]]", "", "### Topics", ""]
    for c in sorted(topics):
        n = len(by_topic[c]["main"]) + len(by_topic[c]["b2"])
        body.append(f"- [[{topic_files[c]}]] ({n})")
    V.put("00 Home.md", [("title", "Home"), ("type", "moc"), ("tags", ["moc"])], "\n".join(body), preserve=True)

    # ---- guides
    V.put(f"{D_GUIDE}/How to use this vault.md", [("title", "How to use this vault"), ("type", "guide"), ("tags", ["guide"])], GUIDE_USE)
    V.put(f"{D_GUIDE}/Properties and tags.md", [("title", "Properties and tags"), ("type", "guide"), ("tags", ["guide"])], GUIDE_PROPS)
    V.put(f"{D_DASH}/Dashboards.md", [("title", "Dashboards"), ("type", "dashboard"), ("tags", ["guide", "dashboard"])], DASH)
    V.put_plain(f"{D_DASH}/Vocabulary.base", BASE_VOCAB)
    V.put_plain(f"{D_DASH}/Phrases and Redemittel.base", BASE_PHR)
    V.put_plain(f"{D_TPL}/New word.md", TPL_WORD)
    V.put_plain(".obsidian/app.json", json.dumps({"alwaysUpdateLinks": True, "useMarkdownLinks": False, "newLinkFormat": "shortest",
                                                    "showUnsupportedFiles": False, "propertiesInDocument": "visible"}, indent=2) + "\n")
    return V, entries


GUIDE_USE = """# How to use this vault

This vault is generated from the CSV banks in `bank_final/`. Open the folder `bank_final/German_Vault` in Obsidian ("Open folder as vault").

## What is where

| Folder | Content |
|---|---|
| `00 Home` | Entry point with counts and links |
| `01 Guide` | These help notes |
| `02 MOCs` | Maps of content: one per level (A1 to C1), one per topic (T01-T16, M1-M4), phrases, Redemittel, medical |
| `03 Dashboards` | Dataview queries and `.base` files (tables you can filter and edit) |
| `10 Words by level` | Main bank, one note per word, in folders A1, A2, B1, B2, C1 and then by topic |
| `20 B2 extra words` | the extra B2 words (no medical, more than 3,600), sorted by topic |
| `30 Phrases` | 1,016 phrases grouped by function (agree, give reasons, ...) |
| `40 Redemittel` | 1,176 speaking and writing expressions, one note per category |
| `90 Templates` | Template for your own new word notes |

## Everyday use

1. Press `Ctrl/Cmd+O` and type a word, a plural or a verb form (aliases are included), for example `Prüfungen` or `hat abgelegt`.
2. In your own notes write `[[Prüfung]]` to link to the word. Hover to preview, or open the backlinks pane to see where you used it.
3. Change the property `status` to `learning` or `known` while you study. The dashboards use it.
4. Write your own text under `## My notes` in a word note. It is kept when the vault is rebuilt.
5. Use the graph view filtered by `tag:#level/B2` or `path:"20 B2 extra words"` to see clusters.

## Rebuilding after the banks change

Run `python3 work/make_vault.py` in the `vocab_bank` folder. It rewrites only the generated block of each note.
Your text below the block, your `status`, `next_review`, `last_review` and `mnemonic` values and the tags you added yourself are kept.

## Plugins

Nothing is needed to read the notes. For tables and counts, use the built-in **Bases** (Obsidian 1.9 or newer): open the `.base` files in `03 Dashboards`.
The **Dataview** queries in [[Dashboards]] need the community plugin Dataview.
"""

GUIDE_PROPS = """# Properties and tags

## Word notes

| Property | Meaning |
|---|---|
| `lemma`, `pos` | dictionary form and part of speech (noun, verb, adjective, adverb, phrase, ...) |
| `article`, `plural` | nouns only |
| `level` | A1, A2, B1, B2, C1 |
| `topic` | link to the topic map, T01-T16 (M1-M4 are medical) |
| `register` | neutral, formal, informal, colloquial, technical, regional |
| `bank` | `main` or `b2` |
| `id` | row id in the CSV (B... main bank, D... B2 bank) |
| `exam_use` | B2 bank only: Lesen, Hören, Schreiben, Sprechen, Alltag, Grammatik, Medien, Wissenschaft |
| `goethe_level`, `netzwerk`, `freq_rank` | main bank only: Goethe list level, Netzwerk neu chapter, frequency rank |
| `skip`, `skip_reason` | `true` for words that are not in the study list (for example country names) |
| `check` | a note when a fact should be double-checked |
| `status` | **yours**: `new`, `learning`, `known` |
| `next_review`, `last_review`, `mnemonic` | **yours**, optional |

## Tags

`#vocab`, `#bank/main`, `#bank/b2`, `#level/B2`, `#topic/T04`, `#pos/noun`, `#exam/Schreiben`, `#medical`, `#skipped`, `#phrase`, `#redemittel`, `#moc`.
Add your own tags freely (for example `#hard` or `#exam-week`); they are kept when the vault is rebuilt.
"""

DASH = """# Dashboards

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
"""

BASE_VOCAB = """filters:
  and:
    - file.hasTag("vocab")
properties:
  level:
    displayName: Level
  pos:
    displayName: Part of speech
  status:
    displayName: Status
views:
  - type: table
    name: To learn (not skipped)
    filters:
      and:
        - skip == false
    order:
      - file.name
      - pos
      - level
      - topic
      - status
    sort:
      - property: level
        direction: ASC
  - type: table
    name: Learning
    filters:
      and:
        - 'status == "learning"'
    order:
      - file.name
      - level
      - topic
      - status
  - type: table
    name: B2 bank
    filters:
      and:
        - 'bank == "b2"'
    order:
      - file.name
      - pos
      - topic
      - exam_use
      - status
  - type: table
    name: Medical
    filters:
      and:
        - file.hasTag("medical")
    order:
      - file.name
      - level
      - topic
      - status
  - type: table
    name: Skipped
    filters:
      and:
        - skip == true
    order:
      - file.name
      - skip_reason
"""

BASE_PHR = """filters:
  or:
    - file.hasTag("phrase")
    - file.hasTag("redemittel")
properties:
  count:
    displayName: Items
views:
  - type: table
    name: Phrase groups
    filters:
      and:
        - 'type == "phrase-group"'
    order:
      - file.name
      - count
      - levels
  - type: table
    name: Redemittel sets
    filters:
      and:
        - 'type == "redemittel-set"'
    order:
      - file.name
      - count
      - levels
"""

TPL_WORD = """---
lemma:
pos:
level:
topic:
status: new
tags: [vocab, mine]
---
# {{title}}

**Meaning:**

> [!example] Beispiel
>

**Collocations**
-

## My notes

"""


# ---------------------------------------------------------------- checks
def check(vault_root):
    root = Path(vault_root)
    notes = [p for p in root.rglob("*.md")]
    names = defaultdict(list)
    for p in notes:
        names[p.stem.lower()].append(p)
    dup = {k: v for k, v in names.items() if len(v) > 1}
    stems = {p.stem for p in notes} | {p.name for p in root.rglob("*.base")} | {p.name for p in root.rglob("*") if p.suffix.lower() in EXTS}
    stems |= {p.name for p in AUDIO_DIR.glob("*")} if AUDIO_DIR.is_dir() else set()  # audio embeds ![[word.wav]]
    broken, bad_yaml = [], []
    try:
        import yaml
    except Exception:
        yaml = None
    link_re = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
    for p in notes:
        t = p.read_text(encoding="utf-8")
        fm, body = split_note(t)
        if yaml and t.startswith("---\n"):
            try:
                yaml.safe_load(t[4:t.find("\n---\n", 4)])
            except Exception as ex:
                bad_yaml.append((p.name, str(ex)[:80]))
        for m in link_re.finditer(t):
            if m.group(1).strip() not in stems:
                broken.append((p.name, m.group(1)))
    print(f"notes: {len(notes)}  case-insensitive duplicate names: {len(dup)}  broken links: {len(broken)}  bad yaml: {len(bad_yaml)}")
    for x in list(dup.items())[:5]:
        print("  dup", x)
    for x in broken[:10]:
        print("  broken", x)
    for x in bad_yaml[:5]:
        print("  yaml", x)
    return not dup and not broken and not bad_yaml


if __name__ == "__main__":
    if "--check" in sys.argv:
        tmp = Path(tempfile.mkdtemp())
        V, _ = build(tmp, copy_audio=False)  # no audio copies in the temp check build
        ok = check(tmp)
        shutil.rmtree(tmp)
        sys.exit(0 if ok else 1)
    V, entries = build(VAULT)
    for d in (OLD_VOCAB, OLD_B2):  # remove only EMPTY folders left over from the earlier layout
        for sub in sorted((VAULT / d).rglob("*"), reverse=True) if (VAULT / d).exists() else []:
            if sub.is_dir() and not any(sub.iterdir()):
                sub.rmdir()
        if (VAULT / d).exists() and not any((VAULT / d).iterdir()):
            (VAULT / d).rmdir()
    print("moved", V.stats["moved"], "written", V.stats["written"], "unchanged", V.stats["unchanged"])
    existing = {p for p in VAULT.rglob("*") if p.is_file()}
    extra = sorted(str(p.relative_to(VAULT)) for p in existing - V.written)
    if extra:
        print(f"{len(extra)} files in the vault are not generated (kept):", extra[:5])
    ok = check(VAULT)
    sys.exit(0 if ok else 1)
