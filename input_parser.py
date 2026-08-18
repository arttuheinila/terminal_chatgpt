"""Convert one line of interactive terminal input into a command object."""

from dataclasses import dataclass
from typing import Literal

CommandType = Literal[
    "exit",
    "context_full",
    "context_recent",
    "history_load",
    "history_save_as",
    "set_prompt_mode",
    "list_prompt_modes",
    "chat",
    "help",
    "save_note"
    "search_notes"
    "list_notes",
    "show_note",
    "use_note"
]

@dataclass
class ParsedInput:
    """Normalized data required to execute one interactive command."""

    type: CommandType
    content: str = ""
    filename: str | None = None
    mode_name: str | None = None
    note_title: str | None = None
    search_query: str | None = None
    note_name: str | None = None

def parse_user_input(raw: str) -> ParsedInput:
    """Recognize supported commands; treat all other text as a chat message."""

    text = raw.strip()
    lower = text.lower()

    if lower == "exit":
        return ParsedInput(type="exit")

    if lower == "q":
        return ParsedInput(type="exit")
    
    if lower in {"help", "h", "?"}:
        return ParsedInput(type="help")
    
    if lower == "context full":
        return ParsedInput(type="context_full")

    if lower == "context recent":
        return ParsedInput(type="context_recent")

    if lower.startswith("history load "):
        filename = text[len("history load "):].strip()
        return ParsedInput(type="history_load", filename=filename)

    if lower.startswith("history save-as "):
        filename = text[len("history save-as "):].strip()
        return ParsedInput(type="history_save_as", filename=filename)

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

    if lower.startswith("notes search"):
        search_query = text[len("notes search "):].strip()
        return ParsedInput(type="search_notes", search_query=search_query)

    if lower.startswith("search notes"):
        search_query = text[len("search notes"):].strip()
        return ParsedInput(type="search_notes", search_query=search_query)

    if lower == "notes list":
        return ParsedInput(type="list_notes")

    if lower == "notes show" or lower.startswith("notes show "):
        note_name = text[len("notes show "):].strip()
        return ParsedInput(type="show_note", note_name=note_name)

    if lower.startswith("notes use "):
        note_name = text[len("notes use "):].strip()
        return ParsedInput(type="use_note", note_name=note_name)

    return ParsedInput(type="chat", content=text)
    
def print_help() -> None:
    print("""
Commands:
  exit                                  Exit and save current session
  help | h | ?                           Show this help

  history load <file>                   Load a past session as conversation context
  history save-as <file>                Save a named copy of the current session
  context full                          Use all current-session messages as context
  context recent                        Use recent current-session messages as context

  note <title>                          Save the latest assistant reply as Markdown
  notes search <query>                  Search local Markdown notes
  notes list                            List saved Markdown notes
  notes show <name>                     Display one saved Markdown note
  notes use <name>                      Use one Markdown note as next-request context

  modes | mode list                     List configured prompt modes
  mode <name> [message] | m <name> [message]
                                        Switch the prompt mode; optionally send a message
""".strip())
