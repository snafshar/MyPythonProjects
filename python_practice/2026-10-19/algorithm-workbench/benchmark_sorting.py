"""Compare simple sorting algorithms with the built-in sorted function."""

import argparse
import random
import timeit

from sorting import insertion_sort, merge_sort


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 500, 1500])
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if any(size < 0 for size in args.sizes) or args.repeats < 1:
        parser.error("sizes must be non-negative and repeats must be positive")

    rng = random.Random(12345)
    print(f"{'n':>8} {'insertion ms':>15} {'merge ms':>12} {'sorted ms':>12}")
    for size in args.sizes:
        sample = [rng.randint(-size, size) for _ in range(size)]
        expected = sorted(sample)
        assert insertion_sort(sample) == expected
        assert merge_sort(sample) == expected
        measurements = []
        for function in (insertion_sort, merge_sort, sorted):
            elapsed = timeit.timeit(lambda: function(sample), number=args.repeats)
            measurements.append(elapsed * 1000 / args.repeats)
        print(f"{size:>8} {measurements[0]:>15.3f} {measurements[1]:>12.3f} {measurements[2]:>12.3f}")


if __name__ == "__main__":
    main()
