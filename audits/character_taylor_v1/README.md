# Full field-source comparison using character relations and Taylor blocks

**The complete field-source guarantee has an equally compact conventional
character/Jordan-Taylor implementation.** This is an audit of the remaining
candidate theorem, not a new domain or public format.

[THEORY.md](THEORY.md) proves that the alternative recognizes the entire initial
orbit of any supported invertible affine prime-field source, retaining repeated
factors. It rechecks the same `alc.compiled-orbit.v1` evidence and returns the
same membership and least-period answers. No first hitting time is supplied.
The scalar/field coordinates, source relations and Taylor coefficients are
polynomial-size. Source discovery may still require difficult algebra.

The query reads characteristic-primary digits from a normalized binomial row,
then checks every coefficient in every local block. This replaces the original
cyclic-unipotent decoder, not just a wrapper around its answer. The comparator
also independently computes cyclic coordinates and checks source obligations.
A fresh-process test disables the old coordinate and unipotent routines BEFORE
compilation and confirms that no original compiler or producer is imported.
Elementary polynomial arithmetic, parsing and primality verification are shared.
This is useful diversity, not full formal or arithmetic independence.

## Why this changes the contribution assessment

The earlier reduction-layer comparison left the main field compiler as a shared
black box. This one does not. It gives a complete source-certificate/query path
at the same coarse polynomial bounds. Standard character relations handle the
field phases; Taylor/Jordan and binomial identities handle repeated factors.
The proof bytes are identical, so the baseline receives no stronger hints.

[SOURCES.md](SOURCES.md) records a readable author-hosted copy of Menezes-Wu and
the completed inspection of its mathematical sections. Character, compact-circuit
and binomial predecessors are treated with their actual assumptions. The adapter
is written for this audit; it is not falsely attributed to a native published
solver, and no timing advantage has been measured.

The [updated assessment](../../research/CONTRIBUTION_ASSESSMENT_08.md) classifies
the coarse compilation theorem as a certifying reformulation on current evidence.
It does not assert that the exact software interface has been published before.
An original verification or useful analysis contribution still needs to be earned.
Manuscript writing remains on hold.

## Run

Python3.10+ and the standard library, from a checkout:

```sh
python audits/character_taylor_v1/verify.py
python -O audits/character_taylor_v1/verify.py
```

No network or package installation. The default root regression suite includes
the new audit. Its manifest pins dependencies and compares a fresh temporary
report with the recorded exact bytes; it never overwrites a fixture to hide a
failure. Existing source, historical results, license and APIs remain unchanged.

## Recorded scope

The new audit rechecks661 source certificates, including180 sources with repeated
factors and172 with extension-field factors. It compares7,209 target queries
against both the original compiler and independently stepped orbits.660 sources
receive every state in their finite domain; the remaining one receives330
orbit/seeded controls. There are240 additional independent large-characteristic
closed-form comparisons,320 Taylor coefficient/product checks and13,440
binomial controls. Eighteen altered source proofs and four malformed query
states are rejected by both compilers.

The two retained rejection examples matter: a non-prime-field coefficient is not
a valid base-p digit, and matching only the p-power coefficient positions does
not establish the full binomial pattern. The source for `1+Z^3` modulo Z^5 in
characteristic2 passes the sparse digit inspection but is correctly excluded
by full coefficient replay.

These counts overlap previous mathematical families and are not distinct
applications. The audit also records a small index-conversion issue in the
inspected author copy and checks the corrected conversion on eighteen Jordan
powers. That is not a claimed new reduction or the intended publication result.

Basic use in internal audits:

```python
from audits.character_taylor_v1.baseline import compile_baseline
compiled = compile_baseline(source_document, certificate_document)
answer = compiled.query(target_vector)
```

The source and certificate must be separately supplied and checked. Returned
Python objects are not unforgeable security capabilities. Queries are exact
complete-state membership, not arbitrary projected guards or timing recovery.
