"""Compact dynamic-programming exercises."""


def fibonacci(n):
    """Return the nth Fibonacci number for non-negative n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def minimum_coins(coins, amount):
    """Return the fewest coins needed to form amount, or None if impossible.

    Coin values must be positive integers and amount must be non-negative.
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if any(not isinstance(coin, int) or coin <= 0 for coin in coins):
        raise ValueError("coin values must be positive integers")
    best = [0] + [amount + 1] * amount
    for subtotal in range(1, amount + 1):
        for coin in coins:
            if coin <= subtotal:
                best[subtotal] = min(best[subtotal], best[subtotal - coin] + 1)
    return best[amount] if best[amount] <= amount else None


def lis_length(values):
    """Return the length of the longest strictly increasing subsequence."""
    if not values:
        return 0
    lengths = [1] * len(values)
    for end in range(len(values)):
        for previous in range(end):
            if values[previous] < values[end]:
                lengths[end] = max(lengths[end], lengths[previous] + 1)
    return max(lengths)
