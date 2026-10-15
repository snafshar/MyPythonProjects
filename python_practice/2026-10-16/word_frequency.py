#!/usr/bin/env python3
"""Print the most common words in a UTF-8 text file."""
import argparse
from collections import Counter
from pathlib import Path
import re

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be positive")
    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    words = re.findall(r"\b[\w']+\b", text.casefold())
    for word, count in Counter(words).most_common(args.top):
        print(f"{count:5} {word}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
