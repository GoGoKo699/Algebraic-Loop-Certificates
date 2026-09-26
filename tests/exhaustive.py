"""Independent small orbit enumeration and consumer checks; exact integers only."""
from __future__ import annotations
from itertools import product
import hashlib
import json
from pathlib import Path
from alc.schema import Problem, canonical
from alc.producer import produce
from alc.checker import verify
from alc.consumer import window, intersect_schedule


def cases():
    # ALL invertible 2x2 affine maps over F2, and linear maps over F3.
    for p in (2, 3):
        for a,b,c,d in product(range(p), repeat=4):
            if (a*d-b*c) % p == 0:
                continue
            A = ((a,b),(c,d))
            shifts = product(range(p), repeat=2) if p == 2 else [(0,0)]
            for offset in shifts:
                for initial in product(range(p), repeat=2):
                    for target in product(range(p), repeat=2):
                        yield Problem(p, A, tuple(offset), initial, target)
    # ALL invertible one-dimensional affine maps over F5.
    for a,c,x,y in product(range(1,5), range(5), range(5), range(5)):
        yield Problem(5, ((a,),), (c,), (x,), (y,))


def reference(problem):
    """Scalar stepping; no checker powers, period reduction, or primality code."""
    x, trajectory = list(problem.initial), []
    while tuple(x) not in trajectory:
        trajectory.append(tuple(x))
        out = []
        for i in range(len(x)):
            total = problem.c[i]
            for j in range(len(x)):
                total += problem.A[i][j]*x[j]
            out.append(total % problem.p)
        x = out
    if tuple(x) != problem.initial:
        raise AssertionError('Reference orbit not a pure cycle')
    first = trajectory.index(problem.target) if problem.target in trajectory else None
    return trajectory, first


def run():
    summary = {'cases': 0, 'positive_certificates': 0, 'unreachable_enumerated': 0,
               'window_queries': 0, 'schedule_intersections': 0,
               'by_field': {}, 'maximum_period': 0}
    h = hashlib.sha256()
    for problem in cases():
        states, first = reference(problem)
        r = len(states)
        result = produce(problem.as_dict(), max_steps=problem.p**len(problem.A))
        summary['cases'] += 1
        key = 'F'+str(problem.p)
        summary['by_field'][key] = summary['by_field'].get(key, 0)+1
        summary['maximum_period'] = max(summary['maximum_period'], r)
        if first is None:
            if result['status'] != 'unreachable_enumerated' or result['certified'] is not False:
                raise AssertionError('Producer mislabeled a negative reference result')
            summary['unreachable_enumerated'] += 1
        else:
            if result['status'] != 'candidate':
                raise AssertionError('Producer missed a positive reference result')
            hits = verify(problem.as_dict(), result['certificate'])
            if (hits.first, hits.period) != (first, r):
                raise AssertionError('Checker accepted an incorrect complete hit set')
            summary['positive_certificates'] += 1
            for lo, hi in [(0,0), (0,3*r+2), (r,4*r+1), (5*r+1,6*r+3)]:
                actual = [t for t in range(lo, hi+1) if states[t % r] == problem.target]
                answer = window(hits, lo, hi)
                if answer['count'] != len(actual) or answer['first'] != (actual[0] if actual else None):
                    raise AssertionError('Incorrect count or first hit in finite window')
                if answer['last'] != (actual[-1] if actual else None):
                    raise AssertionError('Incorrect last hit')
                summary['window_queries'] += 1
            for modulus in (1,2,3):
                for residue in range(modulus):
                    joined = intersect_schedule(hits, residue, modulus)
                    brute = [t for t in range(r*modulus) if states[t % r] == problem.target and t % modulus == residue]
                    if (joined is None) != (not brute):
                        raise AssertionError('Incorrect CRT consistency result')
                    if joined is not None:
                        f, period = joined
                        if f != brute[0] or any((t-f) % period for t in brute):
                            raise AssertionError('Incorrect CRT progression')
                        generated = list(range(f, r*modulus, period))
                        if generated != brute:
                            raise AssertionError('Incomplete CRT progression')
                    summary['schedule_intersections'] += 1
        h.update(canonical([problem.as_dict(), first, r]))
    summary['case_sha256'] = h.hexdigest()
    summary['arithmetic'] = 'exact Python integers; no quantum or native algebra backend'
    summary['scope'] = 'exhaustive over the three declared finite families, not every prime field or recurrence'
    return summary


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
