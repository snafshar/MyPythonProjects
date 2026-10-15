"""Unit tests for StudySprint's core data operations."""

import json
import tempfile
import unittest
from pathlib import Path

from studysprint import add_session, load_sessions, save_sessions


class StudySprintTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "sessions.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_is_empty(self):
        self.assertEqual(load_sessions(self.data_path), [])

    def test_add_session_persists_data(self):
        add_session(self.data_path, "Python", 30, "unit testing")
        sessions = load_sessions(self.data_path)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["topic"], "Python")
        self.assertEqual(sessions[0]["minutes"], 30)
        self.assertEqual(sessions[0]["note"], "unit testing")

    def test_invalid_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            add_session(self.data_path, "Python", 0)

    def test_blank_topic_is_rejected(self):
        with self.assertRaises(ValueError):
            add_session(self.data_path, "   ", 20)

    def test_malformed_json_is_reported(self):
        self.data_path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_sessions(self.data_path)

    def test_save_creates_parent_directories(self):
        nested = Path(self.temp_dir.name) / "nested" / "sessions.json"
        save_sessions(nested, [])
        self.assertEqual(json.loads(nested.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
