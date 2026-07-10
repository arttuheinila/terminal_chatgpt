from dataclasses import dataclass
from pathlib import Path
import tomllib


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


def load_config(path: str | Path = "config.toml") -> AppConfig:
    path = Path(path)

    if not path.exists():
        path = Path("config.toml.example")

    with path.open("rb") as file:
        raw = tomllib.load(file)

    prompts = {
        name: PromptMode(system=value["system"].strip())
        for name, value in raw["prompts"].items()
    }

    return AppConfig(
        openai=OpenAIConfig(
            model=raw["openai"]["model"],
        ),
        storage=StorageConfig(
            session_dir=Path(raw["storage"]["session_dir"]),
            note_dir=Path(raw["storage"]["note_dir"]),
        ),
        truncation=TruncationConfig(
            max_messages=raw["truncation"]["max_messages"],
            max_stdin_chars=raw["truncation"]["max_stdin_chars"],
            stdin_head_chars=raw["truncation"]["stdin_head_chars"],
            stdin_tail_chars=raw["truncation"]["stdin_tail_chars"],
        ),
        prompts=prompts,
    )