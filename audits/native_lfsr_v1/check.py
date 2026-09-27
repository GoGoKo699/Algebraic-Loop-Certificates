"""Replay four source-visible SmokeRand controls with the unchanged alc checker.

This is an experimental workload adapter, not a C frontend. The inspected source
uses only fixed XORs, logical shifts, rotations and uint32 truncation. Their
linearity justifies reconstructing each exact matrix from its basis images.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from alc.checker import verify
from alc.producer import assemble
from alc.schema import Invalid, Problem, canonical

MASK = (1 << 32) - 1
PRIMES = (3, 5, 17, 257, 65537)
CASES = ('shr3', 'xorrot32', 'xorrot32_bad1', 'xorrot32_bad2')


def rotl(x, n):
    return ((x << n) | (x >> (32 - n))) & MASK


def step(name, x):
    if name == 'shr3':
        x ^= (x << 13) & MASK
        x ^= x >> 17
        return x ^ ((x << 5) & MASK)
    if name not in CASES:
        raise ValueError('unsupported fixed control')
    shift = 2 if name == 'xorrot32_bad1' else 1
    left, right = (6, 23) if name == 'xorrot32_bad2' else (9, 27)
    x ^= (x << shift) & MASK
    return x ^ rotl(x, left) ^ rotl(x, right)


def apply_columns(columns, value):
    out = 0
    while value:
        bit = value & -value
        out ^= columns[bit.bit_length() - 1]
        value ^= bit
    return out


def powered(columns, value, exponent):
    """Independent packed-bit control; does not call alc powering."""
    while exponent:
        if exponent & 1:
            value = apply_columns(columns, value)
        exponent >>= 1
        if exponent:
            columns = [apply_columns(columns, col) for col in columns]
    return value


def document(name):
    columns = [step(name, 1 << j) for j in range(32)]
    return {
        'schema': 'alc.problem.v1', 'field': {'kind': 'prime', 'modulus': 2},
        'matrix': [[(col >> i) & 1 for col in columns] for i in range(32)],
        'offset': [0] * 32, 'initial': [1] + [0] * 31,
        'target': [1] + [0] * 31,
    }, columns


def run():
    rows, timings = [], []
    for name in CASES:
        t0 = time.perf_counter()
        doc, columns = document(name)
        t1 = time.perf_counter()
        proof = assemble(Problem.parse(doc), 0, MASK)
        t2 = time.perf_counter()
        try:
            result = verify(doc, proof)
            accepted, error, stats = True, None, result.stats
        except Invalid as exc:
            accepted, error, stats = False, str(exc), None
        t3 = time.perf_counter()
        returns = [{'exponent': t, 'state': powered(columns, 1, t)}
                   for t in (MASK,) + tuple(MASK // q for q in PRIMES)]
        if returns[0]['state'] != 1:
            negative = {'kind': 'failed_full_return', **returns[0]}
        else:
            early = next((r for r in returns[1:] if r['state'] == 1), None)
            negative = None if early is None else {'kind': 'earlier_return', **early}
        if accepted != (negative is None):
            raise RuntimeError('packed-bit control disagrees with primary checker')
        if accepted != (name in ('shr3', 'xorrot32')):
            raise RuntimeError('upstream documented control changed')
        # The positive count is meaningful only after independently checking
        # inverse, point order, zero offset, and nonzero starting state.
        mutations = {}
        # Mutate accepted originals only: rejection of an already-invalid
        # period would not test whether the altered first offset was noticed.
        for key in (('first', 'problem_sha256') if accepted else ()):
            bad = copy.deepcopy(proof)
            bad[key] = 1 if key == 'first' else '0' * 64
            try:
                verify(doc, bad)
            except Invalid:
                mutations[key] = 'rejected'
            else:
                raise RuntimeError('counterfeit accepted')
        rows.append({
            'case': name, 'problem_sha256': Problem.parse(doc).fingerprint,
            'candidate_sha256': hashlib.sha256(canonical(proof)).hexdigest(),
            'candidate_bytes': len(canonical(proof)), 'columns': columns,
            'accepted_maximal_period': accepted, 'rejection': error,
            'negative_witness': negative, 'return_controls': returns,
            'checker_counts': stats, 'mutations': mutations,
        })
        timings.append({'case': name, 'translation_seconds': t1 - t0,
                        'assembly_seconds': t2 - t1, 'verification_seconds': t3 - t2})
    return {'schema': 1, 'period_candidate': MASK, 'cases': rows}, timings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--timings', type=Path)
    args = parser.parse_args()
    result, timings = run()
    raw = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(raw)
    else:
        print(raw, end='')
    if args.timings:
        with args.timings.open('x') as stream:
            json.dump({'scope': 'single local observations; mutations excluded',
                       'rows': timings}, stream, indent=2, sort_keys=True)
            stream.write('\n')


if __name__ == '__main__':
    main()
