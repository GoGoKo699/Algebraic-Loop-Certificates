"""Cross-check the primary positive-certificate API against an isolated reference.

Distinct module namespaces and independent elementary trajectory enumeration
avoid replacing the primary API or accidentally sharing its arithmetic code.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import importlib
from itertools import product
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def package(name, path):
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module
    return importlib.import_module(name+'.checker'), importlib.import_module(name+'.schema') if name == '_primary_alc' else None


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def families():
    for p in (2, 3):
        for flat in product(range(p), repeat=4):
            a = [list(flat[:2]), list(flat[2:])]
            if (a[0][0]*a[1][1]-a[0][1]*a[1][0]) % p:
                yield p, a, [0, 0]
    for p in (2, 3, 5):
        for scalar in range(1, p):
            for c in range(p):
                yield p, [[scalar]], [c]
    for flat in product(range(2), repeat=4):
        a = [list(flat[:2]), list(flat[2:])]
        if (a[0][0]*a[1][1]-a[0][1]*a[1][0]) % 2:
            for c in ([0, 1], [1, 0], [1, 1]):
                yield 2, a, c


def inverse(a, p):
    # Closed forms are independent of both checkers' matrix arithmetic.
    if len(a) == 1:
        return [[pow(a[0][0], -1, p)]]
    u, v = a[0]; w, z = a[1]
    d = pow((u*z-v*w) % p, -1, p)
    return [[z*d % p, -v*d % p], [-w*d % p, u*d % p]]


def run():
    primary, schema = package('_primary_alc', ROOT/'alc')
    reference, _ = package('_reference_alc', HERE/'reference/alc')
    producer = importlib.import_module('_reference_alc.producers')
    counts = dict(recurrences=0, state_target_cases=0, positive_agreements=0,
                  negative_targets_with_false_hit_rejected_by_both=0,
                  corrupted_inverse_witnesses_rejected_by_primary=0,
                  noncanonical_offsets_rejected_by_both=0,
                  valid_reference_negative_certificates=0)
    result_hash = hashlib.sha256()
    for p, a, c in families():
        counts['recurrences'] += 1
        states = list(product(range(p), repeat=len(a)))
        for initial in states:
            orbit = []; current = initial
            while current not in orbit:
                orbit.append(current)
                current = tuple((sum(a[i][j]*current[j] for j in range(len(a)))+c[i]) % p
                                for i in range(len(a)))
            require(current == initial, 'Noninvertible recurrence in audit source.')
            base = dict(schema='alc-instance-1', modulus=p, matrix=a, translation=c,
                        initial=list(initial), target=list(initial))
            seed = producer.produce(base)['certificate']
            for target in states:
                spec = dict(base, target=list(target))
                rcert = deepcopy(seed)
                rcert['instance_sha256'] = reference.instance_hash(spec)
                truth = orbit.index(target) if target in orbit else None
                rcert['claim']['offset'] = 0 if truth is None else truth
                problem = dict(schema='alc.problem.v1', field=dict(kind='prime', modulus=p),
                               matrix=a, offset=c, initial=list(initial), target=list(target))
                proofs = [dict(p=pr['n'], witness=1 if pr['n']==2 else pr['base'],
                               factors=[] if pr['n']==2 else pr['factors'])
                          for pr in rcert['prime_proofs']]
                pcert = dict(schema='alc.certificate.v1', kind='periodic_hits',
                             problem_sha256=schema.Problem.parse(problem).fingerprint,
                             first=rcert['claim']['offset'], period=rcert['claim']['period'],
                             period_factors=rcert['claim']['factors'],
                             inverse_matrix=inverse(a,p), prime_proofs=proofs)
                if truth is None:
                    for check, sp, cert, error in ((primary.verify,problem,pcert,schema.Invalid),
                                                  (reference.verify,spec,rcert,reference.InvalidCertificate)):
                        try: check(sp, cert)
                        except error: pass
                        else: raise AssertionError('False hit of unreachable target accepted.')
                    negative = producer.produce(spec)['certificate']
                    require(reference.verify(spec, negative).is_empty, 'Reference negative proof failed.')
                    counts['negative_targets_with_false_hit_rejected_by_both'] += 1
                    counts['valid_reference_negative_certificates'] += 1
                else:
                    pr = primary.verify(problem, pcert)
                    rr = reference.verify(spec, rcert)
                    require((pr.first,pr.period)==(rr.offset,rr.period)==(truth,len(orbit)),
                            'Positive checker disagreement.')
                    counts['positive_agreements'] += 1
                    bad = deepcopy(pcert)
                    bad['inverse_matrix'][0][0] = (bad['inverse_matrix'][0][0]+1) % p
                    try: primary.verify(problem,bad)
                    except schema.Invalid: pass
                    else: raise AssertionError('Invalid inverse witness accepted.')
                    counts['corrupted_inverse_witnesses_rejected_by_primary'] += 1
                    badp=deepcopy(pcert); badp['first'] += pr.period
                    badr=deepcopy(rcert); badr['claim']['offset'] += rr.period
                    for check, sp, cert, error in ((primary.verify,problem,badp,schema.Invalid),
                                                  (reference.verify,spec,badr,reference.InvalidCertificate)):
                        try: check(sp,cert)
                        except error: pass
                        else: raise AssertionError('Noncanonical offset accepted.')
                    counts['noncanonical_offsets_rejected_by_both'] += 1
                counts['state_target_cases'] += 1
                result_hash.update(json.dumps([p,a,c,initial,target,truth,len(orbit)],sort_keys=True).encode())
    files = ['alc/checker.py','alc/schema.py']
    return dict(schema=1, comparison_counts=counts, outcomes_sha256=result_hash.hexdigest(),
                primary_source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
                scope='Two implementations agree on the enumerated domain and reject the tested false positive claims. '
                      'Primary API remains positive-only; reference negative schemas are NOT production support. '
                      'No formal verification, native algebra performance comparison, or novelty claim.')


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); report=run()
    with args.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps(report,indent=2,sort_keys=True))
