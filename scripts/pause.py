#!/usr/bin/env python3
"""pause.py — Save task state to disk."""
import json
import uuid
import os
import sys
from datetime import datetime, timezone

# Directory paths
MEMORY_DIR = os.environ.get(
    'OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory')
)
PAUSED_DIR = os.path.join(MEMORY_DIR, 'paused', 'paused-tasks')
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')


def pause_task(
    keyword: str,
    title: str,
    context: dict = None,
    next_steps: list = None,
    phase: str = "unknown",
    progress_percent: int = 0,
    progress_desc: str = ""
) -> str:
    """Save the current task state to disk and register it in the index.

    Args:
        keyword:     Unique keyword used to recall this task later.
        title:       Human-readable task title.
        context:     Optional dict of additional context to preserve.
        next_steps: Optional list of planned next steps.
        phase:       Current phase label (e.g. "research", "review").
        progress_percent: Estimated completion percentage (0–100).
        progress_desc:    Short description of current progress.

    Returns:
        The generated task ID (first 8 chars of UUID).
    """
    os.makedirs(PAUSED_DIR, exist_ok=True)
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()

    task = {
        "id": task_id,
        "keyword": keyword.lower().strip(),
        "title": title,
        "status": "paused",
        "phase": phase,
        "pausedAt": now,
        "lastAccessedAt": now,
        "pauseCount": 1,
        "progress": {
            "percent": progress_percent,
            "description": progress_desc
        },
        "nextSteps": next_steps or [],
        "context": context or {},
        "conversationSummary": {},
        "attachedFiles": []
    }

    filepath = os.path.join(PAUSED_DIR, f"{task_id}-{keyword}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    # Update keyword index
    update_index(keyword, f"paused-tasks/{task_id}-{keyword}.json")

    print(f"[PAUSED] keyword={keyword} id={task_id}")
    return task_id


def update_index(keyword: str, rel_path: str) -> None:
    """Register (or re-register) a keyword in the global paused-task index."""
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)

    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {"keywords": {}, "lastCleanup": ""}

    index["keywords"][keyword.lower().strip()] = rel_path

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Save a paused task state.")
    parser.add_argument('--keyword', required=True, help="Recall keyword")
    parser.add_argument('--title', required=True, help="Task title")
    parser.add_argument('--phase', default="unknown", help="Current phase")
    parser.add_argument('--percent', type=int, default=0, help="Progress %%")
    parser.add_argument('--desc', default="", help="Progress description")
    args = parser.parse_args()

    pause_task(
        args.keyword,
        args.title,
        phase=args.phase,
        progress_percent=args.percent,
        progress_desc=args.desc
    )
