import json
from typing import Any

from fastapi import Body, Cookie, Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .ai import (
    AIChatRequest,
    build_ai_messages,
    call_openrouter,
    extract_ai_message,
    parse_structured_ai_response,
)
from .db import (
    create_user_if_missing,
    get_or_create_board_for_user,
    get_user_id,
    init_database,
    save_board_data,
)

VALID_USERNAME = "user"
VALID_PASSWORD = "password"
COOKIE_NAME = "kanban_user"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    init_database()

@app.get("/api/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}

@app.post("/api/auth/login")
async def login(response: Response, credentials: dict[str, str] = Body(...)) -> dict[str, Any]:
    username = credentials.get("username", "")
    password = credentials.get("password", "")

    if username != VALID_USERNAME or password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    user_id = create_user_if_missing(username)
    get_or_create_board_for_user(user_id)

    response.set_cookie(
        COOKIE_NAME,
        username,
        httponly=True,
        samesite="lax",
        path="/",
    )

    return {"message": "logged in", "username": username}

@app.post("/api/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "logged out"}


def get_current_username(kanban_user: str | None = Cookie(default=None)) -> str:
    if kanban_user != VALID_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return kanban_user


@app.get("/api/kanban")
async def get_kanban(username: str = Depends(get_current_username)) -> Any:
    user_id = get_user_id(username)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    board_data = get_or_create_board_for_user(user_id)
    return json.loads(board_data)


@app.post("/api/kanban")
async def update_kanban(
    board_data: dict[str, Any] = Body(...),
    username: str = Depends(get_current_username),
) -> dict[str, str]:
    user_id = get_user_id(username)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    save_board_data(user_id, json.dumps(board_data))
    return {"message": "board updated"}


@app.post("/api/ai/ping")
async def ai_ping(test: dict[str, str] = Body({"question": "2+2"})) -> dict[str, str]:
    question = test.get("question", "2+2")
    messages = build_ai_messages(question, {"columns": [], "cards": {}}, [])
    response_json = await call_openrouter(messages)
    model_response = extract_ai_message(response_json)
    return {"message": "AI ping successful", "modelResponse": model_response}


@app.post("/api/ai/chat")
async def ai_chat(
    payload: AIChatRequest = Body(...),
    username: str = Depends(get_current_username),
) -> dict[str, Any]:
    user_id = get_user_id(username)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    board_data = json.loads(get_or_create_board_for_user(user_id))
    messages = build_ai_messages(payload.question, board_data, payload.history)
    response_json = await call_openrouter(messages)
    raw_ai_text = extract_ai_message(response_json)

    structured_result = parse_structured_ai_response(raw_ai_text)
    user_message = structured_result["userMessage"]
    kanban_update = structured_result.get("kanbanUpdate")

    if kanban_update is not None:
        save_board_data(user_id, json.dumps(kanban_update))

    return {
        "userMessage": user_message,
        "kanbanUpdate": kanban_update,
        "board": kanban_update or board_data,
    }


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "backend is running"}
