# Primary sources for the bounded exporter assessment

Inspected 27 September 2026. This dossier supports
[Gate 18](../CONTRIBUTION_ASSESSMENT_18.md). It records a targeted comparison,
not an exhaustive novelty search. No external experiment was reproduced.

## Scope and read depth

Starting from the existing Certifaiger/HWMCC and LFSR dossiers, the audit used
primary-paper title searches, backward/forward citation tracing, and combinations
of LFSR, algebraic verification, witness circuits, history, seed period, and
sequential verification. Broad keyword results were often irrelevant. The
assessment rests on the specified definitions, constructions and evaluation
sections below, not on search-result absence. Reading those sections is not an
independent reconstruction of every proof in each paper.

Gates [08](../CONTRIBUTION_ASSESSMENT_08.md),
[12](../ODD_ORDER_WITNESS_GATE_12.md) and
[13](../INVARIANT_HISTORY_GATE_13.md) remain the earlier algebra/order and
inverse-bit assessments. This dossier focuses on the surviving exporter claim.
All descriptions below are paraphrases; papers are linked, not vendored.

## S1 — Witness-circuit certification

Yu, Biere and Heljanko, *Progress in Certifying Hardware
Model Checking Results*, CAV 2021, pp. 363–386.
[Primary PDF](https://cca.informatik.uni-freiburg.de/papers/YuBiereHeljanko-CAV21.pdf).
DOI: 10.1007/978-3-030-81688-9_17.

Read §2 Definition 6 and §§3–4. Original-model binding, bookkeeping state and
an inductive invariant already form a separately checked witness circuit.
Its conditions and construction establish the generic architecture preceding
this repository. The exact odd-order seed-period selector is not supplied by
the inspected construction.

## S2 — Stratified resets and history

Yu, Froleyks, Biere and Heljanko, *Stratified
Certification for k-Induction*, FMCAD 2022, pp. 59–64.
[Primary PDF](https://cca.informatik.uni-freiburg.de/papers/YuFroleyksBiereHeljanko-FMCAD22.pdf).
DOI: 10.34727/2022/isbn.978-3-85448-053-2_11.

Read §III, Definitions 6–10, pp. 60–61. Acyclic reset dependencies permit SAT
checks; the witness records past state/input copies and initialization state.
Neither stratified resets nor history-bearing witness generation is a new
general mechanism here. This paper addresses k-induction certification, not
the specific reseeding LFSR construction.

## S3 — Transfer across preprocessing

Yu, Froleyks, Biere and Heljanko, *Towards
Compositional Hardware Model Checking Certification*, FMCAD 2023, pp. 44–54.
[Primary PDF](https://cca.informatik.uni-freiburg.de/papers/YuFroleyksBiereHeljanko-FMCAD23.pdf).
DOI: 10.34727/2023/isbn.978-3-85448-060-0_12.

Read the certificate constructions on PDF pp. 6–7: Definition 13/Theorem 2
and Definition 14/Theorem 3. Composite and backward witnesses support transfer
of certification across temporal decomposition to the original model.
Generic original-model certificate recovery is therefore established prior work;
these constructions do not identify the exact seed-period compiler.

## S4 — Folded witnesses explicitly retain history

Froleyks, Yu, Biere and Heljanko, *Certifying Phase
Abstraction*, IJCAR 2024, pp. 284–303.
[Primary PDF](https://cca.informatik.uni-freiburg.de/papers/FroleyksYuBiereHeljanko-IJCAR24.pdf),
[author preprint](https://arxiv.org/html/2405.04297v1).
DOI: 10.1007/978-3-031-63498-7_17.

Read §§5.1–5.2, Definitions 9–11 and Theorem 4, especially the folded witness
with original-latch history copies. This directly precedes generic history
export into the existing certificate interface. The paper's periodic-signal
phase abstraction and preprocessing differ from our seed-dependent orbit-phase
counter; the shared word “phase” does not establish an exact duplicate.

## S5 — An established consumer and complete-workflow evaluation

Froleyks, Yu, Preiner, Biere and Heljanko,
*Introducing Certificates to the Hardware Model Checking Competition*,
CAV 2025, pp. 281–295.
[Primary PDF](https://cca.informatik.uni-freiburg.de/papers/FroleyksYuPreinerBiereHeljanko-CAV25.pdf).
DOI: 10.1007/978-3-031-98668-0_14.

Read §3 Definition 1/Theorem 1 and §§4.1–4.3. The existing consumer checks
original/witness relations, safety and reset stratification; evaluation includes
solving and checking costs, witness size and invalid-certificate treatment.
This supports the consumer requirement, not a claim that our corpus is part
of that competition evaluation or that our repository has industrial adoption.

## S6 — The comparator's broader scope

Su, Yang, Ci, Bu and Huang, *The rIC3 Hardware
Model Checker*, CAV 2025, pp. 185–199.
[Primary chapter](https://link.springer.com/chapter/10.1007/978-3-031-98668-0_9).
DOI: 10.1007/978-3-031-98668-0_9.

Read §§2–4, §7.1 and §8. The tool includes preprocessing and multiple engines
and configurations, including a multithreaded portfolio and a separate
single-thread setting. Arithmetic limitations are discussed. Our qualified
single-worker IC3 command is one fixed comparator, not an evaluation of every
published rIC3 configuration. No portfolio rerun or budget change belongs to
this assessment.

## S7 — Certifaiger's checking and trust architecture

Froleyks and Yu, *Hardware Model Checking Certification with
Certifaiger and Cerbtora*, IJCAR 2026, pp. 276–285.
[Author PDF](https://froleyks.de/assets/pdf/Froleyks%20et%20al.%20-%202026%20-%20Hardware%20Model%20Checking%20Certification%20with%20Certifaiger%20and%20Cerbtora.pdf).
DOI: 10.1007/978-3-032-32589-1_17.

Read §§2–3, including the trust-base discussion, pp. 279–281. Mapping,
obligation splitting, CNF conversion and optional DRAT/LRAT checking are existing
tool architecture. Our independently replayed CNF evidence does not verify
those transformations. This paper's five safety conditions must not replace
the nine concrete obligations emitted by the version pinned in our protocol.

## S8 — Specialized certified coverage beyond rIC3

Seufert and Scholl, *Certified Sequential Sweep Without
Unrolling*, FMCAD 2026, pp. 472–484.
[Primary proceedings PDF](https://repositum.tuwien.at/bitstream/20.500.12708/230516/1/Seufert-2026-Certified%20Sequential%20Sweep%20Without%20Unrolling-vor.pdf).
DOI: 10.34727/2026/isbn.978-3-85448-093-8_51.

Read §§IV-D–IV-E and §V, pp. 478–482. The construction transfers a retimed
invariant to the original equivalence miter and uses Certifaiger. Its evaluation
already demonstrates specialized certifying coverage beyond a rIC3 portfolio.
This is a close methodological predecessor to the generic contribution pattern.
It concerns sequential equivalence, different circuit families, and different
resource settings; no numerical comparison with our timings is valid. The
inspected construction is not the reseeding seed-period exporter.

## S9 — Sequential finite-field algebraic verification

Sun, Kalla, Pruss and Enescu, *Formal Verification
of Sequential Galois Field Arithmetic Circuits Using Algebraic Geometry*,
DATE 2015, pp. 1623–1628.
[Primary PDF](https://past.date-conference.com/proceedings-archive/2015/pdf/0158.pdf).

Read §§I and V–VII. Polynomial representations and Gröbner-basis elimination
exploit sequential finite-field structure. The contract is a k-cycle arithmetic
implementation of a word-level specification, not the original unbounded
arbitrary-reseeding odd-return safety task. This precedes the broad algebraic
verification idea; its reported performance does not transfer to our workload.

## S10 — Specialized LFSR verification in an application

Auerbach, Copty and Paruthi, *Formal Verification of Arbiters
using Property Strengthening and Underapproximations*, FMCAD 2010.
[Primary PDF](https://fmcad10.isec.tugraz.at/Papers/papers/03Session2/005Auerbach.pdf).

Read §§II–IV and VII. Configurable seeds, nondeterministic seed choice and long
LFSR behaviors motivate source-aware verification. Fixed-seed underapproximations
support bug finding; success on an underapproximation does not prove every seed
safe. The paper
does not provide the inspected Certifaiger exporter, and its industrial setting
does not make our six-case comparison industrial validation.

Access gap: the full Kailas–Paruthi–Monwai FMCAD 2009 arbiter paper was not
obtained. Its IBM publication record and the 2010 paper's account of complete
random sequences were inspected. No claim here attributes a directly read
technical construction to that unavailable 2009 full text.

## S11 — Existing period algorithms

GAP FSR package, Chapter 2, §2.2-4, *Period of LFSR*.
[Official manual](https://nzidaric.github.io/fsr/doc/chap2.html).
The earlier pinned source record is retained in
[the Gate 12 dossier](../odd_order_witness_v1/SOURCES.md).

The manual distinguishes primitive, irreducible and reducible LFSR period
computations. Period reasoning is established algebraic functionality; it does
not itself supply the consumer's standard original-model witness. No fresh
GAP experiment or claim of algorithmic priority follows from this inspection.

## Assessment limit

These sources rule out claiming the general interface, history technique,
source-aware idea or specialized-certification comparison pattern as new.
They do not establish a complete historical equivalence for the exact exporter.
Conversely, not finding that exact implementation does not clear originality
or significance. Gate 18's stopping decision is an evidence-based project
judgment, not a theorem that this implementation could never support useful
further research.
