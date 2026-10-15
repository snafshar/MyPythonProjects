#!/usr/bin/env python3
"""Starter template for a small command-line application."""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="input value or file path")
    parser.add_argument("--verbose", action="store_true", help="show extra details")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.verbose:
        print(f"Input: {args.input}")
    else:
        print(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
