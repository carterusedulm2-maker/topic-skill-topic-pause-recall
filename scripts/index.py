#!/usr/bin/env python3
"""index.py — Manage the paused-task keyword index."""
import json
import os
import sys

MEMORY_DIR = os.environ.get(
    'OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory')
)
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')


def get_index() -> dict:
    """Return the current index, or an empty structure if none exists."""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"keywords": {}}


def remove_keyword(keyword: str) -> bool:
    """Remove a keyword entry from the index. Returns True if it existed."""
    index = get_index()
    kw = keyword.lower().strip()
    if kw in index["keywords"]:
        del index["keywords"][kw]
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        return True
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage the paused-task keyword index.")
    parser.add_argument('--list', action='store_true', help='Print the full index')
    parser.add_argument('--remove', type=str, help='Remove a keyword from the index')
    args = parser.parse_args()

    if args.list:
        print(json.dumps(get_index(), ensure_ascii=False, indent=2))
    elif args.remove:
        removed = remove_keyword(args.remove)
        print(f"[INDEX] Removed: {removed}")
    else:
        parser.print_help()
