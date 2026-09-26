"""Independent deterministic certificate checker. Does NOT import producers.

The JSON objects are untrusted. This is an auditable reference checker, not a
formally verified or denial-of-service-hardened service. Limits bound its input.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from math import gcd
from .arithmetic import dot, mv, power_apply, rank


class InvalidCertificate(ValueError):
    pass


class VerificationLimit(ValueError):
    """A verifier resource policy was exceeded; this is not mathematical falsity."""


@dataclass(frozen=True)
class Limits:
    max_dimension: int = 32
    max_integer_bits: int = 4096
    max_prime_proofs: int = 2048
    max_cycle_states: int = 100000


@dataclass(frozen=True)
class VerifiedSummary:
    """Trusted result returned after checking a certificate for a bound instance."""
    instance_sha256: str
    evidence_kind: str
    offset: int | None = None
    period: int | None = None

    @property
    def is_empty(self) -> bool:
        return self.offset is None

    def as_dict(self) -> dict:
        return dict(instance_sha256=self.instance_sha256, evidence_kind=self.evidence_kind,
                    hit_set='empty' if self.is_empty else 'arithmetic_progression',
                    offset=self.offset, period=self.period)


def integer(value, name: str, limits: Limits, minimum=0) -> int:
    if type(value) is not int or value < minimum:
        raise InvalidCertificate(f'{name}: integer >= {minimum} required; bool is not accepted.')
    if value.bit_length() > limits.max_integer_bits:
        raise VerificationLimit(f'{name}: integer bit limit exceeded.')
    return value


def fields(obj, expected, name):
    if type(obj) is not dict or set(obj) != set(expected):
        raise InvalidCertificate(f'{name}: exact fields {sorted(expected)} required.')


def vector(obj, size, p, name, limits):
    if type(obj) is not list or len(obj) != size:
        raise InvalidCertificate(f'{name}: list of length {size} required.')
    answer = tuple(integer(v, name, limits) for v in obj)
    if any(v >= p for v in answer):
        raise InvalidCertificate(f'{name}: noncanonical residue (must be 0 <= x < p).')
    return answer


def parse_instance(obj, limits=Limits()):
    fields(obj, ('schema', 'modulus', 'matrix', 'translation', 'initial', 'target'), 'instance')
    if obj['schema'] != 'alc-instance-1':
        raise InvalidCertificate('Unsupported instance schema.')
    p = integer(obj['modulus'], 'modulus', limits, 2)
    a = obj['matrix']
    if type(a) is not list or not a:
        raise InvalidCertificate('Nonempty square matrix required.')
    n = len(a)
    if n > limits.max_dimension:
        raise VerificationLimit('Matrix dimension limit exceeded.')
    a = tuple(vector(row, n, p, 'matrix row', limits) for row in a)
    c = vector(obj['translation'], n, p, 'translation', limits)
    x = vector(obj['initial'], n, p, 'initial', limits)
    y = vector(obj['target'], n, p, 'target', limits)
    return p, a, c, x, y


def instance_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True).encode()).hexdigest()


def factorization(items, expected, certified_primes, limits):
    if type(items) is not list or len(items) > expected.bit_length():
        raise InvalidCertificate('Factor list malformed or unnecessarily long.')
    product, previous, primes = 1, 1, []
    for item in items:
        if type(item) is not list or len(item) != 2:
            raise InvalidCertificate('Each factor must be [prime, exponent].')
        q = integer(item[0], 'factor prime', limits, 2)
        e = integer(item[1], 'factor exponent', limits, 1)
        if q <= previous or q not in certified_primes or e > expected.bit_length():
            raise InvalidCertificate('Factors must be sorted, distinct, and proven prime.')
        previous = q
        product *= q ** e
        if product > expected:
            raise InvalidCertificate('Factor product exceeds claimed integer.')
        primes.append(q)
    if product != expected:
        raise InvalidCertificate('Incomplete or incorrect factorization.')
    return primes


def check_primes(proofs, limits=Limits()):
    """Lucas/Pratt certificates with fully factored n-1 and a common witness."""
    if type(proofs) is not list:
        raise InvalidCertificate('prime_proofs must be a list.')
    if len(proofs) > limits.max_prime_proofs:
        raise VerificationLimit('Too many prime proofs.')
    proven, last = set(), 1
    for proof in proofs:
        if type(proof) is not dict or 'n' not in proof:
            raise InvalidCertificate('Malformed prime proof.')
        n = integer(proof['n'], 'prime', limits, 2)
        if n <= last:
            raise InvalidCertificate('Prime proofs must be distinct and sorted.')
        if n == 2:
            fields(proof, ('n',), 'base prime proof')
        else:
            fields(proof, ('n', 'base', 'factors'), 'prime proof')
            qs = factorization(proof['factors'], n - 1, proven, limits)
            base = integer(proof['base'], 'primality witness', limits, 2)
            if base >= n or pow(base, n - 1, n) != 1:
                raise InvalidCertificate('Invalid Fermat/primality witness.')
            for q in qs:
                if gcd(pow(base, (n - 1) // q, n) - 1, n) != 1:
                    raise InvalidCertificate('Insufficient multiplicative order for primality.')
        proven.add(n)
        last = n
    return proven


def verify(instance, certificate, limits=Limits()) -> VerifiedSummary:
    p, a, c, x, y = parse_instance(instance, limits)
    fields(certificate, ('schema', 'instance_sha256', 'prime_proofs', 'claim'), 'certificate')
    if certificate['schema'] != 'alc-certificate-1':
        raise InvalidCertificate('Unsupported certificate schema.')
    digest = instance_hash(instance)
    if certificate['instance_sha256'] != digest:
        raise InvalidCertificate('Certificate is bound to a different instance.')
    primes = check_primes(certificate['prime_proofs'], limits)
    if p not in primes:
        raise InvalidCertificate('No valid proof that the modulus is prime.')
    if rank(a, p) != len(a):
        raise InvalidCertificate('Only invertible recurrences are supported.')
    n = len(a)
    lift = tuple(row + (shift,) for row, shift in zip(a, c)) + ((0,) * n + (1,),)
    start, target = x + (1,), y + (1,)
    claim = certificate['claim']
    if type(claim) is not dict or 'kind' not in claim:
        raise InvalidCertificate('Malformed claim.')
    kind = claim['kind']
    if kind == 'hit':
        fields(claim, ('kind', 'offset', 'period', 'factors'), 'hit claim')
        t = integer(claim['offset'], 'offset', limits)
        r = integer(claim['period'], 'period', limits, 1)
        if t >= r:
            raise InvalidCertificate('Offset must be canonical: 0 <= t < period.')
        factors = factorization(claim['factors'], r, primes, limits)
        if power_apply(lift, t, start, p) != target:
            raise InvalidCertificate('Claimed target hit is false.')
        if power_apply(lift, r, start, p) != start:
            raise InvalidCertificate('Claimed period does not return to the initial state.')
        if any(power_apply(lift, r // q, start, p) == start for q in factors):
            raise InvalidCertificate('Claimed period is not minimal.')
        return VerifiedSummary(digest, kind, t, r)
    if kind == 'outside-span':
        fields(claim, ('kind', 'separator'), 'outside-span claim')
        w = vector(claim['separator'], n + 1, p, 'separator', limits)
        v = start
        for _ in range(n + 1):
            if dot(w, v, p):
                raise InvalidCertificate('Separator does not annihilate the Krylov span.')
            v = mv(lift, v, p)
        if not dot(w, target, p):
            raise InvalidCertificate('Separator does not distinguish the target.')
        return VerifiedSummary(digest, kind)
    if kind == 'cycle-exclusion':
        fields(claim, ('kind', 'states'), 'cycle-exclusion claim')
        states = claim['states']
        if type(states) is not list or not states:
            raise InvalidCertificate('Nonempty closed trajectory required.')
        if len(states) > limits.max_cycle_states:
            raise VerificationLimit('Explicit cycle length exceeds verifier policy.')
        current = x
        for raw in states:
            s = vector(raw, n, p, 'cycle state', limits)
            if s != current or s == y:
                raise InvalidCertificate('Invalid trajectory or target appears in exclusion witness.')
            current = tuple((dot(row, s, p) + ci) % p for row, ci in zip(a, c))
        if current != x:
            raise InvalidCertificate('Exclusion trajectory is not closed.')
        return VerifiedSummary(digest, kind)
    raise InvalidCertificate('Unknown claim kind; no untrusted status is accepted.')
