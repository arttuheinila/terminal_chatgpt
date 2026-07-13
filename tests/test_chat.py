from ..chat import build_openai_messages
from ..config import AppConfig, OpenAIConfig, StorageConfig, TruncationConfig, PromptMode
from ..state import Message, SessionState
from pathlib import Path

def fake_config() -> AppConfig:
    return AppConfig(
        openai=OpenAIConfig(model="test-model"),
        storage=StorageConfig(
            session_dir=Path("sessions"),
            note_dir=Path("notes"),
        ),
        truncation=TruncationConfig(
            max_messages=8,
            max_stdin_chars=16000,
            stdin_head_chars=10000,
            stdin_tail_chars=4000,
        ),
        prompts={
            "default": PromptMode(system="Default system prompt."),
            "debug": PromptMode(system="Debug system prompt.")
        },
    )

def test_build_openai_message_order():
    state = SessionState(
        messages=[],
        prompt_mode="debug",
        reused_context=[
            Message(role="user", content="old question"),
            Message(role="assistant", content="old answer"),
        ],
    )

    messages = build_openai_messages(
        state=state,
        config=fake_config(),
        user_input="new question",
        include_history=True,
    )

    assert messages == [
        {"role": "system", "content": "Debug system prompt."},
        {"role": "user", "content": "old question"},
        {"role": "assistant", "content": "old answer"},
        {"role": "user", "content": "new question"},
    ]