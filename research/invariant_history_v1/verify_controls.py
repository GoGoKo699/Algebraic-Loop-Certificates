#!/usr/bin/env python3
"""Small independent semantic audit; no source recognizer or producer imports."""

from collections import deque
from itertools import permutations, product
import json
import time


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def transition(f, q, u):
    r, s, c = q
    match = s != 0 and f[r] == s
    return (f[r], s, 0 if match else 1 - c) if u == 0 else (u, u, 0)


def bad(f, q, u):
    r, s, c = q
    return (u == 0 and c == 1 and s != 0 and f[r] == s) or (
        s != 0 and f[r] == 0
    )


def explicit_sets(f):
    """BFS and backward attraction use only transition/detector semantics."""
    states = set(product(range(len(f)), range(len(f)), range(2)))
    edges = {q: {transition(f, q, u) for u in range(len(f))} for q in states}
    reached = {(0, 0, 0)}
    pending = deque(reached)
    while pending:
        for nxt in edges[pending.popleft()]:
            if nxt not in reached:
                reached.add(nxt)
                pending.append(nxt)
    unsafe = {q for q in states if any(bad(f, q, u) for u in range(len(f)))}
    while True:
        enlarged = unsafe | {q for q in states if edges[q] & unsafe}
        if enlarged == unsafe:
            return reached, states - unsafe
        unsafe = enlarged


def orbit(f, seed):
    values = [seed]
    while f[values[-1]] != seed:
        values.append(f[values[-1]])
        if len(values) > len(f):
            raise ValueError("not a permutation cycle")
    return values


def recover(f, r, s, period, invariant):
    if period == 1:
        return 0
    base_parity = 1 - int((r, s, 0) in invariant)
    lo, hi = 0, period
    while hi - lo > 1:
        threshold = (lo + hi) // 2
        shift = period - threshold
        shifted = r
        for _ in range(shift):
            shifted = f[shifted]
        shifted_parity = 1 - int((shifted, s, 0) in invariant)
        above = shifted_parity ^ base_parity ^ (shift & 1)
        if above:
            lo = threshold
        else:
            hi = threshold
    return lo


def verify():
    counts = dict(permutations=0, odd_permutations=0, even_cycle_refusals=0,
                  source_states=0, phase_pairs=0, phase_recoveries=0,
                  history_states=0, history_edges=0, tail_controls=0,
                  padded_permutations=0, padded_output_checks=0)
    for active in range(6):
        for perm in permutations(range(1, active + 1)):
            f = (0,) + perm
            counts["permutations"] += 1
            cycles = {s: orbit(f, s) for s in range(len(f))}
            even_seed = next((s for s in cycles if len(cycles[s]) % 2 == 0), None)
            if even_seed is not None:
                # An actual reachable error, not rejection inferred from a label.
                q = transition(f, (0, 0, 0), even_seed)
                found = False
                for _ in range(len(cycles[even_seed])):
                    found |= bad(f, q, 0)
                    q = transition(f, q, 0)
                require(found, "even cycle failed to produce a reachable error")
                counts["even_cycle_refusals"] += 1
                continue
            counts["odd_permutations"] += 1
            reached, safe = explicit_sets(f)
            expected_r = {(0, 0, 0), (0, 0, 1)}
            expected_s = {(r, 0, c) for r in range(len(f)) for c in range(2)}
            for s in range(1, len(f)):
                for t, r in enumerate(cycles[s]):
                    expected_r.add((r, s, t & 1))
                    expected_s.add((r, s, t & 1))
                    counts["phase_pairs"] += 1
                    for invariant in (reached, safe):
                        require(recover(f, r, s, len(cycles[s]), invariant) == t,
                                "exact phase recovery disagrees with orbit phase")
                        counts["phase_recoveries"] += 1
                for r in set(range(1, len(f))) - set(cycles[s]):
                    expected_s.update((r, s, c) for c in range(2))
            require(reached == expected_r, "BFS reachable set differs from formula")
            require(safe == expected_s, "backward safe set differs from formula")
            # At sizes 2 and 4, a single active cycle admits the exact total
            # bit-string padding from the note, including its zero output.
            if active in (1, 3) and len(cycles[1]) == active:
                for s in range(1, len(f)):
                    h = cycles[s] + [0]
                    require(set(h) == set(range(len(f))),
                            "padded map is not a total permutation")
                    inverse = {r: t for t, r in enumerate(h)}
                    for r in range(len(f)):
                        for invariant in (reached, safe):
                            require(((r, s, 0) in invariant) == (inverse[r] % 2 == 0),
                                    "padded inverse-bit equality failed")
                            counts["padded_output_checks"] += 1
                    counts["padded_permutations"] += 1
            states = list(product(range(len(f)), range(len(f)), range(2)))
            counts["source_states"] += len(states)
            max_period = max(map(len, cycles.values()))
            modulus = 1 << max(1, (max_period - 1).bit_length())

            def history(q, t):
                r, s, c = q
                if s == 0:
                    return r == 0 and t == 0
                if t >= len(cycles[s]):
                    return False
                # Direct stepping is separate from the table used in the formulas.
                point = s
                for _ in range(t):
                    point = f[point]
                return r == point and c == (t & 1)

            projection = set()
            for q in states:
                for t in range(modulus):
                    if not history(q, t):
                        continue
                    projection.add(q)
                    counts["history_states"] += 1
                    r, s, _ = q
                    for u in range(len(f)):
                        require(not bad(f, q, u), "history predicate admits bad state")
                        reset = u != 0 or s == 0 or (s != 0 and f[r] == s)
                        nxt_t = 0 if reset else (t + 1) % modulus
                        require(history(transition(f, q, u), nxt_t),
                                "history predicate is not inductive")
                        counts["history_edges"] += 1
            require(projection == reached, "history projection differs from reachability")

    # Dropping recurrence invalidates forced parity: both counters at a tail
    # seed are universally safe, although only the zero counter is reachable.
    tail = (0, 1, 1)
    reached, safe = explicit_sets(tail)
    require((2, 2, 0) in reached and (2, 2, 1) not in reached,
            "tail control lacks intended reachability distinction")
    require((2, 2, 0) in safe and (2, 2, 1) in safe,
            "tail control does not permit both safe counter values")
    counts["tail_controls"] += 1
    require(counts["permutations"] == 154, "permutation count changed")
    require(counts["odd_permutations"] == 60, "odd-permutation count changed")
    require(counts["even_cycle_refusals"] == 94, "even-cycle control count changed")
    return counts


if __name__ == "__main__":
    start = time.perf_counter()
    results = verify()
    print(json.dumps({"status": "PASS", "counts": results,
                      "elapsed_seconds": time.perf_counter() - start}, indent=2))
