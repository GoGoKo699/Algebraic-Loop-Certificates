"""Conventional odd-order decision for the same extracted companion matrix.

This comparator needs no supplied exponent, factorization, or full orbit engine.
Circuit binding still requires the same raw-AAG structural check.
"""


def remainder(a, b):
    if b == 0:
        raise ValueError("zero polynomial divisor")
    while a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def gcd(a, b):
    while b:
        a, b = b, remainder(a, b)
    return a


def odd_order(n, taps):
    if type(n) is not int or type(taps) is not int or not 2 <= n <= 64 or not 0 <= taps < 1 << n:
        raise ValueError("unsupported dimension or taps")
    # r'_0 = sum_i taps_i r_i; r'_j = r_(j-1).
    # det(XI-A) = X^n + sum_i taps_i X^(n-1-i).
    f = (1 << n) | sum(((taps >> i) & 1) << (n - 1 - i) for i in range(n))
    derivative = sum(((f >> i) & 1) << (i - 1) for i in range(1, n + 1, 2))
    return bool(f & 1) and gcd(f, derivative) == 1
