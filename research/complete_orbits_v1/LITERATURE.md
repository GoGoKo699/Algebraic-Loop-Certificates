# Background and contribution evidence

Checked on 26 September 2026. This is research support for eventual statements,
not an abstract, introduction, related-work section, or conclusion draft.
A source's existence is distinct from a claim that its complete proof was read.
A search producing no close hit does not establish originality.

## S1. Cyclic-space orbit reduction

Muhammad Imran and Gabor Ivanyos, *Efficient quantum algorithms for some
instances of the semidirect discrete logarithm problem* (2024), Section 3.3.
https://doi.org/10.1007/s10623-024-01416-8

Primary full HTML read at the relevant section. It explicitly builds the
initial cyclic subspace, rejects an outside-span target, and reduces a
point-orbit query to matrix power membership. It also distinguishes the
rational-field algorithm from the finite-field case. This supports T2's
lineage and excludes priority claims for the orbit reduction or its quantum
use. Our prime-field affine lift is elementary, not the new contribution.

## S2. Matrix logarithms and field decomposition

Alfred J. Menezes and Yi-Hong Wu, *The Discrete Logarithm Problem in GL(n,q)*,
Ars Combinatoria 47, 23-32 (1997).
https://combinatorialpress.com/ars-articles/volume-047-ars-articles/the-discrete-logarithm-problem-in-gln-q/

The primary abstract establishes a polynomial-time reduction to logarithms in
smaller finite-field extensions. The primary PDF has no parsed text in this
session. A screenshot of printed page 27 was inspected: it explains why a
common splitting field may have exponentially large degree and instead uses
individual extensions. Screenshots of other requested pages failed. The
full order/repeated-root algorithm has NOT been audited here at equation level.
Therefore we classify T1 as a **certifying reformulation of established algebra,
with priority unresolved**, not a new finite-field algorithm. Closing this
comparison is a required research gate, not an optional bibliography task.

## S3. Probabilistic generation versus deterministic factor checking

Michael O. Rabin, *Probabilistic Algorithms in Finite Fields*, SIAM Journal on
Computing 9(2), 273-280 (1980).
https://doi.org/10.1137/0209024

Primary abstract and publication metadata read. Factoring and irreducible
polynomial construction are established algorithmic tasks. T3 states and proves
the exact Frobenius/gcd criterion used by this implementation; no performance
claim about a native Rabin factorer is made. The producer's trial factorer is
not an appropriate strongest classical performance baseline.

## S4. Supplied prime proofs

Vaughan R. Pratt, *Every Prime Has a Succinct Certificate*, SIAM Journal on
Computing 4(3), 214-220 (1975).
https://doi.org/10.1137/0204018

Primary abstract, proof-rule description, and short-certificate statement read.
Supports polynomial-size proofs of primality and the producer/verifier
separation. The production Lucas-Pratt checker is reused. Historical statements
about what was then unknown concerning primality testing are not current claims.
Primality proof verification is not free factorization of the period.

## S5. General group nonmembership is a different access problem

Laszlo Babai, *Bounded Round Interactive Proofs in Finite Groups*, SIAM Journal
on Discrete Mathematics 5(1), 88-111 (1992).
https://doi.org/10.1137/0405008

Primary abstract read. It gives interactive proof results for black-box group
nonmembership and describes oracle limitations even for abelian groups. This is
why T1 explicitly uses matrix/field representations, cyclic linear algebra,
irreducible factors and field arithmetic. It is NOT a deterministic
noninteractive theorem for arbitrary black-box groups. No transfer of its
oracle lower bounds to the present explicit representation is asserted.

## S6. Loop acceleration has existing consumers

Florian Frohn and Carsten Fuhs, *A calculus for modular loop acceleration and
non-termination proofs*, STTT 24, 691-715 (2022).
https://doi.org/10.1007/s10009-022-00670-2

Primary full HTML abstract, introduction and formulation read. Supports the
independent purpose of loop summaries in reachability, safety, runtime and
termination analysis. Its principal domain is integer programs. 'Modular'
means compositional techniques here, not arithmetic modulo a prime. Our fixed
initial state and point target do not automatically provide its general loop
relation, guard handling or program analysis. No native LoAT comparison was run.

## S7. Producer/checker separation is established

George C. Necula, *Proof-carrying code*, POPL 1997, 106-119.
https://doi.org/10.1145/263699.263712

Primary abstract read. Supports the general idea of accompanying untrusted
computation/code with checkable evidence. We do not claim this architecture as
new, and our Python checker does not constitute a verified safe-code loader.

## S8. Exact linear algebra certificates

Jean-Guillaume Dumas, Erich Kaltofen, Emmanuel Thome and Gilles Villard,
*Linear Time Interactive Certificates for the Minimal Polynomial and the
Determinant of a Sparse Matrix*, arXiv:1602.00810.
https://arxiv.org/abs/1602.00810

Primary abstract read. Establishes sophisticated certifying linear algebra as
an existing comparator. Its interaction, randomness, sparse-access and verifier
costs differ. Our checker recomputes a small cyclic module by elimination and
is only claimed polynomial time, not faster than these certificate algorithms.
Their full proofs and native code have not been reproduced.

## S9. Existing machine-checked primality certificates

*Pratt's Primality Certificates*, Archive of Formal Proofs.
https://isa-afp.org/entries/Pratt_Certificate.html

Official entry read. A machine-checked formalization of related primality
mathematics exists. It does not cover our Python certificate format, parser,
cyclic-space elimination, unipotent digit routine, or integration. No formal
verification of those new files is claimed.

## S10. Independent software witness exchange

Dirk Beyer, Gidon Ernst, Martin Jonas and Marian Lingsch-Rosenfeld,
*SV-LIB 1.0: A Standard Exchange Format for Software-Verification Tasks*,
arXiv:2511.21509 (2025).
https://arxiv.org/abs/2511.21509

Primary abstract read. Documents an independent direction toward task and
witness interchange/validation. A custom JSON algebraic certificate is not
a new general exchange standard, nor automatically compatible with SV-LIB.
This source motivates a future consumer integration rather than claiming one
has already been implemented.

## S11. Native computational baselines

SymPy 1.14.0 number-theory documentation:
https://docs.sympy.org/latest/modules/ntheory.html

SageMath generic group algorithms:
https://doc.sagemath.org/html/en/reference/groups/sage/groups/generic.html

Official API documentation inspected for multiplicative order and discrete
logarithm operations. The optional native check actually ran SymPy 1.14.0 on
81 polynomial factorizations and 300 scalar cases. Sage was not executed. The
current source uses elementary trial factorization and baby-step/giant-step;
we must not compare it only with orbit enumeration in a future timing study.

## Claim-to-evidence map for eventual opening and closing statements

| Intended fact or conclusion | Evidence | Allowed wording / limit |
|---|---|---|
| Loop summaries can support program analysis | S6 | Established purpose; not measured usefulness of this implementation |
| A finite-field orbit can be reduced algebraically | S1, S2 | Prior method, not our novelty claim |
| All supported outcomes admit short checkable evidence | THEORY T1-T9 | Current derived certificate theorem; originality unresolved |
| General inside-span negatives need not list a whole cycle | THEORY T3-T8; repeated-factor tests | For the explicit prime-field affine point-target model, with supplied witnesses |
| The checker needs no discrete-log search or factor search | Source audit and THEORY T3-T9 | Does not imply efficient witness production |
| The reference producer avoids vector-orbit enumeration | producer.py | Uses other potentially expensive classical searches |
| Verified results answer future horizon queries | THEORY T10; 18,615 finite query checks | Fixed model/initial state/target, not arbitrary changing guards |
| The implementation agrees with existing arithmetic | sympy_results.json | Primitive/scalar correctness, not full-model performance dominance |
| The implementation is correct on every input | Not established at code level | Theorem plus tests; no proof-assistant-verified implementation |
| This is a new publishable algorithm / fast classical DLP | Not established | Do not put this in any abstract or conclusion |
| The system improves actual analyzer performance | No matched integration benchmark | No such claim until a consumer and comparison are executed |

## Search limits and next priority audit

Searches covered finite-field orbit certificates, matrix power membership,
cyclic nonmembership, deterministic/interactive certificates, and loop
acceleration, including current primary sources. No direct duplicate of this
exact JSON system was located. That observation is not evidence that its
mathematical reformulation is novel. S2 remains the most important incomplete
full-text comparison. A missing source is not to be replaced by an unattributed
secondary paraphrase or by an inference from the title.
