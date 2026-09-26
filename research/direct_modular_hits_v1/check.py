"""Independent finite controls and an optional matched positive-proof comparison."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from copy import deepcopy
from itertools import product
from math import gcd
import argparse,hashlib,json,platform,statistics,subprocess,tempfile,time
from alc.schema import Invalid,digest
from research.direct_modular_hits_v1.checker import verify
from research.direct_modular_hits_v1.producer import assemble


def problem(N,A,c,a,b):
    return dict(schema='alc.modular-problem.v1',modulus=N,matrix=A,offset=c,initial=a,target=b)


def orbit(doc):
    A,c,N=doc['matrix'],doc['offset'],doc['modulus'];a=tuple(doc['initial']);x=a;out=[]
    while x not in out:
        out.append(x);x=tuple((sum(u*v for u,v in zip(row,x))+z)%N for row,z in zip(A,c))
    if x!=a:raise AssertionError('test family not bijective')
    return out


def families():
    for N in range(2,13):
        for A in range(1,N):
            if gcd(A,N)!=1:continue
            for c,a in product(range(N),repeat=2):yield N,[[A]],[c],[a]
    for flat in product(range(4),repeat=4):
        if gcd(flat[0]*flat[3]-flat[1]*flat[2],4)!=1:continue
        for c in ([0,0],[1,2]):
            for a in product(range(4),repeat=2):yield 4,[list(flat[:2]),list(flat[2:])],c,list(a)


def run():
    count=wrong=nonminimal=period_one=0;h=hashlib.sha256();fixture=None
    for N,A,c,a in families():
        base=problem(N,A,c,a,a);path=orbit(base);r=len(path)
        for b in product(range(N),repeat=len(A)):
            doc=problem(N,A,c,a,list(b));t=path.index(b) if b in path else None
            cert=assemble(doc,t if t is not None else 0,r)['certificate']
            if t is None:
                try:verify(doc,cert)
                except Invalid:wrong+=1
                else:raise AssertionError('false reachable assertion accepted')
            else:
                ans=verify(doc,cert)
                if (ans['first'],ans['period'])!=(t,r):raise AssertionError('wrong direct schedule')
                count+=1;period_one+=int(r==1)
                if 2*r<=N**len(A):
                    bad=assemble(doc,t,2*r)['certificate']
                    try:verify(doc,bad)
                    except Invalid:nonminimal+=1
                    else:raise AssertionError('nonminimal return accepted')
                if fixture is None and r>1:fixture=(doc,cert)
            h.update(json.dumps([N,A,c,a,b,t,r]).encode())
    doc,cert=fixture;mutations=[]
    for key,v in [('schema','wrong'),('problem_sha256','0'*64),('first',True),
                  ('first',-1),('first',cert['period']),('period_factors',[])]:
        bad=deepcopy(cert);bad[key]=v;mutations.append(bad)
    bad=deepcopy(cert);bad['inverse_matrix'][0][0]=0;mutations.append(bad)
    for bad in mutations:
        try:verify(doc,bad)
        except Invalid:pass
        else:raise AssertionError('malformed direct proof accepted')
    # Nonunit matrix entries with unit determinant; never use a field inverse.
    doc=problem(6,[[2,3],[3,2]],[0,0],[1,0],[2,3]);path=orbit(doc)
    cert=assemble(doc,path.index((2,3)),len(path))['certificate'];verify(doc,cert)
    # Checker never needs a primality proof of composite N, nor N's factors.
    if any(q['p']==6 for q in cert['prime_proofs']):raise AssertionError('spurious modulus proof')
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'proof.json';p.write_text(json.dumps([doc,cert]))
        code=('import sys,json;from research.direct_modular_hits_v1.checker import verify;'
              'd,c=json.load(open(sys.argv[1]));verify(d,c);'
              'raise SystemExit(any(k.endswith("producer") or k.endswith("producers") for k in sys.modules))')
        out=subprocess.run([sys.executable,'-c',code,str(p)],cwd=ROOT,capture_output=True,text=True)
        if out.returncode:raise AssertionError('checker imported producer: '+out.stderr)
    return dict(schema=1,positive_certificates=count,false_hits_rejected=wrong,
                nonminimal_periods_rejected=nonminimal,period_one_cases=period_one,
                malformed_proofs_rejected=len(mutations),outcomes_sha256=h.hexdigest(),
                scope='Independent finite ring positive-certificate audit. No new order theorem, compact general negative proof, or runtime advantage claimed.')


def benchmark(repeats):
    from research.scalar_comparison_v1.baseline import solve
    from research.scalar_comparison_v1.check import replay
    from research.modular_lifting_v1.producer import produce
    from research.modular_lifting_v1.lifting import decide
    import sympy
    rows=[]
    for w in (16,32,64):
        N=1<<w;t=(1<<(w-1))+123;b=replay(5,1,t,0,N)
        doc=problem(N,[[5]],[1],[0],[b])
        # Warm all paths. The same ordinary solver supplies both candidate times.
        hit=solve(N,5,1,0,b);direct=assemble(doc,*hit)['certificate'];verify(doc,direct)
        layered=produce(doc)['certificate'];decide(doc,layered)
        ns=[];ps=[];vs=[];lps=[];lvs=[]
        for j in range(repeats):
            start=time.perf_counter_ns();candidate=solve(N,5,1,0,b);ns.append(time.perf_counter_ns()-start)
            if candidate!=hit:raise AssertionError('native answer changed')
            def direct_path():
                start=time.perf_counter_ns();c=assemble(doc,*candidate)['certificate'];ps.append(time.perf_counter_ns()-start)
                start=time.perf_counter_ns();v=verify(doc,c);vs.append(time.perf_counter_ns()-start)
                if (v['first'],v['period'])!=hit:raise AssertionError('direct result changed')
            def layered_path():
                start=time.perf_counter_ns();c=produce(doc)['certificate'];lps.append(time.perf_counter_ns()-start)
                start=time.perf_counter_ns();v=decide(doc,c);lvs.append(time.perf_counter_ns()-start)
                if (v['first'],v['period'])!=hit:raise AssertionError('layered result changed')
            if j%2:direct_path();layered_path()
            else:layered_path();direct_path()
        encoded=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
        rows.append(dict(width=w,problem=doc,first=hit[0],period=hit[1],
                    direct_certificate=direct,direct_bytes=len(encoded(direct)),
                    layered_bytes=len(encoded(layered)),layered_sha256=hashlib.sha256(encoded(layered)).hexdigest(),
                    repeats=repeats,native_ns=ns,assembly_ns=ps,checking_ns=vs,
                    layered_production_ns=lps,layered_checking_ns=lvs,
                    median_native_ns=statistics.median(ns),median_assembly_ns=statistics.median(ps),
                    median_checking_ns=statistics.median(vs),
                    median_layered_production_ns=statistics.median(lps),median_layered_checking_ns=statistics.median(lvs)))
    return dict(schema=1,python=platform.python_version(),platform=platform.platform(),sympy=sympy.__version__,
                cases=rows,scope='Same positive answer and independent-proof obligation; two different encodings and producers. Warm-process seven-repeat controls, not broad performance or novelty evidence. Native solve must be added to direct assembly and checking cost.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--benchmark',type=Path);p.add_argument('--repeats',type=int,default=7);a=p.parse_args()
    if a.output.exists() or (a.benchmark and a.benchmark.exists()):raise SystemExit('Refusing to overwrite evidence')
    if not 1<=a.repeats<=100:raise SystemExit('Invalid repeat count')
    result=run()
    with a.output.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    if a.benchmark:
        result=benchmark(a.repeats)
        with a.benchmark.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(result if not a.benchmark else
         [{'width':x['width'],'bytes':[x['direct_bytes'],x['layered_bytes']],
           'ms':[x['median_native_ns']/1e6,x['median_assembly_ns']/1e6,x['median_checking_ns']/1e6,
                 x['median_layered_production_ns']/1e6,x['median_layered_checking_ns']/1e6]} for x in result['cases']],indent=2))
