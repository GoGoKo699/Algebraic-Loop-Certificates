# Composing exact orbit certificates across modular precision

Research note, 26 September 2026. This is a proof and experimental specification,
not a manuscript. The primary package remains unchanged. The purpose is to
transfer a complete prime-field certificate system to actual integer residue
rings without pretending that a composite modulus defines a field.

## 1. Exact mathematical problem

The input is an explicitly encoded integer N >= 2, a d-by-d matrix A, translation
c, initial state a and full-state target b, all over Z/NZ. Assume det(A) is a unit
modulo N. Define F(x)=Ax+c. The question is the complete set of nonnegative
iteration counts for which F^t(a)=b.

Invertibility makes every point orbit a pure cycle. Therefore the answer is
empty or one progression t0+r*j with 0 <= t0 < r and j >= 0, where r is the
least point period. An arbitrary Boolean guard, a singular map, an external
input, or a program with branch-dependent updates is a different task.

N=2^w models fixed-width modular addition and multiplication by constants. It
is not the extension field F_(2^w), and the proof never uses a field inverse of
a nonunit residue. Mixed word widths, language-level undefined overflow, signed
comparisons, shifts, XOR mixed with addition, memory access, and a full program
frontend are not covered merely by naming an integer modulus.

## 2. Precision-fiber lemma

Suppose p is prime and, modulo p^k, the complete hit set is t_k+r_k*j with
0 <= t_k < r_k. Work now modulo p^(k+1), and compute

    y0 = F^(t_k)(a),
    F^(r_k)(x) = B_full*x + c_full.

The lifted initial point y0 reduces to b modulo p^k. It also returns to itself
under F^(r_k) modulo p^k. Hence these coordinate-wise integer divisions are exact:

    target_digit = (b-y0)/p^k mod p,
    defect_digit = (F^(r_k)(y0)-y0)/p^k mod p.

All values on the right are computed modulo p^(k+1) using canonical integer
representatives; using negative differences before division does not change the
result after reduction modulo p. Put B = B_full mod p = A^(r_k) mod p.

**Lemma.** Starting at z_0=0 over F_p, the affine recurrence

    z_(j+1) = B*z_j + defect_digit

satisfies

    F^(t_k+r_k*j)(a) = y0 + p^k*z_j mod p^(k+1)

for every j >= 0. Consequently the higher-precision target is reached at such
an iteration exactly when z_j=target_digit.

**Proof.** The assertion at j=0 is the definition of y0. For an arbitrary z,
affinity gives

    F^(r_k)(y0+p^k*z)
      = F^(r_k)(y0)+p^k*B_full*z
      = y0+p^k*(defect_digit+B*z) mod p^(k+1).

Induction proves the identity. The lower-precision completeness assertion
implies that every possible higher-precision hit already has this time form.
Thus the equivalence loses no candidate iterations. B is invertible over F_p
because A is invertible modulo p. The derived problem is in the exact domain
of the existing complete finite-field certificate system. QED.

The lemma is elementary lifting algebra. Its use here is an explicit certificate
composition contract; a novelty claim requires comparison with prior modular
orbit and logarithm algorithms, not the absence of an identical notation.

## 3. Exact update of the offset and least period

If the derived field problem is unreachable, no hit exists modulo p^(k+1).
Otherwise suppose its complete schedule is j=j0+s*q, 0 <= j0 < s. Set

    t_(k+1) = t_k+r_k*j0,
    r_(k+1) = r_k*s.

Substitution in the precision-fiber lemma gives the complete higher-precision
hit set. The offset is canonical, because t_k<r_k and j0<s.

For least-period correctness, consider the higher-precision orbit starting at
y0. Its reduction modulo p^k has period r_k, so every return time must be a
multiple of r_k. Among those multiples, the lemma identifies returns exactly
with returns of the field state z_0=0. Its least period is s. Hence the least
period of y0 is r_k*s. Since y0=F^(t_k)(a) and F is invertible, a has the same
point period. This establishes minimality, not merely an upper bound.

**Point periods must not be confused with matrix orders.** For F(x)=2x modulo
25 and a=5, the point is fixed modulo 5 but has period four modulo 25:

    5 -> 10 -> 20 -> 15 -> 5.

The ratio is 4, not 1 or 5. For target20, the lifted field problem is
z -> 2z+1 over F5, from0 to3, whose schedule is 2 mod4. This does not contradict
the standard order-lifting lemma for a multiplicative unit: the initial point
5 is not a unit, and the matrix multiplier's order is a different quantity.
The concrete counterexample prevents an unsound shortcut in point-orbit code.

## 4. Complete certificate chain for a prime power

For modulus p^e:

1. Check a full prime-field decision certificate at precision1.
2. If negative, terminate the local proof with that negative answer.
3. Otherwise derive the next field problem from the checked schedule and the
   original modular input, not from an untrusted proposed quotient instance.
4. Check its certificate and update the schedule as above. Repeat through e.

At most e field certificates are needed. Every derived input is computable by
binary powering; no loop of length r_k is necessary. Negative layers can occur
above precision1. For example, x -> x+4 modulo8 from0 cannot reach2: the target
is reachable modulo2 but not modulo4. The corresponding second field problem
certifies the obstruction.

**Soundness and completeness.** Induct on precision. The base is the sound,
complete prime-field proof system in ../complete_orbits_v1/THEORY.md. The lemma
and least-period result transfer its conclusions in either direction at every
step. For any valid instance, each derived field problem has a polynomial-size
certificate of its correct answer. Thus every prime-power instance admits a
finite complete proof chain. This is certificate completeness, not a claim that
a bounded reference producer always finishes or that discovery is polynomial.

## 5. General integer moduli

Supply a complete prime-power factorization N=product_i p_i^(e_i), together
with recursively checked primality certificates. The ring CRT identifies a
state modulo N with its reductions modulo every prime power.

Check a local chain for each prime power. If any local answer is empty, the
original hit set is empty. Otherwise intersect the local schedules using the
generalized integer CRT. Local moduli here are the *point periods*, which need
not be coprime even though the ring factors are coprime.

A conflict between residues gives an exact negative result. For example,
multiplication by11 modulo12, starting at1 and targeting5, requires even time
modulo4 and odd time modulo3. Each local target is attainable, but there is no
common iteration. A feasible intersection has the least common multiple of
the local periods and the canonical combined offset. This is the least global
point period by the ring CRT and invertibility.

The checker verifies a supplied inverse matrix by two products modulo N. It
does not perform ordinary field Gaussian elimination over Z/NZ. The reference
producer uses exact rational inversion followed by modular reduction; this
handles invertible matrices such as [[2,3],[3,2]] modulo6, whose first column has
no unit entry. A production implementation could use more efficient modular
inversion; none is assumed for the comparison.

## 6. Certificate size and checking complexity

Let L=ceil(log2(N+1)). The total number of field subproblems is at most
sum_i e_i <= log2 N. Each has d state coordinates and prime bit length at most L.
Its coefficients are computed from d-dimensional affine matrix powers at
exponents whose bit length is O(dL), since every point period is <=N^d.
The wrapper's arithmetic therefore has polynomial bit complexity in d and L.

Let P(d,l) and V(d,l) denote polynomial bounds for the size and deterministic
checking time of the prime-field certificates. The complete modular proof has
size at most

    poly(d,L) + sum_i e_i*P(d,log p_i),

and checking time at most

    poly(d,L) + sum_i e_i*V(d,log p_i).

These bounds include supplied integer factorization and primality proofs, not
free factorization calls. They are not claimed optimal exponents. All nested
certificates may repeat their elementary prime proofs; deduplication is optional.
The prototype enforces additional practical size limits. Raising those limits
preserves the mathematical algorithm but can make verification expensive.

**A useful fixed-parameter consequence.** For fixed d and fixed p, the derived
field problem has a bounded finite description space. A correct exhaustive or
algebraic field solver has a cost depending on d,p but not e. Thus prime-power
point-orbit construction can be polynomial in e for fixed d,p. This is not a
new uniform polynomial-time discrete-logarithm algorithm, and we do not claim
priority for this consequence. It explains why a large word width alone must
not be presented as a hard classical problem.

## 7. What is implemented, and what is deliberately absent

- `lifting.py` validates the modular problem/certificate, verifies prime factors,
  constructs every field problem, checks it, and combines schedules. It imports
  no producer and never enumerates an orbit.
- `producer.py` calls the existing reference finite-field producer with a shared
  effort budget; it supplies a candidate or UNKNOWN. This is no more a new fast
  discrete-logarithm algorithm than the underlying field producer.
- `check.py` uses separately written ordinary modular steps to establish truth
  for the small controls. Only the test oracle enumerates trajectories.

The experimental schemas are `alc.modular-problem.v1` and
`alc.modular-decision.v1`. They are NOT `alc.problem.v1` or
`alc.certificate.v1`. Production parsers should continue to reject these inputs.
A wrapper certificate supplies a complete modulus factorization, prime proofs,
an inverse witness, one ordered field-proof list per prime factor, and an
asserted final outcome. Derived layer matrices and targets are not supplied as
trusted data. Each field proof is bound to the input the checker computes.

The implementation supports mathematical modular affine recurrences, not a
sound source-language translator, arbitrary safety guards, singular recurrences,
or a proof assistant formalization. There is no claim that native bitvector
solvers require enumeration or that the example improves on them.

## 8. Exact consequence for a point-guard loop

For the explicitly stipulated operational program

    x := a
    while x != b:
        x := A*x+c mod N

where the test occurs before the body and the vector comparison is exact,
a reachable certificate proves termination after exactly t0 body executions.
An unreachable certificate proves nontermination. The proof is immediate from
the complete hit-set theorem: the guard first becomes false at the least hit,
or never does. The result has no hidden fairness, nondeterminism or environmental
assumptions because this program is deterministic and has only that guard.

`consumer.py` rechecks the modular certificate before returning this conclusion
or a time-window count. It does not claim that arbitrary source code was
translated faithfully into the stipulated loop. This is a useful scoped consumer,
not a new theorem of general program termination or a verified frontend.

## 9. Prior work and remaining significance question

Scalar discrete-logarithm lifting is established: Viglietta and Kachi [R2]
explicitly improve Bach's 1984 lifting algorithm. Their scalar unit-group
setting is different from an arbitrary initial vector of an affine matrix
recurrence. Our point-period counterexample must not be advertised as a flaw
in that scalar result. Its optimized scalar approach belongs in future matched
performance comparisons.

Finite-ring dynamics also has direct classical predecessors: Xu and Zou [R3],
Wei, Xu and Zou [R4], and Kantic et al. [R1]. The last studies cyclic modules over
Galois rings and algorithms for sets of cycle lengths and transient heights.
Its cycle-analysis objective is not identical to a fixed-target complete hit
schedule, but a different objective alone does not establish that our algorithm
or proof format is original. Its Section4 also declares prime-factorization
lookup assumptions; do not transfer its runtime to an access model without them.

The defensible current claim is a proved and implemented certificate-composition
mechanism with explicit modular semantics. Whether it supplies a new research
contribution beyond those algorithms and established certifying computation
remains a priority and consumer-comparison question. Research is not declared
publication-ready from this implementation alone.

## Primary sources and reading scope

[R1] Kantic, Qureshi, Panario, Legl. On the Dynamics of Linear Finite Dynamical
Systems Over Galois Rings. arXiv:2604.01548v1, 2 April 2026. Full HTML inspected,
including Sections2,4 and the algorithm/access assumptions. No native code run;
no claim to reproduce every theorem. https://arxiv.org/html/2604.01548v1

[R2] Viglietta, Kachi. Efficient Lifting of Discrete Logarithms Modulo Prime
Powers. arXiv:2505.07434v1, May2025. Full HTML, algorithm and correctness setup
inspected; optimized published algorithm not run. https://arxiv.org/html/2505.07434v1

[R3] Xu, Zou. Linear Dynamical Systems over Finite Rings. arXiv:0810.3164 /
Journal of Algebra321(2009),2149-2155; DOI10.1016/j.jalgebra.2008.09.029. Primary abstract inspected; not a complete
proof comparison. https://arxiv.org/abs/0810.3164

[R4] Wei, Xu, Zou. Dynamics of Linear Systems over Finite Commutative Rings.
AAECC27,469-479(2016), DOI10.1007/s00200-016-0290-y; arXiv:1709.08579 was deposited in2017. Primary abstract and publisher metadata inspected; full algorithm audit still required.
https://arxiv.org/abs/1709.08579

[R5] SMT-LIB, FixedSizeBitVectors, official theory specification, inspected
26 September2026. Supports the exact unsigned modular add/multiply semantics,
not a claim about every source language's overflow rules.
https://smt-lib.org/theories-FixedSizeBitVectors.shtml

[R6] Hull, Dobell. Random Number Generators. SIAM Review4(3),230-254(1962),
DOI10.1137/1004061. Primary publisher page inspected. The chosen 5*x+1 modulo
2^64 example is an established full-period case, not a discovered generator.
https://epubs.siam.org/doi/10.1137/1004061
