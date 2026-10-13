"""Packet-loss statistics from sent and received packet counts."""


def packet_loss(sent: int, received: int) -> float:
    if sent < 0 or received < 0 or received > sent:
        raise ValueError("require 0 <= received <= sent")
    if sent == 0:
        return 0.0
    return 100.0 * (sent - received) / sent


if __name__ == "__main__":
    print(f"loss: {packet_loss(100, 97):.2f}%")
