# topic-pause-recall

> Pause any long-running agent task and seamlessly resume it later by keyword.

## What It Does

When you're mid-task with an agent and need to step away, `topic-pause-recall` lets you save the exact progress state to disk. When you're ready to continue, just say "continue [keyword]" and the agent picks up right where it left off.

## Features

- **Pause** — Save current task state (goal, params, progress, next steps) to disk
- **Recall** — Resume any paused task by keyword
- **List** — View all paused tasks with status and timestamps
- **Auto-cleanup** — Remove expired tasks (default: 30 days)

## Keywords

| Keyword | What it triggers |
|---------|-----------------|
| `先這樣` / `先暫停` / `先這樣吧` | Pause current task |
| `繼續 <keyword>` | Recall a paused task |
| `停了哪些任務` / `列出暂停` | List all paused tasks |

## Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/carterusedulm2-maker/topic-skill-topic-pause-recall.git ~/.openclaw/workspace/skills/topic-pause-recall
```

### Usage

```bash
# Pause a task
python3 scripts/pause.py --keyword "code-review" --title "Review PR #42" --phase "review" --percent 60 --desc "Finished first pass"

# List all paused tasks
python3 scripts/list.py

# Recall a task
python3 scripts/recall.py --keyword "code-review"

# Cleanup expired tasks
python3 scripts/cleanup.py --days 30
```

## Output Format

List output:
```
📋 Paused Topics
━━━━━━━━━━━━━━━━━━━━━
1. 🔧 code-review   [2026-03-28] 2days ago
   Review PR #42
   60% · Finished first pass
━━━━━━━━━━━━━━━━━━━━━
Say "continue [keyword]" to resume
```

## File Structure

```
topic-pause-recall/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # This file
├── scripts/
│   ├── pause.py         # Save task state
│   ├── recall.py        # Restore by keyword
│   ├── list.py          # Show all paused tasks
│   ├── index.py         # Manage keyword index
│   └── cleanup.py       # Remove expired tasks
└── templates/
    └── paused-task.schema.json
```

## Task State Schema

```json
{
  "id": "a1b2c3d4",
  "keyword": "code-review",
  "title": "Review PR #42",
  "status": "paused",
  "phase": "review",
  "pausedAt": "2026-03-28T09:00:00+08:00",
  "lastAccessedAt": "2026-03-28T09:00:00+08:00",
  "pauseCount": 1,
  "progress": { "percent": 60, "description": "Finished first pass" },
  "nextSteps": ["Address feedback", "Re-review"],
  "context": {},
  "conversationSummary": {},
  "attachedFiles": []
}
```

## Privacy

This skill is a **generic framework**. It stores no task-specific data by default — only the keyword, title, and progress description you provide. No file paths, no secrets, no personal info.
