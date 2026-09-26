"""Scalar affine orbit comparator, using the native SymPy integer-log API.

This is a derived classical reduction, not a new algorithm or certificate.
Both initial nonunits and composite moduli are retained; division is justified
by gcd cancellation with a changed modulus, never a field-style inverse.
"""
from math import gcd


def reduce_instance(N, A, c, initial, target):
    if any(type(x) is not int for x in (N,A,c,initial,target)) or N < 2:
        raise ValueError('Exact integer scalar instance required.')
    if any(not 0 <= x < N for x in (A,c,initial,target)) or gcd(A,N) != 1:
        raise ValueError('Canonical residues and an invertible multiplier required.')
    if A == 1:
        g = gcd(c,N)
        if (target-initial) % g:
            return {'kind':'empty'}
        period = N//g
        first = 0 if period == 1 else ((target-initial)//g * pow(c//g,-1,period)) % period
        return {'kind':'direct','first':first,'period':period}
    larger = N*(A-1)
    u = (A-1)*initial+c
    v = (A-1)*target+c
    g = gcd(u,larger)
    if v % g:
        return {'kind':'empty'}
    modulus = larger//g
    if modulus == 1:
        return {'kind':'direct','first':0,'period':1}
    target_power = (v//g * pow(u//g,-1,modulus)) % modulus
    if gcd(target_power,modulus) != 1:
        return {'kind':'empty'}
    return {'kind':'logarithm','modulus':modulus,'base':A%modulus,'target':target_power}


def solve(N,A,c,initial,target):
    from sympy.ntheory import n_order, discrete_log
    reduced = reduce_instance(N,A,c,initial,target)
    if reduced['kind'] == 'empty': return None
    if reduced['kind'] == 'direct': return reduced['first'], reduced['period']
    m,b,v = reduced['modulus'],reduced['base'],reduced['target']
    period = int(n_order(b,m))
    try:
        # Public API, no factorization/order hints. Supplying an order is not
        # equivalent to supplying its factorization in every SymPy version.
        first = int(discrete_log(m,v,b)) % period
    except ValueError:
        return None
    if pow(b,first,m) != v:
        raise ArithmeticError('Native log output failed direct replay.')
    return first,period
