"""Small, dependency-free algorithms for practice."""


def binary_search(values, target):
    """Return the index of target in sorted values, or -1 if absent."""
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
    """Return a dictionary mapping each item to its occurrence count."""
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def brackets_are_balanced(text):
    """Check (), [], and {} nesting while ignoring other characters."""
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
    print("binary_search:", binary_search([1, 3, 5, 7], 5))
    print("frequencies:", frequencies("banana"))
    print("balanced:", brackets_are_balanced("call([x], {y: 2})"))
