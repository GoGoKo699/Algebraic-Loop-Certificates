# Executable protocol: separate raw and metadata budgets

This version implements the [storage amendment](STORAGE_AMENDMENT.md). It
inherits the scientific question, six original source files, route meanings,
three-of-three criterion and negative stopping rule from the unchanged
[study design](../completion_v1/STUDY_DESIGN.md). The first experiment and its
[protocol](../completion_v1/EXECUTABLE_PROTOCOL.md) remain historical evidence;
this file does not reinterpret their outcomes.

## Fixed workflows and order

Use the unchanged `completion_v1.worker` and qualified executables. Every route
reads the original upstream ASCII AIGER model. The exporter validates explicit
width, taps and `M=2^n-1` hints and charges their validation and factorization.
rIC3 retains ordinary preprocessing and the fixed command:

```text
ric3 check model.aag --cert witness.aag --ui false ic3 --rseed 0
```

A witness is accepted only after the unchanged Certifaiger, aigsplit,
aigtocnf, CaDiCaL and lrat-trim commands in the first protocol complete all nine
obligations. Those obligations, in order, are Reset, Transition, Safety,
Liveness, Base, Inductive, Decrease, Closure and Consistent. A solver message or
zero exit alone is insufficient. Native model/witness-to-CNF translations remain
trusted. The structural route produces a separate decision with a different
output contract. The exporter receives extra structural hints; the generic
baseline does not. No route uses the complete orbit engine.

Run 54 fresh-process trials: widths 2, 4, 8, 12, 16 and 24, three routes, three
repetitions. For each repetition, widths ascend. At each width the order is
exporter, rIC3, structural for repetitions 1 and 3; rIC3, exporter, structural
for repetition 2. No case selection or restart option is provided.

## Shared resource contract

| Quantity | Limit and interpretation |
|---|---|
| CPU affinity | One CPU, selected and recorded before measurement |
| Address space | Hard inherited 1 GiB per process, not aggregate resident memory |
| Workflow wall time | 30 seconds total, including imports, reads, construction, native checks and worker bookkeeping |
| Raw artifacts | 64 MiB sampled acceptance budget |
| Known metadata and logs | Separate 64 MiB sampled acceptance budget |
| All trial files | 128 MiB conservative guard, implied by the two component budgets |
| Individual file | Hard inherited 64 MiB size limit |
| Each captured stdout/stderr stream | 1 MiB |

Start the monotonic clock before launching the worker. Do not reset the timer
between stages. Native descendants inherit the affinity and process limits.
The Linux subreaper terminates and reaps descendants, including new sessions;
incomplete cleanup is an infrastructure failure. Cleanup after stopping,
compression, archive indexing and independent offline proof replay are outside
the measured workflow. Record those boundaries rather than inventing completion
times for stopped trials.

Scan the trial tree and visible open deleted files at nominal 10 ms intervals
and at completion. Record raw, metadata and combined observed peaks and final
sizes, deleted-file observations and the largest actual sampling gap. Short
peaks can be missed and overshoot has no guaranteed byte bound. An observed
excess remains a violation after a file shrinks or disappears. This is not an
instantaneous aggregate disk quota. Symlinks and special files are rejected.

The existing bounded descriptor-access retry remains charged to the workflow:
at most 50 ms, with sleeps of at most 1 ms. An inaccessible descriptor directory
is skipped only for a vanished process or the same process identity in terminal
state with at most one remaining thread. Persistent live denials and reused
process identifiers fail closed. The supervisor is for inspected non-hostile
tools that preserve their limits and write inside the isolated trial directory.

## Exact metadata paths

Paths below are relative to one trial directory and case-sensitive. Only these
present regular files receive metadata classification:

- `workflow.stdout` and `workflow.stderr`;
- `data/JOURNAL.json`, `data/CONSTRUCTION.json`, `data/RESULT.json`, and each
  corresponding `.json.tmp` atomic copy;
- `data/STAGES.jsonl`;
- `data/STAGE.stdout.txt` and `data/STAGE.stderr.txt`, where `STAGE` is `ric3`,
  `generate`, `split`, or one of the nine obligation names followed by `_cnf`,
  `_solve` or `_replay`.

Every other file counts as raw, including unknown `.json` or `.log` files and
all paths under `tmp/`. Every visible open deleted file counts as raw regardless
of its previous name. Thus a recognized atomic JSON copy is metadata while
present but raw if observed through a deleted open descriptor. There is no
extension-based exemption for native artifacts. Supervisor reports and archive
indices created after the measured workflow are retained separately and do not
retroactively enter its byte observations.

## Verdict precedence and evidence

Record all observed component violations. The two component checks imply the
128 MiB combined guard; it has no separate eligibility rule. `metadata_limit`,
output overflow, failed cleanup, setup failures and correctness conflicts
suspend execution. Metadata or output failure takes
precedence over simultaneous deadline or raw-artifact exhaustion for scientific
classification. All retained results, journals, finished stage records and
definitive solver verdicts participate in that decision; a later outer limit
cannot conceal an earlier rejection or failed proof check.

With no conflicting evidence, `deadline` and `artifact_limit` are UNKNOWN
outcomes eligible for the original resource-based comparison rule, and the fixed
sequence continues. A per-file signal, arbitrary crash, allocation failure or
producer UNKNOWN alone does not establish a declared resource cause. Successful
completion requires no observed violation and the route's complete output
contract. Do not substitute a structural decision for an accepted witness.

Retain command arrays, bounded raw stream prefixes, exit codes, phase records,
partial outputs and every observed violation. Keep interrupted journals distinct
from completed results. Compress only after stopping, binding both original and
stored hashes and sizes. Each trial uses a new directory; no interrupted or
completed directory may be reused.

## Before measurement and reproduction

Validate the original qualification evidence and qualified executable hashes.
Run the same four tiny synthetic controls under the amended supervisor: positive
exporter and rIC3 witnesses, the exporter selector corruption, and the mapped
rIC3 latch-reset corruption. Retain them as qualification, outside the six-case
comparison. Check the amended resource and classification controls, then create
a new source/input/binary freeze before measuring any of the six cases. Bind
this protocol, the amendment, the new supervisor/driver, and every reused
execution dependency. A source edit invalidates that freeze. Keep
`PYTHONHASHSEED=0`, `LC_ALL=C`, `RUST_LOG=info` and seed 0.

```sh
python -m research.completion_v2.study freeze --tools /absolute/tools --output /new/PROTOCOL_FREEZE.json
python -m research.completion_v2.study execute --tools /absolute/tools --freeze /frozen/PROTOCOL_FREEZE.json --output /new/study-evidence
```

Do not run builds, tests, solver jobs or offline proof replay concurrently with
the measured sequence. Record the host and runtime; fresh processes do not mean
cold caches or controlled shared-host load. Paths to qualified binaries may
change but their bytes must match. Repository sources, inputs, executables and
Python are bound; system libraries, kernel and most inherited environment are
not a hermetic runtime. Hashes bind evidence bytes, not authenticated execution.

The amendment was selected with knowledge of the first incomplete run. Preserve
both experiments separately and evaluate the original primary criterion only
from a completed new sequence. Another suspension remains an incomplete study.
