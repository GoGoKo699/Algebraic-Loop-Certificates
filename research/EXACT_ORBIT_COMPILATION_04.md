# Research update: from reusable exclusion to one exact source predicate

26 September2026. Manuscript preparation remains on hold. Read
[the new theorem](compiled_orbits_v1/THEORY.md) and
[the strengthened source comparison](compiled_orbits_v1/SOURCES.md).

The prior invariant theorem had the order of quantifiers 'for each unreachable
target, a small separating witness exists'. The new theorem constructs one
polynomial-size family depending only on the recurrence and initial state,
whose conjunction is the entire orbit. A new source-only certificate checks
that conjunction's completeness. Later full-state membership queries use no
finite-field target-logarithm search. Index/time recovery is not provided.

The source certificate contains a complete primary decomposition, exact orders,
source-to-source comparison alignments, and a checked compatibility graph.
These are stronger compilation obligations than those for one inductive
predicate. At query time the fixed coordinate map, local subgroup powers,
alignment equalities and nilpotent membership test suffice. Target membership
can then be certified positively as well as negatively, without an orbit list.
This is a proved mathematical statement, not a new fast synthesis claim.

A graph of selected comparisons is complete exactly when every prime-power
support is connected inside it. Ordinary graph connectivity is insufficient:
orders6,10,15 require all three constraints. The implemented producer uses a
source-only prime-wise star union, and the checker proves coverage independently.
This elementary reduction has an exact necessity/sufficiency proof; it is not
claimed as a new optimal graph algorithm.

New evidence:657 compiled sources;5,354 exhaustive target queries on655 sources;
430 controls on a three-component source and240 closed-form large-characteristic
controls;1,728 graphs and74,088 residue assignments. No native performance claim
follows. The familiar F13 example now excludes the formerly accepted unreachable
origin. Its complete certificate is604 bytes versus418 for the earlier weaker
predicate, illustrating the extra assurance rather than universal size savings.

The source audit found two important precedents beyond the existing separating-
invariant papers: the torus-action paper already uses compact arithmetic circuits,
and Ree-group membership algorithms already move logarithm work to preprocessing.
Thus neither compact syntax nor offline/online separation can be claimed as the
new result. The exactness, verified representation and prime-field cyclic scope
are now explicit, but the incremental original contribution still needs a matched
comparison with equally compact, certifying prior methods.

No older file, evidence fixture, primary interface, license or parent repository
is modified by this additive module. The default fixed resource limits remain
policies; source-dependent compilation data are not P/poly advice. Arbitrary
symbolic guards, composite-ring compiled membership, singular maps, multiple
initial states, verified frontends, and formal Python correctness are not claimed.

## Scientific completion

This pass closes a specific logical and algorithmic obligation: a fixed certified
source description for ALL subsequent point membership queries. It does not
close originality, practical contribution, or the overall scientific programme.
A full-checkout CI result, when available, is an integration result, not novelty.
Further work should compare this precise source-certificate/query contract with
known compact invariant constructions before adding more formats or examples.
