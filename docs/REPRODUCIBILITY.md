# Reproduce and inspect

Run `python verify.py` from a checkout. Python 3.10+ and the standard library suffice; no installation or network access is needed. The optional package metadata permits normal installation, but that is not required to inspect or verify the repository.

The root verifier checks every recorded file digest, preserves the original MIT license and historical note hashes, checks Markdown local links, runs `tests/audit.py` in a temporary copy, and compares the deterministic report byte-for-byte with `reports/expected.json`. The production checks use exceptions, not disabled assertions, and the verification also runs under `python -O verify.py`.

The independent exhaustive oracle uses ordinary affine steps and a closed-list membership check, not the arithmetic kernel used by the producer/checker. It covers all invertible two-by-two **linear** maps over F2 and F3; all one-dimensional invertible **affine** maps over F2, F3, and F5; and every nonzero translation of the invertible two-by-two maps over F2. These are 100 recurrences and 4,834 initial/target pairs. This is not an exhaustive test over all fields or dimensions.

The 2,282 positive cases each receive a noncanonical-offset mutation and a nonminimal-period mutation. The 1,846 outside-span and 706 explicit-cycle cases provide distinct negative evidence. Tests also cover 6,084 arithmetic schedule intersections, 298 independent primality cases, field/input corruption, missing factorization, forged claims, CLI duplicate JSON keys, output non-overwrite, resource exhaustion, and producer-import independence.

Examples are inputs and proof objects, not trusted expected assertions. The demo checks certificates before answering queries. Its horizon of `10^30` illustrates use after verification; no comparison with optimized loop acceleration or native algebra software is inferred.

To regenerate a report manually, use a **new** path:

```sh
python tests/audit.py --output /tmp/alc-fresh-report.json
```

Never overwrite fixtures to make a broken run pass. Changes to the schema or evidence require explicit review, a new expected report, and an updated manifest after the results have been explained. The CI workflow runs Python 3.10, 3.12, and 3.13; local runs establish only the interpreter actually used, not the remote matrix result.

The original `Quantum_Discovery_Algebraic_Loop_Scout.zip` was not mounted and was not found in the available file search. No claim of a historical replay is made. The predecessor note was recovered from a pinned public Git blob and matches it byte-for-byte. All production code and reported bootstrap tests were written and run anew.
