# Primary sources and their role

Inspected 27 September 2026. Source scope, executed evidence and our inference
are distinguished below; none establishes a new orbit algorithm.

## Executed native comparator: SmokeRand

Repository: <https://github.com/alvoskov/SmokeRand>, MIT licensed, by Alexey L.
Voskov and contributors. The unmodified checkout used here is commit
`20f3adab3121b4205a12f06746055551e6504648` (14 September 2026), identifying itself
as version 0.51. No upstream code or binary is copied into this repository.

| Inspected source | Git blob SHA-1 | Role |
|---|---|---|
| [docs/lfsr.md](https://github.com/alvoskov/SmokeRand/blob/20f3adab3121b4205a12f06746055551e6504648/docs/lfsr.md) | `b73f233c61cd699422a2fab4a7d5eb16b775b4ac` | Native contract and the advertised positive, negative and unsupported controls |
| [src/lfsr_period.c](https://github.com/alvoskov/SmokeRand/blob/20f3adab3121b4205a12f06746055551e6504648/src/lfsr_period.c) | `3642af92e9cfa64315c71a4ac9958d2cd1eea9de` | State probing, polynomial construction, order checks and verdicts |
| [src/lfsr_period_factors.c](https://github.com/alvoskov/SmokeRand/blob/20f3adab3121b4205a12f06746055551e6504648/src/lfsr_period_factors.c) | `939cbcc6f9c920b08c82f09f089378be718268df` | Fixed period-quotient exponent tables |
| [generators/shr3.c](https://github.com/alvoskov/SmokeRand/blob/20f3adab3121b4205a12f06746055551e6504648/generators/shr3.c) | `395f8ca872fb7a10e816a3d0640f197be22d77c8` | Published 32-bit XOR/shift recurrence, used unchanged by C harness |
| [generators/xorrot32.c](https://github.com/alvoskov/SmokeRand/blob/20f3adab3121b4205a12f06746055551e6504648/generators/xorrot32.c) | `03a44f8f836f696abca20c4051c3ac89747f3147` | Default and both intentionally nonmaximal upstream variants |
| [Makefile.gnu](https://github.com/alvoskov/SmokeRand/blob/20f3adab3121b4205a12f06746055551e6504648/Makefile.gnu) | `5e3ec91811c4307d97adf82236bc4cc33fb2a069` | Unchanged native build |

The API consumes a compiled generator with directly accessible bit-vector state.
It reconstructs transition data and checks maximal order. Since version 0.50,
the order stage uses characteristic/jump polynomials; the comparator is therefore
not forced to use dense matrix powering or enumerate the claimed period.
Our frozen cases come from its testing instructions, not a new synthetic family.

The source labels its state-layout and linearity checks empirical. In particular,
agreement with decimated basis probes at exponent 65,537 is not a proof of
linearity on every possible state. The subsequent algebra presumes the LFSR
model. Its fixed quotient tables are additional trusted inputs of this executed
implementation. We did not audit every table or formalize the C analyzer.

**Inference from this run:** all advertised categories in the fixed corpus are
resolved; this task does not establish a native capability gap needing a complete
orbit compiler. It says nothing universal about all other orbit consumers.

## Hardware motivation inspected, not executed: OpenTitan

[OpenTitan's primary documentation](https://opentitan.org/book/hw/ip/prim/doc/prim_lfsr.html)
describes the `prim_lfsr` hardware primitive. The inspected source revision is
`69d82086985aee7cb338ced7a2df7dc93dd59679` (25 September 2026):

| Source | Git blob SHA-1 |
|---|---|
| [hw/ip/prim/doc/prim_lfsr.md](https://github.com/lowRISC/opentitan/blob/69d82086985aee7cb338ced7a2df7dc93dd59679/hw/ip/prim/doc/prim_lfsr.md) | `0531fdde5b8f6b7009005084803a7392dbe2c9d9` |
| [hw/ip/prim/rtl/prim_lfsr.sv](https://github.com/lowRISC/opentitan/blob/69d82086985aee7cb338ced7a2df7dc93dd59679/hw/ip/prim/rtl/prim_lfsr.sv) | `ba150064736c7c5cc36d2f79ee7284b1a62bdcfa` |

The docs supply two LFSR forms and coefficient widths 3–168, with a maximal-period
claim. They separately report formally checked transition implementation and
full simulation sweeps through width 34. This is evidence of a real verification
requirement, not evidence that algebraic checking is unavailable above width 34.

The RTL has external seeding, entropy injection and lockup recovery. Its maximum
length assertions are disabled after the relevant perturbation flag, while an
enable controls when transitions occur. Consequently a free-running recurrence
model is only a restricted mode of this hardware. No source extraction, HDL
simulator or hardware proof was run in this audit; these files are motivation,
not additional successful test instances.

## Established mathematical and downstream context

- George Marsaglia, [Xorshift RNGs](https://www.jstatsoft.org/article/view/v008i14),
  *Journal of Statistical Software* 8(14), 2003,
  [DOI 10.18637/jss.v008.i14](https://doi.org/10.18637/jss.v008.i14).
  The publisher page establishes the original XOR/shift generator family and
  stated periods. This audit does not re-audit all published parameter triples.
- Sebastiano Vigna and David Blackman,
  [generator implementations and jump functions](https://prng.di.unimi.it/).
  The authors explain the role of jumps in separating parallel streams, and
  distinguish period from statistical quality. No independent-seed distance
  or nonoverlap experiment was run here.
- SageMath's [generic group algorithms](https://doc.sagemath.org/html/en/reference/groups/sage/groups/generic.html)
  and [matrix base class](https://doc.sagemath.org/html/en/reference/matrices/sage/matrix/matrix0.html)
  document order/discrete-log capabilities. Sage and GAP were not installed in
  this execution environment. SmokeRand was selected because it directly accepts
  the existing workload and could be executed; lack of Sage/GAP execution is not
  evidence of a missing mathematical capability.

These sources support avoiding a simulation-only baseline. The native program,
its table assumptions and the exact root certificate checker remain different
trust configurations. Their existence alone establishes neither a novel proof
system nor an assurance advantage for this project.
