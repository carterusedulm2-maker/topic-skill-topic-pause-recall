---
name: topic-pause-recall
description: >
  暫停對話任務並未來召回。當用戶說「先這樣」「繼續 XXX」
  「停了哪些任務」時自動觸發。通用框架，不含任何本地任務資訊。
en_description: >
  Pause any long-running agent task and seamlessly resume it later by keyword.
  Automatically triggers when the user says "先這樣" (pause), "繼續 XXX" (recall),
  or "停了哪些任務" (list). A generic framework — stores no task-specific data
  by default, only the keyword, title, and progress description you provide.
user-invocable: true
allowed-tools: "Read, Write, Bash, process"

hooks:
  UserPromptSubmit:
    # Detects pause keywords and saves current task state to disk.
    - name: pause-recall-hook
      type: command
      command: |
        INPUT="$1"
        SCRIPT_DIR="$HOME/.openclaw/workspace/skills/topic-pause-recall/scripts"
        
        # Pause detection
        if echo "$INPUT" | grep -iqE '^(先這樣|先到此為止|先暫停|我之後再回來|先去做別的事)'; then
          echo "[topic-pause-recall] PAUSE detected"
        fi
        
        # List detection
        if echo "$INPUT" | grep -iqE '停了哪些|列出.*暂停|目前.*暂停|暂停.*話題|有什麼任務'; then
          echo "[topic-pause-recall] LIST detected"
          python3 "$SCRIPT_DIR/list.py"
        fi
        
        # Recall detection
        if echo "$INPUT" | grep -iqE '^繼續\s+'; then
          KEYWORD=$(echo "$INPUT" | sed 's/^繼續\s*//' | awk '{print $1}')
          echo "[topic-pause-recall] RECALL keyword=$KEYWORD"
          python3 "$SCRIPT_DIR/recall.py" --keyword "$KEYWORD"
        fi

tools:
  pause:
    # Save the current task state to disk.
    description: Pause the current task (requires keyword and title).
    args:
      - name: keyword
        type: string
        required: true
        description: Unique recall keyword (e.g., "code-review").
      - name: title
        type: string
        required: true
        description: Human-readable task title.
      - name: phase
        type: string
        required: false
        description: Current phase label (e.g., "research", "review").
      - name: percent
        type: integer
        required: false
        description: Estimated completion percentage (0–100).
      - name: desc
        type: string
        required: false
        description: Short description of current progress.

  recall:
    # Load a paused task from disk and mark it as accessed.
    description: Restore a paused task by keyword.
    args:
      - name: keyword
        type: string
        required: true
        description: The keyword the task was registered with.

  list:
    # Print all paused tasks with status, timestamps, and age.
    description: List all paused tasks.
    args: []

  cleanup:
    # Remove tasks older than the specified number of days.
    description: Remove expired paused tasks.
    args:
      - name: days
        type: integer
        required: false
        description: Age threshold in days (default: 30).
