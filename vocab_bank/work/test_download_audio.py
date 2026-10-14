"""Offline test of download_audio.py with FAKE network responses (no internet needed).
It checks the logic only (word cleaning, query building, parsing, speaker choice, fallback, manifest, file naming);
it says nothing about the real hit rate - for that run: python3 work/download_audio.py --test 50

  python3 work/test_download_audio.py
"""
import json
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import download_audio as da  # noqa: E402

WAV = b"RIFF" + b"\x00" * 2000
OGG = b"OggS" + b"\x00" * 2000


def fake_http_factory(log):
    def fake_http(url, data=None, accept=None, tries=5, timeout=60):
        log.append(url if not data else (url, data))
        if url == da.SPARQL:
            q = data["query"]
            if "rdfs:label ?l" in q:
                return json.dumps({"results": {"bindings": [{"l": {"value": "German"}}]}}).encode()
            b = []
            if '"Haus"' in q:
                for f, s in (("LL-Q188 (deu)-Anna-Haus.wav", "Anna"), ("LL-Q188 (deu)-Bert-Haus.wav", "Bert")):
                    b.append({"word": {"value": "Haus"}, "file": {"value": f}, "speakerLabel": {"value": s}})
            if '"gehen"' in q:
                b.append({"word": {"value": "gehen"}, "file": {"value": "LL-Q188 (deu)-Anna-gehen.wav"}})  # speaker from file name
            if '"essen"' in q:
                b.append({"word": {"value": "essen"}, "file": {"value": "LL-Q188 (deu)-Anna-essen.wav"}, "speakerLabel": {"value": "Anna"}})
            return json.dumps({"results": {"bindings": b}}).encode()
        if url.startswith(da.COMMONS_API):
            titles = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["titles"][0].split("|")
            pages = [{"title": t, "missing": True} for t in titles]
            for p in pages:
                if p["title"] == "File:De-Kindergarten.ogg":
                    p.pop("missing")
                    p["imageinfo"] = [{"url": "https://upload.wikimedia.org/x/De-Kindergarten.ogg", "user": "Uploader",
                                       "extmetadata": {"Artist": {"value": '<a href="x">Sprecher One</a>'}}}]
            return json.dumps({"query": {"pages": pages}}).encode()
        if "Anna" in url or "upload.wikimedia.org" in url:
            return OGG if url.endswith(".ogg") else WAV
        raise AssertionError("unexpected url " + url)
    return fake_http


class T(unittest.TestCase):
    def test_pipeline(self):
        tmp = Path(tempfile.mkdtemp())
        log = []
        da.AUDIO_DIR, da.MANIFEST = tmp / "audio", tmp / "manifest.json"
        da.http = fake_http_factory(log)
        da.time.sleep = lambda s: None
        words = [("Haus", ["M1"], False), ("gehen", ["M2"], False), ("Essen", ["M3"], False), ("essen", ["M4"], False),
                 ("Kindergarten", ["M5"], False), ("Xylofonwort", ["M6"], False), ("Nord-", ["M7"], True)]
        da.read_words = lambda levels, inc: words
        self.assertEqual(da.main(["--all"]), 0)
        m = {e["word"]: e for e in json.loads(da.MANIFEST.read_text(encoding="utf-8"))}
        self.assertEqual(m["Haus"]["source"], "lingua_libre")
        self.assertEqual(m["gehen"]["speaker"], "Anna")  # parsed from the file name
        self.assertEqual(m["Haus"]["speaker"], "Anna")  # most-covering speaker wins over Bert
        self.assertEqual(m["Essen"]["file"], m["essen"]["file"])  # one recording for both capitalisations
        self.assertEqual(m["Kindergarten"]["source"], "wikimedia_wiktionary")
        self.assertEqual(m["Kindergarten"]["speaker"], "Sprecher One")
        self.assertEqual(m["Xylofonwort"]["source"], "missing")
        self.assertNotIn("Nord-", m)
        for e in m.values():
            if e["source"] != "missing":
                self.assertTrue((da.AUDIO_DIR / e["file"]).is_file())
        n = len(log)
        da.main(["--all"])  # second run: everything known, no downloads
        self.assertFalse([u for u in log[n:] if isinstance(u, str) and "Special:FilePath" in u])

    def test_helpers(self):
        self.assertEqual(da.parse_filename("https://commons.wikimedia.org/wiki/File:LL-Q188_(deu)-Anna-Haus.wav"), "LL-Q188 (deu)-Anna-Haus.wav")
        self.assertEqual(da.speaker_from_filename("LL-Q188 (deu)-Anna-Haus.wav"), "Anna")
        self.assertIn('"a\\"b"', da.lingualibre_query(['a"b']))


if __name__ == "__main__":
    unittest.main(verbosity=2)
