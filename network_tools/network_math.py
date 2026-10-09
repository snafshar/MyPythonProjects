def packet_loss_percent(sent: int, received: int) -> float:
    if sent < 0 or received < 0 or received > sent:
        raise ValueError("invalid packet counts")
    return 0.0 if sent == 0 else 100.0 * (sent - received) / sent

def bits_per_second(byte_count: int, seconds: float) -> float:
    if byte_count < 0 or seconds <= 0:
        raise ValueError("invalid transfer parameters")
    return byte_count * 8 / seconds
