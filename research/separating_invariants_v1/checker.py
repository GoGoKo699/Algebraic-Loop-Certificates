"""Check invariant construction, then evaluate it on independently supplied states.

Three schemes: the initial cyclic span; a power preimage of a cyclic unipotent
subgroup; equal equivariant powers in a commutative quotient algebra. No search,
polynomial factoring/irreducibility test, order-factor proof, or target log.
The inherited proof that p is prime is still required. No code formalization.
"""
from dataclasses import dataclass
from alc.schema import (Problem, DEFAULT_LIMITS, Invalid, ResourceLimit,
                        keys, integer, matrix, vector, digest)
from alc.checker import prime_proofs, product, identity
from research.complete_orbits_v1 import algebra as alg


def source_hash(document):
    source = dict(document)
    source.pop('target', None)
    return digest(source)


def evaluate(poly, element, modulus, p):
    """Horner evaluation in F_p[Z]/(modulus)."""
    value = ()
    for c in reversed(poly):
        value = alg.add(alg.mmul(value, element, modulus, p), (c,), p)
    return value


def polynomial(raw, p, max_degree, label, limits):
    if type(raw) is not list or len(raw) > max_degree+1:
        raise Invalid(label+': polynomial degree limit')
    result = tuple(integer(x, label, 0, p-1, limits) for x in raw)
    if result and result[-1] == 0:
        raise Invalid(label+': trailing zero')
    return result


def monic(raw, p, bound, label, limits):
    result = polynomial(raw, p, bound, label, limits)
    if len(result) < 2 or result[-1] != 1:
        raise Invalid(label+': positive-degree monic polynomial required')
    return result


def cyclic_basis(problem):
    p = problem.p
    n = len(problem.A)
    T = tuple(row+(c,) for row, c in zip(problem.A, problem.c)) + ((0,)*n+(1,),)
    v = problem.initial+(1,)
    basis = []
    for _ in range(n+2):
        coefficients = alg.solve_columns(basis, v, p)
        if coefficients is not None:
            return tuple(basis), tuple(-a % p for a in coefficients)+(1,)
        basis.append(v)
        v = alg.mv(T, v, p)
    raise ArithmeticError('Cyclic-dimension bound failed.')


@dataclass(frozen=True)
class CheckedInvariant:
    """A checked predicate, NOT a declaration that every satisfying state is reachable.

    Instances should be obtained through compile_invariant. The returned object
    is an in-process result, not a secure object capability or signed artifact.
    """
    problem: Problem
    binding: str
    basis: tuple
    mu: tuple
    kind: str
    parameters: tuple
    limits: object

    def contains(self, state):
        p = self.problem.p
        y = vector(state, len(self.problem.A), p, 'queried state', self.limits)
        coefficients = alg.solve_columns(self.basis, y+(1,), p)
        if coefficients is None:
            return False
        beta = alg.trim(coefficients, p)
        if self.kind == 'cyclic-span':
            return True
        if self.kind == 'power-kernel':
            divisor, exponent, u = self.parameters
            value = alg.power(beta, exponent, divisor, p)
            log, _, _, _ = alg.unipotent_log(u, value, divisor, p)
            return log is not None
        modulus, left, right, e1, e2 = self.parameters
        y1 = alg.power(evaluate(beta, left, modulus, p), e1, modulus, p)
        y2 = alg.power(evaluate(beta, right, modulus, p), e2, modulus, p)
        return y1 == y2

    def query(self, state):
        included = self.contains(state)
        return {'source_sha256': self.binding,
                'status': 'not_excluded' if included else 'unreachable',
                'invariant_kind': self.kind,
                'qualification': 'Membership in the invariant alone is not a reachability proof.'}


def compile_invariant(document, certificate, limits=DEFAULT_LIMITS):
    # The supplied target is syntactically checked, but is not part of the proof
    # binding or of the invariant construction. It can be changed legitimately.
    problem = Problem.parse(document, limits)
    keys(certificate, {'schema','source_sha256','prime_proofs','inverse_matrix',
                       'invariant'}, 'invariant certificate')
    if certificate['schema'] != 'alc.separating-invariant.v1':
        raise Invalid('Wrong invariant schema.')
    binding = source_hash(problem.as_dict())
    if certificate['source_sha256'] != binding:
        raise Invalid('Wrong recurrence/initial-state binding.')
    proven = prime_proofs(certificate['prime_proofs'], limits, {'modular_power_checks': 0})
    if problem.p not in proven:
        raise Invalid('Prime-field evidence missing.')
    n = len(problem.A)
    inv = matrix(certificate['inverse_matrix'], n, problem.p, 'inverse witness', limits)
    if product(problem.A, inv, problem.p) != identity(n) or product(inv, problem.A, problem.p) != identity(n):
        raise Invalid('Wrong inverse witness.')
    basis, mu = cyclic_basis(problem)
    k = len(mu)-1
    data = certificate['invariant']
    if type(data) is not dict or 'kind' not in data:
        raise Invalid('Invariant scheme required.')
    kind = data['kind']
    parameters = ()
    if kind == 'cyclic-span':
        keys(data, {'kind'}, 'cyclic span')
    elif kind == 'power-kernel':
        keys(data, {'kind','divisor','exponent'}, 'power kernel')
        g = monic(data['divisor'], problem.p, k, 'quotient divisor', limits)
        if alg.rem(mu, g, problem.p):
            raise Invalid('Proposed divisor does not divide the cyclic minimal polynomial.')
        exponent = integer(data['exponent'], 'power exponent', 1, limits=limits)
        u = alg.power((0,1), exponent, g, problem.p)
        if alg.power(alg.sub(u, (1,), problem.p), len(g)-1, g, problem.p):
            raise Invalid('The powered generator is not unipotent in this quotient.')
        parameters = (g, exponent, u)
    elif kind == 'equal-powers':
        keys(data, {'kind','algebra_modulus','left_root','right_root',
                    'left_exponent','right_exponent'}, 'equal powers')
        h = monic(data['algebra_modulus'], problem.p, k*k, 'comparison algebra', limits)
        left = polynomial(data['left_root'], problem.p, len(h)-2, 'left root', limits)
        right = polynomial(data['right_root'], problem.p, len(h)-2, 'right root', limits)
        if evaluate(mu, left, h, problem.p) or evaluate(mu, right, h, problem.p):
            raise Invalid('Evaluation maps do not descend from the cyclic quotient.')
        e1 = integer(data['left_exponent'], 'left exponent', 1, limits=limits)
        e2 = integer(data['right_exponent'], 'right exponent', 1, limits=limits)
        if alg.power(left, e1, h, problem.p) != alg.power(right, e2, h, problem.p):
            raise Invalid('The two powers do not have a common update multiplier.')
        parameters = (h, left, right, e1, e2)
    else:
        raise Invalid('Unsupported invariant scheme.')
    return CheckedInvariant(problem, binding, basis, mu, kind, parameters, limits)
