"""Bounded reference construction of a precision-composed certificate.

No trajectory enumeration; calls the existing experimental finite-field
producer. Search budgets count source operations, not CPU-time or bit costs.
The checker does not import this module or trust its derived-layer instances.
"""
from fractions import Fraction
from alc.schema import Invalid, ResourceLimit, digest
from research.complete_orbits_v1.producer import (Budget,PrimeBuilder,
                                                  produce as produce_field)
from research.complete_orbits_v1.algebra import crt
from .lifting import parse_problem, field_document, next_layer


def inverse_over_ring(A,N):
    """Untrusted producer inversion over Q followed by denominator reduction.

    Unit pivots need not appear in the original matrix over Z/NZ even when its
    determinant is a unit. Rational elimination avoids that mistaken field step.
    Exact inverse denominators divide the determinant and hence are units mod N.
    """
    n=len(A);rows=[[Fraction(v) for v in row]+[Fraction(int(i==j)) for j in range(n)]
                 for i,row in enumerate(A)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if rows[i][j]),None)
        if pivot is None:raise Invalid('singular matrix')
        rows[j],rows[pivot]=rows[pivot],rows[j]
        v=rows[j][j];rows[j]=[x/v for x in rows[j]]
        for i in range(n):
            if i!=j:
                v=rows[i][j];rows[i]=[x-v*y for x,y in zip(rows[i],rows[j])]
    try:return [[int(v.numerator)*pow(int(v.denominator),-1,N)%N for v in row[n:]] for row in rows]
    except ValueError as exc:raise Invalid('matrix not invertible modulo N') from exc


def produce(document,max_work=1000000):
    if type(max_work) is not int or max_work<0:raise ValueError('nonnegative budget required')
    budget=Budget(max_work);builder=PrimeBuilder(budget);field_calls=0
    try:
        N,A,c,a,b=parse_problem(document)
        factors=builder.factor(N)
        for p,e in factors:builder.prime(p)
        inv=inverse_over_ring(A,N)
        certificate={'schema':'alc.modular-decision.v1','problem_sha256':digest(document),
            'modulus_factors':factors,'prime_proofs':[builder.proofs[p] for p in sorted(builder.proofs)],
            'inverse_matrix':inv,'local_proofs':[],'claim':{'status':'unreachable'}}
        local_schedules=[]
        for p,e in factors:
            layers=[];current=field_document(p,A,c,a,b);first,period=0,1;possible=True
            for j in range(e):
                budget.tick() # includes a charge for each call, even when field search is trivial
                out=produce_field(current,max_work=max_work-budget.used);field_calls+=1
                budget.tick(out['metrics']['budgeted_search_work'])
                if out['status']!='candidate':raise ResourceLimit(out['reason'])
                proof=out['certificate'];layers.append(proof)
                if proof['claim']['status']=='unreachable':possible=False;break
                t,r=proof['claim']['first'],proof['claim']['period']
                first,period=first+period*t,period*r
                if j+1<e:current=next_layer(A,c,a,b,p,j+1,first,period)
            certificate['local_proofs'].append({'prime':p,'layers':layers})
            local_schedules.append((first,period) if possible else None)
        if all(v is not None for v in local_schedules):
            t,r=0,1
            for u,s in local_schedules:
                joint=crt(t,r,u,s)
                if joint is None:break
                t,r=joint
            else:certificate['claim']={'status':'reachable','first':t,'period':r}
        return {'status':'candidate','certificate':certificate,
                'metrics':{'field_calls':field_calls,'budgeted_search_work':budget.used,'trajectory_steps':0}}
    except ResourceLimit as exc:
        return {'status':'unknown','reason':str(exc),
                'metrics':{'field_calls':field_calls,'budgeted_search_work':budget.used,'trajectory_steps':0}}
