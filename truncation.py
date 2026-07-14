# tgpt/truncation.py

from .state import Message


def truncate_messages(messages: list[Message], limit: int) -> list[Message]:
    if limit <= 0:
        return []

    return messages[-limit:]


def truncate_text(
    text: str,
    max_chars: int,
    head_chars: int,
    tail_chars: int,
) -> str:
    if len(text) <= max_chars:
        return text

    head = text[:head_chars]
    tail = text[-tail_chars:]

    return (
        head
        + "\n\n--- INPUT TRUNCATED ---\n\n"
        + tail
    )