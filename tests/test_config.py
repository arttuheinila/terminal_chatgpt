from ..config import load_config, PROJECT_DIR

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