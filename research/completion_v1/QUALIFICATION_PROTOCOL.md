# Native baseline qualification protocol

27 September 2026. This protocol precedes its native run. It is a compatibility
qualification, **not** the matched study in `STUDY_DESIGN.md` and not its
executable protocol freeze. No comparative measurements are authorized by this
script, and no setup or interface failure counts as a performance outcome.

## Fixed scope

Build the rIC3 source candidate already selected in `BASELINE_QUALIFICATION.md`
at `8dcec6995e0e5c0adf7d4397047aafc06e9559dc`. Its README documents
`ric3 check MODEL ic3` as the single-thread route. The inspected command parser
provides `--cert PATH` and `--ui false`. The smoke command is:

```sh
ric3 check ORIGINAL_MODEL --cert SMOKE_WITNESS --ui false ic3
```

Normal preprocessing is unchanged. Do not invoke rIC3's own `--certify` as a
substitute for external acceptance, switch to the parallel portfolio, patch a
solver, or change a witness to obtain interoperability. A mismatch is BLOCKED.

The unchanged Certifaiger, AIGER, CaDiCaL and lrat-trim source pins remain those
of Gate 12, recorded explicitly in `qualify_native.py`. Direct C/C++ build
commands follow Gate 11's recorded builds with assertions enabled in the
obligation generator and AIGER tools. Each rebuilt executable gets its own
hash. Historical binary identities and observations remain unchanged.

Build rIC3 using `cargo build --locked --release --jobs 2`, after recursively
checking out its pinned submodules. Retain Cargo.lock, cargo metadata, recursive
submodule identities, compiler versions, source-tree identities, tracked-source
status, all argument arrays and build logs. The host's installed stable Rust
compiler and system package versions are setup observations, not a predeclared
reproducible toolchain image. Qualification does not freeze the later benchmark
binary, transitive build environment or resource harness by implication.

## Smoke input and controls

The smoke is the unmodified published 2-bit original
`fibonacci-02-0x3.aag`, upstream git blob
`492d5e8ed0f745bb32b9074893cf27d7bf42805a`. It is intentionally a compatibility
smoke, not a withheld benchmark case. Retain its original arbitrary-input
behavior and complete bad property. Bind consumed original bytes again before
native execution. Use the same existing external `run_native.py` path for:

| Candidate | Required observation |
|---|---|
| rIC3's fresh 2-bit witness | All nine obligations UNSAT with native LRAT replay |
| Historical `phase02` history witness | All nine obligations UNSAT with native LRAT replay |
| Historical `bad_zero02` | SAT rejection at Safety |
| Historical `reset_flipped02` | SAT rejection at Reset |
| Historical `freeze_phase04` | SAT rejection at Inductive |
| Historical `inverted_phase04` | SAT rejection at Inductive |

The original 4-bit control source must retain git blob
`908ebd7b513afa29385671c07e71167eaf1df90d`. Independently replay every completed
CNF/LRAT proof, including prefixes preceding negative-control rejections, with
the existing Python checker. If all controls behave as specified there are
30 completed proofs: 18 from the two positives and 12 from negative prefixes.
Missing obligations, a false native proof-check exit, independent replay
failure or an accepted counterfeit suspends qualification.

## Execution and interpretation

Use `python qualify_native.py --work NEW_BUILD_DIRECTORY --output NEW_EVIDENCE_DIRECTORY`
from this directory, or give the script's full path from the repository root.
The driver refuses overwrites. The GitHub Actions job runs `python verify.py`
before and after, on a public standard Linux runner, without paid services or
credentials for external solvers. It has read-only repository permissions.

Builds are separate setup work. For smoke subprocesses, enforce one CPU by
affinity and 1 GiB address space per process, with a 120-second outer process-group
deadline. The historical native driver retains its 10-second per-subprocess
limit. Process-group cleanup runs on completion and timeout. This is not a
hostile-code sandbox and is not the pending 30-second total-workflow resource
harness. There is no benchmark coverage result in this qualification.

Retain stdout/stderr, exit codes, errors, source and executable identities,
consumed inputs, generated obligations, CNFs, LRAT traces and independent replay
results. Build failures leave a machine-readable BLOCKED record, not a fictional
solver timeout. Uploaded evidence contains no external executable or source
redistribution. An archive of this repository's checked-out source may accompany
it to support offline verification; existing third-party licenses are preserved.

A successful run establishes compatibility for this tiny fixed smoke and the
negative controls only. Larger-case compatibility, end-to-end accounting,
resource enforcement, comparative coverage and significance remain separate
unfinished tasks. In particular, it does not establish a new algebraic theorem
or an advantage for the complete orbit engine. Manuscript work remains on hold.
