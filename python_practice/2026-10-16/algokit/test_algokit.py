import unittest

from algokit import (
    binary_search,
    brackets_are_balanced,
    frequencies,
    linear_search,
)


class AlgoKitTests(unittest.TestCase):
    def test_linear_search(self):
        self.assertEqual(linear_search([4, 2, 4], 4), 0)
        self.assertEqual(linear_search([4, 2, 4], 3), -1)
        self.assertEqual(linear_search([], 1), -1)

    def test_binary_search(self):
        self.assertEqual(binary_search([1, 3, 5, 7], 5), 2)
        self.assertEqual(binary_search([1, 3, 5, 7], 4), -1)
        self.assertEqual(binary_search([], 1), -1)
        self.assertIn(binary_search([2, 2, 2], 2), [0, 1, 2])

    def test_frequencies(self):
        self.assertEqual(frequencies("banana"), {"b": 1, "a": 3, "n": 2})
        self.assertEqual(frequencies([]), {})
        self.assertEqual(frequencies([1, 1, 2]), {1: 2, 2: 1})

    def test_balanced_brackets(self):
        self.assertTrue(brackets_are_balanced("f([x], {y: 2})"))
        self.assertFalse(brackets_are_balanced("([)]"))
        self.assertFalse(brackets_are_balanced("((("))
        self.assertFalse(brackets_are_balanced("]"))
        self.assertTrue(brackets_are_balanced("plain text"))

    def test_frequency_rejects_unhashable_items(self):
        with self.assertRaises(TypeError):
            frequencies([[1], [1]])


if __name__ == "__main__":
    unittest.main()
