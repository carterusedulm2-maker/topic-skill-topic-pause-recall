#!/usr/bin/env python3
"""recall.py — Restore a paused task by keyword."""
import json
import os
import sys
from datetime import datetime, timezone

MEMORY_DIR = os.environ.get(
    'OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory')
)
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')


def recall_task(keyword: str) -> dict:
    """Load a paused task from disk and mark it as accessed.

    Args:
        keyword: The keyword the task was registered with.

    Returns:
        The task dict if found, otherwise None.
    """
    if not os.path.exists(INDEX_FILE):
        print("[RECALL] No tasks paused yet")
        return None

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)

    keywords = index.get("keywords", {})
    if keyword.lower() not in keywords:
        print(f"[RECALL] keyword '{keyword}' not found. Available: {list(keywords.keys())}")
        return None

    rel_path = keywords[keyword.lower()]
    task_path = os.path.join(MEMORY_DIR, 'paused', rel_path)

    if not os.path.exists(task_path):
        print(f"[RECALL] Task file not found: {task_path}")
        return None

    with open(task_path, 'r', encoding='utf-8') as f:
        task = json.load(f)

    # Update lastAccessedAt to track usage
    task["lastAccessedAt"] = datetime.now(timezone.utc).isoformat()
    with open(task_path, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    print(f"[RECALL] Restored: {task['title']} (keyword={keyword}, phase={task.get('phase')})")
    print(f"[RECALL] Progress: {task['progress']['percent']}% — {task['progress']['description']}")
    print(f"[RECALL] Next steps: {task.get('nextSteps', [])}")
    return task


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Restore a paused task by keyword.")
    parser.add_argument('--keyword', required=True, help="Recall keyword")
    args = parser.parse_args()
    recall_task(args.keyword)
