"""Small dependency-free helpers for summarising network measurements."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkHealth:
    latency_ms: float
    packet_loss_percent: float

    @property
    def status(self) -> str:
        if self.packet_loss_percent >= 10 or self.latency_ms >= 200:
            return "poor"
        if self.packet_loss_percent >= 2 or self.latency_ms >= 100:
            return "degraded"
        return "healthy"


def summarise(latency_ms: float, packet_loss_percent: float) -> NetworkHealth:
    if latency_ms < 0:
        raise ValueError("latency_ms must be non-negative")
    if not 0 <= packet_loss_percent <= 100:
        raise ValueError("packet_loss_percent must be between 0 and 100")
    return NetworkHealth(latency_ms, packet_loss_percent)


if __name__ == "__main__":
    sample = summarise(42.0, 0.5)
    print(f"latency={sample.latency_ms:.1f} ms")
    print(f"loss={sample.packet_loss_percent:.1f}%")
    print(f"status={sample.status}")
