import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path

import backend.db as db

class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        os.environ["KANBAN_DB_PATH"] = str(Path(self.tempdir.name) / "kanban_test.db")
        importlib.reload(db)
        db.init_database()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_create_user_and_default_board(self) -> None:
        user_id = db.create_user_if_missing("user")
        self.assertIsInstance(user_id, int)

        board_data = db.get_or_create_board_for_user(user_id)
        parsed = json.loads(board_data)

        self.assertIn("columns", parsed)
        self.assertIn("cards", parsed)
        self.assertEqual(parsed["columns"][0]["title"], "Backlog")

    def test_save_board_data_updates_existing_record(self) -> None:
        user_id = db.create_user_if_missing("user")
        board_data = db.get_or_create_board_for_user(user_id)
        parsed = json.loads(board_data)
        parsed["columns"][0]["title"] = "Updated Backlog"

        db.save_board_data(user_id, json.dumps(parsed))
        stored = json.loads(db.get_board_data(user_id))
        self.assertEqual(stored["columns"][0]["title"], "Updated Backlog")

    def test_get_user_id_returns_none_for_unknown_user(self) -> None:
        self.assertIsNone(db.get_user_id("missing"))

if __name__ == "__main__":
    unittest.main()
