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

    return AppConfig(
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