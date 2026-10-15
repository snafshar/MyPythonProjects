import tempfile
import unittest
from pathlib import Path
from path_report import inventory

class InventoryTests(unittest.TestCase):
    def test_counts_files_and_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub").mkdir()
            (root / "a.txt").write_text("abc", encoding="utf-8")
            (root / "sub" / "b.txt").write_text("de", encoding="utf-8")
            files, dirs, size = inventory(root)
            self.assertEqual((files, dirs, size), (2, 1, 5))

if __name__ == "__main__":
    unittest.main()
