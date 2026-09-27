"""Bounded native-SMT gate for checking power-relation loop invariants.

No new orbit API. Three routes receive the same recurrence and invariant:
raw finite-field verification conditions; elementary multiplication-DAG
proof decomposition; the existing separating-invariant checker. The native
routes are solver verdicts, not independently replayed proof-assistant proofs.
"""
from pathlib import Path
import argparse, hashlib, json, os, platform, subprocess, sys, tempfile, time
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from alc.schema import Invalid
from research.complete_orbits_v1.producer import PrimeBuilder, Budget, matrix_inverse
from research.separating_invariants_v1.checker import compile_invariant, source_hash


def mul(A, B, p):
    return [[sum(x*y for x,y in zip(row,col)) % p for col in zip(*B)] for row in A]


def cases():
    """Fixed before native execution. All are source-visible algebraic controls."""
    out = []
    for p, g, e, f in ((13,2,3,2), (257,3,17,16), (65537,3,65,64),
                       (65537,3,257,256), (65537,3,1025,1024)):
        for mixed in (False, True):
            S = [[1,1],[1,2]] if mixed else [[1,0],[0,1]]
            Si = matrix_inverse(S,p)
            a = [sum(r) % p for r in Si]
            for broken in (False, True):
                alpha, beta = pow(g,f,p), pow(g,e,p)
                if broken: beta = beta*g % p
                A = mul(mul(Si,[[alpha,0],[0,beta]],p),S,p)
                out.append(dict(name=f'p{p}_e{e}_{"mixed" if mixed else "diagonal"}_{"broken" if broken else "valid"}',
                    p=p,e=e,f=f,S=S,A=A,initial=a,alpha=alpha,beta=beta,
                    expected='sat' if broken else 'unsat'))
    return out


def certificate(c):
    p=c['p']; pb=PrimeBuilder(Budget()); pb.prime(p)
    doc=dict(schema='alc.problem.v1',field=dict(kind='prime',modulus=p),
             matrix=c['A'],offset=[0,0],initial=c['initial'],target=c['initial'])
    proof=dict(schema='alc.separating-invariant.v1',source_sha256=source_hash(doc),
               prime_proofs=[pb.proofs[q] for q in sorted(pb.proofs)],
               inverse_matrix=matrix_inverse(c['A'],p),
               invariant=dict(kind='equal-powers',algebra_modulus=[0,1],
                   left_root=[c['alpha']],right_root=[c['beta']],
                   left_exponent=c['e'],right_exponent=c['f']))
    return doc,proof


def truth(c, x):
    p=c['p']; u,v=[sum(a*b for a,b in zip(row,x))%p for row in c['S']]
    return pow(u,c['e'],p)==pow(v,c['f'],p)


def step(c, x):
    return [sum(a*b for a,b in zip(row,x))%c['p'] for row in c['A']]


def dag(n):
    """Every node after input1 is a product of earlier nodes, with value x**j."""
    seq=[];seen={1}
    def rec(k):
        if k in seen:return
        j=k//2;rec(j);rec(k-j);seq.append((k,j,k-j));seen.add(k)
    rec(n)
    return seq


def formula(c, decomposed):
    """QF_FF counterexample queries; arithmetic is modulo p, never a bitvector."""
    p=c['p']; lines=['(set-logic QF_FF)',f'(define-sort F () (_ FiniteField {p}))']
    const=lambda a:f'(as ff{a%p} F)'
    prod=lambda a,b:f'(ff.mul {a} {b})'
    add=lambda a,b:f'(ff.add {a} {b})'
    eq=lambda a,b:f'(= {a} {b})'
    def linear(row,vals):return add(prod(const(row[0]),vals[0]),prod(const(row[1]),vals[1]))
    def define(name,expr):lines.append(f'(define-fun {name} () F {expr})');return name
    for v in ('x','y','r','s','v','w'):lines.append(f'(declare-fun {v} () F)')
    src=('x','y'); nxt=[define(f'n{i}',linear(row,src)) for i,row in enumerate(c['A'])]
    obs=[define(f'o{i}',linear(row,src)) for i,row in enumerate(c['S'])]
    after=[define(f'a{i}',linear(row,nxt)) for i,row in enumerate(c['S'])]
    bad=[]; obligations=[]
    if decomposed:
        for i,scale in enumerate((c['alpha'],c['beta'])):
            obligations.append(eq(after[i],prod(const(scale),obs[i])))
        for exponent,scale in ((c['e'],c['alpha']),(c['f'],c['beta'])):
            for k,i,j in dag(exponent):
                premises=f'(and {eq("v",prod(const(pow(scale,i,p)),"r"))} {eq("w",prod(const(pow(scale,j,p)),"s"))})'
                conclusion=eq(prod('v','w'),prod(const(pow(scale,k,p)),prod('r','s')))
                obligations.append(f'(=> {premises} {conclusion})')
        final=eq(prod(const(pow(c['alpha'],c['e'],p)),'r'),prod(const(pow(c['beta'],c['f'],p)),'s'))
        obligations.append(f'(=> {eq("r","s")} {final})')
        bad=[f'(not {o})' for o in obligations]
        lines.append('(assert (or '+' '.join(bad)+'))')
    else:
        def power(base,n,prefix):
            names={1:base}
            for k,i,j in dag(n):names[k]=define(f'{prefix}{k}',prod(names[i],names[j]))
            return names[n]
        left=power(obs[0],c['e'],'u');right=power(obs[1],c['f'],'v')
        newleft=power(after[0],c['e'],'a');newright=power(after[1],c['f'],'b')
        lines.append('(assert (and '+eq(left,right)+' (not '+eq(newleft,newright)+')))' )
    lines.append('(check-sat)')
    return '\n'.join(lines)+'\n',len(obligations)


def local_check():
    count=states=nodes=0; corpus=[]
    for c in cases():
        if not truth(c,c['initial']):raise AssertionError('Initialization fails.')
        common=pow(c['alpha'],c['e'],c['p'])==pow(c['beta'],c['f'],c['p'])
        if common!=(c['expected']=='unsat'):raise AssertionError('Construction outcome differs.')
        doc,proof=certificate(c)
        try:obj=compile_invariant(doc,proof);accepted=True
        except Invalid:accepted=False
        if accepted!=common:raise AssertionError('Existing certificate checker mismatch.')
        if not common and truth(c,step(c,c['initial'])):raise AssertionError('Broken case lacks its explicit counterexample.')
        # Exhaust the small field and a deterministic sample in the larger fields.
        domain=((x,y) for x in range(c['p']) for y in range(c['p'])) if c['p']==13 else (
            ((i*i+3)%c['p'],(7*i+11)%c['p']) for i in range(64))
        for x in domain:
            if common and truth(c,x) and not truth(c,step(c,x)):raise AssertionError('Induction fails.')
            if common and obj.contains(list(x))!=truth(c,x):raise AssertionError('Exported predicate differs from checked invariant.')
            states+=1
        for n in (c['e'],c['f']):
            exps={1:1}
            for k,i,j in dag(n):
                if exps[i]+exps[j]!=k:raise AssertionError('DAG dependency invalid.')
                exps[k]=k;nodes+=1
        raw,_=formula(c,False);dec,obs=formula(c,True)
        corpus.append(dict(case=c,raw_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                           decomposed_sha256=hashlib.sha256(dec.encode()).hexdigest(),
                           raw_bytes=len(raw.encode()),decomposed_bytes=len(dec.encode()),obligations=obs))
        count+=1
    return dict(schema=1,cases=count,predicate_and_step_checks=states,multiplication_dag_nodes=nodes,corpus=corpus,
                scope='Local exact generator, certificate, predicate and induction controls. No native SMT run implied.')


def limit_memory():
    import resource
    resource.setrlimit(resource.RLIMIT_AS,(1536*1024**2,1536*1024**2))


def run_solver(binary, text, timeout_ms):
    start=time.perf_counter_ns()
    cmd=[str(binary),'--lang=smt2',f'--tlimit-per={timeout_ms}']
    try:
        p=subprocess.run(cmd,input=text,text=True,capture_output=True,timeout=timeout_ms/1000+3,
                         preexec_fn=limit_memory if os.name=='posix' else None)
        words=p.stdout.splitlines()
        answer=next((s for s in words if s in ('sat','unsat','unknown')),None)
        if p.returncode!=0:answer='error'
        return dict(status=answer or 'no_verdict',returncode=p.returncode,
                    elapsed_ns=time.perf_counter_ns()-start,stdout=p.stdout,stderr=p.stderr)
    except subprocess.TimeoutExpired as exc:
        return dict(status='external_timeout',elapsed_ns=time.perf_counter_ns()-start)


def native_run(binary, destination, timeout_ms=2000):
    destination.mkdir(parents=True,exist_ok=False)
    metadata={}
    for option in ('--version','--show-config'):
        v=subprocess.run([str(binary),option],capture_output=True,text=True,timeout=10)
        metadata[option]=dict(returncode=v.returncode,stdout=v.stdout,stderr=v.stderr)
    metadata['binary_sha256']=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
    rows=[]
    for c in cases():
        row=dict(name=c['name'],expected=c['expected'],routes={})
        for name,flag in (('raw',False),('decomposed',True)):
            text,obligations=formula(c,flag)
            (destination/f'{c["name"]}_{name}.smt2').write_text(text)
            result=run_solver(binary,text,timeout_ms)
            result['obligations']=obligations;result['input_sha256']=hashlib.sha256(text.encode()).hexdigest()
            if result['status'] in ('sat','unsat') and result['status']!=c['expected']:
                raise AssertionError('Native verdict contradicts proved control: '+c['name'])
            row['routes'][name]=result
        rows.append(row)
        print(json.dumps(row,sort_keys=True),flush=True)
    result=dict(schema=1,python=platform.python_version(),platform=platform.platform(),solver=metadata,
                timeout_ms=timeout_ms,memory_limit_mb=1536,cases=rows,
                protocol='One cold solver process per route/case; includes startup, no tuning or excluded failures. Fixed algebraic controls, not application benchmarks.',
                assurance='Solver verdicts only. No CPC/Pacheck/Lean proof replay or absence-of-trust-steps certification.')
    (destination/'native_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('NATIVE_REPORT '+json.dumps(result,sort_keys=True),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--solver',type=Path);parser.add_argument('--timeout-ms',type=int,default=2000)
    args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite evidence.')
    if args.solver:native_run(args.solver,args.output,args.timeout_ms)
    else:
        report=local_check();args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k!='corpus'},indent=2))
