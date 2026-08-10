from ..state import Message
from ..storage import save_messages, load_messages, save_note


def test_save_and_load_messages_round_trip(tmp_path):
    path = tmp_path / "session.jsonl"

    original = [
        Message(role="user", content="hello", timestamp="2026-07-10 10:00"),
        Message(role="assistant", content="hi", timestamp="2026-07-10 10:01")
    ]

    save_messages(original, path)
    loaded = load_messages(path)

    assert loaded == original

def test_save_note_creates_markdown_file(tmp_path):
    path = save_note(
        question="How should I test piped input?",
        answer="Useful answer.",
        title="Piped input testing",
        note_dir=tmp_path,
        prompt_mode="debug",
    )
    
    assert path.name == "piped-input-testing.md"

    content = path.read_text(encoding="utf-8")

    assert "# Piped input testing" in content
    assert "Mode: debug" in content
    assert "## Question" in content
    assert "How should I test piped input?" in content
    assert "## Answer" in content
    assert "Useful answer." in content