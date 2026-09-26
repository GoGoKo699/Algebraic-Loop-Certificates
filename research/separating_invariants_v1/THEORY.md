# Three target-independent invariant schemes suffice for prime-field point exclusion

Research derivation, 26 September 2026. Manuscript writing remains on hold.
This is a theorem and executable proof contract, not a claim of priority,
a new fast logarithm algorithm, or a formally verified implementation.

## 1. Statement and distinction from the previous decision format

Fix an invertible affine map F(y)=Ay+c on F_p^d and an initial state a, with p
prime and all data explicit. For every b outside its orbit, one of the three
schemes below defines a set I satisfying

    a belongs to I;  F(I) is contained in I;  b does not belong to I.

The invariant certificate has polynomial bit length in d and log p. Its validity
and membership of any supplied state in I are deterministically checkable in
polynomial time. The statement quantifies over valid prime-field invertible
inputs; fixed implementation limits can return a resource error.

The proof binds the recurrence and a, but NOT b. Thus one checked object can
exclude many subsequent targets. A point inside I is only `not_excluded`;
this is not a positive reachability or exact-time certificate. A finite list
of forbidden states can be excluded by checking them all. Arbitrary symbolic
sets still require a separate implication/disjointness proof.

Unlike the previous complete decision certificate, these exported invariants
contain no exact field-order list, order factorization, irreducibility proof,
or discrete logarithm of the requested target. The base prime p still needs
its existing Lucas-Pratt proof. Discovery may require integer/polynomial
factoring and discrete logs aligning powers of two base eigenvalues. Those
costs are NOT erased. The deterministic unipotent procedure internally extracts
p-adic digits; `no target log` must not be interpreted as no arithmetic that
resembles logarithm computation.

The results are for program **inductive predicates**, not necessarily scalar
polynomials fixed by a group action. In particular a relative invariant that
scales after a step still defines an invariant zero set. Nor do we construct
a minimal separating set for every orbit simultaneously.

## 2. Common exact cyclic representation

Lift the affine map to T=[[A,c],[0,1]], v=(a,1). Let W be the span of
v,Tv,... and let mu be the monic minimal polynomial on this initial cyclic
module. Write k=deg(mu)<=d+1. Invertibility implies mu(0)!=0.

The checker calculates a Krylov basis, mu and coordinates by exact elimination.
It does not accept unproved eigenvectors or a producer-supplied minimality flag.
For y with (y,1) in W, write h_y for the unique polynomial of degree below k
such that h_y(T)v=(y,1). In R=F_p[X]/(mu), writing x=X mod mu,

    h_a=1,       h_(F(y))=x h_y.

If (y,1) is outside W, all predicates below reject it. The first scheme is
simply this cyclic-span condition. W is T-invariant; therefore it is sound
and excludes exactly those targets not in the affine slice of W. Computing
this representation is established cyclic-module algebra.

## 3. Power-kernel scheme

Supply a positive-degree monic divisor g of mu and a positive integer m.
Let Q=F_p[X]/(g), alpha=X mod g, and u=alpha^m. The checker verifies

    g divides mu,       (u-1)^(deg g)=0 in Q.

The second identity establishes that u is unipotent, so its order is a power
of p. Neither g's irreducibility nor m's minimality is a proof obligation.
Define

    I_(g,m) = { y in W's affine slice : (h_y mod g)^m belongs to <u> }.

Membership in <u> is computed by the deterministic nilpotent digit procedure
proved in ../complete_orbits_v1/THEORY.md, T6. For completeness of this note:
find the least a with u^(p^a)=1, let z=u^(p^(a-1)) and H=z-1. For maximal
ell with H^ell nonzero,

    H^(ell-1) (z^t-1) = t H^ell,   0<=t<p.

A nonzero coefficient determines the sole possible digit in F_p, and a whole
power replay checks it. Successive p-power projections determine at most
ceil(log_p(deg g)) digits; a final power equality decides subgroup membership.
No p-element search or trajectory enumeration occurs. This applies to arbitrary
candidate elements, including nonunits, which cannot pass the final equality.
For u=1 the predicate is just `(h_y mod g)^m=1`.

**Soundness.** Initially h_a=1, which passes. In the commutative quotient Q,

    (alpha h)^m = u h^m.

Multiplication by u preserves its cyclic subgroup. Thus the predicate is
inductive. Its complement consists only of unreachable targets. This argument
uses the actual checked divisor map; an arbitrary unrelated quotient would be
unsound.

This subsumes both a simple field subgroup obstruction and the previous
repeated-factor/unipotent obstruction. It exports only what is necessary to
prove closure and exclusion, not a complete factor-by-factor decision transcript.

## 4. Equal-powers scheme

Supply a monic positive-degree polynomial H of degree at most k^2, two elements
r1,r2 of S=F_p[Z]/(H), and positive integers e1,e2. Check

    mu(r1)=mu(r2)=0 in S,        r1^e1=r2^e2=lambda in S.

Evaluation at either root descends to a well-defined unital algebra map
phi_i:R -> S. Define

    I_equal = { y in W's affine slice : phi_1(h_y)^e1=phi_2(h_y)^e2 }.

Initially both sides equal one. After a step both sides are multiplied by the
same lambda, so equality is preserved. This establishes induction directly.
There is no need to certify that H is irreducible: soundness uses a nonzero
commutative quotient algebra and the verified root/common-multiplier identities.
The implementation accepts a deliberately reducible H in a regression test.

The comparison roots must satisfy mu(r_i)=0; matching update multipliers alone
would not establish well-defined maps on the initial cyclic module. A claimed
relative invariant is not accepted by testing it only on observed states.

## 5. Completeness: every unreachable target has one of these witnesses

The following factorization and order arguments are used to prove witness
existence. They are not additional untrusted data accepted by the new checker.

Factor mu=product_i f_i^(e_i), with distinct monic irreducible f_i. Let
K_i=F_p[X]/(f_i), alpha_i=X mod f_i, beta_i=h_b mod f_i, and let m_i be the
exact order of alpha_i. There are at most k factors; the sum of their degrees
is at most k. Targets outside W are handled by the span scheme.

### Case A: a local field target is not in its generator subgroup

If beta_i is zero or beta_i^(m_i)!=1, choose the power-kernel witness
(g,m)=(f_i,m_i). Then u=1, so the invariant rejects b. Conversely, over a
finite field the roots of Z^(m_i)-1 are exactly <alpha_i>, because that group
is cyclic and alpha_i has exact order m_i. Thus, if Case A never applies,
write uniquely beta_i=alpha_i^(t_i), 0<=t_i<m_i, for reasoning purposes.
The new proof does not include or verify these t_i.

### Case B: two necessary time congruences conflict

If the congruences t=t_i mod m_i are not jointly consistent, some pair i,j
fails t_i=t_j mod D, where D=gcd(m_i,m_j)>1. Pairwise compatibility is
sufficient for the generalized Chinese remainder theorem.

Both fields embed into F_(p^L) with L=lcm(deg f_i,deg f_j). This extension has
L<=deg f_i*deg f_j<=k^2, not the possibly much larger common splitting field
of every factor. Choose a defining irreducible H of degree L and images r1,r2
of alpha_i,alpha_j. They satisfy mu(r1)=mu(r2)=0.

The elements w1=r1^(m_i/D) and w2=r2^(m_j/D) both have exact order D. The
multiplicative group of the common finite field is cyclic, hence w2^c=w1 for
some c with 1<=c<D and gcd(c,D)=1. Choose

    e1=m_i/D,       e2=(m_j/D)c.

The update multipliers match. At b the two powers are w1^(t_i) and
w1^(t_j), which differ. The equal-powers scheme therefore excludes b.
Finding c can require a logarithm between **base** elements; no efficient
construction claim is hidden by the existence proof.

### Case C: the field residues are compatible but the full ring target is not

Let m=lcm_i(m_i), and choose the canonical compatible residue t_bar modulo m.
Set u=x^m in R and c=h_b*x^(-t_bar). Both u and c are one modulo every
irreducible f_i, so both belong to the principal-unit group 1+J, where
J=(product_i f_i)/(mu) is nilpotent. Every element of 1+J has p-power order,
and m is coprime to p.

Suppose h_b^m were a power u^z. Since h_b=x^(t_bar)c, this gives

    c^m = u^(z-t_bar).

Choose a power P of p annihilating the orders of c and u. Raising to an integer
inverse of m modulo P shows c belongs to <u>. Then h_b belongs to <x>, a
contradiction. Consequently h_b^m is outside <x^m>.

Choose the power-kernel witness (g,m)=(mu,m). Its generator is unipotent, so the
checker can establish that exclusion by the deterministic digit test.

These alternatives exhaust nonmembership. Cases A and B use only ordinary
finite-field cyclic groups; Case C preserves information hidden in repeated
factors. This proves the stated relative completeness of the three schemes.
It does not prove that every individual invariant defines the orbit exactly.

## 6. Bit complexity and trust

Set B=ceil(log2 p). The inverse witness occupies O(d^2 B) bits. The complete
prime proof for p has polynomial size in B. A power-kernel witness has at most
k+1 coefficients and an exponent of O(kB) bits in the completeness construction.
An equal-powers witness uses O(k^2) coefficients and exponents with O(kB) bits.
Hence the selected witness has polynomial size in d,B.

Checking the inverse, cyclic representation, polynomial divisibility, root
substitution, common power identity, and nilpotent subgroup predicate takes
polynomial bit time. Exponents are binary encoded and evaluated by repeated
squaring. There is no arithmetic in a common splitting field of all components.
Default byte/integer/dimension limits remain implementation policies. The
reference producer may take exponential work in B for its trial factorer,
embedding search, or base alignment. The theorem is not uniform polynomial-time
invariant synthesis.

The Python checker shares its primality and polynomial arithmetic with earlier
modules. The new producer is not imported by its checker. Exhaustive induction
checks establish finite evidence, not machine-checked proof of the interpreter,
parser, cyclic algebra, or implementation on all inputs.

## 7. Reuse and a concrete invariant

Over F13 let F(s,t)=(4s,5t) and a=(1,1). Since 4^3=5^2=12, the relation

    s^3=t^2

holds initially and is preserved. It excludes (10,12), since 10^3=12 and
12^2=1 modulo13. This one relation excludes 156 of the 169 possible states.
The actual orbit has length12; the invariant contains13 states, including
(0,0), which is unreachable. Its inclusion must be reported as `not_excluded`,
not `reachable`. This example is elementary and supplies no hardness evidence.

Once a certificate for this invariant is checked, testing another target
requires only coordinate/predicate evaluation. Changing A,c,p or the original
initial state invalidates its source binding; changing the queried target does
not. No new proof of an unsupported whole-program translation is implied.

For the stipulated point-guard loop, exclusion implies nontermination, but the
invariant does not supply a least hit time when it fails to exclude the target.
For an assertion that the state always satisfies I, the induction proof is
already the relevant safety argument. This restricted predicate language is not
a solver for arbitrary guard implication or general nonlinear program safety.

## 8. Relation to existing mathematics

These are specialized separating predicates built from established cyclic
algebra, characters, and nilpotent-unit arithmetic. Finite-group separating
invariants and diagonal-action monomials have substantial prior literature;
see SOURCES.md. The equality predicate is a relative-invariant zero set rather
than automatically a member of the scalar invariant ring. Our representation
and checker obligations differ from minimizing polynomial degree or producing
an invariant-ring generating set. That difference does not itself prove a
new research contribution.

The strengthened result relative to this repository is a proved small grammar
of reusable inductive predicates, with complete point-exclusion coverage and
less exported algebraic proof data. A claim of originality or practical
advantage beyond existing invariant construction remains to be justified.
