# Fixed native ABC PDR probe

The six cases and resource limits in [the protocol](../NATIVE_PROTOCOL.md) were
fixed before any solver run. This probe obtained **two native SAFE verdicts and
four unknown outcomes**. A timeout says nothing about whether another strategy,
longer limit, or source-aware algebra would succeed.

| LFSR width | ABC PDR outcome | Observed process wall time |
|---:|---|---:|
| 2 | SAFE, ABC status 1 | 0.042 s |
| 4 | SAFE, ABC status 1 | 0.385 s |
| 8 | UNKNOWN, external timeout | 10.007 s |
| 12 | UNKNOWN, external timeout | 10.006 s |
| 16 | UNKNOWN, external timeout | 10.006 s |
| 24 | UNKNOWN, external timeout | 10.012 s |

There was one cold solver process per case, no preprocessing portfolio or
post-result parameter tuning, a 10-second wall budget, and a 1 GiB address-space
limit. The external Python watchdog polls every 10 ms; the small wall overshoot
includes scheduling and process reaping. Compilation and format conversion are
outside the reported solver-process times. This is not a matched comparison of
total verification costs or independent replay of an ABC proof. ABC itself reports
successful invariant checking in the two conclusive runs.

The source-aware odd-order/squarefree argument remains the stronger relevant
classical comparator. These results establish neither novel algebra nor
superiority over hardware verification tools.

## Exact inputs and tools

The source corpus is pinned to `c8efd0251c0548dd46168db8410e6777c5f82b73` of
[tniessen/aiger-safety-properties](https://github.com/tniessen/aiger-safety-properties).
Every actual input was checked against its recorded Git blob before invocation.
The original bad-output property, arbitrary input/reseeding behavior, and
zero-initialized latches are retained.

- [Berkeley ABC](https://github.com/berkeley-abc/abc), commit
  `ab2139ee0c418f54136deb4e8e89eeea3b87efc8`.
- [AIGER converter](https://github.com/arminbiere/aiger), commit
  `039ec1a2cc37d3093ac35c4b6df65336b346f409`.

ABC was built with `make -j6 ABC_USE_NO_READLINE=1`; AIGER with
`./configure.sh` and `make -j2 aigtoaig`. Both tracked source trees were clean.
The earlier no-CUDD ABC configuration failed to link because upstream
`cecSatG2.c` references CUDD routines; that failed log and the clean/default-CUDD
build logs are retained. No upstream source was patched. GCC/G++ 13.3.0 on Linux
x86-64 were used; [environment.json](environment.json) records details.

The first measurement-wrapper attempt failed before invoking ABC because
`/usr/bin/time` was absent. The replacement Python watchdog and `os.wait4`
measurement were installed before the first solver run. The incident and its
conversion-only output are retained separately.

The final command was `abc -s -c 'read_aiger CASE.aig; pdr -S 91648253; print_status'`,
with `stdbuf` for log flushing. `-s` disables initialization files. PDR otherwise
uses the pinned defaults, including its 10,000-frame cap. No frame-limit outcome
occurred in this run.

## Conversion assurance and offline replay

Official `aigtoaig` converts the source AAG to binary AIGER, and then back to
AAG for checking. Gate numbering and the order of AND fanins change. The runner
therefore compares the exact AND DAGs with shared tuple interning, identifying
input and latch leaves by position, retaining complement bits, and sorting the
two AND fanins. Latch initial values, all next-state roots, and all output roots
must match. Induction through the acyclic gates proves identical Boolean
functions; equality of next states and initial latches then proves identical
transition systems. No probabilistic hash is used for that structural equality.
This is a check for these pinned basic-AAG files, not a general AIGER frontend.

All six conversion checks passed. The AIG files below are converted input data,
not executable binaries. Solver executables and source checkouts are not vendored.

```sh
python research/aiger_lfsr_v1/verify_native.py
```

This offline command verifies the evidence manifest, original input blobs,
conversion structure, and recorded verdict/timeout consistency. It starts no
solver and makes no network call. It validates the integrity of the recorded
experiment, not an independently supplied PDR proof.

[run_native.py](../run_native.py) is preserved byte-for-byte as executed. To rerun
it, supply the retained executables and a fresh output directory:

```sh
python research/aiger_lfsr_v1/run_native.py \
  --upstream research/aiger_lfsr_v1/upstream \
  --abc /absolute/path/to/abc \
  --aigtoaig /absolute/path/to/aigtoaig \
  --out /absolute/path/to/fresh-results
```

The observed runner requires the exact binary SHA256 values in
[TOOL_PROVENANCE.json](TOOL_PROVENANCE.json), as well as pinned clean source
checkouts beside the binaries. Rebuilding in another environment or directory
can change binary hashes, especially with debug information. Such a new build
requires a separately recorded rerun configuration; do not overwrite this
historical provenance to force a match.

[results/results.json](results/results.json) contains commands, source/conversion
hashes, exit statuses, measured times, and the exact runner/plan hashes. Per-case
stdout, stderr and `os.wait4` resource records are adjacent.
[MANIFEST.json](MANIFEST.json) covers the observed runner, plan, build and
environment records, preflight incident, and raw case evidence.
