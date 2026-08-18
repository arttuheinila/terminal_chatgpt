"""Read and write session transcripts and user-selected Markdown notes."""

import json
from pathlib import Path
from datetime import datetime
from .state import Message
from .config import AppConfig
import re
from dataclasses import dataclass

@dataclass
class NoteSearchResult:
    path: Path
    title: str
    snippet: str
    score: int

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

def note_title(content:str, path: Path) -> str:
    first_line = content.splitlines()[0] if content else ""
    if first_line.startswith("# "):
        return first_line[2:].strip()

    return path.stem

def note_snippet(content: str, query: str, limit: int = 180) -> str:
    normalized = " ".join(content.split())
    index = normalized.casefold().find(query.casefold())

    if index == -1:
        return normalized[:limit].rstrip() + "..."

    start = max(0, index -50)
    end = min(len(normalized), index + limit)

    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(normalized) else ""

    return prefix + normalized[start:end].strip() + suffix


def search_notes(
        query: str,
        note_dir: str | Path,
        limit: int = 10,
) -> list[NoteSearchResult]:
    note_dir = Path(note_dir)
    normalized_query = " ".join(query.casefold().split())
    terms = normalized_query.split()

    if not normalized_query or not note_dir.exists():
        return []

    results: list[NoteSearchResult] = []

    for path in note_dir.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        normalized_content = content.casefold()
        title = note_title(content, path)
        normalized_title = title.casefold()

        #Require every search word to occur somewhere in the note
        if not all(term in normalized_content for term in terms):
            continue

        score = sum(normalized_content.count(term) for term in terms)

        #Prefer exact phrase matches and title matches.
        if normalized_query in normalized_content:
            score += 10
        if normalized_query in normalized_title:
            score += 20

        results.append(
            NoteSearchResult(
                path=path,
                title=title,
                snippet=note_snippet(content, normalized_query),
                score=score,
            )
        )

    return sorted(results, key=lambda result: result.score, reverse=True)[:limit]

def list_notes(note_dir: str | Path) -> list[Path]:
    note_dir = Path(note_dir)

    if not note_dir.exists():
        return []

    return sorted(
        note_dir.glob("*.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

def load_note(name: str, note_dir: str | Path) -> tuple[Path, str] | None:
    if "/" in name or "\\" in name or ".." in name:
        return None

    filename = name if name.endswith(".md") else f"{name}.md"
    path = Path(note_dir) / filename

    if not path.is_file():
        return None

    return path, path.read_text(encoding="utf-8")
