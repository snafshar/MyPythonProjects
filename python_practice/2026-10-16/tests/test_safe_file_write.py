import tempfile
import unittest
from pathlib import Path
from safe_file_write import atomic_write_text

class AtomicWriteTests(unittest.TestCase):
    def test_writes_utf8_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "message.txt"
            atomic_write_text(target, "hello 🌍")
            self.assertEqual(target.read_text(encoding="utf-8"), "hello 🌍")

if __name__ == "__main__":
    unittest.main()
