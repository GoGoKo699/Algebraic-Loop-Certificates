# Certifying baseline qualification record

27 September 2026. Status: **source inspected; executable not qualified**.
No rIC3 benchmark or native proof replay has been run in this checkpoint.

The official rIC3 source candidate is pinned to
[`8dcec6995e0e5c0adf7d4397047aafc06e9559dc`](https://github.com/gipsyh/rIC3/tree/8dcec6995e0e5c0adf7d4397047aafc06e9559dc).
Its [`Cargo.toml`](https://github.com/gipsyh/rIC3/blob/8dcec6995e0e5c0adf7d4397047aafc06e9559dc/Cargo.toml)
declares package version 1.5.2, Rust edition 2024 and executable `ric3`.
The dependencies include separately built SAT/SMT and AIGER components; the
package version alone does not bind those dependencies or the final executable.

The inspected
[`src/cli/check.rs`](https://github.com/gipsyh/rIC3/blob/8dcec6995e0e5c0adf7d4397047aafc06e9559dc/src/cli/check.rs)
(Git blob `68f81945e946a6a6380b539dc15666c767221f30`) exposes `--cert` for writing
a certificate and a separate `--certify` option for invoking the tool's own
checker path. Bit-level certificate writing occurs after a conclusive engine
result and applies the frontend's certificate transformation. This is source
evidence for an export path, not proof that the resulting bytes interoperate
with our pinned external checker.

The intended configuration is a documented single-worker IC3 engine with
certificate output, retaining its normal preprocessing. Confirm the exact full
command against the built executable's help and a labeled tiny smoke case.
Use the fixed external Certifaiger/CNF/LRAT path for comparative acceptance;
do not substitute the producer's own `--certify` result for it. Record any
additional worker/runtime threads and enforce the same CPU allowance.

Environment inspection found no `cargo` or `rustc` on PATH and no existing
rIC3 executable in the inspected working directories. The older official
[HWMCC'24 submission](https://github.com/gipsyh/rIC3-HWMCC24/tree/4c02bcfb04aa096e62947a0fb03e9af00adbc4b7)
documents a certificate output but uses a different command-line interface and
a default parallel portfolio. It is not an automatically interchangeable
replacement for the current source candidate or the single-worker comparison.

Next actions are to obtain a reproducible build or a provenance-bound official
binary, freeze dependencies and executable hashes, and pass the smoke input
through all external obligations. Setup and compatibility failures must be
reported as an incomplete comparison. Do not interpret missing local tooling
as a timeout, a solver limitation or evidence in favor of the exporter.
