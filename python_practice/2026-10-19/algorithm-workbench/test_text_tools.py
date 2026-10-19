import unittest

from text_tools import is_palindrome, normalize_whitespace, word_frequencies


class TextToolsTests(unittest.TestCase):
    def test_normalize_whitespace(self):
        self.assertEqual(normalize_whitespace("  hello\n\tworld  "), "hello world")
        self.assertEqual(normalize_whitespace(""), "")

    def test_word_frequencies(self):
        self.assertEqual(word_frequencies("Red red, BLUE!"), {"red": 2, "blue": 1})

    def test_palindrome(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama!"))
        self.assertTrue(is_palindrome(""))
        self.assertFalse(is_palindrome("algorithm"))


if __name__ == "__main__":
    unittest.main()
