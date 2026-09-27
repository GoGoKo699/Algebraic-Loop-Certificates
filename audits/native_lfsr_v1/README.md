# Native LFSR workload gate

27 September 2026. **The existing native analyzer resolves this workload.**
Maximal LFSR period does not supply the missing capability gap for the complete
algebraic orbit compiler. Manuscript preparation remains on hold.

The [protocol](PROTOCOL.md) was committed locally before the native run and is
published with its evidence. Its input is
an existing compiled generator with a supported binary-linear state update;
its output is maximal nonzero-state period, nonmaximal period, or an unsupported
input. This is SmokeRand's own task and advertised controls. It does not ask
for a target offset, an arbitrary guard, random quality, or a general C proof.

## Recorded result

SmokeRand 0.51 at commit `20f3adab3121b4205a12f06746055551e6504648` was built
without source changes, using its GNU Makefile and GCC 13.3.0.

| Native input | Explicit native verdict | Exit code | Process wall time |
|---|---|---:|---:|
| shr3 | Maximal, 32 bits | 0 | 0.0850 s |
| xorrot32, default | Maximal, 32 bits | 0 | 0.0838 s |
| xorrot32, bad1 | Nonmaximal | 1 | 0.0868 s |
| xorrot32, bad2 | Nonmaximal | 1 | 0.0850 s |
| xoroshiro128pp | Maximal, 128 bits | 0 | 0.2158 s |
| xoshiro256pp | Maximal, 256 bits | 0 | 0.2022 s |
| splitmix | Analysis not applicable | 2 | 0.1174 s |
| sfc64 | Analysis not applicable | 2 | 0.1137 s |

All eight agreed with the upstream documented categories; none timed out.
The last two are domain refusals, not mathematical nonmaximality decisions.
[RESULTS.json](native/RESULTS.json), the per-case stdout/stderr files and
[build.log](native/build.log) preserve the observations. The initial build time
was not measured. Each time above includes a fresh process, native probing,
algebra and output; these single observations establish no performance ratio.

## Existing checker on the same 32-bit cases

[check.py](check.py) translates the four inspected 32-bit recurrences and uses
the unchanged root proof assembler/checker. [expected.json](expected.json)
records acceptance of the two genuine maximal periods and rejection of the
two false period claims. Each serialized candidate is 2,603 bytes, excluding
the separately trusted problem document. No orbit enumerator is run.

The negative conclusions also have independent packed-bit witnesses: starting
from state 1, bad1 reaches 1,166,829,039 after 4,294,967,295 updates; bad2 returns
to 1 after 858,993,459 updates. These witnesses, rather than certificate
rejection alone, refute the respective maximal-period claims. For a linear
invertible map fixing zero, a nonzero point with period `2^32 - 1` exhausts all
nonzero states, so the positive point-order certificate answers this consumer.

The [C harness](transition_probe.c) includes the unchanged upstream routines.
[TRANSITION_PROBES.json](native/TRANSITION_PROBES.json) records 160 native outputs:
32 basis vectors and eight fixed sample words for each of the four recurrences.
These check the Python translation; their finite sample does not certify an
arbitrary C program's behavior. [local_timings.json](local_timings.json) keeps
translation, assembly and checking observations separate from the native runs.
The larger native cases are coverage evidence, not matched root-checker cases.

## Trust and application boundary

SmokeRand uses established order tests and characteristic/jump polynomials,
with fixed tables of period-quotient exponents. Its empirical checks of
linearity and state layout are guards, not a formal proof of arbitrary code.
The executed path trusts its C implementation, compiler and tables. The root
checker instead checks its supplied complete prime factorization with exact
prime witnesses, but trusts the problem translation and its own Python code.
Neither run is proof-assistant replay or a cleared novel assurance result.

OpenTitan provides a concrete hardware motivation: its `prim_lfsr` documentation
states maximal-period requirements and distinguishes formally checked transition
logic from simulation sweeps through width 34. That does not establish that
larger widths lack algebraic analysis. External entropy, seed loading, reset,
enable and lockup recovery alter the hardware transition contract. This audit
executes no OpenTitan HDL and certifies none of those behaviors. Its native
experiment is solely the listed SmokeRand workload. See [SOURCES.md](SOURCES.md).

## Reproduction

The ordinary repository verifier rechecks the local algebra and stored evidence.
To rerun the external baseline, obtain a clean checkout and build the six
plugins using the upstream Makefile (commands below start at this repo's root):

```sh
git clone https://github.com/alvoskov/SmokeRand.git /tmp/alc-SmokeRand
git -C /tmp/alc-SmokeRand checkout --detach 20f3adab3121b4205a12f06746055551e6504648
make -C /tmp/alc-SmokeRand -f Makefile.gnu -j2 bin/smokerand bin/generators/shr3.so bin/generators/xoroshiro128pp.so bin/generators/xoshiro256pp.so bin/generators/xorrot32.so bin/generators/splitmix.so bin/generators/sfc64.so
python audits/native_lfsr_v1/run_native.py --source /tmp/alc-SmokeRand --output /tmp/alc-lfsr-rerun
```

The runner refuses an existing output directory, a different source commit,
or modified tracked source. It makes no network request and installs nothing.
Binary hashes are recorded, not expected to survive a compiler/platform change.
The original report retains the actual scratch checkout path and nondeterministic
native diagnostics. Its `build_command` lists the same targets in canonical
order; the command above gives the original target order. Logs and JSON were
copied without byte changes. Later runs need not reproduce timing, addresses,
machine diagnostics, initialization seeds or log hashes.

To reproduce the transition observations, compile our harness against that same
checkout and invoke both executables:

```sh
gcc -std=c99 -O2 -ffunction-sections -fdata-sections -Wl,--gc-sections -DHARNESS_SHR3 -I /tmp/alc-SmokeRand -I /tmp/alc-SmokeRand/include audits/native_lfsr_v1/transition_probe.c -o /tmp/alc-shr3-probe
gcc -std=c99 -O2 -ffunction-sections -fdata-sections -Wl,--gc-sections -I /tmp/alc-SmokeRand -I /tmp/alc-SmokeRand/include audits/native_lfsr_v1/transition_probe.c -o /tmp/alc-xorrot32-probe
/tmp/alc-shr3-probe
/tmp/alc-xorrot32-probe
```

Compare the rows with `native/shr3.transition-probe.csv` and
`native/xorrot32.transition-probe.csv`. The original probe metadata retains the
then-used harness filename `smokerand_transition_probe.c`; the repository copy
is named `transition_probe.c` and has identical contents. No upstream source or
binary is vendored into this audit.
