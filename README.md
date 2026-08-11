# tgpt

Small terminal-first AI assistant for short answers, prompt modes, and piped
input. It is actively under development.

The current goal is not to polish features yet. The focus is on keeping the
codebase clean enough to add note retrieval next.

## What this project is becoming

The intended shape is:

- answer succinct questions from the terminal
- accept piped input as well as interactive prompts
- support prompt modes from configuration
- save selected questions and answers as local Markdown notes
- search those notes later
- feed relevant prior notes back into new questions
- eventually behave like a small personal wiki

## Current capabilities

- Interactive terminal chat
- Configurable prompt modes
- One-shot piped input
- Local session history
- Saving the latest question and answer as a Markdown note

## Usage

Interactive chat:

```bash
tgpt
```

List and switch modes in interactive chat:

```text
modes
mode debug
mode via_negativa How can I simplify this?
```

Use piped input:

```bash
git diff | tgpt --review
journalctl -xe --no-pager | tgpt --debug "What is likely wrong?"
cat essay.md | tgpt --rewrite "Make clearer while preserving tone."
```

Piped input is truncated according to `[truncation]` in `config.toml` when it
is too large.

Save the latest question and answer from an interactive chat:

```text
note piped-input-testing
```

## Still in development

- Better handling and visibility of truncated input
- Markdown note keyword search and explicit reuse of selected notes as context
- More robust error handling and tests
- Better CLI help and installation flow

## Possible future additions

- A SQLite index for efficient Markdown note search once a simple file-based
  search is no longer sufficient
