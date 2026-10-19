# AlgoKit: Small Algorithm Practice

A dependency-free collection of beginner-friendly algorithms with tests and clear input contracts.

## Run

```bash
python3 algokit.py
python3 -m unittest -v
```

Run the commands from this directory. Python 3.8+ is recommended.

## Included algorithms

| Function | Purpose | Typical time |
|---|---|---|
| `linear_search(values, target)` | Find the first matching item | O(n) |
| `binary_search(values, target)` | Search ascending sorted values | O(log n) |
| `frequencies(items)` | Count occurrences of hashable items | O(n) average |
| `brackets_are_balanced(text)` | Check nesting of (), [], {} | O(n) |

Binary search requires ascending sorted input. The bracket checker ignores non-bracket characters and is not a parser for programming-language strings or comments.

## Suggested extensions

- Add a benchmark comparing linear and binary search on sorted lists.
- Generate randomized test cases and compare both search functions.
- Add a function that returns the first matching index in binary search.
- Measure memory usage as well as runtime.
