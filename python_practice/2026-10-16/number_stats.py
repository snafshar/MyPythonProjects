"""Compute basic descriptive statistics for finite numbers."""
import math
from statistics import mean, median

def summarize(values: list[float]) -> dict[str, float | int]:
    cleaned = [value for value in values if math.isfinite(value)]
    if not cleaned:
        raise ValueError("at least one finite number is required")
    return {"count": len(cleaned), "min": min(cleaned), "max": max(cleaned),
            "mean": mean(cleaned), "median": median(cleaned)}

if __name__ == "__main__":
    print(summarize([3.0, 5.0, 8.0, 10.0]))
