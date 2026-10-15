"""Helpers for parsing ISO-8601 timestamps."""
from datetime import datetime, timezone

def parse_timestamp(value: str) -> datetime:
    """Parse ISO text; treat naive values as UTC by explicit policy."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed

def to_utc_iso(value: str) -> str:
    return parse_timestamp(value).astimezone(timezone.utc).isoformat()

if __name__ == "__main__":
    print(to_utc_iso("2026-10-15T12:00:00Z"))
