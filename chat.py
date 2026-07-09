#builds OpenAI messages and calls API

import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from .state import Message, SessionState

load_dotenv

OPEN_AI_URL = "https_//api.openai.com/v1/chat/completions"
MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPTS = {
    "default": """
You are a concise and analytical assistant designed to provide multiple perspectives, clear summaries, and actionable insights.

For any question, focus on key points, relevant examples, or short step-by-step instructions. Avoid unnecessary details.

When appropriate, include contrasting views or summarize in bullet points. Respond as if answering an experienced coder looking for efficient, reliable information.
""".strip(),

    "debug": """
You are a concise debugging assistant. Diagnose likely causes, suggest the next concrete test,
and avoid broad lectures unless necessary.
""".strip(),

    "brief": """
Answer briefly and directly. Prefer the useful 20 percent.
""".strip(),
}

class OpenAIError(Exception):
    pass

def current_timestamp() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")

def get_api_key() -> str:
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError(
            "API key not found. Set API_KEY in your environment or .env file"
        )
    
    return api_key

def truncate_messages(messages: list[Message], limit: int = 8) -> list[Message]:
    return messages[-limit:]

def messages_for_api(messages: list[Message]) -> list[dict[str, str]]:
    return [
        {"role": message.role, "content": message.content}
        for message in messages
        if message.role in {"user", "assistant", "system"}
    ]

def build_openai_messages(
        state: SessionState,
        user_input: str,
        include_history: bool = True,
) -> list[dict[str, str]]:
    system_prompt = SYSTEM_PROMPTS.get(state.prompt_mode, SYSTEM_PROMPTS["default"])

    api_messages: list[Message] = [
        Message(role="system", content=system_prompt)
    ]

    if include_history:
        api_messages.extend(state.reused_context)

    api_messages.append(Message(role="user", content=user_input))

    return messages_for_api(api_messages)
    
def call_openai(
    state:SessionState,
    user_input: str,
    include_history: bool = True,
) -> str:
    api_key = get_api_key()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": build_openai_messages(
            state=state,
            user_input=user_input,
            include_history=include_history,
        ),
    }

    response = requests.post(
        OPEN_AI_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise OpenAIError(f"Error {response.status_code}: {response.text}")
    
    data = response.json()
    return data["choices"][0]["message"]["content"]

