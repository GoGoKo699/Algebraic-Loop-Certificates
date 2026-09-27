# Bounded predecessor audit: invariant evaluation and history

Inspected 27 September 2026, starting from repository revision `5b4f46d`.
This audit concerns [the phase-parity argument](../proof_interface_v1/THEORY.md),
Sections 2–5, and the distinction between evaluating an original-state
invariant and checking a supplied history state. It is not a systematic
literature review. The [preceding dossier](../odd_order_witness_v1/SOURCES.md)
records the algebraic proof interfaces and workload sources.

**Decision:** the central mechanism has a direct generic predecessor:
easy witness relations can force every separator of their projections to
compute a bit of an inverse. Conservative history instrumentation is also
established. The concrete odd-cycle monitor and its executable AIGER witnesses
are a useful worked instance, but this audit does not support a new general
invariant-succinctness theorem. Stop expanding this construction as an
originality candidate; preserve the proofs, limitations and native evidence.

## Direct inverse-bit separator predecessor

Maria Luisa Bonet, Toniann Pitassi and Ran Raz, *On Interpolation and
Automatization for Frege Systems*, SIAM Journal on Computing 29(6), 2000,
pp. 1939–1967. [Author-hosted full paper](https://www.cs.upc.edu/~bonet/revistas/siam3.pdf).

Section 1.2, p. 1942, gives relations asserting that a permutation maps a
private input to the shared output and that a chosen input bit is respectively
zero or one. Injectivity makes their conjunction unsatisfiable. Any separator
of the projected relations determines that inverse bit. The authors attribute
this construction to Krajíček–Pudlák. Section 1 defines feasible interpolation
using polynomial-size circuits. Sections 1.3 and 6 discuss their conditional,
nonuniform Frege/threshold-Frege results; those results are not invariant
lower bounds for this repository.

Read depth: Sections 1–1.3 and 6; the displayed inverse-bit argument was read
in full. The technical arithmetic proofs in Section 7 were not audited.
Reference [KP] identifies Krajíček and Pudlák, *Some consequences of
cryptographical conjectures for S¹₂ and EF*, LNCS 960, 1995, pp. 210–220.
That original paper was not obtained in this audit; its results are attributed
through the explicit discussion above, not reported as independently read.

The following comparison is our derivation. On the primitive active slice,
let `M = 2^n - 1` and define the two efficiently checked relations

```text
E_b(r, s, t) := s != 0 AND 0 <= t < M
                AND r = A^t s AND (t mod 2) = b,   b in {0,1}.
```

Their existential projections partition the nonzero `(r,s)` pairs. The
repository's reachability and future-error arguments force every adequate
original-state invariant `I` to accept `(r,s,0)` exactly on the projection
of `E_0`. Thus `I(r,s,0)` is a separator of the same inverse-bit kind.
The sequential monitor supplies the reachability/safety sandwich; the
separator/projection phenomenon itself is already present in the cited work.
The paper does not contain this exact AIGER monitor, and finding no verbatim
instance in this bounded audit is not evidence of novelty.

## Conservative history state

Martín Abadi and Leslie Lamport, *The Existence of Refinement Mappings*,
Theoretical Computer Science 82(2), 1991, pp. 253–284.
[Author-hosted full report](https://lamport.azurewebsites.net/pubs/abadi-existence.pdf),
[journal DOI](https://doi.org/10.1016/0304-3975(91)90224-P).

Report Section 5.1, printed pp. 20–22, defines history augmentation by H1–H5.
In particular, H4 requires every original transition to lift from every
corresponding augmented source state. Proposition 4 proves preservation of
externally visible behavior. Section 7, Theorem 2, adds history and prophecy
to obtain refinement mappings under machine-closure, internal-continuity
and finite-invisible-nondeterminism hypotheses. Its history construction
stores a finite execution prefix of unbounded possible length; it supplies
no polynomial-size invariant guarantee.

Read depth: Section 5.1 including Proposition 4's proof; Section 7's theorem
statement and history-construction stage. The full completeness proof was
not audited. Page numbers refer to the author report, not journal pagination.

For this repository, the total phase update and unchanged original input,
reset and transition functions provide a particular history extension.
Retaining `t` makes the relation `r=A^t s` directly checkable. It does not
provide an efficient procedure to reconstruct `t` from arbitrary current
`(r,s)`. Soundness of adding such history and the complexity of reconstructing
it are separate questions.

## Definitional auxiliaries and restricted CNF size

Andrew Luka and Yakir Vizel, *Property Directed Reachability with Extended
Resolution*, CAV 2025.
[Published primary text](https://doi.org/10.1007/978-3-031-98668-0_13),
[versioned full preprint](https://arxiv.org/html/2505.18998v1).

Section 5, Definition 3, restricts auxiliary circuits to acyclic AND/XOR
definitions over original current-state variables and earlier auxiliaries.
Definition 4 states initialization, induction and safety using these
definitions in both time frames. Lemmas 3–4 eliminate auxiliaries by
substitution. Published Theorem 2 (preprint Theorem 5.1) characterizes safety
using closed generalized traces. Section 6.3 addresses examples with
exponential CNF invariants, including examples inherited from IC3-INN.

Read depth: Sections 1, 4 and 5, including the definitions and elimination
arguments, and Section 6.3. No reproduction of the reported experiments or
independent reading of the IC3-INN paper is claimed here.

Our inference: retaining DAG sharing during substitution gives an ordinary
original-state Boolean circuit of size `O(|E| + |Inv|)`. A reduction in CNF
clauses therefore does not establish a corresponding separation against
arbitrary original-state circuits. The phase history used here has a
different contract: its value is maintained through transitions, without a
small current-state reconstruction circuit being supplied. None of the
paper's performance results transfers to our corpus without measurement.

## Discrete-log bits and inference are distinct questions

Claus-Peter Schnorr, *Security of Allmost ALL Discrete Log Bits*,
[ECCC TR98-033, 1998](https://eccc.weizmann.ac.il/report/1998/033/).
The primary abstract discusses odd-order groups and shifted exponent bits,
and attributes least-significant-bit security to Peralta (1985) and
Long–Wigderson (1988). Read depth for this dossier is the abstract; unreliable
PDF extraction is not counted as a full-paper reading. This establishes
relevant prior context, not a theorem imported with unchecked hypotheses.
The repository's exact-oracle recovery is proved directly and requires no
claim about noisy prediction or cryptographic security.

Feldman, Immerman, Sagiv and Shoham, *Complexity and Information in Invariant
Inference*, POPL 2020, article 5.
[Full preprint](https://arxiv.org/pdf/1910.12256),
[DOI](https://doi.org/10.1145/3371073).
The introduction and model definition were read in the preceding audit.
Their black-box Hoare-query inference model excludes direct transition-code
access. Its query lower bounds do not establish hardness of evaluating an
already supplied invariant or of constructing source-aware history.

## What the comparison permits

| Repository statement | Assessment after this audit |
|---|---|
| All adequate invariants agree with phase parity on the specified slice | A concrete reachability/safety theorem; keep its exact domain and proof. |
| An exact parity evaluator recovers phase using efficient binary jumps | An explicit reduction, consistent with classical discrete-log-bit reasoning. It is not a new cryptographic assumption or established hardness result. |
| Supplied history makes phase consistency easy to check | A bounded instance of an established witness/projection and history-variable distinction. |
| No short original-state invariant exists | Unsupported without a representation restriction and a matching hardness assumption. |
| Auxiliary variables yield an arbitrary-circuit lower bound | Unsupported: definitional extensions preserve circuit sharing; genuine history has a different interface. |
| Native SAT proof replay demonstrates an asymptotic separation | Unsupported: the retained runs establish those finite checks only. |

The generic argument needs an efficiently computable binary-exponent jump
operation and a known odd orbit period. Reversibility alone does not make
exponentially many iterates inexpensive. Finite-field matrix powering is
one implementation of that premise, not the source of the separator idea.

The short quantified circuit `exists t. H(r,s,c,t)` already has only original
free variables. Existentially quantifying its Tseitin gate variables also
gives a short quantified Boolean formula. Calling every such invariant
necessarily long would be false. The useful distinction is evaluating
membership without a witness versus checking it with supplied history.

A uniform efficient invariant constructor and evaluator would yield a
uniform phase-recovery algorithm; polynomial-size invariant circuits would
yield nonuniform recovery circuits. These implications do not prove either
hardness premise. Nor does a small invariant circuit guarantee small SAT
proofs for its universally quantified induction obligations.

The audit establishes close generic predecessors, not a claim that one
paper already states every detail of this monitor. No further frontend,
larger synthetic corpus or manuscript is justified by this distinction
alone. A later continuation needs an independently useful, measured cost or
assurance question under equally expressive certificate interfaces.
