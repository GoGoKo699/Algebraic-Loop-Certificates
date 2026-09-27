# Scientific completion: suspended bounded comparison

The [current gate](../BOUNDED_COMPARISON_GATE_16.md) records a suspended study.
The exact first 32 trials of the frozen 54-trial sequence ran; the remaining 22
were not attempted. The primary three-of-three criterion is unevaluated, so this
is neither a completed positive nor a completed negative comparison. Manuscript
preparation remains on hold.

| Recorded outcome | Exporter | rIC3 | Structural | Total |
|---|---:|---:|---:|---:|
| Completed workflow | 6 | 4 | 10 | 20 |
| Deadline unknown | 0 | 7 | 0 | 7 |
| Raw-artifact-limit unknown | 4 | 0 | 0 | 4 |
| Execution issue: all-file storage guard | 1 | 0 | 0 | 1 |
| Attempted | 11 | 11 | 10 | 32 |

The final trial was the width-16 exporter in repetition 2. The shared cap was
67,108,864 bytes. Raw artifacts occupied 67,098,722 bytes, 10,142 below that cap;
all files occupied 67,170,336 bytes, 61,472 above it. The difference was 71,614
bytes of metadata and logs. The all-file guard therefore suspended the run as an
execution issue, as the frozen policy requires. This is not an invalid-witness
finding: the Inductive solve was interrupted after the first five obligations
had completed proofs.

No third repetition ran. At width 8, the exporter completed twice and rIC3
reached the 30-second deadline twice. These partial observations cannot establish
the required three-repetition win. No comparative claim is recovered by dropping
the failed trial, calling it raw-budget exhaustion or resuming selected trials.

The [study report](STUDY_REPORT.json), [run context](STUDY_RUN_CONTEXT.json),
[retention note](STUDY_RETENTION_NOTE.json) and
[lossless archive](study_20260927.tar.xz.parts/manifest.json) retain the executed prefix. Independent
replay validates all 115 completed CNF proofs, including those before interrupted
solves. Native source-to-CNF translations remain trusted, and the structural
reference does not supply the requested hardware witness. Check the retained
study without invoking native tools:

```sh
python -m research.completion_v1.verify_study
```

The [comparison design](STUDY_DESIGN.md), [executable protocol](EXECUTABLE_PROTOCOL.md)
and [freeze](PROTOCOL_FREEZE.json) are preserved unchanged. The next step is a
separate prospective review of the shared storage policy and a decision on
whether a fresh whole 54-trial sequence is warranted, with the original raw
budget, sources and corpus fixed. Original outcomes must not be reclassified.

The earlier [qualification gate](../BASELINE_QUALIFICATION_GATE_15.md) remains
valid: the conventional LFSR exporter and pinned rIC3 pass the same external
checker on a synthetic smoke control; both corruptions are rejected; 23 completed
qualification proofs and both negative SAT assignments are independently checked.
That compatibility evidence is separate from the comparative study. The earlier
[requirement audit](../SCIENTIFIC_CLOSURE_GATE_14.md) and retrospective accounting
below remain unchanged scientific evidence.

## What the existing costs actually measure

All times below are seconds from the original single observations. The two
width-8 rows concern the same original model with different witness producers;
rotation3 and mixed5 are synthetic premise controls. These are not eight
independent benchmark instances or a new comparative experiment.

| Observation | Witness bytes | Raw LRAT bytes | Native total | SAT search and emission | Native LRAT replay |
|---|---:|---:|---:|---:|---:|
| Gate 11 ABC, width 2 | 833 | 9,695 | 0.1020 | 0.0270 | 0.0159 |
| Gate 11 ABC, width 4 | 12,393 | 367,471 | 0.1219 | 0.0541 | 0.0184 |
| Gate 11 history, width 2 | 1,146 | 13,787 | 0.0780 | 0.0217 | 0.0137 |
| Gate 11 history, width 4 | 2,802 | 230,169 | 0.1028 | 0.0359 | 0.0193 |
| Gate 11 history, width 8 | 11,211 | 25,813,066 | 3.4174 | 3.0559 | 0.2320 |
| Gate 12 rotation3 | 1,920 | 27,776 | 0.0793 | 0.0232 | 0.0135 |
| Gate 12 mixed5 | 4,937 | 587,449 | 0.1117 | 0.0468 | 0.0186 |
| Gate 12 published8 | 11,872 | 24,898,388 | 3.3326 | 3.0727 | 0.1814 |

For Gate 12 published8, most recorded native time is SAT search and proof
emission. Its Inductive obligation alone accounts for 3.0487 seconds of search
and 24,856,409 proof bytes. This identifies the observed cost center; it does
not establish a scaling law or prove that another encoding is needed.

Native totals exclude witness construction and initial input copying/hashing.
They include obligation generation, splitting, CNF conversion, SAT search,
native LRAT replay, and intervening orchestration. The residual after summing
recorded stages is labeled unallocated overhead, not silently charged to the
SAT solver. Gate 11's later reconstruction timings and incomplete ABC adapter
timings cannot repair its missing original end-to-end measurement. Gate 12 has
separate pre-run construction observations, but no single complete workflow
timer. Accordingly every full original workflow total in the report is null.

## Reproduce the audit

From the repository root:

```sh
python -m research.completion_v1.audit_costs --check
```

The script uses only the standard library. It verifies the recorded stage and
obligation sequences, exits, input bindings, shared binary provenance, artifact
metadata and construction scope, then reconciles the arithmetic with
[COST_AUDIT.json](COST_AUDIT.json). Decimal strings preserve the recorded JSON
tokens without adding measurement precision. A new report can be written with
`--output PATH`; existing files are never overwritten by that option.

This accounting check does not execute tools, replay LRAT, validate native
translations, or establish safety. Those responsibilities remain with the
preserved Gate 11/12 verifiers, included in `python verify.py`. Hashes bind the
analytical inputs; they are not an additional soundness theorem.

## Remaining work

Resolve the prospective storage-policy question before deciding on a fresh
whole study. The suspended sequence supplies no completed primary result, and
its evidence remains fixed. A completed negative comparison would close the
benefit hypothesis; it would not authorize an expanding search for favorable
cases. The complete orbit compiler's consumer usefulness remains a separate
unresolved question and is not claimed by this narrower integration.
