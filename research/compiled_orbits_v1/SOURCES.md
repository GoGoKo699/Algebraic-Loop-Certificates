# Source comparison: exact source compilation is not automatically a new principle

Checked 26 September2026. This is a research evidence map, not manuscript prose.
The source-only membership theorem is proved in THEORY.md. Its novelty is not
established by the lack of a search hit for the exact Python schema.

## 1. Compact circuit representations are already a serious comparator

Peter Burgisser, M. Levent Dogan, Visu Makam, Michael Walter and Avi Wigderson,
Polynomial time algorithms in invariant theory for torus actions (2021).
Primary PDF: https://arxiv.org/pdf/2102.07727

Parsed primary paper inspected at Sections1.2-1.3 and the statements around
Theorems1.2-1.3; no native implementation run. The paper explicitly constructs
polynomial-bit-size arithmetic circuits for a small generating family of
Laurent invariants and uses invariant methods to decide orbit relations.
Therefore compact exponent/circuit representation is not itself our novelty.
The source uses complex tori supplied by integer weight matrices. It does not
state our arbitrary-characteristic finite cyclic source contract or repeated-
factor certificate. That difference is not an automatic improvement over its
stronger uniform polynomial-time result in its own model. A comparison must
retain its compact circuit representation rather than expanding its polynomials.

## 2. Moving logarithms into preprocessing is established in group computation

Henrik Baarnhielm, Recognising the small Ree groups in their natural
representations, Journal of Algebra416(2014),139-166.
https://doi.org/10.1016/j.jalgebra.2014.06.017
Preprint: https://arxiv.org/abs/1206.0411

Primary full publisher HTML inspected at the abstract, Theorem1.1, Section2.1,
and Section7's preprocessing/main-stage statements. No Magma run or figure-based
performance number imported. It already separates expensive source-dependent
preprocessing, with logarithm access, from subsequent polynomial-time membership
work. The group, randomized model and constructive output differ; this is not a
complete duplicate audit. It prevents a blanket originality claim for this
computational architecture, even in matrix-group settings.

## 3. The appropriate abstract comparison is also knowledge compilation

Adnan Darwiche and Pierre Marquis, A Knowledge Compilation Map,
JAIR17(2002),229-264, DOI10.1613/jair.989.
https://arxiv.org/abs/1106.1819

Primary abstract inspected; the2011 arXiv posting is not the publication year.
It distinguishes representation size, supported queries and transformations.
That is exactly why the new membership predicate is not silently a solver for
first hitting times or symbolic-region queries. No theorem about a Boolean
compilation language is automatically transferred to our algebraic one.

## 4. Direct predecessors retained from the preceding invariant audit

Kemper, Lopatin and Reimers, Separating invariants over finite fields,
JPAA226(4)(2022),106904.
https://doi.org/10.1016/j.jpaa.2021.106904
https://arxiv.org/abs/2011.07408

Primary abstract and the publisher's finite-orbit indicator construction were
inspected in this and the preceding pass. Orbit separation exists generally;
our candidate is a particular checked polynomial-size source representation.
No lower bound against circuit-encoded versions of their method is established.

Domokos, Separating monomials for diagonalizable actions,
BLMS55(1)(2023),205-223.
https://arxiv.org/pdf/2202.07002

Primary PDF reopened; the preceding audit inspected Theorem1.7 and cyclic
small-support consequences. Multiplicative/character relations and pairwise
semisimple separation are already strong antecedents. The graph criterion here
makes explicit which chosen compatibility tests suffice, but is an elementary
CRT fact until a targeted priority comparison establishes otherwise.

Kohls and Sezer, Separating invariants for the Klein four group and cyclic groups.
https://arxiv.org/abs/1007.5197

The preceding source dossier documents its inspection of the quotient theorem
and modular cyclic section. Those modular-group results must remain comparators
for our repeated-factor membership predicate; using nilpotent units does not
establish first treatment of modular invariant theory.

## 5. Exact orbit and logarithm algebra remain known foundations

Imran and Ivanyos, Efficient quantum algorithms for some instances of the
semidirect discrete logarithm problem, DCC92(2024),2825-2843, Section3.3.
https://doi.org/10.1007/s10623-024-01416-8

Menezes and Wu, The Discrete Logarithm Problem in GL(n,q),
Ars Combinatoria47(1997),23-32.
https://combinatorialpress.com/ars-articles/volume-047-ars-articles/the-discrete-logarithm-problem-in-gln-q/
PDF: https://combinatorialpress.com/article/ars/Volume%20047/volume_47_paper-3.pdf

The first paper's section was read in the prior audit. In this pass the second
PDF again exposes its title/abstract and printed page27, including separate-
extension processing; screenshot requests for printed pages28-30 failed with
cache misses and direct runtime download failed DNS resolution. The whole-paper
inspection gap remains. We do not repeatedly declare its algebra absent from
prior work because the full scan is inaccessible. No OCR or secondary summary
has been presented as a primary full-paper reading.

## 6. The updated contribution boundary

Already established, and NOT claimed original: invariant orbit separation;
small character/monomial descriptions; compact arithmetic circuits; offline
preprocessing followed by membership queries; primary-module analysis; exact
order tests; CRT compatibility; and standard primality certificates.

Proved and implemented here as a scoped statement: a source-only certificate
for a complete prime-field affine initial-orbit predicate, checked before any
target is supplied; a complete prime-power support criterion for a sparse set
of compatibility checks; and a deterministic per-target predicate that avoids
finite-field target-logarithm search and retains repeated factors.

Whether those guarantees together add an independently new representation or
verification theorem remains unresolved. The appropriate comparator is a
certifying, compact-circuit implementation of known cyclic invariant/character
methods, not an expanded orbit listing or a fresh logarithm query imposed on
every competing membership algorithm. No such native matched benchmark was run.

## Claim support for eventual opening and closing statements

| Proposed statement | Support | Qualification |
|---|---|---|
| Source-only preprocessing can support all later point targets | THEORY1-7; source format and exact tests | Mathematical guarantee; production time may be difficult |
| The compiled predicate is exact rather than merely inductive | Checked complete decomposition and graph coverage; THEORY6 | These stronger compilation obligations must not be omitted |
| Query evaluation does not solve a finite-field target logarithm | checker.py and query-stage forbidden-primitive test | Nilpotent characteristic-digit membership still runs |
| All timing questions become easy | None | False implication; index recovery remains distinct |
| This is the first compact invariant compiler | Sources1-4 | Not supported; do not claim |
| The system improves a production analyzer | No integration benchmark | Not established |
| The graph reduction preserves exactness | THEORY5 and exhaustive residue/graph controls | No claim that its star union minimizes edge count |

Manuscript drafting stays on hold. This pass closes a logical exactness/reuse
obligation and strengthens the prior-work baseline, not the entire publication
research programme.
