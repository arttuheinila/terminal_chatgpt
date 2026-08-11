"""Read and write session transcripts and user-selected Markdown notes."""

import json
from pathlib import Path
from datetime import datetime
from .state import Message
from .config import AppConfig
import re

def generate_default_session_path(config: AppConfig) -> Path:
    """Return an unused, date-based path for a new session transcript."""

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
    """Overwrite a JSONL transcript with the supplied ordered messages."""

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
    """Load a JSONL transcript, accepting older entries without timestamps."""

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

def note_slug(title: str) -> str:
    """Convert a human-readable note title into a portable filename stem."""

    normalized = " ".join(title.split()).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "note"

def save_note(
        question: str,
        answer: str,
        title: str,
        note_dir: str | Path,
        prompt_mode: str,
) -> Path:
    """Write one selected question-and-answer exchange as a Markdown note.

    A numeric suffix is added when the requested title already exists, which
    preserves earlier notes rather than overwriting them.
    """

    note_dir = Path(note_dir)
    note_dir.mkdir(parents=True, exist_ok=True)

    base_name = note_slug(title)
    path = note_dir / f"{base_name}.md"

    suffix = 2
    # Avoid data loss when a user saves more than one note with the same title.
    while path.exists():
        path = note_dir / f"{base_name}-{suffix}.md"
        suffix += 1

    created = datetime.now().strftime("%Y-%m-%d %H:%M")
    markdown = (
        f"# {title}\n\n"
        f"Created: {created}\n"
        f"Mode: {prompt_mode}\n\n"
        "## Question\n\n"
        f"{question.rstrip()}\n\n"
        "## Answer\n\n"
        f"{answer.rstrip()}\n"
    )

    path.write_text(markdown, encoding="utf-8")
    return path
