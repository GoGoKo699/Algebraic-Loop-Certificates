"""Untrusted AIGER producer using each seed's exact odd point period.

This extends the experimental witness construction, not the production API.
Its output requires external source-bound Certifaiger proof checking.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.aiger_lfsr_v1.check import Rejected, parse, replay
from research.proof_interface_v1.produce import Builder, compose


class Unsupported(ValueError):
    pass


def factor_complete(value):
    """Complete deterministic trial factorization, with explicit bounded input."""
    if type(value) is not int or not 0 < value < (1 << 24) or not value & 1:
        raise Unsupported("M must be positive, odd, and below 2^24")
    original = value
    factors = []
    divisor = 2
    trials = 0
    while divisor * divisor <= value:
        trials += 1
        exponent = 0
        while value % divisor == 0:
            value //= divisor
            exponent += 1
        if exponent:
            factors.append((divisor, exponent))
        divisor += 1
    if value > 1:
        factors.append((value, 1))
    product = 1
    for prime, exponent in factors:
        product *= prime ** exponent
    if product != original:
        raise RuntimeError("incomplete internal factorization")
    return tuple(factors), trials


def matrix_power(rows, exponent):
    value = tuple(1 << j for j in range(len(rows)))
    while exponent:
        if exponent & 1:
            value = compose(value, rows)
        exponent >>= 1
        if exponent:
            rows = compose(rows, rows)
    return value


def canonical_rowspace(rows):
    """Reduced binary rowspace basis, highest-set-bit pivots, sorted by pivot."""
    basis = {}
    for original in rows:
        row = original
        for pivot in sorted(basis, reverse=True):
            if row >> pivot & 1:
                row ^= basis[pivot]
        if row:
            pivot = row.bit_length() - 1
            for old in tuple(basis):
                if basis[old] >> pivot & 1:
                    basis[old] ^= row
            basis[pivot] = row
    return tuple(basis[pivot] for pivot in sorted(basis))


def add_words(builder, left, right):
    carry = 0
    result = []
    for a, b in zip(left, right):
        parity = builder.xor(a, b)
        result.append(builder.xor(parity, carry))
        carry = builder.any((builder.and_(a, b), builder.and_(carry, parity)))
    return tuple(result)


def multiply_constant(builder, word, constant):
    """Shift/add fixed multiplier, modulo the explicit output word width."""
    width = len(word)
    result = (0,) * width
    for shift in range(constant.bit_length()):
        if constant >> shift & 1:
            shifted = (0,) * shift + word[:width-shift]
            result = add_words(builder, result, shifted)
    return result


def less_unsigned(builder, left, right):
    equal = 1
    less = 0
    for a, b in zip(reversed(left), reversed(right)):
        less = builder.any((less, builder.all((equal, a ^ 1, b))))
        equal = builder.and_(equal, builder.xor(a, b) ^ 1)
    return less


def produce(raw, taps, odd_multiple, *, mutation=None):
    """Return an untrusted candidate and deterministic construction metadata.

    Fixed source-aware variant: canonical row-reduced kernel tests, shared
    duplicate kernels, and ripple shift/add multiplication by fixed primes.
    Mutations are deliberately false candidates for the native negative gate.
    """
    if mutation not in (None, "global_bound", "skip_repeated3"):
        raise Unsupported("unknown negative control")
    factors, factor_trials = factor_complete(odd_multiple)
    try:
        model = parse(raw)
        replay(model, taps)
    except Rejected as exc:
        raise Unsupported("source wrapper is unsupported") from exc
    n = model.n
    if n > 24:
        raise Unsupported("producer dimension limit is 24")
    width = max(1, odd_multiple.bit_length())
    rows = (taps,) + tuple(1 << (i - 1) for i in range(1, n))
    identity = tuple(1 << i for i in range(n))
    if matrix_power(rows, odd_multiple) != identity:
        raise Unsupported("the supplied odd M does not satisfy A^M = I")
    if mutation == "skip_repeated3" and (3, 2) not in factors:
        raise Unsupported("skip_repeated3 requires the 3^2 factor")
    old_l = len(model.latches)
    old_base = n + old_l

    def translated(literal):
        return literal + 2 * width if literal // 2 > old_base else literal

    imported = [(translated(lhs), translated(a), translated(b))
                for lhs, a, b in model.gates]
    builder = Builder(old_base + width, imported)
    inputs = model.inputs
    r = tuple(lhs for lhs, _ in model.latches[:n])
    s = tuple(lhs for lhs, _ in model.latches[n:2*n])
    c = model.latches[-1][0]
    t = tuple(2 * (old_base + i + 1) for i in range(width))

    period = (1,) + (0,) * (width-1)
    kernels = {}
    factor_records = []
    for prime, exponent in factors:
        for level in range(1, exponent+1):
            power_exponent = odd_multiple // (prime ** level)
            fixed = matrix_power(rows, power_exponent)
            kernel = canonical_rowspace(tuple(a ^ b for a, b in zip(fixed, identity)))
            if kernel not in kernels:
                kernels[kernel] = builder.all(
                    builder.parity(s[j] for j in range(n) if row >> j & 1) ^ 1
                    for row in kernel)
            fixes_seed = kernels[kernel]
            skipped = mutation == "skip_repeated3" and prime == 3 and level == 2
            if not skipped:
                multiplied = multiply_constant(builder, period, prime)
                period = tuple(builder.mux(fixes_seed, old, new)
                               for old, new in zip(period, multiplied))
            factor_records.append({"prime": prime, "level": level,
                                   "matrix_exponent": power_exponent,
                                   "kernel_rows": list(kernel), "kernel_rank": len(kernel),
                                   "fixes_seed_literal": fixes_seed, "skipped": skipped})
    if mutation == "global_bound":
        period = tuple((odd_multiple >> i) & 1 for i in range(width))

    ar = builder.matrix_vector(rows, r)
    nonzero_s = builder.any(s)
    match = builder.all((nonzero_s,) + tuple(
        builder.xor(a, b) ^ 1 for a, b in zip(ar, s)))
    reset_phase = builder.any((builder.any(inputs), nonzero_s ^ 1, match))
    carry = 1
    phase_next = []
    for bit in t:
        phase_next.append(builder.and_(reset_phase ^ 1, builder.xor(bit, carry)))
        carry = builder.and_(carry, bit)
    powered_s = s
    matrix = rows
    for phase_bit in t:
        advanced = builder.matrix_vector(matrix, powered_s)
        powered_s = tuple(builder.mux(phase_bit, a, b)
                          for a, b in zip(advanced, powered_s))
        matrix = compose(matrix, matrix)
    idle = builder.all((builder.any(r) ^ 1, nonzero_s ^ 1, builder.any(t) ^ 1))
    active = builder.all((nonzero_s, less_unsigned(builder, t, period),
                          builder.xor(c, t[0]) ^ 1) + tuple(
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
    lines += [f"i{i} = {literal}" for i, literal in enumerate(inputs)]
    lines += [f"l{i} = {lhs}" for i, (lhs, _) in enumerate(model.latches)]
    lines += [f"l{old_l+i} phase_bit_{i}" for i in range(width)]
    lines += ["o0 strengthened_bad", "c",
              "Untrusted exact-seed-period witness; check against the separate model.",
              "model_sha256 " + hashlib.sha256(raw).hexdigest()]
    witness = ("\n".join(lines) + "\n").encode("ascii")
    return witness, {
        "bits": n, "phase_bits": width, "odd_multiple": odd_multiple,
        "mutation": mutation, "variant": "canonical_rref_shared_kernels_fixed_prime_shift_add",
        "factorization": [list(x) for x in factors],
        "factorization_trial_divisors": factor_trials,
        "factorization_algorithm": "complete deterministic trial division, M < 2^24",
        "matrix_order_identity_checked": True,
        "kernel_factors": factor_records, "distinct_kernel_predicates": len(kernels),
        "period_literals": list(period), "invariant_literal": invariant,
        "ghost_literals": list(t), "phase_next_literals": list(phase_next),
        "original_bad_literal": translated(model.output),
        "model_sha256": hashlib.sha256(raw).hexdigest(),
        "witness_sha256": hashlib.sha256(witness).hexdigest(),
        "witness_bytes": len(witness), "original_latches": old_l,
        "original_ands": len(model.gates), "witness_ands": len(builder.gates),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--taps", required=True, type=lambda x: int(x, 0))
    parser.add_argument("--odd-multiple", required=True, type=lambda x: int(x, 0))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mutation", choices=("global_bound", "skip_repeated3"))
    args = parser.parse_args()
    witness, metadata = produce(args.model.read_bytes(), args.taps,
                                args.odd_multiple, mutation=args.mutation)
    with args.output.open("xb") as stream:
        stream.write(witness)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
