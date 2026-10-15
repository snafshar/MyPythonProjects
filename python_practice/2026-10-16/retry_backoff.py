"""A bounded retry helper with injectable sleep for tests."""
from collections.abc import Callable
import time
from typing import TypeVar

T = TypeVar("T")

def retry(operation: Callable[[], T], *, attempts: int = 3,
          delay: float = 0.1, sleep: Callable[[float], None] = time.sleep) -> T:
    if attempts < 1:
        raise ValueError("attempts must be positive")
    if delay < 0:
        raise ValueError("delay cannot be negative")
    for index in range(attempts):
        try:
            return operation()
        except Exception:
            if index == attempts - 1:
                raise
            sleep(delay * (2 ** index))
    raise RuntimeError("unreachable")

if __name__ == "__main__":
    print("Import retry() and provide an operation to retry.")
