# Property-Oriented Testing Without Dependencies

Property-style tests generate many deterministic inputs and check invariants rather than only a few hard-coded examples.

Useful examples:
- Sorting preserves the input multiset.
- A sorted result is non-decreasing.
- Reversing a sequence twice returns the original.
- A graph path begins and ends at the requested vertices.
- A parser either returns a documented result or raises a documented exception.

Use a fixed random seed for reproducibility, keep failing examples small, and include boundary cases. Randomized tests complement—not replace—carefully chosen examples.
