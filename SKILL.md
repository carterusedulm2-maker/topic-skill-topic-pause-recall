---
name: topic-pause-recall
description: >
  暫停對話任務並未來召回。當用戶說「先這樣」「繼續 XXX」
  「停了哪些任務」時自動觸發。通用框架，不含任何本地任務資訊。
user-invocable: true
allowed-tools: "Read, Write, Bash, process"

hooks:
  UserPromptSubmit:
    - name: pause-recall-hook
      type: command
      command: |
        INPUT="$1"
        SCRIPT_DIR="$HOME/.openclaw/workspace/skills/topic-pause-recall/scripts"
        
        # Pause 偵測
        if echo "$INPUT" | grep -iqE '^(先這樣|先到此為止|先暫停|我之後再回來|先去做別的事)'; then
          echo "[topic-pause-recall] PAUSE detected"
        fi
        
        # List 偵測
        if echo "$INPUT" | grep -iqE '停了哪些|列出.*暂停|目前.*暂停|暂停.*話題|有什麼任務'; then
          echo "[topic-pause-recall] LIST detected"
          python3 "$SCRIPT_DIR/list.py"
        fi
        
        # Recall 偵測
        if echo "$INPUT" | grep -iqE '^繼續\s+'; then
          KEYWORD=$(echo "$INPUT" | sed 's/^繼續\s*//' | awk '{print $1}')
          echo "[topic-pause-recall] RECALL keyword=$KEYWORD"
          python3 "$SCRIPT_DIR/recall.py" --keyword "$KEYWORD"
        fi

tools:
  pause:
    description: 暂停當前任務（需指定 keyword 和 title）
    args:
      - name: keyword
        type: string
        required: true
        description: 召回關鍵字（如 "代碼審查"）
      - name: title
        type: string
        required: true
        description: 任務標題
      - name: phase
        type: string
        required: false
      - name: percent
        type: integer
        required: false
      - name: desc
        type: string
        required: false

  recall:
    description: 根據關鍵字恢復任務
    args:
      - name: keyword
        type: string
        required: true

  list:
    description: 列出所有暂停任務
    args: []

  cleanup:
    description: 清理超期任務
    args:
      - name: days
        type: integer
        required: false
