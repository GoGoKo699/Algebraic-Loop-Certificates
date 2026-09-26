"""Bounded construction of one separating invariant for a requested target.

Factoring and base-to-base alignment can be expensive. No claim of fast general
construction. No target discrete logarithm is requested. The resulting proof
has a target-independent binding and must be checked before it is reused.
"""
from math import gcd, lcm
from alc.schema import Problem, Invalid, ResourceLimit
from research.complete_orbits_v1 import algebra as alg
from research.complete_orbits_v1.producer import (
    Budget, PrimeBuilder, factor_polynomial, matrix_inverse, bsgs)
from .checker import source_hash, evaluate, cyclic_basis, compile_invariant


def elements(p, degree, budget):
    for code in range(p**degree):
        budget.tick()
        out=[]
        while code:
            code,r=divmod(code,p);out.append(r)
        yield tuple(out)


def common_algebra(f1, f2, p, budget):
    d1,d2=len(f1)-1,len(f2)-1
    ell=lcm(d1,d2)
    if d1==ell:
        h=f1
    elif d2==ell:
        h=f2
    else:
        h=None
        for coeff in elements(p,ell,budget):
            candidate=coeff+(0,)*(ell-len(coeff))+(1,)
            if alg.irreducible(candidate,p):h=candidate;break
        if h is None:raise ArithmeticError('No irreducible polynomial found.')
    def root(f):
        if len(f)==2:return ((-f[0])%p,) if f[0] else ()
        if f==h:return alg.rem((0,1),h,p)
        for a in elements(p,ell,budget):
            if not evaluate(f,a,h,p):return a
        raise ArithmeticError('Expected finite-field embedding absent.')
    return h,root(f1),root(f2)


def produce(document, max_work=1000000):
    if type(max_work) is not int or max_work<0:
        raise ValueError('Nonnegative work limit required.')
    budget=Budget(max_work)
    pb=PrimeBuilder(budget)
    try:
        problem=Problem.parse(document)
        p=problem.p
        pb.prime(p)
        inv=matrix_inverse(problem.A,p)
        basis,mu=cyclic_basis(problem)
        beta=alg.solve_columns(basis,problem.target+(1,),p)
        proof={'schema':'alc.separating-invariant.v1',
               'source_sha256':source_hash(problem.as_dict()),
               'prime_proofs':[pb.proofs[q] for q in sorted(pb.proofs)],
               'inverse_matrix':inv,'invariant':{}}
        alignments=0
        def done(witness):
            proof['invariant']=witness
            checked=compile_invariant(document,proof)
            if checked.contains(list(problem.target)):
                raise ArithmeticError('Generated invariant does not separate requested target.')
            return {'status':'candidate','certificate':proof,
                    'metrics':{'budgeted_search_work':budget.used,
                               'base_alignment_log_calls':alignments,
                               'finite_field_target_log_calls':0,'trajectory_steps':0}}
        if beta is None:
            return done({'kind':'cyclic-span'})
        beta=alg.trim(beta,p)
        factors=factor_polynomial(mu,p,budget)
        orders=[]
        for f,multiplicity in factors:
            alpha=alg.rem((0,1),f,p)
            r=p**(len(f)-1)-1
            for q,_ in pb.factor(r):
                while r%q==0 and alg.power(alpha,r//q,f,p)==(1,):r//=q
            orders.append((f,r))
            if alg.power(beta,r,f,p)!=(1,):
                return done({'kind':'power-kernel','divisor':list(f),'exponent':r})
        m=lcm(*(r for _,r in orders))
        u=alg.power((0,1),m,mu,p)
        value=alg.power(beta,m,mu,p)
        z,_,_,_=alg.unipotent_log(u,value,mu,p)
        if z is None:
            return done({'kind':'power-kernel','divisor':list(mu),'exponent':m})
        # All local targets lie in their field subgroups. Equal-power predicates
        # test compatibility without solving logarithms of those targets.
        for i,(f1,r1) in enumerate(orders):
            for f2,r2 in orders[i+1:]:
                D=gcd(r1,r2)
                if D==1:continue
                h,a1,a2=common_algebra(f1,f2,p,budget)
                w1=alg.power(a1,r1//D,h,p)
                w2=alg.power(a2,r2//D,h,p)
                alignment=bsgs(w2,w1,D,h,p,budget);alignments+=1
                e1,e2=r1//D,(r2//D)*alignment
                if e2==0:raise ArithmeticError('Nontrivial root alignment cannot be zero.')
                left=alg.power(evaluate(beta,a1,h,p),e1,h,p)
                right=alg.power(evaluate(beta,a2,h,p),e2,h,p)
                if left!=right:
                    return done({'kind':'equal-powers','algebra_modulus':list(h),
                                 'left_root':list(a1),'right_root':list(a2),
                                 'left_exponent':e1,'right_exponent':e2})
        # Do not manufacture a positive time summary from absence of an exclusion.
        return {'status':'no_exclusion','metrics':{'budgeted_search_work':budget.used,
                    'base_alignment_log_calls':alignments,'finite_field_target_log_calls':0,'trajectory_steps':0}}
    except ResourceLimit as exc:
        return {'status':'unknown','reason':str(exc)}
