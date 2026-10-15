#!/usr/bin/env python3
"""Validate a JSON file and print a compact description."""
import argparse
import json
from pathlib import Path
import sys


def describe(value: object) -> str:
    if isinstance(value, dict):
        return f"object with {len(value)} keys"
    if isinstance(value, list):
        return f"array with {len(value)} items"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, (int, float)):
        return "number"
    return type(value).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()
    try:
        with args.json_file.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Cannot read file: {exc}", file=sys.stderr)
        return 1
    print(f"Valid JSON: {describe(value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
