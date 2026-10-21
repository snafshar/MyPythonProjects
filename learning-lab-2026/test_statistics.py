import unittest
from statistics_summary import summarize


class SummaryTests(unittest.TestCase):
    def test_basic_summary(self):
        result = summarize([2, 4, 6])
        self.assertEqual(result["count"], 3.0)
        self.assertEqual(result["mean"], 4)
        self.assertEqual(result["median"], 4)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            summarize([])


if __name__ == "__main__":
    unittest.main()