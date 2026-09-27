# Bounded comparison design: conventional algebra to a checked witness

Status: requirement and study design fixed; executable protocol and native
results pending. This file is not a claim that a preregistered blind experiment
has been completed. The cases have earlier exploratory observations.

## Consumer, source and accepted result

The consumer requires an AIGER safety witness checked against the separately
supplied original model through the pinned Certifaiger pipeline. All nine
outputs emitted by the current pinned tool must yield UNSAT with successful
native LRAT replay. A producer's SAFE message, a custom algebraic verdict, or
an unchecked witness is not acceptance. Subsequent independent Python replay
checks the retained completed CNF proofs separately.

Keep the upstream arbitrary-input/reseeding behavior, initial state and complete
bad-output property. Use the original files at upstream commit
`c8efd0251c0548dd46168db8410e6777c5f82b73`:

| Width | File |
|---:|---|
| 2 | `fibonacci-02-0x3.aag` |
| 4 | `fibonacci-04-0xc.aag` |
| 8 | `fibonacci-08-0xb8.aag` |
| 12 | `fibonacci-12-0xe08.aag` |
| 16 | `fibonacci-16-0xd008.aag` |
| 24 | `fibonacci-24-0xe10000.aag` |

These are exactly the six widths selected in Gate 10, from a published
hand-designed test family. They are neither industrial designs nor a sample
supporting a claim about all hardware verification. Bind each file to
`../aiger_lfsr_v1/SOURCE_MANIFEST.json` before execution.

## Routes and fair interpretation

| Route | Required role | Interpretation |
|---|---|---|
| Existing odd-order history exporter | Candidate; conventional source-aware construction | Must validate the raw wrapper, supplied exponent and factorization; no complete orbit engine is used |
| Pinned rIC3 with witness output | Mandatory existing certifying baseline | Original model to accepted witness under the same external checker and resource policy |
| Existing direct squarefree structural checker | Decision-only reference | Same source property, different trusted checker and no standard witness; report its cost and trust boundary separately |
| Historical ABC PDR and exported invariants | Retained diagnostic reference | Earlier unmatched observations; not the sole competitive baseline |

For the exporter, provide the explicit structural hints `n`, `taps` and
`M=2^n-1`, and charge validation and factorization. These hints are readily
derived from the named source family but are additional structural knowledge
compared with a generic AIGER solver. Record this asymmetry. An invalid or
unsupported hint is a construction failure, not a solver timeout. The external
checker receives the original model independently and must not trust a hint.
Do not claim a general solver or a factorization-free construction.

The same conventional mathematics is allowed on every route. There is no
artificial restriction forcing a source-aware competitor to enumerate orbits.
The exporter is already the strongest identified source-aware route to this
witness; duplicating it under a different name creates no independent advantage.

## Tool qualification before measurements

Obtain rIC3 from its official source/release provenance, record the exact commit,
dependencies, compiler/build configuration and executable hashes, and inspect
the documented witness-output option. Select one documented single-worker
IC3 configuration for the single-worker comparison. Keep its default
preprocessing; do not disable useful baseline features merely to simplify
checking. State that this excludes the default parallel portfolio and does not
establish superiority over all rIC3 configurations or hardware solvers.

Qualify parsing and certificate compatibility on one explicitly labeled tiny
smoke input before freezing the executable protocol. Smoke costs and outcomes
are not benchmark measurements. If the current producer/checker formats do not
interoperate, document the mismatch; do not patch either solver or silently
weaken the acceptance condition. A documented compatible pinned version or an
untrusted adapter requires a separate recorded compatibility decision first.

The Certifaiger/AIGER/CaDiCaL/lrat-trim pins remain those in Gate 12. A rebuilt
binary gets new provenance rather than edits to historical hashes. Freeze all
commands, source and binary hashes, case order and the resource harness before
timed runs. A source candidate is pinned in
[BASELINE_QUALIFICATION.md](BASELINE_QUALIFICATION.md); qualifying its executable
and completing this freeze are still open. The protocol must specify descendant
termination, monitoring of temporary as well as retained artifacts, and bounded
stdout/stderr capture so that subprocesses cannot escape the declared budget.

## Resource and accounting policy

Run sequentially, with three fresh-process trials per case and route. Alternate
the two witness-producing routes by trial; record the exact deterministic order.
Use one CPU, at most 1 GiB address space per process (including Python producers,
adapters and every descendant), a 30-second total
workflow deadline, and 64 MiB total raw circuit/CNF/proof artifacts per trial.
The new orchestration must enforce the remaining total deadline across stages;
the old ten-seconds-per-process runner alone does not do this. Do not claim
one-GiB aggregate memory unless it is actually enforced across descendants.

Start total timing before reading/converting the original source and stop after
the final native proof check. Charge source recognition, algebra, factorization,
construction/export, adapters, format conversion, obligation generation, SAT
search, LRAT replay and orchestration. Record phase times inside this total.
Exclude tool builds, but record their setup separately. Report the later Python
offline replay separately; it is not hidden inside native acceptance timing.
Use the same conversion-validation policy for both routes, or report and justify
any asymmetry before execution. Fresh process does not imply cold filesystem
caches; record the environment and avoid unrelated simultaneous measurements.

Retain witness bytes, raw and compressed evidence bytes, CPU/wall observations,
all command arrays, stdout/stderr, exit codes, partial outputs, and stage status.
Resource exhaustion is UNKNOWN. An invalid witness is rejected; it does not
make the original model unsafe. Native UNSAT without successful proof replay
does not count. Do not time outliers selectively, substitute medians for failed
trials, or treat a deadline as the unknown actual completion time.

## Decision and stopping rule

Primary exploratory outcome: accepted case coverage under this common total
budget. A repeatable added-coverage result requires at least one fixed original
case accepted in all three exporter trials while all three qualified rIC3
trials return UNKNOWN specifically because of the declared time, memory or
artifact limits. Build, setup, parsing or interface failures remain BLOCKED.
Unexpected crashes, invalid witnesses and inconsistent verdicts are correctness
or execution issues to investigate, not performance wins for the other route.
Report any reverse wins and all mixed outcomes equally. If each route has
exclusive cases, describe complementary coverage, not overall superiority. This is a
scoped configuration/corpus observation, not a statistical population claim or
proof of hardness. Existing tiny positive and corrupted-witness controls must
continue to behave as specified; a counterfeit accepted anywhere suspends the
study until the discrepancy is resolved.

If both routes cover the same cases, or the exporter has no repeatable added
coverage, this primary benefit hypothesis fails. Report timings and artifact
sizes descriptively, with medians and full ranges for completed trials; do not
replace the failed primary criterion with a post-hoc speedup claim. A positive
coverage result permits a focused significance/priority review, not an automatic
claim of publication readiness.

If rIC3 cannot be qualified, record the blocker and retain an incomplete
comparison. Do not fall back to an ABC-only success claim. After a completed
negative result, close this benefit route without enlarging widths, changing
budgets or inventing another format to obtain a favorable result.
