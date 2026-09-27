# Matched audit of the prime-power lifting step

**The target-phase-free step has a conventional primary-decomposition
explanation. It should not be the standalone novelty claim.**

This audit adds no new certificate format or supported domain. It compares the
existing source compiler's final membership reduction with a Chinese-remainder
projector version derived from standard finite-group decomposition. Both use
the same checked source, cyclic module, field certificate and p-group primitive.
See [THEORY.md](THEORY.md) for the proof and [SOURCES.md](SOURCES.md) for exactly
what the comparison establishes. This is not an independent full compiler or
a native implementation retrieved from an earlier paper.

## Result

For commuting g,h under a homomorphism with p-group kernel, write the quotient
order of g as m*p^b with gcd(m,p)=1. Then

    h in <g> iff image(h) in <image(g)> and h^m in <g^m>.

The existing lifting predicate is an instance. The alternative explicitly
projects a residue-compatible target to its p-primary component and checks that
component. It needs the same one field certificate, no additional serialized
proof, no target finite-field logarithm, and polynomial query work. This does
not settle novelty of the shared field-source compilation theorem.

One unsafe shortcut is retained: the source period is NOT an order bound for
all residue-compatible targets. For x -> -x modulo25 from1, the source orbit
is {1,24}, but target6 passes reduction modulo5. Using the source's absent
5-part as an ambient bound would accept6 incorrectly. Both proper methods
reject it. This is a falsified shortcut, not a discovered bug in the old code.

## Reproduce

```sh
python audits/primary_splitting_v1/verify.py
python -O audits/primary_splitting_v1/verify.py
```

Python3.10+ and the standard library suffice. No network, software installation,
fixture overwrite, new source schema, or manuscript text is involved.

The exact comparisons cover1,408 sources and25,068 targets, including370
mixed-order source modules. A further294 queries replay six saved certificates.
Abstract groups provide40,060 source/target comparisons across540 generators.
Counterexamples test loss of commutation, an incorrect kernel characteristic,
and inadequate target-order bounds. An independent trajectory oracle checks
small full-state truth; shared compiler/decoder code is explicitly not counted
as independent validation of those shared layers.

The adapter is internal audit code. It is not exported as a new production API.
Existing manifests and source files are unchanged. A new regression gate joins
the full repository tests. [The assessment](../../research/CONTRIBUTION_ASSESSMENT_07.md)
records the revised scientific priority. Manuscript writing remains on hold.
