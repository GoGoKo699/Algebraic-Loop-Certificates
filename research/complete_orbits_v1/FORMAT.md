# Experimental certificate interface

The root `alc/` API is unchanged and remains authoritative for its existing
positive certificate format. This directory adds a research-only interface:

```python
from research.complete_orbits_v1.checker import decide
result = decide(problem_document, certificate_document)
```

The problem uses the production `alc.problem.v1` prime-field encoding. Its
modulus, shape, canonical residues, dimensions and integer limits are parsed by
`alc.schema.Problem`. The certificate must be independently bound to the
problem fingerprint. The checker does not accept the producer's input in place
of an independently specified problem.

## Exact top-level fields

* `schema`: exactly `alc.algebraic-decision.v1`.
* `problem_sha256`: production canonical-problem fingerprint.
* `prime_proofs`: existing production Lucas-Pratt records.
* `inverse_matrix`: an inverse of the original A, checked on both sides.
* `components`: the primary-factor proof data below.
* `claim`: either `{"status":"unreachable"}` or
  `{"status":"reachable","first":t0,"period":r}`.

Unknown fields are rejected. An `unknown` producer outcome is not a certificate.
JSON clients should use the production `load` routine for duplicate-key, byte,
UTF-8 and nonfinite-number checks. This module consumes parsed objects and is
not an unbounded public JSON service.

## Components

Each object has exactly `factor`, `multiplicity`, `order`, `order_factors`, and
`log`. Polynomials are canonical arrays of coefficients in increasing degree.
Factors must be distinct and monic with nonzero constant coefficient. A trailing
zero, excessive degree, incorrect product or reducible purported factor is
rejected. The checker computes the initial-vector minimal polynomial itself,
then checks that the supplied factors and multiplicities reconstruct it.

`order` is the exact multiplicative order of X modulo this irreducible factor.
`order_factors` uses the production complete proved-prime factorization format.
`log` is the least local residue t_i in `[0,order)`, checked by exponentiation.
It is null only if the target residue is zero or fails the subgroup order-power
identity; a missing logarithm for a locally reachable residue is invalid proof,
not evidence of unreachability.

If the target is outside the cyclic span, `components` must be empty. The
checker derives that fact by exact linear algebra and still checks the field
and inverse witnesses. An inside-span target must have the complete primary
factorization, including repeated factors.

## Result

An accepted result has `verified:true`, the problem binding, and either an
empty-set status or a canonical `(first,period)`. It also has a checker-generated
reason, cyclic degree, and any unipotent digit trace. The claimed outcome is
compared with the actual algebraic calculation; modifying it cannot turn a
failed proof into a correct one.

The negative reasons are `outside_cyclic_span`, `field_subgroup_obstruction`,
`incompatible_field_congruences`, `unipotent_digit_mismatch`, or
`unipotent_mismatch`. These are different mechanisms with the same exact
conclusion. In particular, `unipotent_*` handles repeated-factor information
that disappears in the simple field residues.

## Producer and limits

`producer.produce(problem, max_work=..., supplied_factors=...)` returns a
candidate or an unknown result. Its trial factorization and witness search are
budgeted, and a baby-step/giant-step table is budget-checked before allocation.
The generator computes potentially difficult auxiliary arithmetic, so zero
trajectory steps is not a claim of polynomial production time.

The optional supplied polynomial factors are untrusted candidate data. The
checker must still verify irreducibility, multiplicity and exact product.
Producing or obtaining those factors belongs in an end-to-end cost comparison.
Neither the factor hint nor a candidate certificate is trusted automatically.

The new code imports no producer from its checker path. It shares exact
polynomial arithmetic with its experimental producer and the existing primary
parsing/primality routines. Independent direct trajectories, independent trial
irreducibility, direct finite unipotent subgroups and a native SymPy check are
used in validation. This is implementation diversity, not a formal soundness
proof of Python or a guarantee against all resource-exhaustion attacks.

## Scope remains narrow

Inputs are prime fields, invertible affine maps, one initial state and a full
state target. Derived extension fields inside the proof do not make arbitrary
extension-field inputs supported. Machine-word wraparound, arbitrary programs,
guards, changing inputs and singular maps are not silently added.
