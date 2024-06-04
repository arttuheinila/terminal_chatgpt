# ChatGPT Terminal Interface

This project is a simple terminal-based interface for interacting with OpenAI's ChatGPT. It allows users to have continuous conversations, save and load chat histories, and manage sessions easily.

## Features

- Continuous chat interface with ChatGPT.
- Save chat history to a specified file.
- Load chat history (full or truncated) from a specified file.
- Option to save history after each interaction.
- Customizable system prompt.
- Graceful exit with history saving using Ctrl+C.

## Requirements

- Python 3
- Requests library
- Readline library

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/chatgpt-terminal-interface.git
    cd chatgpt-terminal-interface
    ```

2. **Install the required Python libraries:**

    ```bash
    pip install requests readline
    ```

3. **Set your OpenAI API key:**

    You can set your API key in an environment variable named `OPENAI_API_KEY`.

    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```

    Alternatively, you can set it directly in the script for testing purposes.

## Usage

1. **Run the script:**

    ```bash
    python chatgpt_terminal.py
    ```

2. **Interact with ChatGPT:**

    - Type your messages and press Enter to send.
    - Use `exit` to end the chat and save the history.
    - Use `Ctrl+C` to exit the chat and save the history.

3. **Commands:**

    - `load current history full` or `lchf`: Load the full history of the current session for the next query.
    - `load current history truncated` or `lcht`: Load a truncated version of the current session history (last 10 messages) for the next query.
    - `load history full <filename>` or `lhf <filename>`: Load the full history from another session for the next query.
    - `load history truncated <filename>` or `lht <filename>`: Load a truncated version from another session for the next query.
    - `save history <filename>` or `sh <filename>`: Save the current session to a specified file.

## Example

```bash
$ python chatgpt_terminal.py
ChatGPT Terminal Interface. Type 'exit' to end the chat.
Type 'load current history full' or 'lchf' to load the full history of the current session.
Type 'load current history truncated' or 'lcht' to load a truncated version of the current session history.
Type 'load history full <filename>' or 'lhf <filename>' to load the full history from another session.
Type 'load history truncated <filename>' or 'lht <filename>' to load a truncated version from another session.
Type 'save history <filename>' or 'sh <filename>' to save the current session to a specific file.

You: Hello, ChatGPT!
ChatGPT: Hello! How can I assist you today?

You: lchf
Loaded full history of current session
You: How does the history work
ChatGPT: The history allows you to load previous interactions into the current session.

You: sh my_session.txt
Chat history saved to my_session.txt.
