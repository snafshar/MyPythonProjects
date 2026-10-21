"""Calculate a compact summary for a numeric sequence."""
from statistics import mean, median, pstdev


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("values must not be empty")
    return {"count": float(len(values)), "mean": mean(values), "median": median(values), "population_stddev": pstdev(values)}


if __name__ == "__main__":
    sample = [12.0, 15.5, 9.0, 18.5, 15.0]
    for key, value in summarize(sample).items():
        print(f"{key}: {value:.2f}")