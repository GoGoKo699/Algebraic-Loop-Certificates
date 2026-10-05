# Scientific research checkpoint

New readers can start with the [Manna–Pnueli learning path](../docs/LEARNING_PATH.md),
the [worked safety tutorial](../docs/TUTORIAL.md), and the
[reproduction guide](../docs/REPRODUCING.md). They connect the book's safety
framework to the exact construction, code and retained evidence below.
Historical checkpoint recommendations reflect their dates; the Gate 18 decision
and current work order govern the present scope.

This repository serves as a record of the work and a guide for the author’s self-directed learning. For discussion or potential collaboration, please contact Ruge Lin at [gogoko699@gmail.com](mailto:gogoko699@gmail.com).

See [Purpose and contact](../README.md#purpose-and-contact) in the README.
These experimental namespaces leave the production `alc/` API unchanged.

**Latest:** the [completed assessment](CONTRIBUTION_ASSESSMENT_18.md) retains a
reproducible integration case study, with exact priority unresolved and no
established standalone contribution, general solver advantage or benefit for
the complete orbit engine. The [54-trial comparison](BOUNDED_COMPARISON_GATE_17.md)
met its added-coverage criterion at width 8. All 180 completed CNF proofs replay
independently; native translations remain trusted.

The [claims and boundaries guide](../docs/RESEARCH.md) explains the comparator
roles, outcome-informed storage amendment and earlier decisions. The suspended
Gate 16 study remains separate; its observations were not pooled into the
completed study. No further experiment is scheduled.
[CURRENT.md](../work_orders/CURRENT.md) records the conditions for reopening
scientific work.

| Module | Scientific object | Main boundary |
|---|---|---|
| [Contribution and assurance assessment](CONTRIBUTION_ASSESSMENT_18.md) | Core argument, claim ledger, primary-source comparison and stopping decision | Completed integration study; exact priority unresolved and standalone contribution uncleared |
| [Amended completion study](completion_v2/README.md) | Full 54-trial source-bound witness comparison; width-8 added coverage | Outcome-informed storage repair; fixed hinted family and trusted native translations; no novelty or orbit-engine claim |
| [Completion study and cost audit](completion_v1/README.md) | Qualified native interface, suspended bounded comparison, and accounting of retained observations | Primary criterion unevaluated after a storage-guard execution issue; no completed comparison claim |
| [Invariant/history audit](invariant_history_v1/README.md) | Exact forced inverse-bit characterization and conservative-history projection | Established separator pattern; no standalone novelty or general size lower bound |
| [Odd-order witness integration](odd_order_witness_v1/README.md) | Seed-dependent period circuits preserve the weaker odd-order premise at the existing native interface | Established order extraction; factorization cost and trusted native translations remain explicit |
| [Hardware witness interface](proof_interface_v1/README.md) | Original circuits and history invariants accepted through Certifaiger with retained SAT proofs | Stronger maximal-period premise; native obligation and CNF translations remain trusted |
| [Raw AIGER safety](aiger_lfsr_v1/README.md) | Source-bound odd-order proof for the published reseeding wrapper | Restricted structural recognition; no general HDL frontend or novelty claim |
| [Native LFSR workload](../audits/native_lfsr_v1/README.md) | Eight existing native controls and four matched root certificates | Established native algebra already resolves maximality |
| [Complete field certificates](complete_orbits_v1/README.md) | Complete yes/no point-orbit certificates, including repeated factors | Algebraic witnesses may be expensive to find; originality unresolved |
| [Modular precision composition](modular_lifting_v1/README.md) | Checked prime-field layers for invertible affine maps over Z/NZ | A point guard is not an arbitrary safety predicate |
| [Direct positive ring proofs](direct_modular_hits_v1/README.md) | A smaller ordinary order certificate for positive answers | No negative conclusion follows from rejecting one of these proofs |
| [Native scalar comparison](scalar_comparison_v1/README.md) | Same scalar affine problems solved by native modular arithmetic | Not a native full matrix-orbit analyzer or a speedup claim |
| [Separating invariants](separating_invariants_v1/README.md) | Reusable checked predicates excluding targets | Passing one predicate is not a reachability proof |
| [Prime-field source recognition](compiled_orbits_v1/README.md) | One checked source, exact later full-state membership and least period | Queries do not recover first-hit times; source construction can remain expensive |
| [Prime-power source recognition](prime_power_compilation_v1/README.md) | Source compilation through one prime-field certificate and a cyclic-module test | Supporting reduction, not an established runtime advantage |
| [Query-scope audit](query_scope_v1/README.md) | Partial-observation, counting and preprocessing boundaries | Does not supply a general guard solver or clear novelty |
| [Character/Taylor comparison](../audits/character_taylor_v1/README.md) | Alternative recognition path with the same certificate and output contract | Representation/guarantee comparison, not native performance evidence |
| [Native invariant validation](../audits/invariant_validation_v1/README.md) | Frozen supplied-invariant obligations run with cvc5 | Failed application-benefit hypothesis; no matched timing or independent proof replay |

The [completion ledger](RESEARCH_COMPLETION.md) preserves the development record.
The earlier [scientific work order](SCIENTIFIC_WORK_ORDER.md) and
[closer-prior comparison](PRIOR_WORK_COMPARISON_02.md) are historical checkpoints;
Gates 14–18 supersede their next-step recommendations.

Run the standard-library research checks from the repository root:

```sh
python research/complete_orbits_v1/verify.py
python research/modular_lifting_v1/verify.py
python research/direct_modular_hits_v1/verify.py
```

The root regression tests also run these checks through `python verify.py`.
Optional comparisons use an already installed SymPy and never install it:

```sh
python research/complete_orbits_v1/verify.py --sympy
python research/scalar_comparison_v1/verify.py
python research/direct_modular_hits_v1/verify.py --sympy
```

The previous field and modular golden JSON reports are preserved exactly inside
`expected.json.gz`. The verifiers decompress and compare their bytes with fresh
reports in temporary storage. `RESULTS_SUMMARY.json` exposes readable counts and
the uncompressed hash. Timing observations are retained separately and are not
expected to match across runs or machines. No historical fixture has been
changed to conceal a mathematical discrepancy.

These modules do not supply a quantum backend, verified source-language
frontend, general guard solver or proof-assistant certification.
