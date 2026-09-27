# Seed-dependent phase bounds from an odd order multiple

27 September 2026. No new algorithmic or proof-system novelty is claimed.
The associated native experiment has a separate input/output contract.

## Contract and exact extraction

Trusted source semantics are the existing LFSR wrapper. The theorem below holds
for any binary n-by-n matrix A with A^M=I for an odd positive M. Construction is
additionally given a complete factorization M=product_i p_i^e_i with distinct
primes p_i and positive exponents e_i. This is
additional proof/construction data, not a restriction on the source's behavior
or an assertion of maximality. Acquiring it has an explicit cost.

The implemented raw-source adapter recognizes the specific companion-map AAG
wrapper already documented in the repository. The general matrix theorem does
not expand that source contract to arbitrary circuit graphs or linear maps.
An accepted artifact must still bind all original latch updates, initialization,
inputs and the bad detector through the existing native proof interface. The
extra history register changes the witness only; it does not modify the source.

For each i and k=1,...,e_i, precompute the constant matrix

    B_i,k = A^(M / p_i^k).

Define the seed predicate b_i,k(s)=[B_i,k s=s], and the combinational scalar

    P(s) = product_(i,k) (1 if b_i,k(s), otherwise p_i).

Then P(s) is the exact point period of EVERY seed s, including P(0)=1.

Proof: write T_s for the least point period. The source premise implies
T_s divides M. For any divisor D of M, A^D s=s iff T_s divides D. Consequently
b_i,k is true iff v_(p_i)(T_s) <= e_i-k. Exactly v_(p_i)(T_s) of the e_i
predicates are false. Multiplying their p_i contributions gives precisely T_s.
This handles repeated primes, unnecessary prime factors in M, excessive prime
powers, period-one seeds, and multiple distinct seed orbits. No discrete
logarithm, orbit enumeration, adaptive variable-exponent test, or irreducible
decomposition is needed once the factorization has been supplied.

Each b_i,k is membership in ker(B_i,k-I). Row reduction and canonical sharing
of identical kernel tests preserve its Boolean meaning. Empty row space gives
the constant true predicate, including powers that already annihilate all A.

## History extension

Let L=max(1,ceil(log2 M)); for odd M>1 this equals M.bit_length(). Using one
bit also for M=1 avoids zero-width implementation conventions. Add an L-bit
history register t initialized to zero, leaving all original inputs, latches,
updates and the original bad detector intact. Write

    m = [s != 0 and Ar=s].
    t'=0 if u != 0 or s=0 or m;
    t'=t+1 modulo 2^L otherwise.

Use H:

    (r=s=t=0, c arbitrary)
        OR
    (s != 0, 0 <= t < P(s), r=A^t s, c=t mod2).

Initiation is immediate. Reseeding establishes the active case with t=0.
On a zero-input active step, s and therefore P(s) remain constant. Because
P(s) is the exact period, m iff t=P(s)-1. This value is even because P(s)
is odd, so c=0 and originalbad is false at the imminent return. The return
sets t'=0, r'=s and c'=0. Otherwise t<P(s)-1; t increments without overflow,
r advances by A and c toggles. Nonzero r is preserved because A is invertible.
Thus H is inductive and implies the original bad detector is false for every
input, including its ungated zero-register disjunct.

The history update is total. Every original input/state execution lifts uniquely
from t=0; projection discards t and recovers exactly the original execution.
The witness is a conservative extension, not an input constraint.

This changes the previous primitive witness only by replacing constant M in
its bound with the combinational P(s), and sizing t from M rather than n.
The existing verifier's witness format and source-binding obligations remain
the same. The source-aware ordinary algebra route has the same opportunity.

## Circuit and construction costs

Put E=sum_i e_i. Since every prime is odd, E=O(L), and
sum_i e_i bit_length(p_i)=O(L).

* Kernel tests: E fixed n-by-n binary linear maps and equality checks cost
  O(n^2 E) naive Boolean gates; row reduction/sharing may reduce this.
* Period scalar: starting from one, conditionally multiply by fixed p_i on
  each false kernel predicate. A constant multiplier built from shifts and
  additions costs O(L bit_length(p_i)); the mux costs O(L). Summing over all
  repetitions gives O(L^2). Every partial product divides M, so L bits suffice
  without arithmetic overflow for every assignment of the predicate bits.
  If an implementation instead uses a generic L-by-L multiplier per predicate,
  the justified bound is O(L^3), not the tighter constant-multiplier bound.
* A^t s: controlled applications of the L constant powers A^(2^j) cost
  O(n^2 L) naive Boolean gates. Equality, scalar comparison, and ghost-counter
  updates add polynomially smaller terms.

Thus the tight elementary implementation is O(n^2 L+L^2) gates after matrix
constants are available. Precomputing E powers by ordinary repeated squaring
costs O(E n^3 L) naive bit operations, separately from factoring M.

Factoring an arbitrary M is not asserted to be polynomial time. A polynomial
construction bound is conditional on receiving its complete factorization.
For an executable small gate, bounded trial division (e.g. M below 2^24) is
an explicit charged construction choice, not a hidden free oracle. Complete
prime factorization can be independently checked, but it need not be added
to the trusted native proof interface: the final candidate witness and every
precomputed matrix are untrusted artifacts, and the existing independently
checked induction proof establishes the delivered result. Wrong factor data
does not automatically mean an invalid witness on every special source;
acceptance must depend on actual proof obligations, never factor labels.

## Minimal controls and predicted behavior

1. Width 3 rotation, taps 0x4, characteristic X^3+1, M=9=3^2. Its nonzero seeds
   have periods {1:1,3:6}. Tests are A^3s=s (always true), then As=s. This
   checks both period-one seeds and an excessive prime-power bound.
2. Width 5 taps 0x11, characteristic (X^2+X+1)(X^3+X+1)=X^5+X^4+1,
   M=63=3^2*7. Its nonzero seeds have periods {3:3,7:7,21:21}. Tests are
   A^21s=s, A^7s=s, A^9s=s. The selected product yields 3, 7 or 21.
3. Published width 8 taps 0xB8, M=255=3*5*17. All nonzero seeds have period 255;
   this supplies a matched comparison with the previous primitive witness.

Negative controls:

* Omitting the second repeated-prime test for width 3 / M=9 makes P=1 for all
  seeds. Nonfixed seeds then violate induction on the first ordinary step.
* Treating 9 as a single prime factor makes P=9 on nonfixed width 3 seeds.
  H admits the wrong-parity state r=s,c=1,t=3, which is not immediately bad
  but reaches bad after further zero inputs. The native inductiveness check
  must fail for a witness with bad=originalbad OR NOT H.
* Increasing selected P(s) can admit bad phases; concrete controls must verify
  an actual native obligation failure rather than infer it from H alone.

The last caveat matters: if the native witness's actual invariant is H AND
NOT originalbad, merely observing an immediately bad state in H does not prove
that the actual witness is invalid. For example, identity A with M=3 refutes
H-alone under the naive constant bound, yet the strengthened witness may still
be inductive. The period 3 / M=9 control avoids that ambiguity.

## Independent finite controls

`verify_theory.py` uses no producer code, no kernel row reduction, and no
symbolic AAG normalizer. It enumerates all binary matrices in dimensions 1, 2,
and 3, selects the 109 invertible odd-order cases by explicit finite cycles,
and tests M equal to the exact matrix order multiplied by 1, 9, and 25. The
control set includes M=1, identity matrices, nonminimal annihilators, repeated prime powers,
and extra prime factors. It obtains true seed periods by direct iteration,
evaluates each fixed-power predicate by separate literal repeated stepping,
and compares the factor product against the true period for every seed.

For every such case it checks every H-state against the independent orbit
phase table and every input-labelled transition from H. Separate companion
controls check the planned width 3 / M=9, width 5 / M=63, and published width 8 / M=255
period distributions. Incorrect omission/composite-factor controls are verified
to produce future induction failures, not merely immediately bad states that
the native witness could exclude. Small finite checks do not replace the proof.

## Remaining limitation

This removes the semantic maximal-period premise, but does not establish that
the larger variable-bound invariant has short LRAT/RUP proofs or useful native
checking cost. Those are the falsifiable next measurements. No comparably simple
factorization-free polynomial-size witness under only the odd-order premise
has been established; that is a statement of what was found, not an impossibility
claim. The direct squarefree source-safety argument remains a simpler mathematical
baseline, and receives equal access to the same native witness interface.
