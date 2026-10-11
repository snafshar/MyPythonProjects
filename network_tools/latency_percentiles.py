"""Calculate simple latency percentiles from numeric samples."""


def percentile(samples, p):
    values = sorted(samples)
    if not values or not 0 <= p <= 100:
        raise ValueError("samples must be non-empty and p must be 0..100")
    index = (len(values) - 1) * p / 100
    lower, upper = int(index), min(int(index) + 1, len(values) - 1)
    fraction = index - lower
    return values[lower] + (values[upper] - values[lower]) * fraction
