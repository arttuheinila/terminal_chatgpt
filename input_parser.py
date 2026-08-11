"""Convert one line of interactive terminal input into a command object."""

from dataclasses import dataclass
from typing import Literal

CommandType = Literal[
    "exit",
    "load_current_full",
    "load_current_truncated",
    "load_history_full",
    "load_histtory_truncated",
    "save_history",
    "set_prompt_mode",
    "list_prompt_modes",
    "chat",
    "help",
    "save_note"
]

@dataclass
class ParsedInput:
    """Normalized data required to execute one interactive command."""

    type: CommandType
    content: str = ""
    filename: str | None = None
    mode_name: str | None = None
    note_title: str | None = None

def parse_user_input(raw: str) -> ParsedInput:
    """Recognize supported commands; treat all other text as a chat message."""

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

    if lower in {"modes", "mode list"}:
        return ParsedInput(type="list_prompt_modes")

    if lower.startswith("mode "):
        mode_name = text[len("mode "):].strip()
        return ParsedInput(type="set_prompt_mode", mode_name=mode_name)

    if lower.startswith("m "):
        mode_name = text[len("m "):].strip()
        return ParsedInput(type="set_prompt_mode", mode_name=mode_name)

    if lower == "note" or lower.startswith("note "):
        note_title = text[len("note"):].strip()
        return ParsedInput(type="save_note", note_title=note_title)

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
  note <title>                          Save the latest assistant reply as Markdown

  modes | mode list                     List configured prompt modes
  mode <name> [message] | m <name> [message]
                                        Switch the prompt mode; optionally send a message
""".strip())
