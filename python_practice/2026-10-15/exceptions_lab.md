# Python Exception Handling Lab

## Read and run
```python
from pathlib import Path

def read_number(path: Path) -> float:
    try:
        return float(path.read_text(encoding="utf-8").strip())
    except FileNotFoundError as exc:
        raise ValueError(f"input file does not exist: {path}") from exc
    except ValueError as exc:
        raise ValueError(f"input does not contain a valid number: {path}") from exc
```

## Exercises
1. Add a test for a missing file.
2. Add a test for invalid numeric text.
3. Decide which errors should be handled locally and which should reach the caller.
4. Why is catching every exception and silently continuing a bad default?
5. Use temporary files in tests; never depend on a personal absolute path.
