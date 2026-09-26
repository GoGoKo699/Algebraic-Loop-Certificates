"""Bounded, deliberately simple classical producers. No fast discrete log claim.

Certificate verification never imports this module. Generation may exhaust its
limits; UNKNOWN is not an unreachability claim. No result depends on assert.
"""
from __future__ import annotations
from math import gcd
from .arithmetic import dot, mv, rank, solve
from .checker import Limits, InvalidCertificate, instance_hash, parse_instance


class ProducerLimit(RuntimeError):
    pass


class TrialArithmetic:
    def __init__(self, limit=100000):
        if type(limit) is not int or limit < 0:
            raise ValueError('Nonnegative producer effort limit required.')
        self.remaining = limit
        self.work = 0
        self.proofs = {}

    def tick(self):
        if not self.remaining:
            raise ProducerLimit('Trial factorization/witness budget exhausted.')
        self.remaining -= 1
        self.work += 1

    def factor(self, n):
        answer = []
        q = 2
        while q * q <= n:
            self.tick()
            e = 0
            while n % q == 0:
                self.tick()
                n //= q
                e += 1
            if e:
                answer.append([q, e])
            q = 3 if q == 2 else q + 2
        if n > 1:
            answer.append([n, 1])
        return answer

    def prime(self, n):
        if n in self.proofs:
            return
        if self.factor(n) != [[n, 1]]:
            raise InvalidCertificate('Composite modulus or factor is outside the field model.')
        if n == 2:
            self.proofs[n] = {'n': 2}
            return
        factors = self.factor(n - 1)
        for q, _ in factors:
            self.prime(q)
        for base in range(2, n):
            self.tick()
            if pow(base, n - 1, n) == 1 and all(
                gcd(pow(base, (n - 1) // q, n) - 1, n) == 1 for q, _ in factors
            ):
                self.proofs[n] = dict(n=n, base=base, factors=factors)
                return
        raise InvalidCertificate('No primality witness found.')


def produce(instance, max_steps=100000, max_trial_work=100000):
    """Try a span certificate first, then enumerate a bounded full orbit.

    Positive summaries require the complete least period, so finding a first hit
    alone is not reported as a completed certificate.
    """
    if type(max_steps) is not int or max_steps < 0:
        raise ValueError('Nonnegative max_steps required.')
    p, a, c, x, y = parse_instance(instance)
    arithmetic = TrialArithmetic(max_trial_work)
    steps = 0
    try:
        arithmetic.prime(p)
        if rank(a, p) != len(a):
            raise InvalidCertificate('Singular recurrence is outside this producer scope.')
        n = len(a)
        lift = tuple(row + (ci,) for row, ci in zip(a, c)) + ((0,) * n + (1,),)
        start, target = x + (1,), y + (1,)
        krylov, v = [], start
        for _ in range(n + 1):
            krylov.append(v)
            v = mv(lift, v, p)
        separator = solve(krylov + [target], [0] * (n + 1) + [1], n + 1, p)
        if separator is not None:
            claim = dict(kind='outside-span', separator=list(separator))
        else:
            states, first_hit, current = [], None, x
            for t in range(max_steps):
                if current == y and first_hit is None:
                    first_hit = t
                states.append(list(current))
                current = tuple((dot(row, current, p) + ci) % p for row, ci in zip(a, c))
                steps += 1
                if current == x:
                    break
            else:
                raise ProducerLimit('Orbit step budget exhausted before a full return.')
            if first_hit is None:
                claim = dict(kind='cycle-exclusion', states=states)
            else:
                factors = arithmetic.factor(steps)
                for q, _ in factors:
                    arithmetic.prime(q)
                claim = dict(kind='hit', offset=first_hit, period=steps, factors=factors)
        certificate = dict(schema='alc-certificate-1', instance_sha256=instance_hash(instance),
                           prime_proofs=[arithmetic.proofs[p] for p in sorted(arithmetic.proofs)],
                           claim=claim)
        return dict(status='candidate', certificate=certificate,
                    metrics=dict(orbit_steps=steps, trial_work=arithmetic.work))
    except ProducerLimit as exc:
        return dict(status='unknown', reason=str(exc),
                    metrics=dict(orbit_steps=steps, trial_work=arithmetic.work))
