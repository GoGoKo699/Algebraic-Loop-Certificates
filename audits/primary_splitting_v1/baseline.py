"""Matched CRT-projector query path for the existing checked prime-power source.

This is a comparative adapter, NOT an independently developed full compiler.
Normalization, verified residue representation and p-group arithmetic are shared
and explicitly charged. The only replaced layer is the membership reduction.
No new proof format or production API is introduced.
"""
from dataclasses import dataclass
from alc.schema import Invalid, vector
from research.prime_power_compilation_v1 import module as arithmetic


def projectors(m, p_power):
    """CRT idempotents for coprime positive integers, without factor search."""
    from math import gcd
    if any(type(x) is not int or x < 1 for x in (m, p_power)):
        raise Invalid('Positive exact integer factors required.')
    if gcd(m, p_power) != 1:
        raise Invalid('CRT factors must be coprime.')
    exponent = m * p_power
    prime_to_p = 0 if m == 1 else p_power * pow(p_power, -1, m)
    p_primary = (1 - prime_to_p) % exponent
    return prime_to_p, p_primary


@dataclass(frozen=True)
class ProjectorBaseline:
    """Source-only projector data derived from an already verified compilation.

    Like the existing objects this is not an unforgeable security capability.
    Only use a source returned by the existing checked compiler. The parameter
    P bounds p-orders of admissible TARGETS, not merely the source order.
    """
    compiled: object
    p_bound: int
    semisimple_exponent: int
    primary_exponent: int
    primary_generator: tuple
    primary_order_exponent: int
    source_period: int

    @classmethod
    def prepare(cls, checked):
        p, e = checked.p, checked.e
        m = checked.semisimple_order
        residue_period = checked.residue.point_period
        residue_p_part = residue_period // m
        P = residue_p_part * p ** (e - 1)
        es, ep = projectors(m, P)
        M = checked.module
        generator = arithmetic.power(M.action, ep, M.moduli)
        alpha, order = arithmetic.p_order(generator, M.moduli, p, e)
        if m * order != checked.period:
            raise ArithmeticError('Primary projector changed the source period.')
        return cls(checked, P, es, ep, generator, alpha, m * order)

    def query(self, state):
        checked = self.compiled
        M, p = checked.module, checked.p
        y = vector(state, checked.state_dimension, p ** checked.e,
                   'query state', checked.limits) + (1,)
        coords = M.coordinates(y)
        if coords is None:
            return False
        if checked.residue.query([x % p for x in coords])['status'] != 'reachable':
            return False
        B = M.polynomial_action(M.coefficients(coords))
        if arithmetic.apply(B, M.initial, M.moduli) != coords:
            raise ArithmeticError('Target endomorphism replay failed.')
        if not arithmetic.endomorphism(B, M.moduli):
            raise ArithmeticError('Invalid mixed-order target endomorphism.')
        # Under the verified residue-membership premise, ord(B) divides m*P.
        # This is NOT generally implied by the period of the source alone.
        primary = arithmetic.power(B, self.primary_exponent, M.moduli)
        z, _, _ = arithmetic.p_log(self.primary_generator, primary, M.moduli,
                                   p, self.primary_order_exponent)
        return z is not None
