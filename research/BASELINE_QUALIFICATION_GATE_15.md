# Gate 15: qualified baseline and executable comparison protocol

27 September 2026. Manuscript preparation remains on hold.

## Completed scientific preparation

The mandatory rIC3 baseline is now executable and compatible with the same
source-bound Certifaiger/CNF/LRAT pipeline as the conventional exporter. The
[qualification record](completion_v1/BASELINE_QUALIFICATION.md) binds the exact
official source, dependencies, compiler configuration, binary and native smoke
artifacts. No solver or certificate checker was patched.

Two positive controls satisfy all nine native obligations. Two deliberate
witness corruptions are rejected: the exporter's wrong period selector at
Inductive, and the rIC3 witness's changed mapped-latch reset at Reset. Independent
offline verification replays all 23 completed LRAT proofs and checks both SAT
assignments against their complete CNFs. These are compatibility/assurance
controls on one synthetic three-bit circuit, not comparative benchmark results.

Both witness routes use the original ASCII AIGER input directly. Removing the
unnecessary conversion step keeps the external checker bound to the same source
bytes and avoids an additional adapter. rIC3 retains its ordinary preprocessing,
with one IC3 worker and fixed seed zero under one CPU. The default parallel
portfolio and word-level engines are outside the comparison.

## Executable protocol and its boundary

The [protocol](completion_v1/EXECUTABLE_PROTOCOL.md) implements the existing
six-case [study design](completion_v1/STUDY_DESIGN.md). A common supervisor
starts the total deadline before the fresh worker reads the source. It applies
one-CPU affinity, inherited 1 GiB per-process address-space limits, bounded logs,
and descendant cleanup across the entire workflow. Real-process controls check
cumulative deadlines, allocation denial, child/session escape, open deleted
temporary artifacts, output limits and invalid artifact types.

The disk policy is clarified prospectively: 64 MiB is a monitored acceptance
budget, not a hard instantaneous aggregate filesystem quota. Per-file hard
limits and sampled aggregate observations are retained, with observed peaks and
sampling gaps. A short-lived peak between samples can be missed. Metadata/log
exhaustion cannot count as a raw-artifact coverage win. This refinement applies
to both routes before any benchmark outcome is observed.

The [freeze](completion_v1/PROTOCOL_FREEZE.json) binds commands through the
worker/driver source, protocol, six unchanged inputs, tool/Python hashes,
resource settings and deterministic 54-trial order. The driver refuses changed
inputs, policies or unqualified binaries and suspends on correctness/interface
issues. It does not selectively rerun trials or replace failed outcomes with
successful timing samples.

## What remains open

The matched six-case study has not run. Qualification establishes a working
baseline; it establishes neither added coverage nor a new research contribution.
The existing three-of-three benefit criterion and negative stopping rule remain
binding. Historical unmatched costs remain historical observations.

Next execute the frozen comparison sequentially, retain every outcome, and
independently replay completed proofs. Then assess the surviving contribution
and assurance boundary against the closest prior work, or close the benefit
route if the predetermined criterion fails. Native translations remain trusted;
these checks are not end-to-end formal verification. The complete orbit engine
is not used by the exporter and gains no benefit claim from this qualification.
