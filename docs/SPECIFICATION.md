# Mathematical specification and proof

## Exact problem

Let `p` be prime and `A` an invertible `d x d` matrix over `F_p`. Fix vectors `c`, `a`, and `b`. Define

$$
x_0=a,\qquad x_{t+1}=Ax_t+c,\qquad t\in\mathbb Z_{\geq0}.
$$

The target is equality of the **entire state** with `b`. All entries use canonical residues `0,...,p-1`. Prime fields are not arbitrary finite fields, and `F_(2^w)` is not integer arithmetic modulo `2^w`.

An invertible affine transformation permutes the finite state space, so the trajectory of `a` is a cycle with no transient tail. Its least period `r` is at most `p^d`. If `b` is reachable, its occurrences are exactly `t0+j*r` with `0 <= t0 < r` and integer `j >= 0`. The period of this **point** need not equal the matrix order. A linear zero initial state is fixed; an affine zero initial state need not be.

## What the positive certificate contains

The certificate supplies `t0`, `r`, a complete factorization of `r`, an inverse matrix for `A`, and primality witnesses for the field characteristic and the primes used in the factorization. It also records the fingerprint of the independently supplied problem.

The checker first proves the arithmetic domain and inverse witness. It then checks

$$
x_r=a,\qquad x_{r/q}\ne a\quad\text{for every distinct prime }q\mid r,\qquad x_{t_0}=b.
$$

**Soundness.** Let `s` be the true least return period. The first identity implies `s | r`. If `s < r`, choose a prime divisor `q` of `r/s`. Then `s | r/q`, contradicting the corresponding exclusion. Thus `s=r`. Invertibility and minimality imply that the `r` states within one period are distinct, so the verified offset gives every target occurrence, and no others.

This is ordinary order certification, not a claimed new theorem. The proof depends on **primality** of the supplied factors and on completeness of their product. It does not follow from a list of convenient divisors alone.

## A counterfeit certificate that superficial checks would accept

The Fibonacci example over `F_7` has point period 16. The claimed return 32 is also a return. If a checker trusts the purported factorization `32 = 4 * 8`, it checks nonreturns at `32/4=8` and `32/8=4`. Both pass. It would wrongly accept period 32 and omit every other real hit.

Our checker rejects the purported factors: 4 and 8 have no valid prime proofs. Even with the genuine factorization `32=2^5`, the period is rejected because the state already returns at 16. These are separate regression tests.

## Lucas-Pratt primality proofs

The certificate contains a sorted directed acyclic collection of records. The base case is 2. For a candidate `p>2`, a record supplies the **complete** factorization of `p-1` into previously proved primes and a witness `a` satisfying

$$
a^{p-1}\equiv1\pmod p,\qquad
\gcd\left(a^{(p-1)/q}-1,p\right)=1
\quad\text{for each distinct prime }q\mid p-1.
$$

These conditions force the residue class of `a` to have order `p-1` in the unit group modulo `p`, and hence force `p` to be prime. Recursing over smaller primes terminates at 2. This is an established primality-certificate method [Pratt 1975](https://doi.org/10.1137/0204018), not a probabilistic primality heuristic. The [Archive of Formal Proofs entry](https://isa-afp.org/entries/Pratt_Certificate.html) formalizes a Pratt proof system; **our Python implementation has not been formally verified by that project**.

Producing the factorizations and witnesses can be expensive. The reference producer uses bounded trial division; the checker only verifies them. The existence of short proofs is not an efficient discovery algorithm.

## Affine powering and costs

For the checker, introduce homogeneous coordinates:

$$
T=\begin{pmatrix}A&c\\0&1\end{pmatrix},\qquad
v=\begin{pmatrix}a\\1\end{pmatrix}.
$$

The first `d` coordinates of `T^t v` give `x_t`. Repeated squaring evaluates a supplied exponent in time polynomial in its bit length, matrix dimension, and field bit length. The checker makes one period check, one hit check, and one exclusion check per distinct period prime. It does not factor `r` or iterate through `r` states. Primality proof verification and matrix-inverse products are additionally charged.

This establishes polynomial verification in the explicit input and supplied proof size. It is not a wall-clock superiority claim over existing algebra systems, and it does not make discovery polynomial. The producer, proof checker, and downstream consumer have different costs.

## Trust boundaries

The caller supplies the trusted recurrence separately. The digest prevents accidental reuse against a different recurrence under the collision-resistance assumption for SHA-256; it is not a signature or a certificate that the recurrence models a real program. The proof's mathematical obligations are checked against that supplied recurrence.

No positive certificate means no conclusion. Invalid input, failed proof, unsupported domain, and resource exhaustion must never be interpreted as unreachability. The reference producer can exhaust a small orbit and report that it did not hit the target, but v1 provides no independently checkable general negative-certificate format.
