"""Descriptive statistics with no third-party dependencies."""


from math import fsum


def mean(values):
    """Return arithmetic mean; reject an empty collection."""
    items = list(values)
    if not items:
        raise ValueError("mean requires at least one value")
    return fsum(items) / len(items)


def median(values):
    """Return the middle value or average of the two middle values."""
    items = sorted(values)
    if not items:
        raise ValueError("median requires at least one value")
    middle = len(items) // 2
    if len(items) % 2:
        return items[middle]
    return (items[middle - 1] + items[middle]) / 2


def population_variance(values):
    """Return population variance (divide by N, not N-1)."""
    items = list(values)
    center = mean(items)
    return fsum((item - center) ** 2 for item in items) / len(items)


def percentile(values, percent):
    """Return a linearly interpolated percentile for percent in [0, 100]."""
    items = sorted(values)
    if not items:
        raise ValueError("percentile requires at least one value")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    position = (len(items) - 1) * percent / 100
    low = int(position)
    high = min(low + 1, len(items) - 1)
    fraction = position - low
    return items[low] * (1 - fraction) + items[high] * fraction
