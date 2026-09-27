# Scientific research checkpoint

Manuscript preparation is on hold. The production `alc/` API remains unchanged.
These are explicit experimental namespaces, not a silent expansion of its scope.

**Latest:** [existing workloads and raw-circuit safety](NATIVE_WORKLOAD_GATE_10.md). A native LFSR analyzer resolves the eight advertised controls; a scoped checker verifies an odd-order safety argument against 23 original reseeding circuits. The algebra has a simpler conventional comparator, so the next question concerns a useful checked integration.

**Current decision (27 September 2026):** the [constructive contribution assessment](CONTRIBUTION_ASSESSMENT_08.md) treats the engine as a certifying implementation of established algebra. A conventional character/Taylor route reaches the same recognition contract at comparable coarse bounds, and the formerly inaccessible direct paper has now been read. The [native-verifier gate](VERIFICATION_GATE_09.md) found no capability gap on its supplied-invariant corpus: cvc5 solved every valid case directly. Originality, useful advantage and scientific readiness remain unestablished.

The next task starts with an existing verification workload, a native baseline, and a falsifiable cost or assurance improvement. More algebraic formats or broader domains alone do not satisfy that gate. [CURRENT.md](../work_orders/CURRENT.md) records the active work order; earlier work orders and assessments retain their historical context.

| Module | Scientific object | Main boundary |
|---|---|---|
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
the two current assessments above supersede their next-step recommendations.
A proved construction is not automatically a new publishable contribution.

Run the standard-library research checks from the repository root:

```sh
python research/complete_orbits_v1/verify.py
python research/modular_lifting_v1/verify.py
python research/direct_modular_hits_v1/verify.py
```

The new root regression tests also run these checks through `python verify.py`.
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

No quantum backend, verified source-language frontend, general guard support,
proof-assistant certification, or native full matrix-orbit performance advantage
has been established. The scalar comparison, smaller direct positive proof,
constructive algebraic comparison and native invariant gate constrain the claims
without supplying a speedup result.
