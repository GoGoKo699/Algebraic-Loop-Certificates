# Gate 14: a bounded scientific completion study

27 September 2026. Manuscript preparation remains on hold.

## Completed decision

The remaining work is a bounded study of **exporting conventional source-aware
LFSR reasoning into an existing hardware safety certificate interface**. Its
question is the cost and coverage of obtaining an accepted artifact from the
original circuit. This is an empirical integration candidate, not a reopened
claim of new algebra, inverse-bit hardness, or an advantage for the complete
orbit engine.

The requirement audit is complete. The comparative experiment is not. The
[study design](completion_v1/STUDY_DESIGN.md) fixes the intended inputs,
acceptance condition, comparisons, outcome criterion and stopping rule. Tool
qualification and an exact executable protocol must be recorded before its
timed runs. No new native solver experiment was run for this gate.

## Why this is a real interface requirement

The published HWMCC certification study documents mandatory witness circuits
for safe results in HWMCC'24 and measures solving plus validation. A custom
algebraic verdict alone does not provide that artifact. Certifaiger supplies
the already used model/witness checking interface. This establishes a documented
consumer requirement, not use of our software by the competition or membership
of our small corpus in its competition dataset.

The same study compares against the certifying solver rIC3 and reports it
outperforming ABC on its competition benchmarks. Consequently, the earlier
ABC-only observations cannot establish a competitive benefit for this project.
A pinned, qualified rIC3 configuration is a mandatory comparator for the next
study. The existing ABC records remain useful diagnostic evidence.

Primary source: Froleyks, Yu, Preiner, Biere and Heljanko,
[*Introducing Certificates to the Hardware Model Checking Competition*](https://cca.informatik.uni-freiburg.de/papers/FroleyksYuPreinerBiereHeljanko-CAV25.pdf),
CAV 2025, Sections 1, 3, 4.1 and 4.3,
[DOI](https://doi.org/10.1007/978-3-031-98668-0_14).
The [official competition rules](https://hwmcc.github.io/2024/) and the pinned
[tool dossier](proof_interface_v1/SOURCES.md) specify the concrete artifact.

## What the strongest source-aware comparison already settles

The direct squarefree-polynomial route recognizes the supported source wrapper
and proves its safety without finding a discrete logarithm or using the complete
orbit compiler. Under the witness construction's supplied odd-exponent
conditions, conventional reasoning can emit the very same history witness.
There is no separate superior orbit-engine route to time against it. The
candidate under study is that conventional certifying exporter itself.

Direct structural checking and external witness checking have different trusted
code. The former trusts source recognition and its algebraic safety argument.
The latter can leave the producer untrusted but still trusts the native
model/witness-to-CNF transformations and the proof checker. Neither path is
end-to-end formally verified. A larger pipeline is not automatically a stronger
assurance theorem. The direct decision remains a necessary cost and trust
reference, even though it does not by itself supply the requested witness.

## Existing evidence and the missing comparison

| Evidence | What is established | What remains missing |
|---|---|---|
| Complete prime-field certificates and character/Taylor audit | Exact per-target decisions and reusable recognition, with ordinary proofs and independent controls | No matched consumer-level advantage; this engine is not used by the LFSR exporter |
| Gate 10, all 23 original circuits | Source-bound odd-order safety checking for the restricted reseeding wrapper | General frontend and industrial relevance are not established |
| Gate 11, widths 2, 4 and 8 | Accepted history witnesses; widths 2 and 4 also have accepted ABC exports | Initial adapter/construction timing is incomplete; no rIC3 comparison |
| Gate 12, three positive cases | Weaker-premise export and nine checked obligations per case | Two cases are synthetic premise controls; no matched full-workflow study |
| Gate 13 | Exact theorem and direct predecessor comparison | Standalone conceptual novelty route is closed |

[The cost audit](completion_v1/README.md) decomposes all eight retained positive
native observations from Gates 11 and 12. It preserves their single-run status
and separates SAT search from LRAT replay. Those native totals start after
candidate construction; they cannot be relabeled as end-to-end times. No
historical record is changed or supplemented with invented measurements.

## Finite remaining sequence

1. **Qualify and freeze the comparison.** Pin the existing certifying comparator,
   establish a working output/acceptance path, and freeze the harness and all
   hashes before timed runs. A build or interface failure is a blocked comparison,
   not an exporter win. Do not expand the corpus to avoid a failed outcome.
2. **Execute the bounded study.** Charge extraction, supplied-hint validation,
   factorization, construction, conversions, SAT search and replay. Preserve all
   accepted, rejected, unknown and failed outcomes under the common limits.
3. **Close the contribution and assurance assessment.** Compare any surviving
   scoped result with the closest certifying-exporter literature; map every
   proposed claim to proof, measurement and trust assumptions. Stop unsupported
   claims even if the implementation is correct.
4. **Freeze the scientific evidence.** Run the integrated verifier, resolve
   contradictions and document limitations. This closes a study, not a promise
   of a publishable positive result. Manuscript drafting remains a later step.

The complete orbit and modular modules remain preserved supporting research.
This study must not be used to assert that their usefulness question has been
answered. If the common-interface comparison supplies no consequential benefit,
record that conclusion and finish the implementation/integration evidence
without claiming research readiness. Another domain, certificate format or
larger synthetic exponent is not an automatic follow-up.
