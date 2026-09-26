"""Finite validation of query-scope reductions, not empirical complexity evidence.

Tests deliberately use easy sources. Satisfiability, CRT assignments, binary
orbits, and observation fibers are checked through separate explicit routes.
No new certificate format or general partial-target solver is introduced.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from research.query_scope_v1.controls import (
    ClockSource, closed_observation, crt_coprime, formula_holds, guard_for,
    guard_holds, require)
from research.compiled_orbits_v1.producer import produce
from research.compiled_orbits_v1.checker import compile_orbit


def source(p, A, c, a):
    return {'schema': 'alc.orbit-source.v1', 'field': {'kind':'prime', 'modulus':p},
            'matrix':[list(r) for r in A], 'offset':list(c), 'initial':list(a)}


def plain_orbit(s):
    """Independent affine stepper, used only on small finite controls."""
    p=s['field']['modulus']; A=s['matrix']; c=s['offset']
    a=tuple(s['initial']); x=a; states=[]; seen=set()
    while x not in seen:
        states.append(x); seen.add(x)
        x=tuple((sum(A[i][j]*x[j] for j in range(len(x)))+c[i])%p for i in range(len(x)))
    require(x == a, 'Expected invertible test dynamics.')
    return states


def run():
    rng=random.Random(2026092705)
    counts=Counter(); checksum=hashlib.sha256(); fixtures=[]
    def record(value):
        checksum.update(json.dumps(value, sort_keys=True, separators=(',',':')).encode())
        checksum.update(b'\n')
    clocks={n:ClockSource.build(n) for n in range(1,6)}
    time_states={}
    for n,s in clocks.items():
        # Full trajectory controls: at(t) uses modular indexing, while step is
        # a conjugated permutation of the individual vector coordinates.
        current=s.at(0); rows=[]
        for t in range(s.period):
            require(current == s.at(t), 'Independent clock stepping/indexing differ.')
            require(s.point_member(current), 'A reached state fails ordinary membership.')
            rows.append(current); current=s.step(current)
            counts['clock_steps_checked']+=1
        require(current==s.at(0) and len(set(rows))==s.period, 'Clock least period differs.')
        time_states[n]=rows
        for _ in range(40):
            x=rng.getrandbits(s.dimension); y=rng.getrandbits(s.dimension)
            require(s.step(s.step(x),reverse=True)==x, 'Explicit inverse fails.')
            require(s.step(x^y)==s.step(x)^s.step(y), 'Clock update is not linear.')
            counts['arbitrary_state_linearity_inverse_controls']+=1
        # Almost-correct one-hot inputs must fail if just one multivariable
        # block loses phase consistency with the singleton clocks.
        for t in range(min(s.period,40)):
            raw=s.conjugate(s.at(t))
            if n>=2:
                b=next(b for b in s.blocks if len(b.variables)==2)
                altered=raw ^ (1 << (b.offset+t%b.period)) ^ (1 << (b.offset+(t+1)%b.period))
                require(not s.point_member(s.conjugate(altered)), 'Mismatched block phase accepted.')
                counts['inconsistent_one_hot_states_rejected']+=1
            require(not s.point_member(s.at(t)^(1 << s.dummy)), 'Fixed-zero coordinate violated.')
            counts['dummy_mutations_rejected']+=1
        record(s.summary())

    def check_formula(n, clauses):
        s=clocks[n]; guard=guard_for(s,clauses)
        assignments=list(product((0,1),repeat=n))
        expected={crt_coprime(s.primes,a) for a in assignments if formula_holds(a,clauses)}
        actual={t for t,x in enumerate(time_states[n]) if guard_holds(x,guard)}
        require(actual==expected,'Partial-coordinate reduction differs from Boolean satisfaction.')
        require(len(actual)==sum(formula_holds(a,clauses) for a in assignments),
                'The count correspondence is not parsimonious.')
        counts['formula_instances']+=1
        counts['formula_time_guard_checks']+=s.period
        counts['boolean_assignments_checked']+=len(assignments)
        counts['satisfiable_formula_instances' if actual else 'unsatisfiable_formula_instances']+=1
        record([n,clauses,guard,sorted(actual)])
        return guard,sorted(actual)

    # Exhaust all subsets of the indicated distinct clause families.
    for n,clauses in ((1,[(1,),(-1,)]),
                       (2,[(1,),(-1,),(2,),(-2,)]+[(a,b) for a in (1,-1) for b in (2,-2)]),
                       (3,[tuple((i+1)*sign for i,sign in enumerate(signs))
                           for signs in product((-1,1),repeat=3)])):
        for mask in range(1 << len(clauses)):
            check_formula(n,[c for i,c in enumerate(clauses) if mask>>i&1])
        counts['exhaustive_clause_subset_families']+=1
    for n,how_many in ((3,160),(4,60),(5,12)):
        all_clauses=[]
        for size in range(1,4):
            for variables in combinations(range(1,n+1),size):
                all_clauses += [tuple(v*s for v,s in zip(variables,signs))
                                for signs in product((-1,1),repeat=size)]
        for _ in range(how_many):
            clauses=[rng.choice(all_clauses) for _ in range(rng.randrange(0,14))]
            check_formula(n,clauses)
    specials=[[],[()],[(1,1,1)],[(1,-1,2)],[(1,),(-1,)],
              [(1,2,-3),(-1,2,3),(1,-2,3),(-1,-2,-3)],
              [tuple((i+1)*sign for i,sign in enumerate(signs))
               for signs in product((-1,1),repeat=3)]]
    for clauses in specials:
        guard,times=check_formula(3,clauses)
        fixtures.append({'name':'partial_coordinate_control','source_variables':3,
                         'clauses':clauses,'guard':guard,'solution_times_in_one_period':times,
                         'matching_orbit_states':len(times)})

    # Pair the same explicit easy source with the existing general compiler.
    # n=2 has dimension24, within the existing primary dimension limit32.
    clock=clocks[2]; dense=clock.matrix_source(); candidate=produce(dense)
    require(candidate['status']=='candidate','Existing compiler could not construct small clock proof.')
    compiled=compile_orbit(dense,candidate['certificate'])
    require(compiled.point_period==clock.period,'Compiled clock period differs.')
    packed=list(time_states[2])+[rng.getrandbits(clock.dimension) for _ in range(50)]
    packed+=[x^(1 << clock.dummy) for x in time_states[2]]
    for x in packed:
        y=[(x >> i)&1 for i in range(clock.dimension)]
        require((compiled.query(y)['status']=='reachable')==clock.point_member(x),
                'General compiler and source-aware membership disagree.')
        counts['existing_compiler_clock_queries']+=1
    fixtures.append({'name':'small_existing_compiler_pair', 'source':clock.summary(),
                     'certificate':candidate['certificate'],
                     'scope':'Dimension24, period15: validation of the interface, not a hard workload.'})

    # The exact DDH relation on small prime-order subgroups. These finite tests
    # verify the reduction, not any hardness assumption for these tiny groups.
    for p,q,g in ((23,11,2),(47,23,2)):
        powers=[pow(g,t,p) for t in range(q)]
        require(pow(g,q,p)==1 and len(set(powers))==q,'Incorrect subgroup fixture.')
        for a in range(q):
            s=source(p,[[g,0],[0,pow(g,a,p)]],[0,0],[1,1])
            candidate=produce(s)
            require(candidate['status']=='candidate','DDH toy compilation failed.')
            ci=compile_orbit(s,candidate['certificate'])
            actual=set(plain_orbit(s))
            counts['common_exponent_sources']+=1
            for b,z in product(range(q),repeat=2):
                target=[powers[b],powers[z]]
                expected=(z-a*b)%q==0
                answer=ci.query(target)
                require((answer['status']=='reachable')==expected==(tuple(target) in actual),
                        'Common-exponent/DDH equivalence failed.')
                require(answer['first_hit_computed'] is False,'Membership unexpectedly claims an index.')
                counts['common_exponent_target_queries']+=1
                record([p,q,a,b,z,expected])
    scalar=source(23,[[2]],[0],[1]); c=produce(scalar)['certificate']; ci=compile_orbit(scalar,c)
    for t,y in enumerate(plain_orbit(scalar)):
        ans=ci.query(list(y))
        require(ans['status']=='reachable' and not ans['first_hit_computed'],
                'Scalar membership/time distinction failed.')
        require(pow(2,t,23)==y[0], 'Independent scalar indexing control failed.')
        counts['membership_not_index_controls']+=1

    # A tractable class: linear observations with autonomous quotient dynamics.
    # Eligibility independently checked by exhaustive fibers, not the solver.
    quotient_cache={}; nonclosed=None
    for p in (2,3):
        for flat in product(range(p),repeat=4):
            if (flat[0]*flat[3]-flat[1]*flat[2])%p==0:continue
            A=[list(flat[:2]),list(flat[2:])]
            for row in product(range(p),repeat=2):
                if not any(row):continue
                L=[list(row)]; B=closed_observation(A,L,p)
                states=list(product(range(p),repeat=2))
                image=lambda x:sum(v*w for v,w in zip(row,x))%p
                step_linear=lambda x:tuple(sum(A[i][j]*x[j] for j in range(2))%p for i in range(2))
                eligible=all(image(step_linear(x))==0 for x in states if image(x)==0)
                require((B is not None)==eligible,'Quotient eligibility/kernel invariance disagreement.')
                counts['observation_matrix_pairs']+=1
                if B is None:
                    witness=next(x for x in states if image(x)==0 and image(step_linear(x))!=0)
                    require(image(witness)==image((0,0)) and image(step_linear(witness))!=image(step_linear((0,0))),
                            'Nonclosed observation lacks different-successor witness.')
                    if nonclosed is None:
                        nonclosed={'prime':p,'matrix':A,'observation':L,'same_observation_states':[[0,0],list(witness)],
                                   'successor_observations':[0,image(step_linear(witness))]}
                    counts['nonclosed_observation_counterexamples']+=1
                    continue
                counts['closed_observation_pairs']+=1
                require(B[0][0]%p!=0,'An invertible source induced a singular surjective quotient.')
                for shift in ([0,0],[1,1]):
                    d=image(shift)
                    for initial in states:
                        original=source(p,A,shift,initial); projected={image(x) for x in plain_orbit(original)}
                        quotient=source(p,B,[d],[image(initial)])
                        key=json.dumps(quotient,sort_keys=True)
                        if key not in quotient_cache:
                            qcandidate=produce(quotient)
                            require(qcandidate['status']=='candidate','Quotient source compilation failed.')
                            quotient_cache[key]=compile_orbit(quotient,qcandidate['certificate'])
                        qc=quotient_cache[key]
                        for target in range(p):
                            expected=target in projected
                            require((qc.query([target])['status']=='reachable')==expected,
                                    'Closed observation query differs from original projected orbit.')
                            counts['closed_observation_queries']+=1
                            record([p,A,L,shift,initial,target,expected])
    counts['distinct_quotient_compilations']=len(quotient_cache)
    fixtures.append({'name':'nonautonomous_observation','data':nonclosed,
                     'meaning':'Equal current observations can have unequal next observations; no B with LA=BL.'})
    # Basic malformed reduction/observation controls. None is a no-hit result.
    bad_clauses=[[(0,)],[(4,)],[(True,)],[(1,2,3,1)]]
    for clauses in bad_clauses:
        try:guard_for(clocks[3],clauses)
        except ValueError:counts['malformed_clause_controls']+=1
        else:raise AssertionError('Invalid clause accepted.')
    for L in ([[0,0]],[[1,0],[1,0]],[[1]]):
        try:closed_observation([[1,0],[0,1]],L,2)
        except ValueError:counts['malformed_observation_controls']+=1
        else:raise AssertionError('Invalid observation shape/rank accepted.')
    return {'schema':1,'counts':dict(sorted(counts.items())),
            'source_families':[clocks[n].summary() for n in clocks],
            'fixtures':fixtures,'outcomes_sha256':checksum.hexdigest(),
            'scope':'Exact reductions and query-boundary controls. Small inputs do not test asymptotic hardness or novelty. No new production schema, general guard solver, native solver speedup, or formal code proof.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite stored evidence.')
    report=run()
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'counts':report['counts'],'outcomes_sha256':report['outcomes_sha256']},indent=2,sort_keys=True))
