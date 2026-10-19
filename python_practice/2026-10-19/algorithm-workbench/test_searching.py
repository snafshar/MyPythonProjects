import unittest

from searching import binary_search, linear_search, lower_bound


class SearchingTests(unittest.TestCase):
    def test_linear_search(self):
        self.assertEqual(linear_search([4, 2, 4], 4), 0)
        self.assertEqual(linear_search([], 3), -1)

    def test_lower_bound(self):
        self.assertEqual(lower_bound([], 2), 0)
        self.assertEqual(lower_bound([1, 2, 2, 2, 5], 2), 1)
        self.assertEqual(lower_bound([1, 3, 5], 4), 2)
        self.assertEqual(lower_bound([1, 3], 9), 2)

    def test_binary_search_returns_first_duplicate(self):
        self.assertEqual(binary_search([1, 2, 2, 2, 4], 2), 1)
        self.assertEqual(binary_search([1, 3, 5], 2), -1)


if __name__ == "__main__":
    unittest.main()
