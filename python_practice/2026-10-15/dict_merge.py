"""Merge mappings while making precedence explicit."""
from collections.abc import Mapping
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def merge_settings(defaults: Mapping[K, V], overrides: Mapping[K, V]) -> dict[K, V]:
    """Return a new mapping; values in overrides take precedence."""
    return {**defaults, **overrides}


if __name__ == "__main__":
    base = {"theme": "light", "timeout": 10}
    custom = {"theme": "dark"}
    print(merge_settings(base, custom))
