#!/usr/bin/env python3
"""download_audio.py - native German audio for the word banks (Lingua Libre first, Wikimedia Commons second).

  python3 work/download_audio.py --test 50        first 50 words (speed / quality check)
  python3 work/download_audio.py --level A1       A1 | A2 | B1 | B2 | C1  (B2 = main-bank B2 words + the B2 extra bank)
  python3 work/download_audio.py --all            every word in both banks
  python3 work/download_audio.py --all --dry-run  show what would be looked up, no network

Source 1: Lingua Libre SPARQL (https://lingualibre.org/bigdata/namespace/wdq/sparql), German recordings, batches of
          ~75 words with VALUES ?word { ... }; the file is fetched from Wikimedia Commons (Special:FilePath).
Source 2: Wikimedia Commons files File:De-{word}.ogg / File:De-{word}.wav (Wiktionary pronunciations).
Files go to bank_final/audio/; work/audio_manifest.json lists word, file, source (lingua_libre | wikimedia_wiktionary | missing), speaker.
Re-runs skip words that already have a file. Words marked missing are only retried with --retry-missing.
Wikimedia policy: every request sends a descriptive User-Agent; requests are spaced out and retried politely.
"""
import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_util import AUDIO_DIR, MANIFEST, ROOT, clean_word, file_stem  # noqa: E402

UA = "MedicaGermanStudy/1.0 (educational)"
SPARQL = "https://lingualibre.org/bigdata/namespace/wdq/sparql"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
FILEPATH = "https://commons.wikimedia.org/wiki/Special:FilePath/"
LANG_QID = "Q24"  # German in Lingua Libre (as given by the project); verified at start-up, override with --lang-qid
BANKS = ROOT / "bank_final"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]
PREFIX = ("PREFIX prop: <https://lingualibre.org/prop/direct/>\n"
          "PREFIX entity: <https://lingualibre.org/entity/>\n"
          "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n")


# ------------------------------------------------------------------ network
def http(url, data=None, accept=None, tries=5, timeout=60):
    """GET (or POST form data) with the required User-Agent; retries 429/5xx/timeouts with backoff 2,4,8,16 s."""
    delay = 2
    for attempt in range(tries):
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None,
                                     headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                wait = int(e.headers.get("Retry-After", "0") or 0) if e.code == 429 else 0
                time.sleep(max(delay, wait))
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == tries - 1:
                raise
            time.sleep(delay)
            delay *= 2


def sparql(query):
    raw = http(SPARQL, data={"query": query, "format": "json"}, accept="application/sparql-results+json")
    return json.loads(raw)["results"]["bindings"]


# ------------------------------------------------------------------ word list
def read_words(levels=None, include_skipped=False):
    """[(clean_word, [ids], is_bound_prefix)] in study order; main bank first, then the B2 bank."""
    rows = []
    for name in ("vocabulary_bank.csv", "b2_vocabulary_bank.csv"):
        with open(BANKS / name, encoding="utf-8-sig", newline="") as f:
            part = list(csv.DictReader(f))
        if name == "vocabulary_bank.csv":
            part.sort(key=lambda r: int(r["study_order"]) if r.get("study_order", "").isdigit() else 10**9)
        rows += part
    seen, out = {}, []  # out: [word, [bank ids], is_bound_prefix]
    for r in rows:
        if levels and r.get("level") not in levels:
            continue
        if r.get("skip") and not include_skipped:
            continue
        w = clean_word(r["lemma"])
        if not w:
            out.append((r["lemma"], [r["id"]], True))  # bound prefix such as 'Nord-': nothing to record
            continue
        if w in seen:
            seen[w][1].append(r["id"])
        else:
            seen[w] = [w, [r["id"]], False]
            out.append(seen[w])
    return [tuple(x) for x in out]


def group_by_fold(words):
    """'Essen' (noun) and 'essen' (verb) are spoken identically: one lookup / one file per case-folded word."""
    groups = defaultdict(list)
    for w in words:
        groups[w.casefold()].append(w)
    return groups


# ------------------------------------------------------------------ Lingua Libre
def check_language(qid):
    rows = sparql(PREFIX + f"SELECT ?l WHERE {{ entity:{qid} rdfs:label ?l }}")
    labels = [r["l"]["value"] for r in rows]
    if not any(re.search(r"german|deutsch|allemand|deu\b", l, re.I) for l in labels):
        sys.exit(f"entity:{qid} does not look like German in Lingua Libre (labels: {labels[:5]}). Find the right Q-id and pass --lang-qid.")
    return labels


def q_lit(w):
    return '"' + w.replace("\\", "\\\\").replace('"', '\\"') + '"'


def lingualibre_query(variants, qid=LANG_QID):
    return (PREFIX + "SELECT ?word ?file ?speakerLabel WHERE {\n  VALUES ?word { " + " ".join(q_lit(v) for v in variants) + " }\n"
            f"  ?record prop:P4 entity:{qid} ;\n          prop:P5 ?word ;\n          prop:P3 ?file .\n"
            "  OPTIONAL { ?record prop:P6 ?speaker . ?speaker rdfs:label ?speakerLabel . }\n}")


def parse_filename(v):
    """P3 may be a bare file name or a Commons URL; return the bare name ('LL-Q188 (deu)-Name-Haus.wav')."""
    v = urllib.parse.unquote(v.strip())
    v = v.rsplit("/", 1)[-1]
    return re.sub(r"^(File|Datei):", "", v).replace("_", " ")


def speaker_from_filename(name):
    m = re.match(r"LL-Q\d+ \([a-z]+\)-(.+?)-", name)
    return m.group(1) if m else ""


def lingualibre_lookup(groups, qid):
    """groups: {folded: [variants]} -> {folded: [(filename, speaker)]} (all recordings found)."""
    variants = sorted({v for vs in groups.values() for v in vs})
    found = defaultdict(list)
    for b in sparql(lingualibre_query(variants, qid)):
        word = b["word"]["value"]
        name = parse_filename(b["file"]["value"])
        if not name.lower().endswith((".wav", ".ogg", ".oga", ".mp3", ".flac")):
            continue
        spk = (b.get("speakerLabel") or {}).get("value") or speaker_from_filename(name)
        entry = (name, spk, word)
        if entry not in found[word.casefold()]:
            found[word.casefold()].append(entry)
    return found


def choose(entries, speaker_weight):
    """One recording per word: prefer the speaker who recorded most words (consistent voice), then .wav, then name."""
    return sorted(entries, key=lambda e: (-speaker_weight.get(e[1], 0), not e[0].lower().endswith(".wav"), e[0]))[0]


# ------------------------------------------------------------------ Commons (Wiktionary pronunciations)
def commons_titles(word):
    return [f"File:De-{word}.ogg", f"File:De-{word}.wav"]


def strip_html(s):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def commons_lookup(words):
    """words: list of words -> {word: (url, filename, speaker)} for those with a De-{word}.ogg/.wav file on Commons."""
    out = {}
    for i in range(0, len(words), 25):
        chunk = words[i:i + 25]
        titles = [t for w in chunk for t in commons_titles(w)]
        q = {"action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo", "iiprop": "url|user|extmetadata|mime",
             "titles": "|".join(titles)}
        data = json.loads(http(COMMONS_API + "?" + urllib.parse.urlencode(q), accept="application/json"))
        q_norm = {n["from"]: n["to"] for n in data.get("query", {}).get("normalized", [])}
        by_title = {p["title"]: p for p in data.get("query", {}).get("pages", []) if not p.get("missing") and p.get("imageinfo")}
        for w in chunk:
            for t in commons_titles(w):  # .ogg first
                p = by_title.get(q_norm.get(t, t))
                if p:
                    info = p["imageinfo"][0]
                    meta = info.get("extmetadata", {})
                    spk = strip_html(meta.get("Artist", {}).get("value", "")) or info.get("user", "")
                    out[w] = (info["url"], p["title"].split(":", 1)[1], spk)
                    break
        time.sleep(0.5)
    return out


# ------------------------------------------------------------------ files
def fetch_to(path, url):
    data = http(url, timeout=120)
    if len(data) < 800 or not (data[:4] in (b"RIFF", b"OggS") or data[:3] == b"ID3" or data[:2] == b"\xff\xfb"):
        raise ValueError(f"not an audio file ({len(data)} bytes)")
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(data)
    tmp.replace(path)


def load_manifest_list():
    try:
        return {e["word"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        return {}


def save_manifest(m):
    MANIFEST.write_text(json.dumps(sorted(m.values(), key=lambda e: e["word"].casefold()), ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--test", type=int, metavar="N", help="only the first N words")
    g.add_argument("--level", choices=LEVELS, help="one level (B2 includes the B2 extra bank)")
    g.add_argument("--all", action="store_true", help="every word in both banks")
    ap.add_argument("--batch", type=int, default=75, help="words per SPARQL query (50-100)")
    ap.add_argument("--sleep", type=float, default=0.4, help="seconds between downloads")
    ap.add_argument("--lang-qid", default=LANG_QID, help="Lingua Libre entity of German (default %(default)s)")
    ap.add_argument("--no-fallback", action="store_true", help="skip the Commons De-{word}.ogg fallback")
    ap.add_argument("--retry-missing", action="store_true", help="look up words again that were marked missing")
    ap.add_argument("--refresh", action="store_true", help="download again even if the file exists")
    ap.add_argument("--include-skipped", action="store_true", help="also words flagged skip in the main bank (country names ...)")
    ap.add_argument("--dry-run", action="store_true", help="no network: show the word list and a sample query")
    a = ap.parse_args(argv)

    levels = [a.level] if a.level else None
    words = read_words(levels, a.include_skipped)
    if a.test:
        words = words[:a.test]
    bound = [w for w, _, b in words if b]
    todo_words = [w for w, _, b in words if not b]
    manifest = load_manifest_list()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    def have(w):
        e = manifest.get(w)
        if not e:
            return False
        if e["source"] == "missing":
            return not a.retry_missing
        return (AUDIO_DIR / e["file"]).is_file() and not a.refresh

    groups = group_by_fold([w for w in todo_words if not have(w)])
    print(f"{len(words)} entries ({len(bound)} bound prefixes without audio), {len(todo_words)} words, "
          f"{sum(len(v) for v in groups.values())} to look up in {len(groups)} case-folded groups", file=sys.stderr)
    if a.dry_run:
        sample = [v for vs in list(groups.values())[:5] for v in vs]
        print(lingualibre_query(sample, a.lang_qid))
        print("Commons fallback titles:", [t for w in sample[:3] for t in commons_titles(w)])
        return 0
    try:
        labels = check_language(a.lang_qid) if groups else []
    except (urllib.error.URLError, OSError) as e:
        host = urllib.parse.urlparse(SPARQL).netloc
        sys.exit(f"Cannot reach {host} ({e}). Check the internet connection or, in a cloud session, the network policy "
                 f"(allowed hosts needed: lingualibre.org, commons.wikimedia.org, upload.wikimedia.org).")
    if labels:
        print(f"Lingua Libre entity:{a.lang_qid} = {labels[:3]}", file=sys.stderr)

    # ---- Lingua Libre in batches
    keys = list(groups)
    recs = {}  # folded -> list of (file, speaker, word)
    for i in range(0, len(keys), a.batch):
        part = {k: groups[k] for k in keys[i:i + a.batch]}
        for k, v in lingualibre_lookup(part, a.lang_qid).items():
            recs[k] = v
        print(f"  Lingua Libre {min(i + a.batch, len(keys))}/{len(keys)}: {len(recs)} words with recordings", file=sys.stderr)
        time.sleep(0.5)
    weight = Counter(e[1] for v in recs.values() for e in v)

    results = {}  # folded -> manifest entry parts
    for k, entries in recs.items():
        name, spk, word = choose(entries, weight)
        results[k] = dict(source="lingua_libre", remote=name, speaker=spk, spoken=word, url=FILEPATH + urllib.parse.quote(name.replace(" ", "_")))

    # ---- Commons fallback
    if not a.no_fallback:
        rest = [v for k in keys if k not in results for v in groups[k]]
        for i in range(0, len(rest), 100):
            try:
                hits = commons_lookup(rest[i:i + 100])
            except (urllib.error.URLError, ValueError) as e:
                print("  Commons lookup failed:", e, file=sys.stderr)
                break
            for w, (url, name, spk) in hits.items():
                results[w.casefold()] = dict(source="wikimedia_wiktionary", remote=name, speaker=spk, spoken=w, url=url)
            print(f"  Commons fallback {min(i + 100, len(rest))}/{len(rest)}: {len(hits)} hits in this chunk", file=sys.stderr)

    # ---- download
    used_stems = {p.stem.casefold() for p in AUDIO_DIR.iterdir() if p.is_file()}
    for n, k in enumerate(keys, 1):
        variants = groups[k]
        r = results.get(k)
        if not r:
            for w in variants:
                manifest[w] = dict(word=w, file="", source="missing", speaker="")
            continue
        ext = Path(r["remote"]).suffix.lower() or ".wav"
        stem = file_stem(r["spoken"] if r["spoken"] in variants else variants[0])
        fname = stem + ext
        existing = next((manifest[w]["file"] for w in variants if w in manifest and manifest[w]["file"]), "")
        if existing and (AUDIO_DIR / existing).is_file() and not a.refresh:
            fname = existing
        elif stem.casefold() in used_stems and not (AUDIO_DIR / fname).is_file():
            fname = f"{stem} ({n}){ext}"
        try:
            if a.refresh or not (AUDIO_DIR / fname).is_file():
                fetch_to(AUDIO_DIR / fname, r["url"])
                time.sleep(a.sleep)
        except (urllib.error.URLError, ValueError, OSError) as e:
            print(f"  download failed for {variants[0]}: {e}", file=sys.stderr)
            for w in variants:
                manifest[w] = dict(word=w, file="", source="missing", speaker="", error=str(e)[:80])
            continue
        used_stems.add(Path(fname).stem.casefold())
        for w in variants:
            manifest[w] = dict(word=w, file=fname, source=r["source"], speaker=r["speaker"])
        if n % 25 == 0:
            save_manifest(manifest)
            print(f"  downloaded {n}/{len(keys)}", file=sys.stderr)
    save_manifest(manifest)

    # ---- summary
    mine = [manifest[w] for w in todo_words if w in manifest]
    c = Counter(e["source"] for e in mine)
    ok = c["lingua_libre"] + c["wikimedia_wiktionary"]
    print(f"\nwords: {len(mine)}  lingua_libre: {c['lingua_libre']}  wikimedia_wiktionary: {c['wikimedia_wiktionary']}  missing: {c['missing']}  "
          f"hit rate: {100 * ok / max(1, len(mine)):.1f}%")
    spk = Counter(e["speaker"] for e in mine if e["speaker"])
    print("speakers:", ", ".join(f"{s} ({n})" for s, n in spk.most_common(8)) or "-")
    miss = [e["word"] for e in mine if e["source"] == "missing"]
    if miss:
        print(f"missing ({len(miss)}):", ", ".join(miss[:40]) + (" ..." if len(miss) > 40 else ""))
    print(f"manifest: {MANIFEST}   audio folder: {AUDIO_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
