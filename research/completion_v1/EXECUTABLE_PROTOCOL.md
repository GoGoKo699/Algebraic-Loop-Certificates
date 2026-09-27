# Executable protocol for the bounded comparison

This protocol implements the [study design](STUDY_DESIGN.md). Qualification
uses a synthetic three-bit rotation wrapper, outside the six published study
cases. Qualification observations are not benchmark measurements. A valid
`PROTOCOL_FREEZE.json` and matching qualified binaries are required before the
study driver can execute. The freeze records exact source, input and executable
hashes; editing any frozen execution dependency invalidates it.

## Original input and routes

Every route reads the unchanged upstream ASCII AIGER file. The rIC3 frontend
accepts this format directly. There is no input conversion or conversion adapter.
Both witness routes pass the separately copied original `model.aag` to
Certifaiger. rIC3's normal preprocessing stays enabled; the exporter validates
the source wrapper and its explicit width/tap/exponent hints.

The fixed rIC3 command is:

```text
ric3 check model.aag --cert witness.aag --ui false ic3 --rseed 0
```

There is no additional solver time limit and no invocation of its own Docker
certificate checker. A normal zero exit alone is not a safety verdict: require
exactly one result line `UNSAT`, a witness, and all external obligations. The
configuration has one IC3 worker and a control-handler thread. One-CPU affinity
applies to all threads and descendants; it is not a claim of one OS thread.
The default parallel portfolio and word-level engines are outside this study.
Set `RUST_LOG=info`, the producer's normal non-UI logging level, explicitly;
also freeze `PYTHONHASHSEED=0` and `LC_ALL=C` for the common environment.

The exporter calls the existing `odd_order_witness_v1.produce` with the explicit
width, taps and `M=2^n-1` from the frozen case record. Import, source recognition,
hint validation, complete trial factorization, construction and file writing
are inside the workflow clock. It uses no complete orbit engine. The direct
reference calls `parse`, `replay` and `source_aware.odd_order`; it produces a
structural decision with a different trust/output contract.

For each witness, run the unchanged native commands:

```text
certifaiger model.aag witness.aag check.aig
aigsplit -n check.aig obligation_
aigtocnf NAME.aig NAME.cnf
cadical --quiet --unsat --lrat --no-binary --no-factor NAME.cnf NAME.lrat
lrat-trim NAME.cnf NAME.lrat
```

The last three commands run in this exact order for Reset, Transition, Safety,
Liveness, Base, Inductive, Decrease, Closure and Consistent. Required exits are
zero for generation/conversion and 20 for solving and LRAT replay. SAT exit 10
rejects a witness. Native model/witness-to-CNF transformations remain trusted.
Later independent Python CNF-proof replay is separately reported and untimed.

## Order and limits

`study.py` specifies 54 fresh-process trials: three trials of each of three
routes on widths 2, 4, 8, 12, 16 and 24. For each trial number, widths ascend.
For trial numbers 1 and 3 the order at each width is exporter, rIC3, structural;
for trial 2 it is rIC3, exporter, structural. No case selection flag is provided.
Fresh processes do not imply cold caches. Do not run builds, tests or unrelated
measurements concurrently with this sequence.

The supervisor starts the monotonic clock before launching the fresh workflow
worker. The 30-second deadline includes imports, original-source reads, every
phase and intervening orchestration. Successful completion includes final
worker bookkeeping. Cleanup after a stopped trial is measured separately.
Builds, the pre-run provenance check and post-run compression are excluded.
Retain phase wall/CPU observations inside the supervisor total; do not replace
a failed trial with an invented completion time.

One CPU is chosen and recorded at freeze time. A hard 1 GiB address-space limit
is inherited by the supervisor, worker and native descendants. This is a
per-process limit, not an aggregate resident-memory allowance. The Linux
subreaper supervises descendants, including children that start a new session,
and records cleanup success. An incomplete cleanup is an infrastructure failure.
The harness is for the inspected research tools, not hostile programs that
deliberately change their limits or write outside the isolated trial directory.

## Prospective storage refinement

Before any study measurement, the design's 64 MiB raw-artifact limit is made
operational as an **acceptance budget**, not an instantaneous filesystem quota.
Each file has a hard inherited size limit. The aggregate monitor scans the trial
tree and visible open deleted temporary files every nominal 10 ms and once at
completion. All tools inherit an isolated temporary directory. An observed
excess permanently disqualifies a trial; later shrinking or deleting a file
does not restore acceptance. Record the observed peak, final size, and largest
actual sampling gap. Short peaks between samples can be missed, and the number
of transient excess bytes has no guaranteed bound.

As a conservative execution guard, the same 64 MiB cap also covers the trial's
metadata and bounded logs. Raw circuit/CNF/proof/temporary bytes and all trial
bytes are recorded separately. A storage-limit coverage result is eligible only
when the evidence shows the raw budget exceeded; metadata-only excess is an
execution issue. Each stdout/stderr stream is capped at 1 MiB. A log limit or
unattributed failure is not an added-coverage win. This refinement is shared by
both routes and is fixed before observing their benchmark outcomes.

The supervisor uses a common deadline across every stage; it does not reset a
30-second timer for each subprocess. Arbitrary crashes or signals are not
automatically attributed to memory exhaustion. A Python `MemoryError` under the
inherited limit is recorded explicitly; native allocation failures require
evidence and investigation before any resource-based comparison claim.

## Retention, suspension and outcome

Record command arrays before launch, bounded raw logs, partial artifacts,
return codes, elapsed/CPU observations and the worker's active phase. A timeout
may leave only `JOURNAL.json` instead of a completed `RESULT.json`. Preserve that
distinction. Compress files only after the workflow stops, with both raw and
stored hashes and sizes. Never reuse a completed or interrupted trial directory.

The driver suspends on setup/interface failures, unsupported construction,
unattributed UNKNOWN, invalid witnesses, inconsistent verdicts, failed proof
checks or incomplete cleanup. Preserve all earlier observations and investigate;
there is no automatic selective rerun. Known correctness/setup failure evidence
in a result or interrupted journal takes precedence over a later outer deadline.
A deadline or observed raw-artifact excess remains UNKNOWN and the predetermined
sequence continues only when no conflicting failure evidence is retained. Other
resource signals suspend execution until their cause is established; a per-file
signal alone does not substitute for observed aggregate raw-budget excess.
The study design's three-of-three
added-coverage rule and negative stopping rule remain unchanged. Qualification
or execution failure leaves an incomplete comparison, not a favorable outcome.

```sh
python -m research.completion_v1.study freeze --tools /absolute/tools --output /new/PROTOCOL_FREEZE.json
python -m research.completion_v1.study execute --tools /absolute/tools --freeze /frozen/PROTOCOL_FREEZE.json --output /new/study-evidence
```

`--tools` contains the six qualified executables. Their paths may be relocated;
their bytes must match. The Python executable and version are also bound. This
binds repository sources, inputs and executables, not an entire hermetic runtime:
Python standard libraries, system shared libraries, kernel and most inherited
environment settings remain part of the recorded execution environment. This
file is a prospective protocol, not a report that the six-case study has run.
