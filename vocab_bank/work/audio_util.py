"""audio_util.py - shared helpers for the native-audio tools (download_audio.py, make_vault.py, make_study_app.py)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT / "bank_final" / "audio"
MANIFEST = ROOT / "work" / "audio_manifest.json"
EXTS = (".wav", ".ogg", ".oga", ".mp3")


def clean_word(lemma):
    """Word to look up: drop (parentheticals) and [notes], keep the first of 'a/b' alternatives.
    Returns '' for entries that cannot be spoken as a word (bound prefixes such as 'Nord-', 'Ja-/Nein-Frage')."""
    w = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]", "", lemma or "").strip()
    w = re.sub(r"\s*[–—]\s.*$", "", w).strip()
    if "-/" in w or w.endswith("-") or w.startswith("-"):
        return ""
    if "/" in w:
        w = w.split("/")[0].strip()
    return w.rstrip(".,;:!? ").strip()


def file_stem(word):
    """File-system and Obsidian safe name for a word (keeps umlauts and ss)."""
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "_", word).strip()


def load_manifest(path=MANIFEST, audio_dir=AUDIO_DIR):
    """Return {word: filename} for every manifest entry whose file really exists on disk."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    for e in data:
        if e.get("file") and e.get("source") != "missing" and (Path(audio_dir) / e["file"]).is_file():
            out[e["word"]] = e["file"]
    return out


class AudioLookup:
    """lookup.get(lemma) -> audio file name ('' if none). Built once from the manifest + audio folder."""

    def __init__(self, path=MANIFEST, audio_dir=AUDIO_DIR):
        self.exact = load_manifest(path, audio_dir)
        self.folded = {k.casefold(): v for k, v in self.exact.items()}  # 'Essen' and 'essen' share one recording

    def __bool__(self):
        return bool(self.exact)

    def get(self, lemma):
        w = clean_word(lemma)
        if not w:
            return ""
        return self.exact.get(w) or self.folded.get(w.casefold(), "")
