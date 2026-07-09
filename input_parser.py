#turns raw text into command objects

from dataclasses import dataclass
from typing import Literal

CommandType = Literal[
    "exit",
    "load_current_full",
    "load_current_truncated",
    "load_history_full",
    "load_histtory_truncated",
    "save_history",
    "chat",
    "help",
]

@dataclass
class ParsedInput:
    type: CommandType
    content: str = ""
    filename: str | None = None

def parse_user_input(raw: str) -> ParsedInput:
    text = raw.strip()
    lower = text.lower()

    if lower == "exit":
        return ParsedInput(type="exit")
    
    if lower in {"help", "h", "?"}:
        return ParsedInput(type="help")
    
    if lower in {"load current history full", "lchf"}:
        return ParsedInput(type="load_current_full")
    
    if lower in {"load current history truncated", "lcht"}:
            return ParsedInput(type="load_current_truncated")

    if lower.startswith("load history full "):
        filename = text[len("load history full "):].strip()
        return ParsedInput(type="load_history_full", filename=filename)

    if lower.startswith("lhf "):
        filename = text[len("lhf "):].strip()
        return ParsedInput(type="load_history_full", filename=filename)

    if lower.startswith("load history truncated "):
        filename = text[len("load history truncated "):].strip()
        return ParsedInput(type="load_history_truncated", filename=filename)

    if lower.startswith("lht "):
        filename = text[len("lht "):].strip()
        return ParsedInput(type="load_history_truncated", filename=filename)

    if lower.startswith("save history "):
        filename = text[len("save history "):].strip()
        return ParsedInput(type="save_history", filename=filename)

    if lower.startswith("sh "):
        filename = text[len("sh "):].strip()
        return ParsedInput(type="save_history", filename=filename)

    return ParsedInput(type="chat", content=text)
    
def print_help() -> None:
    print("""
Commands:
  exit                                  Exit and save current session
  help | h | ?                           Show this help

  load current history full | lchf       Reuse all current session messages as context
  load current history truncated | lcht  Reuse recent current session messages as context

  load history full <filename> | lhf <filename>
  load history truncated <filename> | lht <filename>

  save history <filename> | sh <filename>
""".strip())