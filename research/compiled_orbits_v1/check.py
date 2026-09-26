"""Exact finite tests of source compilation, all-target membership and graph coverage.

Only independent test oracles enumerate small state spaces. This is not an
application benchmark, a novelty claim, or formal verification of Python.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from collections import Counter
from copy import deepcopy
from itertools import product
from math import gcd
import argparse, hashlib, json, random, subprocess, tempfile
from alc.schema import Invalid
from research.compiled_orbits_v1.checker import compile_orbit, coverage_ok
from research.compiled_orbits_v1.producer import produce, hub_edges
from research.complete_orbits_v1 import algebra as alg
from research.complete_orbits_v1.producer import Budget, PrimeBuilder


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def source(p, A, c, a):
    return {'schema': 'alc.orbit-source.v1', 'field': {'kind': 'prime', 'modulus': p},
            'matrix': [list(v) for v in A], 'offset': list(c), 'initial': list(a)}


def step(s, y):
    p = s['field']['modulus']
    return tuple((sum(a*b for a,b in zip(row, y))+c) % p for row,c in zip(s['matrix'], s['offset']))


def orbit(s):
    initial = tuple(s['initial']); y = initial; out = []
    while y not in out:
        out.append(y); y = step(s, y)
    require(y == initial, 'Expected a bijective test source.')
    return out


def families():
    for p in (2,3):
        for a in product(range(p), repeat=4):
            if (a[0]*a[3]-a[1]*a[2]) % p:
                yield p, [a[:2], a[2:]], [0,0]
    for p in (2,3,5):
        for a in range(1,p):
            for c in range(p):
                yield p, [[a]], [c]
    for a in product(range(2), repeat=4):
        if (a[0]*a[3]-a[1]*a[2]) % 2:
            for c in ((0,1),(1,0),(1,1)):
                yield 2, [a[:2],a[2:]], c


def companion(mu,p):
    n = len(mu)-1; A = [[0]*n for _ in range(n)]
    for j in range(n-1): A[j+1][j] = 1
    for i in range(n): A[i][-1] = -mu[i] % p
    return A


def run():
    counts = Counter(); hashes = hashlib.sha256(); fixtures = []
    def one(s, enumerate_domain=True, supplied=None):
        candidate = produce(s, supplied_factors=supplied)
        require(candidate['status'] == 'candidate', 'Unexpected construction budget failure.')
        cert = candidate['certificate']; compiled = compile_orbit(s,cert)
        counts['compiled_sources'] += 1
        counts['offline_base_alignments'] += candidate['metrics']['base_alignment_log_calls']
        require(candidate['metrics']['target_log_calls'] == 0, 'Unexpected target log.')
        if enumerate_domain:
            actual = set(orbit(s))
            require(compiled.point_period == len(actual), 'Source period differs from direct orbit.')
            p = s['field']['modulus']; n = len(s['initial'])
            accepted = set()
            for y in product(range(p),repeat=n):
                answer = compiled.query(list(y))
                member = answer['status'] == 'reachable'
                require(member == (y in actual), 'Source-only exact recognition differs.')
                require(answer['first_hit_computed'] is False, 'Unexpected time claim.')
                if member: accepted.add(y)
                counts['target_queries'] += 1
                counts['reachable_queries' if member else 'unreachable_queries'] += 1
                hashes.update(json.dumps([s,y,answer],sort_keys=True).encode())
            for y in accepted:
                require(step(s,y) in accepted, 'Exact orbit predicate lost closure.')
                counts['induction_checks'] += 1
        return cert, compiled
    for p,A,c in families():
        counts['recurrences'] += 1
        for a in product(range(p),repeat=len(A)):
            one(source(p,A,c,a))
    for p,factors in [
        (2,[((1,1,1),3)]),
        (3,[((1,0,1),1),((2,1,1),1)]),
        (3,[((2,1),2),((1,1),2)]),
        (5,[((4,1),3)])]:
        mu=(1,)
        for f,e in factors:
            for _ in range(e):mu=alg.mul(mu,f,p)
        n=len(mu)-1
        one(source(p,companion(mu,p),[0]*n,[1]+[0]*(n-1)))
        counts['repeated_or_extension_sources'] += 1
    # Familiar incomplete invariant now completed, without an orbit lookup table.
    s=source(13,[[4,0],[0,5]],[0,0],[1,1]);cert,ci=one(s)
    require(ci.query([0,0])['status']=='unreachable','Old overapproximation not eliminated.')
    fixtures.append({'name':'exact_twelve_state_orbit','source':s,'certificate':cert,
        'period':ci.point_period,'origin_status':ci.query([0,0])['status'],
        'certificate_bytes':len(json.dumps(cert,sort_keys=True,separators=(',',':')).encode())})
    # A connected graph is not enough: component orders6,10,15 require a cycle.
    p=31;g=3
    require(len({pow(g,t,p) for t in range(30)})==30,'Wrong primitive generator in test.')
    vals=[pow(g,5,p),pow(g,3,p),pow(g,2,p)]
    s=source(p,[[vals[i] if i==j else 0 for j in range(3)] for i in range(3)], [0]*3,[1]*3)
    cert,ci=one(s,False)
    order_to_index={r['order']:i for i,r in enumerate(cert['components'])}
    six,ten,fifteen=[order_to_index[m] for m in (6,10,15)]
    missing_edge=tuple(sorted((ten,fifteen)))
    bad=deepcopy(cert);bad['comparisons']=[e for e in bad['comparisons'] if (e['i'],e['j'])!=missing_edge]
    try:compile_orbit(s,bad)
    except Invalid:counts['connected_but_incomplete_graph_rejected']+=1
    else:raise AssertionError('Unsafe graph shortcut accepted.')
    target=[1,1,pow(vals[2],3,p)]
    require(ci.query(target)['status']=='unreachable','Cycle constraint negative not excluded.')
    # Direct check: labels (0 mod6, 0 mod10, 3 mod15) pass gcd2 and gcd3,
    # but fail the missing gcd5 condition. This does not require any logarithm.
    fixtures.append({'name':'connected_graph_trap','source':s,'certificate':cert,'target':target,
                     'local_residues':[[0,6],[0,10],[3,15]],'missing_pair_orders':[10,15]})
    actual=set(orbit(s));rng=random.Random(2026092704)
    for y in list(actual)+[tuple(rng.randrange(p) for _ in range(3)) for _ in range(400)]:
        require((ci.query(list(y))['status']=='reachable')==(y in actual),'Three-component recognition differs.')
        counts['connected_graph_source_queries']+=1
    # Exhaust exact graph criterion against all possible residue assignments.
    pb=PrimeBuilder(Budget())
    for orders in product(range(1,7),repeat=3):
        facts=[pb.factor(v) for v in orders]
        possible=[(0,1),(0,2),(1,2)]
        for mask in range(8):
            edges={edge for j,edge in enumerate(possible) if mask>>j&1}
            sufficient=True
            for residues in product(*(range(m) for m in orders)):
                edge_ok=all((residues[i]-residues[j])%gcd(orders[i],orders[j])==0 for i,j in edges)
                global_ok=all((residues[i]-residues[j])%gcd(orders[i],orders[j])==0 for i,j in possible)
                if edge_ok and not global_ok:sufficient=False
                counts['graph_residue_assignments']+=1
            require(coverage_ok(facts,edges)==sufficient,'Coverage criterion not exact.')
            counts['graph_cases']+=1
        require(coverage_ok(facts,set(hub_edges(facts))),'Hub graph insufficient.')
        counts['hub_graphs_checked']+=1
    require(not coverage_ok([[[2,1]],[[2,2]],[[2,2]]],{(0,1),(0,2)}),'High-power connectivity missed.')
    # Large characteristic repeated-root algebra without p-sized trajectory scan.
    p=65537;f=(p-1,1);mu=(1,)
    for _ in range(3):mu=alg.mul(mu,f,p)
    s=source(p,companion(mu,p),[0,0,0],[1,0,0])
    cert,ci=one(s,False,supplied=[(f,3)])
    require(ci.point_period==p,'Wrong unipotent order.')
    tested=[]
    for _ in range(80):
        t=rng.randrange(p);C=t*(t-1)*pow(2,-1,p)%p
        tested.append([(1-t+C)%p,(t-2*C)%p,C])
    tested += [[rng.randrange(p) for _ in range(3)] for _ in range(160)]
    for y in tested:
        t=(y[1]+2*y[2])%p
        criterion=(sum(y)%p==1 and y[2]==t*(t-1)*pow(2,-1,p)%p)
        require((ci.query(y)['status']=='reachable')==criterion,'Closed-form unipotent control differs.')
        counts['large_characteristic_queries']+=1
    fixtures.append({'name':'large_characteristic_control','source':s,'certificate':cert,
                     'period':ci.point_period,'oracle':'binomial coefficient identity, not enumerated orbit',
                     'supplied_polynomial_factors':[[list(f),3]]})
    # Construction falsifications distinguish sound induction from exactness.
    s=fixtures[0]['source'];cert=fixtures[0]['certificate'];bads=[]
    for key,val in [('schema','wrong'),('source_sha256','0'*64),('prime_proofs',[]),
                    ('inverse_matrix',[[1,0],[0,1]]),('comparisons',[]),('components',[])]:
        b=deepcopy(cert);b[key]=val;bads.append(b)
    for key,val in [('order',8),('order_factors',[]),('multiplicity',2),('factor',[1,0,1]),('order',True)]:
        b=deepcopy(cert);b['components'][0][key]=val;bads.append(b)
    for key,val in [('i',True),('alignment',0),('left_root',[1]),('right_root',[2]),('algebra_modulus',[1])]:
        b=deepcopy(cert);b['comparisons'][0][key]=val;bads.append(b)
    b=deepcopy(cert);b['comparisons'].append(deepcopy(b['comparisons'][0]));bads.append(b)
    b=deepcopy(cert);b['exact']=True;bads.append(b)
    for bad in bads:
        try:compile_orbit(s,bad)
        except Invalid:counts['malformed_or_incomplete_certificates_rejected']+=1
        else:raise AssertionError('Counterfeit exact compilation accepted.')
    for y in ([True,1],[13,1],[1],[-1,0]):
        try:compile_orbit(s,cert).query(y)
        except Invalid:counts['malformed_queries_rejected']+=1
        else:raise AssertionError('Malformed query accepted.')
    changed=deepcopy(s);changed['initial']=[1,2]
    try:compile_orbit(changed,cert)
    except Invalid:counts['changed_source_rejected']+=1
    else:raise AssertionError('Wrong source accepted.')
    with_target=dict(s,target=[1,1])
    try:produce(with_target)
    except Invalid:counts['target_free_input_enforced']+=1
    else:raise AssertionError('Producer has a target argument.')
    require(produce(s,max_work=0)['status']=='unknown','Budget exhaustion became an exact answer.')
    counts['unknown_control']=1
    # Query stage is still valid with compilation/search primitives disabled.
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'input.json';path.write_text(json.dumps(fixtures))
        code='''import json,sys
from research.compiled_orbits_v1.checker import compile_orbit
from research.complete_orbits_v1 import algebra as alg
fixtures=json.load(open(sys.argv[1]))
compiled=[compile_orbit(f['source'],f['certificate']) for f in fixtures]
def forbidden(*a,**kw):raise RuntimeError('compile/search primitive used at query time')
alg.irreducible=forbidden
alg.solve_columns=forbidden
for f,c in zip(fixtures,compiled):
    if c.query(f['source']['initial'])['status']!='reachable':raise RuntimeError('initial excluded')
if any(k.endswith('.producer') or k.endswith('.producers') for k in sys.modules):raise RuntimeError('producer import')
'''
        out=subprocess.run([sys.executable,'-c',code,str(path)],cwd=ROOT,capture_output=True,text=True)
        require(out.returncode==0,'Forbidden query dependency: '+out.stderr)
    counts['query_only_dependency_control']=1
    return {'schema':1,'counts':dict(sorted(counts.items())),'outcomes_sha256':hashes.hexdigest(),
            'fixtures':fixtures,'scope':'Exact source compilation and graph-completeness audit. Small enumeration and large closed-form controls; no native invariant benchmark, general synthesis speedup, or novelty clearance.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite evidence.')
    result=run()
    with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'},indent=2,sort_keys=True))
