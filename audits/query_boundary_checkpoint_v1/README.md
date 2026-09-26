# Preserved independent query-boundary checkpoint

The supplied `Algebraic_Loop_Query_Boundaries_Checkpoint.zip` contained eleven
unpublished additions. Meanwhile `main` acquired a different query-scope audit
at commit `0ccc0f8aba93944ba488ed05111e50772f215574`. Both are retained: this
archive preserves the supplied additions without replacing the live
`research/query_scope_v1/` implementation or creating a competing public API.

`additions.zip` is a deterministic archive of the eleven ORIGINAL FILE BYTES,
not the entire original delivery repackaged under its old name. `MANIFEST.json`
records the original complete checkpoint hash, the original patch hash, the
new archive hash, and every preserved member hash. Source-dependency hashes
remain those from the supplied audit's own manifest. This is not a recovery
of the much older missing loop-scout ZIP.

The pending audit's distinctive evidence includes the format-specific extraction
of a source logarithm,220 reindexed/oriented certificate controls,57,378 diagonal
queries,1,021 source-fixed projection formula controls, and42 optional native
source reconstructions. Its broad projection-hardness results overlap the live
audit; counts must not be added as disjoint discoveries. The archive's historical
statements about unpushed files describe its creation, not current repository
availability. Its mathematical source/claim qualifications remain intact.

## Reproduce without changing any tracked file

```sh
python audits/query_boundary_checkpoint_v1/verify.py
python audits/query_boundary_checkpoint_v1/verify.py --sympy
```

Python3.10+ and the standard library suffice for the default command. The optional
native check requires an already installed SymPy. The runner validates archive
membership, member hashes and current dependency hashes, expands the additions
into temporary storage, and runs their original verifier. It does not execute
an arbitrary user-selected archive. The added root regression test invokes the
default command; no network, dependency installation or fixture rewrite occurs.

To read the preserved derivations/code, inspect the paths
`research/query_boundary_audit_v1/THEORY.md`, `SOURCES.md`, `boundaries.py` and
`check.py` inside the archive. The live complementary record is
[query_scope_v1](../../research/query_scope_v1/README.md).
Manuscript writing remains on hold; neither audit clears the main result's
originality or proves a practical performance advantage.
