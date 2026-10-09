from statistics import mean, median

def summarize(samples: list[float]) -> dict[str, float]:
    if not samples:
        raise ValueError("samples cannot be empty")
    return {
        "mean": mean(samples),
        "median": median(samples),
        "min": min(samples),
        "max": max(samples),
    }

if __name__ == "__main__":
    print(summarize([10.2, 11.4, 9.8, 12.1, 10.7]))
