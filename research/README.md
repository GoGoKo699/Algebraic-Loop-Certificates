# Scientific research checkpoint

Manuscript preparation is on hold. The production `alc/` API remains unchanged.
These are explicit experimental namespaces, not a silent expansion of its scope.

| Module | Scientific object | Main boundary |
|---|---|---|
| [Complete field certificates](complete_orbits_v1/README.md) | Complete yes/no point-orbit certificates, including repeated factors | Algebraic witnesses may be expensive to find; originality unresolved |
| [Modular precision composition](modular_lifting_v1/README.md) | Checked prime-field layers for invertible affine maps over Z/NZ | A point guard is not an arbitrary safety predicate |
| [Direct positive ring proofs](direct_modular_hits_v1/README.md) | A smaller ordinary order certificate for positive answers | No negative conclusion follows from rejecting one of these proofs |
| [Native scalar comparison](scalar_comparison_v1/README.md) | Same scalar affine problems solved by native modular arithmetic | Not a native full matrix-orbit analyzer or a speedup claim |

The [completion ledger](RESEARCH_COMPLETION.md), [scientific work order](SCIENTIFIC_WORK_ORDER.md),
and [closer-prior comparison](PRIOR_WORK_COMPARISON_02.md) describe what remains.
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
has been established. The latest scalar comparison and smaller direct positive
proof strengthen the classical baseline instead of manufacturing a speedup.
