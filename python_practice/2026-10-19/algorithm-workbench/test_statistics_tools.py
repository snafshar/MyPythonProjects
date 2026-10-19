import unittest

from statistics_tools import mean, median, percentile, population_variance


class StatisticsTests(unittest.TestCase):
    def test_mean_and_median(self):
        self.assertEqual(mean([2, 4, 6]), 4)
        self.assertEqual(median([9, 1, 3]), 3)
        self.assertEqual(median([1, 3, 5, 7]), 4)
        with self.assertRaises(ValueError):
            mean([])

    def test_variance(self):
        self.assertEqual(population_variance([2, 4, 6]), 8 / 3)

    def test_percentile_interpolation(self):
        self.assertEqual(percentile([0, 10], 25), 2.5)
        self.assertEqual(percentile([1, 2, 3], 0), 1)
        self.assertEqual(percentile([1, 2, 3], 100), 3)
        with self.assertRaises(ValueError):
            percentile([], 50)


if __name__ == "__main__":
    unittest.main()
