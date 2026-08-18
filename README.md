# tgpt

`tgpt` is a small, local-first terminal assistant built around prompt modes,
piped input, saved chat transcripts, and curated Markdown notes. It is
actively under development.

## Current capabilities

- Interactive terminal chat with configurable prompt modes
- One-shot piped input for logs, diffs, and text files
- Automatic local JSONL session transcripts
- Config validation and configuration-relative storage paths
- Saving the latest question and answer as a Markdown note
- Listing, showing, and keyword-searching local notes
- Explicit use of one selected note as context for the next request
- Full or recent current-session context selection

## Usage

Start an interactive chat:

```bash
tgpt
```

List or choose a prompt mode:

```text
modes
mode debug
mode via_negativa How can I simplify this?
```

Send piped input in one request:

```bash
git diff | tgpt --review
journalctl -xe --no-pager | tgpt --debug "What is likely wrong?"
cat essay.md | tgpt --rewrite "Make clearer while preserving tone."
```

Piped input is truncated according to the `[truncation]` settings in
`config.toml` when it is too large.

Save and work with notes from an interactive chat:

```text
note piped-input-testing
notes list
notes search piped input
notes show piped-input-testing
notes use piped-input-testing
```

`notes use` selects a note as context for the next request; it does not send a
request by itself.

Continue the current conversation with selected context:

```text
context full
context recent
```

## Storage model

```text
sessions/*.jsonl   Automatic raw chat transcripts
notes/*.md         Curated question-and-answer notes
```

Sessions are retained as a local archive. Notes are intended to be readable,
searchable, and explicitly reused when useful. Note search never adds content
to AI context automatically; only an explicit `notes use <name>` command does.

## Architecture

```text
cli.py          Parses command-line flags for one-shot piped requests
input_parser.py Parses commands entered during interactive chat
main.py         Runs the application loop and coordinates state, chat, and storage
chat.py         Builds API messages and calls the OpenAI API
config.py       Loads and validates TOML configuration
state.py        Defines session and message data structures
storage.py      Stores JSONL transcripts and Markdown notes
truncation.py   Limits large piped input before it is sent to the API
```

## Development roadmap

Near term:

- Optional `--no-save` mode for sensitive piped input

Possible later additions:

- More flexible multi-note context management
- A rebuildable SQLite full-text index if file-based Markdown search becomes
  too slow or limited
