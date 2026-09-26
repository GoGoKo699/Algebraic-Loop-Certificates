# What an exact orbit predicate does not compile away

Research note, 27 September 2026. Manuscript writing remains on hold. This is
supporting mathematical research and a query-scope audit, not a manuscript or a
new production interface. The constructions adapt established Diffie-Hellman,
Chinese-remainder automata, and exact-quotient arguments. No priority claim is
made for those principles; see SOURCES.md for the direct predecessors.

## 1. Three distinct tasks

The existing source theorem fixes S=(p,A,c,a), with p prime and A invertible,
and allows expensive source-dependent preparation of a polynomial-size checked
object. A later complete state b is classified by whether F^t(a)=b for some
nonnegative t, where F(x)=Ax+c. It does not recover t or solve quantified queries
over all possible b. This note makes three distinctions explicit:

1. Constructing a source representation versus checking/using one already given.
2. Recognizing a complete target versus finding a completion of a partial target.
3. An arbitrary observation versus an observation with its own closed dynamics.

Complexity statements use explicit matrices and binary integers. The diagnostic
clock code stores an explicitly materializable sparse binary matrix, not a
succinct oracle hiding an exponentially large dimension. No hardness statement
below is evidence that a small test instance is hard or that a quantum method
solves a useful new application.

## 2. A conditional barrier already occurs for a two-dimensional source

Let g generate a prime-order subgroup G of F_p^*, of known order q. Given
h=g^a, form the source

    F(u,v)=(g*u,h*v),     initial=(1,1).

Its orbit is exactly {(g^t,h^t):0<=t<q}. For a query (g^b,z) with z in G,

    (g^b,z) is reachable  <=>  z=g^(a*b).

The first coordinate forces t=b mod q; the second then gives the equivalence.
Thus a uniform algorithm which constructs an exact source recognizer in time
polynomial in log p and answers queries in polynomial time would decide the
Decision Diffie-Hellman problem on this subgroup family. A randomized compiler
with a bounded failure probability gives the corresponding randomized solver,
provided its stated resource/success bound actually holds on these sources.
An unknown or timeout outcome is not a DDH answer.

This is a direct application of the established DDH relation [S1], not a new
cryptographic assumption or unconditional complexity lower bound. Only use the
conditional obstruction for a subgroup family on which DDH is assumed hard.
Do NOT assert DDH hardness for the full group F_p^*, every subgroup, or every
finite field: character tests can make DDH easy in some of those groups. The
tiny groups used in check.py are deliberately easy controls of the equivalence.

There is no conflict with the existence of a short compiled recognizer. Given
the correct a as source-specific information, one can test a target by

    u^q=1 and v=u^a.

That predicate is compact, and g^a=h checks its alignment. Discovering a may be
expensive, but the target query then contains no discrete-logarithm search.
The previous compiler uses the same sort of checked source alignment in a more
general algebraic setting. This observation prevents source compilation from
being described as a new uniformly polynomial orbit algorithm.

Likewise, for the one-dimensional source x -> g*x from1, membership is the
standard subgroup test b^q=1, while a first-hit index solves g^t=b. Timing and
membership are different contracts. DDH is not claimed equivalent to DLP here;
the reductions support only their explicitly stated directions.

## 3. Partial-coordinate reachability is NP-complete over the fixed field F2

Define the following decision problem. An instance supplies an invertible binary
matrix A, an initial binary vector a, and a consistent partial assignment to
selected state coordinates. Ask whether some A^t a satisfies that assignment.
These guards are only conjunctions of coordinate equalities, not arbitrary
Boolean circuits. They are special cases of a linear observation Lx=b.

The problem is in NP: a hit, if any, occurs before the point orbit repeats,
hence at t<2^D for dimension D. Guess its at-most-D-bit canonical time and verify
A^t a by binary powering and the selected coordinate values. No period search
is required to validate such a witness.

For hardness we give an explicit adaptation of the prime-period 3SAT reduction
for unary automata [S2]. The important refinements for this project's contract
are a field fixed to F2, a source depending only on the number of variables,
and a guard consisting of coordinate values in one fixed basis.

### 3.1 A formula-independent family of easy sources

For n>=1 let p_1,...,p_n be the first n ODD primes. For every nonempty subset
S of {1,...,n} with |S|<=3, make a cyclic permutation block of length

    ell_S = product_(i in S) p_i.

The block starts with a one at position0 and zeros elsewhere, and rotates its
one by one position on each step. Add one fixed coordinate initialized to zero.
The complete vector has dimension

    D_n = 1 + sum_(1<=|S|<=3) ell_S.

Since p_n=O(n log(n+1)), D_n=O(n^6 log^3(n+1)). Both the sparse construction and
its dense matrix are polynomial-size in n. Finding these primes by ordinary
sieving or trial tests within a polynomial-size range is polynomial-time.

Let P_n be the direct-sum permutation matrix. Apply one fixed change of basis
S_n: in each singleton block, replace coordinate0 by coordinate0+coordinate1,
and leave all other coordinates unchanged. This transformation is its own
inverse over F2. Set

    A_n=S_n P_n S_n^(-1),     a_n=S_n(initial one-hot blocks and fixed zero).

The source contains no formula or target. It depends on n alone. It is explicit,
invertible, and its point period is exactly R_n=product_i p_i. Every block
period divides R_n, and the singleton blocks force every p_i to divide a return
time. Its order is odd, so its minimal polynomial over F2 is square-free: the
reduction does not exploit unipotent/repeated-factor difficulties.

At time t, a block S before the change of basis is one-hot at position
 t mod ell_S. The first transformed coordinate of a singleton block is one
exactly when t mod p_i is 0 or1. This is why we use odd primes, with distinct
positions0 and1, and why the basis is fixed independently of the formula.

### 3.2 Convert only the query

Let phi be a CNF formula whose clauses have at most three literals. Normalize
repeated literals and skip tautologies; a false empty clause can be represented
by demanding that the fixed-zero coordinate equal one.

First require the transformed coordinate0 of every singleton block to equal1.
Every surviving time therefore encodes a Boolean assignment

    alpha_i = t mod p_i in {0,1}.

A positive unit clause i requires singleton coordinate1=1; a negative unit
clause requires coordinate1=0. This coordinate is not altered by S_n.

For a clause on two or three distinct variables S, let epsilon_i be its unique
falsifying assignment: epsilon_i=0 for a positive literal and1 for a negative
literal. Ordinary CRT gives the unique r in [0,ell_S) with r=epsilon_i mod p_i.
Require coordinate r of block S to be zero. That block is unchanged by S_n,
so its forbidden coordinate is one exactly when the clause is false.

Every constraint is a SINGLE COORDINATE value. The guard contains at most n
plus the number of normalized clauses distinct constraints. Conflicting unit
requirements yield the same fixed-zero-coordinate contradiction. No auxiliary
existential state bits or formula evaluator are placed in the update rule.

It follows that

    A_n^t a_n satisfies the guard
      <=>  every t mod p_i is Boolean and these residues satisfy phi.

CRT supplies a time for every Boolean assignment. This proves NP-hardness and,
with the upper bound, NP-completeness. The complementary guard-avoidance problem
is coNP-complete. The reduction is a scope result for this representation,
not a claim that earlier unary-automata or periodic-recurrence hardness was new.

### 3.3 Full-state recognition of these sources is easy

Undo S_n on a proposed complete state. Reject a nonzero dummy coordinate or
any block which is not one-hot. Read the singleton block residues r_i. Every
other block S must have its one at a position congruent to r_i modulo p_i for
all i in S. Those tests are necessary and sufficient: CRT on the singleton
residues supplies one global time modulo R_n realizing all the blocks.

This is a direct polynomial-time full-state membership algorithm. It can also
recover the canonical time by CRT. It uses no difficult logarithm, factorization,
or exhaustive orbit table. Consequently the partial-target obstruction persists
even on sources for which the previously desired complete-state answers, source
construction, and time recovery are already easy classically.

This prevents blaming partial-target hardness on our particular invariant
language or its expensive preprocessing. A predicate can be efficiently
computed at a point without being efficiently searchable over a region.

## 4. The stronger preprocessing and certificate consequences

The source family above is fixed for each n, and the query carries the formula.
Suppose arbitrary source-only preprocessing, however expensive, always produced
polynomial-size data that enabled uniform polynomial-time answers to ALL
partial-coordinate queries on that source. For formulas of input length s,
use the source with n=s variables, padding unused variables. Its preprocessed
data would be polynomial-length advice depending only on s. Query construction
and answering would decide 3SAT in P/poly. Therefore this proposed compilation
capability implies NP is contained in P/poly. Uniform polynomial-time preparation
and answering would instead imply P=NP directly.

This advice argument applies to a UNIFORM query procedure and polynomial bounds
for the family. It is not a claim that arbitrary source-dependent compiled data
are inherently P/poly advice. They become advice here precisely because the
reduction fixes the whole source by the input length. We assert the implication,
not an unconditional exclusion of such preprocessing.

Similarly, a sound and complete polynomial-size STATIC negative-certificate
system for every guard-avoidance instance, with a deterministic polynomial-time
verifier, would put this coNP-complete problem in NP. Hence NP=coNP would follow.
This statement does not prohibit interactive proofs, randomized guarantees,
long certificates, restricted guard families, or incomplete invariant methods.
Nor does it invalidate the complete polynomial witnesses for individual point
nonmembership established in the preceding modules.

## 5. Counting must specify a finite horizon

For this reduction there is exactly one t in [0,R_n) for each Boolean assignment,
and the orbit states in that interval are distinct. Consequently

    number of guard-matching orbit states in one full period
      = number of satisfying assignments of phi.

Thus counting within one supplied full period is #P-hard by a parsimonious
reduction from #3SAT. The finite-horizon problem of counting integers 0<=t<H
which satisfy a partial guard is in #P: nondeterministically guess a fixed-length
binary representation of t, reject t>=H, and verify the guard using powering.
Its hardness already holds when H is exactly the known least point period of
our source. The infinite set of matching iteration times is NOT what is counted.
For general inputs, counting time occurrences and counting distinct states can
differ; the full-period condition is what identifies them here.

These are standard consequences of the explicit bijection, not a new general
counting-complexity theorem. #P-hardness does not say that each particular query
or every useful class of guards requires expensive computation.

## 6. A sufficient tractable class: closed linear observations

Let L have full row rank k over F_p, A invertible, and F(x)=Ax+c. The following
conditions are equivalent:

    there is B with LA=BL;
    A maps ker L into ker L.

If B exists, kernel invariance is immediate. Conversely define B(Lx)=LAx.
This is well-defined because two preimages differ by ker L; surjectivity of L
then defines a unique linear map B. Row solving constructs it with exact
polynomial-time linear algebra. B is invertible: A(ker L) is an equally
dimensional subspace of ker L, hence equals it, and A induces an invertible
map on the quotient.

The observation z=Lx consequently obeys the exact recurrence

    z_(t+1)=B z_t+Lc,    z_0=La.

Therefore the partial observation condition Lx_t=b is exactly the full-state
target condition z_t=b in this smaller source. The existing prime-field source
compiler can process this quotient and answer later targets within the chosen
observation space. Source preparation may still be expensive; no new uniform
polynomial construction guarantee follows. Projection does not preserve the
original first-hit or point-period information automatically; when needed those
must be obtained for the quotient's own orbit.

The relation LA=BL is checked directly, not inferred from sample trajectories.
Its absence means this globally autonomous linear quotient is unavailable,
not that the guard is unreachable or the query is hard. More general observation
methods, closure on a smaller initial cyclic span, and adding hidden coordinates
may be useful; this audit does not classify all tractable observations.

This is established exact lumping/quotient mathematics [S4,S5], specialized
here to the project's finite-field contract. It is not a new bisimulation
algorithm. The diagnostic tests preserve the original full-state API and use
a derived source rather than teaching the checker to trust an arbitrary guard.

## 7. What these results settle

The earlier exact source representation has a coherent scope: full-state
membership, possibly also membership in a verified autonomous observation
quotient. Neither a compact exact orbit predicate nor unlimited source-only
preprocessing of polynomial output size automatically gives efficient arbitrary
partial-state search, counting, or succinct general negative witnesses.

This audit supplies reductions, a tractable sufficient condition, and explicit
prior-work attribution. It does not claim a new production solver or close the
originality comparison for the earlier exact orbit certificate. The candidate
central contribution remains that precise certification contract; these results
support its boundaries rather than replacing the missing priority assessment.
