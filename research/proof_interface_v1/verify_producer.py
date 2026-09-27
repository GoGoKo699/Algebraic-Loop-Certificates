"""Independent finite controls for the untrusted AIGER witness producer.

This checks emitted raw gates, not Certifaiger's native SAT/LRAT obligations.
Native observations are recorded separately by the native-run owner.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .produce import Unsupported, maximality, produce

HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parent / "aiger_lfsr_v1" / "upstream"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def decode(raw):
    """Separate literal-list interpreter; no symbolic normalization or matrices."""
    lines = raw.decode("ascii").splitlines()
    tag, m, inputs, latches, outputs, gates = lines[0].split()
    m, inputs, latches, outputs, gates = map(int, (m, inputs, latches, outputs, gates))
    require(tag == "aag" and outputs == 1 and m == inputs + latches + gates,
            "emitted header is not canonical")
    pos = 1
    input_literals = [int(x) for x in lines[pos:pos+inputs]]
    pos += inputs
    latch_records = [tuple(map(int, x.split())) for x in lines[pos:pos+latches]]
    pos += latches
    output = int(lines[pos]); pos += 1
    and_records = [tuple(map(int, x.split())) for x in lines[pos:pos+gates]]
    pos += gates
    require(input_literals == list(range(2, 2*inputs+1, 2)), "input numbering")
    for i, rec in enumerate(latch_records):
        require(len(rec) in (2, 3) and rec[0] == 2*(inputs+i+1), "latch numbering")
        require(len(rec) == 2 or rec[2] == 0, "nonzero emitted reset")
    for i, (lhs, a, b) in enumerate(and_records):
        require(lhs == 2*(inputs+latches+i+1) and 0 <= a < lhs and 0 <= b < lhs,
                "gate numbering or topological order")
    symbols = {}
    while pos < len(lines) and lines[pos] != "c":
        name, value = lines[pos].split(maxsplit=1)
        require(name not in symbols, "duplicate emitted symbol")
        symbols[name] = value
        pos += 1

    def evaluate(state, input_word):
        values = [0] * (m+1)
        for i, literal in enumerate(input_literals):
            values[literal // 2] = (input_word >> i) & 1
        for i, rec in enumerate(latch_records):
            values[rec[0] // 2] = (state >> i) & 1
        def bit(literal):
            return values[literal // 2] ^ (literal & 1)
        for lhs, a, b in and_records:
            values[lhs // 2] = bit(a) & bit(b)
        return sum(bit(rec[1]) << i for i, rec in enumerate(latch_records)), bit(output)

    return inputs, latches, symbols, evaluate


def shift(n, taps, value):
    bit = sum((value >> j) & 1 for j in range(n) if (taps >> j) & 1) % 2
    return ((value << 1) & ((1 << n)-1)) | bit


def unpack(n, state):
    mask = (1 << n)-1
    return state & mask, (state >> n) & mask, (state >> (2*n)) & 1, state >> (2*n+1)


def invariant(n, taps, state):
    r, s, c, phase = unpack(n, state)
    if r == s == phase == 0:
        return True
    if s == 0 or phase >= (1 << n)-1 or c != phase % 2:
        return False
    value = s
    for _ in range(phase):
        value = shift(n, taps, value)
    return r == value


def phase_next(n, taps, state, inputs):
    r, s, _, phase = unpack(n, state)
    if inputs or s == 0 or shift(n, taps, r) == s:
        return 0
    return (phase + 1) & ((1 << n)-1)


def run():
    records = []
    exhaustive_transitions = 0
    sampled_transitions = 0
    invariant_transitions = 0
    finite_period_states = 0
    for n, taps in ((2, 3), (3, 6), (4, 12), (8, 184)):
        path = next(UPSTREAM.glob(f"fibonacci-{n:02}-*.aag"))
        raw = path.read_bytes()
        witness, metadata = produce(raw, taps)
        _, old_l, _, model = decode(raw)
        got_n, new_l, symbols, augmented = decode(witness)
        require(got_n == n and new_l == old_l+n, "wrong extension interface")
        for i in range(n):
            require(symbols[f"i{i}"] == f"= {2*(i+1)}", "input correspondence")
        for i in range(old_l):
            require(symbols[f"l{i}"] == f"= {2*(n+i+1)}", "latch correspondence")
        for i in range(n):
            require("=" not in symbols[f"l{old_l+i}"], "ghost must be unmapped")

        # An independent finite cycle check validates the arithmetic producer
        # diagnostics on these small controls, without trusting source labels.
        orbit = set()
        point = 1
        while point not in orbit:
            require(point != 0, "nonzero orbit reached zero")
            orbit.add(point)
            point = shift(n, taps, point)
        require(point == 1 and len(orbit) == (1 << n)-1, "maximality diagnostic wrong")
        finite_period_states += len(orbit)

        if n <= 3:
            assignments = ((s, u) for s in range(1 << new_l) for u in range(1 << n))
        else:
            mask = (1 << n)-1
            samples = [((i * 2654435761 + 97) & ((1 << new_l)-1),
                        (i * 29 + 3) & mask) for i in range(256)]
            # Exercise the powered-vector expression on positive phase states,
            # not only on random assignments outside the invariant.
            for seed in (1, mask, 0x55 & mask):
                value = seed
                for phase in range(mask):
                    state = value | seed << n | (phase % 2) << (2*n) | phase << old_l
                    samples.extend((state, u) for u in (0, 1, mask))
                    value = shift(n, taps, value)
            for counter in (0, 1):
                samples.extend((counter << (2*n), u) for u in (0, 1, mask))
            assignments = iter(samples)
        checked = 0
        for state, inputs in assignments:
            nxt, bad = augmented(state, inputs)
            original_next, original_bad = model(state & ((1 << old_l)-1), inputs)
            expected_next = original_next | (phase_next(n, taps, state, inputs) << old_l)
            h = invariant(n, taps, state)
            require(nxt == expected_next, "emitted transition differs from raw model/ghost contract")
            require(bad == int(not h or original_bad), "emitted strengthened output differs")
            if h:
                require(bad == 0 and invariant(n, taps, nxt), "phase invariant not inductive")
                invariant_transitions += 1
            checked += 1
        if n <= 3:
            exhaustive_transitions += checked
        else:
            sampled_transitions += checked
        records.append({**metadata, "raw_transition_checks": checked,
                        "exhaustive_augmented_state_inputs": n <= 3})

    raw4 = (UPSTREAM / "fibonacci-04-0xc.aag").read_bytes()
    _, old_l, _, original = decode(raw4)
    mutants = []
    for mutation, inputs in (("freeze_phase", (1, 0, 0)),
                             ("inverted_phase", (1, 0))):
        witness, metadata = produce(raw4, 12, mutation=mutation)
        _, _, _, evaluate = decode(witness)
        state = 0
        trace = []
        for value in inputs:
            nxt, bad = evaluate(state, value)
            _, original_bad = original(state & ((1 << old_l)-1), value)
            trace.append({"state": state, "input": value,
                          "witness_bad": bad, "original_bad": original_bad})
            state = nxt
        require(any(row["witness_bad"] for row in trace), "wrong-phase control has no failing trace")
        require(not any(row["original_bad"] for row in trace), "mutant changed original safety property")
        mutants.append({**metadata, "raw_witness_counterexample": trace})

    rejected = 0
    operations = [lambda: maximality((1, 2)), lambda: maximality((2, 1)),
                  lambda: produce(raw4, 13), lambda: produce(raw4, 12, mutation="unknown"),
                  lambda: produce(b"", 12)]
    for operation in operations:
        try:
            operation()
        except Unsupported:
            rejected += 1
        else:
            raise RuntimeError("unsupported producer input accepted")
    return {"schema": 1, "circuits": records,
            "exhaustive_augmented_transitions": exhaustive_transitions,
            "sampled_augmented_transitions": sampled_transitions,
            "invariant_transition_checks": invariant_transitions,
            "independent_finite_period_states": finite_period_states,
            "negative_witness_controls": mutants, "unsupported_producer_rejections": rejected,
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
