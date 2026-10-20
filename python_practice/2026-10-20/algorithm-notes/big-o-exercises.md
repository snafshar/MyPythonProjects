# Big-O Exercises

1. One loop over n items: O(n).
2. Two independent nested loops of size n: O(n²).
3. Repeatedly halve a positive integer: O(log n).
4. Sort then scan: O(n log n) for a comparison sort.
5. Store all pairs: O(n²) additional space.

Extension: identify assumptions behind each answer. A loop with a constant bound is O(1) with respect to n; nested loops do not always imply O(n²) if their bounds differ.