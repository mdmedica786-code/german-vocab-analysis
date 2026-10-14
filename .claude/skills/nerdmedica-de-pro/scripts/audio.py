"""
audio.py — optional native-speaker audio for NerdMedica DE PRO.

Engines
-------
  edge  — Microsoft Edge neural voices (recommended, free, no key).
          pip install edge-tts
          NOTE: Microsoft blocks datacenter IPs. Works on a normal home/laptop
          connection; inside a cloud sandbox it usually fails with HTTP 403.
  gtts  — Google Translate TTS. Robotic but works almost everywhere.
          pip install gTTS

Behaviour
---------
* Files are named by a hash of (engine, voice, rate, text) and cached in
  `cache_dir`. Rebuilding a deck never re-downloads existing audio.
* A failed clip never breaks the build: the field is left empty and the
  failure is counted.
* Adds to each word dict:  audio_word = "[sound:x.mp3]",  audio_sentence = "[sound:y.mp3]"
"""
from __future__ import annotations

import asyncio
import hashlib
import re
from pathlib import Path

VOICES = {
    "katja":   "de-DE-KatjaNeural",
    "conrad":  "de-DE-ConradNeural",
    "florian": "de-DE-FlorianMultilingualNeural",
    "amala":   "de-DE-AmalaNeural",
    "killian": "de-DE-KillianNeural",
}

_TAGS = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", _TAGS.sub("", text or "")).strip()


def _fname(engine: str, voice: str, rate: str, text: str) -> str:
    h = hashlib.md5(f"{engine}|{voice}|{rate}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"nmdepro_{h}.mp3"


async def _edge_one(text, voice, rate, out: Path, sem, retries=3):
    import edge_tts
    async with sem:
        for attempt in range(retries):
            try:
                comm = edge_tts.Communicate(text, voice, rate=rate)
                await comm.save(str(out))
                if out.exists() and out.stat().st_size > 0:
                    return True
            except Exception:
                await asyncio.sleep(1.5 * (attempt + 1))
        if out.exists() and out.stat().st_size == 0:
            out.unlink()
        return False


def _gtts_one(text, out: Path, slow: bool):
    from gtts import gTTS
    try:
        gTTS(text=text, lang="de", slow=slow).save(str(out))
        return out.stat().st_size > 0
    except Exception:
        if out.exists():
            out.unlink()
        return False


def add_audio(words: list[dict], engine: str = "edge", voice: str = "katja",
              rate: str = "-10%", cache_dir: str = "/tmp/nmdepro_audio",
              sentences: bool = True, concurrency: int = 4) -> dict:
    """
    Generate audio for every word (and its example sentence) in place.
    Returns {"media_files": [...], "made": n, "cached": n, "failed": n}.
    """
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    voice_id = VOICES.get(voice.lower(), voice)

    # Collect jobs: (word_index, field, text, path)
    jobs = []
    for i, w in enumerate(words):
        word_text = _clean(f"{w.get('article', '')} {w['de_word']}")
        jobs.append((i, "audio_word", word_text))
        if sentences and w.get("de_sentence"):
            jobs.append((i, "audio_sentence", _clean(w["de_sentence"])))

    made = cached = failed = 0
    todo = []
    for i, field, text in jobs:
        if not text:
            continue
        out = cache / _fname(engine, voice_id, rate, text)
        if out.exists() and out.stat().st_size > 0:
            cached += 1
            words[i][field] = f"[sound:{out.name}]"
        else:
            todo.append((i, field, text, out))

    if todo:
        if engine == "edge":
            async def run():
                sem = asyncio.Semaphore(concurrency)
                return await asyncio.gather(*[
                    _edge_one(t, voice_id, rate, o, sem) for _, _, t, o in todo
                ])
            results = asyncio.run(run())
        elif engine == "gtts":
            slow = rate.startswith("-") and rate not in ("-0%", "-5%")
            results = [_gtts_one(t, o, slow) for _, _, t, o in todo]
        else:
            raise ValueError(f"unknown audio engine '{engine}' (use edge or gtts)")

        for (i, field, _, out), ok in zip(todo, results):
            if ok:
                made += 1
                words[i][field] = f"[sound:{out.name}]"
            else:
                failed += 1
                words[i][field] = ""

    media = sorted({str(cache / m.group(1))
                    for w in words for f in ("audio_word", "audio_sentence")
                    for m in [re.match(r"\[sound:(.+)\]", w.get(f, "") or "")] if m})
    return {"media_files": media, "made": made, "cached": cached, "failed": failed}
