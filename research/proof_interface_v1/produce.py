"""Untrusted phase-history AIGER witness producer for the fixed LFSR wrapper.

The result must be checked against the separately supplied model by Certifaiger.
Local maximality diagnostics do not replace that native proof check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.aiger_lfsr_v1.check import Rejected, parse, replay


class Unsupported(ValueError):
    pass


def apply(rows, value):
    return sum(((row & value).bit_count() & 1) << i
               for i, row in enumerate(rows))


def compose(left, right):
    rows = []
    for mask in left:
        row = 0
        while mask:
            bit = mask & -mask
            row ^= right[bit.bit_length() - 1]
            mask ^= bit
        rows.append(row)
    return tuple(rows)


def point_power(rows, value, exponent):
    while exponent:
        if exponent & 1:
            value = apply(rows, value)
        exponent >>= 1
        if exponent:
            rows = compose(rows, rows)
    return value


def prime_divisors(value):
    """Deterministic bounded trial division; not an imported primality label."""
    result = []
    q = 2
    while q * q <= value:
        if value % q == 0:
            result.append(q)
            while value % q == 0:
                value //= q
        q += 1
    if value > 1:
        result.append(value)
    return result


def maximality(rows):
    """Exact order of point 1 equals the number of nonzero binary states."""
    n = len(rows)
    period = (1 << n) - 1
    full = point_power(rows, 1, period)
    controls = [
        {"prime": p, "exponent": period // p,
         "state": point_power(rows, 1, period // p)}
        for p in prime_divisors(period)
    ]
    if full != 1 or any(row["state"] == 1 for row in controls):
        raise Unsupported("the phase witness requires maximal nonzero point period")
    return {"initial": 1, "period": period, "full_return": full,
            "prime_divisor_controls": controls}


class Builder:
    def __init__(self, variables, imported):
        self.variables = variables
        self.gates = list(imported)
        self.lookup = {}
        for lhs, a, b in self.gates:
            self.lookup.setdefault(tuple(sorted((a, b))), lhs)
        self.variables += len(self.gates)

    def and_(self, a, b):
        if a == 0 or b == 0 or a == (b ^ 1):
            return 0
        if a == 1:
            return b
        if b == 1 or a == b:
            return a
        key = tuple(sorted((a, b)))
        if key not in self.lookup:
            self.variables += 1
            lhs = 2 * self.variables
            self.gates.append((lhs, key[1], key[0]))
            self.lookup[key] = lhs
        return self.lookup[key]

    def all(self, values):
        value = 1
        for literal in values:
            value = self.and_(value, literal)
        return value

    def any(self, values):
        return self.all(literal ^ 1 for literal in values) ^ 1

    def xor(self, a, b):
        if a == b:
            return 0
        if a == (b ^ 1):
            return 1
        if a in (0, 1):
            return b ^ a
        if b in (0, 1):
            return a ^ b
        return self.any((self.and_(a, b ^ 1), self.and_(a ^ 1, b)))

    def parity(self, values):
        value = 0
        for literal in values:
            value = self.xor(value, literal)
        return value

    def mux(self, select, yes, no):
        if yes == no:
            return yes
        return self.any((self.and_(select, yes), self.and_(select ^ 1, no)))

    def matrix_vector(self, rows, vector):
        return tuple(self.parity(vector[j] for j in range(len(vector))
                                 if row >> j & 1) for row in rows)


def produce(raw, taps, *, mutation=None):
    """Return candidate AAG bytes and construction metadata.

    Only the preserved source wrapper, widths 2..24, and maximal nonzero
    periods are supported. The two mutation names are negative test controls.
    """
    if mutation not in (None, "freeze_phase", "inverted_phase"):
        raise Unsupported("unknown negative control")
    try:
        model = parse(raw)
        replay(model, taps)
    except Rejected as exc:
        raise Unsupported("source wrapper is unsupported") from exc
    n = model.n
    if n > 24:
        raise Unsupported("producer dimension limit is 24")
    rows = (taps,) + tuple(1 << (i - 1) for i in range(1, n))
    order = maximality(rows)
    old_l = len(model.latches)
    old_base = n + old_l

    def translated(literal):
        return literal + 2 * n if literal // 2 > old_base else literal

    imported = [(translated(lhs), translated(a), translated(b))
                for lhs, a, b in model.gates]
    builder = Builder(old_base + n, imported)
    inputs = model.inputs
    r = tuple(lhs for lhs, _ in model.latches[:n])
    s = tuple(lhs for lhs, _ in model.latches[n:2*n])
    c = model.latches[-1][0]
    t = tuple(2 * (old_base + i + 1) for i in range(n))

    ar = builder.matrix_vector(rows, r)
    nonzero_s = builder.any(s)
    match = builder.all((nonzero_s,) + tuple(
        builder.xor(a, b) ^ 1 for a, b in zip(ar, s)))
    reset_phase = builder.any((builder.any(inputs), nonzero_s ^ 1, match))
    increment = []
    carry = 1
    for bit in t:
        increment.append(builder.xor(bit, carry))
        carry = builder.and_(carry, bit)
    phase_next = tuple(builder.and_(reset_phase ^ 1, bit) for bit in increment)
    if mutation == "freeze_phase":
        phase_next = (0,) * n

    powered_s = s
    matrix_power = rows
    for phase_bit in t:
        advanced = builder.matrix_vector(matrix_power, powered_s)
        powered_s = tuple(builder.mux(phase_bit, a, b)
                          for a, b in zip(advanced, powered_s))
        matrix_power = compose(matrix_power, matrix_power)
    same_phase = builder.xor(c, t[0]) ^ 1
    if mutation == "inverted_phase":
        same_phase ^= 1
    idle = builder.all((builder.any(r) ^ 1, nonzero_s ^ 1,
                        builder.any(t) ^ 1))
    active = builder.all((nonzero_s, builder.all(t) ^ 1, same_phase) + tuple(
        builder.xor(a, b) ^ 1 for a, b in zip(r, powered_s)))
    invariant = builder.any((idle, active))
    output = builder.any((translated(model.output), invariant ^ 1))

    latches = [(lhs, translated(rhs)) for lhs, rhs in model.latches]
    latches += list(zip(t, phase_next))
    lines = [f"aag {builder.variables} {n} {len(latches)} 1 {len(builder.gates)}"]
    lines += [str(x) for x in inputs]
    lines += [f"{lhs} {rhs} 0" for lhs, rhs in latches]
    lines.append(str(output))
    lines += [f"{lhs} {a} {b}" for lhs, a, b in builder.gates]
    lines += [f"i{i} = {literal}" for i, literal in enumerate(model.inputs)]
    lines += [f"l{i} = {lhs}" for i, (lhs, _) in enumerate(model.latches)]
    lines += [f"l{old_l+i} phase_bit_{i}" for i in range(n)]
    lines += ["o0 strengthened_bad", "c",
              "Untrusted phase-history witness; check against the separate model.",
              "model_sha256 " + hashlib.sha256(raw).hexdigest()]
    witness = ("\n".join(lines) + "\n").encode("ascii")
    return witness, {
        "bits": n, "mutation": mutation,
        "model_sha256": hashlib.sha256(raw).hexdigest(),
        "witness_sha256": hashlib.sha256(witness).hexdigest(),
        "witness_bytes": len(witness), "original_latches": old_l,
        "ghost_latches": n, "original_ands": len(model.gates),
        "witness_ands": len(builder.gates), "maximality": order,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--taps", required=True, type=lambda x: int(x, 0))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mutation", choices=("freeze_phase", "inverted_phase"))
    args = parser.parse_args()
    witness, metadata = produce(args.model.read_bytes(), args.taps, mutation=args.mutation)
    with args.output.open("xb") as stream:
        stream.write(witness)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
