# Complete algebraic decision certificates: specification and proofs

Research derivation, 26 September 2026. This is not manuscript text. The primary
`alc.certificate.v1` format is unchanged. This research format is
`alc.algebraic-decision.v1`. A proof below is an ordinary mathematical argument,
not a claim that the Python implementation is formally verified.

## T1. Main statement

Let p be prime, A an explicitly represented invertible d-by-d matrix over F_p,
c a translation vector, and a,b two states. For the deterministic recurrence
x_(t+1)=A x_t+c with x_0=a and nonnegative integer t, there is a finite
certificate, of size polynomial in d and log p, from which a deterministic
polynomial-time checker derives either:

* the empty hit set; or
* the complete hit set {t0+jr:j>=0}, with 0<=t0<r and r the least point period.

The checker uses exact arithmetic, verified polynomial factors, checked
multiplicative orders and discrete-logarithm WITNESSES. It does not search for
a discrete logarithm, factor a supplied polynomial/integer, enumerate the orbit,
or trust a producer's answer. Existence of these short certificates does NOT
establish a polynomial-time classical producer. Factoring and logarithms may
remain expensive. Default implementation limits can reject large valid inputs
as resource-limited; the theorem concerns the parameterized algorithm.

The construction is a certifying reformulation of established cyclic-module,
finite-field matrix-logarithm and order arguments, not a claim to invent those
algorithms or the classification of matrix orbits. Whether the particular
complete certificate system is a new publishable contribution remains open;
see LITERATURE.md and RESEARCH_STATUS.md.

## T2. Cyclic module instead of the whole state space

Lift the affine transformation to

    T = [[A,c],[0,1]],   v=(a,1),   w=(b,1),   D=d+1.

T is invertible and v is nonzero. Form v,Tv,... until the first linear
dependence, at k<=D. Exact elimination gives the unique monic polynomial mu of
degree k with mu(T)v=0. Its constant coefficient is nonzero: otherwise division
by X and invertibility of T would give a smaller annihilator.

The map

    F_p[X]/(mu) -> span(v,Tv,...),   h -> h(T)v

is a vector-space isomorphism. Surjectivity follows from the Krylov basis;
injectivity follows from minimality of mu. The checker computes this basis,
mu and the coordinates of w itself. The witness does not supply unchecked
minimality or a black-box eigenbasis.

If w is outside the span, it cannot occur at any time. This is a complete,
polynomially checkable obstruction in that case. Otherwise write w=b(X)(T)v
with deg b<k, and let x denote X modulo mu. The original question becomes

    x^t = b in R=F_p[X]/(mu).

The least order of x equals the point period of a; using a full-matrix order
instead would generally be unnecessarily strong.

## T3. Check the primary factorization

The producer supplies distinct monic irreducibles f_i, multiplicities e_i>0,
and enough primality proofs for the base field and claimed orders. The checker
checks the identity

    mu = product_i f_i^(e_i)

with no extra factor or missing multiplicity. Degree limits prevent oversized
irrelevant expansions. Irreducibility is checked by Frobenius identities and
gcds, rather than by running a factor search. One simple deterministic test for
a monic degree-h factor is

    X^(p^h)=X mod f,
    gcd(X^(p^j)-X,f)=1 for 1<=j<=floor(h/2).

An irreducible factor passes. Conversely, a reducible degree-h polynomial has
an irreducible divisor of degree at most h/2, counting multiplicity in the
factorization; such a divisor makes one gcd nontrivial. The final Frobenius equality also excludes repeated
irreducible factors. The test is polynomial in h and log p. Using all these
degrees is deliberately elementary; more efficient Rabin variants are prior art.

Each F_i=F_p[X]/(f_i) is now a verified finite field. The total of its extension
degrees is at most k. No common splitting field, whose degree could be much
larger, is constructed. These are INTERNAL representations derived from a
prime-field input; the production input format has not gained extension-field
semantics.

## T4. Exact order witnesses and local obstructions

Write alpha_i=X mod f_i and beta_i=b mod f_i. The producer supplies m_i and a
complete proved-prime factorization of m_i. The checker verifies

    alpha_i^(m_i)=1,
    alpha_i^(m_i/q)!=1 for every distinct prime q dividing m_i.

These equations prove the exact order: any proper divisor of m_i misses a
prime factor and would imply one of the excluded equalities. It additionally
checks 1<=m_i<=p^(deg f_i)-1. Prime proofs are inherited from the production
Lucas-Pratt checker, with complete factor products checked independently.

There are two local possibilities.

1. beta_i=0, or beta_i^(m_i)!=1. Then beta_i is not in <alpha_i>, so no global
   orbit hit exists. This negative conclusion follows already from the power
   identity; it does not require solving a discrete logarithm.
2. beta_i is nonzero and beta_i^(m_i)=1. The multiplicative group of F_i is
   cyclic. It has exactly one subgroup of size m_i, namely <alpha_i>. Thus a
   unique t_i in [0,m_i) exists with alpha_i^(t_i)=beta_i. The producer supplies
   t_i and the checker validates the power identity.

In case 2, EVERY global solution must satisfy t=t_i mod m_i, because the order
is exact. Merely checking alpha_i^(m_i)=1, or trusting composite 'prime factors',
would be insufficient and is explicitly disallowed.

## T5. Combine necessary congruences

The generalized Chinese remainder theorem either detects inconsistency or
returns the single residue class

    t = t_bar mod m,   m=lcm_i(m_i),   0<=t_bar<m.

Consistency requires each pair of residues to agree modulo the gcd of their
moduli; the iterative CRT in the code is equivalent. If it fails, the target
is unreachable even though every field component separately has a logarithm.
This covers a genuine gap in a check that considers eigenvalues independently.
Since every m_i divides p^(deg f_i)-1, m is coprime to p.

If the congruences are consistent, define in R

    u=x^m,    C=b*x^(-t_bar).

Then a hit is equivalent to u^z=C for some integer z, with
 t=t_bar+m z. Both u and C are congruent to 1 modulo every irreducible factor.
In particular N=u-1 is nilpotent. If E=max_i(e_i), then N^E=0, since each f_i
occurs at least once in N and the factors are coprime. The implementation uses
the looser bound k and checks N^k=0 directly before proceeding.

This step is why square-free analysis alone is not complete: two elements can
have identical residues in every field and still differ modulo repeated
factors. The remaining discrepancy must not be discarded.

## T6. A cyclic unipotent subgroup can be checked without searching p choices

Let u=1+N in R, with N nilpotent, and let its order be p^a. Repeated p-th
powering finds the least a with u^(p^a)=1. It requires at most ceil(log_p k)
nontrivial stages, because in characteristic p

    (1+N)^(p^a)=1+N^(p^a).

If a=0, membership reduces to C=1. Otherwise put

    g=u^(p^(a-1)),  H=g-1.

Then g has exact order p and H is a nonzero nilpotent. Let ell be maximal with
H^ell !=0, so H^(ell+1)=0. For d in {0,...,p-1}, the binomial expansion gives

    H^(ell-1)*(g^d-1) = d*H^ell.                     (1)

A nonzero coefficient of H^ell is an element of the base field F_p. Equation
(1) therefore yields the ONLY possible digit d from one field division. The
checker validates the whole polynomial identity AND g^d against the proposed
order-p element. Matching a single coefficient without replay is not accepted.
The computation has no loop with p iterations. Finding ell takes at most k
ring products; every exponentiation uses binary exponents.

Now recover z in base p. Suppose z_<j=sum_(i<j) d_i p^i has already been forced.
A true solution C=u^z must satisfy

    V_j=(C*u^(-z_<j))^(p^(a-1-j)) = g^(d_j).        (2)

Equation (1) applied to V_j determines d_j; checking g^(d_j)=V_j either confirms
that necessary digit or disproves membership. Iterate for j=0,...,a-1. Finally
check u^(z_<a)=C. Even if intermediate projections do not distinguish every
nonmember, this final equality does.

**Sound rejection.** If C were a power of u, induction in (2) would force each
correct digit; it could not fail any of these checks. Failure therefore means
C is outside <u>.

**Sound acceptance.** The final equality directly proves membership.

**Completeness.** Every member has one exponent in [0,p^a), and the forced-digit
induction recovers it. Every nonmember is rejected at a digit check or the final
equality. This is a specialized characteristic-primary (p-power-order) subgroup calculation;
p need not be small. It is not a claimed breakthrough in generic discrete
logarithms.

## T7. Recover the least full schedule

If the unipotent calculation returns z0, all solutions are

    t=t_bar+m*z0 mod r,   r=m*p^a.

The representative lies in [0,r). To prove r minimal, let R0 be the order of x.
All field orders divide R0, so m divides R0. The order of x^m is R0/m, because
m divides R0. By construction that order is exactly p^a, so R0=m*p^a.
This also proves that the time progression is complete. The code independently
replays x^t=b in the full quotient ring. Positive outputs in the tests are
translated into the unchanged production format and rechecked there.

## T8. Soundness and completeness of the certificate system

Combining T2-T7 establishes soundness. An accepted negative claim exhibits one
of four exhausted alternatives: outside the cyclic span; a local field subgroup
obstruction; incompatible time congruences; or nonmembership in the residual
cyclic unipotent subgroup. An accepted positive claim gives the least complete
schedule. The checker computes its outcome and compares it with the claimed
outcome; an untrusted status label never authorizes an answer.

For completeness, every minimal polynomial has a primary factorization. Every
alpha_i has an exact finite-field multiplicative order with a prime factorization
and finite primality proofs. In each nonzero local subgroup a logarithm exists.
Choose these witnesses. Then all proof checks pass and the deterministic final
calculation returns the correct global answer. Nonmembers of a field subgroup
need no fabricated logarithm; the corresponding certificate entry is null and
is accepted only after a power obstruction is actually checked.

This is proof existence for valid prime-field invertible affine instances, not
a claim that the default bounded producer completes on every instance.

## T9. Bit size and checker complexity

Let h_i=deg f_i and B=ceil(log_2 p). Then sum_i h_i<=k<=d+1 and
log m_i<=h_i B. The entire list of factor coefficients and logarithms has
polynomial size in d,B; the dense inverse witness contributes O(d^2 B) bits.
The sum of the binary lengths of the orders is at most kB. Full prime
factorizations and recursive Pratt proofs for those integers have polynomial
size in that total length. The repeated-factor multiplicities are at most k.

The checker performs polynomially many elimination, polynomial gcd, modular
polynomial exponentiation, prime-proof, CRT and coefficient operations. Exact
field elements require O(B) bits, quotient elements O(kB) bits, and exponents
O(kB) bits. For example, recomputing the cyclic basis by elementary elimination
uses a coarse O(D^4) field-operation bound. Testing all Frobenius degrees is
also polynomial. No arithmetic is done in an exponentially large splitting field.

A deliberately loose conclusion is polynomial certificate size and deterministic
polynomial verification time. No linear-time or optimal-exponent claim is made.
The producer in producer.py uses bounded trial factoring and baby-step/giant-step;
its work can be exponential in log p. Supplied factorizations can help, but their
construction is not erased from an end-to-end comparison.

## T10. Consequence and limits

A verified empty set answers all later time-window queries with zero. A verified
progression answers them by integer arithmetic. This removes the NEED to provide
an explicit full-cycle negative witness for the supported mathematical problem.
It is not a lower bound showing every other classical invariant is large.

The code preserves prime-field inputs, invertibility, one initial state, one
full-state target, and exact deterministic semantics. It does not certify an
arbitrary program-to-recurrence translation, arbitrary guards, machine overflow,
singular/transient dynamics, or a practical benefit over existing analyzers.

T1 is the principal mathematical statement of this research package. The
algorithmic ingredients are strongly related to prior matrix-logarithm
reductions. Proof completion must not be confused with completion of the
novelty/significance audit or with an end-to-end application benchmark.
