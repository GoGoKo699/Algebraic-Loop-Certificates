"""Paired scalar decisions and native baseline timings, not a full matrix benchmark.

Optional SymPy. Exact outcomes are separated from nonportable timings. Both
methods get only the same canonical affine instance and no factor/order hints.
"""
from pathlib import Path
from math import gcd
import argparse,hashlib,json,platform,statistics,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.scalar_comparison_v1.baseline import reduce_instance,solve
from research.modular_lifting_v1.producer import produce
from research.modular_lifting_v1.lifting import decide


def require(ok,message):
    if not ok: raise AssertionError(message)


def instance(N,A,c,a,b):
    return {'schema':'alc.modular-problem.v1','modulus':N,'matrix':[[A]],
            'offset':[c],'initial':[a],'target':[b]}


def expected(N,A,c,a):
    path=[];x=a
    while x not in path:
        path.append(x);x=(A*x+c)%N
    require(x==a,'Test input was not a permutation.')
    return path


def replay(A,c,n,x,N):
    # Independently implemented scalar affine squaring, no matrix kernel.
    mul,add=1,0
    while n:
        if n&1: mul,add=A*mul%N,(A*add+c)%N
        A,c=A*A%N,(A*c+c)%N;n>>=1
    return (mul*x+add)%N


def run(repeats):
    import sympy
    count=paired=0;branches={};h=hashlib.sha256()
    # All scalar affine inputs for these fixed moduli, plus targeted ring cases.
    for N in range(2,11):
        for A in range(1,N):
            if gcd(A,N)!=1:continue
            for c in range(N):
                for a in range(N):
                    orbit=expected(N,A,c,a)
                    for b in range(N):
                        truth=(orbit.index(b),len(orbit)) if b in orbit else None
                        reduced=reduce_instance(N,A,c,a,b)
                        branches[reduced['kind']]=branches.get(reduced['kind'],0)+1
                        answer=solve(N,A,c,a,b)
                        require(answer==truth,'Native affine reduction differs from enumeration.')
                        # Exact per-query comparisons of the proof-producing path
                        # on all moduli through 6, not an unmatched scalar subset.
                        if N<=6:
                            doc=instance(N,A,c,a,b); out=produce(doc)
                            require(out['status']=='candidate','Small certificate production failed.')
                            cert=out['certificate'];v=decide(doc,cert)
                            decoded=None if v['status']=='unreachable' else (v['first'],v['period'])
                            require(decoded==truth,'Certificate and native scalar solver disagree.')
                            paired+=1
                        h.update(json.dumps([N,A,c,a,b,answer]).encode());count+=1
    protocol=[(2**w,5,1,0,2**(w-1)+123,True) for w in (16,32,64)]
    protocol += [(25,2,0,5,4,True),(12,11,0,1,5,False),(8,1,4,0,2,False)]
    # A marker on each row specifies whether b is made by a known test exponent.
    rows=[];timing_rows=[]
    for N,A,c,a,z,construct in protocol:
        b=replay(A,c,z,a,N) if construct else z
        args=(N,A,c,a,b);doc=instance(*args)
        # Warm-up BOTH procedures before reporting steady-process fit costs.
        native=solve(*args);out=produce(doc);require(out['status']=='candidate','Producer exhausted.')
        cert=out['certificate'];verified=decide(doc,cert)
        got=None if verified['status']=='unreachable' else (verified['first'],verified['period'])
        require(native==got,'Matched displayed instance disagrees.')
        if native:
            require(replay(A,c,native[0],a,N)==b and replay(A,c,native[1],a,N)==a,'Final native replay failed.')
        ns=[];ps=[];vs=[]
        for j in range(repeats):
            # Alternate order to reduce one fixed ordering bias. These are not
            # cold-start timings and do not include module import or process startup.
            def classical():
                t=time.perf_counter_ns();answer=solve(*args);elapsed=time.perf_counter_ns()-t
                require(answer==native,'Nondeterministic mathematical result.');ns.append(elapsed)
            def certifying():
                t=time.perf_counter_ns();o=produce(doc);elapsed=time.perf_counter_ns()-t
                require(o['status']=='candidate','Repeated producer exhausted.');ps.append(elapsed)
                t=time.perf_counter_ns();v=decide(doc,o['certificate']);vs.append(time.perf_counter_ns()-t)
                require(v==verified,'Repeated verifier result differs.')
            if j%2:classical();certifying()
            else:certifying();classical()
        row={'input':doc,'native_answer':None if native is None else list(native),
             'reduced_native_problem':reduce_instance(*args),
             'certificate_bytes':len(json.dumps(cert,sort_keys=True,separators=(',',':')).encode()),
             'certificate_sha256':hashlib.sha256(json.dumps(cert,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
             'verified_answer':got,'checked_field_layers':verified['field_certificates_checked']}
        rows.append(row)
        timing_rows.append({'modulus':N,'repeats':repeats,
            'native_ns':ns,'producer_ns':ps,'checker_ns':vs,
            'median_native_ns':statistics.median(ns),'median_producer_ns':statistics.median(ps),
            'median_checker_ns':statistics.median(vs)})
    exact={'schema':1,'sympy_version':sympy.__version__,'exhaustive_scalar_cases':count,
           'paired_certificate_cases':paired,'reduction_branches':branches,
           'outcomes_sha256':h.hexdigest(),'displayed_cases':rows,
           'scope':'Native scalar algebra comparison. Not a native matrix-orbit analyzer, formally verified baseline, or a proof of novelty/speedup. Timings compare same answers but certificate pipeline additionally returns independent evidence.'}
    timings={'schema':1,'python':platform.python_version(),'platform':platform.platform(),
             'sympy_version':sympy.__version__,'protocol':'Warm process; no factor/order hints; alternating order; producer and independent checking recorded separately. Not cold startup or best-possible implementation.',
             'cases':timing_rows}
    return exact,timings

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--timings',type=Path,required=True);p.add_argument('--repeats',type=int,default=7)
    a=p.parse_args()
    if a.output.exists() or a.timings.exists():raise SystemExit('Refusing to replace evidence.')
    if not 1<=a.repeats<=100:raise SystemExit('repeats must be between 1 and 100.')
    exact,timings=run(a.repeats)
    for path,data in ((a.output,exact),(a.timings,timings)):
        with path.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'cases':exact['exhaustive_scalar_cases'],'paired':exact['paired_certificate_cases'],
                     'timings':[{'N':r['modulus'],'native_ms':r['median_native_ns']/1e6,
                        'producer_ms':r['median_producer_ns']/1e6,'checker_ms':r['median_checker_ns']/1e6} for r in timings['cases']]},indent=2))
