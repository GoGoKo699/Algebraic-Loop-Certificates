# Odd-order safety through the existing witness interface

This checkpoint removes the maximal-period assumption from the previous
history-witness construction. Given an odd exponent M with A^M=I, the producer
builds a circuit for each seed's exact period from the complete factorization
of M. The history predicate uses this seed-dependent bound. M need not be the
least matrix order, and different nonzero seeds may have different periods.

The output is an ordinary Certifaiger witness. No new checker rule is needed.
See [CONTRACT.md](CONTRACT.md), [THEORY.md](THEORY.md), the frozen
[native protocol](NATIVE_PROTOCOL.md), the [source comparison](SOURCES.md), and
the project decision in [gate 12](../ODD_ORDER_WITNESS_GATE_12.md).

## Executed result

All three positive witnesses passed all nine native obligations. Both false
period selectors failed Inductive. The 27 positive proofs and ten completed
proofs preceding those failures independently replay: **37 CNF proofs total**.
No planned case timed out or returned UNKNOWN.

| Case | Source | Odd M | Nonzero seed periods | Witness bytes | Raw LRAT bytes | Construction seconds | Native replay seconds |
|---|---|---:|---|---:|---:|---:|---:|
| rotation3 | Synthetic wrapper control | 9 | 1, 3 | 1,920 | 27,776 | 0.0410 | 0.0793 |
| mixed5 | Synthetic wrapper control | 63 | 3, 7, 21 | 4,937 | 587,449 | 0.0379 | 0.1117 |
| published8 | Unchanged published circuit | 255 | 255 | 11,872 | 24,898,388 | 0.0436 | 3.3326 |

Construction includes a fresh Python process, imports, factorization, algebra,
circuit construction and file output. Native replay includes obligation
generation, CNF conversion, SAT search and native LRAT checking. Tool builds,
synthetic model emission and the later independent Python proof replay are
separate. These are single observations, not a speedup or scaling experiment.
The published 8-bit proof is still about 25 MB despite a 12 KB witness.

The global-bound counterfeit on rotation3 fails after 0.0499 seconds; omitting
the repeated-prime test on mixed5 fails after 0.0570 seconds. These are invalid
inductive certificates for safe models, not source counterexamples.
`native/CONSTRUCTION.json`, per-case `RESULTS.json`, and `ARTIFACTS.json` retain
exact timings, logs, sizes and raw/stored hashes. Large files use deterministic
gzip. `EXECUTION.json` records the local pre-execution freeze; the source,
protocol and candidate bytes are also bound by `BUILD_PROVENANCE.json`.

## Independent checks

The mathematical verifier enumerates all 109 odd-order binary matrices in
dimensions 1 through 3, checking 2,562 seed periods and 87,534 history edges.
An independent synthetic-model emitter checks 66,560 raw state/input cases.
The producer audit checks 296 seed-period circuits, 880 fixed-space predicates,
16,384 exhaustive augmented transitions, 4,316 additional transitions, and
3,972 invariant-preservation cases. Both wrong selectors have explicit
inductiveness counterexamples. None is presented as an unsafe reachable trace.

The independent LRAT checker is unchanged from gate 11 and imports no producer
or solver. It proves unsatisfiability of the retained CNFs. Native obligation
construction and AIGER-to-CNF translation remain trusted. The checkpoint replay
also regenerates candidates to check reproducibility; that regeneration is not
the acceptance argument for their safety.

## Run

From the repository root, without downloads or native tools:

```sh
python -m research.odd_order_witness_v1.verify
```

This command is included in `python verify.py`. To generate a new candidate:

```sh
python -m research.odd_order_witness_v1.produce \
  --model research/odd_order_witness_v1/models/mixed5.aag \
  --taps 0x11 --odd-multiple 63 --output /tmp/mixed5-witness.aag
```

The producer refuses to overwrite files. Construction does not mean acceptance.
Native execution requires the separately built pinned tools and frozen protocol.
The implementation supports only the recognized wrapper, widths 2 through 24,
and positive odd M below 2^24. Exact trial division obtains the factorization;
the conditional polynomial circuit bound does not make factoring free.

## Decision

The weaker-premise integration succeeds. Order extraction from a factored
multiple and history variables are established techniques; a conventional
source-aware route can emit the same witness. The two synthetic controls do
not supply a new benchmark advantage. Originality and consequential benefit
remain unresolved. The next research task concerns the precise original-state
evaluation versus added-history distinction and its predecessors, not another
algebraic format or a larger synthetic corpus.
