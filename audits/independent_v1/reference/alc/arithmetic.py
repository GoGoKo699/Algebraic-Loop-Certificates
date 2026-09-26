"""Small exact arithmetic kernel shared by producer and checker.

Prime-field validity is established separately; no floating point or randomized
arithmetic is used. This module contains no orbit or discrete-logarithm search.
"""
from __future__ import annotations

Matrix = tuple[tuple[int, ...], ...]
Vector = tuple[int, ...]


def dot(a, b, p: int) -> int:
    return sum(x * y for x, y in zip(a, b)) % p


def mv(a: Matrix, x: Vector, p: int) -> Vector:
    return tuple(dot(row, x, p) for row in a)


def mm(a: Matrix, b: Matrix, p: int) -> Matrix:
    columns = tuple(zip(*b))
    return tuple(tuple(dot(row, col, p) for col in columns) for row in a)


def power_apply(a: Matrix, exponent: int, x: Vector, p: int) -> Vector:
    """Apply a binary-encoded power without enumerating the trajectory."""
    if type(exponent) is not int or exponent < 0:
        raise ValueError('Exponent must be a nonnegative integer.')
    while exponent:
        if exponent & 1:
            x = mv(a, x, p)
        exponent >>= 1
        if exponent:
            a = mm(a, a, p)
    return x


def solve(rows, rhs, variables: int, p: int):
    """Return one solution over F_p, or None; free variables are set to zero."""
    work = [[v % p for v in row] + [b % p] for row, b in zip(rows, rhs)]
    pivots = []
    for col in range(variables):
        pivot = next((j for j in range(len(pivots), len(work)) if work[j][col]), None)
        if pivot is None:
            continue
        k = len(pivots)
        work[k], work[pivot] = work[pivot], work[k]
        inv = pow(work[k][col], -1, p)
        work[k] = [(v * inv) % p for v in work[k]]
        for j in range(len(work)):
            if j != k:
                scale = work[j][col]
                work[j] = [(v - scale * w) % p for v, w in zip(work[j], work[k])]
        pivots.append(col)
    if any(not any(row[:-1]) and row[-1] for row in work):
        return None
    answer = [0] * variables
    for j, col in enumerate(pivots):
        answer[col] = work[j][-1]
    return tuple(answer)


def rank(a: Matrix, p: int) -> int:
    work = [list(row) for row in a]
    count = 0
    for col in range(len(work[0]) if work else 0):
        pivot = next((j for j in range(count, len(work)) if work[j][col]), None)
        if pivot is None:
            continue
        work[count], work[pivot] = work[pivot], work[count]
        inv = pow(work[count][col], -1, p)
        work[count] = [(v * inv) % p for v in work[count]]
        for j in range(count + 1, len(work)):
            scale = work[j][col]
            work[j] = [(v - scale * w) % p for v, w in zip(work[j], work[count])]
        count += 1
    return count
