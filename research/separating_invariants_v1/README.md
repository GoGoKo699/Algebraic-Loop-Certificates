# Reusable separating invariants (experimental)

**Prove a preserved relation, then exclude every target that violates it.**
The source binding includes the recurrence and initial state, not the queried
target. This directory adds a research-only predicate checker; it does not
change the primary API or the complete modular decision format.

[THEORY.md](THEORY.md) proves that three schemes suffice for all unreachable
targets of invertible affine maps over prime fields: the initial cyclic span,
a power preimage of a cyclic unipotent subgroup, and equality of two powers
with a common update multiplier. Witnesses and checking have polynomial bit
bounds. The checker needs no complete polynomial factorization, irreducibility
test, field-order factorization, or field logarithm of the target. It still
checks p's primality and the map's invertibility.

[SOURCES.md](SOURCES.md) records direct invariant-theory predecessors and the
limits of the novelty audit. These are research proofs and evidence, not a
manuscript. Publication-level originality and practical advantage remain open.

## Example and precise outcome

Over F13, `(s,t) -> (4*s,5*t)` from `(1,1)` preserves `s^3=t^2`. This excludes
`(10,12)` and 155 other states. Its invariant includes `(0,0)`, which is actually
unreachable: satisfying the invariant is **not** a reachability proof.

From a checkout:

```python
import json
from pathlib import Path
from research.separating_invariants_v1.checker import compile_invariant

report = json.loads(Path('research/separating_invariants_v1/expected.json').read_text())
f = next(x for x in report['fixtures'] if x['name'] == 'same_multiplier')
invariant = compile_invariant(f['problem'], f['certificate'])
print(invariant.query([10,12])['status'])  # unreachable
print(invariant.query([0,0])['status'])    # not_excluded
```

The same checked predicate can handle further independently supplied target
states. Changing p,A,c or the initial state invalidates the source binding.
The proof is not a certificate of how source code was translated into the
supplied recurrence. It does not decide arbitrary guard disjointness.

## Producer versus checker

`producer.produce(document, max_work=...)` tries to construct one excluding
invariant. It may return a `candidate`, `no_exclusion`, or `unknown`.
Only compilation plus a false predicate evaluation proves unreachability.
`no_exclusion` is not a certified positive time result. The producer can factor
polynomials and integers, search field embeddings, and align powers of base
elements by a discrete logarithm. These operations may be expensive. It does
not request a finite-field logarithm of the target. Its shared nilpotent routine
does compute elementary p-adic digits, and those costs remain included.

The certificate object has schema `alc.separating-invariant.v1`, fields
`source_sha256`, `prime_proofs`, `inverse_matrix`, and `invariant`. It accepts
only the exact fields for the declared scheme. `compile_invariant` checks the
entire construction. JSON users should retain the production bounded/duplicate-
key-rejecting loader. In-process objects are not hardened unforgeable proof tokens.

## Reproduce

Python3.10+ and the standard library. No network or package installation:

```sh
python research/separating_invariants_v1/verify.py
python -O research/separating_invariants_v1/verify.py
```

The audit covers5,189 small decisions:2,876 negative certificates and2,313
reachable controls. It checks706 distinct predicates over their full small
state domains, for6,562 one-step induction implications. Another2,876 tests
legitimately change the queried target without changing the proof.324 negatives
are also checked by the earlier complete decision system. Malformed quotient
maps, update multipliers, factors, states and source bindings are rejected.

The named elementary examples have certificates of418,299,321 and323 compact
JSON bytes, respectively. Their older complete certificates have565,431,334
and372 bytes. This is a local comparison of formats, not an advantage over
all known invariant or certifying algorithms. Larger common comparison algebras
may make a new witness more expensive than the previous one. No general witness-
size dominance, faster synthesis, or irreducibility-test lower bound is asserted.

The old proofs and result files are unchanged. The new manifest pins dependencies.
Tests independently step the small recurrences; only the test oracle enumerates
orbits. Exact tests are not a proof-assistant formalization or a production
analyzer benchmark.
