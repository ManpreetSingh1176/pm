import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

# Use a temporary database path before importing the app.
_tempdir = tempfile.TemporaryDirectory()
os.environ["KANBAN_DB_PATH"] = str(Path(_tempdir.name) / "kanban_main.db")

from backend.main import app  # noqa: E402

class TestMainRoutes(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)

    def test_ping_route(self) -> None:
        response = self.client.get("/api/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "pong"})

    @patch("backend.main.call_openrouter", new_callable=AsyncMock)
    def test_ai_ping_route(self, mock_openrouter: AsyncMock) -> None:
        mock_openrouter.return_value = {
            "choices": [{"message": {"content": "4"}}]
        }

        response = self.client.post("/api/ai/ping", json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["modelResponse"], "4")

    @patch("backend.main.call_openrouter", new_callable=AsyncMock)
    def test_ai_chat_route_applies_updates(self, mock_openrouter: AsyncMock) -> None:
        login_response = self.client.post(
            "/api/auth/login",
            json={"username": "user", "password": "password"},
        )
        self.assertEqual(login_response.status_code, 200)

        board_response = self.client.get("/api/kanban")
        self.assertEqual(board_response.status_code, 200)
        board = board_response.json()
        board["columns"][0]["title"] = "AI Updated Backlog"

        mock_openrouter.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "userMessage": "Board title updated.",
                                "kanbanUpdate": board,
                            }
                        )
                    }
                }
            ]
        }

        response = self.client.post(
            "/api/ai/chat",
            json={"question": "Update the backlog title.", "history": []},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["userMessage"], "Board title updated.")
        self.assertEqual(
            response.json()["board"]["columns"][0]["title"],
            "AI Updated Backlog",
        )

    def test_kanban_requires_auth(self) -> None:
        response = self.client.get("/api/kanban")
        self.assertEqual(response.status_code, 401)

    def test_login_logout_and_kanban_flow(self) -> None:
        response = self.client.post(
            "/api/auth/login",
            json={"username": "user", "password": "password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "user")

        response = self.client.get("/api/kanban")
        self.assertEqual(response.status_code, 200)
        self.assertIn("columns", response.json())

        new_board = response.json()
        new_board["columns"][0]["title"] = "Updated Backlog"

        update_response = self.client.post("/api/kanban", json=new_board)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["message"], "board updated")

        response = self.client.get("/api/kanban")
        self.assertEqual(response.json()["columns"][0]["title"], "Updated Backlog")

        logout_response = self.client.post("/api/auth/logout")
        self.assertEqual(logout_response.status_code, 200)

        unauth_response = self.client.get("/api/kanban")
        self.assertEqual(unauth_response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
