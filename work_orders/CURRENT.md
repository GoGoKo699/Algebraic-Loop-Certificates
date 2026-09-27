# Current work: a classical certificate contribution, not a quantum speedup claim

Read README.md, docs/SPECIFICATION.md, docs/FORMAT.md, docs/RESEARCH.md, research/BOUNDED_COMPARISON_GATE_17.md, research/completion_v2/README.md, research/completion_v2/EXECUTABLE_PROTOCOL.md, research/completion_v2/PROTOCOL_FREEZE.json, and provenance/ORIGIN.md first. The manuscript is on hold. The original quantum project must not be modified as part of this work.

## Established executable baseline

The package supplies a bounded prime-field affine-orbit producer, an independent positive certificate checker, and an arithmetic consumer. The checker validates primality and complete period factorization, an inverse witness, least point period, canonical hit offset, and problem binding. It does not import or run the producer. The producer is an enumerator, not a fast orbit/discrete-log algorithm. The mathematics is established; no novelty or practical speedup is claimed.

Run `python verify.py` before and after changes. Do not change stored expected evidence just to make modified code pass. Keep tests for composite-factor spoofing, malformed inputs, fixed points, affine shifts, resource limits, and time-window semantics. Limit exhaustion, rejection, and mathematical unreachability are different statuses.

## Current scientific decision

The [amended comparison gate](../research/BOUNDED_COMPARISON_GATE_17.md) completes all 54 trials and meets the original added-coverage criterion at width 8: three accepted exporter witnesses versus three rIC3 deadlines. All 180 completed CNF proofs replay independently. Widths 2 and 4 pass through both witness routes; widths 12, 16 and 24 exhaust both routes' frozen resource budgets. The structural reference passes all cases but has a different output contract.

The amendment is an outcome-informed repair with separate 64 MiB raw and metadata budgets, an exact metadata path allowlist, and unchanged source corpus, native tools, commands, time/memory limits and trial order. Its own qualification and freeze preceded the fresh sequence. Preserve the [original suspended study](../research/BOUNDED_COMPARISON_GATE_16.md), its unevaluated criterion and all historical evidence separately; do not pool or reclassify its trials.

The [requirement audit](../research/SCIENTIFIC_CLOSURE_GATE_14.md) fixes a documented hardware-verification consumer requiring an accepted witness against the original circuit, not just an algebraic safety verdict. The candidate remains the conventional LFSR witness exporter demonstrated at the existing interface. It does not use the complete orbit engine or establish a benefit for that engine.

The [baseline qualification gate](../research/BASELINE_QUALIFICATION_GATE_15.md) qualifies pinned rIC3 through the same native checker as the exporter, including positive and corrupted-witness controls. Commands, sources, binaries, case order and the resource policy are fixed in the [executable protocol](../research/completion_v1/EXECUTABLE_PROTOCOL.md) and [freeze record](../research/completion_v1/PROTOCOL_FREEZE.json). Qualification observations are not benchmark measurements.

rIC3 remains the mandatory certifying baseline. ABC remains a diagnostic reference. The direct squarefree structural checker remains a cost and trust reference with a different output contract; it does not by itself deliver the requested witness. The conventional source-aware route can emit the same history witness, so do not invent a separate orbit-engine advantage over it.

The algebraic contribution boundary in [assessment 08](../research/CONTRIBUTION_ASSESSMENT_08.md), negative supplied-invariant result in [Gate 09](../research/VERIFICATION_GATE_09.md), and closed invariant/history novelty route in [Gate 13](../research/INVARIANT_HISTORY_GATE_13.md) remain binding. Preserve the successful integrations in Gates 10–12 and all unsuccessful controls. The [cost audit](../research/completion_v1/README.md) separates the available native stages; historical partial timings must not become invented full-workflow totals.

## Finite remaining sequence

1. **Assess the surviving scoped contribution.** Compare the completed width-8 certified-witness coverage result with the closest certifying-exporter literature, keeping source recognition, supplied exponent/tap hints, conventional algebra and the required accepted witness explicit. A fixed-corpus coverage result is not a general solver or orbit-engine advantage. Do not reopen the closed algebraic or inverse-bit novelty routes.
2. **Finish the assurance and evidence assessment.** Distinguish independent CNF proof replay from trusted native witness/obligation/CNF transformations and measured resource enforcement. Preserve every completed, unknown and failed observation from both protocols, including the retention notes. Resolve contradictions before making a final scientific claim.
3. **Freeze the scientific conclusion and stopping decision.** Run integrated verification and document the final scope and limitations. Another format, broader arithmetic domain, larger synthetic exponent or selective rerun is not an automatic follow-up. Manuscript drafting remains on hold.

The production `alc/` semantics remain prime fields, invertible affine maps, one initial state and a full-state target. Research-only extensions have their own specifications and proofs. Do not silently broaden production semantics or treat research support as production integration.

## Preservation and delivery

The original license is immutable. The predecessor portable ZIP is unavailable, not imported; recover and preserve it verbatim when accessible. Do not re-create it from the new code. The upstream orbit note is pinned by commit and blob in provenance/ORIGIN.md.

No public release tag, manuscript, journal submission, paid computation, or external contact is authorized by the bootstrap. Ordinary repository development and testing are the requested work. Keep scientific claims distinct from packaging progress and expose any uncompleted verification or comparison.
