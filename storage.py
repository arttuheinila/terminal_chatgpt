#save/load session files

import json
from pathlib import Path
from datetime import datetime
from .state import Message
from .config import AppConfig


def generate_default_session_path(config: AppConfig) -> Path:
    sessions_dir = config.storage.session_dir
    sessions_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    num = 0
    while True:
        # Use a monotonically increasing suffix to avoid overwriting existing
        # sessions created on the same day.
        path = sessions_dir / f"{date_str}_{num}.jsonl"
        if not path.exists():
            return path
        num += 1

def save_messages(messages: list[Message], path: str | Path) -> None:
    path = Path(path)
    # Ensure parent directories exist before writing the transcript.
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for message in messages:
            # Write one JSON object per line for easy appends and streaming reads.
            file.write(json.dumps({
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp,
            }, ensure_ascii=False) + "\n")

def load_messages(path: str | Path) -> list[Message]:
    path = Path(path)

    if not path.exists():
        print(f"No chat history found for {path}. Starting a new session.")
        return []
    
    messages: list[Message] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            # Preserve backward compatibility with older session files that may
            # not have a timestamp field.
            data = json.loads(line)
            messages.append(Message(
                role=data["role"],
                content=data["content"],
                timestamp=data.get("timestamp"),
            ))

    return messages