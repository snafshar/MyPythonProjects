import unittest
from flatten import flatten_once

class FlattenTests(unittest.TestCase):
    def test_flattens_one_level(self):
        self.assertEqual(flatten_once([[1, 2], [3], [4, 5]]), [1, 2, 3, 4, 5])

    def test_empty_input(self):
        self.assertEqual(flatten_once([]), [])

if __name__ == "__main__":
    unittest.main()
