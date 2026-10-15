import unittest

from json_validate import describe


class DescribeTests(unittest.TestCase):
    def test_types(self):
        self.assertEqual(describe({"a": 1}), "object with 1 keys")
        self.assertEqual(describe([1, 2]), "array with 2 items")
        self.assertEqual(describe(None), "null")
        self.assertEqual(describe(True), "boolean")
        self.assertEqual(describe("hi"), "string")
        self.assertEqual(describe(3), "number")


if __name__ == "__main__":
    unittest.main()
