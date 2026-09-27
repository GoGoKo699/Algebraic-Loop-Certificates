# Scientific research checkpoint

Manuscript preparation is on hold. The production `alc/` API remains unchanged.
These are explicit experimental namespaces, not a silent expansion of its scope.

**Latest:** [invariant/history contribution decision](INVARIANT_HISTORY_GATE_13.md). The exact forced predicate specializes an established inverse-bit separator construction. The proof and native integration remain valid, but this standalone novelty route is closed. A compact quantified representation is already available; deterministic evaluation, formula size and native proof checking must be kept distinct.

**Current decision (27 September 2026):** the [constructive contribution assessment](CONTRIBUTION_ASSESSMENT_08.md) treats the engine as a certifying implementation of established algebra. A conventional character/Taylor route reaches the same recognition contract at comparable coarse bounds, and the formerly inaccessible direct paper has now been read. The [native-verifier gate](VERIFICATION_GATE_09.md) found no capability gap on its supplied-invariant corpus: cvc5 solved every valid case directly. Originality, useful advantage and scientific readiness remain unestablished.

The [existing-workload pass](NATIVE_WORKLOAD_GATE_10.md) and subsequent interface experiments now supply a concrete verification consumer and native baseline. The premise gap and conceptual predecessor comparison are resolved. Further work requires an independently motivated consumer with a falsifiable improvement over the strongest source-aware method. More algebraic formats or broader domains alone do not satisfy that gate. [CURRENT.md](../work_orders/CURRENT.md) records the active work order; earlier work orders and assessments retain their historical context.

| Module | Scientific object | Main boundary |
|---|---|---|
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
