"""Retry a callable a bounded number of times."""
from collections.abc import Callable
from time import sleep
from typing import TypeVar

T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int = 3, delay: float = 0.25) -> T:
    if attempts < 1 or delay < 0:
        raise ValueError("attempts must be >= 1 and delay must be >= 0")
    for attempt in range(attempts):
        try:
            return operation()
        except Exception:
            if attempt == attempts - 1:
                raise
            sleep(delay * (attempt + 1))
    raise RuntimeError("unreachable")