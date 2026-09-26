"""Package candidate times. No correctness is implied until checker replay.

This helper searches only for point-period factor/primality data. Producing the
candidate offset and period is external and must be charged separately. It does
not factor N or call a discrete-logarithm routine.
"""
from alc.schema import Invalid, ResourceLimit, integer, DEFAULT_LIMITS, digest
from research.modular_lifting_v1.lifting import parse_problem
from research.modular_lifting_v1.producer import inverse_over_ring
from research.complete_orbits_v1.producer import Budget, PrimeBuilder


def assemble(document, first, period, max_work=1000000):
    N,A,c,a,b=parse_problem(document)
    integer(first,'first',0,limits=DEFAULT_LIMITS)
    integer(period,'period',1,limits=DEFAULT_LIMITS)
    if first>=period or period>N**len(A):raise Invalid('candidate bounds fail')
    if type(max_work) is not int or max_work<0:raise ValueError('nonnegative budget required')
    work=Budget(max_work);builder=PrimeBuilder(work)
    try:
        factors=builder.factor(period)
        for p,e in factors:builder.prime(p)
        cert={'schema':'alc.modular-hits.v1','problem_sha256':digest(document),
              'inverse_matrix':inverse_over_ring(A,N),
              'prime_proofs':[builder.proofs[p] for p in sorted(builder.proofs)],
              'first':first,'period':period,'period_factors':factors}
        return {'status':'candidate','certificate':cert,'budgeted_search_work':work.used}
    except ResourceLimit as exc:return {'status':'unknown','reason':str(exc)}
