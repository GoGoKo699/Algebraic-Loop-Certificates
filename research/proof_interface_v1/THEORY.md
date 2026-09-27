# Exact phase boundary for state-only invariants of the LFSR monitor

27 September 2026. This is a conditional interface result, not a cryptographic
lower bound or novelty claim. The native proof-interface experiment has its
own contract; this note establishes the mathematical obligations it must retain.

## 1. Transition system

Let A be an invertible binary n-by-n matrix of odd order. The state is
q=(r,s,c), r,s in F_2^n and c in {0,1}; input u is arbitrary in F_2^n.
Put m=[s != 0 and Ar=s]. The source-bound wrapper is

    r' = Ar if u=0, otherwise u
    s' = s  if u=0, otherwise u
    c' = (1-c) [u=0] [not m]
    bad(q,u) = ([u=0] and c and m) or (s != 0 and Ar=0)

Initial state q_0=(0,0,0). Safety quantifies over all future inputs, and the
bad detector is evaluated BEFORE the transition. The second disjunct is not
input-gated.

For nonzero s let T_s be its least point period, which is odd. For r on its
orbit write t_s(r) for the unique integer in [0,T_s) with r=A^t s.

## 2. Exact reachable set R

R consists of:

* r=s=0, either counter value;
* s != 0, r on the orbit of s, and c=t_s(r) mod 2.

Proof: zero inputs from q_0 toggle c while retaining r=s=0, so both idle states
are reachable. A nonzero input sets r=s=u and c=0. Each uninterrupted segment
then follows the phase t=0,...,T_s-1. A match occurs just before phase T_s-1
advances to zero and resets the counter. Since T_s is odd, the counter there
is zero. Conversely, any active listed state is reached by seeding s and then
applying t_s(r) zero inputs. This proves both containment directions.

## 3. Exact universally safe set S

S consists of:

* s=0, ANY r and c;
* s != 0, r != 0 on a different A-orbit from s, either c;
* s != 0, r on the orbit of s, and c=t_s(r) mod 2.

Proof: if s=0, both bad disjuncts are false forever under zero inputs; any
nonzero input reaches an active reachable state. If s != 0 and r=0, the
second bad disjunct is immediately true under every input, so exclude it.
If r and s lie on distinct nonzero orbits, zero inputs never produce a match
or zero register; a reseed reaches R. Both counter values are safe.

Finally suppose r=A^t s, 0<=t<T_s. Under zero inputs the first imminent return
occurs after T_s-1-t transitions. Before that time c is toggled at every step.
At that time the counter is

    c XOR ((T_s-1-t) mod 2) = c XOR (t mod 2).

The bad detector fires exactly when c differs from t mod 2. With correct
parity the return resets to (s,s,0), from which every input sequence is safe.
Thus incorrect parity has a zero-input counterexample within T_s clock
evaluations, while correct parity is safe against all inputs.

S is the greatest transition-closed subset on which all input-labelled bad
detectors are false. In particular every ordinary state-only inductive safety
invariant I satisfies R subset I subset S.

The source-specific distinction R != S matters: unreachable states with s=0
and r != 0 may be added by an inductive invariant. One must not assert that
every invariant equals the reachable set globally.

## 4. What every state-only invariant must encode

If A is primitive, its nonzero states form one cycle of length M=2^n-1. Then
for EVERY pair r,s != 0 exactly one counter value belongs to any state-only
inductive safety invariant I:

    I(r,s,c)  iff  c = t_s(r) mod 2      [r,s != 0].

This follows without assumptions about I's syntactic form: the correct value
is reachable, and the wrong value has a future all-zero-input error.
The same statement holds for same-orbit pairs for any odd-order A.

For a primitive field multiplication map r=alpha*r, fixing s=1 makes t_s(r)
the canonical discrete logarithm. Thus evaluating I(r,1,0) yields its parity.
For a companion implementation, a cyclic Krylov basis transports this statement
to F_2[X]/(f); basis construction is ordinary polynomial-time linear algebra.

An exact parity oracle yields the complete canonical phase by an elementary
deterministic reduction directly on vectors; no field representation is needed.
Let M be the known odd point period, r=A^t s, 0<=t<M, and e(t)=t mod2. For
0<=k<M,

    e((t+k) mod M) XOR e(t) XOR (k mod2) = [t >= M-k].

Indeed, reducing t+k modulo the odd M flips its parity exactly when the sum
wraps. An invariant query at (A^k r,s,0) returns the complement of the shifted
parity. For any threshold b in {1,...,M-1}, use k=M-b to decide whether t>=b.
Binary search recovers t using one base query and at most ceil(log2 M) shifted
queries; A^k r is computed by repeated matrix squaring. This needs no noisy
prediction or hard-core-bit theorem. It applies on any same-orbit pair whose
odd point period is known, including the primitive family with M=2^n-1.
In particular, it reduces the full finite-field discrete logarithm to invariant
evaluation when A represents multiplication by a primitive field element.

Consequences and limits:

* A uniformly efficiently constructible/evaluable family of these state-only
  invariants gives a uniform polynomial-time DLP algorithm for that family.
* Polynomial-size invariant circuits for a fixed primitive family imply
  corresponding nonuniform DLP circuits for that family through the reduction.
  This is not a proven superpolynomial circuit or CNF lower bound.
* Formula size, construction cost, evaluation cost, and proof-validation cost
  must not be conflated. There is no unconditional cryptographic hardness
  conclusion, and no obstruction to explicit small-width invariants.
* Characteristic-two DLP already has expected quasi-polynomial algorithms;
  these LFSRs must not be advertised as secure cryptographic instances.

This identifies a real interface constraint: a short source-level algebraic
safety proof need not immediately yield an efficiently evaluable invariant
over ONLY the original state bits.

## 5. History-counter witness for the primitive case

Assume every nonzero s has exact period M, not merely that A^M=I. Introduce a
fresh history register t with values 0,...,M-1, initialized to zero. Its update
is total and does not constrain original inputs or state updates:

    t'=0 on u!=0, on s=0, or on m;
    t'=t+1 modulo 2^n otherwise.

Use the extended invariant H:

    (r=s=0 and t=0, with c unrestricted)
       OR
    (s!=0 and 0<=t<M and r=A^t s and c=t mod2).

Initiation is immediate. Reseeding gives t=0. In an active state, exact period
M gives m iff t=M-1. At that phase M-1 is even, so c=0 and the return resets
all necessary values. Otherwise t<M-1, the increment and parity toggle
preserve H. This proves inductiveness and safety.

The original execution has a unique lifted history run from t=0. Forgetting
t gives exactly the original transition behavior, so this is a conservative
history-variable extension, not a restriction of the workload. An interface
that restricts original inputs using ghost equations would not implement this
contract. The existentially quantified original-state predicate `exists t: H`
is mathematically an invariant too, but evaluating it without a supplied history
value again recovers the phase-parity problem. The efficient claim concerns
the extended predicate with t present as an actual state component.

For M=2^n-1 the register has n bits. Precompute constant matrices
A^(2^0),...,A^(2^(n-1)). A conditional sequence of matrix-vector products
evaluates A^t s with O(n^3) naive Boolean gates. Hence H has a polynomial-size
Boolean circuit, without computing t from (r,s,c).

This does not establish cheap independent validation in a native proof format.
A bit-blasted SAT checker still has to establish no early return for all
nonzero s and all 0<t<M. Algebraic maximal-period evidence can prove that
claim, but the argument does not imply a uniform polynomial SAT-proof bound
or fast replay at larger widths. The native record supplies the measured
small-width outcomes separately.
The interface must also justify adding history latches; purely definitional
combinational Tseitin nodes cannot manufacture t without the parity problem.

## 6. Why an odd multiple is insufficient for the simple history predicate

The existing checker proves A^M=I for an odd M and deliberately does not prove
minimal or uniform point period. Under that weaker contract H need not even
imply safety. For A=I, M=3, s!=0, r=s, t=1, c=1, the active clause of H holds,
but m is true and a zero input makes bad true immediately.

For arbitrary odd-order matrices a direct phase witness needs the exact
seed-dependent period T_s, or a no-earlier-return condition. A bounded phase
modulo a convenient global multiple silently adds false states. Therefore the
primitive ghost-counter route requires an explicitly stronger, independently
checked source contract. The existing source-level odd-order proof retains
its advantage of avoiding maximality and factorization.

## 7. Independent finite checks performed

`verify_theory.py`, independent of the symbolic AAG checker, examines all binary
matrices in dimensions 1,2,3 and selects all odd-order invertible ones:
1,3,105 matrices respectively. For each of these 109 matrices it independently
computes (a) the reachable set by BFS over all inputs and (b) the maximal safe
set by backward bad-attractor computation over all states and inputs. Both sets
agree exactly with Sections 2 and 3. All singular matrices in that finite
enumeration have a nonzero kernel seed and an actual bad trace, as required.

For primitive companion maps of widths 2,3,4 it additionally checks both exact
sets, every input-labelled edge of every H-state, all underlying extended
states against the intended phase predicate, and full DLP recovery for every
nonzero pair (r,s). It includes the identity/M=3 counterexample to the weakened
ghost contract. These are small-instance checks; the arguments above establish
the general claims.

## 8. Primary-source context, not a novelty audit

* C. P. Schnorr, Security of Allmost ALL Discrete Log Bits, ECCC TR98-033:
  https://eccc.weizmann.ac.il/report/1998/033/
  The report studies bit security in polynomially encoded cyclic groups and
  explicitly discusses odd group order and least-significant bits. The exact
  oracle reduction used here is supplied above and makes no stronger noisy-bit
  security claim.
* Thorsten Kleinjung and Benjamin Wesolowski, Discrete logarithms in
  quasi-polynomial time in finite fields of fixed characteristic, Theorem1.1:
  https://arxiv.org/html/1906.10668v2
  It gives expected (pn)^(2 log_2 n+O(1)) time, hence expected quasi-polynomial
  time for fixed characteristic, including two. This rules out language
  suggesting an established exponential lower bound.
* Guido Lido, A provably quasi-polynomial algorithm for the discrete logarithm
  problem in finite fields of small characteristic:
  https://arxiv.org/abs/2206.10327
  Further primary context; not needed for the elementary exact-oracle proof.

The source-aware squarefree-polynomial route has the same opportunity to use
checked history extensions once the stronger common-period premise is supplied.
Nothing here establishes a separation from that comparator. The relevant
experiment is whether a concrete existing proof interface can validate this
history witness and source binding at useful cost. If only original-state
CNF/AIG invariants are accepted, that limitation must be explicit rather than
promising an automatically compact translation of the source proof.
