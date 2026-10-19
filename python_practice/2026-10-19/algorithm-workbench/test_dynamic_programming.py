import unittest

from dynamic_programming import fibonacci, lis_length, minimum_coins


class DynamicProgrammingTests(unittest.TestCase):
    def test_fibonacci(self):
        self.assertEqual([fibonacci(n) for n in range(7)], [0, 1, 1, 2, 3, 5, 8])
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_minimum_coins(self):
        self.assertEqual(minimum_coins([1, 3, 4], 6), 2)
        self.assertIsNone(minimum_coins([4, 6], 5))
        self.assertEqual(minimum_coins([], 0), 0)
        with self.assertRaises(ValueError):
            minimum_coins([0, 1], 4)

    def test_lis_length(self):
        self.assertEqual(lis_length([]), 0)
        self.assertEqual(lis_length([3, 1, 2, 5, 4]), 3)
        self.assertEqual(lis_length([2, 2, 2]), 1)


if __name__ == "__main__":
    unittest.main()
