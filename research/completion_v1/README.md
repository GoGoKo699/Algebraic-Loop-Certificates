# Scientific completion: requirement and cost audit

This checkpoint closes the requirement audit for a bounded conventional LFSR
certificate-export study. It also reconciles eight existing positive native
observations: 72 obligations and 232 subprocess stages. It runs no new solver
experiment and does not add another safety certificate format.

Read [the decision](../SCIENTIFIC_CLOSURE_GATE_14.md),
[the comparison design](STUDY_DESIGN.md), and
[baseline qualification status](BASELINE_QUALIFICATION.md).
The executable protocol and matched results remain pending. Manuscript
preparation remains on hold.

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

Qualify the pinned rIC3 baseline, freeze exact commands and resource enforcement,
and then execute the six-case matched study. Its primary outcome and failure
classification are fixed in the study design. A failed comparison closes that
benefit hypothesis; it does not authorize an expanding search for favorable
cases. The complete orbit compiler's consumer usefulness remains a separate
unresolved question and is not claimed by this narrower integration.
