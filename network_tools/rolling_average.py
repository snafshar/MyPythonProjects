"""Compute a simple trailing rolling average."""

def rolling_average(values, window):
    data = list(values)
    if window < 1 or window > len(data):
        raise ValueError('window must be between 1 and the number of values')
    return [sum(data[i-window+1:i+1]) / window for i in range(window-1, len(data))]
