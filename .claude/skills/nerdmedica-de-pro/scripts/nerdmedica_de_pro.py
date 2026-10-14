"""
NerdMedica DE PRO — core library.

Turns a list of word dicts into a 5-card-type Anki deck (.apkg).

Public API
----------
    build_deck(words, deck_name, deck_id, out_path) -> dict of counts

Each `word` in `words` is a dict following references/word-schema.md.
Missing optional fields cause specific card types to be gracefully skipped,
not errored — see per-builder rules below.
"""
from __future__ import annotations
import hashlib
import re
import unicodedata
from typing import Any


# ==============================================================
# STABLE GUIDS  —  deterministic hash of (card_type, de_word, en_meaning).
# Ensures re-imports UPDATE the same notes → progress preserved.
# ==============================================================
def stable_guid(word: dict, card_type: str) -> str:
    key = (
        "nerdmedica-de-pro::"
        f"{card_type}::"
        f"{word.get('de_word','').strip().lower()}::"
        f"{word.get('gender_class','').strip().lower()}::"
        f"{word.get('en_meaning','').strip().lower()}"
    )
    return hashlib.md5(key.encode("utf-8")).hexdigest()[:10]

try:
    import genanki
except ImportError as e:
    raise ImportError(
        "genanki is required. Install with: pip install genanki --break-system-packages"
    ) from e


# ==============================================================
# CSS  —  works in both LIGHT and DARK (Anki .nightMode)
# ==============================================================
CSS = """
.card {
  font-family: -apple-system, "Helvetica Neue", "Segoe UI", Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #1F2937;
  background-color: #FAFAF9;
  padding: 24px 18px;
  line-height: 1.55;
}
.pos-tag {
  display: inline-block; font-size: 11px; padding: 4px 12px;
  border-radius: 12px; background: #F1F1EF; color: #6B7280;
  letter-spacing: 1.2px; text-transform: uppercase; font-weight: 600;
  margin-bottom: 16px;
}
.en-meaning { font-size: 28px; font-weight: 500; color: #111827; margin: 8px 0 6px 0; }
.identifier {
  font-size: 15px; color: #6B7280; font-style: italic;
  margin: 4px 0 18px 0; font-weight: 500;
}
.identifier .quote { color: #9CA3AF; }
.de-word { font-size: 34px; font-weight: 700; margin: 14px 0 6px 0; letter-spacing: -0.3px; }
.der  { color: #1E40AF; }
.die  { color: #BE185D; }
.das  { color: #047857; }
.pl   { color: #C2410C; }
.verb { color: #6D28D9; }
.adj  { color: #0E7490; }
.prep { color: #A16207; }
.pron {
  font-size: 15px; color: #6B7280; font-style: italic;
  margin: 4px 0 20px 0;
  font-family: "Consolas", "SF Mono", Menlo, monospace;
}
hr { border: none; border-top: 1px solid #E5E7EB; margin: 20px auto; width: 55%; }
.de-sentence { font-size: 20px; color: #111827; margin: 14px 8px 6px 8px; line-height: 1.5; }
.de-sentence b { color: #B45309; font-weight: 700; }
.en-sentence { font-size: 15px; color: #6B7280; font-style: italic; margin: 6px 8px 16px 8px; }
.note {
  display: inline-block; font-size: 13px; background: #FEF2F2; color: #991B1B;
  border-left: 3px solid #DC2626; padding: 8px 14px; margin-top: 14px;
  text-align: left; max-width: 92%; border-radius: 3px; line-height: 1.45;
}
.cloze { font-weight: 700; color: #B45309; }
.hint { font-size: 13px; color: #9CA3AF; margin-top: 18px; font-style: italic; }
.translation { font-size: 15px; color: #6B7280; margin-top: 12px; font-style: italic; }
.usage-line { font-size: 24px; margin: 18px 0; color: #111827; font-weight: 500; }
.grammar-table { margin: 12px auto; font-size: 17px; color: #1F2937; border-collapse: collapse; }
.grammar-table td { padding: 7px 16px; border-bottom: 1px solid #E5E7EB; text-align: left; }
.grammar-table td:first-child { color: #6B7280; text-align: right; font-size: 14px; }
.grammar-table tr:last-child td { border-bottom: none; }
.grammar-decl td { text-align: center; padding: 6px 12px; }
.grammar-decl td:first-child { text-align: right; font-size: 13px; color: #6B7280; font-weight: 600; padding-right: 14px; }
.grammar-decl tr.dg-header td { font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #D1D5DB; padding-bottom: 4px; }
.grammar-decl .dg-sing, .grammar-decl .dg-plur { min-width: 90px; }

/* Dark mode — Anki injects .nightMode on card / .night_mode on body */
.nightMode.card, .card.nightMode, .night_mode .card {
  color: #E5E7EB; background-color: #1F1F23;
}
.nightMode .pos-tag, .card.nightMode .pos-tag { background: #2A2A2E; color: #9CA3AF; }
.nightMode .en-meaning, .card.nightMode .en-meaning { color: #F9FAFB; }
.nightMode .identifier, .card.nightMode .identifier { color: #9CA3AF; }
.nightMode .identifier .quote, .card.nightMode .identifier .quote { color: #6B7280; }
.nightMode .der,  .card.nightMode .der  { color: #60A5FA; }
.nightMode .die,  .card.nightMode .die  { color: #F472B6; }
.nightMode .das,  .card.nightMode .das  { color: #34D399; }
.nightMode .pl,   .card.nightMode .pl   { color: #FB923C; }
.nightMode .verb, .card.nightMode .verb { color: #C084FC; }
.nightMode .adj,  .card.nightMode .adj  { color: #22D3EE; }
.nightMode .prep, .card.nightMode .prep { color: #FCD34D; }
.nightMode .pron, .card.nightMode .pron { color: #9CA3AF; }
.nightMode hr,    .card.nightMode hr    { border-top-color: #2E2E33; }
.nightMode .de-sentence, .card.nightMode .de-sentence { color: #F3F4F6; }
.nightMode .de-sentence b, .card.nightMode .de-sentence b { color: #FBBF24; }
.nightMode .en-sentence, .card.nightMode .en-sentence { color: #9CA3AF; }
.nightMode .note, .card.nightMode .note {
  background: #2A1F1F; color: #FCA5A5; border-left-color: #F87171;
}
.nightMode .cloze, .card.nightMode .cloze { color: #FBBF24; }
.nightMode .hint, .card.nightMode .hint { color: #6B7280; }
.nightMode .translation, .card.nightMode .translation { color: #9CA3AF; }
.nightMode .usage-line, .card.nightMode .usage-line { color: #F3F4F6; }
.nightMode .grammar-table, .card.nightMode .grammar-table { color: #E5E7EB; }
.nightMode .grammar-table td, .card.nightMode .grammar-table td { border-bottom-color: #2E2E33; }
.nightMode .grammar-table td:first-child, .card.nightMode .grammar-table td:first-child { color: #9CA3AF; }
.nightMode .grammar-decl tr.dg-header td, .card.nightMode .grammar-decl tr.dg-header td { color: #6B7280; border-bottom-color: #2E2E33; }
.nightMode .grammar-decl td:first-child, .card.nightMode .grammar-decl td:first-child { color: #9CA3AF; }

/* Flipped CORE — big English reveal */
.en-reveal {
  font-size: 30px; font-weight: 600; color: #111827;
  margin: 16px 0 18px 0; letter-spacing: -0.2px;
}
.de-word-recap { font-size: 20px; font-weight: 600; margin: 8px 0 4px 0; letter-spacing: -0.2px; }
.nightMode .en-reveal, .card.nightMode .en-reveal { color: #F9FAFB; }

/* Word family list */
.word-family-list {
  list-style: none; padding: 0; margin: 14px auto 8px auto;
  font-size: 17px; line-height: 1.9; color: #1F2937; max-width: 85%;
}
.word-family-list li { padding: 4px 0; border-bottom: 1px dashed #E5E7EB; text-align: center; }
.word-family-list li:last-child { border-bottom: none; }
.nightMode .word-family-list, .card.nightMode .word-family-list { color: #E5E7EB; }
.nightMode .word-family-list li, .card.nightMode .word-family-list li { border-bottom-color: #2E2E33; }

@media (max-width: 500px) {
  .card { font-size: 18px; padding: 16px 12px; }
  .en-meaning { font-size: 24px; }
  .de-word { font-size: 28px; }
  .de-sentence, .usage-line { font-size: 18px; }
  .grammar-table { font-size: 15px; }
  .grammar-table td { padding: 6px 10px; }
}
"""


# ==============================================================
# NOTE TYPES — stable IDs so re-imports update in place
# ==============================================================
def _make_models():
    core = genanki.Model(
        2001001001, "NerdMedica DE PRO — Core",
        fields=[{"name": n} for n in [
            "EN_Meaning","POS","DE_Word","Article","GenderClass",
            "Pronunciation","DE_Sentence","EN_Sentence","Note",
            "Audio_Word","Audio_Sentence",
        ]],
        # Two templates on one note → Anki generates 2 cards per word.
        # Bury siblings keeps only one per day.
        templates=[
            {
                "name": "DE → EN",
                "qfmt": ('<div class="pos-tag">{{POS}}</div>'
                         '<div class="de-word {{GenderClass}}">{{Article}} {{DE_Word}}</div>'),
                "afmt": ('<div class="pos-tag">{{POS}}</div>'
                         '<div class="de-word-recap {{GenderClass}}">{{Article}} {{DE_Word}}</div>'
                         '{{#Pronunciation}}<div class="pron">/{{Pronunciation}}/</div>{{/Pronunciation}}'
                         '<hr>'
                         '<div class="en-reveal">{{EN_Meaning}}</div>'
                         '<div class="de-sentence">{{DE_Sentence}}</div>'
                         '<div class="en-sentence">{{EN_Sentence}}</div>'
                         '{{#Note}}<div class="note">{{Note}}</div>{{/Note}}'
                         '{{Audio_Word}}{{Audio_Sentence}}'),
            },
            {
                "name": "EN → DE",
                "qfmt": ('<div class="pos-tag">{{POS}}</div>'
                         '<div class="en-meaning">{{EN_Meaning}}</div>'),
                "afmt": ('<div class="pos-tag">{{POS}}</div>'
                         '<div class="en-meaning">{{EN_Meaning}}</div>'
                         '<hr>'
                         '<div class="de-word {{GenderClass}}">{{Article}} {{DE_Word}}</div>'
                         '{{#Pronunciation}}<div class="pron">/{{Pronunciation}}/</div>{{/Pronunciation}}'
                         '<div class="de-sentence">{{DE_Sentence}}</div>'
                         '<div class="en-sentence">{{EN_Sentence}}</div>'
                         '{{#Note}}<div class="note">{{Note}}</div>{{/Note}}'
                         '{{Audio_Word}}{{Audio_Sentence}}'),
            },
        ],
        css=CSS,
    )
    cloze_sent = genanki.Model(
        2001001002, "NerdMedica DE PRO — Cloze Sentence",
        fields=[{"name": "Text"}, {"name": "Translation"}, {"name": "Hint"}, {"name": "Audio"}],
        templates=[{
            "name": "Cloze Sentence",
            "qfmt": ('<div class="pos-tag">SENTENCE</div>'
                     '<div class="identifier"><span class="quote">&ldquo;</span>{{Translation}}<span class="quote">&rdquo;</span></div>'
                     '<div class="de-sentence">{{cloze:Text}}</div>'
                     '{{#Hint}}<div class="hint">💡 {{Hint}}</div>{{/Hint}}'),
            "afmt": ('<div class="pos-tag">SENTENCE</div>'
                     '<div class="identifier"><span class="quote">&ldquo;</span>{{Translation}}<span class="quote">&rdquo;</span></div>'
                     '<div class="de-sentence">{{cloze:Text}}</div>'
                     '{{Audio}}'),
        }],
        css=CSS, model_type=genanki.Model.CLOZE,
    )
    cloze_gram = genanki.Model(
        2001001003, "NerdMedica DE PRO — Cloze Grammar",
        fields=[{"name": "Text"}, {"name": "Header_EN"}, {"name": "Header_POS"}, {"name": "Notes"}],
        templates=[{
            "name": "Cloze Grammar",
            "qfmt": ('<div class="pos-tag">{{Header_POS}}</div>'
                     '<div class="identifier">{{Header_EN}}</div>'
                     '{{cloze:Text}}'),
            "afmt": ('<div class="pos-tag">{{Header_POS}}</div>'
                     '<div class="identifier">{{Header_EN}}</div>'
                     '{{cloze:Text}}'
                     '{{#Notes}}<div class="note">{{Notes}}</div>{{/Notes}}'),
        }],
        css=CSS, model_type=genanki.Model.CLOZE,
    )
    cloze_use = genanki.Model(
        2001001004, "NerdMedica DE PRO — Cloze Usage",
        fields=[{"name": "Text"}, {"name": "Meaning"}],
        templates=[{
            "name": "Cloze Usage",
            "qfmt": ('<div class="pos-tag">USAGE</div>'
                     '<div class="identifier"><span class="quote">&ldquo;</span>{{Meaning}}<span class="quote">&rdquo;</span></div>'
                     '<div class="usage-line">{{cloze:Text}}</div>'),
            "afmt": ('<div class="pos-tag">USAGE</div>'
                     '<div class="identifier"><span class="quote">&ldquo;</span>{{Meaning}}<span class="quote">&rdquo;</span></div>'
                     '<div class="usage-line">{{cloze:Text}}</div>'),
        }],
        css=CSS, model_type=genanki.Model.CLOZE,
    )
    expand = genanki.Model(
        2001001005, "NerdMedica DE PRO — Expand (Syn/Ant)",
        fields=[{"name": "Text"}, {"name": "Header_EN"}],
        templates=[{
            "name": "Expand",
            "qfmt": ('<div class="pos-tag">EXPAND</div>'
                     '<div class="identifier">{{Header_EN}}</div>'
                     '{{cloze:Text}}'),
            "afmt": ('<div class="pos-tag">EXPAND</div>'
                     '<div class="identifier">{{Header_EN}}</div>'
                     '{{cloze:Text}}'),
        }],
        css=CSS, model_type=genanki.Model.CLOZE,
    )
    word_family = genanki.Model(
        2001001006, "NerdMedica DE PRO — Word Family",
        fields=[{"name": "Text"}, {"name": "Header"}],
        templates=[{
            "name": "Word Family",
            "qfmt": ('<div class="pos-tag">FAMILY</div>'
                     '<div class="identifier">{{Header}}</div>'
                     '{{cloze:Text}}'),
            "afmt": ('<div class="pos-tag">FAMILY</div>'
                     '<div class="identifier">{{Header}}</div>'
                     '{{cloze:Text}}'),
        }],
        css=CSS, model_type=genanki.Model.CLOZE,
    )
    return {
        "core": core, "cloze_sentence": cloze_sent, "cloze_grammar": cloze_gram,
        "cloze_usage": cloze_use, "expand": expand, "word_family": word_family,
    }


# ==============================================================
# CARD BUILDERS — each takes a word dict, returns
#   {"model": key, "fields": [...], "tags": [...]}
# or returns None to gracefully skip.
# ==============================================================

_POS_TAG = {
    "der": "NOUN", "die": "NOUN", "das": "NOUN", "pl": "NOUN (PL.)",
    "verb": "VERB", "adj": "WORD", "adv": "ADVERB", "pron": "PRONOUN / DET",
    "conj": "CONJUNCTION", "prep": "PREPOSITION",
}
_POS_SLUG = {
    "der": "noun", "die": "noun", "das": "noun", "pl": "noun",
    "verb": "verb", "adj": "other", "adv": "adv", "pron": "pron",
    "conj": "conj", "prep": "prep",
}
_PRONOUN_RE = re.compile(r"^(?:ich|du|er/sie/es|er/sie|er|sie|es|wir|ihr)\s+", re.I)


def _strip_pron(form: str) -> str:
    """'ich baue' -> 'baue' (the card adds the pronoun itself, outside the cloze)."""
    return _PRONOUN_RE.sub("", (form or "").strip())

def _base_tags(word: dict) -> list[str]:
    """Preserve user-supplied tags + add our filter tags."""
    tags = ["pro_v3", f"pos::{_POS_SLUG.get(word.get('gender_class',''), 'other')}"]
    for t in word.get("tags", []) or []:
        if t and t not in tags:
            tags.append(t)
    return tags


def build_core(word: dict) -> dict | None:
    """Always builds — Core is the only mandatory card."""
    return {
        "model": "core",
        "fields": [
            word["en_meaning"],
            _POS_TAG.get(word.get("gender_class",""), "WORD"),
            word["de_word"],
            word.get("article", ""),
            word.get("gender_class", ""),
            word.get("pronunciation", ""),
            word.get("de_sentence", ""),
            word.get("en_sentence", ""),
            word.get("note", ""),
            word.get("audio_word", ""),
            word.get("audio_sentence", ""),
        ],
        "tags": _base_tags(word) + ["type::core"],
    }


def build_cloze_sentence(word: dict) -> dict | None:
    """Requires de_sentence with <b>target</b> markup and en_sentence."""
    de = word.get("de_sentence", "")
    en = word.get("en_sentence", "")
    if not de or "<b>" not in de:
        return None
    text = re.sub(r"<b>(.*?)</b>", r"{{c1::\1}}", de)
    gc = word.get("gender_class", "")
    hint = {"der": "noun", "die": "noun", "das": "noun", "pl": "plural noun",
            "verb": "verb", "adj": "adjective / expression", "adv": "adverb",
            "pron": "pronoun / determiner", "conj": "conjunction",
            "prep": "preposition"}.get(gc, "")
    return {
        "model": "cloze_sentence",
        "fields": [text, en, hint, word.get("audio_sentence", "")],
        "tags": _base_tags(word) + ["type::cloze_sentence"],
    }


def _split_article_from(v: str) -> tuple[str, str]:
    """'der Alltag' → ('der', 'Alltag'). Returns ('', v) if no leading article."""
    if not v: return ("", "")
    parts = v.split(None, 1)
    if len(parts) == 2 and parts[0].lower() in ("der","die","das","den","dem","des"):
        return parts[0], parts[1]
    return ("", v)


def build_cloze_grammar(word: dict) -> dict | None:
    """
    NOUN GRAMMAR — full 4-case × 2-number table.
        4 clozes, one per case (Nom/Akk/Dat/Gen), each covering BOTH sing & plur articles.
        Bury-siblings ensures only one case-drill per noun per day.

    VERB GRAMMAR — full available conjugation.
        Uses whatever source data provides: praesens_ich, praesens_er,
        praeteritum, perfekt, konjunktiv_ii, imperativ.
        Cloze grouped by tense so one card = one tense.

    Adjectives / others skip by default (returns None).
    """
    gc = word.get("gender_class", "")
    en = word.get("en_meaning", "")
    de = word["de_word"]

    # ---------------- NOUNS ----------------
    if gc in ("der", "die", "das"):
        decl = dict(word.get("declension", {}) or {})
        # Accusative equals nominative for plural, and for feminine/neuter singular: fill it when the source omits it
        if decl.get("nom_plur") and decl["nom_plur"].lower() not in ("—", "-", "kein plural") and not decl.get("akk_plur"):
            decl["akk_plur"] = decl["nom_plur"]
        if gc in ("die", "das") and decl.get("nom_sing") and not decl.get("akk_sing"):
            decl["akk_sing"] = decl["nom_sing"]
        # Detect "no plural" nouns
        no_plur_marker = False
        plur_check = (decl.get("nom_plur") or "").lower()
        if plur_check in ("—", "-", "kein plural", "") and not decl.get("akk_plur"):
            no_plur_marker = True

        rows_html = []
        case_labels = [("nom","Nom"), ("akk","Akk"), ("dat","Dat"), ("gen","Gen")]
        cidx = 0
        for case_key, case_label in case_labels:
            sing = decl.get(f"{case_key}_sing", "")
            plur = decl.get(f"{case_key}_plur", "")
            if not sing and not plur:
                continue
            cidx += 1
            # Split article from noun stem
            sing_art, sing_stem = _split_article_from(sing)
            plur_art, plur_stem = _split_article_from(plur)
            # Format each cell — cloze the article, leave stem visible
            def _fmt(art, stem, ci):
                if not art and not stem: return "—"
                if art: return f"{{{{c{ci}::{art}}}}} {stem}"
                return stem
            sing_cell = _fmt(sing_art, sing_stem, cidx)
            if no_plur_marker:
                plur_cell = "—"
            else:
                plur_cell = _fmt(plur_art, plur_stem, cidx) if (plur_art or plur_stem) else "—"
            rows_html.append(
                f'<tr><td>{case_label}:</td><td class="dg-sing">{sing_cell}</td>'
                f'<td class="dg-plur">{plur_cell}</td></tr>'
            )

        if cidx < 2:  # need at least 2 cases to be a useful drill
            return None

        header_row = ('<tr class="dg-header"><td></td><td class="dg-sing">Singular</td>'
                      '<td class="dg-plur">Plural</td></tr>')
        text = ('<table class="grammar-table grammar-decl">'
                + header_row + "".join(rows_html) + "</table>")

        notes_map = {
            "der": "Masc: Nom der · Akk den · Dat dem · Gen des.",
            "die": "Fem: Nom die · Akk die · Dat der · Gen der.",
            "das": "Neut: Nom das · Akk das · Dat dem · Gen des.",
        }
        return {
            "model": "cloze_grammar",
            "fields": [text, en, "GRAMMAR · NOUN", notes_map.get(gc, "")],
            "tags": _base_tags(word) + ["type::cloze_grammar"],
        }

    # ---------------- VERBS ----------------
    if gc == "verb":
        conj = word.get("conjugation", {}) or {}
        rows_html = []
        cidx = 0

        # Present tense — one cloze covering both ich + er when both exist
        ich = _strip_pron(conj.get("praesens_ich", "")); er = _strip_pron(conj.get("praesens_er", ""))
        if ich in ("—", "-"): ich = ""
        if ich and er:
            cidx += 1
            rows_html.append(
                f"<tr><td>Präsens:</td><td>ich {{{{c{cidx}::{ich}}}}} · "
                f"er/sie {{{{c{cidx}::{er}}}}}</td></tr>"
            )
        elif ich:
            cidx += 1
            rows_html.append(f"<tr><td>Präsens ich:</td><td>{{{{c{cidx}::{ich}}}}}</td></tr>")
        elif er:
            cidx += 1
            rows_html.append(f"<tr><td>Präsens er:</td><td>{{{{c{cidx}::{er}}}}}</td></tr>")

        prt = _strip_pron(conj.get("praeteritum", ""))
        if prt in ("—", "-"): prt = ""
        if prt:
            cidx += 1
            rows_html.append(f"<tr><td>Präteritum:</td><td>{{{{c{cidx}::{prt}}}}}</td></tr>")

        prf = conj.get("perfekt")
        if prf:
            cidx += 1
            m = re.match(r"^(hat|ist|hatte|war)\s+(.+)$", prf)
            if m:
                rows_html.append(
                    f"<tr><td>Perfekt:</td><td>{m.group(1)} {{{{c{cidx}::{m.group(2)}}}}}</td></tr>"
                )
            else:
                rows_html.append(f"<tr><td>Perfekt:</td><td>{{{{c{cidx}::{prf}}}}}</td></tr>")

        kii = conj.get("konjunktiv_ii")
        if kii and kii != "—":
            cidx += 1
            rows_html.append(f"<tr><td>Konjunktiv II:</td><td>{{{{c{cidx}::{kii}}}}}</td></tr>")

        imp = conj.get("imperativ")
        if imp and imp != "—":
            cidx += 1
            rows_html.append(f"<tr><td>Imperativ:</td><td>{{{{c{cidx}::{imp}}}}}</td></tr>")

        if cidx < 2:
            return None

        text = '<table class="grammar-table">' + "".join(rows_html) + "</table>"
        case_gov = word.get("case_government", "")
        notes = f"Case government: {case_gov}" if case_gov else ""
        return {
            "model": "cloze_grammar",
            "fields": [text, f"{de} — {en}", "GRAMMAR · VERB", notes],
            "tags": _base_tags(word) + ["type::cloze_grammar"],
        }

    return None  # adj / prep / other → no grammar card


def build_cloze_usage(word: dict) -> dict | None:
    """
    Uses the FIRST collocation. Cloze the whole chunk — never leaks
    gender via a visible article in the frame.
    """
    colls = word.get("collocations", []) or []
    if isinstance(colls, str):
        colls = [c.strip() for c in colls.split(",") if c.strip()]
    if not colls:
        return None
    first = colls[0].strip()
    if not first:
        return None
    text = "{{c1::" + first + "}}"
    return {
        "model": "cloze_usage",
        "fields": [text, word["en_meaning"]],
        "tags": _base_tags(word) + ["type::cloze_usage"],
    }


def build_expand(word: dict) -> dict | None:
    """
    Full CEFR ladder: renders whatever levels the source provides.
    Row order:  A1  (everyday)  →  A2  →  B1  →  B2  →  C1  →  C2 (upgrade)  →  antonym.
    Skips any level that is empty / "—" / equal to the target.
    Dedupes across levels: a C1 that duplicates a B2 is dropped.
    Card is skipped entirely if fewer than 2 clean rows remain.
    """
    syn = word.get("synonyms", {}) or {}
    ant = (word.get("antonym") or "").strip()
    target = word["de_word"].lower().strip()

    CEFR_LEVELS = [
        ("A1",     "A1 (everyday):"),
        ("A2",     "A2 (common):"),
        ("A2/B1",  "A2/B1 (common):"),   # back-compat with old 3-row ladder
        ("B1",     "B1 (standard):"),
        ("B2",     "B2 (advanced):"),
        ("C1",     "C1 (academic):"),
        ("C2",     "C2 (upgrade):"),
    ]

    def _junk(v: str) -> bool:
        return not v or v == "—" or v.lower().strip() == target

    seen_lower: set[str] = set()  # track pieces across levels
    def _clean_slash_list(v: str) -> str:
        """Split 'a / b', drop pieces equal to target or already seen."""
        kept = []
        for p in [x.strip() for x in v.split("/")]:
            pl = p.lower().strip()
            if not pl or pl == target or pl in seen_lower: continue
            kept.append(p); seen_lower.add(pl)
        return " / ".join(kept)

    rows = []
    cidx = 1
    for key, label in CEFR_LEVELS:
        val = (syn.get(key) or "").strip()
        if _junk(val): continue
        cleaned = _clean_slash_list(val)
        if not cleaned: continue
        rows.append((label, cleaned, cidx)); cidx += 1

    # Antonym — not part of CEFR ladder but shares the deduplicator
    if ant and ant != "—" and ant.lower().strip() != target and ant.lower() not in seen_lower:
        rows.append(("antonym:", ant, cidx)); cidx += 1

    if len(rows) < 2:
        return None

    html = '<table class="grammar-table">' + "".join(
        f"<tr><td>{lbl}</td><td>{{{{c{ci}::{val}}}}}</td></tr>" for lbl, val, ci in rows
    ) + "</table>"

    return {
        "model": "expand",
        "fields": [html, word["en_meaning"]],
        "tags": _base_tags(word) + ["type::expand"],
    }


def build_word_family(word: dict) -> dict | None:
    """
    WORD FAMILY — tests derivational knowledge.
    Reads `word_family` field: a list (or comma-separated string) of related
    forms like "familiär (adj.), der Familienname (n.), die Großfamilie (n.)".
    Each entry becomes its own cloze. Skipped if < 2 real entries.
    """
    wf = word.get("word_family")
    if not wf: return None
    if isinstance(wf, str):
        entries = [e.strip() for e in wf.split(",")]
    else:
        entries = [str(e).strip() for e in wf]
    entries = [e for e in entries if e and e != "—"]
    target = word["de_word"].lower().strip()
    # Drop entries that are literally the target itself
    entries = [e for e in entries if e.lower().split("(")[0].strip() != target
                                   and e.lower() != f"{word.get('article','').lower()} {target}".strip()]
    if len(entries) < 2:
        return None

    items = "".join(
        f"<li>{{{{c{i}::{e}}}}}</li>" for i, e in enumerate(entries, start=1)
    )
    text = f'<ul class="word-family-list">{items}</ul>'
    article = word.get("article", "")
    header = f"{article} {word['de_word']} — {word['en_meaning']}".strip()
    return {
        "model": "word_family",
        "fields": [text, header],
        "tags": _base_tags(word) + ["type::word_family"],
    }


BUILDERS = [
    ("core",           build_core),
    ("cloze_sentence", build_cloze_sentence),
    ("cloze_grammar",  build_cloze_grammar),
    ("cloze_usage",    build_cloze_usage),
    ("expand",         build_expand),
    ("word_family",    build_word_family),
]

# Subdeck label (per card type) + offset added to the parent deck_id
SUBDECK_SPEC = [
    ("core",           "1_Core",       1),
    ("cloze_sentence", "2_Production", 2),
    ("cloze_grammar",  "3_Grammar",    3),
    ("cloze_usage",    "4_Chunks",     4),
    ("expand",         "5_Breadth",    5),
    ("word_family",    "6_Family",     6),
]


# ==============================================================
# DECK BUILDER — the public entry point
# ==============================================================
def _norm(v):
    """NFC-normalize strings so 'ü' typed two ways never creates two notes."""
    if isinstance(v, str):
        return unicodedata.normalize("NFC", v).strip()
    if isinstance(v, list):
        return [_norm(x) for x in v]
    if isinstance(v, dict):
        return {k: _norm(x) for k, x in v.items()}
    return v


def prepare_words(words: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Validate, normalize and de-duplicate the input word list.
    Duplicates = same (de_word, gender_class, en_meaning). The first copy wins;
    tags from later copies are merged into it. Returns (clean_words, warnings).
    """
    clean: list[dict] = []
    seen: dict[tuple, dict] = {}
    warnings: list[str] = []
    for i, w in enumerate(words):
        w = _norm(dict(w))
        missing = [k for k in ("en_meaning", "de_word", "gender_class") if not w.get(k)]
        if missing:
            warnings.append(f"word #{i} skipped — missing {missing}")
            continue
        if w["gender_class"] not in _POS_TAG:
            warnings.append(f"'{w['de_word']}': unknown gender_class "
                            f"'{w['gender_class']}' (treated as other)")
        key = (w["de_word"].lower(), w["gender_class"].lower(), w["en_meaning"].lower())
        if key in seen:
            first = seen[key]
            for t in w.get("tags", []) or []:
                if t not in first.setdefault("tags", []):
                    first["tags"].append(t)
            warnings.append(f"duplicate '{w['de_word']}' merged")
            continue
        seen[key] = w
        clean.append(w)
    return clean, warnings


def build_deck(
    words: list[dict],
    deck_name: str,
    deck_id: int,
    out_path: str,
    guid_overrides: dict[tuple[str, str], str] | None = None,
    media_files: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build an .apkg containing SIX subdecks (one per card type) nested under
    `deck_name`:  ::1_Core ::2_Production ::3_Grammar ::4_Chunks ::5_Breadth ::6_Family

    Each subdeck has its own daily new-card limit in Anki.
    deck_id — base integer. Subdeck IDs are deck_id * 10 + offset (1..6).
    guid_overrides — {(card_type, stable_guid): old_guid} for progress migration.
    media_files — paths of audio files referenced by [sound:...] fields.
    Words must already be passed through prepare_words().
    """
    models = _make_models()
    subdecks: dict[str, genanki.Deck] = {
        key: genanki.Deck(deck_id * 10 + offset, f"{deck_name}::{suffix}")
        for key, suffix, offset in SUBDECK_SPEC
    }

    per_type = {k: 0 for k, _ in BUILDERS}
    skipped  = {k: 0 for k, _ in BUILDERS if k != "core"}
    guid_overrides = guid_overrides or {}
    used_guids: set[str] = set()

    # OUTER = card type, INNER = word → CORE notes get the lowest due numbers
    for key, builder in BUILDERS:
        for w in words:
            card = builder(w)
            if card is None:
                if key in skipped:
                    skipped[key] += 1
                continue
            sguid = stable_guid(w, key)
            guid = guid_overrides.get((key, sguid), sguid)
            if guid in used_guids:          # two words claimed the same old note
                guid = sguid
            used_guids.add(guid)
            subdecks[key].add_note(genanki.Note(
                model=models[card["model"]],
                fields=card["fields"],
                tags=card["tags"],
                guid=guid,
            ))
            per_type[key] += 1

    pkg = genanki.Package(list(subdecks.values()))
    if media_files:
        pkg.media_files = media_files
    pkg.write_to_file(out_path)
    return {
        "out_path": out_path,
        "per_type": per_type,
        "skipped":  skipped,
        "n_words":  len(words),
        "n_notes":  sum(per_type.values()),
        "n_media":  len(media_files or []),
        "subdeck_names": {k: d.name for k, d in subdecks.items()},
    }
