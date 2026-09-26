"""Deterministic exhaustive controls, independent of producer search decisions."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import product
import json
from math import gcd, isqrt, lcm
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alc import (InvalidCertificate, Limits, VerificationLimit, VerifiedSummary,
                 count_interval, first_at_least, synchronize, verify)
from alc.checker import check_primes, instance_hash
from alc.producers import TrialArithmetic, produce


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def instance(p, a, c, x, y):
    return dict(schema='alc-instance-1', modulus=p, matrix=[list(r) for r in a],
                translation=list(c), initial=list(x), target=list(y))


def trajectory(spec):
    """Independent ordinary affine steps; no arithmetic-kernel imports."""
    p = spec['modulus']; a = spec['matrix']; c = spec['translation']
    x = tuple(spec['initial']); start = x
    states = []
    while True:
        require(x not in states, 'Unexpected transient in invertible recurrence.')
        states.append(x)
        x = tuple((sum(a[i][j]*x[j] for j in range(len(x))) + c[i]) % p
                  for i in range(len(x)))
        if x == start:
            return states


def families():
    # Every invertible 2x2 linear matrix over F2/F3.
    for p in (2, 3):
        for flat in product(range(p), repeat=4):
            a = (flat[:2], flat[2:])
            if (a[0][0]*a[1][1]-a[0][1]*a[1][0]) % p:
                yield p, a, (0, 0), 'linear-2d'
    # All invertible affine recurrences of dimension one over F2/F3/F5.
    for p in (2, 3, 5):
        for scalar in range(1, p):
            for shift in range(p):
                yield p, ((scalar,),), (shift,), 'affine-1d'
    # All nonzero translations of invertible 2x2 matrices over F2.
    for flat in product(range(2), repeat=4):
        a = (flat[:2], flat[2:])
        if (a[0][0]*a[1][1]-a[0][1]*a[1][0]) % 2:
            for c in ((0, 1), (1, 0), (1, 1)):
                yield 2, a, c, 'affine-2d'


def run():
    stats = Counter(); kinds = Counter(); checksum = hashlib.sha256()
    for p, a, c, family in families():
        stats['recurrences'] += 1
        states = list(product(range(p), repeat=len(a)))
        for x in states:
            orbit = trajectory(instance(p, a, c, x, x))
            for y in states:
                spec = instance(p, a, c, x, y)
                candidate = produce(spec, max_steps=p**len(a))
                require(candidate['status'] == 'candidate', 'Small complete enumeration timed out.')
                cert = candidate['certificate']
                result = verify(spec, cert)
                offset = orbit.index(y) if y in orbit else None
                require(result.is_empty == (offset is None), 'Wrong reachability.')
                if offset is not None:
                    require((result.offset, result.period) == (offset, len(orbit)), 'Wrong least schedule.')
                    bad = deepcopy(cert); bad['claim']['offset'] = result.offset + result.period
                    try: verify(spec, bad)
                    except InvalidCertificate: stats['noncanonical_offsets_rejected'] += 1
                    else: raise AssertionError('Noncanonical offset accepted.')
                    bad = deepcopy(cert); bad['claim']['period'] *= 2
                    factors = dict(bad['claim']['factors']); factors[2] = factors.get(2, 0) + 1
                    bad['claim']['factors'] = [[q, factors[q]] for q in sorted(factors)]
                    if not any(z['n'] == 2 for z in bad['prime_proofs']):
                        bad['prime_proofs'].insert(0, {'n': 2})
                    try: verify(spec, bad)
                    except InvalidCertificate: stats['nonminimal_periods_rejected'] += 1
                    else: raise AssertionError('Nonminimal period accepted.')
                for low, high in ((0, 0), (0, 20), (3, 32), (12, 17)):
                    hits = [t for t in range(low, high+1) if orbit[t % len(orbit)] == y]
                    require(count_interval(result, low, high) == len(hits), 'Interval count differs.')
                    expected = None if offset is None else next(
                        t for t in range(low, low + len(orbit)) if orbit[t % len(orbit)] == y)
                    require(first_at_least(result, low) == expected, 'Next hit differs.')
                    stats['consumer_queries'] += 2
                stats['state_target_cases'] += 1
                kinds[result.evidence_kind] += 1
                checksum.update(json.dumps([family, p, a, c, x, y, result.as_dict()],
                                           sort_keys=True).encode())
    # Exhaustive schedule intersections independently checked over their lcm.
    for m in range(1, 13):
        for n in range(1, 13):
            for a in range(m):
                for b in range(n):
                    left = VerifiedSummary('left', 'test-schedule', a, m)
                    right = VerifiedSummary('right', 'test-schedule', b, n)
                    result = synchronize(left, right)
                    hits = [t for t in range(lcm(m, n)) if t % m == a and t % n == b]
                    require(result.is_empty == (not hits), 'CRT reachability differs.')
                    if hits:
                        require(result.offset == hits[0] and result.period == lcm(m, n), 'CRT schedule differs.')
                    stats['schedule_intersections'] += 1
    # Prove primes, compare with independent trial primality, and reject composites.
    for n in range(2, 300):
        expected = all(n % q for q in range(2, isqrt(n)+1))
        arithmetic = TrialArithmetic()
        try:
            arithmetic.prime(n)
            proof = [arithmetic.proofs[q] for q in sorted(arithmetic.proofs)]
            require(n in check_primes(proof), 'Generated prime proof failed.')
            require(expected, 'Composite accepted.')
        except InvalidCertificate:
            require(not expected, 'Prime rejected.')
        stats['primality_cases'] += 1
    # Consumer performs arbitrary-size horizon arithmetic, no trajectory traversal.
    fib = json.loads((ROOT/'examples/fibonacci.json').read_text())
    cert = json.loads((ROOT/'examples/fibonacci.certificate.json').read_text())
    summary = verify(fib, cert)
    require(count_interval(summary, 0, 10**100) == 10**100//16, 'Huge-horizon count failed.')
    # Unknown must not be confused with an empty hit set; a zero budget yields no cert.
    for args in (dict(max_steps=0), dict(max_trial_work=0)):
        unknown = produce(fib, **args)
        require(unknown['status'] == 'unknown' and 'certificate' not in unknown, 'Unknown promoted to evidence.')
        stats['resource_limits_checked'] += 1
    # Invalid-data mutations, not just mathematical false claims.
    mutations = []
    bad = deepcopy(cert); bad['claim']['offset'] = True; mutations.append((fib, bad))
    bad = deepcopy(cert); bad['claim']['offset'] = -1; mutations.append((fib, bad))
    bad = deepcopy(cert); bad['claim']['factors'] = []; mutations.append((fib, bad))
    bad = deepcopy(cert); bad['claim']['factors'].append([2, 1]); mutations.append((fib, bad))
    bad = deepcopy(cert); bad['prime_proofs'] = [{'n': 7}]; mutations.append((fib, bad))
    bad = deepcopy(cert); bad['claim']['kind'] = 'trusted-by-producer'; mutations.append((fib, bad))
    bad = deepcopy(cert); bad['untrusted_extra'] = 'ignore'; mutations.append((fib, bad))
    bad = deepcopy(fib); bad['initial'][0] = 8; mutations.append((bad, cert))
    bad = deepcopy(fib); bad['initial'][0] = 2; mutations.append((bad, cert))
    bad = deepcopy(fib); bad['matrix'][1] = [1]; mutations.append((bad, cert))
    bad = deepcopy(fib); bad['modulus'] = 8
    bc = deepcopy(cert); bc['instance_sha256'] = instance_hash(bad); mutations.append((bad, bc))
    bad = deepcopy(fib); bad['matrix'] = [[1, 0], [0, 0]]
    bc = deepcopy(cert); bc['instance_sha256'] = instance_hash(bad); mutations.append((bad, bc))
    for stem, key, value in [('outside_span', 'separator', [0,0,0]),
                             ('inside_span_absent', 'states', [[1]])]:
        sp = json.loads((ROOT/f'examples/{stem}.json').read_text())
        bad = json.loads((ROOT/f'examples/{stem}.certificate.json').read_text())
        bad['claim'][key] = value; mutations.append((sp, bad))
    for sp, bad in mutations:
        try: verify(sp, bad)
        except InvalidCertificate: stats['malformed_or_false_certificates_rejected'] += 1
        else: raise AssertionError('Bad input/certificate was accepted.')
    try: verify(fib, cert, Limits(max_integer_bits=3))
    except VerificationLimit: stats['resource_limits_checked'] += 1
    else: raise AssertionError('Oversized input was not limited.')
    # CLI trust boundary: separate producer process, then checker/consumer.
    with tempfile.TemporaryDirectory(prefix='alc-cli-') as d:
        dest = Path(d)/'certificate.json'
        cmd = [sys.executable, '-m', 'alc']
        r = subprocess.run(cmd+['produce', 'examples/fibonacci.json', '--output', str(dest)],
                           cwd=ROOT, capture_output=True, text=True)
        require(r.returncode == 0, 'CLI producer failed: '+r.stderr)
        r = subprocess.run(cmd+['query', 'examples/fibonacci.json', str(dest), '--low', '0', '--high', '100'],
                           cwd=ROOT, capture_output=True, text=True)
        require(r.returncode == 0 and json.loads(r.stdout)['query']['count'] == 6, 'CLI verified query failed.')
        old = dest.read_bytes()
        r = subprocess.run(cmd+['produce','examples/fibonacci.json','--output',str(dest)],
                           cwd=ROOT,capture_output=True,text=True)
        require(r.returncode == 2 and dest.read_bytes() == old, 'CLI overwrote an existing artifact.')
        dup = Path(d)/'duplicate.json'; dup.write_text('{"schema":"a","schema":"b"}')
        r = subprocess.run(cmd+['check',str(dup),str(dest)],cwd=ROOT,capture_output=True,text=True)
        require(r.returncode == 2 and 'Duplicate' in r.stderr, 'Duplicate JSON keys accepted.')
        r = subprocess.run(cmd+['produce','examples/fibonacci.json','--output',str(Path(d)/'unknown.json'),
                                 '--max-steps','0'],cwd=ROOT,capture_output=True,text=True)
        require(r.returncode == 3 and not (Path(d)/'unknown.json').exists(), 'CLI unknown emitted certificate.')
        stats['cli_controls'] = 5
    # Verify without producer module even being importable as a dependency.
    code = ('import sys,json; from alc import verify; '
            'assert "alc.producers" not in sys.modules; '
            'verify(json.load(open("examples/fibonacci.json")), '
            'json.load(open("examples/fibonacci.certificate.json"))); '
            'assert "alc.producers" not in sys.modules')
    r = subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True)
    require(r.returncode == 0, 'Checker unexpectedly depends on producer.')
    return dict(schema=1, checks=dict(sorted(stats.items())), evidence_kinds=dict(sorted(kinds.items())),
                outcomes_sha256=checksum.hexdigest(),
                scope='Fresh bootstrap controls; not reruns of the unavailable original scout ZIP. '
                      'No production algebra solver, quantum backend, formal proof assistant, or performance advantage tested.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run()
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(result,indent=2,sort_keys=True))
