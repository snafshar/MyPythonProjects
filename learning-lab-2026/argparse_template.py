"""Reusable pattern for small command-line tools."""
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Count files in a directory")
    parser.add_argument("directory", type=Path, help="directory to inspect")
    parser.add_argument("--recursive", action="store_true", help="include nested files")
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f"not a directory: {args.directory}")
    iterator = args.directory.rglob("*") if args.recursive else args.directory.iterdir()
    print(sum(path.is_file() for path in iterator))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())