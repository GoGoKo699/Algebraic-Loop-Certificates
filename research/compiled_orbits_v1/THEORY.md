# Certifying one exact orbit recognizer before any target is supplied

Research note, 26 September 2026. Manuscript writing remains on hold. These are
ordinary proofs, not a formal verification of the Python implementation or a
claim that the stated compilation result has publication-level priority.

## 1. The quantified result

Let S=(p,A,c,a) specify an invertible affine map F(y)=Ay+c of F_p^d, with prime p
and a fixed initial state a. There exists a certificate C_S of polynomial bit
length in d and log p for which deterministic polynomial-time compilation
returns a predicate P_S such that, for EVERY y in F_p^d,

    P_S(y) is true  <=>  there exists t>=0 with F^t(a)=y.

Each subsequent query takes polynomial bit time and performs no finite-field
target discrete-logarithm search, factorization, irreducibility test or orbit
traversal. It uses a checked, fixed algebraic representation. The compilation
also determines the least point period, but the query does not return a first
hit time. Finding C_S may be expensive; there is no uniform polynomial-time
synthesis claim. A source-dependent compiled object is NOT ordinary length-only
advice in the definition of P/poly.

The earlier theorem asserted that for each unreachable b there is a small
invariant separating b. That alone does not imply a single polynomial-size
family works for every b. Here we explicitly construct a sufficient family
whose cardinality and TOTAL representation size are polynomial and depend
only on S. Its conjunction is the exact orbit, hence the strongest inductive
set containing a. All old single-invariant objects remain overapproximations
unless their own exactness is separately established.

The new format checks completeness, not merely induction. It accordingly
restores several source-level obligations omitted from a single separating
witness: complete primary factorization, irreducibility of those factors,
exact element orders, and sufficient compatibility coverage. Those obligations
are checked once at compilation, not once per query. This is a tradeoff, not
an across-the-board claim that the new checker is simpler or faster.

## 2. Source-only decomposition

Lift F to T=[[A,c],[0,1]] and v=(a,1). Let W be the Krylov span of v. Exact
elimination computes its basis and minimal polynomial mu, of degree k<=d+1,
with mu(0)!=0. As before, h -> h(T)v identifies R=F_p[X]/(mu) with W. A queried
state y outside the affine slice (y,1) in W is unreachable. Inside it, h_y is
unique and one step maps h_y to x*h_y, where x=X mod mu and h_a=1.

The checker precomputes a left inverse of the cyclic basis. Each query obtains
h_y by a matrix-vector product and reconstructs (y,1) to confirm it lies in W.
It does not rerun Gaussian elimination per target. This is an elementary
implementation choice, not a new linear algebra algorithm.

Supply the complete primary factorization

    mu = product_i f_i^(e_i),

with distinct monic irreducible f_i. Let h_i=deg f_i, alpha_i=X mod f_i and
m_i=ord(alpha_i) in K_i=F_p[X]/(f_i). Verify the factorization and exact orders
using the existing deterministic polynomial and prime-proof routines. Put
m=lcm_i m_i. Then gcd(m,p)=1 and u=x^m is unipotent in R. Its order is p^a for
some a, computed by the previous nilpotent routine in polynomial bit time.
The least order of x is r=m*p^a, hence r is the point period of a.

These are established cyclic-module, field-order and primary-unit arguments;
this note's role is a complete source-only certificate/query contract.

## 3. All local subgroup tests can be stored before seeing a target

For a state coordinate h let beta_i=h mod f_i. Define local predicates

    beta_i^(m_i)=1 in K_i.                              (L_i)

They imply beta_i is a nonzero member of <alpha_i>, because K_i^* is cyclic
and has a unique subgroup of order m_i. Thus, for proof purposes, there is a
unique residue t_i modulo m_i with beta_i=alpha_i^(t_i). The algorithm does
NOT need to calculate t_i for the target.

The local conditions alone do not ensure that the t_i are compatible. They
must all describe the SAME iteration count. Exactness requires the next stage.

## 4. Pairwise compatibility without a target logarithm

For a pair i,j set D=gcd(m_i,m_j). If D=1 there is no constraint. Otherwise
embed K_i and K_j into a common finite field of degree lcm(h_i,h_j)<=h_i*h_j
over F_p, and write r_i,r_j for the images of alpha_i,alpha_j. Define

    w_i=r_i^(m_i/D),   w_j=r_j^(m_j/D).

Both have order D. There is a c in [1,D) with gcd(c,D)=1 and w_j^c=w_i. This
alignment depends only on the source. The reference producer may solve this
base-to-base logarithm; that cost is part of preprocessing.

For the target the equality

    h(r_i)^(m_i/D) = h(r_j)^((m_j/D)*c)                  (E_ij)

holds exactly when t_i=t_j modulo D, provided the local predicates pass. Both
sides are powers of the same element w_i, of exact order D.

### Checked comparison algebras need not be fields

The certificate may use any nonzero S_ij=F_p[Z]/(H_ij), H_ij monic of positive
degree at most h_i*h_j, and supply roots r_i,r_j such that

    f_i(r_i)=0, f_j(r_j)=0, r_i^(m_i/D)=r_j^((m_j/D)*c).

Because f_i and f_j were proved irreducible, evaluation gives unital injections
of their fields into this nonzero quotient. The image element orders are
therefore unchanged. The equality test has exactly the claimed meaning even
when H_ij is reducible. No separate irreducibility test of H_ij is necessary.
Unlike the old single invariant, roots of mu alone do not suffice here: they
must correspond to the named primary components whose times are compared.

A common field supplies existence. The stronger checker obligation is the
explicit root and common-power identities, not an unpriced giant splitting
field or an assumed consistent mapping between extension representations.

## 5. Which comparison edges are sufficient? An exact graph criterion

Consider any list of positive moduli m_i and a graph G on their indices. An
edge ij requires t_i=t_j modulo gcd(m_i,m_j). The edge requirements imply ALL
pairwise compatibility conditions for EVERY residue assignment if and only if:

    For each prime q and each level h>=1, the vertices i with q^h dividing m_i
    induce a connected subgraph of G, whenever there are at least two of them.

**Sufficiency.** Fix i,j and a prime power q^h dividing gcd(m_i,m_j). A path in
the induced subgraph propagates equality modulo q^h. Doing so for every prime
power in the gcd gives the missing pair condition. The generalized CRT then
gives one common residue class for all t_i.

**Necessity.** Suppose the q^h-support is disconnected. Select one component.
Assign residue q^(h-1) modulo the q-primary part to its vertices, and zero to
all other vertices. Assign zero for every other prime, and combine these local
assignments by integer CRT at each vertex. Edges crossing the selected component
cannot have both endpoints in the q^h-support, so their common q-power is at
most q^(h-1); they cannot see the discrepancy. All edge constraints hold. A
pair of vertices in different components of that support disagrees modulo q^h,
so global compatibility fails. This proves the criterion.

Supports change only at the positive q-adic valuations of the m_i. The checker
can check those levels using the already verified order factorizations. No new
integer factorization is performed in this step.

**Construction.** For each q choose one index with largest q-adic order and
connect it to every other index divisible by q. The union of these stars meets
the criterion at every level. Repeated edges are stored only once. This gives
at most sum_q(|support(q)|-1) edges, at most k choose2 and at most the total
number of prime occurrences in the supplied order factorizations. It need not
be a minimum-edge graph. We claim no new optimal sparsification algorithm.

**Counterexample to mere connectivity.** For orders 6,10,15, the two edges from
the first vertex check agreement modulo2 and modulo3. Residues (0,0,3) pass
both, but the second/third pair conflicts modulo5. Every full-coverage graph
here must contain the triangle, not a spanning tree. Higher valuations matter
too: for moduli (2,4,4), a path through the order2 vertex cannot enforce agreement
modulo4 between the other two. Both controls are retained in the tests.

The criterion is proved here as a precise certificate obligation. It is an
elementary CRT/graph statement, not claimed new without a separate prior audit.

## 6. One global predicate retains ALL repeated-factor information

Assume the local and selected edge predicates hold. By the verified coverage
criterion, there exists t_bar modulo m agreeing with all t_i. Set

    C=h*x^(-t_bar) in R.

Then C is one modulo every irreducible factor, so C lies in the finite abelian
principal-unit p-group 1+J, where J is the nilradical of R. A global target hit
exists exactly when C belongs to <u>, with u=x^m.

This condition can be checked without knowing t_bar:

    h^m belongs to <u>.                                (U)

Indeed h^m=u^(t_bar)*C^m. The m-th power map is an automorphism of the finite
p-group 1+J because gcd(m,p)=1; its restriction to <u> is likewise an
automorphism. Therefore C^m belongs to <u> if and only if C does. Formally one
can raise to an inverse of m modulo a p-power annihilating the whole group.
Thus (U) is equivalent to the remaining condition once (L) and (E) hold.

The earlier deterministic unipotent membership routine checks (U) without a
search across p values. It extracts at most ceil(log_p k) characteristic-adic
digits using coefficient identities and verifies a final power equality.
This is a specialized cyclic p-group computation, not an arbitrary finite-field
discrete logarithm. The costs remain in the per-query bound.

If (U) passes, write C=u^z for the existence proof; then h=x^(t_bar+m*z). If h
is a power of x, all conditions plainly hold. This proves exact equivalence.

## 7. Polynomial size and cost; no orbit table is implicit

The primary factors have sum_i h_i<=k. For any selected subset of pairs,

    sum_(i<j) deg H_ij <= sum_(i<j) h_i*h_j <= k^2/2.

The source-algebra and pair-map coefficient data therefore occupy O(k^2 log p)
bits, apart from small indexing overhead. Pair exponents are bounded by the
corresponding field-element orders and have O(k log p) bits; the total order
and factor-proof data have polynomial length as in the earlier theorem.
Pratt prime proofs, the matrix inverse, and the source representation are also
polynomial. The certificate contains no list of orbit states or target answers.

Compilation consists of polynomial-time prime proof checks, elimination,
irreducibility/order checks, graph traversal, quotient power equalities and
nilpotent arithmetic. Queries do a fixed coordinate map and replay, local
powers, selected equal-power tests, and one nilpotent-group test. All quotient
degrees and exponent bit lengths are polynomial in the source input size.
A loose polynomial complexity bound is claimed, not an optimal exponent.

Finding factorization, element orders, comparison embeddings and base alignment
may be costly. The producer's bounded trial and BSGS methods are reference
methods, not a strongest production benchmark. On budget exhaustion it returns
unknown and no certificate. A reject during compilation means invalid evidence,
not an assertion about the reachability of an unspecified target.

## 8. What exact membership does and does not supply

The new source object has NO target field. It returns a reachable/unreachable
answer for any later full-state target, plus the common point period. It does
not return the first hitting time. In a scalar example with a subgroup generator
g of order r, membership is the standard test y^r=1; recovering t from g^t=y
is still a discrete-logarithm task. No contradiction with logarithm hardness or
new cryptographic algorithm follows.

For the stipulated point-guard program, membership decides termination but not
the number of body executions. Finite lists of forbidden states can be checked
one by one. Neither exact point membership nor small output size makes arbitrary
symbolic-set intersection, counting points in a guard, bounded-time reachability,
or source-language extraction free. This module does not extend the same
compiled-query bound to composite rings, multiple initial states, singular
maps or nondeterministic updates.

New targets may even be chosen adaptively: this is an exact universally checked
predicate, not a statistical sample bank or a per-query probability guarantee.
Changing p,A,c or a invalidates the source binding. In-memory dataclasses are
not unforgeable security tokens; external users must compile verified serialized
evidence instead of manually constructing a trusted object.

## 9. Scientific status

This closes the exactness and source-only reuse questions for the present
prime-field grammar. It does NOT close the novelty question. Finite-group
separation, compact invariant circuits, subgroup membership after preprocessing,
and cyclic primary decomposition are established. SOURCES.md records new,
particularly direct comparisons showing why those broad ideas cannot be the
claimed contribution. No paper should advertise a first use of compilation,
compact invariants, or offline logarithms from this result alone.
