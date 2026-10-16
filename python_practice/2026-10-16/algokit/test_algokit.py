import unittest

from algokit import binary_search, brackets_are_balanced, frequencies


class AlgoKitTests(unittest.TestCase):
    def test_binary_search_found_and_missing(self):
        self.assertEqual(binary_search([1, 3, 5, 7], 5), 2)
        self.assertEqual(binary_search([1, 3, 5, 7], 4), -1)
        self.assertEqual(binary_search([], 1), -1)

    def test_frequencies(self):
        self.assertEqual(frequencies("banana"), {"b": 1, "a": 3, "n": 2})
        self.assertEqual(frequencies([]), {})

    def test_balanced_brackets(self):
        self.assertTrue(brackets_are_balanced("f([x], {y: 2})"))
        self.assertFalse(brackets_are_balanced("([)]"))
        self.assertFalse(brackets_are_balanced("((("))
        self.assertTrue(brackets_are_balanced("plain text"))


if __name__ == "__main__":
    unittest.main()
