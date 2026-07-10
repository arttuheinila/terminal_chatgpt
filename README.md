# tgpt

Terminal-first AI assistant for short answers, saved notes, and later retrieval.

The current goal is not to polish features yet. The goal is to clean the codebase enough that adding prompt modes, piped input, note saving, and retrieval feels straightforward instead of fragile.

## What this project is becoming

The intended shape is:

- answer succinct questions from the terminal
- accept piped input as well as interactive prompts
- support prompt modes from configuration
- save chosen answers as local markdown notes
- search those notes later
- feed relevant prior notes back into new questions
- eventually behave like a small personal wiki

## Step 1: Clean setup before adding features

Do these in order. The reason for the order is to separate source code from generated data before you add more behavior.

DONE
1. Remove editor backup and generated session clutter.
   - Delete `tgpt.py~`.
   - Move dated transcript files out of the repository root or delete them if they are not intentional examples.
   - Why: these files make it harder to tell what is source and what is output.
2. Decide on one runtime data location.
   - Create separate folders for transcripts and notes, for example `sessions/` and `notes/`.
   - Update `.gitignore` to ignore those runtime folders instead of ignoring every `*.txt` file.
   - Why: you will want text notes in the repo later, so a blanket `*.txt` ignore becomes a problem.
5. Rename the project docs to match the actual entrypoint.
   - Use `README.md` for the main documentation file.
   - Make sure the README describes `tgpt.py` or the package entrypoint you actually plan to run.
   - Why: stale instructions are the fastest way to lose time when you revisit the project later.
3. Split the current script into small responsibilities.
   - Start by extracting four concerns from the current loop: input parsing, message building, API calling, and session storage.
   - Keep the command loop thin. It should only read input, ask whether it is a command or a chat message, and dispatch to the right helper.
   - Move all OpenAI request construction into one function so the system prompt, model name, and message list are assembled in one place.
   - Move save/load logic into one storage helper so file format changes stay isolated.
   - Put session state in one object or dictionary instead of many globals. At minimum, keep messages, active session filename, prompt mode, and any reused context together.
   - If you split into modules, a good first boundary is `input.py`, `chat.py`, and `storage.py`, with a small `main.py` or `tgpt.py` that only wires them together.
   - Why: this makes each later feature land in one obvious layer instead of forcing you to understand and edit the whole script at once.



DO



NOT TODAY

4. Standardize configuration.
   - Pick one environment variable name for the API key and use it everywhere. Do not keep both `API_KEY` and `OPENAI_API_KEY`; choose one and make the code, docs, and examples agree.
   - Add a `config.toml.example` file and treat it as the home for project defaults that a user may want to change without editing code.
   - Put prompt modes in that file, not in the Python source. Each mode should define the system prompt or prompt prefix for one style of answer.
   - Put other stable defaults in the same file, such as the model name, default note folder, default session folder, and any initial truncation setting.
   - Load config in one place at startup, then pass the values down into the rest of the app instead of reading config from scattered spots.
   - Keep secrets out of config. The API key should come from the environment, while non-secret defaults should come from TOML.
   - Why: prompt modes, model choices, and retrieval settings need one obvious place to live, and separating secrets from defaults keeps the project safer and easier to move between machines.


6. Add a tiny testable core before new features.
   - Start with tests that do not need the network. Good first candidates are command parsing, session save/load, truncation, and config loading.
   - Add one command-classification test. Given an input string, it should tell you whether the input is a normal prompt, a save command, a load command, or exit.
   - Add one session round-trip test. Save a tiny fake conversation, load it back, and confirm the messages match.
   - Add one message-building test. Given a session state and system prompt, confirm the final message list is assembled in the right order.
   - Add one truncation test. Given a list of messages and a limit, confirm it returns the expected tail of the list.
   - Add one config-loading test. Read a small TOML fixture and confirm the expected default values and prompt modes are parsed correctly.
   - Why: if you cannot verify the current behavior with small local tests, every later change becomes guesswork and you will not know whether a failure came from input handling, storage, or API setup.

## What to keep for now

Keep the current behavior that is already useful:

- plain terminal interaction
- saving session history
- loading previous history
- truncating context
- graceful exit with Ctrl+C

These are the minimum behaviors worth preserving while you clean up the shape of the project.

## What to change next after cleanup

Once the structure is cleaned up, the next implementation steps should be:

1. Add prompt modes from config.
2. Add piped input detection.
3. Add context truncation rules that are explicit and testable.
4. Save conversations as JSONL.
5. Add “save last answer as Markdown note.”
6. Add note search using filenames and content grep.
7. Add a SQLite index only after file-based notes are solid.
8. Add retrieval so matching notes can become context.
9. Add redaction once notes and retrieval are stable.

## Recommended starter layout

You do not need to build all of this immediately, but it is the direction that will keep the project clean:

- `src/tgpt/` for application code
- `tests/` for behavior checks
- `sessions/` for transcript files
- `notes/` for curated markdown notes
- `config.toml.example` for defaults and prompt modes

## Current status

This repository currently looks like a prototype with generated transcript files mixed into the root. The main cleanup job is to turn it into a small, explicit codebase with a clear boundary between source, config, and runtime data.
