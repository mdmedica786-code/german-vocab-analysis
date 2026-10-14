"""
progress_migrator.py — preserve Anki study progress across a NerdMedica DE PRO rebuild.

Strategy
--------
1. Old deck's notes are keyed by (card_type, en_meaning, de_word), computed
   from the note's model name and its fields — regardless of the guid the
   old deck happens to use (genanki-default or already-stable).
2. When we build the new deck, for any new note whose stable_guid corresponds
   to a word that also exists in the old deck under a different guid, we
   replace the new note's guid with the OLD guid.
3. After genanki writes the .apkg, we post-process its SQLite to copy the
   scheduling columns (queue, due, ivl, factor, reps, lapses, type, mod)
   from old cards to the newly generated cards, matched by note guid + template
   direction name (standard notes) or cloze number (cloze notes).

Result: fields/templates are the NEW rebuild's; scheduling is the OLD deck's
where a match existed, default (queue=0 new) otherwise.
"""
from __future__ import annotations

import os
import re
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nerdmedica_de_pro import stable_guid  # noqa


# ==============================================================
# Identify card_type from an old note's model name
# ==============================================================
_MODEL_TO_TYPE = {
    "Core":           "core",
    "Cloze Sentence": "cloze_sentence",
    "Cloze Grammar":  "cloze_grammar",
    "Cloze Usage":    "cloze_usage",
    "Expand":         "expand",
    "Word Family":    "word_family",
}
def _classify_model(model_name: str) -> str | None:
    for suffix, key in _MODEL_TO_TYPE.items():
        if suffix in model_name:
            return key
    return None


# ==============================================================
# Extract (card_type, en_meaning, de_word) from an old note's fields.
# Field layouts of our note types:
#   Core:            [EN_Meaning, POS, DE_Word, Article, GenderClass, Pron, DE_Sent, EN_Sent, Note]
#   Cloze Sentence:  [Text, Translation, Hint]
#   Cloze Grammar:   [Text, Header_EN, Header_POS, Notes]
#   Cloze Usage:     [Text, Meaning]
#   Expand:          [Text, Header_EN]
# ==============================================================

_STRIP = re.compile(r"<[^>]+>")

def _identify(card_type: str, fields: list[str]) -> tuple[str, str] | None:
    """Return (en_meaning, de_word) or None if we cannot identify."""
    if card_type == "core":
        if len(fields) < 4: return None
        en = fields[0].strip().lower()
        de = fields[2].strip().lower()   # DE_Word (no article)
        return (en, de) if en and de else None

    if card_type == "cloze_grammar":
        if len(fields) < 2: return None
        # Header_EN is either "meaning" (nouns) or "infinitive — meaning" (verbs)
        header = fields[1].strip()
        # Strip cloze markup {{cN::text}} → text  before scanning for an article
        raw = re.sub(r"\{\{c\d+::([^:}]+?)(?:::[^}]+?)?\}\}", r"\1", fields[0])
        if "—" in header:
            de_part, en_part = header.split("—", 1)
            return (en_part.strip().lower(), de_part.strip().lower())
        m = re.search(r"\b(?:der|die|das)\s+([A-ZÄÖÜ][\wäöüß]+)", raw)
        de_guess = m.group(1).lower() if m else ""
        return (header.lower(), de_guess)

    if card_type == "cloze_sentence":
        if len(fields) < 2: return None
        en = fields[1].strip().lower()
        # First cloze payload = target word
        m = re.search(r"\{\{c\d+::([^:}]+?)(?:::[^}]+?)?\}\}", fields[0])
        de = m.group(1).strip().lower() if m else ""
        # For separable verbs, cloze[0] might just be a prefix piece — drop leading/trailing punct
        de = re.sub(r"^\W+|\W+$", "", de)
        return (en, de) if en and de else None

    if card_type == "cloze_usage":
        if len(fields) < 2: return None
        en = fields[1].strip().lower()
        # Chunk cloze — we can't extract de_word cleanly (the whole chunk is clozed)
        # For matching purposes we key on en_meaning only. Set de to "" — the
        # matcher below allows this "en-only" fallback.
        return (en, "")

    if card_type == "expand":
        if len(fields) < 2: return None
        return (fields[1].strip().lower(), "")

    if card_type == "word_family":
        # Header format: "die Familie — family"  →  key by (en_lower, de_lower)
        if len(fields) < 2: return None
        header = fields[1].strip()
        if "—" in header:
            de_part, en_part = header.split("—", 1)
            # de_part may have an article: "die Familie" → strip it
            dp = de_part.strip().split()
            de_only = dp[-1].lower() if dp else ""
            return (en_part.strip().lower(), de_only)
        return (header.lower(), "")

    return None


# ==============================================================
# Load old deck: for each note, extract (card_type, en, de, guid, cards[])
# ==============================================================
def _card_slot(template_name: str | None, ord_: int):
    """Standard templates are keyed by normalized direction name; cloze by ord."""
    if template_name:
        return "t:" + re.sub(r"\s+", "", template_name).replace("->", "→").lower()
    return ord_


def _open_apkg_db(apkg_path: Path):
    tmp = tempfile.mkdtemp(prefix="nmdepro_old_")
    with zipfile.ZipFile(apkg_path) as z:
        z.extractall(tmp)
    for name in ("collection.anki21", "collection.anki2"):
        db = Path(tmp) / name
        if not db.exists(): continue
        try:
            c = sqlite3.connect(db)
            c.execute("SELECT COUNT(*) FROM notes").fetchone()
            return c, tmp
        except sqlite3.OperationalError:
            continue
    raise RuntimeError(f"No notes table in {apkg_path}")


def extract_old_index(old_apkg: Path) -> dict:
    """
    Returns:
      {
        (card_type, en_meaning, de_word_or_empty): {
            "guid":  <str>,
            "cards": {ord: {queue, due, ivl, factor, reps, lapses, type, mod}}
        }, ...
      }
    """
    import json
    c, tmpdir = _open_apkg_db(old_apkg)
    cur = c.cursor()
    # Model id → name
    models_json = cur.execute("SELECT models FROM col").fetchone()[0]
    models = json.loads(models_json)
    model_names = {int(mid): m["name"] for mid, m in models.items()}
    # Standard (non-cloze) models: map ord → template name, so a card can be
    # matched by its DIRECTION (e.g. "EN → DE") instead of its slot number.
    tmpl_names = {
        int(mid): {t["ord"]: t["name"] for t in m.get("tmpls", [])}
        for mid, m in models.items() if m.get("type", 0) == 0
    }
    note_mid = {}

    # notes: id, guid, mid, flds
    cur.execute("SELECT id, guid, mid, flds FROM notes")
    notes = cur.fetchall()
    note_mid = {nid: mid for nid, _, mid, _ in notes}

    # cards per nid
    cur.execute(
        "SELECT nid, ord, queue, due, ivl, factor, reps, lapses, type, mod FROM cards"
    )
    cards_by_nid: dict[int, dict[int, dict]] = {}
    for nid, ord_, queue, due, ivl, factor, reps, lapses, ctype, mod in cur.fetchall():
        names = tmpl_names.get(note_mid.get(nid))
        slot = _card_slot(names.get(ord_) if names else None, ord_)
        cards_by_nid.setdefault(nid, {})[slot] = {
            "queue": queue, "due": due, "ivl": ivl, "factor": factor,
            "reps": reps, "lapses": lapses, "type": ctype, "mod": mod,
        }

    index: dict = {}
    for nid, guid, mid, flds in notes:
        model_name = model_names.get(mid, "")
        card_type = _classify_model(model_name)
        if not card_type: continue
        fields = flds.split("\x1f")
        ident = _identify(card_type, fields)
        if not ident: continue
        en, de = ident
        key = (card_type, en, de)
        if key in index:
            # duplicate — keep the one with more study data
            existing = index[key]
            existing_reps = sum(v["reps"] for v in existing["cards"].values())
            new_reps = sum(v["reps"] for v in cards_by_nid.get(nid, {}).values())
            if new_reps <= existing_reps: continue
        index[key] = {"guid": guid, "cards": cards_by_nid.get(nid, {})}
    c.close()
    return index


# ==============================================================
# Build guid_overrides dict for a set of words → to pass to build_deck()
# ==============================================================
def compute_guid_overrides(words: list[dict], old_index: dict) -> dict:
    """
    Match each (word × card_type) to an old_guid via multi-strategy lookup:
      1. Exact (card_type, en_lower, de_lower)
      2. de-only  (any en, matching de_word) — best for cloze_sentence
      3. en-only  (matching en, any de) — best for usage / expand
    Returns { (card_type, stable_guid_of_new): old_guid }.
    """
    from nerdmedica_de_pro import stable_guid

    # Build alternate indices for fallback lookups
    # Each maps (type, key) → [ (guid, reps_sum), ... ]  so we can pick the most-studied
    by_type_de: dict[tuple[str, str], list[tuple[str, int]]] = {}
    by_type_en: dict[tuple[str, str], list[tuple[str, int]]] = {}
    for (ctype, en, de), val in old_index.items():
        reps = sum(v["reps"] for v in val["cards"].values())
        if de:
            by_type_de.setdefault((ctype, de), []).append((val["guid"], reps))
        if en:
            by_type_en.setdefault((ctype, en), []).append((val["guid"], reps))

    def _pick(candidates: list[tuple[str, int]]) -> str | None:
        if not candidates: return None
        # Prefer the most-studied match; ties broken by first insertion order
        return max(candidates, key=lambda x: x[1])[0]

    overrides: dict = {}
    for w in words:
        en = (w.get("en_meaning") or "").strip().lower()
        de = (w.get("de_word")   or "").strip().lower()
        for card_type in ("core", "cloze_sentence", "cloze_grammar",
                          "cloze_usage", "expand", "word_family"):
            hit = None
            # Strategy 1: full (type, en, de) match
            for candidate_key in ((card_type, en, de), (card_type, en, "")):
                if candidate_key in old_index:
                    hit = old_index[candidate_key]["guid"]; break
            # Strategy 2: de-only match (great for cloze_sentence where en is a sentence)
            if not hit and de:
                hit = _pick(by_type_de.get((card_type, de), []))
            # Strategy 3: en-only match (great for usage / expand)
            if not hit and en:
                hit = _pick(by_type_en.get((card_type, en), []))
            if hit:
                overrides[(card_type, stable_guid(w, card_type))] = hit
    return overrides


# ==============================================================
# Post-process the built .apkg to inject scheduling data
# ==============================================================
def inject_scheduling(new_apkg: Path, old_index: dict, guid_overrides: dict) -> dict:
    """
    Modifies `new_apkg` IN PLACE, rewriting card scheduling columns for cards
    whose note guid appears in the old index (via guid_overrides values).

    Returns stats dict: {'cards_migrated': int, 'notes_matched': int}
    """
    # Map old_guid → old_cards_dict for quick lookup
    guid_to_old_cards = {v["guid"]: v["cards"] for v in old_index.values()}

    tmp = tempfile.mkdtemp(prefix="nmdepro_new_")
    with zipfile.ZipFile(new_apkg) as z:
        z.extractall(tmp)

    # Find the SQLite file
    db_path = None
    for name in ("collection.anki21", "collection.anki2"):
        p = Path(tmp) / name
        if p.exists():
            try:
                sqlite3.connect(p).execute("SELECT COUNT(*) FROM notes").fetchone()
                db_path = p; break
            except sqlite3.OperationalError:
                continue
    if not db_path:
        raise RuntimeError("Could not locate SQLite DB in the built .apkg")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    import json as _json
    new_models = _json.loads(cur.execute("SELECT models FROM col").fetchone()[0])
    new_tmpls = {
        int(mid): {t["ord"]: t["name"] for t in m.get("tmpls", [])}
        for mid, m in new_models.items() if m.get("type", 0) == 0
    }
    cur.execute("SELECT id, guid, mid FROM notes")
    notes = cur.fetchall()

    notes_matched = 0
    cards_migrated = 0
    for nid, guid, mid in notes:
        old_cards = guid_to_old_cards.get(guid)
        if not old_cards: continue
        notes_matched += 1
        # For each card on this note, look up old scheduling by ord
        cur.execute("SELECT id, ord FROM cards WHERE nid = ?", (nid,))
        for cid, ord_ in cur.fetchall():
            names = new_tmpls.get(mid)
            old = old_cards.get(_card_slot(names.get(ord_) if names else None, ord_))
            if not old: continue
            cur.execute(
                "UPDATE cards SET queue=?, due=?, ivl=?, factor=?, reps=?, lapses=?, type=?, mod=? "
                "WHERE id = ?",
                (old["queue"], old["due"], old["ivl"], old["factor"],
                 old["reps"], old["lapses"], old["type"], old["mod"], cid),
            )
            cards_migrated += 1
    conn.commit()
    conn.close()

    # Rezip in place
    tmp_zip = str(new_apkg) + ".tmp"
    with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp):
            for fn in files:
                full = Path(root) / fn
                z.write(full, full.relative_to(tmp))
    os.replace(tmp_zip, new_apkg)

    return {"cards_migrated": cards_migrated, "notes_matched": notes_matched}
