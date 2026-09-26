# Scientific scope audit: a tractable predicate need not be tractably searchable

27 September2026. Manuscript writing remains on hold. Existing production APIs,
research certificates, historical fixtures and licenses remain unchanged.
This is a proof-and-comparison pass, not another certificate format.

Read [the query-scope theorem note](query_scope_v1/THEORY.md),
[the source audit](query_scope_v1/SOURCES.md), and
[the executable controls](query_scope_v1/README.md).

## Scientific consequences

The exact source compiler's polynomial checking/query theorem must not imply
free preprocessing. A two-dimensional diagonal source directly encodes the
common-exponent Decision Diffie-Hellman relation. A uniform efficient compiler
for those sources would decide DDH in the stipulated subgroup family. This is
a conditional application of known cryptographic algebra, not a new hardness
assumption or an unconditional lower bound.

Exact full-state membership does not make partial observations inexpensive.
An explicit source family over the fixed field F2, independent of the later
formula, can encode 3SAT solely in selected coordinate values. The construction
adapts the unary-automata prime-period reduction, with a fixed one-hot binary
encoding and basis change. All source matrices are invertible and have odd
order. Their complete-state membership and index recovery are easy by CRT.

The partial-target problem is NP-complete, avoidance coNP-complete, and counting
within a known full period captures #3SAT parsimoniously. Polynomial-size
source-only advice supporting efficient arbitrary partial-target queries would
imply NP subset P/poly. Polynomial static, deterministically checked negative
certificates for all those guard-avoidance instances would imply NP=coNP.
The notes state precisely which bounds and uniformity assumptions yield these
implications; no unconditional separation is asserted.

A positive sufficient scope exists: a full-row-rank observation L with LA=BL
has exact quotient dynamics z -> Bz+Lc from La. A target for that observation
is a complete target for the quotient, so the existing compiler applies there.
This is established exact quotient/lumping mathematics. Failure of LA=BL does
not prove unreachability or hardness; it only invalidates this reduction.

## Executed evidence and what it does not establish

The new deterministic report checks 755 Boolean-formula reductions, 297,747
finite-period guard evaluations, 13,498 common-exponent target queries, and
5,280 projected-orbit/quotient comparisons. Ordinary direct state membership
is retained as the stronger classical baseline for the constructed clock family.
A small source is paired with the existing general compiler; no clock input is
presented as a speedup workload. No native SAT, automata, invariant, or quotient
package was benchmarked. Finite correctness tests do not establish complexity
lower bounds; the written reductions do the logical work.

## What is now closed, and what is not

The background and limitation support is sharper: the source theorem has an
explicit synthesis barrier and a meaningful query boundary, plus a standard
sufficient observation class. Claims about arbitrary guard solving, timing from
membership, or uniformly easy preprocessing are excluded by explicit arguments.

The exact certificate compiler's incremental originality still needs comparison
with a certifying, compact representation of known cyclic invariant/group
methods. The automata reduction and exact lumping must not be presented as new
general principles. The older inaccessible matrix-logarithm scan is not treated
as evidence of novelty. No final scientific-readiness verdict or practical
performance advantage follows from this audit.

The next effort should identify the central theorem-level difference from the
strongest matched predecessor, not add more formats or inflate toy dimensions.
