# Research continuation: modular membership without recovering the target phase

27 September2026. Manuscript writing remains on hold. All prior primary APIs,
historical sources, fixtures and license bytes remain unchanged.

The live baseline is `0ccc0f8aba93944ba488ed05111e50772f215574`. It already includes
an independently developed query-scope audit. The supplied pending query-boundary
checkpoint is preserved separately through the eleven-member archive and runner
in [audits/query_boundary_checkpoint_v1](../audits/query_boundary_checkpoint_v1/README.md).
Its file bytes and the original delivery/patch hashes are recorded. The overlap
with the live scope audit is explicit; no old file is replaced or rebranded.

## New technical result

[The prime-power theorem](prime_power_compilation_v1/THEORY.md) reduces a source-
only exact orbit recognizer over Z/p^eZ to ONE source-only prime-field recognizer,
plus deterministic polynomial-time finite-module arithmetic. It requires neither
a target's residue logarithm nor a sequence of target-dependent field certificates.
The source includes the explicit binary modulus; there is no hidden complexity
claim polynomial in the bit length of a succinctly supplied enormous exponent.

The crucial object is the initial cyclic module M, not just the original
coordinates modulo p. M may have generators of different p-power orders.
The correct field reduction is M/pM. A target in M defines a well-determined
endomorphism B=h(C) of that module. Once its residue passes the field predicate,
B belongs to <C> exactly when B^m belongs to <C^m>, with m the prime-to-p part
of the residue action's order. The latter cyclic p-group test has an explicit
coefficient-based digit calculation and exact replay, without a p-sized search.

The compiler returns exact all-target membership and the common point period,
not the first hitting time. Only supplied prime powers are covered; arbitrary
composite-modulus source compilation and richer guards are not inferred.
A proof-existence/verification reduction is not a uniformly fast synthesis theorem.

## Evidence completed

The deterministic audit compiles1,414 sources and checks25,189 full-state targets
on1,411 small sources. It separately checks256 modular spans and23,201 cyclic
p-group membership questions on mixed-order modules.380 source modules have
unequal generator orders. Three larger source-visible controls receive138
closed-form queries. False bindings, missing prime/residue evidence, forged
inverses, inconsistent explicit moduli and malformed targets are rejected.

The optional SymPy1.14.0 audit compares120 normal forms and2,868 scalar subgroup
queries on76 sources. Its scalar comparator also avoids target logarithms; it
is not an enumeration strawman. No native general matrix-orbit compiler or
performance comparison was run. Two64-bit controls have531-byte source
certificates; they are known easy families, not speedup evidence.

## What the new comparison prevents us from claiming

[The source dossier](prime_power_compilation_v1/SOURCES.md) includes Hillar-Rhea's
mixed endomorphism representation and modulo-p automorphism criterion,
Banin-Tsaban's field reduction for End(Z/pZ+Z/p^2Z), generic p-group algorithms,
scalar lifting, and current finite-ring dynamics work. Neither mixed modules,
characteristic-digit calculations nor prime-power lifting is claimed new.

The precise candidate is the checked all-target reduction with its torsion and
bit-cost obligations and no target-phase recovery. It remains to establish
whether a certifying implementation of prior finite-module methods already
yields the same guarantee or what independent improvement this contract adds.
The main field compiler's priority gap is not erased by extending its domain.

Thus the technical research advanced, but overall scientific readiness remains
incomplete. These files support later claims; they are not manuscript sections.
Remote integration and actual CI conclusions are recorded in Git history and
delivery receipts, not assumed from this static scientific note.
