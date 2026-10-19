# Complexity Reference

| Algorithm | Typical time | Extra space | Key precondition |
|---|---:|---:|---|
| Linear search | (O(n)) | (O(1)) | None |
| Lower-bound binary search | (O(\log n)) | (O(1)) | Sorted ascending input |
| Insertion sort | (O(n^2)) worst case | (O(n)) returned copy | Comparable values |
| Merge sort | (O(n\log n)) | (O(n)) | Comparable values |
| BFS | (O(V+E)) | (O(V)) | Graph represented by adjacency lists |
| Dijkstra with heap | (O((V+E)\log V)) typical | (O(V)) | Non-negative edge weights |
| Fibonacci loop | (O(n)) | (O(1)) | (n\geq0) |
| Coin change DP | (O(A\cdot C)) | (O(A)) | Positive coin values |
| LIS dynamic program | (O(n^2)) | (O(n)) | Comparable values |
| Disjoint-set union | Near-constant amortized | (O(n)) | Hashable items |

Here (n) is input length, (V) vertices, (E) edges, (A) amount, and (C) the number of coin denominations. Complexity is an analytical estimate; measured runtime also depends on data shape and implementation.
