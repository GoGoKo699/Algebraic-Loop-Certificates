# Independent implementation and cross-check

**The primary API remains the root `alc/` package and `alc.problem.v1` / `alc.certificate.v1` formats.** This audit does not replace it or widen its supported claims.

A separate bootstrap was developed from the initial repository commit before a concurrent bootstrap reached `main` at `ca51357b4c651d687dfe573975df076ccd5e71d9`. Instead of overwriting that work, the second implementation is retained here as a self-contained reference. All files that existed on that main commit are preserved unchanged by this integration.

## Reproduce

From the repository root:

```sh
python audits/independent_v1/verify.py
```

The normal `python verify.py` also runs this audit through the added regression test. Python 3.10+ and the standard library suffice.

The audit first checks the independent reference's full integrity manifest, runs its exact tests in temporary storage, and checks the authentic historical note. It then loads the primary and reference checkers under **separate module names**, translates the same mathematical claims into their distinct schemas, and compares both against a direct affine trajectory oracle.

The primary checker requires an inverse-matrix witness. The reference independently calculates invertibility instead. They also have independently written modular powering and factor-product checks. They use the same established least-period and Lucas/Pratt mathematics, so implementation independence is not formal mathematical independence.

## Results

The common finite domain contains **4,834 state/target pairs across 100 recurrences**. Both checkers agree on all **2,282 valid positive certificates** and reject the tested false hit claims for all **2,552 unreachable targets**. This rejection agreement is not itself a general unreachability proof; direct complete trajectories establish the truth in the small audit cases. The primary checker additionally rejects 2,282 corrupted inverse witnesses, and both reject 2,282 noncanonical offsets.

The reference's own audit also checks 6,084 schedule intersections, 38,672 consumer queries, 298 primality cases, resource-limit behavior, CLI non-overwrite, and malformed claims. Its exact report and its own source manifest are in `reference/reports/expected.json` and `reference/MANIFEST.json`.

`expected.json` pins the two primary source files compared. An intentional primary implementation change requires rerunning and reviewing this audit, not blindly replacing expected hashes. No production algebra package, performance advantage, formally verified checker, or quantum backend is established here.

## Negative certificates are a research branch, not the main API

The isolated reference also implements a separating-functional certificate for targets outside the cyclic span and an explicit closed-cycle exclusion for small inside-span targets. It checks 1,846 of the former and 706 of the latter. Their proofs are in `reference/docs/SPECIFICATION.md`. These methods are elementary, not claimed novel. Explicit cycle proofs can be large.

The primary API still supports **positive hit-set certificates only**. Its formats, consumers, limits, and declared research scope are unchanged. The audit schemas must not be passed to primary commands. A later proposal to adopt negative certificates needs an explicit production-format change, review, and tests.

## Preservation and scientific scope

The reference subtree has Git tree `96d24c3769b89d7be17a15fa82396bbfb17c898a` and is the exact tested second bootstrap, including its original contextual README and work order. Those documents describe the *isolated reference*, not the root production API. Its published predecessor note has the authentic original blob `18a2bd4b39077a6b4a32e8b299b133796e6bf6fb`.

The original conversation scout ZIP remains unavailable and has not been reconstructed. This new source is not described as that archive or as a historical rerun. The root MIT license remains unchanged. The parent quantum-discovery repository is not modified.

The next substantive research step remains a structure-aware, non-enumerative certificate producer and a fair consumer-level comparison. This integration strengthens reproducibility; it does not establish novelty or a publishable speedup. Manuscript preparation stays on hold.
