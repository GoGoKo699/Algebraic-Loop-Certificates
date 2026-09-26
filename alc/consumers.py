"""Classical arithmetic on already verified hit schedules. No source simulation."""
from __future__ import annotations
from math import gcd
from .checker import VerifiedSummary


def natural(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(name + ' must be a nonnegative integer.')
    return value


def first_at_least(summary: VerifiedSummary, start: int):
    natural(start, 'start')
    if summary.is_empty:
        return None
    t, r = summary.offset, summary.period
    return t + r * max(0, (start - t + r - 1) // r)


def count_interval(summary: VerifiedSummary, low: int, high: int) -> int:
    natural(low, 'low'); natural(high, 'high')
    if low > high:
        raise ValueError('Require low <= high (inclusive endpoints).')
    first = first_at_least(summary, low)
    return 0 if first is None or first > high else (high - first) // summary.period + 1


def synchronize(left: VerifiedSummary, right: VerifiedSummary) -> VerifiedSummary:
    """Intersection of two certified schedules at the SAME integer time.

    This is not sequential composition of programs or control-flow analysis.
    """
    binding = left.instance_sha256 + '&' + right.instance_sha256
    if left.is_empty or right.is_empty:
        return VerifiedSummary(binding, 'empty-intersection')
    a, m, b, n = left.offset, left.period, right.offset, right.period
    g = gcd(m, n)
    if (b - a) % g:
        return VerifiedSummary(binding, 'incompatible-congruences')
    reduced = n // g
    j = 0 if reduced == 1 else ((b - a) // g * pow(m // g, -1, reduced)) % reduced
    period = m * reduced
    return VerifiedSummary(binding, 'synchronized-schedules', (a + m * j) % period, period)
