"""Compare the membership reduction against standard CRT primary projectors.

Exact results, no timing claim. Independent small trajectories establish truth;
shared source compiler and p-group kernel mean this is NOT independent full
compiler validation. Abstract group tests also check the premises of the lemma.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from collections import Counter
from itertools import product, permutations
from math import gcd, lcm
import argparse, gzip, hashlib, json, random, subprocess, tempfile
from alc.schema import Invalid
from research.prime_power_compilation_v1.producer import produce
from research.prime_power_compilation_v1.checker import compile_source
from research.prime_power_compilation_v1 import module as arithmetic
from audits.primary_splitting_v1.baseline import ProjectorBaseline, projectors


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def source(p,e,A,c,a):
    return dict(schema='alc.prime-power-source.v1',modulus=p**e,prime=p,exponent=e,
                matrix=[list(r) for r in A],offset=list(c),initial=list(a))


def direct_orbit(s):
    N=s['modulus']; x=tuple(s['initial']); first=x; out=[]
    while x not in out:
        out.append(x)
        x=tuple((sum(u*v for u,v in zip(row,x))+c)%N for row,c in zip(s['matrix'],s['offset']))
    require(x==first,'Test source must be invertible.')
    return out


def families():
    for p,e in ((2,1),(2,2),(2,3),(3,1),(3,2)):
        N=p**e
        for a in range(N):
            if gcd(a,N)!=1: continue
            for c,x in product(range(N),repeat=2):
                yield source(p,e,[[a]],[c],[x])
    for flat in product(range(4),repeat=4):
        if (flat[0]*flat[3]-flat[1]*flat[2])%2==0: continue
        for c in ((0,0),(1,2)):
            for a in ((0,0),(1,0),(2,0)):
                yield source(2,2,[flat[:2],flat[2:]],c,a)
    rng=random.Random(2026092717)
    for p,e in ((2,3),(3,2),(5,2)):
        N=p**e
        for _ in range(12):
            while True:
                A=[[rng.randrange(N) for _ in range(2)] for _ in range(2)]
                if gcd(A[0][0]*A[1][1]-A[0][1]*A[1][0],N)==1: break
            yield source(p,e,A,[rng.randrange(N) for _ in range(2)],
                         [rng.randrange(N) for _ in range(2)])


def additive_order(g, moduli):
    return lcm(*(n//gcd(a,n) for a,n in zip(g,moduli)))


def group_controls(counts):
    # G=(Z/mZ)x(Z/p^aZ)x(Z/p^bZ); quotient is its first coordinate.
    # Every source/target pair is checked, not merely predicted members.
    for p in (2,3):
        for m in range(1,7):
            if m%p==0: continue
            for a,b in ((1,1),(2,1)):
                mods=(m,p**a,p**b)
                elements=list(product(*(range(n) for n in mods)))
                for g in elements:
                    r=additive_order(g,mods)
                    subgroup={tuple(t*x%n for x,n in zip(g,mods)) for t in range(r)}
                    qorder=m//gcd(g[0],m)
                    powered_generator=tuple(qorder*x%n for x,n in zip(g,mods))
                    rp=additive_order(powered_generator,mods)
                    psub={tuple(t*x%n for x,n in zip(powered_generator,mods)) for t in range(rp)}
                    quotient_members={t*g[0]%m for t in range(qorder)}
                    for h in elements:
                        reduced=h[0] in quotient_members
                        powered=tuple(qorder*x%n for x,n in zip(h,mods))
                        inferred=reduced and powered in psub
                        require(inferred==(h in subgroup),'Abelian kernel lemma failed.')
                        counts['abelian_source_target_pairs']+=1
                    counts['abelian_generators']+=1
    # Noncommutation is essential: S3 -> C2 via sign has the 3-group kernel A3.
    identity=(0,1,2);g=(1,0,2);h=(0,2,1)
    mul=lambda x,y:tuple(x[y[i]] for i in range(3))
    require(mul(g,g)==identity and mul(h,h)==identity and h not in (identity,g),
            'Incorrect S3 counterexample.')
    require(mul(g,h)!=mul(h,g),'S3 counterexample must be noncommuting.')
    # Both have the same odd image; both squares are identity; h is not in <g>.
    # Kernel p-primary is also essential: (C4 x C2) -> C4, while p=3.
    require((0,1) not in {(j,0) for j in range(4)},'Wrong non-p kernel example.')
    counts['noncommuting_counterexamples']=1
    counts['wrong_characteristic_kernel_counterexamples']=1
    return {'noncommuting':{'group':'S3','p':3,'g':list(g),'h':list(h),'m':2,
                           'passes_naive_conditions':True,'actual_member':False},
            'non_p_kernel':{'group':'C4 x C2','quotient':'C4','p':3,
                            'g':[1,0],'h':[0,1],'m':4,
                            'passes_naive_conditions':True,'actual_member':False}}


def run():
    counts=Counter(); hashout=hashlib.sha256(); examples=[]
    for s in families():
        candidate=produce(s)
        require(candidate['status']=='candidate','Reference construction exhausted.')
        checked=compile_source(s,candidate['certificate'])
        baseline=ProjectorBaseline.prepare(checked)
        truth=set(direct_orbit(s))
        require(baseline.source_period==len(truth)==checked.period,'Period disagreement.')
        counts['sources']+=1
        if len(set(checked.module.moduli))>1: counts['mixed_order_sources']+=1
        for y in product(range(s['modulus']),repeat=len(s['initial'])):
            old=checked.query(list(y))['status']=='reachable'
            new=baseline.query(list(y))
            require(old==new==(y in truth),'Projector and current predicate disagree.')
            counts['queries']+=1
            counts['reachable' if old else 'unreachable']+=1
            hashout.update(json.dumps([s,y,old],sort_keys=True,separators=(',',':')).encode())
    # The source order does not bound p-orders of all targets passing reduction.
    # Abstract C2 x C5 has g=(1,0), h=(1,1). Taking P=1 from ord(g)=2
    # sends both to the identity and falsely accepts h. Correct P=5 separates.
    es,ep=projectors(2,1)
    require(ep==0,'Expected source-only shortcut exponent zero.')
    good_es,good_ep=projectors(2,5)
    require(good_ep%5==1 and good_ep%2==0,'Ambient primary projector failed.')
    counts['source_order_bound_counterexample']=1
    abstract=group_controls(counts)
    abstract['source_order_bound']={'group':'C2 x C5','g':[1,0],'h':[1,1],
                                   'bad_p_bound':1,'correct_p_bound':5,
                                   'bad_primary_exponent':ep,'correct_primary_exponent':good_ep}
    # The same failure occurs in an actual scalar orbit, not only an abstract group.
    sign_source=source(5,2,[[24]],[0],[1])
    sign_candidate=produce(sign_source)
    require(sign_candidate['status']=='candidate','Sign source creation failed.')
    sign_checked=compile_source(sign_source,sign_candidate['certificate'])
    sign_baseline=ProjectorBaseline.prepare(sign_checked)
    coords=sign_checked.module.coordinates((6,1))
    require(coords is not None,'Sign target must lie in the initial cyclic module.')
    require(sign_checked.residue.query([x%5 for x in coords])['status']=='reachable',
            'Sign target should pass the residue orbit check.')
    B=sign_checked.module.polynomial_action(sign_checked.module.coefficients(coords))
    false_primary=arithmetic.power(B,ep,sign_checked.module.moduli)
    require(false_primary==arithmetic.eye(len(sign_checked.module.moduli)),
            'Wrong bound should erase the target p-component.')
    require(not sign_baseline.query([6]) and sign_checked.query([6])['status']=='unreachable',
            'Correct predicates must reject the lifted false target.')
    require(sign_baseline.p_bound==5 and sign_checked.period==2,'Wrong sign-source parameters.')
    counts['concrete_source_order_counterexample']=1
    abstract['concrete_source_order']={'source':sign_source,'target':[6],
         'orbit':[1,24],'passes_residue':True,'bad_projector_accepts':True,
         'checked_methods_accept':False,'target_endomorphism':[list(r) for r in B]}
    # Replay prior source certificates: no new producer hints or certificate data.
    prior=ROOT/'research/prime_power_compilation_v1/expected.json.gz'
    saved=json.loads(gzip.decompress(prior.read_bytes()))
    rng=random.Random(2026092727)
    for item in saved['fixtures']:
        s=item['source'];checked=compile_source(s,item['certificate'])
        baseline=ProjectorBaseline.prepare(checked);N=s['modulus'];n=len(s['initial'])
        large=N**n>10000
        targets=([tuple(s['initial'])]+[tuple(rng.randrange(N) for _ in range(n)) for _ in range(48)])
        truth=None if large else set(direct_orbit(s))
        for y in targets:
            old=checked.query(list(y))['status']=='reachable';new=baseline.query(list(y))
            require(old==new,'Saved large fixture disagreement.')
            if truth is not None: require(new==(y in truth),'Saved direct trajectory disagreement.')
            elif item['name']=='word64_subgroup':require(new==(y[0]%4==1),'Subgroup closed form failed.')
            else:require(new,'Full-cycle closed form failed.')
            counts['saved_fixture_queries']+=1
        examples.append({'name':item['name'],'modulus':N,'dimension':n,
                         'period':checked.period,'p_bound':baseline.p_bound,
                         'prime_to_p_order':checked.semisimple_order,
                         'primary_projection_exponent':baseline.primary_exponent,
                         'field_certificates':1,'additional_certificate_bytes':0})
    for bad in ((True,2),(2,0),(6,4),(0,1)):
        try:projectors(*bad)
        except Invalid:counts['bad_projector_inputs_rejected']+=1
        else:raise AssertionError('Invalid CRT projector input accepted.')
    # Check dependency contract in a fresh process: no producer imported; no
    # normalization or irreducibility called at query time, including the baseline.
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'fixtures.json';f.write_text(json.dumps(saved['fixtures']))
        code='''import sys,json
from research.prime_power_compilation_v1.checker import compile_source
from audits.primary_splitting_v1.baseline import ProjectorBaseline
from research.prime_power_compilation_v1 import module
from research.complete_orbits_v1 import algebra
fixtures=json.load(open(sys.argv[1]));objects=[ProjectorBaseline.prepare(compile_source(x['source'],x['certificate'])) for x in fixtures]
def forbidden(*a,**kw):raise RuntimeError('Compilation/search used at query stage')
module.build_module=forbidden;module.diagonalize=forbidden
algebra.irreducible=forbidden;algebra.solve_columns=forbidden
for f,c in zip(fixtures,objects):
    if not c.query(f['source']['initial']):raise RuntimeError('Initial state missing')
if any(n.endswith('.producer') or n.endswith('.producers') for n in sys.modules):raise RuntimeError('Producer imported')
'''
        out=subprocess.run([sys.executable,'-c',code,str(f)],cwd=ROOT,text=True,capture_output=True)
        require(out.returncode==0,'Baseline dependency check failed: '+out.stderr)
    counts['query_dependency_control']=1
    return {'schema':1,'counts':dict(sorted(counts.items())),
            'outcomes_sha256':hashout.hexdigest(),'examples':examples,'counterexamples':abstract,
            'scope':'Matched reduction-layer comparison only. Same checked module, residue certificate and p-group kernel; not an independent full compiler or a published native baseline. Independent finite trajectories/group tables test the replacement logic. No timing, practical superiority, or novelty claim.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite evidence.')
    result=run()
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(result,indent=2,sort_keys=True))
