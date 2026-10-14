#!/usr/bin/env python3
"""
build_deck.py — CLI for NerdMedica DE PRO.  words.json → .apkg

    python build_deck.py --words W.json --name "German_PRO_v3::netzwerkA1::kap05" \
        --deck-id 2002001005 --out /mnt/user-data/outputs/kap05.apkg
        [--preserve-progress-from current.apkg]
        [--audio edge|gtts --voice katja --rate -10% --no-sentence-audio]
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nerdmedica_de_pro import build_deck, prepare_words


def main():
    ap = argparse.ArgumentParser(description="Build a NerdMedica DE PRO .apkg")
    ap.add_argument("--words", required=True)
    ap.add_argument("--name", required=True, help="Parent deck name (use ::)")
    ap.add_argument("--deck-id", required=True, type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preserve-progress-from", default=None,
                    help="Medica's current .apkg — keeps scheduling of matching cards")
    ap.add_argument("--audio", choices=["none", "edge", "gtts"], default="none")
    ap.add_argument("--voice", default="katja",
                    help="katja | conrad | florian | amala | killian | full edge voice id")
    ap.add_argument("--rate", default="-10%", help="edge speaking rate, e.g. -10%%, +0%%")
    ap.add_argument("--no-sentence-audio", action="store_true")
    ap.add_argument("--audio-cache", default="/tmp/nmdepro_audio")
    args = ap.parse_args()

    raw = json.load(open(args.words, encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        sys.exit("words.json must be a non-empty JSON list")
    words, warnings = prepare_words(raw)
    if warnings:
        print(f"⚠ {len(warnings)} input warning(s):")
        for w in warnings[:15]:
            print(f"   - {w}")
        if len(warnings) > 15:
            print(f"   … and {len(warnings) - 15} more")
    if not words:
        sys.exit("No valid words after validation.")

    media = []
    if args.audio != "none":
        from audio import add_audio
        print(f"→ Audio: {args.audio} / {args.voice} / rate {args.rate}")
        r = add_audio(words, engine=args.audio, voice=args.voice, rate=args.rate,
                      cache_dir=args.audio_cache, sentences=not args.no_sentence_audio)
        media = r["media_files"]
        print(f"  made {r['made']}, cached {r['cached']}, failed {r['failed']}")
        if r["failed"] and r["made"] == 0 and r["cached"] == 0:
            print("  ⚠ All audio failed (network / blocked IP). Deck is built without audio.")

    overrides, old_index = {}, {}
    if args.preserve_progress_from:
        from progress_migrator import extract_old_index, compute_guid_overrides
        print(f"→ Reading progress from {args.preserve_progress_from}")
        old_index = extract_old_index(Path(args.preserve_progress_from))
        overrides = compute_guid_overrides(words, old_index)
        print(f"  {len(old_index)} old notes indexed, {len(overrides)} matched")

    result = build_deck(words, args.name, args.deck_id, args.out,
                        guid_overrides=overrides, media_files=media)

    if args.preserve_progress_from:
        from progress_migrator import inject_scheduling
        st = inject_scheduling(Path(args.out), old_index, overrides)
        print(f"  scheduling migrated for {st['cards_migrated']} cards "
              f"on {st['notes_matched']} notes")

    print(f"\n✓ {result['out_path']}")
    print(f"  words {result['n_words']} · notes {result['n_notes']} · audio files {result['n_media']}")
    for k, v in result["per_type"].items():
        sk = result["skipped"].get(k, 0)
        print(f"    {k:15s} {v:5d}" + (f"   (skipped {sk})" if sk else ""))


if __name__ == "__main__":
    main()
