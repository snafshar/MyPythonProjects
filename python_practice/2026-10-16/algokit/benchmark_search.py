"""Tiny standard-library benchmark for AlgoKit search functions."""

import argparse
import timeit

from algokit import binary_search, linear_search


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=positive_int,
        default=[1_000, 10_000, 100_000],
        help="list sizes to benchmark (default: 1000 10000 100000)",
    )
    parser.add_argument(
        "--repeats",
        type=positive_int,
        default=20,
        help="number of calls per algorithm and size (default: 20)",
    )
    args = parser.parse_args()

    print(f"Repeated calls per measurement: {args.repeats}")
    print(f"{'n':>10} {'linear (us/call)':>20} {'binary (us/call)':>20}")
    for size in args.sizes:
        values = list(range(size))
        target = size - 1  # Worst-case position for a successful linear search.

        linear_seconds = timeit.timeit(
            lambda: linear_search(values, target), number=args.repeats
        )
        binary_seconds = timeit.timeit(
            lambda: binary_search(values, target), number=args.repeats
        )
        assert linear_search(values, target) == target
        assert binary_search(values, target) == target

        linear_us = linear_seconds * 1_000_000 / args.repeats
        binary_us = binary_seconds * 1_000_000 / args.repeats
        print(f"{size:>10} {linear_us:>20.2f} {binary_us:>20.2f}")


if __name__ == "__main__":
    main()
