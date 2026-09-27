# Native verification baseline and existing proof production

Inspected 27 September 2026. This dossier supports the consumer choice and the
limits of its interpretation; it is not drafted manuscript prose.

## S1. A finite-field solver already addresses the relevant semantics

The official cvc5 finite-field theory reference describes prime-field sorts,
modular addition/multiplication, QF_FF syntax and both its default solver and
an alternative split solver. The gate uses the default solver and actual prime-
field semantics, not a bitvector/integer approximation. The theory and example
sections were inspected. No unpublished solver property is assumed.

https://cvc5.github.io/docs/latest/theories/finite_field.html

The native release was checked through the official GitHub repository: version
1.4.1, released 25 September 2026; Linux x86_64 static GPL asset includes CoCoA.
The workflow checks the downloaded asset's exact SHA256 before executing it.
This is a declared benchmark dependency, not a redistributed binary or a claim
that our MIT source includes the solver's GPL dependencies.

https://github.com/cvc5/cvc5/releases/tag/cvc5-1.4.1
https://github.com/cvc5/cvc5/releases/download/cvc5-1.4.1/cvc5-Linux-x86_64-static-gpl.zip

The executed binary, version/configuration, source commit, CI run and artifact
are identified in native_observations.json. The original solver report and
41-file artifact remain linked from the native job. The selected local record
is a transparent extraction from that job, not an original artifact download.

## S2. Independent checking of finite-field SMT proofs is not a new gap by default

Pedro Saccomani, Abdalrhman Mohamed, Elizaveta Pertseva, Daniela Kaufmann,
Cesare Tinelli, Clark Barrett and Haniel Barbosa, Proof Production for
Satisfiability Modulo Finite Fields with Proof Checking in Pacheck and Lean,
FMCAD 2026, pp. 113-123. DOI 10.34727/2026/isbn.978-3-85448-093-8_17.

https://repositum.tuwien.at/handle/20.500.12708/230471
https://fmcad.forsyte.at/FMCAD26/program/

The primary university record's abstract and metadata and official conference
program were inspected. The abstract describes cvc5 proof production, a PAC
extension and enhanced Pacheck checker, and a Lean formalization with Lean-SMT
integration. Its benchmarks concern zero-knowledge-proof compilers. We did not
run its artifact, audit all proofs, or import its reported performance numbers.
The native build in this gate is not claimed to execute that paper's complete
proof-checking pipeline merely because it runs finite-field SMT.

This source is enough to reject a blanket claim that finite-field SMT lacks
proof production or independent proof checking. A proposed assurance contribution
would need to compare the actual proof contracts and trusted boundaries against
such work, not simply add the words 'certificate' or 'Lean' to this repository.

## S3. The preservation argument is ordinary algebra

The protocol proves a sufficient decomposition using checked linear observation
identities, multiplication congruence at every binary-power node, and a final
common-scaling identity. It needs no field-order or full orbit construction.
These are elementary field identities; no new calculus is claimed. The native
batched decomposition is a particular test encoding, not a claim to implement
all optimizations of existing algebraic proof systems.

## Claim assessment

| Candidate statement | Evidence and boundary |
|---|---|
| A real universal preservation obligation was submitted to a native solver | Forty QF_FF formulas, checked official binary, recorded job inputs/verdicts |
| The full orbit compiler is needed for these high-power invariants | Not supported: all ten valid direct queries were decided |
| Decomposition is universally inferior | Not supported: only one fixed batched encoding; it solves a broken case the direct route leaves unknown |
| There is a measured superiority over cvc5 | Not established; no matched certificate timing or broad workload |
| We obtained independently checked native proofs | Not performed; the experiment records solver verdicts only |
| Adding proof export is a first finite-field assurance contribution | Not supported given S2 |
| This is an industrial application evaluation | False: the corpus is explicit algebraic controls with easy construction |

These findings retire a proposed capability-gap explanation, not the entire
research project. They should guide the next task before another mechanism is
implemented. Keep the protocol, all unknown outcomes and source-reading limits.
