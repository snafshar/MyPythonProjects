#!/usr/bin/env python3
"""Report basic text statistics without third-party packages."""
from collections import Counter
from pathlib import Path
import argparse


def analyze(text: str) -> dict[str, object]:
    words = text.split()
    frequencies = Counter(char.lower() for char in text if char.isalpha())
    return {
        "lines": len(text.splitlines()),
        "words": len(words),
        "characters": len(text),
        "non_whitespace_characters": sum(not char.isspace() for char in text),
        "top_letters": frequencies.most_common(5),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text_file", type=Path)
    args = parser.parse_args()
    try:
        text = args.text_file.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    stats = analyze(text)
    for key, value in stats.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
