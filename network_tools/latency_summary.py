"""Summarise repeated non-negative latency measurements in milliseconds."""
from statistics import mean, median

def summarise_latency(samples_ms):
    values = list(samples_ms)
    if not values:
        raise ValueError('at least one latency sample is required')
    if any(not isinstance(x, (int, float)) or x < 0 for x in values):
        raise ValueError('latency samples must be non-negative numbers')
    return {'count': len(values), 'min_ms': min(values), 'median_ms': median(values),
            'mean_ms': mean(values), 'max_ms': max(values)}
