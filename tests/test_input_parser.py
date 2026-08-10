from ..input_parser import parse_user_input

def test_parse_normal_chat_message():
    parsed = parse_user_input("what is docker compose?")

    assert parsed.type == "chat"
    assert parsed.content == "what is docker compose?"

def test_parse_exit():
    parsed = parse_user_input("exit")

    assert parsed.type == "exit"

def test_parse_save_history_short_command():
    parsed = parse_user_input("sh my-session.jsonl")

    assert parsed.type == "save_history"
    assert parsed.filename == "my-session.jsonl"

def test_parse_load_history_full_short_command():
    parsed = parse_user_input("lhf old-session.jsonl")

    assert parsed.type == "load_history_full"
    assert parsed.filename == "old-session.jsonl"


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

    