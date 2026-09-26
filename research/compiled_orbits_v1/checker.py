"""Check a source-only certificate, then recognize its ENTIRE initial orbit.

Compilation checks factor completeness, exact orders, and congruence coverage.
Queries use no factor search, irreducibility test, or finite-field target log.
A query decides membership, not the iteration index. No producer is imported.
"""
from dataclasses import dataclass
from math import gcd, lcm
from alc.schema import (Problem, DEFAULT_LIMITS, Invalid, keys, integer, matrix,
                        vector, digest)
from alc.checker import prime_proofs, factorization, product, identity
from research.complete_orbits_v1 import algebra as alg
from research.separating_invariants_v1.checker import (
    cyclic_basis, evaluate, polynomial, monic)


def parse_source(document, limits=DEFAULT_LIMITS):
    keys(document, {'schema', 'field', 'matrix', 'offset', 'initial'}, 'orbit source')
    if document['schema'] != 'alc.orbit-source.v1':
        raise Invalid('Wrong target-free source schema.')
    temporary = dict(document, schema='alc.problem.v1', target=document['initial'])
    return Problem.parse(temporary, limits)


def coverage_ok(factorizations, edges):
    """Exact criterion: every prime-power support induces a connected graph.

    Input factorizations are ALREADY verified. Singletons/empty supports impose
    no edge obligation. No full graph connectivity assumption is substituted.
    """
    valuations = [dict(f) for f in factorizations]
    primes = {q for values in valuations for q in values}
    for q in primes:
        levels = {values.get(q, 0) for values in valuations} - {0}
        # Supports change only at the positive valuations appearing here.
        for level in levels:
            vertices = {i for i, v in enumerate(valuations) if v.get(q, 0) >= level}
            if len(vertices) < 2:
                continue
            reached = {min(vertices)}
            while True:
                more = set(reached)
                for i, j in edges:
                    if i in vertices and j in vertices and (i in reached or j in reached):
                        more.update((i, j))
                if more == reached:
                    break
                reached = more
            if reached != vertices:
                return False
    return True


@dataclass(frozen=True)
class CompiledOrbit:
    """Created by compile_orbit, not a hardened unforgeable object capability.

    The serialized proof must be rechecked when loaded in another process.
    Reaching a state and knowing its first hit time are different results.
    """
    problem: Problem
    binding: str
    basis: tuple
    left_inverse: tuple
    mu: tuple
    components: tuple
    comparisons: tuple
    semisimple_period: int
    unipotent_generator: tuple
    point_period: int
    limits: object

    def query(self, state):
        p = self.problem.p
        y = vector(state, len(self.problem.A), p, 'target', self.limits) + (1,)
        coefficients = tuple(sum(a*b for a, b in zip(row, y)) % p for row in self.left_inverse)
        replay = tuple(sum(self.basis[j][i]*coefficients[j] for j in range(len(coefficients))) % p
                       for i in range(len(y)))
        def result(member, reason):
            return {'source_sha256': self.binding, 'verified': True,
                    'status': 'reachable' if member else 'unreachable',
                    'reason': reason, 'point_period': self.point_period,
                    'first_hit_computed': False}
        if replay != y:
            return result(False, 'outside_cyclic_span')
        beta = alg.trim(coefficients, p)
        for f, multiplicity, order in self.components:
            if alg.power(beta, order, f, p) != (1,):
                return result(False, 'local_subgroup_obstruction')
        for i, j, h, left, right, exponent_left, exponent_right in self.comparisons:
            lhs = alg.power(evaluate(beta, left, h, p), exponent_left, h, p)
            rhs = alg.power(evaluate(beta, right, h, p), exponent_right, h, p)
            if lhs != rhs:
                return result(False, 'incompatible_local_times')
        powered = alg.power(beta, self.semisimple_period, self.mu, p)
        digit, _, _, _ = alg.unipotent_log(self.unipotent_generator, powered, self.mu, p)
        if digit is None:
            return result(False, 'principal_unit_obstruction')
        return result(True, 'all_orbit_conditions')


def compile_orbit(document, certificate, limits=DEFAULT_LIMITS):
    problem = parse_source(document, limits)
    keys(certificate, {'schema', 'source_sha256', 'prime_proofs', 'inverse_matrix',
                       'components', 'comparisons'}, 'compiled orbit certificate')
    if certificate['schema'] != 'alc.compiled-orbit.v1':
        raise Invalid('Wrong compiled orbit schema.')
    binding = digest(document)
    if certificate['source_sha256'] != binding:
        raise Invalid('Wrong source binding.')
    proven = prime_proofs(certificate['prime_proofs'], limits, {'modular_power_checks': 0})
    p = problem.p
    if p not in proven:
        raise Invalid('Unproved prime field.')
    n = len(problem.A)
    inv = matrix(certificate['inverse_matrix'], n, p, 'inverse matrix', limits)
    if product(problem.A, inv, p) != identity(n) or product(inv, problem.A, p) != identity(n):
        raise Invalid('False inverse witness.')
    basis, mu = cyclic_basis(problem)
    k = len(mu)-1
    raw = certificate['components']
    if type(raw) is not list or not 1 <= len(raw) <= k:
        raise Invalid('Nonempty complete primary decomposition required.')
    components, factorizations, seen, expanded = [], [], set(), (1,)
    for rec in raw:
        keys(rec, {'factor', 'multiplicity', 'order', 'order_factors'}, 'component')
        f = monic(rec['factor'], p, k, 'primary factor', limits)
        if not f[0] or f in seen:
            raise Invalid('Distinct nonzero-constant factors required.')
        seen.add(f)
        e = integer(rec['multiplicity'], 'multiplicity', 1, k, limits)
        if len(expanded)-1 + (len(f)-1)*e > k or not alg.irreducible(f, p):
            raise Invalid('Wrong factor degree or reducible field polynomial.')
        for _ in range(e):
            expanded = alg.mul(expanded, f, p)
        order = integer(rec['order'], 'field order', 1, p**(len(f)-1)-1, limits)
        primes = factorization(order, rec['order_factors'], proven, limits)
        alpha = alg.rem((0, 1), f, p)
        if alg.power(alpha, order, f, p) != (1,) or any(
                alg.power(alpha, order//q, f, p) == (1,) for q in primes):
            raise Invalid('Nonexact field-element order.')
        components.append((f, e, order))
        factorizations.append(tuple(tuple(v) for v in rec['order_factors']))
    if expanded != mu:
        raise Invalid('Missing or false primary components.')
    raw_edges = certificate['comparisons']
    max_edges = len(components)*(len(components)-1)//2
    if type(raw_edges) is not list or len(raw_edges) > max_edges:
        raise Invalid('Invalid comparison count.')
    edges, comparisons = set(), []
    for rec in raw_edges:
        keys(rec, {'i', 'j', 'algebra_modulus', 'left_root', 'right_root', 'alignment'}, 'comparison')
        i = integer(rec['i'], 'left index', 0, len(components)-1, limits)
        j = integer(rec['j'], 'right index', i+1, len(components)-1, limits)
        if (i, j) in edges:
            raise Invalid('Duplicate comparison.')
        edges.add((i, j))
        f1, _, m1 = components[i]
        f2, _, m2 = components[j]
        common = gcd(m1, m2)
        if common == 1:
            raise Invalid('Unnecessary coprime comparison.')
        h = monic(rec['algebra_modulus'], p, (len(f1)-1)*(len(f2)-1), 'comparison algebra', limits)
        left = polynomial(rec['left_root'], p, len(h)-2, 'left root', limits)
        right = polynomial(rec['right_root'], p, len(h)-2, 'right root', limits)
        # A unital map from a proved field to this nonzero quotient is injective.
        # H itself need NOT be irreducible for the implication to be sound.
        if evaluate(f1, left, h, p) or evaluate(f2, right, h, p):
            raise Invalid('Wrong component evaluation roots.')
        c = integer(rec['alignment'], 'alignment', 1, common-1, limits)
        if gcd(c, common) != 1:
            raise Invalid('Alignment is not a unit modulo the common order.')
        e1, e2 = m1//common, (m2//common)*c
        if alg.power(left, e1, h, p) != alg.power(right, e2, h, p):
            raise Invalid('False common generator relation.')
        comparisons.append((i, j, h, left, right, e1, e2))
    if not coverage_ok(factorizations, edges):
        raise Invalid('Missing prime-power compatibility coverage.')
    m = lcm(*(r for _, _, r in components))
    x = alg.rem((0, 1), mu, p)
    u = alg.power(x, m, mu, p)
    if alg.power(alg.sub(u, (1,), p), k, mu, p):
        raise Invalid('Unipotent residual check failed.')
    _, ppart, _, _ = alg.unipotent_log(u, (1,), mu, p)
    period = m*ppart
    if period > p**n:
        raise Invalid('Point period exceeds state count.')
    # Recompute a left inverse once. Query replay rejects states outside the span.
    transposed_columns = tuple(zip(*basis))
    left_inverse = tuple(alg.solve_columns(transposed_columns,
                         tuple(int(i == j) for i in range(k)), p) for j in range(k))
    if any(row is None for row in left_inverse):
        raise ArithmeticError('Independent cyclic basis lost rank.')
    return CompiledOrbit(problem, binding, basis, left_inverse, mu, tuple(components),
                         tuple(comparisons), m, u, period, limits)
