# Native ABC invariant export for two existing cases

This follow-up uses the same pinned native tool and unchanged original source
cases as the six-case PDR probe. Only the two already solved widths 2 and 4 are
rerun to request an exported proof object; it is not a new performance benchmark.

`PLAN.json` was written before either export. Both exports reported ABC status 1.
`EXPORT_RESULTS.json` preserves actual commands, binary/input/PLA SHA256 values,
exit codes, stdout and elapsed process times. Separate stdout/stderr files retain
the raw logs. The command uses `pdr -S 91648253 -d -e -I FILE`.

| Width | Latches | Exported forbidden cubes | PLA file bytes |
|---:|---:|---:|---:|
| 2 | 5 | 10 | 376 |
| 4 | 9 | 136 | 1,981 |

ABC is pinned at `ab2139ee0c418f54136deb4e8e89eeea3b87efc8` from
https://github.com/berkeley-abc/abc. The exact binary was checked against the
earlier `native/TOOL_PROVENANCE.json`, the source commit was checked, and its
tracked tree was clean. Each binary AIGER input was checked against the previous
conversion record. Each process had a 10-second timeout and 1 GiB address-space
limit. No upstream source was modified.

## Export contract

`src/proof/pdr/pdrCore.c:Pdr_ManSolve` calls
`src/proof/pdr/pdrInv.c:Pdr_ManDumpClauses`. Each PLA row is a blocked latch cube,
printed by `src/proof/pdr/pdrUtil.c:Pdr_SetPrint`. The disjunction of those rows
is the complement of the invariant. `-e` toggles the default support-only
export off, retaining all latch positions; `.ilb` also records their names.
The documented export requires all-zero initial states, as in these circuits.
The source comments and the PLA title alone are not a proof: a checker must
establish initial inclusion, closure, and property implication.

ABC has `inv_check` and `inv_get`/`inv_put` commands, implemented in
`src/base/wlc/wlcCom.c`. `inv_check` uses ABC's own SAT routines through
`Pdr_InvCheck`; this is not an independent external validation path. The native
PDR log's invariant check is likewise not a separate proof-assistant replay.

## Adapter for an existing external witness checker

`pla_to_witness.py` is an **untrusted format adapter** for Certifaiger's existing
AIGER circuit-witness interface. It preserves original input/latch numbering,
initial values, next-state rows, and original AND gates; it appends gates for the
forbidden-cube disjunction and uses that as the witness bad output. Explicit
`iK = literal` and `lK = literal` symbols map shared variables to the original
model. The original model remains the trusted specification supplied separately.
Certifaiger, not this adapter, must validate the relationship and safety.

`n02-witness.aag` and `n04-witness.aag` are the generated candidates. Their
conversion records bind the original raw source, exported PLA and witness by
SHA256. They add 37 and 958 AND gates respectively. The external checker run and
its results are recorded separately by the native-interface task; the existence
of these files alone is not an acceptance claim.

The two larger proof files describe conventional Boolean inductive invariants.
Neither native export nor a successful replay would establish a new algebraic
proof format, a faster verifier, or completeness for the larger timed-out cases.
