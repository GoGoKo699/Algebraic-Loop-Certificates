# Completed bounded comparison with separate storage budgets

The [current result](../BOUNDED_COMPARISON_GATE_17.md) completes all 54 planned
trials. The original three-of-three added-coverage criterion is met on the
8-bit case: three accepted exporter witnesses and three rIC3 workflow deadlines.
Manuscript preparation remains on hold.

| Recorded outcome | Exporter | rIC3 | Structural | Total |
|---|---:|---:|---:|---:|
| Completed workflow | 9 | 6 | 18 | 33 |
| Deadline UNKNOWN | 0 | 12 | 0 | 12 |
| Raw-artifact UNKNOWN | 9 | 0 | 0 | 9 |
| Attempted | 18 | 18 | 18 | 54 |

The exporter supplies accepted witnesses at widths 2, 4 and 8; the fixed rIC3
configuration supplies them at widths 2 and 4. The structural reference accepts
all six widths, with a different decision-only output contract. At widths 12,
16 and 24 both witness routes remain UNKNOWN within the declared budgets. There
is no reverse exclusive coverage result.

The 8-bit exporter workflow median is 4.575608 seconds, with a full range of
4.396952–4.713342 seconds; each trial retained 25,241,374 raw artifact bytes.
The baseline's 30-second deadlines are not measured completion times and do not
support a measured speedup ratio. These are scoped observations on a fixed
hand-designed corpus and configuration. The exporter receives structural hints
and uses conventional mathematics; the complete orbit engine is not involved.

The [storage amendment](STORAGE_AMENDMENT.md) separates 64 MiB raw and 64 MiB
metadata acceptance budgets. It was chosen with knowledge of the
[earlier suspended experiment](../BOUNDED_COMPARISON_GATE_16.md), whose evidence
and classification remain unchanged. This fresh whole sequence does not pool
or resume earlier repetitions. All other scientific conditions and the primary
criterion are retained. The [executable protocol](EXECUTABLE_PROTOCOL.md) and
[freeze](PROTOCOL_FREEZE.json) were recorded before the new measurements.

The [report](STUDY_REPORT.json), [run context](STUDY_RUN_CONTEXT.json),
[retention note](STUDY_RETENTION_NOTE.json), [driver log](STUDY_DRIVER.log) and
[lossless archive](study_20260927_v2.tar.xz.parts/manifest.json) retain the
outcomes and execution boundaries. Independent replay validates all
**180 completed study proofs**, including 45 completed before interrupted
exporter solves. The retention note records ten unindexed raw copies found
after measurement; all exactly matched indexed compressed artifacts, were
preserved separately, and are not timing evidence. Their creation mechanism
remains unknown.

The separate [qualification evidence](qualification/MANIFEST.json) contains the
successful positive controls and rejected corruptions, with 23 completed proofs
and two negative SAT assignments checked independently. Check both evidence
sets without invoking native tools:

```sh
python -m research.completion_v2.verify_qualification
python -m research.completion_v2.verify_study
```

Native model/witness-to-CNF translations remain trusted. Independent CNF proof
replay is not end-to-end formal verification. Source-aware structural decisions
remain separate from the consumer's required externally checked witness.

The next task is a focused significance and priority assessment against existing
certifying exporters. A completed coverage criterion does not establish novelty
or general solver superiority, and does not authorize expanding the experimental
search. Manuscript drafting is the final step.
