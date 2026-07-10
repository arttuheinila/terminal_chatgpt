#command loop and dispatch

import signal
from pathlib import Path

import readline

from .state import Message, SessionState
from .storage import (
    generate_default_session_path,
    save_messages,
    load_messages
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
    if state.active_session_path:
        save_messages(state.messages, state.active_session_path)


def handle_exit(state: SessionState) -> None:
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


def handle_command(
        state: SessionState,
        config: AppConfig,
        parsed: ParsedInput,
    ) -> bool:
    """
    Dispatch parsed input 

    Returns True if the app should continue running.
    Returns False if the app should exit.
    """

    if parsed.type == "exit":
        handle_exit(state)
        return False

    if parsed.type == "help":
        print_help()
        return True

    if parsed.type == "load_current_full":
        state.reused_context = list(state.messages)
        print("Loaded full history of current session as reusable context.")
        return True

    if parsed.type == "load_current_truncated":
        state.reused_context = truncate_messages(state.messages)
        print(
            f"Loaded truncated current history "
            f"({len(state.reused_context)} messages) as reusable context."
        )
        return True

    if parsed.type == "load_history_full":
        assert parsed.filename is not None
        loaded_messages = load_messages(parsed.filename)
        state.messages = loaded_messages
        state.reused_context = list(loaded_messages)
        state.active_session_path = parsed.filename
        print(f"Loaded full history from {parsed.filename}.")
        return True

    if parsed.type == "load_history_truncated":
        assert parsed.filename is not None
        loaded_messages = load_messages(parsed.filename)
        state.messages = loaded_messages
        state.reused_context = truncate_messages(loaded_messages)
        state.active_session_path = parsed.filename
        print(
            f"Loaded truncated history from {parsed.filename} "
            f"({len(state.reused_context)} messages)."
        )
        return True

    if parsed.type == "save_history":
        assert parsed.filename is not None
        save_messages(state.messages, parsed.filename)
        state.active_session_path = parsed.filename
        print(f"Chat history saved to {parsed.filename}.")
        return True

    if parsed.type == "chat":
        handle_chat_message(state, parsed.content)
        return True

    print("Unknown command. Type 'help' for commands.")
    return True

def make_initial_state(config: AppConfig) -> SessionState:
    """Create a fresh session state using configured storage defaults."""

    default_session_path = generate_default_session_path(config)

    return SessionState(
        messages=[],
        active_session_path=str(default_session_path),
        prompt_mode="default",
        reused_context=[],
        last_assistant_reply=None,
    )


def handle_chat_message(state: SessionState, user_input: str) -> None:
    user_message = Message(
        role="user",
        content=user_input,
        timestamp=current_timestamp(),
    )
    state.messages.append(user_message)

    try:
        reply = call_openai(
            state=state,
            user_input=user_input,
            include_history=True,
        )
    except OpenAIError as error:
        print(error)
        return

    print(OUTPUT_FORMAT.format(response=reply))

    assistant_message = Message(
        role="assistant",
        content=reply,
        timestamp=current_timestamp(),
    )
    state.messages.append(assistant_message)

    save_current_session(state)


def main() -> None:
    config = load_config()
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