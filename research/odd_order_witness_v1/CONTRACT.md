# Seed-dependent periods in the existing witness interface

The independently supplied problem is the complete raw AIGER model. Inputs
remain unrestricted, including arbitrary nonzero reseeding. Its zero resets,
all latch updates and full bad-output logic are those of the previously
specified LFSR wrapper. The old production API and both earlier research
checkpoints are unchanged.

The untrusted producer takes the model, a companion tap mask and a positive
odd exponent M. It checks the supported wrapper and A^M=I, factors M by exact
trial division, and emits an ordinary Certifaiger witness. Its implementation
is bounded to widths 2 through 24 and M<2^24. Obtaining and checking the complete
factorization is construction work; the general polynomial circuit-size bound
does not make factorization a free or polynomial-time operation.

## The changed predicate

For each prime power p^e exactly dividing M, and each k=1,...,e, form the fixed
binary matrix B[p,k]=A^(M/p^k). Define the seed-dependent value

```
P(s) = product over (p,k) of (1 if B[p,k] s = s else p).
```

Every seed period T_s divides M, and exactly v_p(T_s) of the tests for p fail.
Thus P(s)=T_s, including P(0)=1. Neither M nor the nonzero seed periods need be
maximal or equal. Row reduction of each fixed B[p,k]-I gives an equivalent
kernel test; sharing those tests is a producer-side simplification fixed before
the native experiment.

The witness copies and explicitly maps every original input and latch. It adds
L=max(1,bit_length(M)) zero-initialized history bits t. The history resets to zero
on nonzero input, inactive seed, or an imminent return; otherwise it increments
modulo 2^L. Its strengthened bad output is original_bad OR NOT H, with

```
H = (r = s = 0 AND t = 0)
    OR (s != 0 AND t < P(s) AND r = A^t s AND c = t mod 2).
```

The inactive branch leaves c unrestricted. As in the earlier construction,
controlled fixed matrix powers evaluate A^t s. Fixed-prime shift/add circuits
and multiplexers build P(s), with no variable division or discrete-log search.
THEORY.md proves the selector, initiation, induction, safety and size bounds.
The general theorem includes M=1; a one-bit history and P=1 suffice. The
restricted companion frontend need not represent an identity matrix.

## Acceptance and comparison

Producer checks and successful construction are not safety acceptance.
Certifaiger receives the model and witness separately and must discharge all
applicable simulation, safety and induction obligations. Every completed
accepted CNF proof is independently replayed using the unchanged positive-hint
LRAT checker from the preceding checkpoint. Rejection, timeout, resource limits
and unsupported syntax never establish that the source is unsafe.

There are no new trusted algebraic rules in this interface. Certifaiger's
mapping/obligation construction and the AIGER-to-CNF transformation retain
their previous trust boundary. The Python constructor, its factorization and
its matrix simplifications are untrusted by native acceptance.

Two explicitly synthetic wrapper models exercise mixed seed periods and a
nonminimal annihilator; they are semantic controls, not newly found published
benchmarks. The one unchanged published model supplies the matched comparison.
The earlier maximal-period producer legitimately reports unsupported scope on
the synthetic controls. That is not a solver failure or a speedup baseline.

This is ordinary order extraction from a factored multiple compiled into an
existing history-witness format. Conventional source-aware methods have the
same construction available. No new algebra, new proof system, general
factorization-free algorithm, performance advantage or publication originality
is implied by removing the former maximality premise.
