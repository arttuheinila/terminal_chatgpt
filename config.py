from dataclasses import dataclass
from pathlib import Path
import tomllib
import os

PROJECT_DIR = Path(
    os.getenv("TGPT_PROJECT_DIR", Path(__file__).resolve().parent)
)

@dataclass
class OpenAIConfig:
    model: str


@dataclass
class StorageConfig:
    session_dir: Path
    note_dir: Path


@dataclass
class TruncationConfig:
    max_messages: int
    max_stdin_chars: int
    stdin_head_chars: int
    stdin_tail_chars: int


@dataclass
class PromptMode:
    system: str


@dataclass
class AppConfig:
    openai: OpenAIConfig
    storage: StorageConfig
    truncation: TruncationConfig
    prompts: dict[str, PromptMode]

class ConfigError(ValueError):
    """Raised when tgpt configuration contains an unsuable value..."""

def validate_config(config: AppConfig) -> None:
    """Raise ConfigError when configuration values are incompatible with tgpt."""

    if not config.openai.model.strip():
        raise ConfigError("openai.model must not be empty.")

    if "default" not in config.prompts:
        raise ConfigError("A [prompts.default] section is required.")

    for name, prompt in config.prompts.items():
        if not prompt.system.strip():
            raise ConfigError(f"Prompt mode '{name}' must define a non-empty system prompt.")

    truncation = config.truncation

    if truncation.max_messages <= 0:
        raise ConfigError("truncation.max_messages must be greater than zero.")

    if truncation.max_stdin_chars <= 0:
        raise ConfigError("truncation.max_stdin_chars must be greater than zero.")

    if truncation.stdin_head_chars < 0:
        raise ConfigError("truncation.stdin_head_chars must not be negative.")

    if truncation.stdin_tail_chars < 0:
        raise ConfigError("truncation.stdin_tail_chars must not be negative.")

    if truncation.stdin_head_chars + truncation.stdin_tail_chars > truncation.max_stdin_chars:
        raise ConfigError(
            "truncation.stdin_head_chars + truncation.stdin_tail_chars "
            "must not exceed truncation.max_stdin_chars."
        )

    for label, directory in {
        "storage.session_dir": config.storage.session_dir,
        "storage.note_dir": config.storage.note_dir,
    }.items():
        if directory.exists() and not directory.is_dir():
            raise ConfigError(f"{label} must be a directory: {directory}")
    
def load_config(path: str | Path | None = None) -> AppConfig:
    if path is None:
        config_path = PROJECT_DIR / "config.toml"
    else:
        config_path = Path(path)
        if not config_path.is_absolute():
            config_path = PROJECT_DIR / config_path

    if not config_path.exists():
        if path is None:
            config_path = PROJECT_DIR / "config.toml.example"
        else:
            raise FileNotFoundError(config_path)

    with config_path.open("rb") as file:
        raw = tomllib.load(file)

    prompts = {
        name: PromptMode(system=value["system"].strip())
        for name, value in raw["prompts"].items()
    }

    storage_base = config_path.parent

    session_dir=Path(raw["storage"]["session_dir"])
    if not session_dir.is_absolute():
        session_dir = storage_base / session_dir

    note_dir=Path(raw["storage"]["note_dir"])
    if not note_dir.is_absolute():
        note_dir = storage_base / note_dir

    config = AppConfig(
        openai=OpenAIConfig(
            model=raw["openai"]["model"],
        ),
        storage=StorageConfig(
            session_dir=session_dir,
            note_dir=note_dir,
        ),
        truncation=TruncationConfig(
            max_messages=raw["truncation"]["max_messages"],
            max_stdin_chars=raw["truncation"]["max_stdin_chars"],
            stdin_head_chars=raw["truncation"]["stdin_head_chars"],
            stdin_tail_chars=raw["truncation"]["stdin_tail_chars"],
        ),
        prompts=prompts,
    )

    validate_config(config)
    return config