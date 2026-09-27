# Frozen odd-order premise controls

This protocol is fixed before any Gate 12 native execution. It retains the
existing Certifaiger interface and does not modify Gate 11 artifacts.

| Case | Model | Supplied odd exponent | Witness |
|---|---|---:|---|
| `rotation3` | New synthetic n=3 wrapper, taps `0x4` | 9 = 3² | Exact seed-period selector |
| `mixed5` | New synthetic n=5 wrapper, taps `0x11` | 63 = 3²·7 | Exact seed-period selector |
| `published8` | Original published n=8 wrapper, taps `0xb8` | 255 = 3·5·17 | Exact seed-period selector |
| `rotation3_global` | Same synthetic n=3 model | 9 | Deliberately force the global bound as seed period |
| `mixed5_omit` | Same synthetic n=5 model | 63 | Deliberately omit the second 3-adic fixed-space test |

There are exactly three planned positive witnesses and two bad-certificate
controls. The synthetic models retain the original monitor equations and
arbitrary reseeding but are not represented as published upstream instances.
The original published file remains unchanged. An independently written raw
wrapper emitter and exhaustive arithmetic checks bind the synthetic models.

Use the unchanged `research/proof_interface_v1/run_native.py` driver and the
same five pinned tool executables as Gate 11. Every positive candidate must
pass all nine named obligations: Reset, Transition, Safety, Liveness, Base,
Inductive, Decrease, Closure, and Consistent. Each emitted CNF requires an UNSAT
verdict plus native LRAT replay; retained completed proofs are subsequently
replayed with the existing independent Python LRAT checker. A SAT obligation
rejects a witness, not the safe source model. A failed construction is not an
accepted witness. Timeouts and resource limits remain UNKNOWN.

Fixed limits: 10 seconds per native process, 1 GiB address space, and 64 MiB
raw AAG/AIG/CNF/LRAT artifacts per case. Retain partial evidence after limits.
Use CaDiCaL `--quiet --unsat --lrat --no-binary --no-factor`, as before. No
post-result changes to cases, exponents, mutations, limits, or solver strategy.

Tool pins: Certifaiger `27d526e3e979074c3e92582768f577dc6eddb0da`;
AIGER `039ec1a2cc37d3093ac35c4b6df65336b346f409`;
CaDiCaL `c60730422e758ef1cebe7aeddf2dda31c996bf04`;
lrat-trim `adba6e61368e91957c79bf952b29800f05dbee51`.
Before native runs, record exact driver/producer/model/witness/tool hashes and
candidate construction timings in `native/BUILD_PROVENANCE.json` and
`native/CONSTRUCTION.json`. Compression occurs only after execution; files
larger than 64 KiB use deterministic gzip, retaining raw and stored hashes.

This is a narrow premise-preservation experiment. It is not a new benchmark
corpus or a claim of superiority over squarefree or primitive-polynomial
methods. The old phase producer correctly refuses nonmaximal models. The
published n=8 case provides the unchanged interface comparison. The native
model/witness-to-CNF transformations remain trusted, even when the CNF proofs
are independently replayed.
