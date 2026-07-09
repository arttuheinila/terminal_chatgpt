#hold session state

from dataclasses import dataclass, field
from typing import Literal

MessageRole = Literal["user", "assistant", "system"]

@dataclass
class Message:
    # A single message exchanged in the chat.
    role: MessageRole
    content: str
    timestamp: str | None = None

@dataclass
class SessionState:
    # Messages currently stored for the active session.
    messages: list[Message] = field(default_factory=list)
    active_session_path: str | None = None
    prompt_mode: str = "default"
    # Previously reused context that can be appended back into the session.
    reused_context: list[Message] = field(default_factory=list)