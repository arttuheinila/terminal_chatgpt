from ..state import Message
from ..storage import save_messages, load_messages, save_note, search_notes, list_notes, load_note
import os


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

def test_search_notes_prefers_title_match(tmp_path):
    save_note(
        question="How can I test piped input?",
        answer="Use printf first.",
        title="Piped input testing",
        note_dir=tmp_path,
        prompt_mode="debug",
    )
    save_note(
        question="How should I debug logs?",
        answer="Read the final lines.",
        title="Debugging logs",
        note_dir=tmp_path,
        prompt_mode="debug",
    )

    results = search_notes("piped input", tmp_path)

    assert len(results) == 1
    assert results[0].title == "Piped input testing"

def test_list_notes_returns_markdown_files_newest_first(tmp_path):
    older_path = save_note(
        question="Older question",
        answer="Older answer",
        title="Older note",
        note_dir=tmp_path,
        prompt_mode="default",
    )
    newer_path = save_note(
        question="Newer question",
        answer="Newer answer",
        title="Newer note",
        note_dir=tmp_path,
        prompt_mode="default",
    )

    # Make the intended order deterministic instead of relying on timing.
    os.utime(older_path, (1, 1))
    os.utime(newer_path, (2, 2))

    notes = list_notes(tmp_path)

    assert [path.name for path in notes] == [
        "newer-note.md",
        "older-note.md",
    ]

def test_list_notes_returns_empty_list_when_directory_is_missing(tmp_path):
    notes = list_notes(tmp_path / "missing-notes")

    assert notes == []

def test_load_note_returns_path_and_markdown_content(tmp_path):
    saved_path = save_note(
        question="How should I test piped input?",
        answer="Use printf first.",
        title="Piped input testing",
        note_dir=tmp_path,
        prompt_mode="debug",
    )

    loaded_note = load_note("piped-input-testing", tmp_path)

    assert loaded_note is not None

    path, content = loaded_note

    assert path == saved_path
    assert "# Piped input testing" in content
    assert "How should I test piped input?" in content
    assert "Use printf first." in content

def test_load_note_accepts_filename_with_markdown_extension(tmp_path):
    save_note(
        question="Question",
        answer="Answer",
        title="Test note",
        note_dir=tmp_path,
        prompt_mode="default",
    )

    loaded_note = load_note("test-note.md", tmp_path)

    assert loaded_note is not None
    assert loaded_note[0].name == "test-note.md"

def test_load_note_returns_none_for_missing_or_unsafe_name(tmp_path):
    assert load_note("missing-note", tmp_path) is None
    assert load_note("../outside", tmp_path) is None
    assert load_note("nested/note", tmp_path) is None
    assert load_note(r"nested\note", tmp_path) is None