"""Optional native SymPy comparisons; not required for the core checker.

This checks factorization and scalar full-hit schedules. It is not a performance
comparison against a full matrix-orbit or program-analysis implementation.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from itertools import product
import json
import warnings
import sympy as sp
from research.complete_orbits_v1 import algebra as alg
from research.complete_orbits_v1.producer import factor_polynomial, Budget, produce
from research.complete_orbits_v1.checker import decide


def run():
    x=sp.Symbol('x');factors_checked=0;scalar_cases=0;yes=0;no=0
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',sp.utilities.exceptions.SymPyDeprecationWarning)
        for p,degree in ((2,5),(3,3),(5,2)):
            for d in range(1,degree+1):
                for cs in product(range(p),repeat=d):
                    if not cs[0]:continue
                    f=cs+(1,)
                    native=sp.Poly.from_list(list(reversed(f)),x,modulus=p).factor_list()[1]
                    normalized=sorted((tuple(int(v)%p for v in reversed(g.all_coeffs())),e) for g,e in native)
                    ours=sorted(factor_polynomial(f,p,Budget()))
                    if normalized!=ours:raise AssertionError('native factorization disagreement')
                    factors_checked+=1
        for p in (3,5,7,11,13):
            for a in range(1,p):
                order=int(sp.n_order(a,p))
                for b in range(1,p):
                    d={'schema':'alc.problem.v1','field':{'kind':'prime','modulus':p},'matrix':[[a]],
                       'offset':[0],'initial':[1],'target':[b]}
                    out=decide(d,produce(d)['certificate'])
                    if pow(b,order,p)==1:
                        exponent=int(sp.discrete_log(p,b,a))
                        if out['status']!='reachable' or (out['first'],out['period'])!=(exponent,order):
                            raise AssertionError('native scalar log/schedule disagreement')
                        yes+=1
                    else:
                        if out['status']!='unreachable':raise AssertionError('native subgroup test disagreement')
                        no+=1
                    scalar_cases+=1
    return {'sympy_version':sp.__version__,'polynomial_factorizations':factors_checked,
            'scalar_cases':scalar_cases,'reachable':yes,'unreachable':no,
            'scope':'Native exact primitive/scalar correctness comparison only. No general matrix-orbit runtime advantage is tested.'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    out=run()
    with args.output.open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(out,indent=2,sort_keys=True))
