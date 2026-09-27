# Why the original safety property needs only odd order

All vector arithmetic is over GF(2). Let r be the running n-bit register, s the
saved seed, c the one-bit counter, and u the current input. Let A be the linear
map extracted from the raw gates. Put z = [u = 0] and
m = [s != 0 and Ar = s]. Exact replay checks these equations:

| Signal | Required expression |
|---|---|
| r' | Ar if z, otherwise u |
| s' | s if z, otherwise u |
| c' | (not c) and z and (not m) |
| bad | (z and c and m) or (s != 0 and Ar = 0) |
| Initial state | r = 0, s = 0, c = 0 |

In particular, the second bad-state disjunct is **not** gated by z in the
original circuits. The proof below covers it as written; replacing it with a
more convenient expression would change the problem.

## Sufficient certificate

Suppose an odd positive integer M satisfies A^M = I. Then A is invertible and
every point period divides M, so each point period is odd.

Before the first nonzero input, r = s = 0. Both bad-state disjuncts are false,
regardless of c. A nonzero input makes the next state r = s = u and c = 0.
After this reset, s is nonzero and r stays nonzero until the next reset, because
A is invertible. Hence the second bad-state disjunct cannot hold, even during
a reseeding step.

Fix a segment with no reseeding and let T be the least period of its nonzero
seed. At the beginning of each traversal r = s and c = 0. After j transitions,
for 0 <= j < T, r = A^j s and c is the parity of j. The imminent return test m
first holds at j = T-1. Since T is odd, j is even and c = 0, so the first
bad-state disjunct is false. The next state has r = s and c = 0 again. This
proves safety for arbitrarily many traversals and arbitrarily many resets.
The period-one case is included: m holds immediately and c remains zero.

Only the displayed identity is required. No assertion that M is minimal or that
all nonzero seeds have the same period is used.

## Conventional source-aware decision

For an invertible binary matrix, odd order is equivalent to a squarefree minimal
polynomial. If the order M is odd, the minimal polynomial divides X^M-1, whose
derivative is X^(M-1), coprime to X^M-1. Conversely, distinct irreducible factors
of degrees d_i each divide X^(2^d_i-1)-1; their product divides X^L-1 for the odd
integer L = lcm_i(2^d_i-1). Thus a squarefree minimal polynomial with nonzero
constant term implies odd order.

For the supported companion matrix, its minimal and characteristic polynomials
coincide. With tap bits t_i and the actual raw-gate coordinate order, that
polynomial is

```text
f(X) = X^n + sum_(i=0,...,n-1) t_i X^(n-1-i).
```

This is the reciprocal of the feedback-polynomial convention printed in the
upstream comments. For example, raw width 4 with taps 0xC has
f(X) = X^4 + X + 1, whereas the comment prints X^4 + X^3 + 1. Both conventions
give the same squarefreeness test when the constant term is nonzero. The
comparator uses the exact raw-gate convention, checks f(0) != 0, then computes
gcd(f,f') = 1 with packed binary polynomial Euclidean arithmetic. It does not
factor f or compute any period.

This establishes a strong comparator and a boundary on research claims: the
published task does not require the existing full orbit engine. A source-bound
odd-exponent certificate is a small certifying integration of established
structure. Native model-checker difficulty alone would not make the algebra new.

## Structural proof replay

The checker assigns distinct Boolean variables to the original inputs/latches
by position and evaluates every AND gate in topological order. Boolean values
are interned DAG nodes with complemented edges. Normalization uses conjunction
associativity/commutativity/idempotence, constants, complementary literals,
double negation, XOR associativity/cancellation, and the identity

```text
not(a and b) and not((not a) and (not b)) = a XOR b.
```

Each rewrite is a Boolean identity. The expected wrapper is built in the same
normalizer. Identical final node IDs therefore prove equality; failure to obtain
identical IDs proves nothing. Every latch and the output must match. These
checks establish source binding without trusting names or commentary. The
independent raw evaluator checks all transitions of the three smallest fixtures
and directly finds unsafe traces for deliberately broken raw-circuit controls.
