"""Optional SymPy normal-form and scalar-group correctness comparison.

No native full matrix-orbit compiler or timing advantage is claimed. The scalar
competitor uses subgroup structure, not a new target discrete logarithm.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import argparse,json,random
from math import gcd
from research.prime_power_compilation_v1 import module as mod
from research.prime_power_compilation_v1.producer import produce
from research.prime_power_compilation_v1.checker import compile_source


def run():
    import sympy as sp
    from sympy.matrices.normalforms import smith_normal_form
    rng=random.Random(2026092708);normalforms=targets=sources=0
    for p,e in ((2,3),(3,2),(5,2)):
        N=p**e
        for n in range(1,6):
            for _ in range(8):
                G=tuple(tuple(rng.randrange(N) for _ in range(n)) for _ in range(n))
                *_,actual=mod.diagonalize(G,p,e)
                S=smith_normal_form(sp.Matrix(G),domain=sp.ZZ)
                expected=tuple(sorted(mod.valuation(abs(int(S[i,i])),p,e) for i in range(n) if int(S[i,i]) and mod.valuation(abs(int(S[i,i])),p,e)<e))
                if actual!=expected:raise AssertionError('Native Smith invariants differ.')
                normalforms+=1
    for p,e in ((3,2),(5,2),(7,2),(2,5)):
        N=p**e
        for A in range(1,N):
            if gcd(A,N)!=1 or (p==2 and A%4!=1):continue
            s=dict(schema='alc.prime-power-source.v1',modulus=N,prime=p,exponent=e,
                   matrix=[[A]],offset=[0],initial=[1])
            result=produce(s)
            if result['status']!='candidate':raise AssertionError('Reference producer exhausted.')
            compiled=compile_source(s,result['certificate'])
            order=int(sp.n_order(A,N))
            if compiled.period!=order:raise AssertionError('Native order mismatch.')
            for y in range(N):
                # For odd p the unit group is cyclic. For p=2 this source is in
                # the cyclic subgroup 1 mod4; the extra congruence is essential.
                answer=pow(y,order,N)==1 and (p!=2 or y%4==1)
                if (compiled.query([y])['status']=='reachable')!=answer:
                    raise AssertionError('Classical subgroup predicate disagrees.')
                targets+=1
            sources+=1
    return dict(schema=1,sympy_version=sp.__version__,normal_form_cases=normalforms,
                scalar_sources=sources,scalar_queries=targets,
                scope='Native Smith invariants and scalar subgroup predicates only. No orbit enumeration or target logarithm on the baseline query path. Not a performance or novelty comparison.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=run()
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(result,indent=2,sort_keys=True))
