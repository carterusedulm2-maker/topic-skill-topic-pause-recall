#!/usr/bin/env python3
"""list.py — List all paused tasks with status and timestamps."""
import json
import os
from datetime import datetime, timezone

MEMORY_DIR = os.environ.get(
    'OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory')
)
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')


def get_status_emoji(paused_at: str) -> str:
    """Return an emoji based on how long ago the task was paused."""
    paused_dt = datetime.fromisoformat(paused_at.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    age_days = (now - paused_dt.replace(tzinfo=now.tzinfo)).days
    if age_days < 7:
        return "🔧"
    elif age_days < 30:
        return "⏸️"
    else:
        return "⚠️"


def list_tasks() -> list:
    """Read the index and return a list of all paused tasks."""
    if not os.path.exists(INDEX_FILE):
        return []

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)

    keywords = index.get("keywords", {})
    tasks = []
    for kw, rel_path in keywords.items():
        task_path = os.path.join(MEMORY_DIR, 'paused', rel_path)
        if os.path.exists(task_path):
            with open(task_path, 'r', encoding='utf-8') as f:
                task = json.load(f)
            paused_dt = datetime.fromisoformat(
                task['pausedAt'].replace('Z', '+00:00'))
            age_days = (
                datetime.now(timezone.utc) -
                paused_dt.replace(tzinfo=datetime.now(timezone.utc).tzinfo)
            ).days
            status = get_status_emoji(task['pausedAt'])
            tasks.append({
                "keyword": kw,
                "title": task['title'],
                "status": status,
                "pausedAt": task['pausedAt'][:10],
                "age": f"{age_days}days ago",
                "progress": task.get('progress', {}).get('description', ''),
                "phase": task.get('phase', '')
            })

    return sorted(tasks, key=lambda x: x['pausedAt'], reverse=True)


def format_list(tasks: list) -> str:
    """Format the task list as a human-readable string."""
    if not tasks:
        return "No paused tasks. Say 'continue [keyword]' to resume one."

    lines = ["📋 Paused Topics", "━━━━━━━━━━━━━━━━━━━━━"]
    for i, t in enumerate(tasks, 1):
        lines.append(
            f"{i}. {t['status']} {t['keyword']:<12} [{t['pausedAt']}] {t['age']}"
        )
        lines.append(f"   {t['title']}")
        if t['progress']:
            progress_percent = ""
            # Try to show percent if available in phase/progress
            lines.append(f"   {t['progress']}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append("Say 'continue [keyword]' to resume")
    return "\n".join(lines)


if __name__ == "__main__":
    tasks = list_tasks()
    print(format_list(tasks))
