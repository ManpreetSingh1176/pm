import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def get_db_path() -> Path:
    return Path(os.getenv("KANBAN_DB_PATH", Path(__file__).resolve().parent.parent / "kanban.db"))

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
"""

CREATE_BOARDS_TABLE = """
CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    board_data TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

DEFAULT_BOARD_JSON = """
{
  "columns": [
    {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
    {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
    {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
    {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
    {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]}
  ],
  "cards": {
    "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
    "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
    "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
    "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
    "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
    "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
    "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
    "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."}
  }
}
"""


from contextlib import contextmanager


@contextmanager
def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        try:
            conn.commit()
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def init_database() -> None:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(CREATE_USERS_TABLE)
        conn.execute(CREATE_BOARDS_TABLE)
        conn.commit()


def create_user_if_missing(username: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO users (username, created_at) VALUES (?, ?)",
            (username, now),
        )
        if cursor.lastrowid:
            return cursor.lastrowid
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return row[0]


def get_user_id(username: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return row[0] if row else None


def get_board_data(user_id: int) -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT board_data FROM boards WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return row[0] if row else None


def save_default_board_for_user(user_id: int, board_data: str = DEFAULT_BOARD_JSON) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO boards (user_id, board_data, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, board_data, now, now),
        )
        conn.commit()


def get_or_create_board_for_user(user_id: int) -> str:
    board_data = get_board_data(user_id)
    if board_data is None:
        save_default_board_for_user(user_id)
        board_data = get_board_data(user_id)
    return board_data


def save_board_data(user_id: int, board_data: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        if conn.execute(
            "SELECT 1 FROM boards WHERE user_id = ?",
            (user_id,),
        ).fetchone():
            conn.execute(
                "UPDATE boards SET board_data = ?, updated_at = ? WHERE user_id = ?",
                (board_data, now, user_id),
            )
        else:
            conn.execute(
                "INSERT INTO boards (user_id, board_data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, board_data, now, now),
            )
        conn.commit()
