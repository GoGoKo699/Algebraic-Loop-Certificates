# Exact acceptance contract

The independently trusted problem is the complete raw ASCII AIGER circuit.
The untrusted certificate has two integers: `taps` and `odd_exponent`.
Filenames, comments, claimed periods, upstream verdict labels, and symbol names
do not participate in acceptance.

`check(raw, taps, odd_exponent)` accepts only when:

1. A strict parser recognizes the supported original AIGER layout, with n input
   bits, 2n+1 zero-initialized latches, one output, and an acyclic AND graph.
2. Exact Boolean normalization proves that **every** next-state latch and the
   output equal the wrapper in THEORY.md, with the proposed tap matrix A.
3. `odd_exponent` is positive and odd, and exact matrix powering proves
   A^odd_exponent = I over GF(2).

The supported matrix has first row `taps`, and row j (j > 0) copies coordinate
j-1. Input bits load both the running register and its saved seed whenever any
input is nonzero. The counter and detector must match exactly. This does not
accept arbitrary affine loops, arbitrary AIGER circuits, guards, fairness,
constraints, nonzero or nondeterministic initialization, or arbitrary queries.

Resource limits are 100,000 input bytes, n between 2 and 64, at most 5,000 AND
gates, at most 4,096 exponent bits, and 2,000,000 Boolean-normalization work
units. Interned node IDs preserve DAG sharing rather than recursively hashing
unfolded expression trees. Exceeding a limit or failing structural recognition
rejects the certificate; it is not a proof of unsafety.

The checker imports no producer, factorizer, primality service, orbit enumerator,
or solver. Acceptance relies on the implementation of parsing, sound Boolean
rewrites, matrix arithmetic, and the mathematical wrapper theorem. This is a
small Python trusted boundary, not a formally verified checker or a standard
AIGER proof artifact. `verify.py` imports the checker for positive and counterfeit
tests; its raw gate evaluator and finite-state exploration do not use the
checker's symbolic expressions or matrix arithmetic.

The source-aware comparator in `source_aware.py` decides odd order of the same
extracted companion matrix using gcd(f,f'). Its circuit-level use still requires
the same source-to-wrapper binding. It does not independently certify that
binding, and its agreement is not independent proof-assistant replay.
