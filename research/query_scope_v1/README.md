# Query scope: what exact orbit compilation does and does not buy

This audit does not add a certificate format. It checks the computational scope
of the existing exact source compiler, with reductions, a standard tractable
observation class, and independent executable controls. Manuscript writing is
on hold. The main compilation theorem's originality is not settled by this audit.

Read [THEORY.md](THEORY.md) for the complete arguments and
[SOURCES.md](SOURCES.md) for the close predecessors and inspection limits.

| Task | What is established here |
|---|---|
| Construct every source recognizer uniformly in polynomial time | Would decide subgroup-specific DDH, even on a two-dimensional diagonal source; a conditional barrier, not an unconditional impossibility. |
| Query a complete target after correct compilation | The preceding source theorem supplies this. Membership does not include a first-hit index. |
| Find a completion of a partial coordinate target | NP-complete even for a formula-independent family of easy invertible binary sources. |
| Answer every partial target using polynomial-size source-only preprocessing | Would imply NP is contained in P/poly; the query procedure must be uniform. |
| Give polynomial-size deterministic static proofs for all guard avoidance | Would imply NP=coNP. This does not exclude sound incomplete methods. |
| Count guard matches | #P-complete for a finite horizon; hardness already holds within one known least period. |
| Observe a closed linear quotient, LA=BL | Reduces exactly to a full-state target problem for the quotient recurrence. This is known quotient/lumping mathematics, not a new analyzer. |

The hardness construction adapts the explicit prime-period 3SAT reduction in
Fernau-Hoffmann-Wehar's Appendix C. It is a theoretical boundary, not an attempt
to manufacture a favorable performance benchmark. The source depends only on
the variable count, not on a SAT formula; the latter changes only the coordinate
query. An ordinary CRT procedure recognizes every complete state of those same
sources efficiently, without needing our general compiler at all.

## Executed controls

`check.py` compares 755 formula instances against direct Boolean truth tables
and all times in their finite clock periods, totaling 297,747 guard evaluations.
The matching counts agree exactly with the number of satisfying assignments.
The fixed binary source construction is checked on arbitrary vectors for
linearity and invertibility, not only on its reached states.

A 24-dimensional source is also processed by the existing general compiler and
compared with its simpler source-aware membership procedure. Small DDH-relation
controls use 34 source compilations and 13,498 target queries. These groups are
easy; the tests establish the reduction identity, not the DDH assumption.

For linear observations, 402 matrix/observation pairs are checked independently
against kernel invariance. The 102 eligible pairs give 5,280 quotient queries
compared with projected original trajectories. For each of the other 300 pairs,
a same-observation/different-successor counterexample is retained by the checks.
The quotient compilation cache has 22 distinct small sources. These are exact
controls, not native performance measurements or formal verification.

## Reproduce

Python3.10+ and the standard library suffice. From a full repository checkout or
the explicitly labeled source-subset delivery:

```sh
python research/query_scope_v1/verify.py
python -O research/query_scope_v1/verify.py
```

The verifier checks pinned source and dependencies, regenerates the report in a
temporary directory, and compares the exact bytes with the saved report. It does
not install software, access the network, alter old fixtures, or benchmark a
native SAT/automata/quotient tool. The new root regression gate runs this audit
without modifying production schemas or historical evidence.

`controls.py` is diagnostic/reduction code. It is not a hardened parser or an
exact general partial-observation decision procedure. Its complete finite-field
inputs are supplied by the tests; invalid/ineligible quotient matrices are not
converted into unreachable answers. `ClockSource` has a polynomial-size explicit
binary matrix, represented sparsely for convenient exact tests, not a succinct
oracle encoding an exponentially larger matrix.

## Research decision

These results complete important scope arguments needed before writing claims
about the compiler. They do not clear the prior-art comparison for its main
certificate contract or establish a practical advantage. The next assessment
should compare that exact contract with equally compact, certifying cyclic-group
and invariant methods. Neither free source synthesis nor generic guard solving
may be used to inflate the claimed consequence.
