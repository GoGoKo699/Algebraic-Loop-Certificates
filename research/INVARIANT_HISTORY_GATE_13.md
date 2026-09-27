# Gate 13: the invariant/history distinction and its predecessor

27 September 2026. Manuscript preparation remains on hold.

## Decision

**Stop pursuing this construction as a standalone novelty claim.** The
forced inverse-bit predicate is a concrete instance of an established
separator construction from proof complexity. Keeping its inverse witness as
history gives a useful hardware-verification integration, but does not by
itself establish a new complexity separation or an advantage over the
source-aware classical comparator.

This decision closes the conceptual comparison requested by
[gate 12](ODD_ORDER_WITNESS_GATE_12.md). It does not invalidate the exact safety
proofs, the native witness experiments, or their independently replayed CNF
proofs. Those remain reproducible integration results. The decision is about
what research claim they justify, not whether the implementation works.

## An exact correspondence, not just a resemblance

Fix a primitive binary update A of width n and a nonzero seed s. Put
M=2^n-1. Extend the orbit map to a permutation on all n-bit inputs:

```
h_s(t) = A^t s,  0 <= t < M;
h_s(M) = 0.
```

The nonzero orbit contains each nonzero vector exactly once, and the spare
input maps to the spare output. Repeated squaring evaluates this permutation
efficiently. No hardness assumption is needed to define it.

For every inductive safety invariant I over the original state, the reachable
states force inclusion of the correct phase parity, and a future bad trace
forces exclusion of the opposite parity. Consequently

```
I(r,s,0) = [least significant bit of h_s^{-1}(r) is zero]
```

for every r. The r=0 boundary also works: the original bad detector immediately
excludes it when s is nonzero, and its inverse index M is odd. Thus there is
no output-domain promise in this fixed-seed primitive case.

Bonet, Pitassi and Raz, *On Interpolation and Automatization for Frege Systems*,
SIAM Journal on Computing 29(6), 2000, §1.2, p.1942, explicitly presents the
Krajíček–Pudlák construction: split the graph of an injective forward map by
one input bit; any separator on the output must recover that inverse bit.
The correspondence above instantiates that construction. This is our
deduction from the primary source, not a claim that their paper contains the
LFSR monitor or its native witness. The [source dossier](invariant_history_v1/SOURCES.md)
records the exact source, reading depth and nearby comparisons.

The transition monitor makes one inverse-bit class reachable and the other
eventually unsafe. The history predicate keeps the inverse witness t as
state instead of reconstructing it. The additional temporal argument is
valid and useful, but no consequential new theorem has emerged from it in
this audit.

## What the precise result says

[THEORY.md](invariant_history_v1/THEORY.md) states the generic odd-cycle
version and its hypotheses. The key boundaries are:

* Forced agreement holds on active same-orbit pairs. Arbitrary invariants may
  differ elsewhere; the reachable set and greatest safe set are not globally
  identical.
* Recovering the whole phase from parity uses O(log M) queries. A polynomial
  running-time claim also needs efficient jumps by a binary-encoded exponent;
  a cheap one-step transition is insufficient. Matrix powers provide those
  jumps in this workload.
* An exact evaluator, an efficiently constructed evaluator, and a nonuniform
  circuit family are different resources. The argument does not prove a
  superpolynomial circuit bound or cryptographic security for binary fields.
* Existentially quantifying the history gives a short quantified circuit with
  only original free variables. Also quantifying its gate values gives a
  short quantified Boolean formula. The issue is deterministic membership
  evaluation after eliminating the witnesses, not arbitrary formula length.
* With g Boolean history bits and an extended predicate of evaluation cost E,
  enumerating history values evaluates the projection in O(2^g E). This is
  elementary existential elimination, not a new lower bound or a proof that
  the current history register is optimal.
* Definitional auxiliary gates can compress a CNF while remaining efficiently
  evaluable from current state. Actual history state is a different resource.
  Neither type of extension automatically gives short native SAT proofs.

These distinctions prevent importing a CNF-specific lower bound, a black-box
inference lower bound, or an observed solver timeout into a claim about all
original-state Boolean circuits.

## Preserved engineering result

The project still supplies a narrow, useful case study: source-bound odd-order
safety for the published reseeding wrapper; ordinary history witnesses through
an existing native interface; and retained SAT proofs with independent replay.
Gate 12 also removes the stronger maximal-period premise, including mixed
seed periods and nonminimal annihilating exponents.

Conventional order and squarefree-polynomial methods can produce the same
witness. The native model/witness-to-CNF translation remains trusted, and a
small witness still generates substantially larger SAT proofs. No additional
native solver experiment was run for this conceptual audit. Its small checks
validate mathematical boundaries, not runtime performance or historical
priority.

## What would justify further research

Close this branch of novelty exploration. Do not add another orbit format,
larger synthetic exponent, finite-field frontend, or history encoding merely
to keep it moving. The missing requirement is an independently motivated
consumer for which a matched cost or assurance improvement survives the
strongest source-aware alternative.

Any future candidate must first specify the source semantics, accepted proof
interface, existing method, and a falsifiable success/stopping condition.
Assess the requirement before implementing the candidate. An unverified
frontend is a real assurance boundary, but its existence alone does not
establish a novel research opportunity. If no such candidate is found, retain
this repository as a checked implementation and integration study rather
than declaring scientific completion.

This is a bounded contribution decision grounded in a direct predecessor.
It is not a claim to have exhaustively searched all literature or proved
that the exact concrete monitor has appeared before.
