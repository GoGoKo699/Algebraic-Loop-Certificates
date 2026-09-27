# Gate 16: bounded comparison suspended by the storage guard

27 September 2026. Manuscript preparation remains on hold.

## Decision

The frozen comparison stopped after an exact **32-trial prefix of 54 planned
trials**. The second 16-bit exporter trial reached the conservative all-file
storage guard while its raw artifacts remained below the declared raw budget.
The driver suspended as specified. No trial was selectively repeated, and the
remaining 22 trials were not attempted.

The primary three-of-three added-coverage criterion is **unevaluated**. This is
an incomplete comparison, neither a successful benefit result nor a completed
negative study. Two accepted 8-bit exporter trials and two rIC3 deadlines are
preliminary observations; they cannot replace the missing third repetition.

## Retained observations

The unchanged [design](completion_v1/STUDY_DESIGN.md),
[executable protocol](completion_v1/EXECUTABLE_PROTOCOL.md), and
[freeze](completion_v1/PROTOCOL_FREEZE.json) governed the run. The baseline was
commit `d965a41c8c67d8247f6205da3c3d9c0f95e751c7`, tree
`a6ab6a64b29b4124295de37fd35074ce6415bb72`. Source and executable hashes matched,
and the pre-run verification passed 61 tests and the exact 4,772-case audit.

Every cell below describes only attempted trials. No third repetition ran.
The structural route supplies a separate decision, not the requested witness.

| Width | Exporter | rIC3 | Structural reference |
|---:|---|---|---|
| 2 | 2 accepted | 2 accepted | 2 decisions accepted |
| 4 | 2 accepted | 2 accepted | 2 decisions accepted |
| 8 | 2 accepted | 2 deadline UNKNOWN | 2 decisions accepted |
| 12 | 2 raw-artifact UNKNOWN | 2 deadline UNKNOWN | 2 decisions accepted |
| 16 | 1 raw-artifact UNKNOWN; 1 execution suspension | 2 deadline UNKNOWN | 1 decision accepted |
| 24 | 1 raw-artifact UNKNOWN | 1 deadline UNKNOWN | 1 decision accepted |

Thus 20 workflows completed: six exporter witnesses, four rIC3 witnesses and
ten structural decisions. Seven rIC3 workflows reached the total deadline;
four exporter workflows exceeded the observed raw-artifact budget. The remaining
attempted exporter workflow triggered the different all-file guard.

These observations do not establish case coverage under the required three
repetitions, a speedup, solver hardness, or superiority over other configurations.
The corpus is the six previously selected hand-designed LFSR wrappers. The
exporter receives explicit structural hints and validates them; rIC3 is a
generic single-worker configuration with its ordinary preprocessing. The
complete orbit engine is not used by the exporter.

## Why execution suspended

Trial `n16-t2-exporter` was stopped during `Inductive_solve` after 8.888614 seconds
of observed workflow wall time. Its first five obligations had completed native
proof replay. The Inductive solver had no recorded finish or SAT/UNSAT verdict,
and there was no completed worker result. Descendant cleanup completed.

| Storage quantity | Bytes |
|---|---:|
| Common cap | 67,108,864 |
| Raw circuit/CNF/proof artifacts | 67,098,722 |
| All trial files | 67,170,336 |
| Metadata and log difference | 71,614 |
| Raw bytes below the cap | 10,142 |
| All-file excess | 61,472 |

The recorded reason is `trial_storage_limit`, not `artifact_limit`. The frozen
protocol excludes metadata/log-only exhaustion from eligible resource-based
coverage evidence and suspends on it. There is no observed invalid witness or
mathematical rejection in this event. Reclassifying it after seeing the outcome
would change the decision rule.

## Accounting and assurance

[STUDY_REPORT.json](completion_v1/STUDY_REPORT.json) preserves every attempted
trial's status, wall time and byte counts, together with medians and full ranges
for completed trials only. Deadline observations are censored, not invented
completion times; no stopped trial is included in those timing summaries.

The [pre-run context](completion_v1/STUDY_RUN_CONTEXT.json) identifies the AMD
EPYC container, Python and operating system. The run used one CPU, an inherited
1 GiB **per-process** address-space limit, a 30-second total workflow deadline,
and the frozen sampled storage policy. No unrelated tests, builds, solver jobs
or offline proof replay ran concurrently with the measured sequence. Shared
host load was not controlled and caches were not flushed. This was not a run on
the author's personal machine.

Supervisor wall time includes startup, source reads, construction, native stages
and worker bookkeeping, and excludes later cleanup and compression. Recorded
supervisor/descendant CPU observations also include cleanup; they are not exact
within-deadline CPU measurements. Sampling gaps and peaks remain observations,
not an instantaneous aggregate filesystem quota.

The [offline verifier](completion_v1/verify_study.py) independently replayed all
**115 completed CNF proofs**: 90 from ten accepted witnesses and 25 completed
before the five stopped exporter trials. It checks the exact planned prefix,
frozen sources and inputs, raw/stored hashes, commands, streams, phase records,
limits, acceptance obligations and final suspension. No SAT assignment was
produced in this study. The earlier positive and corrupted-witness qualification
controls remain separately retained and verified.

CNF replay establishes the supplied formulas' unsatisfiability. Native
model/witness-to-obligation and CNF translations remain trusted; this is not
end-to-end formal verification or a new algebraic theorem. Hashes bind retained
bytes but are not signatures or an attestation of execution.

## Evidence and reproduction

The lossless [study archive](completion_v1/study_20260927.tar.xz.parts/manifest.json) contains the
original protocol copy, suspension, all 32 trial inventories and every retained
raw or compressed artifact. It is distributed in hash-checked parts; the verifier
reassembles the exact archive in temporary storage before extraction. Its post-run
manifest seals those bytes; native
outputs and incomplete proof prefixes are preserved. The
[driver log](completion_v1/STUDY_DRIVER.log) retains the normal progress lines
and the stopping exception.

The [retention note](completion_v1/STUDY_RETENTION_NOTE.json) records two
unlisted raw proof copies found after execution. Both exactly matched the raw
size and hash already bound to the corresponding indexed gzip payload. Their
creation mechanism is unestablished. The extra copies were preserved outside
the study directory, while their exact contents remain losslessly retained in
the original archived payloads. No observation or proof was replaced.

From the repository root, without any native executable:

```sh
python -m research.completion_v1.verify_study
python verify.py
```

The first command safely reads the archive and independently regenerates the
report. Offline replay and archive extraction occur after measurement and are
excluded from native workflow timing. The integrated test compares the regenerated
report with the retained report and exercises counterfeit evidence.

## Next scientific decision

Review a separate prospective amendment to the shared storage policy, addressing
the interaction between the raw budget and metadata guard. Any such decision
must acknowledge these observed outcomes and preserve this frozen experiment.
Do not silently change a limit, reclassify this suspension, resume selected
trials, or substitute the two width-8 observations for three repetitions.

If a revised protocol is justified, it requires a new freeze and a fresh whole
sequence under one common policy. The original corpus and raw budget are not
opened for an outcome-driven search. Until then the matched comparison and
contribution assessment remain incomplete; manuscript drafting stays on hold.
