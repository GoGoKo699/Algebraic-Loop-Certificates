# What the original-state invariant and history witness actually compute

27 September 2026. This is an exact-scope audit of Gates 11 and 12, not a new
hardness, succinctness, or proof-system separation result. The argument is a
specialization of familiar inverse-bit separation and history-variable ideas.

## A generic odd-cycle monitor

Let X be a finite set with distinguished element 0, and let f be a permutation
of X fixing 0 whose other cycles have odd length. The original state is
q=(r,s,c) in X x X x {0,1}, initially (0,0,0). Every input u in X is allowed.
Put m=[s != 0 and f(r)=s]. The exact source semantics are

    r' = f(r) if u=0, otherwise u
    s' = s    if u=0, otherwise u
    c' = (1-c) [u=0] [not m]
    bad(q,u) = ([u=0] and c and m) or (s != 0 and f(r)=0).

Bad is evaluated before the transition; its second disjunct is ungated.
The published linear wrapper is the specialization f(r)=Ar. This generic
mathematical statement does not expand the repository's raw-source recognizer.

For s != 0, let T_s be its exact point period. If r is on s's orbit, let
t_s(r) be the unique t in [0,T_s) with r=f^t(s). Define

    R = {r=s=0, either c}
        union {s != 0, r on orbit(s), c=t_s(r) mod 2};
    S = {s=0, any r,c}
        union {s != 0, r != 0 on a different orbit, either c}
        union {s != 0, r on orbit(s), c=t_s(r) mod 2}.

R is exactly the reachable set and S exactly the universally safe set.
Indeed, a nonzero input starts (s,s,0); zero inputs traverse its cycle and
reset c at the imminent return. The last phase T_s-1 is even. Every listed
active R-state is reached by that seed and t zero inputs; both idle counters
are reached by zero inputs from initialization. If r=f^t(s) has the wrong
counter, after T_s-1-t zero transitions its counter is

    c XOR ((T_s-1-t) mod 2) = c XOR (t mod 2) = 1,

and the next bad evaluation detects the imminent return. Distinct nonzero
orbits never match or reach zero; s=0 never enables bad; any reseed enters R.
Finally, s != 0 and r=0 is immediately bad under every input. These facts
give both claimed equalities, including all unreachable states.

An original-state inductive safety invariant I means a total predicate with
I(q_0), and, for every q,u, I(q) implies both not bad(q,u) and I(q'). Thus
R subset I subset S. Consequently the forced-membership theorem is

    I(r,s,c) iff c=t_s(r) mod 2,
    whenever s != 0 and r is on orbit(s).

It is not a global uniqueness theorem: R and S themselves are different valid
invariants whenever nonzero states exist. Values on idle and different-orbit
states need not encode a phase.

## Exact evaluation versus phase recovery

Suppose the same-orbit promise holds and the exact odd T=T_s is supplied.
An I-membership oracle gives e(t)=t mod 2 as 1-I(r,s,0). For 0<=k<T,

    e((t+k) mod T) XOR e(t) XOR (k mod 2) = [t >= T-k].

Subtracting the odd T changes parity precisely when t+k wraps. Querying I
at (f^k(r),s,0), with k=T-b, therefore tests t>=b for any 1<=b<T.
Binary search recovers t with one base query and at most ceil(log2 T)
shifted queries. For T=1 the answer is already zero.

This is an exact-oracle reduction, with no prediction advantage, distribution,
cryptographic assumption, or noisy-bit theorem. Its cost includes producing
the shifted points. Polynomial-time evaluation of f alone is insufficient:
binary-exponent jumping f^k(r) may take exponentially many successive steps.
The polynomial-time consequence requires an efficient Jump(r,k) routine (or
circuit), efficient access to exact T, and efficient invariant membership.
For matrix f, repeated squaring provides Jump. Gate 12 provides exact T_s
from a complete factorization of a supplied odd annihilator, charging that
additional construction data and its acquisition separately.

Conversely, phase recovery determines I on the promised domain. A total
algorithm that also decides whether r is on s's orbit evaluates the canonical
invariant R, by the displayed formula. A single nonzero cycle removes that
orbit-membership task. Phase recovery alone does not determine an arbitrary
I's optional values elsewhere. Thus the equivalence is a promised-domain
evaluation equivalence, with a separately stated total canonical converse.

For a fixed effectively specified primitive binary family, the correspondence
is an exact instance of an inverse-bit separator, even without an output
promise. Fix nonzero s and M=2^n-1. Define the total n-bit permutation

    h_s(t) = A^t s for 0<=t<M;     h_s(M)=0.

The forward map has a polynomial-size circuit from matrix powers. At nonzero
r, I(r,s,0) is the predicate that the least significant bit of h_s^{-1}(r)
is zero. At r=0 it is false because that state is immediately bad; the inverse
is M, which is odd. The identity therefore holds for every output r. No
one-wayness of this particular permutation is asserted. In field coordinates,
its nonzero inverse is the ordinary canonical discrete logarithm.

The necessary complexity qualifications are:

* Uniformly polynomial construction and evaluation, with uniform Jump and
  exact-period access, give uniform polynomial phase recovery for the same
  family. Being handed an invariant does not establish its construction cost.
* Polynomial-size invariant circuits for a fixed family, with suitable
  polynomial-size Jump/period circuits, give nonuniform phase circuits by
  unrolling the reduction. This is not a circuit lower bound or a claim about
  all fields or arbitrarily changing source descriptions.
* Source decoding, artifact construction, pointwise predicate evaluation,
  global induction checking, proof production, and proof replay are different
  costs. None of the first two evaluation reductions bounds SAT proof size or
  makes native induction obligations easy.

## History changes what is supplied, not the projected mathematics

Given efficient exact T_s and Jump, a history register t yields the predicate

    H(q,t) = (r=s=0 and t=0, c arbitrary)
             or (s != 0, 0<=t<T_s, r=f^t(s), c=t mod 2).

Initialize t=0 and set t'=0 on reseed, s=0, or m; otherwise increment t in
a register wide enough for every T_s. These are total updates, leaving every
original input and update unchanged. On the active branch of H, m iff t=T_s-1,
which is even;
other active steps increment the phase without overflow. Thus H is inductive
and implies original safety. Every original run has a unique lifted history
run, and

    exists t: H(q,t)  iff  q in R.

Checking a supplied t uses Jump rather than reconstructing t. The quantified
formula on the left is nevertheless already a short original-state invariant:
its only free variables are original state variables. More precisely, a
polynomial-size circuit for H gives a short quantified-circuit representation;
to obtain a strict Boolean formula without expanding shared circuit nodes,
also existentially quantify Tseitin gate variables and constrain every gate
and the accepting output. That yields a polynomial-length quantified formula.
Therefore there is no general original-state quantified-formula-length
obstruction. The relevant distinction
is deterministic membership evaluation, quantifier elimination, or a chosen
quantifier-free circuit representation. The short existential formula need
not have an efficient deterministic membership evaluator. On the same-orbit
promise, both parity outcomes have a short phase witness; this also is not a
complexity-class separation.

The usual elimination bound makes the scope precise. Let any total conservative
extension add g Boolean history bits, with extended initial states projecting
onto all original initial states and an extended inductive invariant J that contains
those initial states and implies original safety. Assume every
original transition/input has an extension transition for every history value;
total deterministic history updates suffice. Then P(q)=exists h:J(q,h) is an
original-state inductive safety invariant: choose a witnessing h and lift each
original transition. It contains R because original initial runs lift.
If J has a size-S Boolean circuit, enumeration builds a circuit for P of size
O(2^g(S+1)), or evaluates it using 2^g membership tests. Combining this with
the phase reduction gives the corresponding conditional cost bound. In
particular, polynomial-size J with O(log n) history bits would give polynomial
nonuniform phase circuits when the other routines are polynomial. This is
ordinary existential elimination, not a new tradeoff or a proven lower bound
on g or S. It does not apply if the extension silently restricts original
inputs or fails to lift some original transitions.

Gate 11's phase register uses n bits; its naive elimination has 2^n choices.
Gate 12 replaces a common-period bound with an exact seed-period circuit.
Using only t<M when M is a nonminimal odd multiple can admit false phases;
the exact-period premise or selector is necessary for this particular H.
Purely definitional, efficiently evaluable combinational auxiliary variables
do not supply missing history; genuinely existential auxiliaries may hide the
membership work instead. Neither observation rules out other proof formats.

## Boundaries and prior context

Permutation structure, reachable seeds, and unrestricted advance suffixes
are substantive assumptions. A nonrecurrent tail can make both counter values
safe because a future match never occurs. A seedable even cycle makes this
monitor unsafe, so there is no safety invariant to evaluate. Restricting seeds
limits which correct-parity states must be included; guards that forbid the
all-zero suffix can remove the wrong-parity counterexample. Input-dependent
proof artifacts require their own semantics; this theorem concerns predicates
on q with universal quantification over every original input.

Bonet, Pitassi and Raz, *On Interpolation and Automatization for Frege Systems*
(SIAM Journal on Computing 29(6), 2000), Section 1.2, pages 1942–43, recalls
the Krajicek–Pudlak inverse-bit construction: two inverse graphs with opposite
input-bit constraints are inconsistent, and a separator on their common output
computes the inverse bit. The padded h_s above instantiates that familiar
pattern. Their interpolation and proof-complexity consequences have additional
hypotheses and are not imported as lower bounds here.
Primary source: https://www.cs.upc.edu/~bonet/revistas/siam3.pdf

Classical discrete-log bit recovery is also prior context; the elementary
wrap-threshold argument above is self-contained. See C. P. Schnorr, ECCC
TR98-033, https://eccc.weizmann.ac.il/report/1998/033/ . Efficient history
checking versus inverse reconstruction does not establish standalone novelty.
The conventional source-aware algebraic comparator can use the same history
interface. No new implementation or broader benchmark campaign is justified
by this conceptual audit alone.

`verify_controls.py` independently checks finite permutations fixing 0 with up to five
active elements, using state-space reachability and backward bad attraction,
and checks projection and exact-oracle recovery. These finite checks guard
the boundaries; they do not establish asymptotic complexity statements.
