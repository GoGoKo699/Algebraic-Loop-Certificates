# Current work: a classical certificate contribution, not a quantum speedup claim

Read README.md, docs/SPECIFICATION.md, docs/FORMAT.md, docs/RESEARCH.md, research/BOUNDED_COMPARISON_GATE_16.md, research/completion_v1/README.md, research/completion_v1/EXECUTABLE_PROTOCOL.md, research/completion_v1/PROTOCOL_FREEZE.json, and provenance/ORIGIN.md first. The manuscript is on hold. The original quantum project must not be modified as part of this work.

## Established executable baseline

The package supplies a bounded prime-field affine-orbit producer, an independent positive certificate checker, and an arithmetic consumer. The checker validates primality and complete period factorization, an inverse witness, least point period, canonical hit offset, and problem binding. It does not import or run the producer. The producer is an enumerator, not a fast orbit/discrete-log algorithm. The mathematics is established; no novelty or practical speedup is claimed.

Run `python verify.py` before and after changes. Do not change stored expected evidence just to make modified code pass. Keep tests for composite-factor spoofing, malformed inputs, fixed points, affine shifts, resource limits, and time-window semantics. Limit exhaustion, rejection, and mathematical unreachability are different statuses.

## Current scientific decision

The [bounded comparison gate](../research/BOUNDED_COMPARISON_GATE_16.md) records a suspended study. The exact first 32 trials of the frozen 54-trial sequence ended at the width-16 exporter in repetition 2, after metadata and logs triggered the all-file storage guard while raw artifacts remained below budget. The recorded execution issue is not an invalid-witness finding. The 22 remaining trials were not attempted, and the primary three-of-three criterion is unevaluated. Do not treat partial width-8 observations as a completed win or the suspended study as a completed negative result.

The [requirement audit](../research/SCIENTIFIC_CLOSURE_GATE_14.md) fixes a documented hardware-verification consumer requiring an accepted witness against the original circuit, not just an algebraic safety verdict. The candidate remains the conventional LFSR witness exporter demonstrated at the existing interface. It does not use the complete orbit engine or establish a benefit for that engine.

The [baseline qualification gate](../research/BASELINE_QUALIFICATION_GATE_15.md) qualifies pinned rIC3 through the same native checker as the exporter, including positive and corrupted-witness controls. Commands, sources, binaries, case order and the resource policy are fixed in the [executable protocol](../research/completion_v1/EXECUTABLE_PROTOCOL.md) and [freeze record](../research/completion_v1/PROTOCOL_FREEZE.json). Qualification observations are not benchmark measurements.

rIC3 remains the mandatory certifying baseline. ABC remains a diagnostic reference. The direct squarefree structural checker remains a cost and trust reference with a different output contract; it does not by itself deliver the requested witness. The conventional source-aware route can emit the same history witness, so do not invent a separate orbit-engine advantage over it.

The algebraic contribution boundary in [assessment 08](../research/CONTRIBUTION_ASSESSMENT_08.md), negative supplied-invariant result in [Gate 09](../research/VERIFICATION_GATE_09.md), and closed invariant/history novelty route in [Gate 13](../research/INVARIANT_HISTORY_GATE_13.md) remain binding. Preserve the successful integrations in Gates 10–12 and all unsuccessful controls. The [cost audit](../research/completion_v1/README.md) separates the available native stages; historical partial timings must not become invented full-workflow totals.

## Finite remaining sequence

1. **Review the shared storage policy prospectively.** Preserve the suspended study, its classifications and its exact frozen protocol. Separately assess an amendment that accounts for metadata and logs without changing the original raw-artifact budget, sources or corpus, then decide whether a fresh whole 54-trial sequence is warranted. Do not selectively restart, rerun or reclassify the original trials. Record the rationale before any new measurements.
2. **Complete any justified new comparison before assessing contribution.** A new sequence needs its own prospective freeze and must retain every accepted, rejected, unknown and failed outcome. Charge source recognition, hint validation, factorization, construction, conversions, native obligations, SAT search and LRAT replay. Evaluate the original primary criterion before comparing a surviving scoped result with the closest certifying-exporter literature. CNF proof replay is not end-to-end formal verification; partial observations cannot substitute for the primary result.
3. **Freeze the evidence.** Run the integrated verifier, resolve contradictions, and document the final limitations and stopping decision. A completed negative study is a legitimate endpoint; it does not establish research readiness or permit a post-hoc speedup claim. Manuscript drafting remains on hold.

This sequence supersedes the earlier open-ended next-task recommendations. Another equivalent format, broader arithmetic domain or larger synthetic exponent is not an automatic follow-up to a negative result.

The production `alc/` semantics remain prime fields, invertible affine maps, one initial state and a full-state target. Research-only extensions have their own specifications and proofs. Do not silently broaden production semantics or treat research support as production integration.

## Preservation and delivery

The original license is immutable. The predecessor portable ZIP is unavailable, not imported; recover and preserve it verbatim when accessible. Do not re-create it from the new code. The upstream orbit note is pinned by commit and blob in provenance/ORIGIN.md.

No public release tag, manuscript, journal submission, paid computation, or external contact is authorized by the bootstrap. Ordinary repository development and testing are the requested work. Keep scientific claims distinct from packaging progress and expose any uncompleted verification or comparison.
