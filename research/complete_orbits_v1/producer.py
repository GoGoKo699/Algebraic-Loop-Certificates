"""Proof producer using elementary factorization and baby-step/giant-step.

No trajectory enumeration. Factoring and logarithm search remain potentially
expensive; budgets bound them. This is not a new fast finite-field algorithm.
The checker NEVER calls these search routines.
"""
from __future__ import annotations
from math import isqrt, gcd
from alc.schema import Problem, Invalid, ResourceLimit
from . import algebra as alg


class Budget:
    def __init__(self, limit=1000000): self.limit=limit; self.used=0
    def tick(self, n=1):
        self.used += n
        if self.used > self.limit: raise ResourceLimit('experimental producer work budget exhausted')


class PrimeBuilder:
    def __init__(self, budget): self.budget=budget; self.proofs={}; self.factors={}
    def factor(self,n):
        if n in self.factors: return [list(v) for v in self.factors[n]]
        original=n; out=[]; d=2
        while d*d<=n:
            self.budget.tick(); e=0
            while n%d==0: n//=d; e+=1
            if e: out.append([d,e])
            d=3 if d==2 else d+2
        if n>1: out.append([n,1])
        self.factors[original]=out
        return [list(v) for v in out]
    def prime(self,p):
        if p in self.proofs: return
        if self.factor(p)!=[[p,1]]: raise Invalid('nonprime field parameter')
        if p==2:
            self.proofs[2]={'p':2,'witness':1,'factors':[]};return
        fac=self.factor(p-1)
        for q,e in fac: self.prime(q)
        for a in range(2,p):
            self.budget.tick()
            if pow(a,p-1,p)==1 and all(gcd(pow(a,(p-1)//q,p)-1,p)==1 for q,e in fac):
                self.proofs[p]={'p':p,'witness':a,'factors':fac};return
        raise Invalid('failed to build prime proof')


def factor_polynomial(mu,p,budget):
    """Transparent trial factorer for controls. Supply factors for larger inputs.

    It is NOT used by the checker. No heuristic success is called a proof.
    """
    remaining=mu; out=[]; d=1
    while 2*d <= len(remaining)-1:
        # Do not use itertools.product(range(p), repeat=d): it materializes a
        # pool of p entries before the effort limit can be checked. Decode one
        # candidate at a time, and charge even candidates with zero constant.
        for code in range(p**d):
            budget.tick()
            digits = [0]*d
            for j in range(d-1, -1, -1):
                code, digits[j] = divmod(code, p)
            cs = tuple(digits)
            if not cs[0]: continue
            f=cs+(1,)
            if alg.rem(remaining,f,p): continue
            if not alg.irreducible(f,p): continue
            e=0
            while not alg.rem(remaining,f,p):
                remaining=alg.divmod_poly(remaining,f,p)[0];e+=1
            out.append((f,e))
            if remaining==(1,):return out
        d+=1
    if remaining!=(1,):out.append((remaining,1))
    return out


def bsgs(alpha,beta,order,f,p,budget):
    if beta==(1,):return 0
    m=isqrt(order)+int(isqrt(order)**2<order)
    budget.tick(m) # Bound allocation before building the table.
    table={}; v=(1,)
    for j in range(m):table.setdefault(v,j);v=alg.mmul(v,alpha,f,p)
    step=alg.power(alg.inverse(alpha,f,p),m,f,p);v=beta
    for i in range(m+1):
        budget.tick()
        if v in table:
            t=i*m+table[v]
            if t<order and alg.power(alpha,t,f,p)==beta:return t
        v=alg.mmul(v,step,f,p)
    raise ArithmeticError('field subgroup membership and BSGS disagree')


def matrix_inverse(A,p):
    n=len(A);cols=tuple(zip(*A));answers=[]
    for j in range(n):
        ans=alg.solve_columns(cols,tuple(int(i==j) for i in range(n)),p)
        if ans is None:raise Invalid('singular input outside scope')
        answers.append(ans)
    return [list(row) for row in zip(*answers)]


def produce(document, max_work=1000000, supplied_factors=None):
    if type(max_work) is not int or max_work<0:raise ValueError('nonnegative budget required')
    budget=Budget(max_work);pb=PrimeBuilder(budget)
    try:
        problem=Problem.parse(document);p=problem.p;pb.prime(p)
        inv=matrix_inverse(problem.A,p)
        mu,beta=alg.cyclic_data(problem)
        base={'schema':'alc.algebraic-decision.v1','problem_sha256':problem.fingerprint,
              'prime_proofs':[],'inverse_matrix':inv,'components':[],'claim':{'status':'unreachable'}}
        if beta is not None:
            fs=factor_polynomial(mu,p,budget) if supplied_factors is None else supplied_factors
            for f,e in fs:
                f=tuple(f)
                if not alg.irreducible(f,p):raise Invalid('producer supplied factor not irreducible')
                alpha=alg.rem((0,1),f,p);bound=p**(len(f)-1)-1;r=bound
                for q,_ in pb.factor(bound):
                    while r%q==0 and alg.power(alpha,r//q,f,p)==(1,):r//=q
                factors=pb.factor(r)
                for q,_ in factors:pb.prime(q)
                b=alg.rem(beta,f,p)
                log=None if not b or alg.power(b,r,f,p)!=(1,) else bsgs(alpha,b,r,f,p,budget)
                base['components'].append({'factor':list(f),'multiplicity':e,'order':r,
                                            'order_factors':factors,'log':log})
            t,s=0,1;possible=True
            for rec in base['components']:
                if rec['log'] is None:possible=False;break
                combined=alg.crt(t,s,rec['log'],rec['order'])
                if combined is None:possible=False;break
                t,s=combined
            if possible:
                x=alg.rem((0,1),mu,p);u=alg.power(x,s,mu,p)
                c=alg.mmul(beta,alg.power(alg.inverse(x,mu,p),t,mu,p),mu,p)
                z,ppower,_,_=alg.unipotent_log(u,c,mu,p)
                if z is not None:base['claim']={'status':'reachable','first':t+s*z,'period':s*ppower}
        base['prime_proofs']=[pb.proofs[q] for q in sorted(pb.proofs)]
        return {'status':'candidate','certificate':base,'metrics':{'budgeted_search_work':budget.used,'trajectory_steps':0}}
    except ResourceLimit as exc:
        return {'status':'unknown','reason':str(exc),'metrics':{'budgeted_search_work':budget.used,'trajectory_steps':0}}
