import json
import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OPENROUTER_API_URL = "https://openrouter.ai/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"


class AIChatRequest(BaseModel):
    question: str
    history: list[dict[str, str]] = []


def _load_dotenv() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and os.getenv(key) is None:
            os.environ[key] = value


_load_dotenv()


def get_openrouter_api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY")


def ai_system_instructions() -> str:
    return (
        "You are an AI assistant for a Kanban board web app. "
        "When asked to update the board, respond with valid JSON only. "
        "Return a JSON object with 'userMessage' and optionally 'kanbanUpdate'. "
        "If no board changes are needed, set 'kanbanUpdate' to null. "
        "Do not include any extra text outside the JSON object."
    )


def build_ai_messages(question: str, board_data: dict[str, Any], history: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": ai_system_instructions()},
    ]

    if history:
        for entry in history:
            if entry.get("role") and entry.get("content"):
                messages.append(
                    {"role": entry["role"], "content": entry["content"]}
                )

    board_json = json.dumps(board_data, separators=(",", ":"))
    messages.append(
        {
            "role": "user",
            "content": (
                "Here is the current Kanban board state as JSON:\n"
                f"{board_json}\n\n"
                "User question: \n"
                f"{question}\n\n"
                "Reply with valid JSON only."
            ),
        }
    )
    return messages


async def call_openrouter(messages: list[dict[str, str]]) -> dict[str, Any]:
    api_key = get_openrouter_api_key()
    # If no API key is configured, return a mocked structured response for local testing
    if not api_key:
        # Look for a user message to echo; fall back to a default reply
        last = messages[-1]["content"] if messages else ""
        reply = "Mock AI reply"
        if isinstance(last, str) and "update" in last.lower():
            reply = json.dumps({"userMessage": "Mock: applied update", "kanbanUpdate": None})
        else:
            reply = json.dumps({"userMessage": "Mock reply", "kanbanUpdate": None})
        return {"choices": [{"message": {"content": reply}}]}

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 400,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            OPENROUTER_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()


def extract_ai_message(response_json: dict[str, Any]) -> str:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("OpenRouter response is missing choices.")

    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise ValueError("OpenRouter response is missing message content.")

    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("OpenRouter response message content is not text.")

    return content.strip()


def parse_structured_ai_response(raw_text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("AI response is not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("AI response JSON must be an object.")

    if "userMessage" not in parsed:
        raise ValueError("AI response JSON must include 'userMessage'.")

    if parsed.get("kanbanUpdate") is not None:
        if not isinstance(parsed["kanbanUpdate"], dict):
            raise ValueError("kanbanUpdate must be an object or null.")
        if "columns" not in parsed["kanbanUpdate"] or "cards" not in parsed["kanbanUpdate"]:
            raise ValueError("kanbanUpdate must include 'columns' and 'cards'.")

    return parsed
