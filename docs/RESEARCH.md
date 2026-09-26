# Research assessment and first contribution audit

26 September 2026. The project has an executable certificate workflow. It does **not** yet have an established new research contribution, a fast general classical discrete-log solver, or an application benchmark showing an advantage over existing tools. Manuscript work is on hold.

## Current separation

The producer performs bounded discovery; the checker verifies supplied witnesses; the consumer uses the verified arithmetic progression. The first implementation hardens this separation by including primality proofs and binding the claim to a separately supplied problem. A counterfeit composite-factor example is retained as a regression test. This is sound engineering around established mathematics, not a priority claim.

The implementation is narrower than the finite-field mathematical discussion that motivated it: v1 supports prime fields only. Unsupported extension fields, singular dynamics, arbitrary guards and general unreachability proofs are not silently approximated.

## Source-by-source baseline

| Primary source | Established result or relevance | What this repository does not claim |
|---|---|---|
| Imran and Ivanyos, *Efficient quantum algorithms for some instances of the semidirect discrete logarithm problem*, Designs, Codes and Cryptography 92 (2024), [Section 3.3](https://doi.org/10.1007/s10623-024-01416-8) | Finite-field orbit membership via cyclic-subspace/matrix-power methods and established quantum algorithms | That the orbit reduction or a polynomial quantum producer is new; no quantum backend was run |
| Frohn and Fuhs, *A calculus for modular loop acceleration and non-termination proofs*, STTT (2022), [article](https://doi.org/10.1007/s10009-022-00670-2) | Loop acceleration as reusable program-analysis information; modular composition of classical techniques | That a full-state prime-field target certifies general integer-program safety or automatically beats their methods; no native comparison was run |
| Pratt, *Every Prime Has a Succinct Certificate*, SIAM J. Comput. 4 (1975), [article](https://doi.org/10.1137/0204018) | Short checkable primality certificates, using factorizations and multiplicative-order witnesses | That supplying a factor list alone establishes primality, or that making the proof is always cheap |
| [Pratt's Primality Certificates, Archive of Formal Proofs](https://isa-afp.org/entries/Pratt_Certificate.html) | Existing machine-checked formalization of a related proof system | That our Python checker is covered by that formalization |

The arithmetic-progression consumer and Chinese remainder combination are elementary. The initial source review establishes direct predecessors; it is not an exhaustive novelty audit.

## Useful first milestone

A caller can now supply a trusted recurrence and an untrusted candidate certificate, verify the complete positive hit set, and answer later horizon/schedule queries without rerunning discovery. The examples test this contract rather than assert a naturally hard application. The original experimental counts have not been imported or repeated: the new finite audit has its own specification and evidence.

The producer remains deliberately elementary. A better producer must be compared with relevant finite-field/matrix-order routines and source-level simplification, not only with this enumerator. A dramatic execution horizon is not enough if a classical analyzer already derives the same summary cheaply.

## Next substantive research question

Select one certificate or analysis capability that existing approaches do not already supply as cheaply or as generally. Candidate directions include a carefully scoped negative certificate or a compositional consumer, but neither is an established result or preapproved performance claim. Compare the actual prior algorithms and identify a consumer before broadening the supported semantics.

Before claiming practical benefit, measure the entire chain: extraction of the recurrence, production of the summary, proof size, verification, and downstream analysis. Both sides may exploit invariants, decompositions, smooth orders, cached algebra, and alternative formulations. Do not change the intended task to make those methods fail.

The separate quantum project retains its own goals. This classical repository need not include a quantum section to justify a useful result, and its venue will be chosen only after the contribution is identified.
