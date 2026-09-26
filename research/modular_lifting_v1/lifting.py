"""Exact prime-power precision lifting of affine point-orbit decisions.

The residue ring is Z/NZ, NOT a field. At each additional p-adic precision,
the checker constructs a new affine problem over the genuine prime field F_p.
This module contains no factor or discrete-log search and imports no producer.
"""
from __future__ import annotations
from alc.schema import (DEFAULT_LIMITS, Invalid, ResourceLimit, integer, keys,
                        matrix, vector, digest)
from alc.checker import prime_proofs, factorization
from research.complete_orbits_v1.checker import decide as decide_field
from research.complete_orbits_v1.algebra import crt


def parse_problem(document, limits=DEFAULT_LIMITS):
    keys(document, {'schema','modulus','matrix','offset','initial','target'}, 'modular problem')
    if document['schema'] != 'alc.modular-problem.v1': raise Invalid('wrong modular schema')
    N=integer(document['modulus'],'modulus',2,limits=limits)
    raw=document['matrix']
    if type(raw) is not list or not raw: raise Invalid('nonempty square matrix required')
    d=len(raw)
    if d>limits.max_dimension: raise ResourceLimit('dimension limit exceeded')
    A=matrix(raw,d,N,'matrix',limits)
    c=vector(document['offset'],d,N,'offset',limits)
    a=vector(document['initial'],d,N,'initial',limits)
    b=vector(document['target'],d,N,'target',limits)
    return N,A,c,a,b


def mm(A,B,N):
    cols=tuple(zip(*B))
    return tuple(tuple(sum(x*y for x,y in zip(row,col))%N for col in cols) for row in A)


def eye(d): return tuple(tuple(int(i==j) for j in range(d)) for i in range(d))


def mv(A,v,N): return tuple(sum(x*y for x,y in zip(row,v))%N for row in A)


def affine_power(A,c,t,N):
    if type(t) is not int or t<0: raise Invalid('nonnegative exponent required')
    d=len(A)
    P=tuple(tuple(v%N for v in row)+(ci%N,) for row,ci in zip(A,c))+((0,)*d+(1,),)
    out=eye(d+1)
    while t:
        if t&1: out=mm(P,out,N)
        t>>=1
        if t: P=mm(P,P,N)
    return tuple(row[:d] for row in out[:d]),tuple(row[-1] for row in out[:d])


def apply(A,c,x,N): return tuple((v+ci)%N for v,ci in zip(mv(A,x,N),c))


def field_document(p,A,c,a,b):
    return {'schema':'alc.problem.v1','field':{'kind':'prime','modulus':p},
            'matrix':[[v%p for v in row] for row in A],
            'offset':[v%p for v in c], 'initial':[v%p for v in a], 'target':[v%p for v in b]}


def next_layer(A,c,a,b,p,k,first,period):
    """Derive F_p dynamics within a verified solution fiber modulo p**k.

    If t=first+period*z, the extra digit evolves as zvec -> B*zvec+defect.
    Division is ordinary integer division of proved multiples of p**k. Negative
    representatives are harmless after reduction modulo p. No field inversion
    or Gaussian elimination is attempted over the composite residue ring.
    """
    low=p**k; high=low*p
    H,h=affine_power(A,c,first,high); origin=apply(H,h,a,high)
    B,d=affine_power(A,c,period,high); moved=apply(B,d,origin,high)
    target_diff=tuple((bi%high)-oi for bi,oi in zip(b,origin))
    defect_diff=tuple(mi-oi for mi,oi in zip(moved,origin))
    if any(v%low for v in target_diff+defect_diff):
        raise Invalid('previously claimed schedule does not justify precision lifting')
    target=tuple((v//low)%p for v in target_diff)
    defect=tuple((v//low)%p for v in defect_diff)
    return field_document(p,B,defect,(0,)*len(A),target)


def decide(document,certificate,limits=DEFAULT_LIMITS):
    N,A,c,a,b=parse_problem(document,limits); d=len(A)
    keys(certificate, {'schema','problem_sha256','modulus_factors','prime_proofs',
                       'inverse_matrix','local_proofs','claim'}, 'modular certificate')
    if certificate['schema']!='alc.modular-decision.v1':raise Invalid('wrong modular certificate schema')
    if certificate['problem_sha256']!=digest(document):raise Invalid('wrong modular problem binding')
    proven=prime_proofs(certificate['prime_proofs'],limits,{'modular_power_checks':0})
    factors=certificate['modulus_factors']
    ps=factorization(N,factors,proven,limits)
    inverse=matrix(certificate['inverse_matrix'],d,N,'ring inverse witness',limits)
    if mm(A,inverse,N)!=eye(d) or mm(inverse,A,N)!=eye(d):
        raise Invalid('linear part is not invertible modulo the supplied integer')
    records=certificate['local_proofs']
    if type(records) is not list or len(records)!=len(ps):
        raise Invalid('one local proof list per distinct modulus prime is required')
    local_results=[]; checked_layers=0
    for (p,e),rec in zip(factors,records):
        keys(rec,{'prime','layers'},'prime-power proof')
        if type(rec['prime']) is not int or rec['prime']!=p:raise Invalid('local prime order mismatch')
        layers=rec['layers']
        if type(layers) is not list or not 1<=len(layers)<=e:
            raise Invalid('invalid layer count')
        current=field_document(p,A,c,a,b)
        first,period=0,1; failed=False
        for j,proof in enumerate(layers):
            result=decide_field(current,proof,limits);checked_layers+=1
            if result['status']=='unreachable':
                if j+1!=len(layers):raise Invalid('trailing proof after a negative layer')
                failed=True
                local_results.append({'prime':p,'exponent':e,'status':'unreachable',
                                      'failed_precision':j+1,'reason':result['reason']})
                break
            first,period=first+period*result['first'],period*result['period']
            precision=j+1
            if not 0<=first<period or period>(p**precision)**d:
                raise Invalid('lifted schedule violates finite-state period bounds')
            # Redundant fast replay tests protect the composition implementation.
            H,h=affine_power(A,c,first,p**precision)
            if apply(H,h,a,p**precision)!=tuple(v%(p**precision) for v in b):
                raise Invalid('lifted hit replay failed')
            H,h=affine_power(A,c,period,p**precision)
            if apply(H,h,a,p**precision)!=tuple(v%(p**precision) for v in a):
                raise Invalid('lifted period replay failed')
            if precision<e:
                current=next_layer(A,c,a,b,p,precision,first,period)
        if not failed:
            if len(layers)!=e:raise Invalid('incomplete positive precision chain')
            local_results.append({'prime':p,'exponent':e,'status':'reachable',
                                  'first':first,'period':period})
    claim=certificate['claim']
    if type(claim) is not dict or 'status' not in claim:raise Invalid('modular claim required')
    if claim['status']=='reachable':
        keys(claim,{'status','first','period'},'modular hit claim')
        integer(claim['first'],'first',0,limits=limits)
        integer(claim['period'],'period',1,limits=limits)
    elif claim['status']=='unreachable':keys(claim,{'status'},'modular negative claim')
    else:raise Invalid('unknown is not a proof')
    expected={'status':'unreachable'};reason='local_prime_power_obstruction'
    if all(v['status']=='reachable' for v in local_results):
        first,period=0,1
        for rec in local_results:
            joint=crt(first,period,rec['first'],rec['period'])
            if joint is None:
                reason='incompatible_prime_power_times';break
            first,period=joint
        else:
            expected={'status':'reachable','first':first,'period':period};reason='complete_modular_hit_set'
    if claim!=expected:raise Invalid('modular conclusion differs from checked composition')
    return dict(verified=True,problem_sha256=digest(document),**expected,reason=reason,
                field_certificates_checked=checked_layers,local_results=local_results)
