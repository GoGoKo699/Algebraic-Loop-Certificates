"""Arithmetic consumers of an already verified positive hit set; no simulation."""
from __future__ import annotations
from dataclasses import dataclass
from math import gcd
from .schema import Invalid
from .checker import VerifiedHits


def nat(x, name):
    if type(x) is not int or x < 0:
        raise Invalid(name + ' must be a nonnegative integer')
    return x


def first_at_or_after(first: int, period: int, start: int) -> int:
    nat(start, 'start')
    return first + period*max(0, (start-first+period-1)//period)


def window(hits: VerifiedHits, start: int, through: int) -> dict:
    nat(start, 'start'); nat(through, 'through')
    if through < start:
        raise Invalid('through must be at least start; endpoints are inclusive')
    first = first_at_or_after(hits.first, hits.period, start)
    count = 0 if first > through else (through-first)//hits.period+1
    return {'from': start, 'through': through, 'inclusive': True,
            'count': count, 'first': first if count else None,
            'last': first+(count-1)*hits.period if count else None,
            'next_at_or_after_from': first}


def intersect_schedule(hits: VerifiedHits, residue: int, period: int) -> tuple[int, int] | None:
    """Intersect with a supplied arithmetic schedule, not a second certified loop."""
    nat(residue, 'residue'); nat(period, 'schedule period')
    if period == 0 or residue >= period:
        raise Invalid('schedule requires 0 <= residue < positive period')
    g = gcd(hits.period, period)
    delta = residue-hits.first
    if delta % g:
        return None
    m = period//g
    multiplier = 0 if m == 1 else (delta//g * pow(hits.period//g, -1, m)) % m
    combined = hits.period*m
    return ((hits.first+hits.period*multiplier) % combined, combined)
