# Deeper predecessor audit and a native scalar comparison

26 September 2026. Scientific research, not manuscript drafting. The experimental
proof systems remain separate from the primary positive-only API. Their
soundness/completeness arguments do not automatically establish novelty.

## What the closer sources already do

**Wei, Xu and Zou, Dynamics of Linear Systems over Finite Commutative Rings.**
Their Lemma2.1 lifts a cycle through a module extension by iterating its residual
displacement; the proof uses a geometric sum along the return map. Theorem2.1
and the subsequent algorithm reduce cycle information through prime-field
quotients and use factorization/order information to recover periods. Thus
reducing finite-ring dynamics to field layers is not a new principle of this
project. Our point-target refinement reconstructs a derived affine problem and
carries static evidence for complete positive/negative target schedules; whether
that packaging yields an independently new theorem remains to be established.
Their global period bound is not the invalid claim that every individual point
period grows only by one or p per precision layer.

Source: https://arxiv.org/pdf/1709.08579 . Parsed text of Lemma2.1, Theorem2.1,
Corollary2.1 and the algorithm inspected. Screenshot attempts failed; no table
measurements or claims to reproduce the implementation are made.

**Menezes and Wu, The Discrete Logarithm Problem in GL(n,q), 1997.** A successfully
retrieved image of printed page27 explicitly explains why constructing a common
splitting field can cause large extension degree, and instead treats the
separate small extension fields. Avoiding that common splitting field must not
be advertised as our innovation. The full scan remains incompletely accessible;
one successfully inspected page is not a full audit of its algorithm or proof.

Source: https://combinatorialpress.com/ars-articles/volume-047-ars-articles/the-discrete-logarithm-problem-in-gln-q/
PDF: https://combinatorialpress.com/article/ars/Volume%20047/volume_47_paper-3.pdf

**Kantic, Qureshi, Panario and Legl, On the Dynamics of Linear Finite Dynamical
Systems Over Galois Rings, 2026 preprint.** The paper studies cycle lengths and
transients via cyclic modules, factorization and lifting. Its algorithmic cost
assumptions include available factorization information and parameters for the
irreducible decomposition. That is a serious baseline, not evidence that the
complete bit-cost of every matrix logarithm is constant. A fixed-target,
proof-producing comparison must state the differences in objective and access
rather than claim the common algebra is absent from this work.

Source: https://arxiv.org/html/2604.01548v1 . Full HTML method/algorithm sections
inspected; no native code reproduced. Preprint status is retained.

**Viglietta and Kachi, Efficient Lifting of Discrete Logarithms Modulo Prime
Powers, 2025 preprint.** Their scalar-unit lifting task is distinct from a general
affine point orbit, but it prevents any generic priority claim for efficient
scalar precision lifting. It is not necessary to rerun a unit logarithm from
scratch at every precision in a strong classical implementation.

Source: https://arxiv.org/html/2505.07434v1 . Algorithm and cost discussion
inspected. The implementation below is SymPy, not an execution of their code.

## A comparator actually executed

The new [scalar audit](scalar_comparison_v1/README.md) reduces a one-dimensional
affine recurrence to a modular logarithm by changing modulus and cancelling a
gcd. It does not incorrectly invert a nonunit A-1. Native SymPy routines then
recover the complete schedule, or an empty answer.

All 13,602 scalar instances modulo2 through10 agree with independently stepped
orbits. Another 1,122 paired checks compare those answers with our experimental
certificate producer and independent verifier. The large displayed instances
receive the same canonical input and no supplied order/factorization hints.
The native solver wins the recorded scalar timings, including the 64-bit affine
example. The certificate path has a different additional output: an independently
replayable proof. We do not claim that its higher cost establishes a disadvantage
for every task that requires such a proof; we also do not hide the cost when
comparing ordinary answers. Details and full timing samples are preserved.

## Updated claim boundary

The following are established tools, not current novelty claims: finite-field
matrix-power reductions, separate-field processing, cyclic-module decomposition,
prime-power lifting, order tests, primality certificates, and CRT compatibility.
The transparent integration may be valuable, but value needs an argument beyond
combining their names. Neither an exhaustive small test suite nor a long binary-
encoded time horizon supplies that argument.

The candidate original object is now narrower: a complete, static, polynomial-
size algebraic certificate contract, composed across precision, for exact
point-guard outcomes. The necessary next comparison is with a certifying
version of prior algorithms, not only their original informal descriptions.
We must determine whether adding the same witnesses to those algorithms already
gives the claimed guarantee with comparable resources. If it does, the result
must be positioned as a software/certification implementation or extended by a
new capability, rather than claimed as a new mathematical algorithm.

No general negative result about publication potential follows. No publication-
readiness verdict is made. Missing full-text inspection, native matrix-orbit
comparison, and a justified incremental contribution remain explicit scientific
work. The manuscript remains on hold and the repository contains no venue goal.


## Positive-certificate simplification

[Direct modular hit certificates](direct_modular_hits_v1/README.md) remove the unnecessary full precision chain for positive answers. The standard point-order witness works over any explicit residue ring with a checked inverse and needs no factorization of the modulus. A matched positive-proof comparison reduces the recorded 64-bit witness from 21,744 to 292 bytes. Native solving, proof assembly, and checking are separately costed. This repairs our implementation using established mathematics; it is not claimed to close the originality requirement. Complete negative evidence remains the role of the richer algebraic construction.
