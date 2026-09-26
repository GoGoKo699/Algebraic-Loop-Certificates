"""Exact independent tests for prime-power and composite-modulus composition.

Small cases enumerate trajectories ONLY in the independent test oracle. The
producer/checker do not enumerate them. The 64-bit example has a supplied known
construction, not a new advantage workload or an exhaustive 2**64 experiment.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from collections import Counter
from copy import deepcopy
from itertools import product
from math import gcd
import hashlib
import json
import random
from alc.schema import Invalid, ResourceLimit, digest
from research.modular_lifting_v1.lifting import decide, next_layer
from research.modular_lifting_v1.producer import produce


def problem(N,A,c,a,b):
    return dict(schema='alc.modular-problem.v1',modulus=N,matrix=A,offset=c,initial=a,target=b)


def direct_step(doc,x):
    N=doc['modulus'];A=doc['matrix'];c=doc['offset']
    return tuple((sum(A[i][j]*x[j] for j in range(len(x)))+c[i])%N for i in range(len(x)))


def orbit(doc):
    start=tuple(doc['initial']);x=start;seen=[]
    while True:
        if x in seen:raise AssertionError('expected a pure cycle')
        seen.append(x);x=direct_step(doc,x)
        if x==start:return seen


def check_one(doc,counts,outcomes):
    hist=orbit(doc);target=tuple(doc['target']);where=hist.index(target) if target in hist else None
    result=produce(doc)
    if result['status']!='candidate':raise AssertionError('budget unexpectedly exhausted on small control')
    cert=result['certificate'];got=decide(doc,cert)
    expected=({'status':'unreachable'} if where is None else
              {'status':'reachable','first':where,'period':len(hist)})
    if any(got[k]!=v for k,v in expected.items()):raise AssertionError('derived modular result differs from full orbit')
    counts['cases']+=1;counts[got['reason']]+=1
    counts['field_certificates_checked']+=got['field_certificates_checked']
    if result['metrics']['trajectory_steps']!=0:raise AssertionError('producer used trajectory enumeration')
    bad=deepcopy(cert)
    bad['claim']=({'status':'reachable','first':0,'period':1} if where is None else {'status':'unreachable'})
    try:decide(doc,bad)
    except Invalid:counts['opposite_claims_rejected']+=1
    else:raise AssertionError('forged opposite outcome accepted')
    outcomes.update(json.dumps([doc,expected],sort_keys=True).encode())
    return got,cert


def families():
    # All scalar invertible affine recurrences and all input/target states.
    for N in (2,4,6,8,9,10,12):
        for a in range(N):
            if gcd(a,N)!=1:continue
            for c,x,y in product(range(N),repeat=3):
                yield problem(N,[[a]],[c],[x],[y]),'exhaustive_scalar'
    # All invertible 2x2 matrices over Z/4Z, two translations, all state pairs.
    # There are 96 matrices: |GL(2,F2)| * 2**4.
    for vals in product(range(4),repeat=4):
        if gcd(vals[0]*vals[3]-vals[1]*vals[2],4)!=1:continue
        A=[list(vals[:2]),list(vals[2:])]
        for c in ([0,0],[1,2]):
            for x,y in product(product(range(4),repeat=2),repeat=2):
                yield problem(4,A,c,list(x),list(y)),'exhaustive_matrix_mod4'


def run():
    counts=Counter();outcomes=hashlib.sha256()
    for doc,group in families():
        check_one(doc,counts,outcomes);counts[group]+=1
    # Seeded composite-ring matrices exercise nonunit entries and multiple primes.
    rng=random.Random(2026092621)
    for N in (6,8,9,12,25,27):
        added=0
        while added<20:
            A=[[rng.randrange(N) for _ in range(2)] for _ in range(2)]
            if gcd(A[0][0]*A[1][1]-A[0][1]*A[1][0],N)!=1:continue
            doc=problem(N,A,[rng.randrange(N) for _ in range(2)],
                        [rng.randrange(N) for _ in range(2)],[rng.randrange(N) for _ in range(2)])
            check_one(doc,counts,outcomes);counts['seeded_matrix_cases']+=1;added+=1
    fixtures={}
    fixed={
      'period_ratio_not_p':problem(25,[[2]],[0],[5],[20]),
      'no_unit_pivot':problem(6,[[2,3],[3,2]],[0,0],[1,0],[2,3]),
      'incompatible_times':problem(12,[[11]],[0],[1],[5]),
      'late_obstruction':problem(8,[[1]],[2],[0],[1]),
      'nilpotent_digits_zero_shift':problem(16,[[1,1],[0,1]],[0,0],[0,1],[7,1]),
    }
    for name,doc in fixed.items():
        got,cert=check_one(doc,counts,outcomes)
        fixtures[name]={'problem':doc,'certificate':cert,'result':got}
    ratio=fixtures['period_ratio_not_p']['certificate']['local_proofs'][0]['layers']
    if [x['claim']['period'] for x in ratio]!=[1,4]:raise AssertionError('point-period growth control failed')
    if fixtures['incompatible_times']['result']['reason']!='incompatible_prime_power_times':
        raise AssertionError('intended CRT inconsistency was not exercised')
    # A genuine obstruction arising only above the residue field.
    later=problem(8,[[1]],[4],[0],[2]);r,c=check_one(later,counts,outcomes)
    if r['status']!='unreachable' or r['local_results'][0]['failed_precision']!=2:
        raise AssertionError('late high-digit obstruction not exercised')
    fixtures['genuine_late_obstruction']={'problem':later,'certificate':c,'result':r}
    # Independent binary affine powering for a standard 64-bit wraparound LCG.
    width=64;N=1<<width;desired=(1<<63)+123456789
    multiplier,increment=5,1
    acc_m,acc_c=1,0;m,c=multiplier,increment;t=desired
    while t:
        if t&1:acc_m,acc_c=(m*acc_m)%N,(m*acc_c+c)%N
        m,c=(m*m)%N,(m*c+c)%N;t>>=1
    doc=problem(N,[[multiplier]],[increment],[0],[acc_c])
    out=produce(doc,max_work=200000)
    if out['status']!='candidate':raise AssertionError('64-bit reference exhausted')
    cert=out['certificate'];answer=decide(doc,cert)
    if answer['status']!='reachable' or answer['first']!=desired or answer['period']!=N:
        raise AssertionError('64-bit lifting answer differs from constructed hit and full-period theorem')
    fixtures['word64']={'problem':doc,'certificate':cert,'result':answer,
        'construction':'x -> 5*x+1 modulo 2**64; full period is the classical mixed-congruential case.',
        'known_time':desired,'serialized_certificate_bytes':len(json.dumps(cert,separators=(',',':')).encode()),
        'scope':'64 derived F2 certificates; no orbit enumeration, new speedup, real program frontend or bitvector solver comparison.'}
    counts['large_word_cases']=1
    from research.modular_lifting_v1.consumer import query
    for label,item in fixtures.items():
        if label=='word64': continue
        doc=item['problem'];hist=orbit(doc);target=tuple(doc['target'])
        offset=hist.index(target) if target in hist else None
        for low,high in ((0,0),(0,25),(6,48),(17,31)):
            consumer=query(doc,item['certificate'],low,high)
            hits=[t for t in range(low,high+1) if hist[t%len(hist)]==target]
            expected_loop={'terminates':offset is not None,'body_executions':offset}
            if consumer['count']!=len(hits) or consumer['point_guard_loop']!=expected_loop:
                raise AssertionError('reverified modular consumer disagrees with direct loop')
            counts['reverified_consumers']+=1
    word=fixtures['word64'];consumer=query(word['problem'],word['certificate'],0,10**100)
    expected_count=(10**100-desired)//N+1
    if consumer['count']!=expected_count or consumer['point_guard_loop']['body_executions']!=desired:
        raise AssertionError('large modular consumer arithmetic failed')
    counts['large_horizon_consumer']=1
    # Mutate the proof interfaces, not just their asserted outcome.
    doc=fixtures['period_ratio_not_p']['problem'];cert=fixtures['period_ratio_not_p']['certificate']
    bads=[]
    z=deepcopy(cert);z['local_proofs'][0]['layers'].pop();bads.append(z)
    z=deepcopy(cert);z['local_proofs'][0]['layers'][1]['problem_sha256']='0'*64;bads.append(z)
    z=deepcopy(cert);z['local_proofs'][0]['prime']=True;bads.append(z)
    z=deepcopy(cert);z['modulus_factors']=[[5,1]];bads.append(z)
    z=deepcopy(cert);z['modulus_factors']=[[25,1]];bads.append(z)
    z=deepcopy(cert);z['inverse_matrix'][0][0]=(z['inverse_matrix'][0][0]+1)%25;bads.append(z)
    z=deepcopy(cert);z['claim']['first']=True;bads.append(z)
    z=deepcopy(cert);z['claim']['period']*=5;bads.append(z)
    z=deepcopy(cert);z['local_proofs'][0]['layers'].append(deepcopy(z['local_proofs'][0]['layers'][-1]));bads.append(z)
    for bad in bads:
        try:decide(doc,bad)
        except Invalid:counts['proof_mutations_rejected']+=1
        else:raise AssertionError('malformed modular proof accepted')
    # Even a valid lower certificate cannot be transplanted to another fiber.
    altered=deepcopy(doc);altered['target']=[10]
    try:decide(altered,cert)
    except Invalid:counts['wrong_problem_rejected']+=1
    else:raise AssertionError('changed modular instance accepted')
    limited=produce(doc,max_work=0)
    if limited['status']!='unknown' or 'certificate' in limited:raise AssertionError('resource limit masquerades as proof')
    counts['unknown_control']=1
    # Primary production and prime-field research APIs must refuse ring semantics.
    from alc.schema import Problem
    try:Problem.parse(doc)
    except Invalid:counts['separate_schema_control']=1
    else:raise AssertionError('ring instance accepted by prime-field parser')
    # No untrusted derived layer should be treated as an externally supplied fact.
    try:next_layer(((2,),),(0,),(1,),(4,),5,1,1,1)
    except Invalid:counts['bad_lower_schedule_rejected']=1
    else:raise AssertionError('nonperiodic lower schedule not rejected')
    return dict(schema=1,counts=dict(sorted(counts.items())),outcomes_sha256=outcomes.hexdigest(),fixtures=fixtures,
        scope='Exact new modular-wrapper controls. All small trajectories are independently enumerated; '
              'producer and checker use powering and finite-field subcertificates. '
              'The 64-bit source is a classical easy family, not a native analyzer or speedup experiment.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite report')
    result=run()
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'counts':result['counts'],'outcomes_sha256':result['outcomes_sha256'],
                      'word64':result['fixtures']['word64']['result']},indent=2,sort_keys=True))
