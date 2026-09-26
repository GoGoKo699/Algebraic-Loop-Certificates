# One residue-field certificate for an entire prime-power orbit

Research note, 27 September 2026. Manuscript writing remains on hold. This is
an ordinary mathematical proof and an experimental implementation contract, not
a formal proof of Python correctness or a cleared originality claim.

## 1. Result and what is actually new relative to this repository

Let N=p^e be supplied as an EXPLICIT binary integer, together with p,e, an
invertible d-by-d matrix A modulo N, a translation c and an initial state a.
A checker verifies the prime claim and N=p^e. The modulus must not be represented
only by a binary exponent e: polynomial time in e log p is not in general
polynomial time in log e. Write L=bitlength(N).

There is a polynomial-size, source-only certificate which compiles into a
predicate recognizing every full-state member of the orbit of F(x)=Ax+c from a.
Compilation and each query are deterministic polynomial-time in d,L and the
size of the constituent field certificate. The construction invokes the
existing prime-field source compiler ONCE on a derived source of dimension
at most d+1. It does not invoke a new field compiler for every precision digit
or every requested target. In particular it requires no finite-field logarithm
of a later target. It need not recover that target's first occurrence time.

Source-only synthesis can still be expensive in d and log p. This is a reduction
from certified prime-field source compilation, not a new uniformly efficient
solution of discrete logarithms. No similarly strong source-only reduction for
arbitrary composite N is claimed: different prime factors introduce time
compatibilities not handled by this one-characteristic construction.

The earlier precision-fiber method derives a field problem after a target's
lower-precision time has been recovered. This note instead removes the unknown
time from the membership condition. It must retain the INITIAL CYCLIC MODULE,
which may not be a free module over Z/NZ. Ordinary reduction of the initial
state modulo p would be insufficient.

## 2. A small cyclic module, not the whole ambient vector space

Put T=[[A,c],[0,1]], v=(a,1), and D=d+1. Work over Z/NZ and let

    M = span{v,Tv,...,T^(D-1)v}.

Cayley-Hamilton over a commutative ring shows that M is invariant under T and
contains every orbit state. Since T is invertible on the finite ambient module,
it maps M bijectively to itself. Call its restricted automorphism C. The vector
v is a CYCLIC generator of M under polynomials in C. M is nonzero because of
the last coordinate1, even when the original initial state is zero.

For a queried state b, first test whether w=(b,1) lies in M. If so, express

    w = h(T)v

with deg h<D by modular linear algebra. Define B=h(C) in End(M). This map is
independent of the particular polynomial representative: if h(C)v=0, then
h(C)C^j v=0 for every generator of M, so h(C)=0 on M. Conversely Bv=w determines
B uniquely among these polynomial endomorphisms. Thus

    F^t(a)=b   <=>   B=C^t as endomorphisms of M.             (1)

B is not initially assumed invertible. The residue test below proves it when
needed. Every B obtained this way commutes with C.

## 3. Deterministic coordinates for mixed-order generators

Form the D-by-D Krylov matrix G. Over Z/p^eZ, select a nonzero entry of minimum
p-adic valuation in the remaining submatrix, move it to the next diagonal
position, invert only its UNIT part, and eliminate its row and column. This
produces invertible U,V with

    U G V = diag(p^s_1,...,p^s_k,0,...,0),   0<=s_i<e.

The routine uses exact row/column operations and polynomially many bounded-size
ring operations. It does not factor integers or assume a nonunit has an inverse.
Both the diagonalization and the tracked inverse of U are replayed in the code.

It gives M the coordinates

    M ~= direct_sum_i Z/(p^a_i)Z,     a_i=e-s_i.

For y in the ambient module, write y'=Uy. Membership requires y'_i divisible by
p^s_i for i<=k and the remaining coordinates zero. Its module coordinate is
z_i=y'_i/p^s_i modulo p^a_i. A polynomial coefficient vector is V(z,0,...,0),
because G V(z,0,...)=U^(-1)diag(p^s_i)(z,0,...).

In these coordinates an endomorphism H has its i-th row reduced modulo p^a_i
and must satisfy

    p^a_i divides H_ij p^a_j.

Products are ordinary integer matrix products followed by row-specific modular
reduction. The divisibility condition is what makes intermediate reductions
well-defined. These endomorphism representations are established mathematics;
Hillar-Rhea is a direct predecessor, not background too remote to compare.
The checker computes these coordinates; it does not accept an unverified
producer statement that M is free or that a proposed basis spans it.

## 4. The right field reduction is M/pM

In the coordinates above, M/pM is F_p^k. Let Cbar be C reduced rowwise modulo p,
and vbar the module coordinates of v modulo p. They define a genuine linear
field source. vbar is cyclic: the polynomial generators of M descend to generators
of M/pM. In particular vbar is not zero, since otherwise M=pM, contradicting
nonzero M and p^e M=0.

The field compiler supplies a checked exact orbit predicate for (Cbar,vbar),
plus its least point period r0. Cyclicity means r0 is also the order of Cbar.
Write r0=m p^b with gcd(m,p)=1. No factor search is needed to remove the p-part.
For a target in M, a true field-membership answer implies that for some t

    Bbar vbar=Cbar^t vbar,  and hence Bbar=Cbar^t.           (2)

The implication uses the CYCLIC generating vector and commutation. It would not
hold for an arbitrary target map agreeing on only one vector of a noncyclic
space.

**Automorphism criterion.** An endomorphism B of M is invertible if Bbar is.
Indeed B(M)+pM=M then implies B(M)+p^j M=M by induction; at j=e it gives
B(M)=M. Surjectivity on the finite set implies injectivity. This is the finite
module form of the standard criterion also given by Hillar-Rhea. It does not
assert that an arbitrary matrix over a composite ring can be inverted by field
Gaussian elimination.

## 5. The part invisible modulo p is a p-group

An automorphism K with Kbar=I has form I+E with E(M) subset pM. If E(M) subset
p^j M, the binomial expansion proves

    ((I+E)^p-I)(M) subset p^(j+1) M.

For j>=1, the first term pE has that property; the higher terms do as well,
including the last E^p, because pj>=j+1. This works for p=2. Repeating shows
K^(p^(e-1))=I. Thus the kernel of reduction on automorphisms consists of
p-elements. No embedding of End(M) into a single free matrix ring is assumed.

Let u=C^m. Its field image is unipotent of dimension k and therefore has order
at most p^ceil(log_p k). The preceding argument gives the bound

    ord(u) divides p^(e-1+ceil(log_p k)).

Repeated p-th powering finds its exact order p^alpha in polynomial bit time.
The reference uses a slightly looser safe loop bound. Since m divides ord(C)
and the residue-reduction kernel has p-power exponent,

    ord(C)=m p^alpha.                                    (3)

This is also the original point period, because v generates M. It is not the
order of an unnecessarily larger matrix acting outside the initial module.

## 6. Remove the unknown target time

The proposed exact query consists of three checks:

1. w=(b,1) belongs to M.
2. The field predicate accepts the module coordinate wbar in the orbit of vbar.
3. B^m belongs to the cyclic p-group generated by u=C^m.

Necessity follows immediately from B=C^t. For sufficiency, condition2 supplies
an exponent t in the EXISTENCE proof, without requiring the query algorithm to
compute it. Put D0=B C^(-t). By (2), D0 reduces to I modulo pM, so it is a
p-element. B, C and D0 commute. Condition3 gives B^m=u^z for some z, hence

    D0^m=u^(z-t).

Choose a p-power P annihilating D0 and u, and an inverse s of m modulo P. Then

    D0=(D0^m)^s belongs to <u>.

Consequently B=C^t D0 belongs to <C>, proving (1). The existence of t is enough:
it disappears from the implemented predicate. The query need not find a
semisimple phase before testing the p-primary residue.

This argument does not transfer automatically across different prime factors
of N. The kernel here is a p-group and the coprimality of m to THAT p is crucial.

## 7. Polynomial cyclic p-group membership without a p-element search

The query must not conceal a loop over p candidate digits. Here is the explicit
routine used by the implementation. Suppose u has verified exact order p^alpha
in Aut(M), and put g=u^(p^(alpha-1)). For alpha=0, test B=I directly. Otherwise
g has order p. To decode a potential order-p element V=g^d, use one of two cases.

**Case A: gbar is nonidentity.** Put E=gbar-I. Over F_p this is a nonzero
nilpotent matrix. Let ell be maximal with E^ell nonzero. Then

    E^(ell-1)(Vbar-I) = d E^ell.

A nonzero coefficient determines the unique possible d in F_p. Replay g^d=V
on the FULL mixed module, not just on its reduction.

**Case B: gbar=I.** Let j>=1 be maximal with (g-I)M subset p^j M. Equivalently,
j is the least valuation of a nonzero entry in the row-reduced matrix g-I.
Select an entry attaining j. Higher binomial powers vanish modulo p^(j+1)M,
so the selected coordinate of (V-I)/p^j modulo p equals d times the corresponding
nonzero coordinate of (g-I)/p^j. A field division again gives the only possible
d, followed by the same FULL replay.

For a candidate H, recover z modulo p^alpha by the usual digit induction. If
the first i digits give z_i, form

    V_i=(H u^(-z_i))^(p^(alpha-1-i)).

A true member must give g raised to the next digit. Determine that digit using
A or B and reject when its full replay fails. After alpha digits check u^z=H.
A member cannot fail by induction; final equality certifies acceptance; any
nonmember fails along the way or at that final test. The routine is also safe
on noninvertible endomorphism candidates, which cannot pass final equality.

There are O(e+log k) stages, each using binary powers with polynomial-size
exponents and exact mixed-modulus arithmetic. This is structured p-primary
arithmetic, not an improvement to a generic black-box discrete-log algorithm.
The prime-power digit strategy is classical; our proof states why the order-p
subproblem here has a coefficient solution instead of a generic search.

## 8. Counterexample to reducing the original coordinates

For F(x)=2x modulo25 and a=5, the orbit is {5,10,20,15}. Reducing those ordinary
coordinates modulo5 gives only zero and loses the four-cycle.

The lifted cyclic module is

    M={(5z,w): z mod5, w mod25} ~= Z/5Z + Z/25Z.

But pM={(0,5w)}. The residue M/pM retains the z direction, which is not visible
in ambient reduction of (x,1) modulo5. The derived field action sees the factor2
and its order4. The code deliberately retains this nonfree example; treating
M as a vector space over Z/25Z or using only the ambient modulo5 orbit would
not implement this theorem.

## 9. Certificate and bit bounds

The source contains explicit N,p,e,A,c,a. The serialized certificate contains
an inverse of A modulo N, a proved-prime record for p, and ONE source certificate
for the field orbit constructed from M/pM. Both normalized module data and the
field source are reconstructed by the checker from the trusted input.
The supplied field certificate is bound to that computed source.

If the field certificate size is S(k,log p), the new certificate size is at most

    S(k,log p)+poly(d,L),       k<=d+1.

Compiler verification and every query similarly add polynomial overhead to the
existing field costs. Module elements require at most kL bits, and the p-order
exponent has O(L+log d) bits. Polynomial representatives, coordinate transforms,
endomorphism powers and all dimension bounds are explicit. No truth table,
splitting field of exponential degree or oracle-access upload is introduced.

A source-only producer needs one invocation of the existing field producer
plus polynomial exact normalization. It can copy p's prime proofs from that
certificate. The bounded reference producer charges its remaining expensive
field algebra and returns unknown when that budget fails. Its cost is not
claimed polynomial in general. The current implementation reserves one affine
coordinate under the field producer's 32-coordinate default and therefore
accepts at most31 original coordinates. Changing resource limits requires a
separate implementation review; the theorem is parameterized, not a statement
about acceptance under one fixed default.

## 10. Query scope and scientific boundary

The compiled source recognizes every complete target and supplies the common
least point period. It does not recover first hit times, bounded-time answers,
arbitrary partial-coordinate guard satisfiability, or exact counts in symbolic
regions. The established hardness boundary for those richer queries remains.
The primary root API and the earlier modular per-target proof format are unchanged.

The 64-bit x<-5x+1 example has a source certificate of531 compact JSON bytes,
with one two-dimensional F2 certificate and no target encoded in it. A531-byte
all-target membership certificate and a292-byte one-target timed-hit certificate
prove different things; their byte counts are not a matched performance claim.
The source is a known easy scalar family, not a hard benchmark. Word width alone
must not be advertised as a source of classical hardness.

The new technical statement is a torsion-aware, target-phase-free reduction from
prime-power source compilation to one prime-field source compilation. Its use
of endomorphism modules, residual p-groups and cyclic order arithmetic has direct
prior art. SOURCES.md records that comparison. Whether the combined certification
contract is original remains unestablished. Neither a new schema nor the tests
settle the publication contribution.
