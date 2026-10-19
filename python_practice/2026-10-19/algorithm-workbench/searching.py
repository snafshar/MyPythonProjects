"""Search algorithms with documented input requirements."""


def linear_search(values, target):
    """Return the first matching index, or -1 if the target is absent."""
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def lower_bound(values, target):
    """Return the first index i for which values[i] >= target.

    If every value is smaller than target, return len(values).
    Input must be sorted in ascending order.
    """
    left, right = 0, len(values)
    while left < right:
        middle = (left + right) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


def binary_search(values, target):
    """Return the first index containing target in sorted values, else -1."""
    index = lower_bound(values, target)
    if index < len(values) and values[index] == target:
        return index
    return -1
