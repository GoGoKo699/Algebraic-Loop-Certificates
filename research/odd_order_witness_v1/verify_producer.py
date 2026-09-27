"""Independent raw-gate and finite-orbit controls for the seed-period producer.

The tests do not invoke a native solver or count its separate proof replays.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from research.aiger_lfsr_v1.check import check as old_source_bound_check
from research.aiger_lfsr_v1.source_aware import odd_order
from research.proof_interface_v1.produce import Unsupported as LegacyUnsupported
from research.proof_interface_v1.produce import produce as legacy_produce
from .produce import Unsupported, factor_complete, produce

HERE = Path(__file__).resolve().parent
CASES = (
    ("rotation3", HERE / "models/rotation3.aag", 3, 4, 9),
    ("mixed5", HERE / "models/mixed5.aag", 5, 17, 63),
    ("original8", HERE.parent / "aiger_lfsr_v1/upstream/fibonacci-08-0xb8.aag", 8, 184, 255),
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def raw_model(raw):
    """Independent literal-list evaluator, with observed internal wire values."""
    lines = raw.decode("ascii").splitlines()
    tag, m, ni, nl, no, na = lines[0].split()
    m, ni, nl, no, na = map(int, (m, ni, nl, no, na))
    require(tag == "aag" and no == 1 and m == ni + nl + na, "bad emitted header")
    pos = 1
    inputs = [int(x) for x in lines[pos:pos+ni]]; pos += ni
    latches = [tuple(map(int, x.split())) for x in lines[pos:pos+nl]]; pos += nl
    output = int(lines[pos]); pos += 1
    gates = [tuple(map(int, x.split())) for x in lines[pos:pos+na]]; pos += na
    require(inputs == list(range(2, 2*ni+1, 2)), "bad input order")
    for i, rec in enumerate(latches):
        require(len(rec) in (2, 3) and rec[0] == 2*(ni+i+1), "bad latch order")
        require(len(rec) == 2 or rec[2] == 0, "nonzero initialization")
    for i, (lhs, a, b) in enumerate(gates):
        require(lhs == 2*(ni+nl+i+1) and 0 <= a < lhs and 0 <= b < lhs,
                "bad gate order")
    symbols = {}
    while pos < len(lines) and lines[pos] != "c":
        key, value = lines[pos].split(maxsplit=1)
        require(key not in symbols, "duplicate symbol")
        symbols[key] = value; pos += 1

    def evaluate(state, input_word):
        values = [0] * (m+1)
        for i, literal in enumerate(inputs):
            values[literal // 2] = (input_word >> i) & 1
        for i, rec in enumerate(latches):
            values[rec[0] // 2] = (state >> i) & 1
        def bit(literal):
            return values[literal // 2] ^ (literal & 1)
        for lhs, a, b in gates:
            values[lhs // 2] = bit(a) & bit(b)
        return sum(bit(rec[1]) << i for i, rec in enumerate(latches)), bit(output), values

    return ni, nl, symbols, evaluate


def literal_value(values, literal):
    return values[literal // 2] ^ (literal & 1)


def shift(n, taps, value):
    parity = sum((value >> j) & 1 for j in range(n) if taps >> j & 1) % 2
    return ((value << 1) & ((1 << n)-1)) | parity


def advance(n, taps, value, steps):
    for _ in range(steps):
        value = shift(n, taps, value)
    return value


def point_periods(n, taps):
    periods = []
    for seed in range(1 << n):
        value = shift(n, taps, seed)
        period = 1
        while value != seed and period <= (1 << n):
            value = shift(n, taps, value)
            period += 1
        require(value == seed and period <= (1 << n), "finite control has a transient")
        periods.append(period)
    return periods


def unpack(n, state):
    mask = (1 << n)-1
    return state & mask, (state >> n) & mask, (state >> (2*n)) & 1, state >> (2*n+1)


def invariant(n, taps, periods, state):
    r, seed, parity, phase = unpack(n, state)
    if r == seed == phase == 0:
        return True
    return bool(seed and phase < periods[seed] and parity == phase % 2
                and r == advance(n, taps, seed, phase))


def run():
    records = []
    all_period_checks = 0
    all_kernel_checks = 0
    exhaustive_checks = 0
    sampled_checks = 0
    preservation_checks = 0
    legacy_phase_unsupported = 0
    for name, path, n, taps, multiple in CASES:
        raw = path.read_bytes()
        old_result = old_source_bound_check(raw, taps, multiple)
        require(old_result["accepted"] and odd_order(n, taps), "existing decision baseline disagrees")
        try:
            legacy_produce(raw, taps)
            legacy_status = "candidate"
        except LegacyUnsupported:
            legacy_status = "unsupported_nonmaximal"
            legacy_phase_unsupported += 1
        witness, metadata = produce(raw, taps, multiple)
        _, old_l, _, original = raw_model(raw)
        _, new_l, symbols, augmented = raw_model(witness)
        width = multiple.bit_length()
        mask = (1 << n)-1
        phase_mask = (1 << width)-1
        require(new_l == old_l+width, "wrong phase width")
        for i in range(n):
            require(symbols[f"i{i}"] == f"= {2*(i+1)}", "input mapping differs")
        for i in range(old_l):
            require(symbols[f"l{i}"] == f"= {2*(n+i+1)}", "latch mapping differs")
        for i in range(width):
            require("=" not in symbols[f"l{old_l+i}"], "ghost latch is mapped")
        periods = point_periods(n, taps)
        for seed, expected in enumerate(periods):
            # Other state/input bits vary, so the raw period-wire observation is
            # not limited to the special r=s, phase=0 input to the producer.
            state = ((seed * 17 + 7) & mask) | seed << n
            state |= (seed & 1) << (2*n) | ((seed * 13 + 2) & phase_mask) << old_l
            _, _, values = augmented(state, (seed * 11 + 3) & mask)
            period = sum(literal_value(values, lit) << i
                         for i, lit in enumerate(metadata["period_literals"]))
            require(period == expected, "raw period circuit disagrees with independent orbit")
            all_period_checks += 1
            for control in metadata["kernel_factors"]:
                expected_fixed = advance(n, taps, seed, control["matrix_exponent"]) == seed
                require(literal_value(values, control["fixes_seed_literal"]) == expected_fixed,
                        "row-reduced raw kernel test differs from direct stepping")
                all_kernel_checks += 1

        if n == 3:
            assignments = ((state, inputs) for state in range(1 << new_l)
                           for inputs in range(1 << n))
        else:
            samples = [((i * 2654435761 + 97) & ((1 << new_l)-1),
                        (i * 29 + 3) & mask) for i in range(256)]
            seeds = range(1, 1 << n) if n == 5 else (1, mask, 0x55 & mask)
            for seed in seeds:
                value = seed
                for phase in range(periods[seed]):
                    state = value | seed << n | (phase % 2) << (2*n) | phase << old_l
                    samples.extend((state, inputs) for inputs in (0, 1, mask))
                    value = shift(n, taps, value)
            for parity in (0, 1):
                samples.extend((parity << (2*n), inputs) for inputs in (0, 1, mask))
            assignments = iter(samples)
        checked = 0
        for state, inputs in assignments:
            nxt, bad, _ = augmented(state, inputs)
            old_next, old_bad, _ = original(state & ((1 << old_l)-1), inputs)
            r, seed, _, phase = unpack(n, state)
            ghost_next = 0 if inputs or seed == 0 or shift(n, taps, r) == seed else (phase+1) & phase_mask
            require(nxt == old_next | ghost_next << old_l, "wrong emitted transition")
            h = invariant(n, taps, periods, state)
            require(bad == int(not h or old_bad), "wrong emitted strengthened property")
            if h:
                require(bad == 0 and invariant(n, taps, periods, nxt), "invariant is not inductive")
                preservation_checks += 1
            checked += 1
        if n == 3:
            exhaustive_checks += checked
        else:
            sampled_checks += checked
        records.append({"case": name, **metadata,
                        "existing_odd_exponent_checker_accepts": True,
                        "existing_squarefree_comparator_accepts": True,
                        "legacy_maximal_phase_producer_status": legacy_status,
                        "nonzero_period_histogram": dict(sorted(Counter(periods[1:]).items())),
                        "raw_transition_checks": checked,
                        "exhaustive_augmented_state_inputs": n == 3})

    negative_records = []
    for (name, path, n, taps, multiple), mutation in zip(CASES[:2], ("global_bound", "skip_repeated3")):
        raw = path.read_bytes()
        witness, metadata = produce(raw, taps, multiple, mutation=mutation)
        _, old_l, _, original = raw_model(raw)
        _, _, _, augmented = raw_model(witness)
        counterexample = None
        for seed in range(1, 1 << n):
            for phase in range(1 << multiple.bit_length()):
                value = advance(n, taps, seed, phase)
                state = value | seed << n | (phase % 2) << (2*n) | phase << old_l
                nxt, bad, _ = augmented(state, 0)
                _, next_bad, _ = augmented(nxt, 0)
                if bad == 0 and next_bad == 1:
                    _, original_bad, _ = original(state & ((1 << old_l)-1), 0)
                    _, original_next_bad, _ = original(nxt & ((1 << old_l)-1), 0)
                    counterexample = {"state": state, "input": 0, "next_state": nxt,
                                      "next_input": 0, "current_witness_bad": bad,
                                      "next_witness_bad": next_bad, "seed": seed, "phase": phase,
                                      "original_current_bad": original_bad,
                                      "original_next_bad": original_next_bad,
                                      "claim": "inductiveness counterexample, not an original reachable unsafe trace"}
                    break
            if counterexample is not None:
                break
        require(counterexample is not None, "false candidate lacked an inductiveness counterexample")
        negative_records.append({"case": name, **metadata, "counterexample": counterexample})

    rejected = 0
    raw3 = CASES[0][1].read_bytes()
    operations = [lambda value=value: produce(raw3, 4, value)
                  for value in (True, 0, -1, 2, 1 << 24, 1, 5)]
    operations += [lambda: produce(raw3, 5, 9),
                   lambda: produce(raw3, 4, 9, mutation="unknown"),
                   lambda: produce(raw3, 4, 3, mutation="skip_repeated3"),
                   lambda: produce(b"", 4, 9)]
    for operation in operations:
        try:
            operation()
        except Unsupported:
            rejected += 1
        else:
            raise RuntimeError("unsupported producer input accepted")
    require(factor_complete(1) == ((), 0), "empty factorization of one")
    return {"schema": 1, "circuits": records, "negative_witness_controls": negative_records,
            "all_seed_period_circuit_checks": all_period_checks,
            "all_seed_kernel_circuit_checks": all_kernel_checks,
            "exhaustive_augmented_transitions": exhaustive_checks,
            "sampled_augmented_transitions": sampled_checks,
            "invariant_transition_checks": preservation_checks,
            "existing_odd_exponent_checker_agreements": len(CASES),
            "existing_squarefree_comparator_agreements": len(CASES),
            "legacy_maximal_phase_producer_unsupported": legacy_phase_unsupported,
            "unsupported_producer_rejections": rejected,
            "native_proof_checks_performed_here": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
