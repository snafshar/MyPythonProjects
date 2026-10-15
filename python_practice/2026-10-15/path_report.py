#!/usr/bin/env python3
"""Count files and directories under a path without following symlinks."""
from pathlib import Path
import argparse


def inventory(root: Path) -> tuple[int, int, int]:
    files = directories = bytes_total = 0
    for item in root.rglob("*"):
        if item.is_symlink():
            continue
        if item.is_dir():
            directories += 1
        elif item.is_file():
            files += 1
            try:
                bytes_total += item.stat().st_size
            except OSError:
                pass
    return files, directories, bytes_total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error(f"not a directory: {args.directory}")
    files, directories, total = inventory(args.directory)
    print(f"Files: {files}\nDirectories: {directories}\nBytes: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
