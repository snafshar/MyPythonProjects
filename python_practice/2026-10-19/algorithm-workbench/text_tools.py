"""Small text helpers for common data-cleaning exercises."""


import re
from collections import Counter


def normalize_whitespace(text):
    """Trim leading/trailing whitespace and collapse internal runs to spaces."""
    return " ".join(text.split())


def word_frequencies(text):
    """Count Unicode word-like tokens case-insensitively."""
    tokens = re.findall(r"\w+", text.casefold(), flags=re.UNICODE)
    return dict(Counter(tokens))


def is_palindrome(text):
    """Check palindrome equality after case-folding and removing punctuation."""
    normalized = "".join(character for character in text.casefold() if character.isalnum())
    return normalized == normalized[::-1]
