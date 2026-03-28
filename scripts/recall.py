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
    parser.add_argument('--forget', action='store_true',
                        help="Forget this task after recalling it")
    args = parser.parse_args()

    task = recall_task(args.keyword)
    if task and args.forget:
        # Remove task file and index entry
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
        if task['keyword'] in index["keywords"]:
            del index["keywords"][task['keyword']]
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        task_path = os.path.join(MEMORY_DIR, 'paused',
                                 index.get("keywords", {}).get(task['keyword'],
                                 f"paused-tasks/{task['id']}-{task['keyword']}.json"))
        # Find actual path from current index state before deletion
        for kw_rel in list(index["keywords"].items()):
            pass
        # Re-derive path from what we know
        rel_path = f"paused-tasks/{task['id']}-{task['keyword']}.json"
        task_path = os.path.join(MEMORY_DIR, 'paused', rel_path)
        if os.path.exists(task_path):
            os.remove(task_path)
        print(f"[RECALL] Task '{task['keyword']}' has been forgotten.")
