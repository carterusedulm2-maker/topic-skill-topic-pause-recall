#!/usr/bin/env python3
"""cleanup.py — Remove expired paused tasks (default: older than 30 days)."""
import json
import os
import sys
from datetime import datetime, timezone

MEMORY_DIR = os.environ.get(
    'OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory')
)
PAUSED_DIR = os.path.join(MEMORY_DIR, 'paused', 'paused-tasks')
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')
MAX_AGE_DAYS = 30


def cleanup(days: int = MAX_AGE_DAYS) -> list:
    """Remove tasks paused longer than `days` and update the index.

    Args:
        days: Age threshold in days. Tasks older than this are removed.

    Returns:
        List of removed keyword strings.
    """
    if not os.path.exists(INDEX_FILE):
        return []

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)

    removed = []
    for kw, rel_path in list(index["keywords"].items()):
        task_path = os.path.join(MEMORY_DIR, 'paused', rel_path)
        if os.path.exists(task_path):
            with open(task_path, 'r', encoding='utf-8') as f:
                task = json.load(f)
            # Skip tasks already marked completed or abandoned
            if 'completed' not in task.get('status') and 'abandoned' not in task.get('status'):
                paused_dt = datetime.fromisoformat(
                    task.get('pausedAt', '').replace('Z', '+00:00')
                )
                age = datetime.now(timezone.utc) - paused_dt.replace(tzinfo=timezone.utc)
                if age.days >= days:
                    os.remove(task_path)
                    del index["keywords"][kw]
                    removed.append(kw)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"[CLEANUP] Removed {len(removed)} expired tasks: {removed}")
    return removed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean up expired paused tasks.")
    parser.add_argument('--days', type=int, default=30, help='Age threshold in days')
    args = parser.parse_args()
    cleanup(args.days)
