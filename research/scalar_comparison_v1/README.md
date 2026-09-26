# A native scalar comparator, not an enumerative strawman

This audit compares the experimental modular certificate construction with a
classical scalar-affine reduction using the public SymPy 1.14.0 `n_order` and
`discrete_log` functions. It is a comparator, not a new algorithmic contribution.
The original larger matrix problem is not reduced to this scalar benchmark.

## Exact reduction

Consider `x <- A*x+c mod N`, with canonical integer data, `N>=2`, and
`gcd(A,N)=1`. If `A=1`, solve `c*t = b-a mod N` by gcd cancellation. This gives
an empty set or a complete progression with period `N/gcd(c,N)`.

For `A>1`, work temporarily modulo `L=N*(A-1)`, and define

    u=(A-1)*a+c,   v=(A-1)*b+c.

Iteration satisfies

    (A-1)*F^t(a)+c = A^t*u mod L.

The map from `x mod N` to `(A-1)*x+c mod L` is injective, and intertwines the
original affine update with multiplication by A. Let `g=gcd(u,L)`. If `g`
does not divide v, no hit is possible. Otherwise divide the congruence and its
modulus by g. With `M=L/g`, the resulting input `u/g` is a unit modulo M.
For `M>1`, the target equation is

    A^t = (v/g)*(u/g)^(-1) mod M.

If its right-hand side is a nonunit there is no solution. Otherwise the native
modular logarithm routine supplies a candidate offset, or reports no logarithm.
Its least period is the native multiplicative order of A modulo M. For `M=1`
the original point is fixed. The correspondence is injective, so the least
multiplicative order is exactly the least point period, not merely a multiple.
No inverse of `A-1 mod N` is assumed: that inverse need not exist. Initial
nonunits, such as a=5 modulo25, are supported. The expanded modulus has O(log N)
bits for canonical A, not exponentially many input bits.

This elementary reduction is derived here as a fair comparator, not claimed
new. The APIs are documented at:
https://docs.sympy.org/latest/modules/ntheory.html#sympy.ntheory.residue_ntheory.discrete_log
https://docs.sympy.org/latest/modules/ntheory.html#sympy.ntheory.residue_ntheory.n_order
The former already chooses among trial, baby-step/giant-step, Pollard, index-
calculus and Pohlig-Hellman methods. Both methods get the same mathematical
input and no externally supplied factorization, order, or logarithm hints.
The two native calls may duplicate work; this is not the optimal possible
scalar implementation. The checker for the certificate path never calls SymPy.

## Fixed experiment and interpretation

`check.py` exhausts 13,602 scalar cases for moduli 2 through10. It independently
steps each small orbit. For all moduli through6, it also constructs and checks
the experimental modular certificate: 1,122 paired cases. Mathematical outputs
are stored separately from hardware-dependent timings.

Six displayed cases were specified before measuring: affine congruential maps
`5*x+1` modulo `2^16`, `2^32`, and `2^64`; one nonunit-start example modulo25;
and two negative cases modulo12 and8. The three targets are constructed at
`2^(w-1)+123`. This is not the previous checkpoint's `+123456789` example.
Constructing targets and module imports are excluded equally from both timing
paths. The purpose is calibration, not evidence of naturally hard inputs.

Each method is warmed up, then seven evaluations are timed with alternating
execution order. Producer and checker time are separately recorded. Every
measured answer is replayed or checked; no failed/slow case is dropped. Cache
state is ordinary library process state; no attempt is made to simulate a cold
process. Timing observations are not required to reproduce byte-for-byte.

For the 64-bit case, the recorded medians are 0.673152 ms for native solution,
15.492050 ms for certificate production, and 24.162343 ms for independent
checking. There is no scalar solution speedup on these controls. The proof path
returns additional independent evidence, which the native scalar routine does
not. The proper interpretation is not that one solves exactly the same assurance
task faster: the mathematical answer agrees, but the assurance contracts differ.
A claimed benefit of independent certificates must be justified separately.

## Reproduce

The optional comparison requires SymPy. No dependency is installed by these
scripts and no network is used during verification. From the repository root:

    python research/scalar_comparison_v1/verify.py

It checks the integrity manifest, reruns exact decisions and one timing repeat
in temporary storage, and compares deterministic mathematical fields, excluding
the library version field. The saved seven-repeat timings are never overwritten.
An intentional dependency change must still be reviewed; matching these tests is
not a proof that every version is interchangeable. Run `check.py` with fresh
`--output` and `--timings` paths to record a new environment explicitly.

## Research consequence

The general field/ring certificate theorems are not invalidated. The comparison
removes a proposed performance justification based on huge nominal horizons or
lack of an ordinary scalar solver. Further work must show a meaningful assurance,
certificate-size, verifier-cost, or analysis-capability contribution. A native
full matrix-orbit/loop-analysis comparison and an exact novelty determination
remain open. Manuscript writing remains on hold.
