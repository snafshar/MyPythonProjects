# AlgoKit: Small Algorithm Practice

A dependency-free collection of beginner-friendly algorithms with unit and deterministic randomized tests.

## Run

```bash
python3 algokit.py
python3 -m unittest discover -v
python3 benchmark_search.py
```

Run these commands from this directory. Python 3.8+ is recommended.

## Included algorithms

| Function | Purpose | Typical time |
|---|---|---|
| `linear_search(values, target)` | Find the first matching item | O(n) |
| `binary_search(values, target)` | Search ascending sorted values | O(log n) |
| `two_sum(values, target)` | Find two indices whose values sum to target | O(n) average |
| `frequencies(items)` | Count occurrences of hashable items | O(n) average |
| `brackets_are_balanced(text)` | Check nesting of (), [], {} | O(n) |

Binary search requires ascending sorted input. `two_sum` returns a pair of distinct indices or `None`. The bracket checker ignores non-bracket characters and is not a parser for programming-language strings or comments.

## Benchmark

Compare the worst-case successful linear-search position with binary search:

```bash
python3 benchmark_search.py --sizes 1000 10000 100000 --repeats 20
```

Benchmark timings vary by machine and should be interpreted as observations, not guarantees. The script verifies the answers before printing timings.

## Test coverage

The unit tests include edge cases, repeated values, invalid bracket nesting, and fixed-seed randomized comparisons against a reference search. CI runs on Python 3.11 and 3.13.
