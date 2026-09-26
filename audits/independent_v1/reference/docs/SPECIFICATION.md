# Mathematical and certificate specification

## 1. Exact input model

An instance contains a prime integer `p`, an invertible square matrix `A` over `F_p`, a translation vector `c`, an initial vector `a`, and a full-state target `b`. The recurrence is

$$x_{t+1}=Ax_t+c,\qquad x_0=a,\qquad t\in\{0,1,2,\ldots\}.$$

All residues must be canonical integers in `[0,p)`. Booleans are not accepted as integers. Empty/ragged matrices, singular maps, composite moduli, extra fields, and schema mismatches are rejected. Prime fields are the **implemented** scope; the abstract ideas extend further, but an integer `p^k` does not implement an extension field.

The exact JSON fields are `schema`, `modulus`, `matrix`, `translation`, `initial`, `target`. The schema is `alc-instance-1`; translation is explicit even when zero. The supplied [Fibonacci instance](../examples/fibonacci.json) is an executable format example.

Affine dynamics are lifted to ordinary linear dynamics:

$$T=\begin{pmatrix}A&c\\0&1\end{pmatrix},\qquad v=(a,1),\qquad w=(b,1).$$

The checker creates this lift itself. Its dimension is `d+1`. Invertibility ensures pure periodicity from the initial state; the code does not silently assume this for a singular map.

## 2. Instance binding and prime proofs

A certificate has exactly `schema`, `instance_sha256`, `prime_proofs`, and `claim`. Its schema is `alc-certificate-1`. The digest is SHA-256 of the instance serialized with Python JSON options `sort_keys=True`, `separators=(',', ':')`, and `ensure_ascii=True`. It binds a certificate to its declared instance; it is not an external signature, proof of authorship, or replacement for the mathematical checks.

The CLI rejects duplicate JSON keys. It parses at most four MiB per file. By default the checker limits matrix dimension to 32, integer bit length to 4096, prime-proof count to 2048, and explicit cycle length to 100000. Exceeding a policy limit is a `VerificationLimit`, not a mathematical rejection. These limits are not a complete denial-of-service defense.

Each entry in `prime_proofs` is a Lucas/Pratt-style certificate. Entries are sorted strictly by the proposed prime. The base case is `{"n":2}`. A larger number has fields `n`, `base`, and `factors`, where `factors` is a sorted list of distinct `[q,e]` pairs factoring `n-1`. Each `q` must have an earlier valid proof. The checker tests

$$g^{n-1}=1\pmod n,\qquad \gcd(g^{(n-1)/q}-1,n)=1\quad\text{for each prime }q\mid n-1.$$

**Why sufficient:** for every prime divisor `r` of `n`, these tests force the order of `g mod r` to contain the full prime-power factorization of `n-1`. Thus `n-1` divides `r-1`, implying `r>=n`, so `n` is prime. Generating the proof may require expensive factorization. Verifying a supplied proof does not call a factorization routine. The method is classical prior art; see [the audit](PRIOR_WORK.md).

No unsupported probabilistic-primality flag is accepted. The factorization of a claimed period is likewise checked for complete product, distinct sorted prime factors, positive exponents, and primality proofs.

## 3. Positive hit schedules

A hit claim contains `kind: "hit"`, `offset: t0`, `period: r`, and a complete `factors` list for `r`. Require `0 <= t0 < r`. The checker verifies

$$T^{t_0}v=w,\qquad T^rv=v,$$

and, for every distinct prime `q` dividing `r`,

$$T^{r/q}v\ne v.$$

**Least-period proof.** The actual period `s` divides `r`. If `s<r`, some prime divisor `q` of `r/s` would make `s` divide `r/q`, contradicting the exclusion. Thus `s=r`. Within one period, distinct times give distinct states, since the dynamics are invertible. Therefore the hit set is exactly

$$\{t_0+jr:j\geq0\}.$$

The period-one case has an empty factorization and is supported. Zero initial vectors and nonzero translations are handled through the same lift; there is no special unjustified nonzero-state assumption.

Checking requires binary matrix powering, not enumerating `r` states. With dense matrices, the simple kernel uses polynomially many field operations in `d`, the number of supplied factors, and the exponent bit lengths. This is not a new period theorem or a claim of an optimal matrix algorithm.

## 4. Two negative certificate classes

### Outside the cyclic span

A claim with `kind: "outside-span"` supplies a row vector `separator` of length `d+1`. The checker tests

$$uT^jv=0\quad (0\leq j\leq d),\qquad uw\ne0.$$

Cayley-Hamilton implies that all higher powers applied to `v` lie in the span of those first `d+1` Krylov vectors. Consequently `u` annihilates every reachable lifted state but not the target. This proves the hit set is empty. A separating functional exists whenever the target is outside that span, but not for every unreachable target.

The checker recomputes the short Krylov prefix; it does not trust a producer's rank calculation or an unsupported claim that a subspace is invariant. The producer obtains a separator by solving a linear system; the checker does not import that search.

### Explicit cycle exclusion

A claim with `kind: "cycle-exclusion"` supplies a nonempty list of original, unlifted `states`. The checker verifies that the list starts at `a`, every step follows the recurrence, the final next state returns to `a`, and no listed state equals `b`. Determinism then implies all future states repeat the listed trajectory.

Distinctness is not needed for this *negative* proof; repeating a closed trajectory cannot introduce a missed target. The certificate is linear in the supplied trajectory length. It is useful for small instances and as a reference, not a compact or polynomial-size guarantee for all finite-field nonmembership problems.

No certificate is emitted when a bounded producer merely fails to finish. An `unknown` result is not accepted by the checker as any sort of proof.

## 5. Consumers and their exact contracts

`first_at_least(summary, H)` returns the least hit at or after a nonnegative integer `H`, or `None` for a verified empty set. `count_interval(summary, low, high)` counts hits in the **inclusive** interval. Negative bounds and reversed intervals are rejected.

`synchronize(left, right)` intersects two certified arithmetic progressions on the same integer time axis using the generalized Chinese remainder theorem. With residues `a mod m` and `b mod n`, the intersection is empty exactly when `gcd(m,n)` does not divide `b-a`; otherwise it has period `lcm(m,n)`. The synthesized summary is an arithmetic consequence of its verified parents, not a new external certificate for a new loop.

Synchronization does not summarize two sequentially composed loops, arbitrary guards, asynchronous clocks, resets, or nondeterministic choices. There are no implicit extra semantics. Python callers must pass verified summaries; the JSON CLI rechecks the input certificate before every query.

## 6. Trust and correctness boundaries

The trusted executable core is the checker, the shared exact arithmetic, JSON parsing, Python's integer operations, and the operating environment. The code is independently organized, not formally verified. Producer and checker share the arithmetic kernel; independent trajectory enumeration in the tests does **not** use that kernel.

The proof system checks claims about the supplied model. It does not establish that a program was translated into that model correctly. Whole-program semantics, a verified frontend, optimized algebra backends, extension fields, succinct general nonmembership, and published performance gains remain open development/research tasks.
