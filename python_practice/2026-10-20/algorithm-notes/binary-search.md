# Binary Search: Invariants and Edge Cases

For a sorted array, maintain a search interval `[low, high)`. At each step, choose `mid = low + (high - low) // 2`. If the middle value is smaller than the target, set `low = mid + 1`; otherwise set `high = mid`.

This form finds the first position whose value is at least the target. The result may equal the array length, meaning every element is smaller than the target.

Test empty arrays, one element, duplicates, target below/above the range, and an existing target. Time complexity is (O(\log n)); extra space is (O(1)) for an iterative implementation.
