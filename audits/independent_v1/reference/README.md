# Algebraic Loop Certificates

**Discover a loop summary. Check its proof independently. Reuse the result without replaying the loop.**

This research repository studies exact summaries for invertible linear and affine recurrences. The current implementation uses **prime fields** and a specified initial state and full-state target. A verified positive answer describes every hit time as one arithmetic progression. Negative answers carry explicit evidence; exhausting a computation budget means **unknown**, not unreachable.

**Status:** working, independently checked reference implementation. The mathematics is established; a new algorithmic contribution, production performance advantage, and quantum advantage have not been established. Manuscript preparation is on hold. This classical spinoff has no quantum backend requirement and no selected journal.

## Try a complete verified example

Python 3.10 or later; no third-party runtime dependencies. Run from the repository root:

```sh
python verify.py
python -m alc check examples/fibonacci.json examples/fibonacci.certificate.json
python -m alc query examples/fibonacci.json examples/fibonacci.certificate.json --low 0 --high 100
python examples/consumer_demo.py
```

Over the field with seven elements, the recurrence is

$$
\begin{pmatrix}x_{t+1}\\y_{t+1}\end{pmatrix}
=
\begin{pmatrix}1&1\\1&0\end{pmatrix}
\begin{pmatrix}x_t\\y_t\end{pmatrix},\qquad
(x_0,y_0)=(1,0).
$$

The target `(4,5)` occurs exactly at **11, 27, 43, 59, ...**: offset 11 and least period 16. The certificate proves the target hit, proves the return at 16, and excludes the necessary smaller period. The query above returns **six** hits in the inclusive interval `[0,100]`.

The consumer demo verifies a second affine clock, combines the two schedules, and counts simultaneous hits through `10^30` using integer arithmetic. It does not simulate that many iterations. This is a demonstration of the summary interface, **not** a benchmark against a competent classical analyzer.

To generate a new certificate with the bounded reference producer:

```sh
python -m alc produce examples/fibonacci.json --output /tmp/alc-new-certificate.json
```

The output must not already exist. The CLI verifies its own candidate before writing a certificate. It exits with code 3, without a certificate, when the producer exhausts its limit. Use `python -m alc --help` for the interface.

## What is trusted, and what is not?

| Component | Responsibility | Boundary |
|---|---|---|
| [Producer](alc/producers.py) | Find evidence | Uses bounded orbit enumeration and trial arithmetic; no fast order/discrete-log algorithm is claimed. |
| [Checker](alc/checker.py) | Validate evidence against the exact input | Imports no producer or search code. Checks primality, field semantics, invertibility, witness equations, and instance binding. |
| [Consumers](alc/consumers.py) | Count hits, find the next hit, intersect schedules | Operate on verified summaries. Synchronization is not arbitrary program composition. |

The checker uses integer arithmetic, not numerical tolerances. Period factors come with recursively checkable Lucas/Pratt primality proofs; neither a factor label nor a probable-prime claim is trusted. This is a reference implementation, **not a formally verified checker or hardened public service**.

## Evidence supported today

A **hit certificate** proves the complete arithmetic progression. An **outside-span certificate** proves that a linear functional annihilates all reachable states but not the target. A **cycle-exclusion certificate** lists a complete closed trajectory containing no target; its size and checking time grow with the trajectory, so it is not a compact general solution to unreachability.

The bundled [examples](examples/README.md) cover all three forms. The tests check **4,834 state/target cases across 100 small recurrences**, **6,084 schedule intersections**, malformed inputs, altered periods, composite-modulus controls, and resource exhaustion. See [the recorded scope](reports/expected.json) and [reproducibility instructions](docs/REPRODUCIBILITY.md). These are newly run bootstrap tests, not a replay of the unavailable original scout archive.

## Read the research

Start with [the specification and proofs](docs/SPECIFICATION.md), then [the prior-work and contribution audit](docs/PRIOR_WORK.md). The [current research task](work_orders/CURRENT.md) prioritizes a defensible contribution and a useful consumer before manuscript work.

This implementation does **not** cover extension-field encodings, ordinary machine-word overflow, singular recurrences with transients, noisy inputs, arbitrary guards, or uncontrolled program branches. A point target is not a general safety predicate. Large example horizons do not establish faster discovery. The original quantum-discovery project remains separate.

## Origin and collaboration

The idea arose during [Quantum-Assisted Algorithm Discovery](https://github.com/GoGoKo699/Quantum-Assisted-Algorithm-Discovery). The published predecessor note is preserved byte-for-byte, with pinned provenance. The original conversation ZIP is not currently available for import; it has not been reconstructed or represented as preserved. [Provenance](provenance/README.md) distinguishes the authentic source snapshot, the missing archive, and newly written code.

Manuscript writing is on hold. For collaboration, questions, or corrections, contact **Ruge Lin** at **gogoko699@gmail.com**.

## License

[MIT](LICENSE), Copyright (c) 2026 Ruge Lin. The repository's original license is unchanged.
