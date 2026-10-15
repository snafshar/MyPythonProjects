#!/usr/bin/env python3
"""A tiny JSON-backed command-line expense tracker."""

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def load_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read data file {path}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("data file must contain a JSON list")
    return data


def save_entries(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(entries, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def add_entry(entries: list[dict], amount: float, description: str, category: str) -> dict:
    description = description.strip()
    category = category.strip()
    if amount <= 0:
        raise ValueError("amount must be greater than zero")
    if not description:
        raise ValueError("description cannot be empty")
    if not category:
        raise ValueError("category cannot be empty")
    entry = {
        "amount": round(amount, 2),
        "description": description,
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    entries.append(entry)
    return entry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path("ledgerlite.json"))
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="record an expense")
    add.add_argument("amount", type=float)
    add.add_argument("description")
    add.add_argument("--category", default="uncategorized")
    commands.add_parser("list", help="list all expenses")
    commands.add_parser("summary", help="summarize spending by category")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        entries = load_entries(args.file)
        if args.command == "add":
            entry = add_entry(entries, args.amount, args.description, args.category)
            save_entries(args.file, entries)
            print(f"Added {entry['amount']:.2f}: {entry['description']} [{entry['category']}]")
        elif args.command == "list":
            if not entries:
                print("No expenses recorded.")
            for index, entry in enumerate(entries, start=1):
                print(f"{index:>3}. {entry['amount']:>9.2f}  {entry['category']:<14} {entry['description']}")
        else:
            totals: dict[str, float] = {}
            for entry in entries:
                totals[entry["category"]] = totals.get(entry["category"], 0.0) + float(entry["amount"])
            if not totals:
                print("No expenses recorded.")
            for category, total in sorted(totals.items()):
                print(f"{category:<18} {total:>9.2f}")
            print(f"{'TOTAL':<18} {sum(totals.values()):>9.2f}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
