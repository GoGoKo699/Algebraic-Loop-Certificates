#!/usr/bin/env python3
"""Untrusted format adapter: ABC blocked-cube PLA -> Certifaiger witness.

The original inputs, latches, initial values, and next-state rows are retained.
Only the property is strengthened to the disjunction of blocked latch cubes.
An external checker must validate the witness against the original circuit.
"""
import argparse
import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def convert(model, pla, output):
    need(not output.exists(), "Refusing to overwrite witness")
    lines = model.read_text().splitlines()
    header = lines[0].split()
    need(header[0] == "aag" and len(header) == 6, "Requires basic AAG")
    maximum, ni, nl, no, na = map(int, header[1:])
    need(no == 1 and maximum == ni + nl + na, "Expected one bad output and dense source")
    inputs = [int(v) for v in lines[1:1+ni]]
    latch_rows = lines[1+ni:1+ni+nl]
    latches = [int(row.split()[0]) for row in latch_rows]
    old_gates = lines[1+ni+nl+no:1+ni+nl+no+na]
    symbols = {}
    for line in lines[1+ni+nl+no+na:]:
        if line == "c":
            break
        if line.startswith("l"):
            name, label = line.split(" ", 1)
            symbols[int(name[1:])] = label
    fields = {}
    cubes = []
    for line in pla.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("."):
            parts = line.split()
            fields[parts[0]] = parts[1:]
            continue
        bits, value = line.split()
        need(value == "1" and len(bits) == nl and set(bits) <= set("01-"), "Malformed blocked cube")
        cubes.append(bits)
    need(fields.get(".i") == [str(nl)], "PLA does not cover every latch")
    need(fields.get(".o") == ["1"] and fields.get(".p") == [str(len(cubes))], "PLA header mismatch")
    need(fields.get(".ilb") == [symbols[i] for i in range(nl)], "PLA latch ordering differs")
    new_gates = []

    def conjunction(a, b):
        nonlocal maximum
        if a == 0 or b == 0:
            return 0
        if a == 1:
            return b
        if b == 1:
            return a
        maximum += 1
        lit = 2 * maximum
        new_gates.append(f"{lit} {a} {b}")
        return lit

    bad = 0
    for cube in cubes:
        term = 1
        for bit, latch in zip(cube, latches):
            if bit != "-":
                term = conjunction(term, latch ^ (bit == "0"))
        bad = conjunction(bad ^ 1, term ^ 1) ^ 1
    output.write_text("\n".join([
        f"aag {maximum} {ni} {nl} 1 {na+len(new_gates)}",
        *map(str, inputs), *latch_rows, str(bad), *old_gates, *new_gates,
        *(f"i{i} = {lit}" for i, lit in enumerate(inputs)),
        *(f"l{i} = {lit}" for i, lit in enumerate(latches)),
        "o0 blocked_by_ABC_invariant", "c",
        "Untrusted witness adapted from ABC PLA; validate against original model.",
    ]) + "\n")
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    return {"model": str(model), "model_sha256": digest(model), "pla": str(pla), "pla_sha256": digest(pla), "witness": str(output), "witness_sha256": digest(output), "latches": nl, "blocked_cubes": len(cubes), "original_gates": na, "added_gates": len(new_gates)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model", type=Path)
    parser.add_argument("pla", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(convert(args.model, args.pla, args.output), indent=2))
