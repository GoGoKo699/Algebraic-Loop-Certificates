"""Independent positive-certificate checker: no orbit enumeration or factoring.

Trusted computation uses exact integer arithmetic, explicit matrix products,
modular powering, and supplied Lucas-Pratt primality proofs. It never imports
producer.py. A rejected certificate says nothing about target unreachability.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import gcd
from .schema import DEFAULT_LIMITS, Invalid, Limits, ResourceLimit, Problem, integer, keys, matrix


def product(A, B, p):
    cols = tuple(zip(*B))
    return tuple(tuple(sum(a*b for a, b in zip(row, col)) % p for col in cols) for row in A)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def advance(problem: Problem, exponent: int, stats: dict) -> tuple[int, ...]:
    """Homogeneous-coordinate powering, logarithmic in the supplied exponent."""
    n = len(problem.A)
    power = tuple(tuple(row) + (c,) for row, c in zip(problem.A, problem.c))
    power += ((0,)*n + (1,),)
    state = problem.initial + (1,)
    stats['power_checks'] += 1
    while exponent:
        if exponent & 1:
            state = tuple(sum(a*b for a, b in zip(row, state)) % problem.p for row in power)
            stats['matrix_vector_products'] += 1
        exponent >>= 1
        if exponent:
            power = product(power, power, problem.p)
            stats['matrix_squares'] += 1
    if state[-1] != 1:
        raise Invalid('affine-coordinate invariant failed')
    return state[:-1]


def factorization(value: int, data, proven: set[int], limits: Limits) -> tuple[int, ...]:
    if type(data) is not list:
        raise Invalid('factor list required')
    if len(data) > limits.max_factors:
        raise ResourceLimit('factor list limit exceeded')
    remaining = value
    last = 1
    primes = []
    for pair in data:
        if type(pair) is not list or len(pair) != 2:
            raise Invalid('each factor is [proved_prime, positive_exponent]')
        q = integer(pair[0], 'factor prime', 2, limits=limits)
        e = integer(pair[1], 'factor exponent', 1, limits=limits)
        if q <= last or q not in proven:
            raise Invalid('factors must be distinct, sorted, and already proved prime')
        if e > value.bit_length():
            raise Invalid('factor exponent cannot divide the claimed integer')
        for _ in range(e):
            if remaining % q:
                raise Invalid('factorization is not exact')
            remaining //= q
        last = q
        primes.append(q)
    if remaining != 1:
        raise Invalid('incomplete factorization')
    return tuple(primes)


def prime_proofs(records, limits: Limits, stats: dict) -> set[int]:
    """Check an ascending proof DAG; leaves and every factor must be justified."""
    if type(records) is not list:
        raise Invalid('prime_proofs must be a list')
    if len(records) > limits.max_prime_records:
        raise ResourceLimit('prime proof record limit exceeded')
    proven: set[int] = set()
    last = 1
    for rec in records:
        keys(rec, {'p', 'witness', 'factors'}, 'prime proof')
        p = integer(rec['p'], 'proved number', 2, limits=limits)
        if p <= last:
            raise Invalid('prime proofs must be strictly increasing')
        a = integer(rec['witness'], 'prime witness', 1, p-1, limits)
        if p == 2:
            if a != 1 or rec['factors'] != []:
                raise Invalid('base proof for 2 must have witness 1 and no factors')
        else:
            qs = factorization(p-1, rec['factors'], proven, limits)
            if pow(a, p-1, p) != 1:
                raise Invalid('failed prime power identity')
            for q in qs:
                if gcd(pow(a, (p-1)//q, p)-1, p) != 1:
                    raise Invalid('failed prime-order exclusion')
            stats['modular_power_checks'] += 1+len(qs)
        proven.add(p)
        last = p
    stats['prime_records'] = len(proven)
    return proven


@dataclass(frozen=True)
class VerifiedHits:
    """Use checker.verify to create this result; arithmetic consumers do not prove it."""
    problem_sha256: str
    first: int
    period: int
    stats: dict

    def as_dict(self) -> dict:
        return {'status': 'valid', 'claim': 'complete_positive_hit_set',
                'problem_sha256': self.problem_sha256,
                'first': self.first, 'period': self.period,
                'hit_set': 'first + j * period for every integer j >= 0',
                'checks': dict(self.stats)}


def verify(problem_document: dict, certificate: dict,
           limits: Limits = DEFAULT_LIMITS) -> VerifiedHits:
    problem = Problem.parse(problem_document, limits)
    keys(certificate, {'schema', 'kind', 'problem_sha256', 'first', 'period',
                      'period_factors', 'inverse_matrix', 'prime_proofs'}, 'certificate')
    if certificate['schema'] != 'alc.certificate.v1' or certificate['kind'] != 'periodic_hits':
        raise Invalid('unknown certificate type; v1 verifies positive hit sets only')
    if certificate['problem_sha256'] != problem.fingerprint:
        raise Invalid('certificate does not match the independently supplied problem')
    stats = {'prime_records': 0, 'modular_power_checks': 0, 'power_checks': 0,
             'matrix_vector_products': 0, 'matrix_squares': 0, 'inverse_products': 0}
    proven = prime_proofs(certificate['prime_proofs'], limits, stats)
    if problem.p not in proven:
        raise Invalid('field modulus lacks a valid primality proof')
    n = len(problem.A)
    inverse = matrix(certificate['inverse_matrix'], n, problem.p, 'inverse_matrix', limits)
    unit = identity(n)
    if product(problem.A, inverse, problem.p) != unit or product(inverse, problem.A, problem.p) != unit:
        raise Invalid('invalid inverse witness or noninvertible recurrence')
    stats['inverse_products'] = 2
    r = integer(certificate['period'], 'period', 1, limits=limits)
    if r > problem.p**n:
        raise Invalid('claimed point period exceeds the finite state count')
    t0 = integer(certificate['first'], 'first', 0, r-1, limits)
    qs = factorization(r, certificate['period_factors'], proven, limits)
    if advance(problem, r, stats) != problem.initial:
        raise Invalid('claimed period does not return to the initial state')
    for q in qs:
        if advance(problem, r//q, stats) == problem.initial:
            raise Invalid('claimed period is not the least period')
    if advance(problem, t0, stats) != problem.target:
        raise Invalid('claimed first time does not hit the target')
    return VerifiedHits(problem.fingerprint, t0, r, stats)
