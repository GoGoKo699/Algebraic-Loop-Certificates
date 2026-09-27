# Native invariant-validation gate: no demonstrated need for the orbit compiler

The concrete obligation was initiation and universal one-step preservation of
an already supplied power-relation invariant. The fixed native experiment did
not establish a capability gap that requires the full algebraic orbit compiler.
Manuscript writing remains on hold. No new orbit theorem or format is introduced.

## Recorded result

The protocol and generator were committed at `8da6f2569e8c2cf18d96e539be7fc1d6d8468abd`
BEFORE the native experiment. No source, exponent, expected verdict, solver flag
or resource limit was changed after seeing the results. The 20 source-visible
controls have ten preserved relations and ten broken updates; each broken
case has an explicit one-step counterexample at the initial state.

| Native cvc5 route | Valid invariants proved | Broken updates detected | Unknown |
|---|---:|---:|---:|
| Direct counterexample query | 10/10 | 9/10 | 1/20 |
| Frozen batched multiplication-DAG decomposition | 4/10 | 10/10 | 6/20 |

Every conclusive verdict agrees with the mathematical control. There were no
parser, unsupported-field or nonzero-exit errors in this run. The existing
Python certificate checker separately accepted the ten valid certificates and
rejected the ten broken ones; its time was not measured. A certificate rejection
is not generally a proof that an invariant is false: the explicit counterexample
is what establishes falsity in these controls.

All ten direct valid queries completed in 6.026 to 64.335 milliseconds, including
cold process startup. These are SINGLE observations, not medians, statistical
speedups or hardware-independent bounds. The largest mixed broken query returned
unknown at the two-second internal limit. The decomposed route decided that
case, but returned unknown on all six larger valid cases. Neither route therefore
dominates on all recorded cases. In particular, the failures of this disjunction-
batched encoding are not a theorem about all proof-decomposition strategies.

The direct route already verifies every positive preservation claim in this
corpus. Thus this gate does not justify a larger study based on the assertion
that high-power invariants need our full orbit machinery. It does not prove
that the existing certificate checker has no possible speed or assurance benefit.
Those would require different, explicit matched measurements or proof replay.

## What was actually run

GitHub Actions run `36295303134`, job `108552934824`, checked the pinned official
cvc5 1.4.1 static-GPL asset and ran all 40 formulas. The build reports CoCoA support.
[The native job](https://github.com/GoGoKo699/Algebraic-Loop-Certificates/actions/runs/36295303134/job/108552934824)
retains the complete stdout/configuration and per-case JSON rows. The original
41-file artifact has SHA256 `fd0b32f9292d30ace9c6331512ef728a96801b7545ddc80b4c5459c16a3d749a`
and a 30-day retention period. Solver binaries are not redistributed here.

`native_observations.json` permanently records selected exact fields extracted
from those JSON log rows, with source-run and binary provenance. It is explicitly
NOT a byte-identical download of the original native artifact. All 40 measured
formula hashes were checked against local regeneration from the frozen source.
The original full artifact has its own hash; it must not be confused with this
selected-field record. The frozen formulas can be regenerated without cvc5.

Limits: one cold solver process per case/route, default finite-field solver,
2,000 ms internal time, three-second external grace and 1,536 MiB address-space
limit. Recorded time excludes formula generation, certificate construction and
local certificate checking. No native proof was exported or replayed: UNSAT/SAT
verdicts are not CPC, Pacheck or Lean proof-assistant validation.

## Reproduce without rewriting evidence

```sh
python audits/invariant_validation_v1/verify.py
python -O audits/invariant_validation_v1/verify.py
```

These standard-library commands regenerate the 20 exact semantic controls and
check all measured input hashes and summary counts. They DO NOT rerun cvc5.
The full local control report has a fixed hash in `expected.json`; stored native
outcomes are never made golden timing expectations for a new run.

With an already installed suitable native binary, use a fresh output directory:

```sh
python audits/invariant_validation_v1/gate.py --solver /path/to/cvc5 --output /new/result-directory --timeout-ms 2000
```

The dedicated CI workflow performs that optional native run with a pinned official
asset. Normal root tests do not download or install anything. Later executions
produce separate artifacts; they never replace the first-run observations.

Read [PROTOCOL.md](PROTOCOL.md) for the mathematical decomposition and predeclared
criteria, [SOURCES.md](SOURCES.md) for current finite-field proof precedents, and
[the research assessment](../../research/VERIFICATION_GATE_09.md) for the decision.
