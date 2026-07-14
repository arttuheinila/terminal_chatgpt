from ..state import Message
from ..truncation import truncate_messages, truncate_text

def test_truncate_messages_return_tail():
    messages = [
        Message(role="user", content="1"),
        Message(role="assistant", content="2"),
        Message(role="user", content="3"),
    ]

    result = truncate_messages(messages, limit=2)

    assert [message.content for message in result] == ["2", "3"]

def test_truncate_messages_with_zero_limit_returns_empty_list():
    messages = [
        Message(role="user", content="1"),
        Message(role="assistant", content="2"),
    ]

    assert truncate_messages(messages, limit=0) == []

def test_truncate_text_keeps_short_text_unchanged():
    assert truncate_text("hello", max_chars=10, head_chars=4, tail_chars=4) == "hello"

def test_truncate_text_adds_marker():
    text = "abcdefghijklmnopqrstuvwxyz"

    result = truncate_text(
        text,
        max_chars=10,
        head_chars=5,
        tail_chars=5,
    )

    assert result.startswith("abcde")
    assert result.endswith("vwxyz")
    assert "--- INPUT TRUNCATED ---" in result