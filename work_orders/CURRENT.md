# Current work: maintain and release the completed resource

Start with [README.md](../README.md), [the production specification](../docs/SPECIFICATION.md),
[the interface contract](../docs/FORMAT.md), [the research assessment](../docs/RESEARCH.md)
and [the final bounded assessment](../research/CONTRIBUTION_ASSESSMENT_18.md).
This repository serves as a record of the work and a guide for the author’s self-directed learning. For discussion or potential collaboration, please contact Ruge Lin at [gogoko699@gmail.com](mailto:gogoko699@gmail.com).

See [Purpose and contact](../README.md#purpose-and-contact) in the README.
Present this as a standalone project, centered on its own contracts and results.

## Teaching and repository maintenance

The reader path is anchored in Manna and Pnueli's *Temporal Verification of
Reactive Systems: Safety* (1995). Maintain [the learning path](../docs/LEARNING_PATH.md),
[the worked tutorial](../docs/TUTORIAL.md) and [the reproduction guide](../docs/REPRODUCING.md)
alongside the exact specifications. The book is the single background anchor;
the repository supplies the finite-field and certificate-interface bridge.
Keep [llms.txt](../llms.txt) consistent with these sources.

Keep the production target-hit contract distinct from the research safety-witness
contract, and the mathematical proof distinct from native checking and retained
proof replay. Maintenance and release preparation include checking reproducibility,
repairing defects, removing redundant explanatory text and improving navigation.
They do not reopen the frozen studies or broaden the corpus.

## Executable baseline and release checks

The package supplies a bounded prime-field affine-orbit producer, an independent
positive certificate checker and an arithmetic consumer. The checker validates
primality and complete period factorization, an inverse witness, least point
period, canonical hit offset and problem binding. It does not import or run the
producer. The producer uses bounded enumeration and trial division; it is not a
fast orbit or discrete-logarithm algorithm.

Run `python verify.py` before and after changes. Do not change stored expected
evidence just to make modified code pass. Preserve tests for composite-factor
spoofing, malformed inputs, fixed points, affine shifts, resource limits and
time-window semantics. Limit exhaustion, rejection and mathematical
unreachability are different statuses. For packaging or interface changes,
check installation and the documented commands from outside the source tree.
Expose any uncompleted verification; packaging progress is not a scientific result.

## Scientific scope and stopping decision

[Assessment 18](../research/CONTRIBUTION_ASSESSMENT_18.md) is the canonical
contribution, assurance and stopping record. [Gate 17](../research/BOUNDED_COMPARISON_GATE_17.md)
is the completed 54-trial comparison; [the protocol](../research/completion_v2/EXECUTABLE_PROTOCOL.md)
and [freeze record](../research/completion_v2/PROTOCOL_FREEZE.json) govern its
measurements. Retain the result as a reproducible integration case study.
Neither a distinct standalone contribution nor a benefit for the complete orbit
engine was established. No further experiment is scheduled.

The storage amendment was outcome-informed and increased the combined allowance.
Keep the [suspended Gate 16 study](../research/BOUNDED_COMPARISON_GATE_16.md), its
unevaluated criterion and evidence separate; do not pool or reclassify its trials.
Qualification controls are not benchmark measurements. rIC3 is the matched
certifying baseline, ABC a diagnostic reference, and the structural checker a
cost/trust reference with a different output contract. A conventional source-aware
route can emit the same history witness. Historical partial timings must not
become invented full-workflow totals.

The closed algebraic and invariant/history routes in Gates 08, 09 and 13 remain
closed; preserve the successful integrations and failed controls in Gates 10–12.
Independent CNF replay establishes the supplied formulas' unsatisfiability;
original-model parsing, witness obligations and CNF translation remain trusted.
Hashes bind retained bytes rather than attest execution.

Do not automatically add experiments, change budgets, expand the synthetic corpus
or draft a manuscript. Reopening scientific development requires a concrete new
question with a plausible distinct result and a specified consumer, or a material
correctness/assurance defect. Another format, broader arithmetic domain or larger
exponent alone does not meet that condition. Older recommendations in archived
gates describe their historical context, not a current task queue.

The production `alc/` semantics remain prime fields, invertible affine maps, one
initial state and a full-state target. Research-only extensions have their own
specifications and proofs; do not silently broaden production semantics.

## Preservation

Preserve LICENSE byte-for-byte, both study protocols, all completed, unknown and
failed observations, and retention notes. Do not remove retained proof artifacts
as duplicates of summaries. Keep external source attribution and historical
import status accurate; see [the source record](../provenance/ORIGIN.md).
