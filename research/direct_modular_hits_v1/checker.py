"""Direct positive certificates over Z/NZ, without factoring the modulus.

Only point-period factors need primality proofs. The input matrix's inverse
witness establishes bijectivity directly over the ring. No producer or search
is imported. This is the standard order certificate, not a new group theorem.
"""
from alc.schema import DEFAULT_LIMITS, Invalid, integer, keys, matrix, digest
from alc.checker import prime_proofs, factorization
from research.modular_lifting_v1.lifting import parse_problem, mm, eye, affine_power, apply


def verify(document, certificate, limits=DEFAULT_LIMITS):
    N,A,c,a,b=parse_problem(document,limits);d=len(A)
    keys(certificate,{'schema','problem_sha256','inverse_matrix','prime_proofs',
                      'first','period','period_factors'},'direct modular hit certificate')
    if certificate['schema']!='alc.modular-hits.v1':raise Invalid('wrong direct schema')
    if certificate['problem_sha256']!=digest(document):raise Invalid('wrong problem binding')
    inv=matrix(certificate['inverse_matrix'],d,N,'ring inverse witness',limits)
    if mm(A,inv,N)!=eye(d) or mm(inv,A,N)!=eye(d):raise Invalid('invalid ring inverse')
    t=integer(certificate['first'],'first',0,limits=limits)
    r=integer(certificate['period'],'period',1,limits=limits)
    if t>=r or r>N**d:raise Invalid('noncanonical offset or impossible period')
    stats={'modular_power_checks':0}
    primes=prime_proofs(certificate['prime_proofs'],limits,stats)
    qs=factorization(r,certificate['period_factors'],primes,limits)
    def state_at(n):
        P,q=affine_power(A,c,n,N)
        return apply(P,q,a,N)
    if state_at(t)!=b:raise Invalid('false target hit')
    if state_at(r)!=a:raise Invalid('false point period')
    for q in qs:
        if state_at(r//q)==a:raise Invalid('nonminimal point period')
    return {'verified':True,'status':'reachable','problem_sha256':digest(document),
            'first':t,'period':r,'affine_power_checks':2+len(qs),
            'modulus_factorization_required':False}
