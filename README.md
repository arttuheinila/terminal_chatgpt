# tgpt

`tgpt` is a terminal-first OpenAI assistant for short chats, one-shot analysis
of piped input, and a small local knowledge base made from Markdown notes.

It keeps its data local: chat transcripts are stored as JSONL files and saved
notes remain ordinary, readable Markdown files.

## Features

- Interactive chat with configurable prompt modes
- One-shot piped input for logs, diffs, and text files
- Safe truncation of large piped input, with a warning on stderr
- Optional `--no-save` mode for sensitive piped input
- Automatic local JSONL chat transcripts
- Curated Markdown notes containing the latest question and answer
- Local note listing, display, and keyword search
- Explicit use of one selected note as context for the next request
- Full or recent context selection for the current chat session
- Configuration validation and storage paths resolved relative to `config.toml`

## Setup

The project requires Python 3.11+ and an OpenAI API key.

Create a `.env` file in the project directory:

```text
API_KEY=your_api_key_here
```

Copy and adjust the example configuration if needed:

```bash
cp config.toml.example config.toml
```

The `[storage]` paths in `config.toml` are relative to that configuration file,
so `sessions` and `notes` remain in the project directory even when `tgpt` is
launched elsewhere.

## Usage

Start an interactive chat:

```bash
tgpt
```

Choose a prompt mode:

```text
modes
mode debug
mode via_negativa How can I simplify this?
```

Analyze piped input in a one-shot request:

```bash
git diff | tgpt --review
journalctl -xe --no-pager | tgpt --debug "What is likely wrong?"
cat essay.md | tgpt --rewrite "Make clearer while preserving tone."
```

Avoid creating a JSONL transcript for a sensitive piped request:

```bash
git diff | tgpt --review --no-save
```

## Notes

After receiving an answer in interactive chat, save the latest question and
answer as a Markdown note:

```text
note piped-input-testing
```

Browse and search saved notes:

```text
notes list
notes search piped input
notes show piped-input-testing
```

Select a note as context for the next chat request:

```text
notes use piped-input-testing
```

`notes use` does not send a request itself. Note searches never add content to
AI context automatically.

## Current-session context

Use the current conversation as context for a later message in the same
interactive session:

```text
context full
context recent
```

`context recent` keeps only the recent messages, which is useful when limiting
request size and cost.

## Storage model

```text
sessions/*.jsonl   Automatic raw chat transcripts
notes/*.md         Curated question-and-answer notes
```

Sessions are a local archive. Notes are the reusable, searchable layer of the
tool.

## Architecture

```text
cli.py          Parses CLI flags for one-shot piped requests
input_parser.py Parses commands entered during interactive chat
main.py         Coordinates application flow, state, chat, and storage
chat.py         Builds API messages and calls the OpenAI API
config.py       Loads and validates TOML configuration
state.py        Defines chat-message and session-state data structures
storage.py      Stores JSONL transcripts and Markdown notes
truncation.py   Limits large piped input before it is sent to the API
```

## Verification

Run the automated test suite:

```bash
pytest -q
```

## Possible future enhancement

If a larger note collection makes file-based search too slow or limited, a
rebuildable SQLite FTS index could accelerate search while keeping Markdown
notes as the source of truth.
