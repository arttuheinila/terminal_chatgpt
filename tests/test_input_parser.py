from ..input_parser import parse_user_input

def test_parse_normal_chat_message():
    parsed = parse_user_input("what is docker compose?")

    assert parsed.type == "chat"
    assert parsed.content == "what is docker compose?"

def test_parse_exit():
    parsed = parse_user_input("exit")

    assert parsed.type == "exit"

def test_parse_history_save_as_command():
    parsed = parse_user_input("history save-as my-session.jsonl")

    assert parsed.type == "history_save_as"
    assert parsed.filename == "my-session.jsonl"

def test_parse_history_load_command():
    parsed = parse_user_input("history load old-session.jsonl")

    assert parsed.type == "history_load"
    assert parsed.filename == "old-session.jsonl"


def test_parse_context_commands():
    assert parse_user_input("context full").type == "context_full"
    assert parse_user_input("context recent").type == "context_recent"


def test_parse_set_prompt_mode_command():
    parsed = parse_user_input("mode debug")

    assert parsed.type == "set_prompt_mode"
    assert parsed.mode_name == "debug"


def test_parse_list_prompt_modes_command():
    parsed = parse_user_input("modes")

    assert parsed.type == "list_prompt_modes"

def test_parse_save_note_command():
    parsed = parse_user_input("note piped input testing")

    assert parsed.type == "save_note"
    assert parsed.note_title == "piped input testing"

