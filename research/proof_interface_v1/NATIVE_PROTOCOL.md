# Frozen external witness-replay gate

27 September 2026. This protocol is fixed before the native certificate checks.
No production API or original circuit property is changed.

The accepted interface is Certifaiger's existing AIGER model/witness format.
Every check receives the original unrestricted-input safety model separately
from the untrusted candidate witness. The witness retains all original inputs,
latches, resets and transitions under explicit literal mapping. Extra history
latches are permitted by the existing interface, with zero reset here. Its
single bad signal is a strengthened property; the external safety obligation
must imply the original full bad-signal property, including arbitrary reseeding.

## Tools frozen for execution

| Tool | Git commit |
|---|---|
| Certifaiger | `27d526e3e979074c3e92582768f577dc6eddb0da` |
| AIGER tools/library | `039ec1a2cc37d3093ac35c4b6df65336b346f409` |
| CaDiCaL | `c60730422e758ef1cebe7aeddf2dda31c996bf04` |
| lrat-trim | `adba6e61368e91957c79bf952b29800f05dbee51` |

The pipeline calls unchanged native Certifaiger to construct its nine named
obligations, native `aigsplit` to separate them, and native `aigtocnf` to produce
CNF. The safety-only inputs still generate four trivial liveness obligations;
none will be skipped. CaDiCaL emits an LRAT trace for each UNSAT result and
`lrat-trim` independently checks that trace against the exact emitted CNF.
Native UNSAT without successful proof replay is not acceptance.
Use `--lrat --no-binary --no-factor` to retain readable traces and avoid the
factoring extension, consistent with Certifaiger's verified-LRUP-checker setup.

## Fixed cases and limits

1. ABC PDR-exported forbidden-cube witnesses at widths 2 and 4, translated to
   AIGER by an untrusted adapter. These establish the standard interface baseline.
2. History-register witnesses at widths 2, 4 and 8 from the same original family.
   Width 8 is the first frozen native PDR timeout case. Do not expand the sweep
   after observing results. The phase construction's stronger common-period
   premise must be explicit; odd order alone is not its justification.
3. Two malformed width-2 witnesses: replace their sole bad output with constant
   false; flip an original mapped latch reset. They must not be accepted. These
   are invalid proof candidates for the same original safe model, not unsafe
   model counterexamples.
4. Two width-4 history controls, fixed before replay: freeze the history register
   instead of advancing it; invert the asserted phase parity. Both must fail.

Each native process has a 10-second wall limit and 1 GiB address-space limit.
Retained proof/circuit artifacts are capped at 64 MiB per case; hitting a limit
is UNKNOWN, not a negative safety verdict. Record exit codes, stdout/stderr,
source and binary hashes, witness/construction sizes, per-stage times and total
replay cost. Preserve all generated obligations and completed proof traces.
The limits and single observations establish no statistical speedup ratio.

## Decision and trust boundary

The gate succeeds as an integration if an unchanged external witness checker
accepts a candidate and every SAT proof is replayed against the original full
task. Width-8 timeout remains an admissible recorded outcome. A malformed witness
accepted at any stage is a failed gate and must be investigated.

The candidate constructor and SAT search need not be trusted after validation.
The remaining trusted code includes Certifaiger's parser/mapping/obligation
construction, AIGER's parser and CNF translation, the LRAT checker, compiler and
execution environment. This is not end-to-end proof-assistant verification.
An additional transparent offline checker may replay supported LRAT steps; it
must reject unsupported proof rules rather than silently treating them as checked.

The conventional squarefree-polynomial or primitive-polynomial route can produce
the same witness when its needed premise holds. The complete orbit engine has
no presumed advantage at this interface. No new proof-system or mathematical
priority claim follows merely from an accepted witness.
