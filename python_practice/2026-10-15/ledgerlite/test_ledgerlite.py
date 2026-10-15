"""Unit tests for LedgerLite; run with python -m unittest.""" 

import json
import tempfile
import unittest
from pathlib import Path

from ledgerlite import add_entry, load_entries, save_entries


class LedgerLiteTests(unittest.TestCase):
    def test_add_entry_trims_text_and_stores_amount(self):
        entries = []
        entry = add_entry(entries, 12.5, " lunch ", " food ")
        self.assertEqual(entry["description"], "lunch")
        self.assertEqual(entry["category"], "food")
        self.assertEqual(entry["amount"], 12.5)
        self.assertEqual(len(entries), 1)

    def test_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            add_entry([], 0, "coffee", "food")

    def test_rejects_blank_description(self):
        with self.assertRaises(ValueError):
            add_entry([], 2, "   ", "food")

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "ledger.json"
            entries = [add_entry([], 4.25, "bus", "transport")]
            save_entries(path, entries)
            self.assertEqual(load_entries(path), entries)

    def test_missing_file_is_empty_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_entries(Path(directory) / "missing.json"), [])

    def test_invalid_json_reports_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_entries(path)


if __name__ == "__main__":
    unittest.main()
