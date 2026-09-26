"""Bounded reference producer. Deliberately NOT a fast discrete-log solver.

Trial division and orbit enumeration are untrusted discovery operations.
Only checker.verify turns a candidate into an accepted positive certificate.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import gcd, isqrt
from .schema import DEFAULT_LIMITS, Invalid, ResourceLimit, Problem, integer


@dataclass
class Builder:
    factor_budget: int = 100_000
    witness_budget: int = 100_000
    tests: int = 0
    records: dict = field(default_factory=dict)
    factored: dict = field(default_factory=dict)

    def factor(self, n: int) -> list[list[int]]:
        if n in self.factored:
            return [x[:] for x in self.factored[n]]
        original, out, d = n, [], 2
        while d*d <= n:
            self.tests += 1
            if self.tests > self.factor_budget:
                raise ResourceLimit('reference producer trial-division budget exhausted')
            exponent = 0
            while n % d == 0:
                n //= d
                exponent += 1
            if exponent:
                out.append([d, exponent])
            d = 3 if d == 2 else d+2
        if n > 1:
            out.append([n, 1])
        self.factored[original] = out
        return [x[:] for x in out]

    def prove(self, p: int) -> None:
        if p in self.records:
            return
        if p < 2 or self.factor(p) != [[p, 1]]:
            raise Invalid('reference producer requires a prime modulus/factor')
        if p == 2:
            self.records[2] = {'p': 2, 'witness': 1, 'factors': []}
            return
        factors = self.factor(p-1)
        for q, _ in factors:
            self.prove(q)
        for a in range(2, p):
            self.witness_budget -= 1
            if self.witness_budget < 0:
                raise ResourceLimit('reference producer prime-witness budget exhausted')
            if pow(a, p-1, p) == 1 and all(gcd(pow(a, (p-1)//q, p)-1, p) == 1 for q, _ in factors):
                self.records[p] = {'p': p, 'witness': a, 'factors': factors}
                return
        raise Invalid('could not construct a prime proof')


def inverse(A, p):
    """Producer-side Gaussian elimination, independent of checker multiplication."""
    n = len(A)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            raise Invalid('noninvertible recurrence is outside v1')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = pow(rows[col][col], -1, p)
        rows[col] = [(x*scale) % p for x in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [(x-scale*y) % p for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def assemble(problem: Problem, first: int, period: int, builder: Builder | None = None) -> dict:
    """Package supplied candidate values; this function does not prove the claim."""
    b = Builder() if builder is None else builder
    b.prove(problem.p)
    factors = b.factor(period)
    for q, _ in factors:
        b.prove(q)
    return {'schema': 'alc.certificate.v1', 'kind': 'periodic_hits',
            'problem_sha256': problem.fingerprint, 'first': first, 'period': period,
            'period_factors': factors, 'inverse_matrix': inverse(problem.A, problem.p),
            'prime_proofs': [b.records[q] for q in sorted(b.records)]}


def produce(document: dict, max_steps: int = 10_000) -> dict:
    p = Problem.parse(document)
    integer(max_steps, 'max_steps', 1, 1_000_000)
    builder = Builder()
    builder.prove(p.p)
    inverse(p.A, p.p)  # Reject singular input before relying on pure-cycle semantics.
    x, first = p.initial, (0 if p.initial == p.target else None)
    n = len(x)
    for t in range(1, max_steps+1):
        x = tuple((sum(p.A[i][j]*x[j] for j in range(n)) + p.c[i]) % p.p for i in range(n))
        if x == p.initial:
            if first is None:
                return {'status': 'unreachable_enumerated', 'certified': False,
                        'orbit_period': t, 'steps': t,
                        'reason': 'complete orbit was enumerated; no negative certificate format in v1'}
            return {'status': 'candidate', 'certified': False, 'steps': t,
                    'certificate': assemble(p, first, t, builder)}
        if x == p.target and first is None:
            first = t
    return {'status': 'inconclusive', 'certified': False, 'steps': max_steps,
            'reason': 'step_limit; finding one hit without the full period is insufficient'}
