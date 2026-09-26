"""Experimental complete point-orbit decision certificate checker.

The production alc.certificate.v1 interface is untouched. This checker uses
only the production parser, primality verifier, and inverse witness checks,
plus exact polynomial/cyclic-space arithmetic. It never imports the producer.
"""
from __future__ import annotations
from alc.schema import (Problem, DEFAULT_LIMITS, Invalid, ResourceLimit,
                        integer, keys, matrix)
from alc.checker import prime_proofs, factorization, product, identity
from . import algebra as alg


def polynomial(raw, p, degree_bound, label, limits):
    if type(raw) is not list or len(raw) > degree_bound+1:
        raise Invalid(label+': invalid polynomial length')
    a = tuple(integer(v, label, 0, p-1, limits) for v in raw)
    if a and not a[-1]: raise Invalid(label+': noncanonical trailing zero')
    return a


def decide(problem_document, certificate, limits=DEFAULT_LIMITS):
    problem = Problem.parse(problem_document, limits)
    keys(certificate, {'schema','problem_sha256','prime_proofs','inverse_matrix',
                       'components','claim'}, 'decision certificate')
    if certificate['schema'] != 'alc.algebraic-decision.v1': raise Invalid('wrong experimental schema')
    if certificate['problem_sha256'] != problem.fingerprint: raise Invalid('wrong problem binding')
    stats = {'modular_power_checks':0}
    proven = prime_proofs(certificate['prime_proofs'], limits, stats)
    if problem.p not in proven: raise Invalid('modulus not proved prime')
    n = len(problem.A); p = problem.p
    inv = matrix(certificate['inverse_matrix'], n, p, 'inverse witness', limits)
    if product(problem.A, inv, p) != identity(n) or product(inv, problem.A, p) != identity(n):
        raise Invalid('invalid inverse witness')
    mu, beta = alg.cyclic_data(problem); degree = len(mu)-1
    raw = certificate['components']
    if type(raw) is not list: raise Invalid('component list required')
    if len(raw) > degree: raise Invalid('too many irreducible components')
    claim = certificate['claim']
    if type(claim) is not dict or 'status' not in claim: raise Invalid('claim object required')
    if claim['status'] == 'reachable':
        keys(claim, {'status','first','period'}, 'positive decision claim')
        integer(claim['first'],'first',0,limits=limits)
        integer(claim['period'],'period',1,limits=limits)
    elif claim['status'] == 'unreachable':
        keys(claim, {'status'}, 'negative decision claim')
    else: raise Invalid('unknown is not a certificate')

    def finish(first, period, reason, trace=None):
        expected = {'status':'unreachable'} if first is None else {'status':'reachable','first':first,'period':period}
        if claim != expected: raise Invalid('claimed outcome differs from algebraic checks')
        return dict(verified=True, problem_sha256=problem.fingerprint, **expected,
                    reason=reason, cyclic_degree=degree,
                    unipotent_trace=[] if trace is None else trace)

    if beta is None:
        if raw: raise Invalid('outside-span certificate must have no components')
        return finish(None, None, 'outside_cyclic_span')
    expanded = (1,); seen = set(); records = []
    for rec in raw:
        keys(rec, {'factor','multiplicity','order','order_factors','log'}, 'component')
        f = polynomial(rec['factor'],p,degree,'irreducible factor',limits)
        if len(f) < 2 or f[-1] != 1 or not f[0] or f in seen:
            raise Invalid('distinct monic nonzero-constant factors required')
        seen.add(f)
        e = integer(rec['multiplicity'],'multiplicity',1,degree,limits)
        if (len(f)-1)*e+len(expanded)-1 > degree: raise Invalid('factor degrees exceed minimal polynomial')
        if not alg.irreducible(f,p): raise Invalid('reducible purported field factor')
        for _ in range(e): expanded=alg.mul(expanded,f,p)
        r = integer(rec['order'],'component order',1,p**(len(f)-1)-1,limits)
        qs = factorization(r,rec['order_factors'],proven,limits)
        alpha=alg.rem((0,1),f,p)
        if alg.power(alpha,r,f,p)!=(1,) or any(alg.power(alpha,r//q,f,p)==(1,) for q in qs):
            raise Invalid('component order not exact')
        b=alg.rem(beta,f,p)
        nonmember=not b or alg.power(b,r,f,p)!=(1,)
        if nonmember:
            if rec['log'] is not None: raise Invalid('local nonmember log must be null')
            t=None
        else:
            t=integer(rec['log'],'component log',0,r-1,limits)
            if alg.power(alpha,t,f,p)!=b: raise Invalid('false discrete log witness')
        records.append((t,r))
    if expanded != mu: raise Invalid('factorization does not equal the independently computed minimal polynomial')
    if any(t is None for t,r in records): return finish(None,None,'field_subgroup_obstruction')
    first, period=0,1
    for t,r in records:
        combined=alg.crt(first,period,t,r)
        if combined is None: return finish(None,None,'incompatible_field_congruences')
        first,period=combined
    x=alg.rem((0,1),mu,p)
    u=alg.power(x,period,mu,p)
    residual=alg.mmul(beta,alg.power(alg.inverse(x,mu,p),first,mu,p),mu,p)
    z,ppower,reason,trace=alg.unipotent_log(u,residual,mu,p)
    if z is None: return finish(None,None,reason,trace)
    full_first=first+period*z; full_period=period*ppower
    if full_period > p**n or not 0 <= full_first < full_period:
        raise Invalid('period/state-count contradiction')
    if alg.power(x,full_first,mu,p)!=beta: raise Invalid('final quotient-ring replay failed')
    return finish(full_first,full_period,'complete_hit_set',trace)
