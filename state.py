"""Data structures representing a chat transcript and its active state."""

from dataclasses import dataclass, field
from typing import Literal

MessageRole = Literal["user", "assistant", "system"]

@dataclass
class Message:
    """A single chat message stored locally or sent to the API."""

    role: MessageRole
    content: str
    timestamp: str | None = None

@dataclass
class SessionState:
    """Mutable state for the currently running terminal session."""

    # Full local transcript. It is persisted to JSONL after successful replies.
    messages: list[Message] = field(default_factory=list)
    active_session_path: str | None = None
    prompt_mode: str = "default"
    # Explicitly selected messages included with the next API request.
    reused_context: list[Message] = field(default_factory=list)
    # The latest completed exchange is available to the ``note`` command.
    last_assistant_reply: str | None = None
    last_user_message: str | None = None
