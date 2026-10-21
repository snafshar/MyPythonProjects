"""Summarize a CSV column using only the Python standard library."""
import csv
import sys
from statistics import mean


def numeric_column(path: str, column: str) -> list[float]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or column not in reader.fieldnames:
            raise ValueError(f"Missing column: {column}")
        values = []
        for row_number, row in enumerate(reader, start=2):
            try:
                values.append(float(row[column]))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid number on row {row_number}") from exc
    if not values:
        raise ValueError("No data rows found")
    return values


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python csv_report.py FILE COLUMN")
    data = numeric_column(sys.argv[1], sys.argv[2])
    print(f"count={len(data)} mean={mean(data):.3f} min={min(data):.3f} max={max(data):.3f}")