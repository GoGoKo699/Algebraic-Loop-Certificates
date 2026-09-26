# Prime-power source compilation, without a target phase

Compile an invertible affine recurrence over **Z/p^eZ** once. Reuse its checked
object for every later complete-state target. The source contains no target,
and the query returns exact membership plus the common point period, **not** a
first hitting time. This is a research module; the primary API is unchanged.

[THEORY.md](THEORY.md) proves the reduction to ONE prime-field source certificate,
including initial cyclic modules with different generator orders. The checker
reconstructs that module itself. [SOURCES.md](SOURCES.md) records direct finite-
module and discrete-log predecessors and the unresolved contribution assessment.
Manuscript writing is on hold. No new general DLP or runtime advantage is claimed.

## Why this is not ordinary modulo-p reduction

Starting at5, multiplication by2 modulo25 visits5,10,20,15. All four values are
zero modulo5. The correct reduction retains the cyclic module M and uses M/pM,
which can remember directions lost by reducing ambient coordinates. The code
represents M as a direct sum of cyclic groups of orders p^a_i, with explicit
row-specific arithmetic; it never treats a nonfree module as a vector space.

The source schema is `alc.prime-power-source.v1`, with exactly `schema`,
`modulus`, `prime`, `exponent`, `matrix`, `offset`, `initial`. The explicit modulus
is necessary for the bit-complexity claim; it is checked to equal p^e. The proof
schema `alc.compiled-prime-power.v1` contains `schema`, `source_sha256`,
`prime_proofs`, `inverse_matrix`, `residue_certificate`. One field certificate
is bound to the derived source. It is not an arbitrary lower-precision claim.

The producer invokes the existing field producer once and copies its prime
proofs. Hard source algebra is still charged. The compiler checks that evidence,
normalizes the cyclic module, and prepares the p-primary test. Every target
is converted to a well-defined commuting endomorphism of that module. Its field
membership and one cyclic p-group check decide membership without requiring a
semisimple target logarithm. The characteristic-adic digit work is explicit.

## Reproduce and query

```sh
python research/prime_power_compilation_v1/verify.py
python -O research/prime_power_compilation_v1/verify.py
```

The optional native checks use an already installed SymPy:

```sh
python research/prime_power_compilation_v1/verify.py --sympy
```

```python
import gzip, json
from pathlib import Path
from research.prime_power_compilation_v1.checker import compile_source

r = json.loads(gzip.decompress(Path('research/prime_power_compilation_v1/expected.json.gz').read_bytes()))
f = next(x for x in r['fixtures'] if x['name'] == 'nonunit_point')
orbit = compile_source(f['source'], f['certificate'])
print(orbit.query([20])['status'])  # reachable
print(orbit.query([0])['status'])   # unreachable
```

The core diagnostic compiles1,414 sources;1,411 receive all-target small-domain
checks (25,189 queries). The three larger sources receive138 independent closed-
form queries. It also checks256 modular spans and23,201 mixed-module p-group
queries, plus malformed evidence and query-stage forbidden dependencies.
The exact report is pinned and never regenerated over itself.

Two64-bit scalar sources each have a531-byte source certificate with one field
subcertificate. These are known easy algebraic families; the size is not a
speedup benchmark. A full-state membership object is not a292-byte certificate
for one target's timed progression and must not be compared as the same task.

## Boundaries

Only a supplied prime-power modulus, invertible affine update, one initial state,
and complete-state queries are covered. No arbitrary-composite source compiler,
general guard solver, verified frontend, timing recovery, formal implementation
proof or native full matrix-orbit performance comparison is included. The default
implementation reserves one of the field producer's32 coordinates for lifting;
its raw state-dimension limit is31. The mathematical theorem is parameterized.

The producer may return unknown. Invalid evidence is not unreachability. In-memory
objects should only be obtained by checking the serialized proof; they are not
unforgeable secure capabilities. All use remains exact integer arithmetic.
