# Existing-workload gate: LFSR maximal-period validation

27 September 2026. This protocol fixes the task before the recorded native
run. Manuscript preparation remains on hold. No production API is changed.

## Consumer and comparator

The task is the one supplied by SmokeRand's LFSR analyzer: determine whether a
compiled, supported binary-linear generator has maximal nonzero-state period
`2^n - 1`. This is an existing workload, not a target or horizon chosen to favor
the algebraic-loop engine. The native baseline is SmokeRand itself at commit
`20f3adab3121b4205a12f06746055551e6504648`.

Freeze the following upstream tests, taken from `docs/lfsr.md`, before running:

| Generator | Parameter | Upstream expected category |
|---|---|---|
| shr3 | default | maximal, 32 bits |
| xorrot32 | default | maximal, 32 bits |
| xorrot32 | bad1 | nonmaximal, 32 bits |
| xorrot32 | bad2 | nonmaximal, 32 bits |
| xoroshiro128pp | default | maximal, 128 bits |
| xoshiro256pp | default | maximal, 256 bits |
| splitmix | default | not an accepted binary-linear generator |
| sfc64 | default | not an accepted binary-linear generator |

Build the upstream `smokerand` target and the six required shared-library
plugins using its Makefile. Record the exact compiler, commands, source commit,
binary hashes, exit statuses, stdout and stderr. Run one cold process per case
with a 60-second external timeout. Keep unsupported/nonlinear controls separate
from false maximal-period claims. A timeout or process failure is inconclusive.
Native program exit status alone need not encode the mathematical verdict;
retain the human-readable output and interpret its explicit status.

No exhaustive parameter search, statistical randomness battery, or maximal-period
enumeration is required. Native preprocessing and matrix/polynomial construction
are part of each run; record build cost separately. Single observations do not
justify statistical speedup claims.

## Matched existing-certificate check

For the four 32-bit cases, translate the inspected XOR/shift/rotation updates
to explicit GF(2) matrices, with bit zero first. These operations are linear;
the exact source-to-matrix reasoning must be stated. Initial and target state
are both integer 1. Supply the candidate least period `2^32 - 1`, first hit zero,
and use the unchanged `alc` producer's proof assembly and checker.

Accepting that period for one nonzero point of an invertible linear map covers
all `2^32 - 1` nonzero states, so it answers the maximal-period task. Rejection
alone is not a negative proof: record a concrete failed return or earlier return
to justify each nonmaximal result independently. Charge translation, proof
assembly and verification separately. Do not run the bounded orbit enumerator.
Do not increase root dimension limits or silently substitute a larger research
format for the native 128/256-bit controls; those are native coverage evidence.

## Falsifiable decision

If the native algebraic analyzer resolves the supported advertised controls,
maximal LFSR period is not evidence of a capability gap requiring the complete
orbit compiler. A smaller independent proof may still be useful, but no novel
assurance advantage follows without a matched trust-boundary/proof comparison.

Finite probes of compiled code do not prove arbitrary code is binary linear.
SmokeRand's documented LFSR assumption and our inspected translation must both
be explicit. Nonlinear adversarial inputs outside that assumption will not be
used to manufacture a solver failure. This gate does not validate random quality,
cryptographic security, arbitrary HDL, reset logic, or hardware behavior.
