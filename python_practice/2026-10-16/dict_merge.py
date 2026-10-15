"""Merge mappings with override values taking precedence."""
from collections.abc import Mapping
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")

def merge_settings(defaults: Mapping[K, V], overrides: Mapping[K, V]) -> dict[K, V]:
    """Return a new dict; values in overrides win."""
    return {**defaults, **overrides}

if __name__ == "__main__":
    print(merge_settings({"theme": "light", "timeout": 10}, {"theme": "dark"}))
