# Direct source audit and resolved access gap

27 September 2026. Background and claim evidence, not manuscript sections.
No source's statement is enlarged to cover our whole interface without proof.

## Menezes-Wu: readable author copy located

The Discrete Logarithm Problem in GL(n,q), Ars Combinatoria 47, 23-32.
Publisher metadata labels the article 1997; the author's list says 1998.
This bibliographic discrepancy is recorded rather than silently resolved.

- Publisher: https://combinatorialpress.com/ars-articles/volume-047-ars-articles/the-discrete-logarithm-problem-in-gln-q/
- Author's publication list: https://cryptography101.ca/publications/
- Author-hosted readable copy: https://cryptography101.ca/wp-content/uploads/2025/04/glnq.pdf

The complete mathematical text was inspected, including Sections 3-5, Lemma 1,
Theorems 2-4 and Algorithms 1-2. Author-copy pages 7-9 were also inspected as
screenshots. The earlier inaccessible publisher scan is no longer the only
available primary copy. No OCR, local download, or byte-identity between the
copies is claimed. No copyrighted PDF is rehosted in this repository.

The paper explicitly handles repeated Jordan blocks, separates small extension
fields, reads characteristic information from binomial entries, and gives a
polynomial bound for its remaining characteristic-primary search. Its input
promises B=A^ell; it is not the present static all-target certificate API.
The comparison's membership extension is proved in THEORY.md, not attributed
verbatim to this predecessor. Old statements about the then-current complexity
of field logarithms are not imported as present-day claims.

## A small index conversion in the author copy

Algorithm 2, step 4.9, labels the search index j as ell mod P after matching
J^(ell0+j*s)=J^ell. The residue follows instead as (ell0+j*s) mod P. For the
4-by-4 Jordan block J_4(2) over F3 with ell=1, ell0=1 and s=2, the first match
has j=0 but ell mod9=1. Eighteen direct matrix checks retain this distinction.
This appears to be an indexing slip, not a failure of the polynomial reduction:
the conversion repairs it without changing its complexity. No publication
novelty or practical advantage is claimed from this observation. No corrected
version or external author response has been obtained.

## Character relations and compact representations

Domokos, Separating monomials for diagonalizable actions, BLMS 55(1),205-223
(2023), online2022. Primary arXiv v3 inspected at the character definitions,
Proposition1.1, Theorem1.7, and the positive-characteristic qualifications.
https://arxiv.org/pdf/2202.07002
https://doi.org/10.1112/blms.12722

It connects separating monomials to relations in character groups. Our scalar
compatibility predicates are such relations after source calibration. The paper
works over an algebraically closed field with diagonalizable actions; it does
not establish the repeated-factor certificate algorithm by itself. We neither
expand the competitor's exponents nor confuse polynomial degree with bit-size.

Burgisser, Dogan, Makam, Walter and Wigderson, Polynomial time algorithms in
invariant theory for torus actions, CCC2021.
https://arxiv.org/pdf/2102.07727
https://doi.org/10.4230/LIPIcs.CCC.2021.32

The primary statements about arithmetic circuits and orbit problems in Sections
1.2-1.3 were inspected. Compact circuit representations and polynomial-time orbit
algorithms are already established in that model. Complex torus inputs differ
from finite cyclic sources, and no theorem is transferred without the explicit
finite-algebra argument in THEORY.md. No native implementation was executed.

Kohls and Sezer, Separating invariants for the Klein four group and cyclic groups.
https://arxiv.org/pdf/1007.5197

The quotient/fiber and modular cyclic passages are documented in the prior audit.
They remain direct context for separating invariants with a characteristic part.
This round does not claim a fresh full reproduction of that work, or priority
from choosing Taylor rather than invariant-polynomial output.

## Binomial digits

Eric Rowland, Lucas' theorem modulo p^2, American Mathematical Monthly129(9),
846-855(2022). The primary introduction's congruence(1) and base-p formulation
were read; later tables and figures are not used here.
https://arxiv.org/pdf/2006.11701
https://doi.org/10.1080/00029890.2022.2038004

Its opening states the classical Lucas relation and credits Lucas1878. The
present decoder uses only that classical mod-p identity; it uses none of the
paper's new mod-p^2 extension. THEORY.md independently proves the special
coefficient formula needed by the algorithm. No modern priority is claimed
for extracting digits from a binomial row.

## Claim-to-evidence decisions

| Claim | Finding |
|---|---|
| Earlier matrix-logarithm work ignores repeated blocks | False: now directly checked in the author copy |
| No accessible full copy could be inspected | Previously true locally; resolved this round |
| Source-only recognition requires a new unipotent routine | Not for the coarse guarantee: a Taylor/Lucas path suffices |
| Ordinary characters can only handle diagonal toy sources | False as a comparison strategy: primary Taylor blocks cover the full stated domain |
| A prior paper supplies our complete exact certificate API | Not established; the audit is a derived certifying adaptation |
| The alternative can use the same untrusted evidence | Proved and implemented; independent source checks revalidate it |
| A native full solver was benchmarked | No; this is code written for the controlled comparison |
| The current coarse theorem is a cleared novel algorithmic result | No; classify it as a certifying reformulation on current evidence |

The remaining publication obligation is not another search for identical wording.
It is a new, independently useful guarantee or a justified verification benefit.
Historical priority of the exact interface remains unestablished in either
direction. There is no manuscript, submission, external contact, or venue
statement in this research record.
