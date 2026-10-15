"""Readable examples of common collection transformations."""
from collections import Counter, defaultdict


def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        if word:
            grouped[word[0].lower()].append(word)
    return dict(grouped)


def frequency_table(words: list[str]) -> list[tuple[str, int]]:
    return Counter(word.casefold() for word in words).most_common()


if __name__ == "__main__":
    sample = ["Linux", "Python", "network", "programming", "process"]
    print(group_by_first_letter(sample))
    print(frequency_table(sample))
