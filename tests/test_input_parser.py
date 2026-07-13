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