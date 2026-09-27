"""Independently emitted synthetic premise controls for the published wrapper.

These AAG files are new synthetic models, not members of the upstream corpus.
The emitter implements the documented input-dependent monitor equations and
shares no Boolean builder with either witness producer. Exhaustive arithmetic
replay checks every state/input assignment at the two fixed small widths.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {"rotation3": (3, 0x4), "mixed5": (5, 0x11)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def emit(n, taps):
    require((n, taps) in CASES.values(), "Only the two frozen synthetic controls are supported")
    gates = []
    next_variable = 3 * n + 1

    def both(a, b):
        nonlocal next_variable
        if not a or not b:
            return 0
        if a == 1:
            return b
        if b == 1:
            return a
        next_variable += 1
        lhs = 2 * next_variable
        gates.append((lhs, a, b))
        return lhs

    def either(a, b):
        return both(a ^ 1, b ^ 1) ^ 1

    def xor(a, b):
        return either(both(a, b ^ 1), both(a ^ 1, b))

    def any_(values):
        result = 0
        for value in values:
            result = either(result, value)
        return result

    def all_(values):
        result = 1
        for value in values:
            result = both(result, value)
        return result

    def choose(selector, yes, no):
        return either(both(selector, yes), both(selector ^ 1, no))

    inputs = tuple(2 * (i + 1) for i in range(n))
    r = tuple(2 * (n + i + 1) for i in range(n))
    s = tuple(2 * (2 * n + i + 1) for i in range(n))
    c = 2 * (3 * n + 1)
    feedback = 0
    for i, bit in enumerate(r):
        if taps >> i & 1:
            feedback = xor(feedback, bit)
    advanced = (feedback,) + r[:-1]
    input_nonzero, seed_nonzero = any_(inputs), any_(s)
    match = both(seed_nonzero, all_(xor(a, b) ^ 1 for a, b in zip(advanced, s)))
    register_next = tuple(choose(input_nonzero, u, a) for u, a in zip(inputs, advanced))
    seed_next = tuple(choose(input_nonzero, u, a) for u, a in zip(inputs, s))
    counter_next = all_((c ^ 1, input_nonzero ^ 1, match ^ 1))
    bad = either(all_((input_nonzero ^ 1, c, match)), both(seed_nonzero, any_(advanced) ^ 1))
    latch_rows = list(zip(r + s + (c,), register_next + seed_next + (counter_next,)))
    lines = [f"aag {next_variable} {n} {2*n+1} 1 {len(gates)}"]
    lines += list(map(str, inputs))
    lines += [f"{lhs} {rhs} 0" for lhs, rhs in latch_rows]
    lines.append(str(bad))
    lines += [f"{lhs} {a} {b}" for lhs, a, b in gates]
    lines += [f"i{i} input_{i}" for i in range(n)]
    lines += [f"l{i} register_bit_{i}" for i in range(n)]
    lines += [f"l{n+i} copy_bit_{i}" for i in range(n)]
    lines += [f"l{2*n} counter_bit_0", "o0 bad_state_detector", "c",
              "Synthetic premise control, independently emitted from documented monitor equations.",
              "Not an upstream published benchmark file.", f"width {n}; taps {hex(taps)}"]
    return ("\n".join(lines) + "\n").encode("ascii")


def raw_circuit(raw):
    lines = raw.decode("ascii").splitlines()
    _, maximum, n, nl, no, na = lines[0].split()
    maximum, n, nl, no, na = map(int, (maximum, n, nl, no, na))
    inputs = list(map(int, lines[1:1+n]))
    latches = [tuple(map(int, line.split())) for line in lines[1+n:1+n+nl]]
    output = int(lines[1+n+nl])
    gates = [tuple(map(int, line.split())) for line in lines[2+n+nl:2+n+nl+na]]
    return maximum, n, inputs, latches, output, gates


def verify_controls():
    rows = []
    for name, (n, taps) in CASES.items():
        raw = (HERE / "models" / (name + ".aag")).read_bytes()
        require(raw == emit(n, taps), "Synthetic fixture does not match independent emitter")
        maximum, width, inputs, latches, output, gates = raw_circuit(raw)
        require(width == n and all(row[2] == 0 for row in latches), "Incorrect source initialization")
        mask = (1 << n) - 1
        checked = 0
        for state in range(1 << (2*n+1)):
            r, s, c = state & mask, (state >> n) & mask, state >> (2*n)
            ar = ((r << 1) & mask) | ((r & taps).bit_count() & 1)
            match = bool(s and ar == s)
            for u in range(1 << n):
                values = [0] * (maximum + 1)
                for i, lit in enumerate(inputs):
                    values[lit // 2] = (u >> i) & 1
                for i, (lit, _, _) in enumerate(latches):
                    values[lit // 2] = (state >> i) & 1
                for lhs, a, b in gates:
                    values[lhs // 2] = (values[a // 2] ^ (a & 1)) & (values[b // 2] ^ (b & 1))
                next_state = sum((values[rhs // 2] ^ (rhs & 1)) << i for i, (_, rhs, _) in enumerate(latches))
                actual_bad = values[output // 2] ^ (output & 1)
                expected = (u if u else ar) | ((u if u else s) << n) | ((int(not c and not u and not match)) << (2*n))
                expected_bad = int((not u and c and match) or (s != 0 and ar == 0))
                require(next_state == expected and actual_bad == expected_bad, "Raw model disagrees with arithmetic wrapper")
                checked += 1
        periods = []
        for seed in range(1, 1 << n):
            value, period = seed, 0
            while True:
                value = ((value << 1) & mask) | ((value & taps).bit_count() & 1)
                period += 1
                require(period <= mask, "Control orbit did not close")
                if value == seed:
                    break
            periods.append(period)
        histogram = dict(sorted(Counter(periods).items()))
        require(histogram == ({1: 1, 3: 6} if n == 3 else {3: 3, 7: 7, 21: 21}), "Unexpected control periods")
        rows.append({"case": name, "state_input_assignments": checked, "nonzero_period_histogram": histogram,
                     "model_sha256": hashlib.sha256(raw).hexdigest()})
    return {"synthetic_controls": rows, "scope": "New premise controls, not published benchmark instances"}


if __name__ == "__main__":
    print(json.dumps(verify_controls(), sort_keys=True))
