"""Independent small trajectories, module spans, p-groups and forged proofs.

Only the test oracle enumerates state or endomorphism sets. The large controls
have explicitly stated closed forms and are not advantage benchmarks.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from collections import Counter
from copy import deepcopy
from itertools import product
from math import gcd
import argparse,hashlib,json,random,subprocess,tempfile
from alc.schema import Invalid,ResourceLimit
from research.prime_power_compilation_v1 import module as mod
from research.prime_power_compilation_v1.checker import compile_source,residue_source
from research.prime_power_compilation_v1.producer import produce


def require(ok,message):
    if not ok:raise AssertionError(message)


def source(p,e,A,c,a):
    return dict(schema='alc.prime-power-source.v1',modulus=p**e,prime=p,exponent=e,
                matrix=[list(r) for r in A],offset=list(c),initial=list(a))


def trajectory(s):
    N=s['prime']**s['exponent'];x=tuple(s['initial']);out=[]
    while x not in out:
        out.append(x)
        x=tuple((sum(u*v for u,v in zip(row,x))+c)%N for row,c in zip(s['matrix'],s['offset']))
    require(x==tuple(s['initial']),'Expected invertible test recurrence.')
    return out


def run():
    counts=Counter();modes=Counter();outcomes=hashlib.sha256();fixtures=[]
    def one(s,all_targets=True):
        result=produce(s)
        require(result['status']=='candidate','Small source exhausted its effort budget.')
        certificate=result['certificate'];compiled=compile_source(s,certificate)
        counts['compiled_sources']+=1
        require(result['metrics']['field_compilations']==1,'More than one field source compiled.')
        if len(set(compiled.module.moduli))>1:counts['mixed_order_modules']+=1
        if all_targets:
            path=set(trajectory(s))
            require(compiled.period==len(path),'Incorrect least point period.')
            N=s['prime']**s['exponent'];n=len(s['initial'])
            for y in product(range(N),repeat=n):
                answer=compiled.query(list(y));member=y in path
                require((answer['status']=='reachable')==member,'False modular target classification.')
                require(answer['first_hit_computed'] is False,'Unexpected timing claim.')
                counts['target_queries']+=1
                counts['reachable_queries' if member else 'unreachable_queries']+=1
                modes[answer['p_digit_mode'] or 'early_rejection']+=1
                outcomes.update(json.dumps([s,y,answer],sort_keys=True).encode())
        return compiled,certificate,result['metrics']
    # All invertible scalar affine SOURCES, then every possible target.
    for p,e in ((2,1),(2,2),(2,3),(3,1),(3,2)):
        N=p**e
        for A in range(N):
            if gcd(A,N)!=1:continue
            for c,a in product(range(N),repeat=2):
                one(source(p,e,[[A]],[c],[a]));counts['scalar_sources']+=1
    # Every invertible 2x2 mod4 matrix, two translations, three contrasting initials.
    for vals in product(range(4),repeat=4):
        if (vals[0]*vals[3]-vals[1]*vals[2])%2==0:continue
        for c in ((0,0),(1,2)):
            for a in ((0,0),(1,0),(2,0)):
                one(source(2,2,[vals[:2],vals[2:]],c,a));counts['matrix_mod4_sources']+=1
    rng=random.Random(2026092707)
    for p,e in ((2,3),(3,2),(5,2)):
        for _ in range(12):
            N=p**e
            while True:
                A=[[rng.randrange(N) for _ in range(2)] for _ in range(2)]
                if gcd(A[0][0]*A[1][1]-A[0][1]*A[1][0],N)==1:break
            s=source(p,e,A,[rng.randrange(N) for _ in range(2)],[rng.randrange(N) for _ in range(2)])
            one(s);counts['seeded_matrix_sources']+=1
    # Independent subgroup enumeration validates the module coordinate conversion.
    for vals in product(range(4),repeat=4):
        G=(vals[:2],vals[2:]);U,V,Ui,ss=mod.diagonalize(G,2,2)
        original={((G[0][0]*x+G[0][1]*y)%4,(G[1][0]*x+G[1][1]*y)%4) for x,y in product(range(4),repeat=2)}
        reconstructed=set()
        for coords in product(*(range(2**(2-s)) for s in ss)):
            diagonal=tuple((2**s)*z for s,z in zip(ss,coords))+(0,)*(2-len(ss))
            reconstructed.add(tuple(sum(Ui[i][j]*diagonal[j] for j in range(2))%4 for i in range(2)))
        require(original==reconstructed,'Mixed module does not equal generated subgroup.')
        counts['independent_module_spans']+=1
    # Cyclic p-subgroups of endomorphisms on genuinely mixed-order modules.
    # The independent oracle operates as permutations/functions on explicit tuples.
    for p,mods in ((2,(2,4)),(2,(4,4)),(3,(3,9))):
        k=len(mods);I=mod.eye(k)
        choices=[tuple(v for v in range(mods[i]) if v*mods[j]%mods[i]==0) for i in range(k) for j in range(k)]
        matrices=[tuple(tuple(flat[i*k+j] for j in range(k)) for i in range(k)) for flat in product(*choices)]
        domain=list(product(*(range(q) for q in mods)))
        def mapping(A):return tuple(tuple(sum(A[i][j]*x[j] for j in range(k))%mods[i] for i in range(k)) for x in domain)
        ident=tuple(domain)
        for u in matrices:
            mapping_u=mapping(u)
            if len(set(mapping_u))!=len(domain):continue
            orbit=[];current=I
            while current not in orbit:
                orbit.append(current);current=mod.product(current,u,mods)
            r=len(orbit);left=r;a=0
            while left%p==0:left//=p;a+=1
            if left!=1:continue
            # Compare to a separate direct FUNCTION iteration, not matrix product alone.
            composed=ident
            actual=[];lookup=dict(zip(domain,mapping_u))
            while composed not in actual:
                actual.append(composed);composed=tuple(lookup[x] for x in composed)
            require(len(actual)==r,'Matrix and function orders differ.')
            for B in matrices:
                expected=mapping(B) in actual
                z,mode,steps=mod.p_log(u,B,mods,p,a)
                require((z is not None)==expected,'p-primary member test failed.')
                if z is not None:require(actual[z]==mapping(B),'Wrong p-primary exponent.')
                counts['independent_p_group_queries']+=1
    named=[('nonunit_point',source(5,2,[[2]],[0],[5])),
           ('mixed_word_subgroup',source(2,5,[[5]],[0],[1])),
           ('two_coordinate_nilpotent',source(2,3,[[1,1],[0,1]],[0,0],[0,1]))]
    for name,s in named:
        compiled,certificate,metrics=one(s)
        fixtures.append(dict(name=name,source=s,certificate=certificate,period=compiled.period,
                             module_exponents=[compiled.e-t for t in compiled.module.valuations],metrics=metrics,
                             certificate_bytes=len(json.dumps(certificate,sort_keys=True,separators=(',',':')).encode())))
    # p^e membership without e nested finite-field certificates; easy closed forms.
    large=[('word64_affine',source(2,64,[[5]],[1],[0])),
           ('word64_subgroup',source(2,64,[[5]],[0],[1])),
           ('large_characteristic',source(257,2,[[1]],[1],[0]))]
    for name,s in large:
        compiled,certificate,metrics=one(s,False);N=s['prime']**s['exponent']
        wanted=N//4 if name=='word64_subgroup' else N
        require(compiled.period==wanted,'Closed-form point-period disagreement.')
        targets=[0,1,2,3,4,N-1]+[rng.randrange(N) for _ in range(40)]
        for y in targets:
            expected=(y%4==1) if name=='word64_subgroup' else True
            require((compiled.query([y])['status']=='reachable')==expected,'Closed-form membership differs.')
            counts['large_closed_form_queries']+=1
        fixtures.append(dict(name=name,source=s,certificate=certificate,period=compiled.period,
                             module_exponents=[compiled.e-t for t in compiled.module.valuations],metrics=metrics,
                             certificate_bytes=len(json.dumps(certificate,sort_keys=True,separators=(',',':')).encode()),
                             scope='Known scalar structure, not a hard benchmark or native speed comparison.'))
    # Nonunit point really cannot be modeled by ordinary ambient reduction.
    nonunit=fixtures[0];require(nonunit['period']==4,'Expected nonunit period4.')
    counts['ambient_reduction_counterexample']=1
    s=fixtures[1]['source'];cert=fixtures[1]['certificate'];bads=[]
    for field,value in [('schema','wrong'),('source_sha256','0'*64),('prime_proofs',[]),
                        ('inverse_matrix',[[1]]),('residue_certificate',{})]:
        bad=deepcopy(cert);bad[field]=value;bads.append((s,bad))
    bad=deepcopy(cert);bad['residue_certificate']['source_sha256']='0'*64;bads.append((s,bad))
    bad=deepcopy(cert);bad['residue_certificate']['components']=[];bads.append((s,bad))
    changed=deepcopy(s);changed['initial']=[2];bads.append((changed,cert))
    changed=deepcopy(s);changed['exponent']=4;bads.append((changed,cert))
    changed=deepcopy(s);changed['prime']=4;bads.append((changed,cert))
    changed=deepcopy(s);changed['exponent']=True;bads.append((changed,cert))
    changed=deepcopy(s);changed['target']=[1];bads.append((changed,cert))
    changed=deepcopy(s);changed['modulus']*=2;bads.append((changed,cert))
    for sp,bad in bads:
        try:compile_source(sp,bad)
        except (Invalid,ResourceLimit):counts['malformed_compilations_rejected']+=1
        else:raise AssertionError('Invalid compilation accepted.')
    compiled=compile_source(s,cert)
    for target in ([True],[-1],[32],[],[1,2]):
        try:compiled.query(target)
        except Invalid:counts['malformed_queries_rejected']+=1
        else:raise AssertionError('Invalid target accepted.')
    require(produce(s,max_work=0)['status']=='unknown','Exhausted search became a proof.')
    counts['unknown_control']=1
    # Fresh query process has neither producer modules nor query-time normalization.
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'fixtures.json';f.write_text(json.dumps(fixtures))
        code='''import sys,json
from research.prime_power_compilation_v1.checker import compile_source
from research.prime_power_compilation_v1 import module
from research.complete_orbits_v1 import algebra
fs=json.load(open(sys.argv[1]));cs=[compile_source(f['source'],f['certificate']) for f in fs]
def forbidden(*a,**kw):raise RuntimeError('Compilation primitive used at query stage')
module.build_module=forbidden;module.diagonalize=forbidden
algebra.solve_columns=forbidden;algebra.irreducible=forbidden
for f,c in zip(fs,cs):
    if c.query(f['source']['initial'])['status']!='reachable':raise RuntimeError('Initial point missing')
if any(k.endswith('.producer') or k.endswith('.producers') for k in sys.modules):raise RuntimeError('Producer imported')
'''
        result=subprocess.run([sys.executable,'-c',code,str(f)],cwd=ROOT,capture_output=True,text=True)
        require(result.returncode==0,'Query dependency control failed: '+result.stderr)
    counts['query_only_dependency_control']=1
    return {'schema':1,'counts':dict(sorted(counts.items())),'query_modes':dict(sorted(modes.items())),
            'outcomes_sha256':outcomes.hexdigest(),'fixtures':fixtures,
            'scope':'Exact prime-power source compilation. Standard algebraic components; not novelty clearance, formal implementation proof, or runtime advantage. No first-hit claim or arbitrary composite-modulus compilation.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite evidence.')
    result=run()
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'},indent=2,sort_keys=True))
