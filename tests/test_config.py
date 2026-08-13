from ..config import (
    load_config, 
    PROJECT_DIR,
    AppConfig,
    ConfigError,
    OpenAIConfig,
    PromptMode,
    StorageConfig,
    TruncationConfig,
    validate_config,
)
from pathlib import Path
import pytest

expected_storage_base = PROJECT_DIR / "tests" / "fixtures"


def test_load_config_from_toml_fixture():
    config = load_config("tests/fixtures/config.toml")

    assert config.openai.model == "test-model"
    assert config.storage.session_dir == (
        expected_storage_base / "test-sessions"
)
    assert config.storage.note_dir == (
    expected_storage_base / "test-notes"
)

    assert config.truncation.max_messages == 4
    assert config.truncation.max_stdin_chars == 1000
    assert config.truncation.stdin_head_chars == 600
    assert config.truncation.stdin_tail_chars == 300

    assert config.prompts["default"].system == "Default prompt."
    assert config.prompts["debug"].system == "Debug prompt."

def test_load_config_from_toml_fixture_independent_of_cwd(monkeypatch):
    monkeypatch.chdir("tests")

    config = load_config("tests/fixtures/config.toml")

    assert config.openai.model == "test-model"
    assert config.storage.session_dir == expected_storage_base / "test-sessions"
    assert config.storage.note_dir == expected_storage_base / "test-notes"

def valid_config() -> AppConfig:
    return AppConfig(
        openai=OpenAIConfig(model="test-model")
        ,
        storage=StorageConfig(
            session_dir=Path("sessions"),
            note_dir=Path("notes")
        ),
        truncation=TruncationConfig(
            max_messages=8,
            max_stdin_chars=12000,
            stdin_head_chars=9000,
            stdin_tail_chars=3000,
        ),
        prompts={
            "default": PromptMode(system="Useful default prompt."),
        },
    )

def test_validate_config_accepts_valid_configurationU():
    validate_config(valid_config())

def test_validate_config_requires_default_prompt():
    config = valid_config()
    config.prompts = {}

    with pytest.raises(ConfigError, match=r"\[prompts\.default\]"):
        validate_config(config)

def test_validate_config_rejects_empty_model():
    config = valid_config()
    config.openai.model = "   "

    with pytest.raises(ConfigError, match="openai.model"):
        validate_config(config)

def test_validate_config_rejects_empty_prompt():
    config = valid_config()
    config.prompts["default"] = PromptMode(system="")

    with pytest.raises(ConfigError, match="non-empty system prompt"):
        validate_config(config)

def test_validate_config_rejects_invalid_stdin_split():
    config = valid_config()
    config.truncation = TruncationConfig(
        max_messages=8,
        max_stdin_chars=12000,
        stdin_head_chars=10000,
        stdin_tail_chars=3001,
    )

    with pytest.raises(ConfigError, match="must not exceed"):
        validate_config(config)

def test_validate_config_rejects_storage_path_that_is_a_file(tmp_path):
    storage_file = tmp_path / "not-a-directory"
    storage_file.write_text("not a directory", encoding="utf-8")

    config = valid_config()
    config.storage = StorageConfig(
        session_dir=storage_file,
        note_dir=tmp_path / "notes",
    )

    with pytest.raises(ConfigError, match="storage.session_dir"):
        validate_config(config)