# Source audit and claim support for separating predicates

26 September 2026. This is background research, not draft introduction or
conclusion text. The existing field/modular completeness arguments remain
attributed to cyclic-module, group-order and lifting mathematics. No literature
search result is treated as proof that another result does not exist.

## Direct new comparison: finite-field separating invariants

Gregor Kemper, Artem Lopatin and Fabian Reimers, *Separating invariants over
finite fields*, Journal of Pure and Applied Algebra 226(4), 106904 (2022),
DOI 10.1016/j.jpaa.2021.106904; arXiv:2011.07408.
https://doi.org/10.1016/j.jpaa.2021.106904
https://arxiv.org/abs/2011.07408

Primary publisher HTML inspected: abstract, introduction, finite-field orbit
separation formulation and the orbit-indicator construction (1.1)-(1.2). It
establishes that different finite-group orbits can be distinguished by invariant
polynomials and studies minimal numbers and degree bounds. Thus existence of
an invariant separating a bad point is NOT a contribution of this project.

The current claim concerns a compact, checked circuit/predicate representation
for one explicitly given cyclic action and initial state. Our power-kernel
scheme is a decidable group-membership predicate, not an expanded scalar
polynomial, and the equal-powers zero set can be preserved even while its
underlying polynomial scales. A comparison must translate objectives and
representations explicitly. We have NOT established an asymptotic advantage
over a suitably circuit-encoded implementation of this invariant literature.

## Diagonal actions and multiplicative relations

Matyas Domokos, *Separating monomials for diagonalizable actions*, Bulletin of
the London Mathematical Society 55(1), 205-223 (2023), first online2022,
DOI 10.1112/blms.12722.
https://londmathsoc.onlinelibrary.wiley.com/doi/full/10.1112/blms.12722

Primary PDF inspected at the introduction, Theorem1.7, and its discussion of
finite cyclic groups and coset intersections; not every theorem is audited.
https://arxiv.org/pdf/2202.07002
For a finite cyclic diagonalizable action, the bound in Theorem1.7 specializes
to two-coordinate support sufficing in the corresponding monomial separation
problem. Thus the semisimple **pairwise** nature of our certificate is not an
independent novelty claim. Character relations and separating monomials are established. The new equal-power scheme
is therefore not a new general principle that multiplicative relations supply
invariants. Its concrete use is a checked pair of algebra maps with the same
update multiplier; its relation to prior minimal separating constructions is
still a theorem-level comparison obligation.

Martin Kohls and Mufit Sezer, *Separating invariants for the Klein four group
and cyclic groups*, arXiv:1007.5197.
https://arxiv.org/abs/1007.5197

Primary PDF read at Theorem1 and Section3, Lemma10 through Proposition13 and
its proof. The equivariant-quotient theorem already separates coarse orbit
information from the remaining fibers. The paper treats indecomposable cyclic
order-pm representations in characteristic p (Section3 makes the restriction
to a single p factor explicit), using recursive transfers and norms. Thus our
nilpotent/semisimple division is not the first handling of modular cyclic
separation or of quotient/fiber proof composition. We retain a separate
bit-cost and representation comparison: our predicates use a checked
nilpotent-group recognizer rather than outputting their invariant polynomials.
https://arxiv.org/pdf/1007.5197
No native implementation of this predecessor was executed.

## Prior algebraic decision mechanisms remain direct precedents

Menezes and Wu, *The Discrete Logarithm Problem in GL(n,q)*, Ars Combinatoria47,
23-32 (1997).
https://combinatorialpress.com/ars-articles/volume-047-ars-articles/the-discrete-logarithm-problem-in-gln-q/

The primary PDF was reopened in this pass. Its title/abstract page and printed
page27 were successfully viewed. Screenshots of the other pages returned cache
misses; direct runtime download failed because network name resolution was
unavailable. No OCR or invented full-paper summary was substituted. The open
whole-paper inspection gap is unchanged. The successfully inspected page27
explicitly uses separate small extension fields instead of a large common
splitting field. Our pairwise comparison field of degree lcm(h_i,h_j)<=k^2
is not a new claim that all-component splitting fields are unnecessary.

Imran and Ivanyos, finite-field orbit discussion, Section3.3:
https://doi.org/10.1007/s10623-024-01416-8
The previous research ledger already records the full-section inspection.
The cyclic-module conversion used here remains prior work.

## Completed and uncompleted scientific claims

| Claim | Evidence | Status |
|---|---|---|
| Three invariant schemes suffice to exclude every unreachable prime-field point | THEORY Sections2-5 | Derived and proved here as a scoped certificate statement; priority unestablished |
| These certificates are target-independent and can be reused | Source binding, compile/query API, finite rebinding checks | Implemented; not an exact orbit characterization for each single predicate |
| Checking uses no irreducibility test or supplied target logarithms/order factors | Checker source and disabled-irreducibility test | Implemented; base prime proofs and polynomial arithmetic still needed |
| A bounded producer uses no finite-field logarithm of the target | Producer source, metrics | Implemented; base-to-base logarithm alignment and nilpotent digit extraction remain |
| Preservation holds beyond the actual reached trajectory | Exact full-state tests of I(y)=>I(F(y)) | Finitely checked and mathematically proved, not formally verified Python |
| This is the first short separating invariant method | Existing invariant literature | Not established and not claimed |
| It is faster than native invariant-generation or verification software | No such matched benchmark | Not established |
| It extends modular precision composition to all guarded programs | No proof or implementation | Not claimed |

## Consequence for the completion plan

The next original-contribution comparison is now also with finite-group
separating invariants, not just discrete-logarithm algorithms. Producing a
custom certificate format is not enough. The relevant question is whether the
explicit grammar, complete coverage, verifier simplicity or reusable predicate
has a stronger guarantee than a certifying version of those existing methods.
A proof is not automatically new because it can be tested in Python.

The manuscript remains on hold. Background for motivation, prior methods,
consequences and limitations has been extended, not declared exhaustive.
