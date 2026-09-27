# Research assessment

Updated 27 September 2026. The project has an executable certificate workflow. It does **not** yet have an established new research contribution, a fast general classical discrete-log solver, or an application benchmark showing an advantage over existing tools. Manuscript work is on hold.

## Current decision

The [constructive contribution assessment](../research/CONTRIBUTION_ASSESSMENT_08.md) supersedes the initial open comparison: a conventional character/Taylor route supplies the same complete source-recognition contract at comparable coarse polynomial bounds. The direct matrix-logarithm paper is now accessible and its relevant mathematics has been read. The engine is treated as a certifying implementation of established structure; the representation/guarantee comparison is not a native performance benchmark or an exhaustive historical priority finding.

The [supplied-invariant gate](../research/VERIFICATION_GATE_09.md) then tested a concrete verification task. Native cvc5 solved all ten valid invariants directly, so that corpus supplies no capability gap requiring the orbit engine. Finite-field proof production also has direct predecessors. No matched timing or proof-assistant replay was performed. The next task must earn a useful cost or assurance improvement for an independently specified consumer, before more engine development.

The following baseline records the original production implementation. Experimental complete certificates, source recognizers, query boundaries and independent recognition audits are indexed in [research/README.md](../research/README.md); they do not change that production API.

The [next existing-workload pass](../research/NATIVE_WORKLOAD_GATE_10.md) executes a native LFSR analyzer and checks a smaller odd-order argument against 23 published AIGER safety circuits. This gives a concrete source-to-safety integration candidate; source-aware squarefree-polynomial reasoning reaches the same algebraic decision, so originality remains unresolved.

The [proof-interface gate](../research/PROOF_INTERFACE_GATE_11.md) now delivers history witnesses through Certifaiger's existing AIGER interface. Three history witnesses and two exported ABC invariants passed all native obligations with SAT-proof replay. The phase-parity reduction clarifies why adding history matters, without claiming a size lower bound. This establishes a measured integration, while its stronger maximal-period premise and the equally available conventional algebraic route still limit the contribution claim.

The subsequent [odd-order gate](../research/ODD_ORDER_WITNESS_GATE_12.md) removes that maximal-period premise. Exact seed periods are compiled from a factored odd annihilating exponent, so mixed seed periods and nonminimal exponents work through the same native interface. All three positive witnesses passed; both wrong selectors failed induction; 37 completed proofs independently replayed. Factorization remains construction work and native source-to-CNF translation remains trusted. The conventional route can emit the same witness. The next question is the precise original-state evaluation/history distinction and its predecessors, rather than another algebraic format.

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

Identify an existing verification workload or documented requirement, specify its natural input/output contract, and execute the strongest relevant baseline. State in advance what measurable cost or assurance improvement would count as success and what result would end the attempt. Complete negative certificates and compositional consumers already exist in the research modules; adding them again or changing the algebraic format does not resolve the contribution gap.

Before claiming practical benefit, measure the entire chain: extraction of the recurrence, production of the summary, proof size, verification, and downstream analysis. Both sides may exploit invariants, decompositions, smooth orders, cached algebra, and alternative formulations. Do not change the intended task to make those methods fail.

The separate quantum project retains its own goals. This classical repository need not include a quantum section to justify a useful result.
