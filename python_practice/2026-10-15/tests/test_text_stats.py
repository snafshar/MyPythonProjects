import unittest

from text_stats import analyze


class TextStatsTests(unittest.TestCase):
    def test_counts(self):
        result = analyze("Hello world\nPython!")
        self.assertEqual(result["lines"], 2)
        self.assertEqual(result["words"], 3)
        self.assertEqual(result["characters"], len("Hello world\nPython!"))

    def test_empty_text(self):
        result = analyze("")
        self.assertEqual(result["words"], 0)
        self.assertEqual(result["top_letters"], [])


if __name__ == "__main__":
    unittest.main()
