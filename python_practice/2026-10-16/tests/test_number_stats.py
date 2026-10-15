import unittest
from number_stats import summarize

class NumberStatsTests(unittest.TestCase):
    def test_summary(self):
        result = summarize([1.0, 3.0, 5.0])
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["mean"], 3.0)
        self.assertEqual(result["median"], 3.0)

    def test_rejects_empty_values(self):
        with self.assertRaises(ValueError):
            summarize([])

if __name__ == "__main__":
    unittest.main()
