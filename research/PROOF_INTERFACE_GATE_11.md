# Replaying circuit safety through an existing proof interface

27 September 2026. Manuscript preparation remains on hold. This checkpoint
follows the [source-bound circuit gate](NATIVE_WORKLOAD_GATE_10.md) without
changing its original models or the production `alc/` API.

## The concrete result

An untrusted constructor now emits ordinary AIGER witness circuits for the
existing Certifaiger interface. The native pipeline accepted history-register
witnesses for the original LFSR models at widths 2, 4 and 8. Every one of its
nine generated obligations was translated to CNF, proved UNSAT by CaDiCaL, and
replayed by lrat-trim. ABC's exported invariants at widths 2 and 4 passed the
same pipeline, providing an existing-producer baseline.

The width-8 witness replay took about 3.4 seconds in the single recorded run;
width 8 was the first timeout in the preceding fixed 10-second PDR run.
The [module record](proof_interface_v1/README.md) separates construction,
artifact sizes, native replay and offline verification. This is an executed
integration result on a small published verification family, not a statistical
speedup estimate or an industrial workload claim.

The candidate constructor is outside this acceptance path's trusted boundary.
Certifaiger checks the original circuit separately from the witness, including
the relation between their inputs, resets, transitions and safety properties.
The original arbitrary-reseeding behavior remains unrestricted. Its obligation
generator and the AIGER-to-CNF translation remain trusted; replaying LRAT does
not prove those transformations correct. This is not end-to-end formalization.

## Why adding history is useful here

For a primitive n-bit update A, every nonzero pair (r,s) has a unique phase
t in [0,2^n-1) satisfying r=A^t s. The original counter c must equal t modulo
two. Correct parity is reachable; wrong parity leads to the bad output under
zero inputs. Consequently, every inductive safety invariant over just the
original state bits must encode this parity on nonzero pairs.

The [exact argument](proof_interface_v1/THEORY.md) shows that an evaluator for
that parity recovers the complete phase with O(n) shifted queries. This is an
oracle reduction, not a lower bound on invariant size, SAT-proof length or
runtime. It explains why a short algebraic safety argument need not translate
directly into an easily evaluated invariant over the original bits alone.

An added n-bit history register supplies t along the execution. Controlled
constant matrix powers check r=A^t s with polynomially many Boolean gates.
Reset and induction obligations then establish that the history is consistent
with every original input sequence. The witness does not obtain a phase by
restricting inputs or assuming a discrete-log solution for an arbitrary state.

## The stronger premise and the conventional comparator

This history predicate requires maximal nonzero period 2^n-1. The prior
odd-order proof needed only some odd M with A^M=I, and remains more general.
For example, A=I and M=3 makes the naive phase predicate admit an unsafe
counter value. We preserve that false-witness control rather than silently
strengthening the old contract.

The constructor checks maximal point order by exact powering and prime-divisor
exclusions before emitting a candidate. These are construction diagnostics;
the external pipeline independently establishes its circuit obligations.
No complete orbit compiler is needed. Ordinary primitive-polynomial reasoning
can emit the same witness, and the squarefree-polynomial route still solves
the broader odd-order safety decision. There is no demonstrated advantage over
that source-aware mathematics and no new proof-system claim.

## Research decision

The proof-interface feasibility gate is positive at the measured widths. It
replaces a custom-only acceptance path with actual artifacts accepted through
an existing hardware witness interface and separately replayable SAT proofs.
The retained malformed witnesses, exhaustive small-state checks and explicit
trusted transformations delimit that result.

The next question is whether this integration offers a consequential assurance
or cost improvement over the strongest source-aware implementation at the same
interface. In particular, the simple history predicate spends a stronger
maximality premise than safety itself needs. Resolve that mismatch and inspect
direct predecessors before enlarging the benchmark, adding algebraic formats,
or preparing a manuscript. The engine's originality and scientific completion
remain open.
