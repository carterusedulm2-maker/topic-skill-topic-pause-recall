#!/usr/bin/env python3
"""forget.py — Delete a paused task, optionally clearing related files."""
import json
import os
import shutil
import argparse

MEMORY_DIR = os.environ.get(
    'OPENCLAW_MEMORY_DIR',
    os.path.expanduser('~/.openclaw/workspace/memory')
)
PAUSED_DIR = os.path.join(MEMORY_DIR, 'paused', 'paused-tasks')
INDEX_FILE = os.path.join(MEMORY_DIR, 'paused', 'index.json')


def forget_task(keyword_or_id: str, clear_dir: str = None, clear_memory: list = None) -> bool:
    """
    Delete a paused task.

    Args:
        keyword_or_id: keyword or task id to match
        clear_dir: optional workspace subdir to remove (e.g. 'news-dashboard')
        clear_memory: optional list of memory filenames to remove
    """
    if not os.path.exists(INDEX_FILE):
        print(f"[FORGET] No tasks paused yet.")
        return False

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)

    task_file = None
    found_keyword = None

    # Match by keyword or task id prefix
    for kw, rel_path in list(index["keywords"].items()):
        if kw == keyword_or_id or keyword_or_id.startswith(kw):
            task_file = os.path.join(MEMORY_DIR, 'paused', rel_path)
            found_keyword = kw
            break

    if not task_file or not os.path.exists(task_file):
        print(f"[FORGET] Task not found: {keyword_or_id}")
        return False

    # Read task to get id before deleting
    with open(task_file, 'r', encoding='utf-8') as f:
        task = json.load(f)

    # Remove task file
    os.remove(task_file)

    # Remove from index
    del index["keywords"][found_keyword]
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    # Remove associated workspace directory
    if clear_dir:
        dir_path = os.path.join(os.path.expanduser('~/.openclaw/workspace'), clear_dir)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"[FORGET] Removed directory: {dir_path}")

    # Remove associated memory files
    if clear_memory:
        for mem_file in clear_memory:
            mem_path = os.path.join(MEMORY_DIR, mem_file)
            if os.path.exists(mem_path):
                os.remove(mem_path)
                print(f"[FORGET] Removed memory: {mem_path}")

    print(f"[FORGET] Removed task: {found_keyword} (id={task['id']})")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a paused task.")
    parser.add_argument('--keyword', required=True, help="Keyword or task id to forget")
    parser.add_argument('--clear-dir', type=str,
                        help="Workspace subdir to remove (e.g. news-dashboard)")
    parser.add_argument('--clear-memory', nargs='+',
                        help="Memory files to remove (e.g. earnings-automation.md)")
    args = parser.parse_args()

    forget_task(args.keyword, args.clear_dir, args.clear_memory)
