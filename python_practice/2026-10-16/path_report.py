#!/usr/bin/env python3
"""Count regular files, directories, and file bytes beneath a path."""
import argparse
from pathlib import Path

def inventory(root: Path) -> tuple[int, int, int]:
    files = dirs = size = 0
    for item in root.rglob("*"):
        if item.is_symlink():
            continue
        if item.is_dir():
            dirs += 1
        elif item.is_file():
            files += 1
            try:
                size += item.stat().st_size
            except OSError:
                pass
    return files, dirs, size

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f"not a directory: {args.directory}")
    f, d, b = inventory(args.directory)
    print(f"Files: {f}\nDirectories: {d}\nBytes: {b}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
