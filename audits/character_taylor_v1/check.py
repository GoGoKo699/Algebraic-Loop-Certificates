"""Exact source-certificate comparison and independent Taylor/trajectory controls.

The original producer supplies the same untrusted evidence to both compilers.
Both compilers recheck it. The baseline does not invoke the original compiler,
its coordinate solver, or its unipotent decoder. Basic polynomial arithmetic
and the production parser/primality checker remain shared and are not described
as independently verified here. No runtime superiority claim is made.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from collections import Counter
from copy import deepcopy
from itertools import product
from math import comb
import argparse,gzip,hashlib,json,random,subprocess,tempfile
from alc.schema import Invalid
from research.compiled_orbits_v1.producer import produce
from research.compiled_orbits_v1.checker import compile_orbit
from research.complete_orbits_v1 import algebra as field
from audits.character_taylor_v1.baseline import compile_baseline, taylor_basis, linear_taylor, lucas_binomial


def require(ok,why):
    if not ok:raise AssertionError(why)


def source(p,A,c,a):
    return dict(schema='alc.orbit-source.v1',field=dict(kind='prime',modulus=p),
                matrix=[list(row) for row in A],offset=list(c),initial=list(a))


def step(s,y):
    return tuple((sum(x*v for x,v in zip(row,y))+c)%s['field']['modulus']
                 for row,c in zip(s['matrix'],s['offset']))


def orbit(s):
    initial=tuple(s['initial']);y=initial;out=[]
    while y not in out:out.append(y);y=step(s,y)
    require(y==initial,'Input is not a permutation source.')
    return out


def base_sources():
    for p in (2,3):
        for vals in product(range(p),repeat=4):
            if (vals[0]*vals[3]-vals[1]*vals[2])%p:
                A=[vals[:2],vals[2:]]
                for a in product(range(p),repeat=2):yield source(p,A,[0,0],a)
    for p in (2,3,5):
        for mul in range(1,p):
            for shift,a in product(range(p),repeat=2):yield source(p,[[mul]],[shift],[a])
    for vals in product(range(2),repeat=4):
        if (vals[0]*vals[3]-vals[1]*vals[2])%2:
            for shift in ((0,1),(1,0),(1,1)):
                for a in product(range(2),repeat=2):yield source(2,[vals[:2],vals[2:]],shift,a)


def companion(mu,p):
    k=len(mu)-1;A=[[0]*k for _ in range(k)]
    for j in range(k-1):A[j+1][j]=1
    for i in range(k):A[i][-1]=-mu[i]%p
    return A


def repeated_source(p,fs):
    mu=(1,)
    for f,e in fs:
        for _ in range(e):mu=field.mul(mu,f,p)
    k=len(mu)-1
    return source(p,companion(mu,p),[0]*k,[1]+[0]*(k-1))


def multiply_series(a,b,f,e,p):
    out=[() for _ in range(e)]
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            if i+j<e:out[i+j]=field.add(out[i+j],field.mmul(x,y,f,p),p)
    return tuple(out)


def run():
    counts=Counter();reasons=Counter();h=hashlib.sha256();fixtures=[]
    def one(s,targets=None,proof=None):
        if proof is None:
            candidate=produce(s)
            require(candidate['status']=='candidate','Small producer exhausted.')
            proof=candidate['certificate']
        old=compile_orbit(s,proof);new=compile_baseline(s,proof)
        truth=set(orbit(s))
        require(old.point_period==new.period==len(truth),'Period mismatch.')
        counts['compiled_sources']+=1
        if any(c[1]>1 for c in new.components):counts['repeated_factor_sources']+=1
        if any(len(c[0])>2 for c in new.components):counts['extension_field_sources']+=1
        if targets is None:
            targets=product(range(s['field']['modulus']),repeat=len(s['initial']))
            counts['full_domain_sources']+=1
        for y in targets:
            a=old.query(list(y));b=new.query(list(y));member=y in truth
            require((a['status']=='reachable')==(b['status']=='reachable')==member,'Target mismatch.')
            require(not a['first_hit_computed'] and not b['first_hit_computed'],'False time result.')
            counts['target_queries']+=1;counts['reachable' if member else 'unreachable']+=1
            reasons[b['reason']]+=1
            h.update(json.dumps([s,y,b],sort_keys=True,separators=(',',':')).encode())
        return proof,new
    for s in base_sources():one(s)
    counts['base_source_count']=counts['compiled_sources']
    for p,fs in [
        (2,[((1,1),9)]),
        (2,[((1,1,1),3)]),
        (2,[((1,1),2),((1,1,1),2)]),
        (3,[((1,0,1),1),((2,1,1),1)]),
        (3,[((2,1),2),((1,1),2)]),
        (3,[((1,0,1),2),((2,1),1)]),
        (3,[((2,1),4)]),
        (5,[((4,1),3)]),
        (5,[((4,1),2),((3,1),2)]),
    ]:
        s=repeated_source(p,fs);proof,new=one(s)
        fixtures.append(dict(name='factor_control_'+str(len(fixtures)),source=s,certificate=proof,
                             period=new.period,certificate_bytes=len(json.dumps(proof,separators=(',',':'),sort_keys=True).encode())))
    saved=json.loads(gzip.decompress((ROOT/'research/compiled_orbits_v1/expected.json.gz').read_bytes()))['fixtures']
    rng=random.Random(2026092708)
    # Saved phase-compatibility counterexample includes three noncoprime components.
    for fixture in saved[:2]:
        s=fixture['source'];domain=s['field']['modulus']**len(s['initial'])
        targets=None if domain<1000 else list(orbit(s))+[tuple(rng.randrange(s['field']['modulus']) for _ in s['initial']) for _ in range(300)]
        one(s,targets,fixture['certificate'])
    # The sparse p-power coefficients alone do not certify a full binomial row.
    s=repeated_source(2,[((1,1),5)]);proof=produce(s)['certificate'];new=compile_baseline(s,proof)
    target=[0,1,1,1,0] # h(X)=X+X^2+X^3 -> h(1+Z)=1+Z^3.
    result=new.query(target)
    require(result['reason']=='taylor_coefficient_obstruction','Sparse digit counterexample missed.')
    require(tuple(target) not in orbit(s),'Counterexample target is reachable.')
    counts['non_digit_coefficient_counterexample']=1
    fixtures.append(dict(name='non_digit_coefficient',source=s,certificate=proof,target=target,
                         result=result,normalized_series='1+Z^3; p-power coefficients at 1,2,4 are zero'))
    # Non-base-field digit: h(alpha+Z)=1+Z, alpha in F4 not in F2.
    # Find the 4-dimensional source point through finite enumeration, only in TEST.
    s=repeated_source(2,[((1,1,1),2)]);proof=produce(s)['certificate'];new=compile_baseline(s,proof)
    witnesses=[]
    for y in product(range(2),repeat=4):
        if new.query(list(y))['reason']=='non_base_field_digit':witnesses.append(list(y))
    require(witnesses,'Non-base-field digit control not exercised.')
    fixtures.append(dict(name='non_base_field_digit',source=s,certificate=proof,target=witnesses[0],
                         result=new.query(witnesses[0])))
    counts['non_base_field_digit_counterexample']=1
    # Independent coefficient formula, multiplication preservation, and Lucas digits.
    for p,f,e in [(2,(1,1),5),(2,(1,1,1),3),(3,(1,0,1),3),(5,(4,1),4)]:
        alpha=field.rem((0,1),f,p);k=(len(f)-1)*e;columns=taylor_basis(k,alpha,f,e,p)
        modulus=(1,)
        for _ in range(e):modulus=field.mul(modulus,f,p)
        for _ in range(80):
            coeff=tuple(rng.randrange(p) for _ in range(k));second=tuple(rng.randrange(p) for _ in range(k))
            actual=linear_taylor(coeff,columns,e,p);formula=[]
            for j in range(e):
                value=()
                for r in range(j,k):value=field.add(value,field.scale(field.power(alpha,r-j,f,p),coeff[r]*comb(r,j),p),p)
                formula.append(value)
            require(actual==tuple(formula),'Taylor coefficient formula disagreement.')
            result=field.rem(field.mul(coeff,second,p),modulus,p)
            require(linear_taylor(result,columns,e,p)==multiply_series(actual,linear_taylor(second,columns,e,p),f,e,p),
                    'Taylor map does not preserve multiplication.')
            counts['taylor_formula_and_product_checks']+=1
    for p in (2,3,5,7):
        for n in range(160):
            for j in range(21):
                wanted=comb(n,j)%p if j<=n else 0
                require(lucas_binomial(n,j,p)==wanted,'Binomial digit mismatch.')
                counts['binomial_controls']+=1
    # Large-characteristic source: supplied polynomial factors are acknowledged;
    # querying uses an independent binomial closed form, never p-state enumeration.
    f=saved[2];s=f['source'];old=compile_orbit(s,f['certificate']);new=compile_baseline(s,f['certificate']);p=s['field']['modulus']
    for _ in range(240):
        if _<80:
            t=rng.randrange(p);C=t*(t-1)*pow(2,-1,p)%p;y=[(1-t+C)%p,(t-2*C)%p,C]
        else:y=[rng.randrange(p) for _ in range(3)]
        t=(y[1]+2*y[2])%p
        wanted=(sum(y)%p==1 and y[2]==t*(t-1)*pow(2,-1,p)%p)
        require((new.query(y)['status']=='reachable')==(old.query(y)['status']=='reachable')==wanted,'Large-characteristic discrepancy.')
        counts['large_characteristic_queries']+=1
    fixtures.append(f)
    # Fresh code path: original compilation, coordinate solver and unipotent
    # recognizer are disabled BEFORE constructing the alternative, not just queries.
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'proofs.json';path.write_text(json.dumps(fixtures))
        code='''import json,sys
from research.complete_orbits_v1 import algebra
from audits.character_taylor_v1.baseline import compile_baseline
def forbidden(*a,**k):raise RuntimeError('Original source compiler/decoder reached')
algebra.solve_columns=forbidden
algebra.unipotent_log=forbidden
for f in json.load(open(sys.argv[1])):
    c=compile_baseline(f['source'],f['certificate'])
    if c.query(f['source']['initial'])['status']!='reachable':raise RuntimeError('initial excluded')
    if 'target' in f and c.query(f['target'])['status']!='unreachable':raise RuntimeError('negative accepted')
for m in sys.modules:
    if m.endswith('.producer') or m.endswith('.producers') or m.startswith('research.compiled_orbits_v1') or m.startswith('research.separating_invariants_v1'):
        raise RuntimeError('Forbidden dependency: '+m)
'''
        result=subprocess.run([sys.executable,'-c',code,str(path)],cwd=ROOT,capture_output=True,text=True)
        require(result.returncode==0,'Baseline dependency control: '+result.stderr)
    counts['independent_compilation_path_control']=1
    # The SAME malformed evidence is submitted to both compilers.
    f=saved[0];s=f['source'];cert=f['certificate'];bads=[]
    for key,value in [('schema','wrong'),('source_sha256','0'*64),('prime_proofs',[]),
                      ('inverse_matrix',[[1,0],[0,1]]),('components',[]),('comparisons',[])]:
        b=deepcopy(cert);b[key]=value;bads.append(b)
    for key,value in [('order',True),('order',8),('order_factors',[]),('multiplicity',2),('factor',[1,0,1])]:
        b=deepcopy(cert);b['components'][0][key]=value;bads.append(b)
    for key,value in [('alignment',0),('i',True),('left_root',[1]),('right_root',[2]),('algebra_modulus',[1])]:
        b=deepcopy(cert);b['comparisons'][0][key]=value;bads.append(b)
    b=deepcopy(cert);b['exact']=True;bads.append(b)
    b=deepcopy(cert);b['comparisons'].append(deepcopy(b['comparisons'][0]));bads.append(b)
    for bad in bads:
        for compiler in (compile_orbit,compile_baseline):
            try:compiler(s,bad)
            except Invalid:pass
            else:raise AssertionError('Bad evidence accepted.')
        counts['malformed_certificates_rejected_by_both']+=1
    for state in ([True,1],[13,1],[1],[-1,0]):
        for c in (compile_orbit(s,cert),compile_baseline(s,cert)):
            try:c.query(state)
            except Invalid:pass
            else:raise AssertionError('Invalid query accepted.')
        counts['bad_queries_rejected_by_both']+=1
    changed=dict(s,initial=[1,2])
    try:compile_baseline(changed,cert)
    except Invalid:counts['changed_source_rejected']=1
    else:raise AssertionError('Wrong source accepted.')
    # Apparent index-conversion slip in author-hosted MW Algorithm2 step4.9:
    # matching J^(ell0+j*s) gives ell mod P=(ell0+j*s) mod P, not j in general.
    # A direct Jordan-matrix example: p=3, lambda=2, block size4, ell=1.
    J=tuple(tuple(2 if i==j else 1 if j==i+1 else 0 for j in range(4)) for i in range(4))
    ell,ell0,scalar_order,P=1,1,2,9;j=0
    identity=tuple(tuple(int(i==j) for j in range(4)) for i in range(4))
    def mm(A,B):
        return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(4))%3 for j in range(4)) for i in range(4))
    powers=[identity]
    for _ in range(18):powers.append(mm(powers[-1],J))
    require(powers[18]==identity,'Jordan test order incorrect.')
    require(powers[ell0+j*scalar_order]==powers[ell] and j!=ell%P,'Expected search-index discrepancy absent.')
    for exponent in range(18):
        start=exponent%scalar_order
        index=next(j for j in range(P) if powers[start+j*scalar_order]==powers[exponent])
        require((start+index*scalar_order)%P==exponent%P,'Corrected index replay failed.')
        counts['author_copy_index_conversion_controls']+=1
        if index!=exponent%P:counts['author_copy_literal_index_discrepancies']+=1
    return dict(schema=1,counts=dict(sorted(counts.items())),reasons=dict(sorted(reasons.items())),
                outcomes_sha256=h.hexdigest(),fixtures=fixtures,
                author_copy_index_control=dict(characteristic=3,eigenvalue=2,block_size=4,exponent=1,
                    scalar_order=2,primary_period=9,search_start=1,search_index=0,
                    literal_index_residue=0,correct_exponent_residue=1),
                scope='Same untrusted certificate and full prime-field membership contract; alternative rechecks the source without old compiler/coordinate/unipotent routines. Parser, primality and elementary polynomial arithmetic are shared. Classical character/Jordan-Taylor construction; no first-hit recovery, timing advantage or priority claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite evidence.')
    result=run()
    with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('fixtures',)},indent=2,sort_keys=True))
