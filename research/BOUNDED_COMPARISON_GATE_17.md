# Gate 17: completed bounded comparison after the storage amendment

27 September 2026. Manuscript preparation remains on hold.

## Decision

All **54 planned trials** completed execution under the separately frozen
amended protocol. The original primary criterion is met on **the 8-bit case**:
the exporter delivered an externally accepted witness in all three repetitions,
while the qualified rIC3 configuration reached the declared 30-second workflow
deadline in all three. No case was accepted by rIC3 in three repetitions while
remaining unknown for the exporter in all three.

This is a repeatable added-coverage observation for this fixed configuration,
budget and six-case corpus. It permits the planned focused significance and
priority review. It does not establish general solver superiority, a speedup,
new algebraic mathematics, or a benefit for the complete orbit engine. The
candidate uses the existing conventional source-aware witness construction.

## Complete outcome

Each table entry includes all three predetermined repetitions. A resource-limit
UNKNOWN is not a finding that the original model is unsafe.

| Width | Exporter | rIC3 | Structural reference |
|---:|---|---|---|
| 2 | 3 accepted witnesses | 3 accepted witnesses | 3 accepted decisions |
| 4 | 3 accepted witnesses | 3 accepted witnesses | 3 accepted decisions |
| 8 | 3 accepted witnesses | 3 deadline UNKNOWN | 3 accepted decisions |
| 12 | 3 raw-artifact UNKNOWN | 3 deadline UNKNOWN | 3 accepted decisions |
| 16 | 3 raw-artifact UNKNOWN | 3 deadline UNKNOWN | 3 accepted decisions |
| 24 | 3 raw-artifact UNKNOWN | 3 deadline UNKNOWN | 3 accepted decisions |

The totals are **33 completed workflows**, **9 raw-artifact UNKNOWN** and
**12 deadline UNKNOWN**. Completed workflows comprise nine exporter witnesses,
six rIC3 witnesses and 18 structural decisions. There was no metadata-limit
suspension or selective rerun. All 54 trial outcomes are retained.

For the 8-bit exporter, complete workflow times were 4.575608, 4.396952 and
4.713342 seconds: median 4.575608 seconds, range 4.396952–4.713342 seconds.
Each retained 25,241,374 raw artifact bytes. These are observations on one host,
not population statistics. The corresponding rIC3 deadlines are censored
observations, not measured completion times; no ratio of them is a measured
speedup. The [machine-readable report](completion_v2/STUDY_REPORT.json) provides
the completed-trial medians and full ranges for every route and width.

The structural route accepted all six widths, but supplies a separate trusted
decision rather than the consumer's required AIGER witness. Its timing cannot
substitute for the cost of constructing and externally checking that witness.
Both witness routes use the same original model and external native checker.
The exporter receives and validates explicit structural hints; rIC3 is the
fixed generic single-worker configuration with ordinary preprocessing. This
comparison does not establish superiority over other rIC3 configurations or
source-aware methods using the same mathematics.

## A separate, outcome-informed experiment

The [first comparison](BOUNDED_COMPARISON_GATE_16.md) remains suspended at its
original 32-trial prefix. Its outcomes, protocol, freeze and evidence remain
unchanged. None of its repetitions enter this gate's primary result.

The [amendment](completion_v2/STORAGE_AMENDMENT.md) was selected after seeing
that the first all-file guard consumed raw-artifact headroom with diagnostic
metadata. It is explicitly outcome-informed. The amendment retained the 64 MiB
raw budget and introduced a separate 64 MiB metadata budget, with an implied
128 MiB combined guard. It retained one CPU, 1 GiB address space per process,
30 seconds per complete workflow, 64 MiB per file and 1 MiB per captured stream.
The sources, corpus, exporter hints, native binaries, commands, seed, order,
three repetitions and primary decision rule stayed fixed.

Only 69 exact control/log paths count as metadata; an arbitrary JSON or log
extension does not create an exemption. Unknown paths, every file in `tmp/`
and every visible open deleted file count as raw. Known atomic JSON copies are
metadata while present and raw if observed after deletion. Both component caps
are sampled acceptance budgets, not instantaneous aggregate filesystem quotas.
Metadata exhaustion remains an execution issue even alongside a deadline or
raw excess. The largest observed metadata total was 164,783 bytes; this outcome
did not determine the prospective metadata budget.

The source tree was committed before measurement as
`73b9efff0353cb61510bc1a72ac8308656d6d6fc`, tree
`2f2d8c4eed2e80298d7e48c7ed8069c777dc9e6a`. The
[protocol freeze](completion_v2/PROTOCOL_FREEZE.json) has SHA256
`3d0343852203e03b516a5c9fdce67eb062be33fb701a09fa9f2b307655179872`.
The [run context](completion_v2/STUDY_RUN_CONTEXT.json) records the equivalent
local source commit, Python runtime and AMD EPYC container. The full pre-run
verification passed 99 tests and the unchanged exact 4,772-case audit.

No project tests, builds, solver jobs or proof replay ran concurrently with
the measured sequence. Shared host load was not controlled and caches were not
flushed. This was not a run on the author's personal machine. The workflow clock
includes startup, source recognition, factorization, construction, native checks
and worker bookkeeping. Subsequent cleanup, compression and offline proof replay
are separate. CPU accounting includes cleanup and is not an exact within-deadline
CPU measurement.

## Verification and retained evidence

The same four tiny synthetic qualification controls ran under the amended
supervisor before the new freeze. Both positive witnesses passed all nine
obligations; the incorrect exporter selector and corrupted rIC3 latch reset were
rejected. The [qualification evidence](completion_v2/qualification/MANIFEST.json)
supports independent replay of 23 completed proofs and checking both negative
SAT assignments. These controls are outside the six-case comparison.

The [offline verifier](completion_v2/verify_study.py) independently replayed all
**180 completed CNF proofs**: 135 from the 15 accepted witnesses and 45 completed
before the nine raw-artifact stops. No SAT assignment was produced in the study.
The verifier checks the complete fixed sequence, frozen sources and inputs,
qualified binaries, artifact hashes, native command records, streams, phase
records, resource observations and final outcome. It regenerates the retained
report without executing a native tool.

CNF proof replay establishes unsatisfiability of the supplied formulas. Native
model/witness-to-obligation and CNF translations remain trusted. This is not
end-to-end formal verification. Hashes bind the retained evidence bytes; they
are not signatures or an attestation of execution.

The [lossless study archive](completion_v2/study_20260927_v2.tar.xz.parts/manifest.json)
contains the protocol copy, all 54 trial inventories, retained raw or compressed
artifacts, and the post-run evidence seal. Its 65,426,660 bytes are distributed
in 16 hash-checked parts. The archive SHA256 is
`cd0521ad4d6e2a098ccb3a30f48257671f714ae449cfb0180e47786423c6673d`.
The verifier reconstructs and safely extracts the archive in temporary storage
before checking its evidence.

The [retention note](completion_v2/STUDY_RETENTION_NOTE.json) records ten
unindexed raw copies observed after measurement: three 8-bit Inductive proofs
and seven native files from the second 24-bit exporter trial. Each copy matched
its indexed compressed artifact byte-for-byte. The copies were preserved in a
separate recovery directory; their exact contents remain losslessly retained
in the canonical indexed artifacts. Their creation mechanism is unknown and
they are not timing evidence. No measured record or indexed payload was changed.

From the repository root:

```sh
python -m research.completion_v2.verify_qualification
python -m research.completion_v2.verify_study
python verify.py
```

Offline reconstruction, extraction and proof replay are outside the measured
workflow times. They validate retained evidence without rerunning the comparison.

## Remaining scientific step

Assess the surviving scoped result against the closest existing certifying
exporter and hardware-witness literature. The question is whether converting
this conventional source-aware construction into an externally accepted witness
provides a meaningful and sufficiently distinct contribution for the documented
consumer. The completed coverage criterion alone does not answer priority,
novelty or significance.

Keep the original corpus and measured evidence fixed during that assessment.
Another format, broader domain, larger exponent or favorable budget search is
not the next step. Resolve the contribution boundary, then freeze the final
claims and limitations. Manuscript drafting remains on hold.
