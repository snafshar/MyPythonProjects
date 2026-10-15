"""Flatten one level of nested lists."""
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")

def flatten_once(items: Iterable[Iterable[T]]) -> list[T]:
    return [value for group in items for value in group]

if __name__ == "__main__":
    print(flatten_once([[1, 2], [3], [4, 5]]))
