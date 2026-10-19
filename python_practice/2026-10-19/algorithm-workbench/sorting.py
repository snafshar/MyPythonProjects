"""Simple sorting algorithms that return new lists."""


def insertion_sort(values):
    """Return a sorted copy using insertion sort; O(n^2) worst-case time."""
    result = list(values)
    for index in range(1, len(result)):
        current = result[index]
        position = index
        while position > 0 and result[position - 1] > current:
            result[position] = result[position - 1]
            position -= 1
        result[position] = current
    return result


def merge_sort(values):
    """Return a stable sorted copy using divide-and-conquer merge sort."""
    items = list(values)
    if len(items) < 2:
        return items
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
