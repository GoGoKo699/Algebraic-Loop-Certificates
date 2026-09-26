"""Independent orbit and inductivity tests for the target-free proof contract.

Only the test oracle walks trajectories. Full-state induction is checked on
small explicit domains, including states not reachable from the initial state.
The checks are not proofs of source-code soundness or publication priority.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from copy import deepcopy
from itertools import product
from collections import Counter
import argparse,hashlib,json,subprocess,tempfile
from alc.schema import Invalid, ResourceLimit, Problem
from research.separating_invariants_v1.producer import produce
from research.separating_invariants_v1.checker import compile_invariant, source_hash
from research.complete_orbits_v1.producer import produce as full_produce
from research.complete_orbits_v1.checker import decide as full_decide
from research.complete_orbits_v1 import algebra as alg


def require(ok,msg):
    if not ok:raise AssertionError(msg)


def document(p,A,c,x,y):
    return {'schema':'alc.problem.v1','field':{'kind':'prime','modulus':p},
            'matrix':[list(r) for r in A],'offset':list(c),'initial':list(x),'target':list(y)}


def step(d,x):
    p=d['field']['modulus']
    return tuple((sum(a*b for a,b in zip(r,x))+c)%p for r,c in zip(d['matrix'],d['offset']))


def orbit(d):
    x=tuple(d['initial']);out=[]
    while x not in out:
        out.append(x);x=step(d,x)
    require(x==tuple(d['initial']),'Non-bijective test family.')
    return out


def families():
    for p in (2,3):
        for a in product(range(p),repeat=4):
            if (a[0]*a[3]-a[1]*a[2])%p:yield p,[a[:2],a[2:]],[0,0]
    for p in (2,3,5):
        for a in range(1,p):
            for c in range(p):yield p,[[a]],[c]
    for a in product(range(2),repeat=4):
        if (a[0]*a[3]-a[1]*a[2])%2:
            for c in ((0,1),(1,0),(1,1)):yield 2,[a[:2],a[2:]],c


def companion(mu,p):
    n=len(mu)-1;A=[[0]*n for _ in range(n)]
    for j in range(n-1):A[j+1][j]=1
    for i in range(n):A[i][-1]=-mu[i]%p
    return A


def run():
    counts=Counter();kinds=Counter();hashes=hashlib.sha256();seen=set();fixtures=[]
    def one(d,full_comparison=False):
        truth=tuple(d['target']) in orbit(d)
        r=produce(d)
        require(r['status']!='unknown','Small producer exhausted budget.')
        if truth:
            require(r['status']=='no_exclusion','Reachable state falsely excluded.')
            counts['reachable_no_exclusion']+=1
        else:
            require(r['status']=='candidate','A negative case has no separating proof.')
            proof=r['certificate'];i=compile_invariant(d,proof)
            require(not i.contains(d['target']),'Negative target not excluded.')
            counts['negative_certificates']+=1;kinds[i.kind]+=1
            # The object must not become target-bound after compilation.
            same_source=deepcopy(d);same_source['target']=d['initial']
            reused=compile_invariant(same_source,proof)
            require(reused.query(d['initial'])['status']=='not_excluded','Initial state rejected on reuse.')
            counts['target_rebindings_checked']+=1
            key=json.dumps([i.binding,proof['invariant']],sort_keys=True)
            if key not in seen:
                seen.add(key)
                states=list(product(range(i.problem.p),repeat=len(i.problem.A)))
                included={x:i.contains(list(x)) for x in states}
                require(included[tuple(d['initial'])],'Initial state missing from invariant.')
                for x in states:
                    require(not included[x] or included[step(d,x)],'Invariant fails one-step closure.')
                    require(not (x in orbit(d)) or included[x],'Invariant excludes actual orbit.')
                    counts['full_domain_induction_checks']+=1
                counts['distinct_invariant_predicates_checked']+=1
            if full_comparison:
                f=full_produce(d)
                require(f['status']=='candidate','Prior certificate producer failed.')
                verdict=full_decide(d,f['certificate'])
                require(verdict['status']=='unreachable','Independent old decision disagrees.')
                counts['prior_negative_checker_comparisons']+=1
        hashes.update(json.dumps([d,r],sort_keys=True).encode())
        counts['decision_cases']+=1
        return r
    for p,A,c in families():
        counts['recurrences']+=1
        states=list(product(range(p),repeat=len(A)))
        for x in states:
            for y in states:one(document(p,A,c,x,y))
    # Nontrivial comparison fields and repeated factors, at fixed initial state.
    factored=[(2,[((1,1,1),3)]),
              (3,[((1,0,1),1),((2,1,1),1)]),
              (3,[((2,1),2),((1,1),2)]),
              (5,[((4,1),3)])]
    for p,factors in factored:
        mu=(1,)
        for f,e in factors:
            for _ in range(e):mu=alg.mul(mu,f,p)
        n=len(mu)-1;A=companion(mu,p);x=[1]+[0]*(n-1)
        for y in product(range(p),repeat=n):
            one(document(p,A,[0]*n,x,y),full_comparison=True)
            counts['mixed_and_repeated_cases']+=1
    named=[('same_multiplier',document(13,[[4,0],[0,5]],[0,0],[1,1],[10,12])),
           ('subgroup_obstruction',document(5,[[4]],[0],[1],[2])),
           ('outside_span',document(7,[[1,0],[0,1]],[0,0],[1,0],[0,1]))]
    mu=(1,)
    for _ in range(3):mu=alg.mul(mu,(4,1),5)
    beta=alg.add((1,),alg.mul((4,1),(4,1),5),5)
    named.append(('nilpotent_obstruction',document(5,companion(mu,5),[0]*3,[1,0,0],beta)))
    for label,d in named:
        r=one(d,True);proof=r['certificate'];ci=compile_invariant(d,proof)
        old=full_produce(d)['certificate'];full_decide(d,old)
        allstates=list(product(range(ci.problem.p),repeat=len(ci.problem.A)))
        accepted=[list(x) for x in allstates if ci.contains(list(x))]
        fixtures.append({'name':label,'problem':d,'certificate':proof,
                         'accepted_states':accepted,'excluded_count':len(allstates)-len(accepted),
                         'orbit_length':len(orbit(d)),
                         'compact_bytes':len(json.dumps(proof,sort_keys=True,separators=(',',':')).encode()),
                         'old_complete_bytes':len(json.dumps(old,sort_keys=True,separators=(',',':')).encode())})
    # Equal powers may be checked in a reducible algebra. Irreducibility is NOT
    # needed for a valid homomorphism and common scaling identity.
    d=fixtures[0]['problem'];proof=fixtures[0]['certificate']
    altered=deepcopy(proof);altered['invariant']['algebra_modulus']=[0,12,1]
    reducible=compile_invariant(d,altered)
    require(not reducible.contains(d['target']),'Valid reducible-algebra proof rejected.')
    counts['reducible_algebra_positive_control']=1
    # A satisfying state may still be unreachable: do not turn the invariant
    # predicate into a claim of an exact orbit characterization.
    require((0,0) not in orbit(d),'Overapproximation example wrong.')
    require(compile_invariant(d,proof).query([0,0])['status']=='not_excluded','Overapproximation turned into a verdict.')
    counts['strict_overapproximation_control']=1
    # Alter obligations rather than merely changing an outcome label.
    bads=[]
    for key,val in [('schema','wrong'),('source_sha256','0'*64),('prime_proofs',[]),('inverse_matrix',[[1,0],[0,1]])]:
        b=deepcopy(proof);b[key]=val;bads.append((d,b))
    for key,val in [('left_root',[1]),('right_root',[2]),('left_exponent',True),
                    ('right_exponent',4),('algebra_modulus',[1]),('left_root',[5,0])]:
        b=deepcopy(proof);b['invariant'][key]=val;bads.append((d,b))
    b=deepcopy(proof);b['invariant']['log']=0;bads.append((d,b))
    sub=fixtures[1]
    b=deepcopy(sub['certificate']);b['invariant']['divisor']=[0,1];bads.append((sub['problem'],b))
    b=deepcopy(sub['certificate']);b['invariant']['exponent']=1;bads.append((sub['problem'],b))
    changed=deepcopy(d);changed['initial']=[1,2];bads.append((changed,proof))
    for sp,b in bads:
        try:compile_invariant(sp,b)
        except (Invalid,ResourceLimit):counts['malformed_obligations_rejected']+=1
        else:raise AssertionError('Forged construction accepted.')
    for state in ([True,1],[13,1],[1],[-1,0]):
        try:compile_invariant(d,proof).contains(state)
        except Invalid:counts['bad_query_states_rejected']+=1
        else:raise AssertionError('Bad state accepted.')
    require(produce(d,max_work=0)['status']=='unknown','Budget exhaustion became a result.')
    counts['unknown_control']=1
    # Test forbidden proof-search routines by disabling them in a fresh process.
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'fixture.json';path.write_text(json.dumps(fixtures))
        code='''import sys,json
from research.separating_invariants_v1.checker import compile_invariant
from research.complete_orbits_v1 import algebra as alg
def forbidden(*a,**kw): raise RuntimeError("forbidden search/certificate routine")
alg.irreducible=forbidden
'''
        code+='''
for f in json.load(open(sys.argv[1])):
    v=compile_invariant(f['problem'],f['certificate'])
    if v.contains(f['problem']['target']): raise RuntimeError('target accepted')
if any(k.endswith('.producer') or k.endswith('.producers') for k in sys.modules):
    raise RuntimeError('checker imports a producer')
'''
        out=subprocess.run([sys.executable,'-c',code,str(path)],cwd=ROOT,capture_output=True,text=True)
        require(out.returncode==0,'Proof checker dependency control failed: '+out.stderr)
    counts['checker_import_and_irreducibility_control']=1
    return {'schema':1,'counts':dict(sorted(counts.items())),'kinds':dict(sorted(kinds.items())),
            'outcomes_sha256':hashes.hexdigest(),'fixtures':fixtures,
            'scope':'Exact small-domain inductive-invariant and exclusion checks. The complete scheme has a mathematical proof; this is not formal code verification, novelty clearance, or a speed advantage.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise SystemExit('Refusing to overwrite prior evidence.')
    result=run()
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'},indent=2,sort_keys=True))
