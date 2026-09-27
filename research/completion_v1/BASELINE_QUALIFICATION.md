# Certifying baseline qualification record

27 September 2026. Status: **bit-level IC3 executable qualified against the
existing external checker**. The six-case comparative study has not run.

## Pinned build

The official rIC3 source is pinned to
[`8dcec6995e0e5c0adf7d4397047aafc06e9559dc`](https://github.com/gipsyh/rIC3/tree/8dcec6995e0e5c0adf7d4397047aafc06e9559dc),
package version 1.5.2, with its unchanged Cargo.lock and recursively pinned code
submodules. A local build used Rust 1.98.1, Clang 18.1.3 and CMake 3.28.3:

```sh
cargo build --release --locked --offline -j 2
```

The resulting executable is 8,639,792 bytes, SHA-256
`e8ea8072fc76bbfeb002337677292b23557b045464b016fe38fcfddbe7a7ba76`.
The source and code submodules remained unmodified. The upstream release
profile retains LTO, abort-on-panic and stripping. The optional Bitwuzla wrapper
uses its upstream default stub when no system Bitwuzla is installed: word-level
SMT is unsupported in this build and is not used by the selected bit-level IC3
route. This is not a modified solver or a qualification of every rIC3 engine.

[Build provenance](qualification/build/BUILD_PROVENANCE.json) records the
source tree, Cargo.lock hash, submodules, compiler package hashes, system
tool hashes, dynamic-library paths, build command and log hash. The lockfile,
build log, compiler versions and executable help are retained alongside it.
The recipe binds this observed build; bit-for-bit rebuild determinism has not
been tested. External source and executables are not vendored. The build script
records local setup paths, not a portable installer.

## Confirmed interface

```text
ric3 check model.aag --cert witness.aag --ui false ic3 --rseed 0
```

The original ASCII AIGER input works directly, with normal preprocessing.
No conversion or adapter is needed. One IC3 worker plus its control-handler
thread runs under one-CPU affinity. No internal ten-second limit or default
parallel portfolio is used. A normal zero exit does not distinguish UNSAT,
SAT and UNKNOWN; the worker checks the result line and requires the exported
witness to satisfy the external pipeline. It never calls `--certify` or the
producer's Docker-based checker.

The pinned Certifaiger, AIGER, CaDiCaL and lrat-trim executables are exactly those
used in Gate 12. Their source and binary provenance is bound in the qualification
manifest. Certifaiger receives a separate byte-for-byte copy of the original
model, not a transformed model supplied by rIC3.

## Compatibility controls, separate from benchmark measurements

All controls use the existing synthetic three-bit rotation model with arbitrary
reseeding. It is outside the six published study cases. Its SHA-256 is
`52cbf63d24a8eb77ece89bf25042be555dc214fbd23cef4680ff93463dd50788`.
The exporter uses taps `0x4` and nonminimal odd multiple 9.

| Control | Native outcome | Independent offline check |
|---|---|---|
| Existing exporter | All nine obligations accepted | Nine LRAT proofs replayed |
| Pinned rIC3 export | All nine obligations accepted | Nine LRAT proofs replayed |
| Exporter with deliberately wrong global-period selector | Inductive obligation SAT; witness rejected | Five earlier proofs replayed; SAT assignment checks all 371 CNF clauses |
| rIC3 witness with mapped latch 0 reset changed from 0 to 1 | Reset obligation SAT; witness rejected | SAT assignment checks all 56 CNF clauses |

The rIC3 corruption changes exactly one latch line (`8 60` to `8 60 1`),
preserving its `l0 = 8` original-latch mapping and every other byte. The verifier
reconstructs that change from the accepted rIC3 witness. Neither rejection
means the original safe circuit is unsafe.

All four controls completed under the common resource harness, with successful
descendant cleanup and no observed resource violation. Their construction,
native commands, raw logs, proof artifacts and supervisor records are retained
in [the qualification manifest](qualification/MANIFEST.json). Run:

```sh
python -m research.completion_v1.verify_qualification
```

This replays 23 completed CNF proofs and checks two negative SAT assignments,
without a native executable or network access. It does not formally verify the
model/witness-to-CNF transformations. The [executable protocol](EXECUTABLE_PROTOCOL.md)
and its subsequent hash freeze govern the separate comparative experiment.
