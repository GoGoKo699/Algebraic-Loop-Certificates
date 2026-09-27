# Algebraic Loop Certificates

**Exact summaries and independently checkable certificates for finite-field recurrences.**

A loop may run for an enormous number of iterations while its visits to one target have a short description:

$$
\{t\geq0:x_t=b\}=\{t_0+jr:j\geq0\}.
$$

This project separates **finding that description**, **checking its proof**, and **using it**. A producer may be slow or untrusted. The checker does not enumerate the orbit, search for a discrete logarithm, or factor an integer: it checks supplied witnesses using exact arithmetic. A verified summary supports time-window and schedule calculations without replaying the loop.

**Status:** working research prototype, not a new fast classical orbit algorithm, a quantum-advantage result, or a production program verifier. The [current contribution assessment](research/CONTRIBUTION_ASSESSMENT_08.md) treats the algebraic engine as a certifying implementation of established structure. A [native-verifier gate](research/VERIFICATION_GATE_09.md) found no capability gap for the tested supplied-invariant task. A [circuit-integration result](research/NATIVE_WORKLOAD_GATE_10.md) checks an odd-order safety argument against 23 published AIGER circuits, including their reseeding logic. The [latest proof-interface gate](research/PROOF_INTERFACE_GATE_11.md) replays history witnesses through Certifaiger and independently checked SAT proofs at widths 2, 4 and 8. Research originality and a consequential advantage over source-aware alternatives remain unestablished. Manuscript preparation is on hold.

## Try a complete example

Requires Python 3.10 or later. The commands run directly from a checkout with no third-party runtime dependencies.

```sh
python -m alc verify --problem examples/fibonacci_f7/problem.json --certificate examples/fibonacci_f7/certificate.json
python -m alc query --problem examples/fibonacci_f7/problem.json --certificate examples/fibonacci_f7/certificate.json --from 1000000000000000000000000000000 --through 1000000000000000000000000000100
```

The recurrence is `(x,y) -> (x+y,x) mod 7`, starting at `(1,0)`, with target `(4,5)`. The checker establishes the **complete** hit set `11 + 16j`, not just one observed hit. The second command reports six hits in the inclusive interval: the first is `10^30 + 11` and the last is `10^30 + 91`.

To regenerate a candidate, choose a new output path:

```sh
python -m alc produce --problem examples/fibonacci_f7/problem.json --output /tmp/fibonacci-candidate.json --max-steps 1000
python -m alc verify --problem examples/fibonacci_f7/problem.json --certificate /tmp/fibonacci-candidate.json
python verify.py
```

The producer uses bounded classical enumeration and trial division. It refuses to overwrite a file. Exhausting its budget is **inconclusive**, never a proof of unreachability.

## Read in this order

| Document | What it establishes |
|---|---|
| [Mathematical specification and proof](docs/SPECIFICATION.md) | Exact domain, complete positive-hit theorem, and the role of primality proofs |
| [Certificate and command-line interface](docs/FORMAT.md) | Trusted input, untrusted certificate, validation rules, exit codes, and limits |
| [Research assessment](docs/RESEARCH.md) | Prior work, current contribution boundary, and the next substantive research question |
| [Research modules and latest decisions](research/README.md) | Experimental complete certificates, reusable recognizers, comparison audits, and the failed application-benefit gate |
| [Verification record](evidence/README.md) | Finite families actually checked and what was not tested |
| [Origin and import status](provenance/ORIGIN.md) | Relationship to the quantum project and the unavailable earlier ZIP |
| [Current work order](work_orders/CURRENT.md) | Scope for the next research session |

## Supported now

The production `alc/` implementation covers invertible linear and affine maps `x -> A x + c` over **prime fields** `F_p`, with a supplied initial state and a **full-state target**. It checks the modulus by a Lucas-Pratt proof, matrix invertibility by an inverse witness, and the least point period using a complete proved-prime factorization. The certificate is bound to a separately supplied canonical problem document.

Extension fields, composite-modulus arithmetic, machine-word overflow, singular maps with transient tails, arbitrary guards, and general negative certificates are **not implemented**. The mathematics can be discussed more broadly than this implementation; unsupported encodings are rejected, not silently reinterpreted.

That boundary applies to the production `alc/` API. Separate [research modules](research/README.md) implement complete point-orbit certificates and reusable source recognizers, including scoped modular extensions. Their contracts and evidence do not silently broaden the production API.

A positive certificate says nothing about whether the recurrence was faithfully extracted from a larger program. That extraction and the trusted problem specification are outside the current checker.

## Repository structure

`alc/producer.py` creates candidate proofs. `alc/checker.py` is independent of the producer and performs no discovery. `alc/consumer.py` uses accepted summaries. `tests/` includes independently stepped orbits and deliberately false proofs. `examples/` contains linear, affine, and fixed-point cases. GitHub Actions runs the same local verifier.

The first milestone is a reproducible producer-checker-consumer interface with explicit trust boundaries. It is not an acceptance claim for a future paper. In particular, the finite-field orbit reduction and loop acceleration precede this project; see the [source-by-source assessment](docs/RESEARCH.md).

## Relationship to the original project

This is an independent classical spinoff of [Quantum-Assisted Algorithm Discovery](https://github.com/GoGoKo699/Quantum-Assisted-Algorithm-Discovery). A quantum producer could supply certificates later, but neither the checker nor the consumer requires quantum hardware. The original project and its research branches are unchanged.

[MIT license](LICENSE), Copyright (c) 2026 Ruge Lin. The license supplied when this repository was created is preserved byte-for-byte.
