"""A small bounded retry helper with exponential backoff."""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    initial_delay: float = 0.25,
    maximum_delay: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call operation up to attempts times, then re-raise the final error."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if initial_delay < 0 or maximum_delay < 0:
        raise ValueError("delays cannot be negative")

    delay = initial_delay
    for attempt in range(attempts):
        try:
            return operation()
        except retry_on:
            if attempt == attempts - 1:
                raise
            sleep(delay)
            delay = min(delay * 2, maximum_delay)
    raise RuntimeError("unreachable")
