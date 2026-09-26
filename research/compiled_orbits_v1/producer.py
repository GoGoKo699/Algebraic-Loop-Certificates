"""Source-only certificate producer; construction may require difficult algebra.

No target is an input. One prime-power hub graph avoids redundant alignments.
The checker independently verifies the graph coverage, never trusts the policy.
"""
from math import gcd
from alc.schema import Invalid, ResourceLimit, digest
from research.complete_orbits_v1 import algebra as alg
from research.complete_orbits_v1.producer import (Budget, PrimeBuilder,
    factor_polynomial, matrix_inverse, bsgs)
from research.separating_invariants_v1.producer import common_algebra
from research.separating_invariants_v1.checker import cyclic_basis
from .checker import parse_source


def hub_edges(factorizations):
    """For each prime choose a maximal-valuation vertex and join its support."""
    vals = [dict(v) for v in factorizations]
    primes = sorted({q for v in vals for q in v})
    edges = set()
    for q in primes:
        support = [i for i, v in enumerate(vals) if q in v]
        hub = min(support, key=lambda i: (-vals[i][q], i))
        for i in support:
            if i != hub:
                edges.add(tuple(sorted((i, hub))))
    return sorted(edges)


def produce(document, max_work=1000000, supplied_factors=None):
    if type(max_work) is not int or max_work < 0:
        raise ValueError('Nonnegative effort limit required.')
    budget = Budget(max_work)
    pb = PrimeBuilder(budget)
    try:
        problem = parse_source(document)
        p = problem.p
        pb.prime(p)
        inv = matrix_inverse(problem.A, p)
        _, mu = cyclic_basis(problem)
        factors = factor_polynomial(mu, p, budget) if supplied_factors is None else supplied_factors
        records = []
        for f, e in factors:
            f = tuple(f)
            if not alg.irreducible(f, p):
                raise Invalid('Invalid supplied polynomial factor.')
            alpha = alg.rem((0, 1), f, p)
            order = p**(len(f)-1)-1
            for q, _ in pb.factor(order):
                while order % q == 0 and alg.power(alpha, order//q, f, p) == (1,):
                    order //= q
            fac = pb.factor(order)
            for q, _ in fac:
                pb.prime(q)
            records.append({'factor': list(f), 'multiplicity': e, 'order': order, 'order_factors': fac})
        edges = hub_edges([r['order_factors'] for r in records])
        comparisons = []
        for i, j in edges:
            r1, r2 = records[i]['order'], records[j]['order']
            f1, f2 = tuple(records[i]['factor']), tuple(records[j]['factor'])
            D = gcd(r1, r2)
            h, left, right = common_algebra(f1, f2, p, budget)
            w1 = alg.power(left, r1//D, h, p)
            w2 = alg.power(right, r2//D, h, p)
            alignment = bsgs(w2, w1, D, h, p, budget)
            comparisons.append({'i': i, 'j': j, 'algebra_modulus': list(h),
                                'left_root': list(left), 'right_root': list(right),
                                'alignment': alignment})
        cert = {'schema': 'alc.compiled-orbit.v1', 'source_sha256': digest(document),
                'prime_proofs': [pb.proofs[q] for q in sorted(pb.proofs)],
                'inverse_matrix': inv, 'components': records, 'comparisons': comparisons}
        return {'status': 'candidate', 'certificate': cert,
                'metrics': {'base_alignment_log_calls': len(edges), 'target_log_calls': 0,
                            'budgeted_search_work': budget.used, 'trajectory_steps': 0}}
    except ResourceLimit as exc:
        return {'status': 'unknown', 'reason': str(exc)}
