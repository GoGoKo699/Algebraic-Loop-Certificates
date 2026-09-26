# Prior work and first contribution audit

**Assessment: implementation and research infrastructure are established here; publication-level novelty is not established.** This spinoff should earn a contribution through a useful certificate system, producer improvement, or analyzer integration. It should not rebrand known orbit algebra as a new quantum-inspired classical algorithm.

## Direct precedents

**Finite-field orbit reduction.** Imran and Ivanyos, *Efficient quantum algorithms for some instances of the semidirect discrete logarithm problem*, Designs, Codes and Cryptography (2024), DOI [10.1007/s10623-024-01416-8](https://doi.org/10.1007/s10623-024-01416-8), Section 3.3, explicitly reduce the finite-field point-orbit problem through its cyclic subspace to a matrix-power problem. The abstract quantum capability and that reduction are prior work. The bootstrap does not implement a quantum backend or a new classical discrete-logarithm solver.

**Loop acceleration.** Frohn and Fuhs, *A calculus for modular loop acceleration and non-termination proofs*, STTT (2022), DOI [10.1007/s10009-022-00670-2](https://doi.org/10.1007/s10009-022-00670-2), develops modular classical acceleration for integer programs. It establishes a research context and a competing methodology, not that its inputs have our finite-field semantics. Do not transfer results between rational arithmetic, finite fields, and integer overflow.

**Primality certificates.** Pratt, *Every Prime Has a Succinct Certificate*, SIAM Journal on Computing 4(3), 214-220 (1975), DOI [10.1137/0204018](https://doi.org/10.1137/0204018), establishes succinct proofs of primality. The Lucas/Pratt proof chain here is an existing tool. The historical paper's discussion of primality-testing status is not a statement about the present state of that problem.

**Certified linear algebra.** Dumas, Kaltofen, and Thome, *Interactive certificate for the verification of Wiedemann's Krylov sequence*, [arXiv:1507.01083](https://arxiv.org/abs/1507.01083), and Dumas, Kaltofen, Thome, and Villard, *Linear Time Interactive Certificates for the Minimal Polynomial and the Determinant of a Sparse Matrix*, [arXiv:1602.00810](https://arxiv.org/abs/1602.00810), demonstrate that separating an expensive producer from a cheaper checker is established in exact linear algebra. Their interaction, randomness, access, field, and verification-cost assumptions differ. The present deterministic reference checker is not claimed to improve their complexities.

**Elementary components.** Homogeneous lifting of affine maps, Cayley-Hamilton, separating linear functionals, order checks using prime divisors, binary powering, and the generalized Chinese remainder theorem are established mathematics. The repository contains explicit proofs for the particular certificate contract, not generic priority claims for those ingredients.

The two Springer primary papers and the primary abstracts for certificate methods were inspected during this bootstrap. The published predecessor's other references remain historical source context, not new full-paper audits. No native analyzer, computer-algebra benchmark, or complete novelty survey was executed.

## What the bootstrap adds as an implementation

A strict bound-instance JSON format; a checker isolated from search; recursively verified prime factors; separate positive, outside-span, and explicit-cycle evidence; meaningful unknown results; consumers for long-horizon queries and synchronized hit times; and reproducible counterexample-oriented tests. All of these are concrete deliverables. None by itself establishes a new research result.

The outside-span certificate and closed-cycle negative witness extend the executable coverage relative to the positive-only description in the unavailable local scout. They are newly written here using elementary linear algebra. This does not assert that the original scout code has been imported or rerun.

## The first research choice

Prioritize a **non-enumerative, proof-producing classical producer with a useful consumer**. It should exploit cyclic-subspace/minimal-polynomial structure, supplied factorization or order hints when legitimate, and classical discrete-logarithm methods. Compare against native exact-algebra tools; do not require the baseline to enumerate the whole orbit.

Keep discovery and verification costs separate, then report their sum for the actual consumer. Do not make a problem harder solely by selecting large awkward moduli. A supplied certificate can be easy to check even when its construction remains costly; that is a contract, not a speedup claim.

A parallel proof obligation is compact unreachability inside the cyclic span. The existing closed-orbit witness is complete when supplied but can be enormous. It is not a solution to that research question. A proposed short negative certificate must be proved sound and compared with prior nonmembership methods before advertising it as new.

Avoid broadening to arbitrary guards, singular maps, all machine words, or a full programming-language frontend until one scoped contribution is justified. Manuscript preparation is on hold and this classical spinoff has no selected journal.
