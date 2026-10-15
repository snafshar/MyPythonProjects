#!/usr/bin/env python3
"""StudySprint: a tiny JSON-backed study-session tracker."""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys


def load_sessions(path: Path) -> list[dict]:
    """Load sessions, treating a missing file as an empty tracker."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read data file {path}: {exc}") from exc
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("data file must contain a JSON list of session objects")
    return data


def save_sessions(path: Path, sessions: list[dict]) -> None:
    """Write data atomically to reduce the chance of a partially written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(sessions, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def add_session(path: Path, topic: str, minutes: int, note: str = "") -> None:
    if minutes <= 0:
        raise ValueError("minutes must be a positive integer")
    topic = topic.strip()
    if not topic:
        raise ValueError("topic cannot be empty")
    sessions = load_sessions(path)
    sessions.append({
        "topic": topic,
        "minutes": minutes,
        "note": note.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    save_sessions(path, sessions)
    print(f"Recorded {minutes} minutes for {topic!r}.")


def list_sessions(path: Path) -> None:
    sessions = load_sessions(path)
    if not sessions:
        print("No sessions recorded yet.")
        return
    for item in reversed(sessions):
        stamp = item.get("created_at", "unknown time")
        topic = item.get("topic", "(untitled)")
        minutes = item.get("minutes", 0)
        note = item.get("note", "")
        print(f"{stamp} | {minutes:>3} min | {topic}" + (f" — {note}" if note else ""))


def show_summary(path: Path) -> None:
    totals: dict[str, int] = defaultdict(int)
    sessions = load_sessions(path)
    for item in sessions:
        topic = str(item.get("topic", "(untitled)"))
        try:
            minutes = int(item.get("minutes", 0))
        except (TypeError, ValueError):
            continue
        if minutes > 0:
            totals[topic] += minutes
    if not totals:
        print("No study time recorded yet.")
        return
    print(f"Sessions: {len(sessions)}")
    print(f"Total: {sum(totals.values())} minutes")
    for topic, minutes in sorted(totals.items(), key=lambda pair: (-pair[1], pair[0].casefold())):
        print(f"{topic}: {minutes} minutes")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("studysprint.json"),
                        help="path to the JSON data file")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record a study session")
    add.add_argument("topic", help="subject or activity")
    add.add_argument("minutes", type=int, help="duration in whole minutes")
    add.add_argument("--note", default="", help="optional short note")

    commands.add_parser("list", help="list recorded sessions")
    commands.add_parser("summary", help="summarise study time")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            add_session(args.data, args.topic, args.minutes, args.note)
        elif args.command == "list":
            list_sessions(args.data)
        elif args.command == "summary":
            show_summary(args.data)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
