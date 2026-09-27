# Existing hardware proof interface

The independently trusted problem is an original circuit from
`../aiger_lfsr_v1/upstream/`. Its inputs remain unconstrained, its latches are
zero initialized, and its sole output must remain false for every execution.
The circuit includes arbitrary nonzero reseeding. All original bytes and the
earlier odd-order checker are preserved.

The new artifact is an **untrusted AIGER witness circuit** for Certifaiger.
Producing this artifact, passing Python checks, or finding an algebraic order
does not by itself establish external acceptance. External acceptance requires
all of Certifaiger's applicable simulation and induction obligations to be
discharged. Failure, timeout, or unsupported proof syntax is inconclusive.

## Two producers, one interface

The native baseline exports ABC PDR's forbidden cubes. Their disjunction is
the complement of its invariant. The witness preserves all original latches
and uses that invariant as its safety property. Certifaiger separately checks
that it implies the original property. Exported support and latch order must be bound to the actual model;
an ABC verdict or an unbound PLA file is insufficient.

The algebraic producer adds n history latches for a phase t. It retains every
original input, latch reset, next-state function and bad signal, with explicit
literal mapping. Adding latches shifts the original gate literals but changes
no original equation. Its sole output is original_bad OR NOT H, where

```
H = (r = s = 0 AND t = 0)
    OR (s != 0 AND t < 2^n - 1 AND r = A^t s AND c = t mod 2).
```

The history starts at zero, resets to zero on nonzero input, inactive seed, or
an imminent return, and increments otherwise. The inactive disjunct leaves c
unrestricted. Controlled constant matrix powers implement A^t s without
enumerating the orbit. The construction and its bounds are in THEORY.md.

This H requires every nonzero state to have exact period 2^n-1. Merely checking
an odd multiple of the matrix order is insufficient. Producer-side checks can
prevent wasting effort on unsupported inputs; the external witness checker
must still establish the entire circuit-level claim. This is a restricted
research producer, not a replacement for the more general odd-order theorem.

## Trust and replay

The interface checks shared-latch reset and transition simulation, implication
of the original safety property, and the witness's base and inductive steps.
Constant zero resets make the added-latch reset dependency condition trivial.
Explicit mappings bind every original input and latch; ghosts are unmapped.
There are no additional assumptions, constraints, fairness conditions or
restrictions on inputs.

Certifaiger's obligation construction and AIGER-to-CNF translation remain
trusted transformations. A checked SAT proof establishes unsatisfiability of
the emitted CNF, not independently the correctness of those transformations.
The Python producer and the algebraic argument are not trusted by that path.
Source pins, file hashes, logs and timings preserve what was run; they are
provenance evidence, not substitutes for proof replay. NATIVE_PROTOCOL.md and
the native evidence verifier identify which steps actually ran and which can
be replayed offline.

## Comparison boundary

The conventional squarefree-polynomial method already decides safety for this
wrapper. It can use exactly the same history construction when the stronger
maximal-period premise holds. Thus successful external replay would establish
an integration and assurance improvement over a custom-only proof, not an
advantage of the complete orbit engine over that conventional method.

The original-state parity reduction in THEORY.md is a representation and
evaluation statement. It proves neither an unconditional circuit-size lower
bound nor that this ghost witness will be easy for SAT. Construction cost,
artifact size, obligation generation, solving and proof replay must be exposed
separately. These experiments do not establish general solver limits,
publication novelty, or formal verification of the complete pipeline.
