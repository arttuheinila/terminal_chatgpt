from ..state import Message
from ..storage import save_messages, load_messages

def test_save_and_load_messages_round_trip(tmp_path):
    path = tmp_path / "session.jsonl"

    original = [
        Message(role="user", content="hello", timestamp="2026-07-10 10:00"),
        Message(role="assistant", content="hi", timestamp="2026-07-10 10:01")
    ]

    save_messages(original, path)
    loaded = load_messages(path)

    assert loaded == original