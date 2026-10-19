#!/usr/bin/env python3
"""compare_folder.py - is my copy (Obsidian vault or word lists) the same as the repo version?

  python compare_folder.py "C:\\path\\to\\my\\German_Vault"                   compares with vocab_bank/bank_final/German_Vault
  python compare_folder.py "C:\\path\\to\\my\\folder" --repo-dir WORD_LISTS    compares with another repo folder
  python compare_folder.py MY_FOLDER --show 30                                list up to 30 files per group

Reports: identical files, files that differ (old or edited), files only in my copy, files only in the repo.
Read-only: it never changes anything. A .obsidian folder and files that start with '.' are ignored.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def digest(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree(base):
    out = {}
    for p in base.rglob("*"):
        if p.is_file() and not any(part.startswith(".") for part in p.relative_to(base).parts):
            out[p.relative_to(base).as_posix()] = p
    return out


def find_base(mine, repo):
    """If the user points at the folder above German_Vault (or the zip was unpacked one level deeper), step into it."""
    if (mine / "German_Vault").is_dir() and not (mine / "00 Home.md").exists():
        return mine / "German_Vault"
    return mine


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mine", help="my folder (for the vault: the German_Vault folder)")
    ap.add_argument("--repo-dir", default="vocab_bank/bank_final/German_Vault", help="repo folder to compare with (relative to the repo root)")
    ap.add_argument("--show", type=int, default=15)
    a = ap.parse_args()
    mine = find_base(Path(a.mine).expanduser(), None)
    repo = (ROOT / a.repo_dir)
    for p in (mine, repo):
        if not p.is_dir():
            sys.exit(f"folder not found: {p}")
    m, r = tree(mine), tree(repo)
    same, diff = [], []
    for k in sorted(set(m) & set(r)):
        (same if m[k].stat().st_size == r[k].stat().st_size and digest(m[k]) == digest(r[k]) else diff).append(k)
    only_m, only_r = sorted(set(m) - set(r)), sorted(set(r) - set(m))
    print(f"my folder   : {mine}  ({len(m)} files)")
    print(f"repo folder : {repo}  ({len(r)} files)")
    print(f"identical   : {len(same)}")
    print(f"different   : {len(diff)}   (old version, or edited by you / your agent)")
    print(f"only in mine: {len(only_m)}")
    print(f"only in repo: {len(only_r)}   (new words or notes you do not have yet)")
    for title, items in (("DIFFERENT", diff), ("ONLY IN MINE", only_m), ("ONLY IN REPO", only_r)):
        if items:
            print(f"\n{title} (first {min(a.show, len(items))} of {len(items)}):")
            for k in items[: a.show]:
                print("  ", k)
    print("\nVERDICT:", "same as the repo" if not (diff or only_m or only_r) else "NOT the same - see the lists above")


if __name__ == "__main__":
    main()
