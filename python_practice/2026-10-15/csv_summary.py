#!/usr/bin/env python3
"""Summarize numeric columns in a CSV file using only the standard library."""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def summarize(path: Path) -> dict[str, dict[str, float | int]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV must have a header row")
        values: dict[str, list[float]] = {name: [] for name in reader.fieldnames}
        for line_number, row in enumerate(reader, start=2):
            for name, raw in row.items():
                if raw is None or not raw.strip():
                    continue
                try:
                    number = float(raw)
                except ValueError:
                    continue
                if math.isfinite(number):
                    values[name].append(number)
    result = {}
    for name, column in values.items():
        if column:
            result[name] = {
                "count": len(column),
                "min": min(column),
                "max": max(column),
                "mean": sum(column) / len(column),
            }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    try:
        report = summarize(args.csv_file)
    except (OSError, csv.Error, ValueError) as exc:
        parser.error(str(exc))
    if not report:
        print("No numeric columns found.")
    for column, stats in report.items():
        print(f"{column}: n={stats['count']} min={stats['min']:.4g} "
              f"max={stats['max']:.4g} mean={stats['mean']:.4g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
