"""Exact, independent-trajectory, adversarial, and consumer checks.

Only small trajectories are enumerated by the TEST oracle. The experimental
producer and checker never enumerate a matrix/vector trajectory.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from itertools import product
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from alc.schema import Invalid, ResourceLimit, Problem
from alc.checker import verify as verify_positive
from research.complete_orbits_v1 import algebra as alg
from research.complete_orbits_v1.checker import decide
from research.complete_orbits_v1.producer import produce, PrimeBuilder, Budget


def require(ok,message):
    if not ok:raise AssertionError(message)


def problem(p,A,c,x,y):
    return {'schema':'alc.problem.v1','field':{'kind':'prime','modulus':p},
            'matrix':[list(row) for row in A],'offset':list(c),'initial':list(x),'target':list(y)}


def trajectory(d):
    x=tuple(d['initial']); start=x; out=[]; p=d['field']['modulus']; A=d['matrix'];c=d['offset']
    while x not in out:
        out.append(x)
        x=tuple((sum(a*b for a,b in zip(row,x))+v)%p for row,v in zip(A,c))
    require(x==start,'test family not invertible')
    return out


def families():
    for p in (2,3):
        for a in product(range(p),repeat=4):
            if (a[0]*a[3]-a[1]*a[2])%p:
                yield p,[a[:2],a[2:]],[0,0]
    for p in (2,3,5):
        for a in range(1,p):
            for c in range(p):yield p,[[a]],[c]
    for a in product(range(2),repeat=4):
        if (a[0]*a[3]-a[1]*a[2])%2:
            for c in ((0,1),(1,0),(1,1)):yield 2,[a[:2],a[2:]],c


def companion(mu,p):
    n=len(mu)-1
    A=[[0]*n for _ in range(n)]
    for j in range(n-1):A[j+1][j]=1
    for i in range(n):A[i][-1]=-mu[i]%p
    return A


def primary_certificate(d,c,out):
    pb=PrimeBuilder(Budget())
    fac=pb.factor(out['period'])
    for q,e in fac:pb.prime(q)
    proofs={r['p']:r for r in c['prime_proofs']};proofs.update(pb.proofs)
    return {'schema':'alc.certificate.v1','kind':'periodic_hits',
            'problem_sha256':Problem.parse(d).fingerprint,'first':out['first'],
            'period':out['period'],'period_factors':fac,'inverse_matrix':c['inverse_matrix'],
            'prime_proofs':[proofs[q] for q in sorted(proofs)]}


def run():
    counts=Counter(); reasons=Counter(); checksum=hashlib.sha256(); fixtures=[]
    def case(d):
        orbit=trajectory(d); target=tuple(d['target'])
        expected=None if target not in orbit else orbit.index(target)
        result=produce(d)
        require(result['status']=='candidate','small producer unexpectedly exhausted budget')
        c=result['certificate'];out=decide(d,c);reasons[out['reason']]+=1
        require((out['status']=='reachable')==(expected is not None),'reachability mismatch')
        if expected is not None:
            require((out['first'],out['period'])==(expected,len(orbit)),'least schedule mismatch')
            pc=primary_certificate(d,c,out);verified=verify_positive(d,pc)
            require(verified.first==expected and verified.period==len(orbit),'production verifier disagreement')
            counts['primary_positive_replays']+=1
        wrong=deepcopy(c)
        wrong['claim']={'status':'unreachable'} if expected is not None else {'status':'reachable','first':0,'period':len(orbit)}
        try:decide(d,wrong)
        except Invalid:counts['opposite_claims_rejected']+=1
        else:raise AssertionError('false decision accepted')
        for low,high in ((0,0),(3,42),(19,113)):
            predicted=0 if expected is None else max(0,(high-expected)//len(orbit)+1)-max(0,(low-1-expected)//len(orbit)+1)
            actual=sum(orbit[t%len(orbit)]==target for t in range(low,high+1))
            require(predicted==actual,'bounded consumer mismatch');counts['window_queries']+=1
        checksum.update(json.dumps([d,out],sort_keys=True).encode());counts['state_target_cases']+=1
        return c,out
    for p,A,c in families():
        counts['base_recurrences']+=1
        states=list(product(range(p),repeat=len(A)))
        for x in states:
            for y in states:case(problem(p,A,c,x,y))
    # High multiplicities and nonlinear unit targets, including all p-adic digits.
    for p,k in ((2,3),(2,5),(3,3),(3,4),(5,3)):
        mu=(1,)
        for _ in range(k):mu=alg.mul(mu,(p-1,1),p)
        A=companion(mu,p);x=[1]+[0]*(k-1)
        for y in product(range(p),repeat=k):
            case(problem(p,A,[0]*k,x,y));counts['repeated_factor_cases']+=1
    # Mixed repeated factors test the simultaneous field-congruence and
    # nilpotent reduction, not only one repeated linear eigenvalue.
    mixed = [
        (2, [((1,1),2), ((1,1,1),1)]),
        (2, [((1,1,1),3)]),
        (2, [((1,1),2), ((1,1,1),2)]),
        (3, [((2,1),2), ((1,1),2)]),
        (3, [((1,0,1),2), ((2,1),1)]),
        (5, [((4,1),2), ((3,1),2)])]
    for p, factors in mixed:
        mu=(1,)
        for f, multiplicity in factors:
            for _ in range(multiplicity): mu=alg.mul(mu,f,p)
        k=len(mu)-1; A=companion(mu,p); x=[1]+[0]*(k-1)
        for y in product(range(p),repeat=k):
            case(problem(p,A,[0]*k,x,y));counts['mixed_factor_cases']+=1
    # A zero search budget must act before generating a finite-field pool.
    # No arithmetic/primality claim is needed for this allocation control.
    from research.complete_orbits_v1.producer import factor_polynomial
    try: factor_polynomial((1,0,0,0,1), (1<<127)-1, Budget(0))
    except ResourceLimit: counts['factor_generation_limit_control']=1
    else: raise AssertionError('factor generator ignored its budget')
    # Irreducibility/polynomial identity controls independent via trial division.
    for p,maxd in ((2,6),(3,4)):
        for d in range(1,maxd+1):
            for coeff in product(range(p),repeat=d):
                f=coeff+(1,); trial=True
                for e in range(1,d//2+1):
                    for lower in product(range(p),repeat=e):
                        if not alg.rem(f,lower+(1,),p):trial=False;break
                    if not trial:break
                require(alg.irreducible(f,p)==trial,'irreducibility disagreement')
                counts['independent_irreducibility_cases']+=1
    # Exhaust arbitrary elements against actual subgroups of nilpotent units.
    for p,k in ((2,3),(2,4),(3,3)):
        mu=(0,)*k+(1,)
        units=[(1,)+cs for cs in product(range(p),repeat=k-1)]
        all_elements=[alg.trim(cs,p) for cs in product(range(p),repeat=k)]
        for raw_u in units:
            u=alg.trim(raw_u,p);current=(1,);orbit=[]
            while current not in orbit:orbit.append(current);current=alg.mmul(current,u,mu,p)
            for c in all_elements:
                z,r,_,_=alg.unipotent_log(u,c,mu,p)
                expected=orbit.index(c) if c in orbit else None
                require(z==expected and r==len(orbit),'unipotent solver false membership decision')
                counts['unipotent_ring_cases']+=1
    # Distinct obstruction examples and an ordinary positive case.
    examples=[('fibonacci',problem(7,[[1,1],[1,0]],[0,0],[1,0],[4,5])),
              ('field_obstruction',problem(5,[[4]],[0],[1],[2])),
              ('congruence_conflict',problem(13,[[4,0],[0,5]],[0,0],[1,1],[10,12])),
              ('outside_span',problem(7,[[1,0],[0,1]],[0,0],[1,0],[0,1]))]
    mu=(1,)
    for _ in range(3):mu=alg.mul(mu,(4,1),5)
    A=companion(mu,5)
    h=alg.add((1,),alg.mul((4,1),(4,1),5),5)
    examples.append(('unipotent_obstruction',problem(5,A,[0]*3,[1,0,0],list(h))))
    for name,d in examples:
        c,out=case(d);fixtures.append({'name':name,'problem':d,'certificate':c,'result':out})
    # Large characteristic unipotent recurrence: avoid a p-step orbit or p-digit search.
    p=65537;k=3;mu=(1,)
    for _ in range(k):mu=alg.mul(mu,(p-1,1),p)
    A=companion(mu,p);h=alg.add((1,),alg.mul((p-1,1),(p-1,1),p),p)
    d=problem(p,A,[0]*k,[1,0,0],list(h))
    r=produce(d,supplied_factors=[((p-1,1),3)]);out=decide(d,r['certificate'])
    require(out['status']=='unreachable' and 'unipotent' in out['reason'],'large-prime nilpotent rejection failed')
    fixtures.append({'name':'large_characteristic_control','problem':d,'certificate':r['certificate'],'result':out})
    # Exercise the real proof-consuming interface, not only an arithmetic formula.
    from research.complete_orbits_v1.consumer import query
    for fixture in fixtures[:5]:
        d=fixture['problem'];c=fixture['certificate'];orb=trajectory(d);y=tuple(d['target'])
        for low,high in ((0,0),(3,42),(19,113)):
            out=query(d,c,low,high)['interval']
            actual=[t for t in range(low,high+1) if orb[t%len(orb)]==y]
            require(out['count']==len(actual) and out['first']==(actual[0] if actual else None)
                    and out['last']==(actual[-1] if actual else None), 'actual consumer discrepancy')
            counts['reverified_consumer_queries']+=1
    fib=fixtures[0]
    h=10**100
    huge=query(fib['problem'],fib['certificate'],h,h+100)['interval']
    require(huge['count']==6 and huge['first']==h+11 and huge['last']==h+91,
            'large-horizon consumer arithmetic failed')
    counts['large_horizon_consumer_control']=1
    # Alter different proof obligations and check actual rejection.
    c=fixtures[0]['certificate'];d=fixtures[0]['problem'];mutations=[]
    for field,value in [('problem_sha256','0'*64),('schema','trusted'),('inverse_matrix',[[1,0],[0,1]]),('prime_proofs',[])]:
        b=deepcopy(c);b[field]=value;mutations.append(b)
    for index,field,value in [(0,'multiplicity',0),(0,'multiplicity',2),(1,'factor',[1,0,1]),
                              (1,'order',8),(1,'order',True),(1,'order_factors',[]),
                              (1,'log',10),(1,'log',None)]:
        b=deepcopy(c);b['components'][index][field]=value;mutations.append(b)
    b=deepcopy(c);b['components'].append(deepcopy(b['components'][0]));mutations.append(b)
    b=deepcopy(c);b['claim']['first']=-1;mutations.append(b)
    b=deepcopy(c);b['claim']['period']*=2;mutations.append(b)
    b=deepcopy(c);b['components'][1]['order_factors']=[[4,2]];mutations.append(b)
    for b in mutations:
        try:decide(d,b)
        except (Invalid,ResourceLimit):counts['proof_mutations_rejected']+=1
        else:raise AssertionError('malformed proof accepted')
    bad=deepcopy(d);bad['target'][0]=3
    try:decide(bad,c)
    except Invalid:counts['wrong_problem_rejected']+=1
    else:raise AssertionError('wrong problem binding accepted')
    zero=produce(d,max_work=0)
    require(zero['status']=='unknown' and 'certificate' not in zero,'budget exhaustion promoted to certificate')
    counts['unknown_control']=1
    # Producer imports must be absent in a fresh verifier process.
    with __import__('tempfile').TemporaryDirectory() as td:
        path=Path(td)/'proof.json';path.write_text(json.dumps(fixtures[0]))
        code=('import sys,json; from research.complete_orbits_v1.checker import decide; '
              'q=json.load(open(sys.argv[1])); decide(q["problem"],q["certificate"]); '
              'raise SystemExit(any(k.endswith("producer") or k.endswith("producers") for k in sys.modules))')
        proc=subprocess.run([sys.executable,'-c',code,str(path)],cwd=ROOT,capture_output=True,text=True)
        require(proc.returncode==0,'verifier imports a producer: '+proc.stderr)
    return {'schema':1,'counts':dict(sorted(counts.items())), 'outcome_reasons':dict(sorted(reasons.items())),
            'outcomes_sha256':checksum.hexdigest(),'fixtures':fixtures,
            'scope':'Experimental complete decision certificates; independent finite controls, not proof of publication novelty, practical speedup, or formal checker verification.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=run()
    with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'},indent=2,sort_keys=True))
