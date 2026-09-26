# Current work: a classical certificate contribution, not a quantum speedup claim

Read README.md, docs/SPECIFICATION.md, docs/FORMAT.md, docs/RESEARCH.md, and provenance/ORIGIN.md first. The manuscript is on hold. No journal is selected for this spinoff. The original quantum project must not be modified as part of this work.

## Established executable baseline

The package supplies a bounded prime-field affine-orbit producer, an independent positive certificate checker, and an arithmetic consumer. The checker validates primality and complete period factorization, an inverse witness, least point period, canonical hit offset, and problem binding. It does not import or run the producer. The producer is an enumerator, not a fast orbit/discrete-log algorithm. The mathematics is established; no novelty or practical speedup is claimed.

Run `python verify.py` before and after changes. Do not change stored expected evidence just to make modified code pass. Keep tests for composite-factor spoofing, malformed inputs, fixed points, affine shifts, resource limits, and time-window semantics. Limit exhaustion, rejection, and mathematical unreachability are different statuses.

## Next research task

Perform a targeted prior-work comparison and identify one genuinely useful certificate or consumer improvement. Before implementing a broad extension, state the exact new claim, strongest existing method, and downstream task. A scoped negative-certificate mechanism or composition of independently certified summaries may be worth auditing, but neither is established as original here. Do not inflate a toy's horizon to claim useful speedup, or compare only against the elementary producer.

The current executable semantics are prime fields, invertible affine maps, one initial state and a full-state target. Extension fields, machine-word rings, singular maps/tails, arbitrary guards and negative certificates require explicit new specifications and proofs. Do not silently broaden them.

## Preservation and delivery

The original license is immutable. The predecessor portable ZIP is unavailable, not imported; recover and preserve it verbatim when accessible. Do not re-create it from the new code. The upstream orbit note is pinned by commit and blob in provenance/ORIGIN.md.

No public release tag, manuscript, journal submission, paid computation, or external contact is authorized by the bootstrap. Ordinary repository development and testing are the requested work. Keep scientific claims distinct from packaging progress and expose any uncompleted verification or comparison.
