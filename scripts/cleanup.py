#!/usr/bin/env python3
"""cleanup.py — 清理超期任務（預設>30天）"""
import json, os, sys
from datetime import datetime, timezone, timedelta

MEMORY_DIR = os.environ.get('OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory'))
PAUSED_DIR = os.path.join(MEMORY_DIR, 'paused', 'paused-tasks')
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')
MAX_AGE_DAYS = 30

def cleanup(days: int = MAX_AGE_DAYS) -> list:
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
            # 超過30天且狀態不是 completed/abandoned 的任務
            if 'completed' not in task.get('status') and 'abandoned' not in task.get('status'):
                paused_dt = datetime.fromisoformat(task.get('pausedAt', '').replace('Z', '+00:00'))
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=30)
    args = parser.parse_args()
    cleanup(args.days)
