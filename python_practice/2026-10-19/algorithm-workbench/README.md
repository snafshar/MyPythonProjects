# Algorithm Workbench

A standard-library-only set of small algorithms with explicit contracts, unit tests, randomized-regression patterns, and a repeatable benchmark.

## Run the examples

```bash
python3 -m unittest discover -v
python3 benchmark_sorting.py --sizes 1000 5000 10000
python3 -c "from searching import binary_search; print(binary_search([1, 3, 5], 3))"
```

## Modules

- `searching.py`: linear search and lower-bound binary search.
- `sorting.py`: insertion sort and merge sort.
- `graph_algorithms.py`: breadth-first shortest path and Dijkstra's algorithm.
- `dynamic_programming.py`: Fibonacci, minimum coin change, and LIS length.
- `statistics_tools.py`: mean, median, population variance, and interpolated percentile.
- `text_tools.py`: whitespace normalization, word counts, and normalized palindrome check.
- `data_structures.py`: disjoint-set union / union-find.

The code is intended for learning, not as a substitute for carefully profiled production libraries. Benchmarks are machine-dependent and do not constitute performance guarantees.
