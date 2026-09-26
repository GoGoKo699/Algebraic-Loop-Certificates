# One checked source, exact answers for every later target

This experimental module compiles an invertible affine recurrence over a prime
field into an exact initial-orbit recognizer. Its source input has **no target**.
After the certificate is checked, every full-state query is classified as
reachable or unreachable. No new finite-field target logarithm is calculated.
The first hit time is NOT returned, and synthesis may still be expensive.

The primary API, old separating predicates, and modular decision schemas are
unchanged. Old individual invariants retain their `not_excluded` semantics.
Only this format checks the additional completeness obligations that justify
an exact membership answer. Manuscript writing remains on hold; novelty and
practical superiority have not been established.

[THEORY.md](THEORY.md) proves the source-only result, gives its complexity, and
characterizes when a subset of compatibility checks is complete.
[SOURCES.md](SOURCES.md) explains why compact invariant circuits and expensive
preprocessing are themselves established ideas, not new contribution claims.

## Use a checked fixture

```python
import gzip
import json
from pathlib import Path
from research.compiled_orbits_v1.checker import compile_orbit

r = json.loads(gzip.decompress(Path('research/compiled_orbits_v1/expected.json.gz').read_bytes()))
f = next(x for x in r['fixtures'] if x['name'] == 'exact_twelve_state_orbit')
orbit = compile_orbit(f['source'], f['certificate'])
print(orbit.query([10, 8])['status'])   # reachable
print(orbit.query([10, 12])['status'])  # unreachable
print(orbit.query([0, 0])['status'])    # unreachable, not merely not_excluded
```

The source is F(s,t)=(4s,5t) over F13 from(1,1). The earlier single invariant
s^3=t^2 contained13 states, including the unreachable origin. The new complete
predicate contains exactly the12 orbit states. Its certificate is604 compact
JSON bytes. This is larger than the418-byte single invariant because it proves
more; it is not claimed smaller or faster than every alternative.

## Proof and query boundaries

`alc.orbit-source.v1` has fields `schema`, `field`, `matrix`, `offset`, `initial`.
`alc.compiled-orbit.v1` has `schema`, `source_sha256`, `prime_proofs`,
`inverse_matrix`, `components`, `comparisons`. The primary problem parser checks
the same arithmetic semantics through an internal instance with target=initial.
The target-free schema rejects unexpected fields, including a supplied target.

Each component contains a verified irreducible factor, its multiplicity, the
exact order of X in its residue field, and verified order factors. Each
comparison identifies two components, a quotient algebra, its two evaluation
roots and a checked base alignment. Missing components or missing compatibility
coverage reject compilation, even if the surviving predicates are all inductive.

Compatibility edges must connect every prime-power support, not just the overall
graph. Orders6,10,15 can require a triangle; a star misses the condition modulo5.
The bounded reference producer chooses the union of prime-wise maximum-valuation
stars. It does not claim an optimal number of edges.

`producer.produce(source)` has no target argument and returns a candidate or
unknown. Candidate data are not trustworthy until compiled. Querying a compiled
object uses only its validated polynomial/coordinate operations. The specialized
nilpotent routine extracts characteristic-adic digits; its work is not hidden by
the phrase 'no finite-field target logarithm'. Loading a saved certificate into
a new process requires rechecking it, not trusting a Python dataclass name.

## Reproduce

```sh
python research/compiled_orbits_v1/verify.py
python -O research/compiled_orbits_v1/verify.py
```

Python3.10+ and the standard library suffice. No network or package installation.
The verifier checks a dependency manifest and regenerates exact results only in
temporary storage. Existing evidence is never overwritten.

The audit constructs657 source objects. For655 of them it checks all possible
states (5,354 queries), including repeated factors and extension-field pairs.
Two additional sources receive430 orbit/random controls and240 independently
closed-form controls. These are source and query counts, not applications.
The graph criterion is compared with all residue assignments for1,728 graphs,
covering74,088 assignments;216 hub graphs are checked. Eighteen malformed or
incomplete certificates are rejected. Query-only tests disable irreducibility
and linear solving after compilation and ensure no producer is imported.

The 65,537-characteristic control uses a source-visible repeated-root model and
supplied polynomial factors. It is not a discovery benchmark. The source maps,
compilation effort, and desired output must remain equally available to classical
competitors. No native invariant package, proof assistant, whole-program frontend
or asymptotic performance separation was tested.
