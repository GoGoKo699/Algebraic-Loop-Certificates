# An existing LFSR safety workload with a small algebraic proof

This is a source-bound integration experiment for an existing third-party
model-checking workload. It does not establish new algebra, a new orbit
algorithm, a performance advantage over source-aware methods, or proof-assistant
replay. Manuscript preparation remains on hold.

The [upstream corpus](upstream/README.md) consists of hand-designed AIGER safety
tasks for testing and limited benchmarking of model checkers. We preserve its
23 `lfsr-period` tasks, widths 2 through 24, at commit
`c8efd0251c0548dd46168db8410e6777c5f82b73`, including the original
[MIT license](upstream/LICENSE). These are existing crafted verification tasks,
not industrial designs or tasks newly inflated for this project.

Each original circuit permits a new nonzero seed on every clock. It reports an
error if the running shift register becomes zero, or if its return period is
even. The original semantics, including arbitrary reseeding, the immutable seed
copy, the parity counter, and the output detector, are retained.

The useful simplification is that this task needs only **an odd exponent M with
A^M = I**. It does not need a least period, maximal period, factorization,
primitive-polynomial proof, or full orbit membership. Our independent checker
first binds the raw AAG gates to the precise documented wrapper, then checks the
odd matrix exponent with exact binary arithmetic. A different valid circuit
encoding may be unrecognized; rejection is inconclusive.

Run from the repository root:

```sh
python -m research.aiger_lfsr_v1.verify
```

The deterministic result is preserved in [expected.json](expected.json):

- All 23 original raw circuits are accepted with M = 2^n - 1.
- A conventional source-aware squarefree-polynomial decision agrees on all 23.
- An independent literal evaluator checks every state/input transition of the
  width-2, -3, and -4 circuits: 9,344 transitions, including unreachable states.
- Independent finite-state exploration checks the wrapper theorem for all 530
  binary matrices of dimensions 1, 2, and 3. Identity and even-period swap
  controls are explicit.
- Sixty small companion maps check the squarefree criterion against cycle
  enumeration. Deliberate malformed certificates and circuit mutations are
  rejected; three mutated raw circuits also have independently found unsafe
  traces. A 5,000-gate shared-DAG regression covers a discovered resource issue.

The squarefree comparator is a substantive limitation on the claim:
[source_aware.py](source_aware.py) decides this extracted companion-matrix
obligation without a supplied exponent. It is a simpler ordinary algebraic
baseline, not a claim that the full orbit engine is needed. The fixed native
ABC/PDR run reported SAFE for widths 2 and 4 and reached the 10-second wall limit
for widths 8, 12, 16 and 24. Those four outcomes are UNKNOWN, not unsafety or
evidence about every model checker. Read the [native record](native/README.md)
and [frozen protocol](NATIVE_PROTOCOL.md). This limited comparison does not
remove the stronger source-aware comparator or establish a novel algorithm.

See [CONTRACT.md](CONTRACT.md) for acceptance and trust boundaries,
[THEORY.md](THEORY.md) for the proof, and [SOURCES.md](SOURCES.md) for provenance.
