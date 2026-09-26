# Direct predecessors and claim audit

Inspected 27 September2026. These are supporting research records, not drafted
abstract/introduction/conclusion text. No search absence establishes originality.

## 1. Mixed-modulus endomorphism arithmetic is established

Christopher J. Hillar and Darren L. Rhea, *Automorphisms of finite abelian groups*,
American Mathematical Monthly114(10),917-923(2007), preprint2006.
https://arxiv.org/abs/math/0605185
https://arxiv.org/pdf/math/0605185

The primary parsed PDF was read at Definition3.1, Theorem3.3, Lemma3.4 and
Theorem3.6, including the proofs. It characterizes endomorphisms by integer
matrices with divisibility conditions and row-dependent modular reduction,
and characterizes automorphisms through the matrix modulo p. This is a direct
predecessor of the representation in THEORY Sections3-5. We do not claim the
mixed-module arithmetic or modulo-p automorphism criterion as new. A screenshot
was requested; no figure/table observation or successful visual audit is claimed.

## 2. Reduction to field logarithms in a mixed-order endomorphism ring

Matan Banin and Boaz Tsaban, *The Discrete Logarithm Problem in Bergman's
non-representable ring*, arXiv:1206.1077v2 (2012).
https://arxiv.org/abs/1206.1077
https://arxiv.org/pdf/1206.1077

The primary parsed paper was inspected in Sections1 and2, including the
End(Z/pZ + Z/p^2Z) representation, the Euler-isomorphism calculation and the
main reduction setup. It gives a deterministic polynomial reduction of that
ring's discrete-log problem to field discrete logs. This is particularly close
prior art: exotic mixed orders do not create new generic logarithm hardness.
Our claim concerns source-only, independently checked membership for an arbitrary
initial cyclic module, not first-exponent recovery in that fixed ring. That
difference does not by itself establish novelty. A generic certifying adaptation
of existing module/group algorithms must remain a competitor. Screenshot calls
for pages2,5 and6 failed; no scan-only measurement is used.

## 3. Prime-primary digit methods and generic comparisons

Andrew V. Sutherland, *Structure computation and discrete logarithms in finite
abelian p-groups*, Mathematics of Computation80(2011),477-500,
DOI10.1090/S0025-5718-10-02356-2.
https://arxiv.org/abs/0809.3413

Primary abstract inspected. It improves generic group-operation algorithms.
Its model is not the explicit mixed-module endomorphism model in which a
coefficient reveals an order-p digit. We must not quote generic square-root
costs as a lower bound for the structured problem. The p-adic digit induction
in this implementation is established methodology; the note spells out its
specific coefficient test and full replay obligations.

Giovanni Viglietta and Yasuyuki Kachi, *Efficient Lifting of Discrete Logarithms
Modulo Prime Powers*, arXiv:2505.07434v1 (2025).
https://arxiv.org/html/2505.07434v1

Primary HTML introduction, stated algorithm and correctness setup inspected.
It starts with a supplied scalar logarithm modulo p and efficiently lifts the
answer. Our membership predicate does not require a later target's residue
logarithm, and retains nonfree initial modules. This is a difference of contract,
not evidence that all previous algorithms need a new target logarithm at every
precision, nor that we improve their optimized scalar running time.

## 4. Finite-ring dynamics remains a strong baseline

Kantic, Qureshi, Panario and Legl, *On the Dynamics of Linear Finite Dynamical
Systems Over Galois Rings*, arXiv:2604.01548v1 (2026 preprint).
https://arxiv.org/html/2604.01548v1

Primary full HTML reopened and relevant source/decomposition/cycle-algorithm
sections inspected. The earlier dossiers retain its access assumptions. This
paper and Wei-Xu-Zou's earlier finite-ring methods establish that field layers,
module structure and period lifting are classical algorithms. We claim neither
first analysis of ring dynamics nor a demonstrated speedup over them. No native
implementation of those full matrix methods was executed here.

## 5. Native methods actually run

SymPy1.14.0 official normal-form and number-theory documentation:
https://docs.sympy.org/latest/modules/matrices/normalforms.html
https://docs.sympy.org/latest/modules/ntheory.html

The optional diagnostic ran 120 native Smith normal forms over ZZ and compared
their truncated p-valuations with the normalization used here. It also used
native multiplicative orders on76 scalar sources and checked2,868 targets by
ordinary subgroup power identities. For odd prime powers the unit group is
cyclic; for powers of2 we restrict the comparison sources to1 modulo4 and
retain that congruence in the predicate. That restriction is not a claim about
all even-modulus unit groups. The query baseline does not run a new target
logarithm and is a stronger comparator than full trajectory enumeration.

These are correctness checks, not timings or a general matrix-orbit comparison.
No software performance assertion follows from their counts. The source-visible
64-bit affine and multiplicative examples remain easy known families.

## 6. What is and is not supported

| Claim | Evidence | Assessment |
|---|---|---|
| One verified prime-field source suffices for the prime-power all-target contract | THEORY Sections2-9 | Derived theorem; prototype tested; originality unestablished |
| Nonfree initial modules are retained | Diagonal replay,256 independent spans,380 mixed-order source cases | Implemented; not a new normal-form algorithm |
| Residue-phase recovery is unnecessary for membership | THEOREM6 equivalence and source-only API | Does not recover timing or make synthesis free |
| Query arithmetic has no p-sized digit search | THEORY7 and module.py | Explicit structure, not a generic DLP improvement |
| Ordinary p-primary arithmetic or modular lifting was invented here | Sources1-4 | False; not claimed |
| The method improves a native general matrix solver or verifier | No matched native full implementation | Not established |
| All paper research is complete | No resolved final contribution assessment | False; manuscript remains on hold |

A closer comparison has therefore narrowed, not eliminated, the scientific
obligation. The potential result is the exact certified source/query reduction
with its bit-cost and torsion conditions. The remaining question is whether a
certifying adaptation of established finite-module algorithms already supplies
that same guarantee, or whether an independently useful additional guarantee
can be established. This dossier must not be replaced by a claim that no exact
match appeared in a title search.
