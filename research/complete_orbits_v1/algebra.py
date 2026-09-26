"""Exact polynomial and cyclic-space arithmetic; no integer/poly factor search.

Polynomials are canonical coefficient tuples in increasing degree. The zero
polynomial is (). All callers have already established a prime modulus.
"""
from __future__ import annotations


def trim(a, p):
    a = [v % p for v in a]
    while a and a[-1] == 0:
        a.pop()
    return tuple(a)


def add(a, b, p):
    c = [0]*max(len(a), len(b))
    for i, v in enumerate(a): c[i] += v
    for i, v in enumerate(b): c[i] += v
    return trim(c, p)


def neg(a, p): return trim([-v for v in a], p)


def sub(a, b, p): return add(a, neg(b, p), p)


def scale(a, c, p): return trim([c*v for v in a], p)


def mul(a, b, p):
    if not a or not b: return ()
    c = [0]*(len(a)+len(b)-1)
    for i, u in enumerate(a):
        for j, v in enumerate(b): c[i+j] += u*v
    return trim(c, p)


def divmod_poly(a, b, p):
    if not b: raise ZeroDivisionError('zero polynomial divisor')
    r = list(trim(a, p)); q = [0]*max(0, len(r)-len(b)+1)
    inv = pow(b[-1], -1, p)
    while len(r) >= len(b):
        j = len(r)-len(b); c = r[-1]*inv % p; q[j] = c
        for k, v in enumerate(b): r[j+k] = (r[j+k]-c*v) % p
        while r and r[-1] == 0: r.pop()
    return trim(q, p), tuple(r)


def rem(a, m, p): return divmod_poly(a, m, p)[1]


def mmul(a, b, m, p): return rem(mul(a, b, p), m, p)


def power(a, exponent, m, p):
    if type(exponent) is not int or exponent < 0:
        raise ValueError('nonnegative exponent required')
    a = rem(a, m, p); result = rem((1,), m, p)
    while exponent:
        if exponent & 1: result = mmul(result, a, m, p)
        exponent >>= 1
        if exponent: a = mmul(a, a, m, p)
    return result


def gcd_poly(a, b, p):
    while b: a, b = b, rem(a, b, p)
    return scale(a, pow(a[-1], -1, p), p) if a else ()


def inverse(a, m, p):
    r0, r1, s0, s1 = m, rem(a, m, p), (), (1,)
    while r1:
        q, r2 = divmod_poly(r0, r1, p)
        r0, r1 = r1, r2
        s0, s1 = s1, sub(s0, mul(q, s1, p), p)
    if len(r0) != 1: raise ValueError('nonunit')
    return rem(scale(s0, pow(r0[0], -1, p), p), m, p)


def irreducible(f, p):
    """Deterministic Frobenius/gcd test; no factorization oracle.

    Testing every j <= degree//2 avoids importing a factorization of the degree.
    A reducible polynomial has an irreducible divisor of degree at most half.
    The full-degree Frobenius equality also excludes repeated factors.
    """
    if len(f) < 2 or f[-1] != 1: return False
    d = len(f)-1; x = rem((0, 1), f, p); cur = x
    for j in range(1, d+1):
        cur = power(cur, p, f, p)
        if j <= d//2 and gcd_poly(sub(cur, x, p), f, p) != (1,): return False
    return cur == x


def mv(A, v, p):
    return tuple(sum(a*b for a, b in zip(row, v)) % p for row in A)


def solve_columns(cols, target, p):
    """Exact Gaussian elimination, None if target is outside the column span."""
    n = len(target); k = len(cols)
    rows = [[cols[j][i] for j in range(k)]+[target[i]] for i in range(n)]
    pivots = []
    for col in range(k):
        pivot = next((i for i in range(len(pivots), n) if rows[i][col]), None)
        if pivot is None: continue
        at = len(pivots); rows[at], rows[pivot] = rows[pivot], rows[at]
        rows[at] = [v*pow(rows[at][col], -1, p) % p for v in rows[at]]
        for i in range(n):
            if i != at:
                a = rows[i][col]
                rows[i] = [(v-a*w) % p for v, w in zip(rows[i], rows[at])]
        pivots.append(col)
    if any(not any(row[:k]) and row[k] for row in rows): return None
    ans = [0]*k
    for i, col in enumerate(pivots): ans[col] = rows[i][k]
    return tuple(ans)


def cyclic_data(problem):
    """Compute the minimal polynomial ON THE INITIAL CYCLIC MODULE, not on A.

    Affine lifting makes the initial vector nonzero even for the zero fixed point.
    No orbit enumeration, random projection, factoring or target search occurs.
    """
    p = problem.p; n = len(problem.A)
    T = tuple(row+(c,) for row, c in zip(problem.A, problem.c))+((0,)*n+(1,),)
    v = problem.initial+(1,); target = problem.target+(1,); cols = []
    for _ in range(n+2):
        coefficients = solve_columns(cols, v, p)
        if coefficients is not None:
            mu = tuple((-c) % p for c in coefficients)+(1,)
            beta = solve_columns(cols, target, p)
            return mu, None if beta is None else trim(beta, p)
        cols.append(v); v = mv(T, v, p)
    raise ArithmeticError('cyclic dimension bound failed')


def crt(a, m, b, n):
    from math import gcd
    d = gcd(m, n)
    if (b-a) % d: return None
    q = n//d
    j = 0 if q == 1 else ((b-a)//d*pow(m//d, -1, q)) % q
    period = m*q
    return (a+m*j) % period, period


def unipotent_log(u, c, mu, p):
    """Exact membership and log in <u>, when u-1 is nilpotent.

    No loop of length p or order(u). p-adic digits are recovered by a
    coefficient ratio and each recovered order-p power is checked exactly.
    Returns (exponent or None, order(u), reason, trace).
    """
    one = (1,); degree = len(mu)-1
    if power(sub(u, one, p), degree, mu, p):
        raise ValueError('u is not verified unipotent')
    a = 0; order = 1; cur = u
    while cur != one:
        cur = power(cur, p, mu, p); a += 1; order *= p
        if a > degree.bit_length(): raise ArithmeticError('unipotent order bound failed')
    if a == 0: return (0 if c == one else None), 1, 'identity' if c == one else 'unipotent_mismatch', []
    g = power(u, order//p, mu, p); N = sub(g, one, p)
    pre, top = one, N
    for _ in range(degree):
        nxt = mmul(top, N, mu, p)
        if not nxt: break
        pre, top = top, nxt
    else: raise ArithmeticError('nilpotence bound failed')
    pivot = next(i for i, v in enumerate(top) if v)
    invu = inverse(u, mu, p); z = 0; place = 1; trace = []
    for j in range(a):
        residual = mmul(c, power(invu, z, mu, p), mu, p)
        v = power(residual, p**(a-1-j), mu, p)
        product = mmul(pre, sub(v, one, p), mu, p)
        numerator = product[pivot] if pivot < len(product) else 0
        digit = numerator*pow(top[pivot], -1, p) % p
        trace.append({'place': j, 'digit': digit})
        if product != scale(top, digit, p) or power(g, digit, mu, p) != v:
            return None, order, 'unipotent_digit_mismatch', trace
        z += digit*place; place *= p
    if power(u, z, mu, p) != c:
        return None, order, 'unipotent_mismatch', trace
    return z, order, 'member', trace
