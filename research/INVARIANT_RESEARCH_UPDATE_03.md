# Research continuation: replace a target-specific rejection transcript by an invariant

26 September 2026. The manuscript remains on hold. Prior implementation and
historical evidence are unchanged. Start with
[the new proof](separating_invariants_v1/THEORY.md) and
[the precise source comparison](separating_invariants_v1/SOURCES.md).

## Mathematical progress

For each unreachable target of an invertible affine recurrence over a prime
field, a polynomial-size certificate from one of three predicate schemes
suffices: the initial cyclic span, a power preimage of a cyclic unipotent
subgroup, or two powers with a common update multiplier in a checked quotient
algebra. The witness certifies initiation and induction independently of the
target. Predicate evaluation then excludes every state outside the invariant.
The proof covers repeated polynomial factors, not only semisimple dynamics.

The new checker does not require a complete polynomial factorization,
irreducibility tests, exact field orders/factorizations, or logarithms of the
target. It does need p's primality proof, an inverse witness, exact cyclic
coordinates, and polynomial arithmetic. Some construction costs are shifted
to a producer that can still perform difficult factoring and base-alignment
logarithms. No efficient general synthesis or blanket size advantage is claimed.

This is a stricter proof-interface result than only validating the final word
`unreachable`: it returns an actual inductive predicate, and the proof is not
bound to a single target. A satisfying state remains `not_excluded` unless a
separate reachability proof is supplied.

## New executed evidence

5,189 finite decision cases; 2,876 excluding certificates; 2,313 reachable
controls; 706 distinct predicates tested over full small state domains, with
6,562 induction implications. Every negative certificate is reused with a
changed target, including its reachable initial state.324 negatives are also
verified by the previous complete decision checker. Malformed relation maps,
common multipliers, divisor claims, query states, and source bindings fail.
A valid reducible comparison algebra passes, illustrating why irreducibility
need not be an exported proof obligation.

The F13 example F(s,t)=(4s,5t) from(1,1) gives s^3=t^2. It excludes156 of169
states, but includes the unreachable origin. Its complete certificate is418
compact JSON bytes versus565 for the earlier target-specific full proof. This
is an easy example and not a claim of uniformly smaller or faster proofs.

## Prior-work finding and remaining novelty obligation

The newly relevant comparison is finite-group separating invariant theory.
Kemper-Lopatin-Reimers2022 already gives finite-field orbit separation results.
Domokos2023 supplies small-support separating monomial structure; for cyclic
diagonalizable actions its two-component consequence directly overlaps our
pairwise semisimple argument. Kohls-Sezer's Theorem1 and cyclic-group Section3
already use quotient/fiber separation and modular-group invariants.

Consequently neither existence of a separating invariant, use of a multiplicative
relation, pairwise semisimple separation, nor quotient/fiber composition is
claimed original. The precise candidate is the typed, executable predicate
representation with complete coverage and explicit polynomial bit/checking
bounds. Whether a certifying version of the preceding constructions already
offers the same guarantees remains an open scientific comparison.

The 1997 matrix-logarithm scan still could not be fully viewed. Only its first
page and printed page27 were accessible in this pass; this retrieval gap has
not been transformed into a claim of originality. All negative evidence and
current source-reading limits are retained.

## Completion status

- The new relative-completeness and induction arguments are written.
- The predicate producer/checker, reuse interface and adversarial tests run.
- The background dossier now includes direct invariant-theory predecessors.
- The overall new-result/priority and matched practical-benefit claims remain
  unestablished. This is not a declaration that the scientific work is complete.
- No manuscript, selected publication venue, release, external contact, or
  promotion of research schemas into the primary API is part of this update.

The next scientific decision is whether the explicit proof grammar yields an
independently useful representation/verifier theorem beyond those predecessors,
not whether another large but easy orbit can be constructed. More implementation
coverage alone will not close that question.
