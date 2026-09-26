# Primary-source and contribution audit for query boundaries

27 September 2026. Manuscript preparation remains on hold. Ordinary proofs in
THEORY.md support the stated reductions; finite tests check their implementation,
not complexity assumptions. No novel hardness principle or quotient method is
claimed merely because it is expressed in this project's certificate notation.

## S1. Common exponents and conditional compilation cost

Dan Boneh, *The Decision Diffie-Hellman Problem*, ANTS III, LNCS1423,48-63(1998).
Author page: https://crypto.stanford.edu/~dabo/abstracts/DDH.html
Primary PDF: https://crypto.stanford.edu/~dabo/papers/DDH.pdf

Author bibliographic page and parsed primary Sections1-2 inspected, including
its warning about easy character tests and its prime-order subgroup examples.
The diagonal-source equivalence is an immediate application of the DDH relation.
The historical survey is not used to claim the currently best known running
time or that every finite-field DDH instance is hard. Our statement is expressly
conditional on a subgroup family satisfying DDH, and does not assert DDH=DLP.

## S2. The direct predecessor for the prime-clock reduction

Henning Fernau, Stefan Hoffmann, Michael Wehar, *Finite Automata Intersection
Non-Emptiness: Parameterized Complexity Revisited*, arXiv:2108.05244v1(2021).
https://arxiv.org/abs/2108.05244
https://arxiv.org/pdf/2108.05244

Parsed primary introduction and Appendix C, proof of Theorem4.1 on PDF pages
28-29, inspected. The latter explicitly reduces 3SAT using prime-period unary
automata: residues0/1 encode variables, and a clause forbids its unique falsifying
residue modulo the product of its variable primes. It attributes the older
hardness results and provides a self-contained construction.

This is a very close mathematical antecedent, not generic background. Our
reduction pools every subset of at most three variables into a formula-independent
source, encodes rotations as binary permutation blocks, and makes each test a
coordinate constraint through a fixed basis change. Those details establish the
precise source/query contract and the preprocessing implication; they do not
justify announcing a new general prime-clock hardness technique. An exact
priority claim for that strengthened formulation remains unestablished.

The PDF contains publisher-template placeholders (CVIT2016) on its first page.
Those are not cited as a real venue, DOI, or publication date. The inspected
source is the actual arXiv2021 version identified above.

## S3. Periodic linear recurrence hardness already exists

Akshay S., Nikhil Balaji, Nikhil Vyas, *Complexity of Restricted Variants of
Skolem and Related Problems*, MFCS2017, LIPIcs83,78:1-78:14.
https://doi.org/10.4230/LIPIcs.MFCS.2017.78
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.MFCS.2017.78

Official record and parsed primary Section3, especially Theorem6 and the
prime-period construction, inspected. It proves hardness for periodic integer
linear recurrences and relates their characteristic roots to roots of unity.
That arithmetic domain differs from F2. We do not reduce its integer sums modulo2
and assume truth is preserved: cancellations could break the reduction. The
binary one-hot/coordinate construction is independently specified and tested.
Historical comments about the then-current general Skolem frontier are not
presented as an assessment of its current status.

## S4. Quotients preserving observed dynamics are established

George J. Pappas, *Bisimilar linear systems*, Automatica39(12),2035-2047(2003),
DOI10.1016/j.automatica.2003.07.003.
https://www.sciencedirect.com/science/article/pii/S0005109803002553

Primary publisher abstract/intro excerpts retrieved by search; direct page open
failed. It studies quotient and observation maps for discrete/continuous linear
control systems, connecting them to invariant subspaces and reachability.
The simple autonomous finite-field condition LA=BL is proved separately here;
no control-system theorem with different semantics or full implementation is
transferred on the strength of this abstract. No native quotient tool was run.

## S5. Exact lumping and its practical algorithms

Alexey Ovchinnikov, Isabel Pérez Verona, Gleb Pogudin, Mirco Tribastone,
*CLUE: exact maximal reduction of kinetic models by constrained lumping of
differential equations*, Bioinformatics37(12),1732-1738(2021).
https://academic.oup.com/bioinformatics/article/37/12/1732/6126795

Primary full HTML retrieved; lumping definitions, invariant-subspace/Jacobian
conditions, and the discussion of earlier lumping work inspected. This is a
continuous polynomial/kinetic-model setting, not a finite-field orbit benchmark.
It reinforces the prior status of exact observation-preserving reduction; we
do not claim the biological model examples as uses of this repository.

## S6. Query languages, not just representation sizes

Adnan Darwiche and Pierre Marquis, *A Knowledge Compilation Map*, JAIR17,
229-264(2002), DOI10.1613/jair.989.
https://arxiv.org/abs/1106.1819

Primary abstract inspected; the arXiv deposit is2011, not the publication year.
Supports the need to state which queries and transformations a compiled language
admits. It is background, not a theorem that an arbitrary algebraic predicate
has exactly the complexity of one of the paper's Boolean representation languages.

## Inspection limits

PDF screenshot requests for S1-S3 failed in the web tool; their parsed primary
text remained available. No figure/table-based measurements, visual full-page
inspection, or OCR claims are made. The hard-to-access 1997 Menezes-Wu scan was
again only partly retrievable; a direct runtime download failed DNS resolution.
This turn does not close that earlier whole-paper comparison. Inaccessibility
is not evidence of novelty. All tested code in this module was written anew;
no upstream implementation was copied or represented as reproduced.

## Evidence map

| Claim | Evidence | Qualification |
|---|---|---|
| A general efficient source compiler would solve the stipulated DDH problem | THEORY2; exact diagonal examples; S1 | Conditional subgroup-specific barrier, not an unconditional lower bound |
| Full-state recognition does not imply partial-coordinate search | THEORY3; S2/S3 lineage; exact reductions | NP-complete restricted problem, not a claim about every guard |
| Polynomial-size source-only preprocessing for all partial queries implies NP subset P/poly | Formula-independent source; THEORY4 | Uniform query procedure, padding by input length, nonuniform implication |
| General guard-avoidance polynomial static certificates imply NP=coNP | NP-completeness and complement argument | Does not exclude partial/interactive/long-certificate methods |
| Counting one-period matches captures #3SAT | Explicit CRT bijection; THEORY5 | No infinite-time count or general distinct-state-count conflation |
| Closed observations reduce to full-state quotient queries | THEORY6; 5,280 paired quotient queries; S4/S5 | Known sufficient mechanism, not all tractable cases or uniformly fast synthesis |
| These results establish a new publishable main theorem | No priority clearance | Supporting scope science; the original contribution audit remains open |

The sensible next step is to assess the existing exact certified compilation
result against equally compact, certifying prior constructions, now without
using unsupported claims about general guard solving or free preprocessing.
