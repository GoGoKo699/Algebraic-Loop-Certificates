# Gate 18: contribution, assurance, and stopping assessment

27 September 2026. This closes the finite assessment prescribed after Gate 17.
It is a scientific decision record, not a manuscript or a new experiment.

## Decision

The defensible completed result is a **reproducible integration case study**:
conventional odd-order reasoning is compiled into source-bound history witnesses
for the published reseeding LFSR family and checked at an existing native
hardware-verification interface. Under the fixed amended comparison, this route
adds repeatable accepted-witness coverage at width 8 over one qualified rIC3
configuration. Larger cases expose substantial native proof-artifact costs.

The result does **not** presently clear a distinct standalone research
contribution. The closest primary sources already cover witness circuits,
history state, transfer back to the original model, and specialized certifying
workflows that add coverage beyond rIC3. The precise seed-dependent exporter was
not identified in the inspected sources. That leaves its priority unresolved;
it neither proves novelty nor proves that the exact combination is a duplicate.
Known components alone would not rule out a useful new combination, but the
current theorem and six-case evidence do not establish that stronger case.

The bounded study and its contribution/assurance assessment are complete.
**Scientific readiness for a standalone contribution remains uncleared.** Freeze
the present conclusion and evidence here; manuscript preparation stays on hold.
There is no automatic next benchmark, format extension, or solver-budget search.

## The surviving argument in compact form

The mathematical premise is a binary matrix A with A^M = I for an odd positive
integer M, together with a complete factorization M = product_i p_i^e_i.
The implemented frontend recognizes the specific companion-map AAG wrapper;
the more general matrix statement does not make it a general circuit frontend.

For each seed s, let T(s) be its least period. Since T(s) divides M,

    A^(M / p_i^k) s = s  iff  v_p_i(T(s)) <= e_i - k.

There are therefore exactly v_p_i(T(s)) failed fixed-space tests for prime p_i.
Multiplying one p_i for each failure computes T(s) exactly, including T(0) = 1.
This is conventional order extraction expressed as a combinational circuit.
The [existing proof](odd_order_witness_v1/THEORY.md) covers mixed seed periods,
repeated primes and nonminimal annihilators; maximal nonzero period is unnecessary.

An added history counter records the phase since reseeding or return. The
invariant has an inactive zero-register case, and an active case

    s != 0,  0 <= t < T(s),  r = A^t s,  c = t mod 2.

Every active return occurs at t = T(s)-1, which is even. Reseeding resets the
phase, and all other active steps increment it and toggle parity. The inactive
case and the original ungated bad detector are handled explicitly in the full
proof. Total history updates lift every original execution and project back to
it; they do not constrain the original inputs. Native obligations check the
candidate against the original circuit, rather than trusting a substituted model.

With L = max(1, ceil(log2 M)) and E = sum_i e_i, constant-multiplier construction
uses O(n^2 L + L^2) Boolean gates after matrix constants are available. This is
not a bound on factorization, native proof length, or checking time. The existing
O(E n^3 L) statement charges the E fixed-space powers. A bound for *all* naive
matrix precomputation, also covering A^M and the controlled powers when M = 1
and E = 0, is O((E+1) n^3 L). This clarification does not change the frozen code,
proof artifacts, or measurements.

The exporter therefore supplies a concrete implementation of a valid scoped
construction. It does not depend on the complete orbit-certificate engine, and
the conventional source-aware route can construct exactly the same witness.

## What the closest predecessors settle

The [primary-source dossier](contribution_v1/SOURCES.md) records inspected
sections, access limits and the bounded search. The assessment follows from
those sources and the repository evidence; it is not an exhaustive priority
search or an independent reproduction of other papers' experiments.

| Candidate claim | Closest evidence | Assessment |
|---|---|---|
| A new interface for independently checking a hardware witness | S1–S3, S5 and S7 define and implement this architecture | Existing interface; this project is a producer integration |
| Adding history makes certification possible in a new general way | S2 and S4 explicitly construct history-bearing witnesses; Gate 13 already closes the inverse-bit route | No new general history or separator principle established |
| Algebra can exploit sequential hardware structure | S9, S10 and S11 provide algebraic, LFSR and period-computation precedents | The source-aware idea and period mathematics are established |
| Specialized construction plus Certifaiger can add coverage beyond rIC3 | S8 already demonstrates that pattern for sequential equivalence | The general workflow and comparison pattern are not new |
| The exact arbitrary-reseeding seed-period exporter has appeared before | No exact match identified in the inspected constructions | Priority unresolved; absence from this audit is not evidence of absence |
| The present exporter adds accepted coverage under the fixed study contract | Gate 17: width 8, all three repetitions, same original model and checker | Supported for this corpus/configuration only |
| This establishes a general solver advantage or orbit-engine benefit | No matched evidence for either claim | Unsupported |

S4's phase abstraction concerns periodic signals and preprocessing; it is not
the same operation as the seed-dependent phase counter here. S8 concerns
sequential equivalence and different circuits, budgets and configurations.
These are methodological predecessors, not measurements interchangeable with
ours. Their existence narrows the contribution claim without proving that they
implement the exact LFSR selector.

## Evidence and significance

The [completed Gate 17 study](BOUNDED_COMPARISON_GATE_17.md) is unchanged:
54 trials, with nine accepted exporter witnesses, six accepted rIC3 witnesses,
18 structural decisions, nine exporter raw-artifact UNKNOWN outcomes and twelve
rIC3 deadline UNKNOWN outcomes. Widths 2 and 4 pass both witness routes; width 8
passes only the exporter route; widths 12, 16 and 24 pass neither witness route
within the fixed limits. No unsafe conclusion follows from an UNKNOWN.

At width 8 the exporter took 4.396952–4.713342 seconds, median 4.575608 seconds,
and retained 25,241,374 raw bytes each time. Three rIC3 30-second deadlines are
censored observations, not completion times or a measured speedup ratio.
The primary added-coverage condition is true, with no reverse-exclusive case.
That is an empirical result, not by itself a novelty or significance criterion.

The corpus has six predetermined widths from one published, structurally
recognized family. The exporter uses supplied exponent/tap hints and validates
its source contract; the fixed generic rIC3 configuration uses its ordinary
preprocessing. A source-aware conventional competitor has access to the same
algebra and witness construction. The structural reference passes all widths,
but its decision alone is not the required accepted witness. Thus the study
isolates the practical value and cost of this particular export route, not a
general failure of source-aware reasoning or of the rIC3 portfolio described
in S6. It supplies no industrial adoption or cross-family generalization evidence.

The storage amendment was selected after the first experiment exposed an
accounting issue. It preserved the raw cap and added a separate metadata cap,
increasing the possible combined allowance. Its qualification and freeze
preceded a fresh complete sequence. This supports the amended result with an
explicit outcome-informed history, not a blind preregistration claim. The
32-trial suspended Gate 16 prefix and its unevaluated primary criterion remain
separate; no old repetition is pooled, reclassified or selectively resumed.

## Assurance boundary

| Layer | What the retained evidence establishes | What remains trusted or outside the claim |
|---|---|---|
| Original problem | Pinned AIGER sources, source identities, exact inputs and fixed trial order | That these are the intended problem and that AIGER semantics match the intended hardware task |
| Exporter | Source recognition, hints, factorization, kernel computations and circuit generation produce a candidate | These components need not be trusted for accepted original-model safety when the external checker and its translations are sound; they still matter to construction/support and cost claims |
| Native witness checking | The pinned checker consumes both original model and candidate; accepted witnesses pass all nine recorded obligations | Parsing, latch mapping, reset semantics, obligation construction, `aigsplit` and `aigtocnf` transformations |
| SAT certificates | Independent replay of 180 completed study CNF proofs: 135 in 15 accepted witnesses, 45 before interrupted solves | Correctness of the native and Python proof checkers and their runtimes; CNF UNSAT alone does not certify the preceding translations |
| Negative qualification controls | A wrong selector and corrupted reset are rejected; two SAT assignments and 23 completed proofs checked separately | These controls are not an exhaustive soundness proof or additional benchmark trials |
| Resource and time evidence | Fixed supervisor policy, commands, stage records, streams, hashes and outcome reconstruction | OS/runtime behavior, sampled storage observation and shared-host conditions; the caps are not instantaneous aggregate quotas |
| Retention | Hash-checked archive and exact offline reconstruction; all completed and UNKNOWN observations retained | Hashes are neither signatures nor execution attestation; the environment is not a hermetic reproduction of the entire native toolchain |

The version-pinned nine-obligation contract is the one actually executed. The
five safety conditions in older descriptions of Certifaiger are not a reason
to relabel the current files or to claim a new proof interface. The study had
no SAT assignment; its partial completed proofs do not turn interrupted
workflows into accepted witnesses. Qualification and study counts stay separate.

Workflow times include construction and the recorded native acceptance path.
Post-run compression, cleanup and independent offline evidence replay are not
included; CPU accounting also includes cleanup. Replaying the retained CNFs is
valuable extra assurance, not an unmeasured replacement for native workflow cost.
The ten post-run unindexed raw copies remain documented in the
[retention note](completion_v2/STUDY_RETENTION_NOTE.json): identical contents
are preserved in indexed artifacts, their creation mechanism remains unknown,
and they supply no timing evidence. The audit does not silently resolve that
provenance limitation.

## Frozen claim and stopping rule

The strongest supported statement is:

> We implement conventional odd-order reasoning as source-bound history
> witnesses for a published reseeding LFSR family and evaluate complete witness
> production and external native checking. Under the fixed amended protocol,
> the exporter adds repeatable accepted-witness coverage at width 8 over one
> qualified rIC3 configuration, while larger cases expose native proof-artifact
> costs. Retained completed CNF proofs replay independently; the native
> translations remain trusted.

This closes the finite follow-up from Gates 14–17. No theorem, benchmark result,
or delivery check in this gate clears the stronger contribution requirement.
Do not present a new general verification method, history principle, algebraic
algorithm, end-to-end verified compiler, polynomial native proof bound, or
complete-orbit-engine advantage as an established result.

Preserve this checkpoint as a completed integration study. Reopening scientific
development needs a concrete new question with a plausible distinct result and
a specified consumer, or a material correctness/assurance defect to repair.
A larger synthetic exponent, another output format, a new timing budget or an
open-ended search for a favorable comparison is not such a question by itself.
No further experiment or manuscript task is scheduled by this decision.

The delivery gate is the unchanged integrated `python verify.py`, including
offline evidence verification. Passing it validates the repository checkpoint;
it cannot convert the assessment into a positive originality finding. Historical
gates, protocols, sources, native artifacts and expected outcomes stay fixed.
