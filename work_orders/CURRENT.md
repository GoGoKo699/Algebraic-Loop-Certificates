# Current work: a classical certificate contribution, not a quantum speedup claim

Read README.md, docs/SPECIFICATION.md, docs/FORMAT.md, docs/RESEARCH.md, research/CONTRIBUTION_ASSESSMENT_08.md, research/VERIFICATION_GATE_09.md, research/NATIVE_WORKLOAD_GATE_10.md, research/PROOF_INTERFACE_GATE_11.md, and provenance/ORIGIN.md first. The manuscript is on hold. The original quantum project must not be modified as part of this work.

## Established executable baseline

The package supplies a bounded prime-field affine-orbit producer, an independent positive certificate checker, and an arithmetic consumer. The checker validates primality and complete period factorization, an inverse witness, least point period, canonical hit offset, and problem binding. It does not import or run the producer. The producer is an enumerator, not a fast orbit/discrete-log algorithm. The mathematics is established; no novelty or practical speedup is claimed.

Run `python verify.py` before and after changes. Do not change stored expected evidence just to make modified code pass. Keep tests for composite-factor spoofing, malformed inputs, fixed points, affine shifts, resource limits, and time-window semantics. Limit exhaustion, rejection, and mathematical unreachability are different statuses.

## Current scientific decision

The research namespaces now supply complete certificates and source recognizers beyond the production API. The constructive character/Taylor comparison reaches the same all-target membership and least-period contract at comparable coarse polynomial bounds. The direct matrix-logarithm paper has been read; its former access problem is resolved. Treat the engine as a certifying implementation of established structure, not an already cleared novel theorem.

The supplied-invariant feasibility gate is complete: native cvc5 discharged all ten valid invariants directly. This corpus does not establish a need for our orbit engine. Preserve the broken controls and unknown outcomes; neither an unmeasured checker nor extra synthetic examples establish an advantage. See the two current assessments above for exact scope and provenance.

## Next research task

The [existing-workload pass](../research/NATIVE_WORKLOAD_GATE_10.md) supplies checked odd-order safety proofs for 23 published AIGER circuits with arbitrary reseeding. SmokeRand already resolves the separate maximal-period workload. The [proof-interface gate](../research/PROOF_INTERFACE_GATE_11.md) now passes three history witnesses and two ABC-exported invariants through Certifaiger with retained, independently replayed SAT proofs. The phase-parity reduction is a precise interface constraint, not an invariant-size or cryptographic lower bound.

Prioritize the remaining premise and comparison gap: the history predicate needs a common exact maximal period, while the safety theorem only needs odd order. Determine whether an existing checked algebraic interface can preserve the weaker premise at useful cost, or justify a consequential benefit for the measured stronger contract. Compare the strongest structural/squarefree/primitive-polynomial method at exactly the same proof interface; it can emit the same current witness. Inspect direct predecessors before enlarging the corpus. Do not treat familiar odd-order algebra or witness circuits as novel, and do not infer end-to-end formal assurance from CNF proof replay alone.

Start from an independently specified verification workload or documented requirement. Retain its natural input/output contract, identify the strongest source-aware baseline, and state a falsifiable cost or assurance improvement. Execute that baseline before building more source machinery. Proof-producing finite-field verification already has direct predecessors, so independent checkability alone is not a sufficient gap. A useful integration or a strictly justified checker cost/assurance result must survive equally compact representations and matched assumptions.

Another equivalent orbit format, a broader arithmetic domain, or a larger synthetic exponent is not the next objective. Count extraction, construction, witness size, checking, and useful consumption; do not inflate a horizon or compare only against the elementary producer. Preserve unsuccessful gates as scientific evidence.

The production `alc/` semantics remain prime fields, invertible affine maps, one initial state and a full-state target. Research-only extensions have their own specifications and proofs. Do not silently broaden production semantics or treat research support as production integration.

## Preservation and delivery

The original license is immutable. The predecessor portable ZIP is unavailable, not imported; recover and preserve it verbatim when accessible. Do not re-create it from the new code. The upstream orbit note is pinned by commit and blob in provenance/ORIGIN.md.

No public release tag, manuscript, journal submission, paid computation, or external contact is authorized by the bootstrap. Ordinary repository development and testing are the requested work. Keep scientific claims distinct from packaging progress and expose any uncompleted verification or comparison.
