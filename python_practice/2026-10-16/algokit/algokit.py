"""Small, dependency-free algorithms for practice."""


def linear_search(values, target):
    """Return the first index of target, or -1 if it is absent."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def binary_search(values, target):
    """Return an index of target in ascending sorted values, or -1 if absent.

    The input must be sorted in ascending order. If duplicates exist, any
    matching index may be returned.
    """
    left, right = 0, len(values) - 1
    while left <= right:
        middle = (left + right) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1


def frequencies(items):
    """Return a dictionary mapping each hashable item to its occurrence count."""
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def brackets_are_balanced(text):
    """Check bracket nesting for (), [], and {}; ignore other characters.

    This educational checker does not parse string literals or comments.
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())
    stack = []
    for character in text:
        if character in opening:
            stack.append(character)
        elif character in pairs:
            if not stack or stack.pop() != pairs[character]:
                return False
    return not stack


if __name__ == "__main__":
    sample = [1, 3, 5, 7, 9]
    print("linear_search:", linear_search(sample, 5))
    print("binary_search:", binary_search(sample, 5))
    print("frequencies:", frequencies("banana"))
    print("balanced:", brackets_are_balanced("call([x], {y: 2})"))
