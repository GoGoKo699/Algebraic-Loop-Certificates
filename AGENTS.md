# Working in this repository

This is a standalone classical certificate project. Present its own questions, contracts and results without a spinoff narrative. No new quantum or classical speedup is established. Start with `work_orders/CURRENT.md`.

This repository serves as a record of the work and a guide for the author’s self-directed learning. For discussion or potential collaboration, please contact Ruge Lin at [gogoko699@gmail.com](mailto:gogoko699@gmail.com).

Maintain this wording in current reader-facing notices. See `README.md#purpose-and-contact` for the public purpose and contact, and `llms.txt` for a question-to-source reading map.

Preserve LICENSE and historical evidence. Keep the independently trusted problem separate from the untrusted proof. Do not use floating-point arithmetic or probabilistic primality labels for an exact accepted certificate. The checker must not import the producer or use factorization, orbit enumeration, external services, or assertion-only proof checks.

Run `python verify.py`. New functionality needs a written contract, an argument for soundness, independent small-instance checks, and deliberately malformed/counterfeit cases. A producer timeout is inconclusive; rejecting a certificate does not prove unreachability. Refuse unsupported domains rather than pretending they are prime fields.

Preserve source pins and import-status records in `provenance/ORIGIN.md`; never represent unavailable historical bytes as imported or replayed. Keep source-aware classical competitors, total construction/checking/use costs, and novelty boundaries explicit.
