# Targeted predecessor and interface comparison

Inspected 27 September 2026. This is a bounded comparison for the odd-order
witness contract, not a systematic literature review or a novelty claim.
The original workload and executed Certifaiger toolchain remain pinned in
[the preceding source dossier](../proof_interface_v1/SOURCES.md).

## Existing algebraic proof interfaces

Saccomani, Mohamed, Pertseva, Kaufmann, Tinelli, Barrett and Barbosa,
*Proof Production for Satisfiability Modulo Finite Fields with Proof Checking
in Pacheck and Lean*, FMCAD 2026, pp. 113–123,
[DOI 10.34727/2026/isbn.978-3-85448-093-8_17](https://doi.org/10.34727/2026/isbn.978-3-85448-093-8_17).
[Author PDF](https://danielakaufmann.at/publication/2026_fmcad/2026_FMCAD.pdf),
[university record](https://repositum.tuwien.at/handle/20.500.12708/230471),
[reviewed artifact](https://zenodo.org/records/20133205).

The paper's Sections III–V describe prime-field SMT refutations: instrumented
cvc5 produces Alethe proofs, Carcara checks surrounding SMT reasoning, and
FFPACHECK checks embedded algebraic proofs. The finite-field calculus supports
polynomial combinations and root branching, including reduction by field
equations. Its Lean reconstruction uses `ZMod p` with a primality premise.
The implementation does not directly support extension-field sorts. The
presented Lean root-completeness check enumerates field elements. These are
proof interfaces for field equations and disequations, not AIGER traces or
unbounded safety.

The artifact metadata describes a 4.6 GB x86 Docker archive, recommends 30 GB
disk, and estimates a ten-minute smoke run. Archive SHA256:
`8ab6cfd71baf3be2ce163c564565a0cbe31349c1364558b77e98cddfd03a6cb8`.
We inspected the paper, metadata and public source paths; we did not download
or execute this artifact and claim no measured cost comparison with it.

Public source pins inspected in this comparison:

| Component | Pin and relevant source | Boundary |
|---|---|---|
| Lean-SMT finite-fields branch | [`9b314968f6405395ecbc030c4d3f9b35e4974aa1`](https://github.com/ufmg-smite/lean-smt/tree/9b314968f6405395ecbc030c4d3f9b35e4974aa1), `Smt/Reconstruct/ZMod.lean`, `Smt/Translate/ZMod.lean`, `Test/Unit/ZMod.lean` | Lean/Mathlib v4.32.0; reconstruction selects native evaluation or kernel reduction through `useNative`. That setting must be recorded in an assurance claim. |
| Lean cvc5 dependency | [`abdoo8080/lean-cvc5`, `4733baf`](https://github.com/abdoo8080/lean-cvc5/blob/4733baf/lakefile.lean) | Downloads the author's `clean-wip` cvc5 release; the repository's earlier official cvc5 1.4.1 run is not this proof pipeline. |
| Carcara finite-fields branch | [`6e005a9b0093c9df7500cc11063f9c2fdc3afd7a`](https://github.com/psaccomani15/carcara/tree/6e005a9b0093c9df7500cc11063f9c2fdc3afd7a), `carcara/src/checker/shared.rs`, `carcara/src/checker/rules/finite_fields.rs` | The inspected dispatch passes PAC arguments to an external checker. Binding embedded arguments to outer premises/conclusions needs an integration test before claiming complete trust closure; this branch may differ from the reviewed artifact. No counterfeit test was performed. |

A matrix-power identity over F2 fits the prime-field semantics without
requiring a maximal-period Boolean phase predicate. A formal-polynomial
Bézout certificate needs coefficient equality: checking
`u(x) f(x) + v(x) f'(x) = 1` only at `x : F2` is insufficient. For example,
`x^2+x` vanishes on F2 but is a nonzero formal polynomial. Whether a restricted
PAC derivation without field-function reductions supplies the desired
polynomial-ring contract was not established here.

For either representation, connecting checked algebra to the original
arbitrary-input trace property still requires the generic odd-order safety
theorem and a checked source interpretation. A Lean formalization could make
that bridge explicit; adding this new bridge is substantial work, not a
capability already supplied by the finite-field SMT interface.

## Conventional algebra remains the comparator

The GAP FSR package documents primitive, irreducible and reducible period
computations, including the lcm of irreducible-factor orders and the
characteristic-power contribution from repeated factors:
[official manual, Section 2.2-4](https://nzidaric.github.io/fsr/doc/chap2.html).
Inspected source: [`nzidaric/fsr` commit
`1194c9d4a0fa9f170e47938439337481d248e618`](https://github.com/nzidaric/fsr/tree/1194c9d4a0fa9f170e47938439337481d248e618),
`lib/lfsr.gi`, blob `dc6882b8448489b8cc2d590cefed3f854d8b2d3b`.
`PeriodReducible` calls polynomial factorization, root order and lcm; the
top-level routine chooses special primitive/irreducible cases when applicable.
This is an existing algebraic computation, not an independently replayed
hardware-safety certificate. GAP was not run in this gate.

For the companion matrices here, nonzero constant coefficient plus a
squarefree polynomial already implies odd order. A squarefree method can
derive an odd annihilating exponent and use exactly the same power tests,
state-period predicate and witness interface as any full orbit method.
State-period divisibility tests `A^d s = s` are ordinary linear algebra.
Neither those tests nor the lcm rule become novel by appearing in a witness.
The earlier executed [SmokeRand comparison](../../audits/native_lfsr_v1/README.md)
separately rules out a general missing capability for maximal LFSR periods.

## History variables and loop observers

Abadi and Lamport, *The Existence of Refinement Mappings*, TCS 82(2), 1991,
pp. 253–284 (LICS 1988 version),
[author record](https://www.microsoft.com/en-us/research/publication/the-existence-of-refinement-mappings/),
[DOI 10.1016/0304-3975(91)90224-P](https://doi.org/10.1016/0304-3975(91)90224-P),
establishes auxiliary-state refinement methods. History variables remember
past information without changing original behavior; their use is longstanding.
The completeness result also needs prophecy variables and stated hypotheses,
so it does not assert that every useful invariant has a small history circuit.

Schuppan and Biere, *Efficient reduction of finite state model checking to
reachability analysis*, STTT 5, 2004, pp. 185–204,
[author preprint](https://www.schuppan.de/viktor/VSchuppanABiere-STTT-2004.pdf),
[DOI 10.1007/s10009-003-0121-x](https://doi.org/10.1007/s10009-003-0121-x).
Introduction and Section 2 explain saving a guessed loop-start state and
detecting its recurrence with an observer while leaving original behavior
unchanged; they also compare counter-based observers. This is a corrected,
extended successor to Biere–Artho–Schuppan's FMICS 2002 paper. The current
resetting parity monitor is a different concrete property, but recording
state and adding counters to prove temporal properties is not a new method.

The already executed Certifaiger model/witness interface is the direct
consumer for this gate. Kind 2 provides another established safety interface:
its [proof-certificate documentation](https://kind.cs.uiowa.edu/kind2_user_docs/v1.7.0/9_other/5_proofs.html)
specifies `(k, phi)` invariant certificates, SMT checks, LFSC invariance
rules, and optional frontend equivalence proofs. Its documented signatures
cover propositional reasoning, equality and linear arithmetic. This is not
evidence that Kind 2 accepts the finite-field PAC pipeline or an AIGER
odd-order theorem; no such integration was run.

## Original-state evaluation versus inference

Schnorr, *Security of Allmost ALL Discrete Log Bits*,
[ECCC TR98-033, 1998](https://eccc.weizmann.ac.il/report/1998/033/), explicitly
studies odd-order cyclic groups and shifted bits
`lsb(2^-i x mod q)`. Its abstract attributes odd-order least-significant-bit
security to Peralta (1985) and Long–Wigderson (1988). Thus relating a discrete
logarithm bit oracle to logarithm recovery is established cryptographic
reasoning. We inspected this primary abstract; the report's PDF text extraction
was unreliable, so we do not rely on uninspected internal theorem details.

Feldman, Immerman, Sagiv and Shoham, *Complexity and Information in Invariant
Inference*, POPL 2020, article 5,
[author preprint](https://arxiv.org/pdf/1910.12256),
[DOI 10.1145/3371073](https://doi.org/10.1145/3371073).
The introduction and model definition concern information-theoretic lower
bounds for finding polynomial-length invariants through black-box Hoare
queries. The model expressly excludes direct access to the transition code
and does not cover white-box abstract interpretation. This is a different
question from evaluating an already supplied original-state invariant, or
constructing a history witness with source-aware algebra.

The repository's phase-parity observation forces an evaluator of any adequate
original-state invariant to decide parity on designated same-orbit states.
Its potential conceptual distinction is that forced predicate, not the
classical bit-extraction reduction or the introduction of history state.
This targeted comparison does not establish novelty of that distinction.
It yields no unconditional circuit-size bound, no lower bound for general
invariant inference, and no cryptographic security claim for binary fields.

## Decision for this gate

Keep the existing Certifaiger interface for the bounded weaker-premise test.
Do not build another finite-field frontend merely to recheck algebraic
identities. Compare construction and replay under the same accepted witness
contract, with squarefree/structural methods allowed to emit the same witness.
If the remaining question is conceptual, investigate the exact original-state
evaluation/history distinction and its predecessors before adding more
formats or workloads. The available evidence supports an integration study;
it does not establish a new algebraic decision method or a research novelty.
