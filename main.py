"""Run the interactive terminal loop and dispatch user commands."""

import signal
import sys
from pathlib import Path
import readline

if __package__ in {None, ""}:
    package_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(package_root.parent))
    __package__ = package_root.name

from .cli import parse_args
from .truncation import truncate_text
from .state import Message, SessionState
from .storage import (
    generate_default_session_path,
    save_messages,
    load_messages,
    save_note,
    search_notes,
)
from .input_parser import parse_user_input, print_help, ParsedInput
from .chat import (
    call_openai,
    current_timestamp,
    truncate_messages,
    OpenAIError,
)
from .config import AppConfig, load_config

OUTPUT_FORMAT = "ChatGPT: {response}"

def save_current_session(state: SessionState) -> None:
    """Persist the current transcript when it has an assigned session path."""

    if state.active_session_path:
        save_messages(state.messages, state.active_session_path)


def handle_exit(state: SessionState) -> None:
    """Save the active transcript before ending the interactive session."""

    save_current_session(state)
    print("\nChat history saved. Exiting...")


def create_signal_handler(state: SessionState):
    """Create a Ctrl-C handler that can access the current session state."""

    def exit_gracefully(signum, frame):
        handle_exit(state)
        raise SystemExit(0)

    return exit_gracefully

def set_prompt_mode(
    state: SessionState,
    config: AppConfig,
    mode_name: str,
) -> None:
    """Switch prompt mode if it exists in config."""

    if mode_name not in config.prompts:
        available = ", ".join(sorted(config.prompts.keys()))
        print(f"Unknown mode: {mode_name}")
        print(f"Available modes: {available}")
        return

    state.prompt_mode = mode_name
    print(f"Prompt mode set to: {mode_name}")


def split_mode_and_message(
    config: AppConfig,
    requested_mode: str,
) -> tuple[str, str]:
    """Separate a configured mode name from an optional inline chat message."""

    for mode_name in sorted(config.prompts, key=len, reverse=True):
        if requested_mode == mode_name:
            return mode_name, ""
        if requested_mode.startswith(f"{mode_name} "):
            return mode_name, requested_mode[len(mode_name):].strip()

    return requested_mode, ""


def list_prompt_modes(state: SessionState, config: AppConfig) -> None:
    """Show modes loaded from the active configuration."""

    print("Configured prompt modes:")
    for mode_name in sorted(config.prompts):
        marker = " (active)" if mode_name == state.prompt_mode else ""
        print(f"  {mode_name}{marker}")


def handle_command(
        state: SessionState,
        config: AppConfig,
        parsed: ParsedInput,
    ) -> bool:
    """
    Dispatch one parsed interactive command.

    Return ``True`` to continue the terminal loop and ``False`` to exit it.
    """

    if parsed.type == "exit":
        handle_exit(state)
        return False

    if parsed.type == "help":
        print_help()
        return True

    if parsed.type == "list_prompt_modes":
        list_prompt_modes(state, config)
        return True

    if parsed.type == "set_prompt_mode":
        assert parsed.mode_name is not None
        mode_name, inline_message = split_mode_and_message(
            config, parsed.mode_name
        )
        if mode_name not in config.prompts:
            set_prompt_mode(state, config, mode_name)
            return True

        set_prompt_mode(state, config, mode_name)
        if inline_message:
            handle_chat_message(state, config, inline_message)
        return True

    if parsed.type == "context_full":
        state.reused_context = list(state.messages)
        print("Using full current session as conversation context.")
        return True

    if parsed.type == "context_recent":
        state.reused_context = truncate_messages(state.messages)
        print(
            f"Using recent current session messages "
            f"({len(state.reused_context)} messages) as conversation context."
        )
        return True

    if parsed.type == "history_load":
        assert parsed.filename is not None
        loaded_messages = load_messages(parsed.filename)
        state.reused_context = list(loaded_messages)
        print(
            f"Loaded {len(loaded_messages)} messages from {parsed.filename} "
            "as conversation context."
        )
        return True

    if parsed.type == "history_save_as":
        assert parsed.filename is not None
        save_messages(state.messages, parsed.filename)
        print(f"Saved a copy of the current session to {parsed.filename}.")
        return True

    if parsed.type == "save_note":
        # Notes are intentional exports of the latest complete exchange, not
        # automatic copies of every session message.
        if not parsed.note_title:
            print("A note title is required. Usage: note <title>")
            return True

        if not state.last_assistant_reply:
            print("No assistant reply is available to save.")
            return True

        path = save_note(
            question=state.last_user_message or "",
            answer=state.last_assistant_reply,
            title=parsed.note_title,
            note_dir=config.storage.note_dir,
            prompt_mode=state.prompt_mode,
        )
        print(f"Saved note: {path}")
        return True

    if parsed.type == "search_notes":
        if not parsed.search_query:
            print("A search query is required. Usage: notes search <query>")
            return True

        results = search_notes(
            query=parsed.search_query,
            note_dir=config.storage.note_dir,
        )

        if not results:
            print("No matching notes found.")
            return True

        print(f"Found {len(results)} matching notes:")
        for index, result in enumerate(results, start=1):
            print(f"\n{index}. {result.path}")
            print(f"   {result.title}")
            print(f"   {result.snippet}")

        return True

    if parsed.type == "chat":
        handle_chat_message(state, config, parsed.content)
        return True

    print("Unknown command. Type 'help' for commands.")
    return True

def make_initial_state(config: AppConfig) -> SessionState:
    """Create a fresh transcript and reserve a unique path for its JSONL file."""

    default_session_path = generate_default_session_path(config)

    return SessionState(
        messages=[],
        active_session_path=str(default_session_path),
        prompt_mode="default",
        reused_context=[],
        last_assistant_reply=None,
    )


def handle_chat_message(state: SessionState, config: AppConfig, user_input: str) -> None:
    """Send one message, retain the completed exchange, and persist the transcript."""

    state.last_user_message = user_input

    user_message = Message(
        role="user",
        content=user_input,
        timestamp=current_timestamp(),
    )
    state.messages.append(user_message)

    try:
        reply = call_openai(
            state=state,
            config=config,
            user_input=user_input,
            include_history=True,
        )
    except OpenAIError as error:
        print(error)
        return

    print(OUTPUT_FORMAT.format(response=reply))

    state.last_assistant_reply = reply

    assistant_message = Message(
        role="assistant",
        content=reply,
        timestamp=current_timestamp(),
    )
    state.messages.append(assistant_message)

    save_current_session(state)


def main() -> None:
    config = load_config()
    args = parse_args()

    if not sys.stdin.isatty():
        # A non-terminal stdin stream indicates one-shot piped input. It must
        # finish after the reply so it composes cleanly with other shell tools.
        mode = args.mode or "default"
        if mode not in config.prompts:
            available = ", ".join(sorted(config.prompts))
            raise SystemExit(f"Unknown mode: {mode}. Available: {available}")

        state = make_initial_state(config)
        state.prompt_mode = mode

        raw_source = sys.stdin.read()

        source = truncate_text(
            raw_source,
            max_chars=config.truncation.max_stdin_chars,
            head_chars=config.truncation.stdin_head_chars,
            tail_chars=config.truncation.stdin_tail_chars,
        )

        if len(raw_source) > config.truncation.max_stdin_chars:
            retained_chars = (
                config.truncation.stdin_head_chars + config.truncation.stdin_tail_chars
            )
            omitted_chars = len(raw_source) - retained_chars

            print(
                "Warning: input was "
                f"{len(raw_source):,} characters; retained the first "
                f"{config.truncation.stdin_head_chars:,} and last "
                f"{config.truncation.stdin_tail_chars:,} characters "
                f"{len(source):,} characters sent after adding the truncation marker; "
                f"{omitted_chars:,} original characters omitted).",
                file=sys.stderr,
            )

        question = " ".join(args.question) or "Analyze the supplied input."

        user_input = f"""Task:
{question}

Input:
{source}"""

        handle_chat_message(state, config, user_input)
        return

    state = make_initial_state(config)
    signal.signal(signal.SIGINT, create_signal_handler(state))

    print("ChatGPT Terminal Interface. Type 'exit' to end the chat.")
    print("Type 'help' for commands.")
    print(f"Active session: {state.active_session_path}")
    print(f"Prompt mode: {state.prompt_mode}")

    

    while True:
        raw_input = input("You: ")
        parsed = parse_user_input(raw_input)

        should_continue = handle_command(
            state=state,
            config=config,
            parsed=parsed
            )

        if not should_continue:
            break


if __name__ == "__main__":
    main()
