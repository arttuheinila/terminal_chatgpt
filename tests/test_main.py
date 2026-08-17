from pathlib import Path

from ..config import AppConfig, OpenAIConfig, PromptMode, StorageConfig, TruncationConfig
from ..main import handle_command
from ..input_parser import parse_user_input
from ..state import Message, SessionState
from ..storage import save_messages, save_note
from argparse import Namespace
from io import StringIO
from .. import main



def fake_config() -> AppConfig:
    return AppConfig(
        openai=OpenAIConfig(model="test-model"),
        storage=StorageConfig(session_dir=Path("sessions"), note_dir=Path("notes")),
        truncation=TruncationConfig(
            max_messages=8,
            max_stdin_chars=16000,
            stdin_head_chars=10000,
            stdin_tail_chars=4000,
        ),
        prompts={
            "default": PromptMode(system="Default prompt."),
            "debug": PromptMode(system="Debug prompt."),
        },
    )


def test_mode_command_selects_a_configured_prompt_mode(capsys):
    state = SessionState(prompt_mode="default")

    handle_command(state, fake_config(), parse_user_input("mode debug"))

    assert state.prompt_mode == "debug"
    assert capsys.readouterr().out == "Prompt mode set to: debug\n"


def test_mode_command_rejects_unknown_modes(capsys):
    state = SessionState(prompt_mode="default")

    handle_command(state, fake_config(), parse_user_input("mode missing"))

    assert state.prompt_mode == "default"
    assert capsys.readouterr().out == (
        "Unknown mode: missing\nAvailable modes: debug, default\n"
    )


def test_mode_command_can_send_an_inline_message(monkeypatch, capsys):
    state = SessionState(prompt_mode="default")
    monkeypatch.setattr("tgpt.main.call_openai", lambda **_: "Reply")

    handle_command(
        state,
        fake_config(),
        parse_user_input("mode debug explain the error"),
    )

    assert state.prompt_mode == "debug"
    assert state.messages[0].content == "explain the error"
    assert state.messages[1].content == "Reply"
    assert capsys.readouterr().out == "Prompt mode set to: debug\nChatGPT: Reply\n"


class PipeInput(StringIO):
    def isatty(self):
        return False


def test_piped_input_uses_selected_mode(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        main,
        "parse_args",
        lambda: Namespace(
            mode="debug",
            question=["What", "is", "wrong?"],
        ),
    )
    monkeypatch.setattr(main.sys, "stdin", PipeInput("error log text"))

    def fake_handle_chat_message(state, config, user_input):
        captured["mode"] = state.prompt_mode
        captured["input"] = user_input

    monkeypatch.setattr(main, "handle_chat_message", fake_handle_chat_message)

    main.main()

    assert captured["mode"] == "debug"
    assert captured["input"] == (
        "Task:\n"
        "What is wrong?\n\n"
        "Input:\n"
        "error log text"
    )

def test_note_command_saves_latest_reply(tmp_path, capsys):
    state = SessionState(
        prompt_mode="debug",
        last_user_message="How should I test piped input?",
        last_assistant_reply="Useful answer.",
    )
    config = fake_config()
    config.storage.note_dir = tmp_path

    handle_command(
        state,
        config,
        parse_user_input("note useful answer"),
    )

    assert (tmp_path / "useful-answer.md").exists()
    assert "Saved note:" in capsys.readouterr().out


def test_history_load_adds_context_without_replacing_current_session(tmp_path, capsys):
    history_path = tmp_path / "previous.jsonl"
    previous_messages = [Message(role="user", content="Previous question")]
    save_messages(previous_messages, history_path)

    current_messages = [Message(role="user", content="Current question")]
    state = SessionState(
        messages=current_messages,
        active_session_path="sessions/current.jsonl",
    )

    handle_command(
        state,
        fake_config(),
        parse_user_input(f"history load {history_path}"),
    )

    assert state.messages == current_messages
    assert state.active_session_path == "sessions/current.jsonl"
    assert state.reused_context == previous_messages
    assert "as conversation context" in capsys.readouterr().out


def test_history_save_as_keeps_the_active_session_path(tmp_path, capsys):
    export_path = tmp_path / "copy.jsonl"
    state = SessionState(
        messages=[Message(role="user", content="Current question")],
        active_session_path="sessions/current.jsonl",
    )

    handle_command(
        state,
        fake_config(),
        parse_user_input(f"history save-as {export_path}"),
    )

    assert export_path.exists()
    assert state.active_session_path == "sessions/current.jsonl"
    assert "Saved a copy" in capsys.readouterr().out

def test_notes_list_prints_saved_notes(tmp_path, capsys):
    config = fake_config()
    config.storage.note_dir = tmp_path

    save_note(
        question="Question",
        answer="Answer",
        title="Piped input testing",
        note_dir=tmp_path,
        prompt_mode="debug",
    )

    handle_command(
        SessionState(),
        config,
        parse_user_input("notes list"),
    )

    output = capsys.readouterr().out

    assert "Saved notes:" in output
    assert "piped-input-testing.md" in output
    assert "Piped input testing" in output

def test_notes_list_reports_when_no_notes_exist(tmp_path, capsys):
    config = fake_config()
    config.storage.note_dir = tmp_path

    handle_command(
        SessionState(),
        config,
        parse_user_input("notes list"),
    )

    assert capsys.readouterr().out == "No saved notes found.\n"

def test_notes_show_prints_note_content(tmp_path, capsys):
    config = fake_config()
    config.storage.note_dir = tmp_path

    save_note(
        question="How should I test piped input?",
        answer="Use printf first.",
        title="Piped input testing",
        note_dir=tmp_path,
        prompt_mode="debug",
    )

    handle_command(
        SessionState(),
        config,
        parse_user_input("notes show piped-input-testing"),
    )

    output = capsys.readouterr().out

    assert "# Piped input testing" in output
    assert "How should I test piped input?" in output
    assert "Use printf first." in output

def test_notes_show_reports_missing_note(tmp_path, capsys):
    config = fake_config()
    config.storage.note_dir = tmp_path

    handle_command(
        SessionState(),
        config,
        parse_user_input("notes show missing-note"),
    )

    assert capsys.readouterr().out == "No note found: missing-note\n"

