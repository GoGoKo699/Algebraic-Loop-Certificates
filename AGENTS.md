# Repository guidance

This is a classical research spinoff, not a claim of quantum advantage. Start with `work_orders/CURRENT.md`. The manuscript remains on hold. Keep explanations and proofs in Markdown; do not start manuscript drafting.

Preserve `LICENSE` and `history/` byte-for-byte. `provenance/` distinguishes source facts, historical reports, and newly run evidence. Do not fabricate the unavailable predecessor archive or cite its old tests as fresh runs.

The executable scope is prime-field, invertible affine dynamics, specified initial state, and full-state target. Do not confuse prime fields with extension fields, integers, or machine-word overflow.

Run `python verify.py` and `python -O verify.py` before proposing a merge. The checker must not import producers, factor numbers, enumerate a claimed positive period, or rely on assert statements. New schemas and certificate classes require a soundness argument and adversarial tests. Validate every external result before a consumer uses it. Unknown and resource-limit outcomes are not unreachability.

Keep comparisons fair: exact output, confidence, representation, preprocessing, producer, checker, and consumer costs all count. Existing mathematical components require attribution. A large example horizon is not an advantage benchmark. No novelty or practical speedup is established by this bootstrap.
