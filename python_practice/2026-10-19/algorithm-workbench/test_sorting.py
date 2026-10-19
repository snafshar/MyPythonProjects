import random
import unittest

from sorting import insertion_sort, merge_sort


class SortingTests(unittest.TestCase):
    def test_examples(self):
        values = [5, -1, 3, 3, 0]
        self.assertEqual(insertion_sort(values), [-1, 0, 3, 3, 5])
        self.assertEqual(merge_sort(values), [-1, 0, 3, 3, 5])
        self.assertEqual(values, [5, -1, 3, 3, 0])

    def test_randomized_against_sorted(self):
        rng = random.Random(20261019)
        for _ in range(100):
            values = [rng.randint(-100, 100) for _ in range(rng.randint(0, 60))]
            self.assertEqual(insertion_sort(values), sorted(values))
            self.assertEqual(merge_sort(values), sorted(values))

    def test_empty_and_single(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(insertion_sort([7]), [7])


if __name__ == "__main__":
    unittest.main()
