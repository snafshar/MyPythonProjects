"""Small, dependency-free network throughput calculations."""

def throughput_mbps(bytes_received: int, elapsed_seconds: float) -> float:
    """Return decimal megabits per second from bytes and elapsed seconds."""
    if bytes_received < 0:
        raise ValueError('bytes_received must be non-negative')
    if elapsed_seconds <= 0:
        raise ValueError('elapsed_seconds must be positive')
    return bytes_received * 8 / elapsed_seconds / 1_000_000

if __name__ == '__main__':
    print(f'{throughput_mbps(12_500_000, 2):.2f} Mbps')
