# Data format and command-line contract

## Problem document

The closed schema `alc.problem.v1` has exactly six keys: `schema`, `field`, `matrix`, `offset`, `initial`, and `target`. The field object has `kind: "prime"` and `modulus: p`. Vectors have the matrix dimension; entries are exact JSON integers in `0,...,p-1`. Offsets are always explicit, including zero offsets for linear maps.

[The Fibonacci input](../examples/fibonacci_f7/problem.json) is a complete example. Booleans, floating-point representations such as `1.0`, nonfinite values, duplicate JSON keys, ragged matrices, unknown keys, and unknown versions are rejected. Integers beyond binary64 precision are supported by Python's exact JSON integer parsing; do not round them through a JavaScript number when exchanging files.

The canonical fingerprint is SHA-256 of Python `json.dumps(problem, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')`, after successful closed-schema validation. Whitespace and object-key order do not change it; scientific values do.

## Certificate document

`alc.certificate.v1` has exactly these keys:

| Key | Meaning |
|---|---|
| `kind` | Must be `periodic_hits` |
| `problem_sha256` | Fingerprint of the independently supplied problem |
| `first` | Canonical first occurrence, `0 <= first < period` |
| `period` | Claimed least point period, positive and at most `p^d` |
| `period_factors` | Ascending distinct `[prime, exponent]` pairs multiplying exactly to the period; empty for period one |
| `inverse_matrix` | Witness checked on both sides against the original linear part |
| `prime_proofs` | Ascending records with `p`, `witness`, and complete `factors` for `p-1`; base 2 has witness 1 and no factors |

The `schema` key is also mandatory. See the [complete example certificate](../examples/fibonacci_f7/certificate.json). A prime record may use only primes proved by earlier records. Untrusted labels such as `"is_prime": true` have no role.

## Commands

`python -m alc produce --problem P --output C --max-steps N` runs the bounded reference producer. `C` must not exist. A created certificate is labelled a **candidate**, not a verified conclusion.

`python -m alc verify --problem P --certificate C` checks every proof obligation and reports the complete positive hit set. It imports no producer code. This path remains valid under Python `-O`; mathematical checks do not rely on `assert`.

`python -m alc query --problem P --certificate C --from L --through H` first verifies the certificate, then counts hits in the **inclusive** interval `[L,H]`. It reports the next hit at or after `L`, even if it lies beyond `H`. Time arguments must be nonnegative, with `H >= L`.

The optional `--schedule RESIDUE PERIOD` intersects the verified progression with an ordinary supplied arithmetic schedule by the generalized Chinese remainder theorem. A null intersection is certified only as an arithmetic intersection of those supplied progressions; the second schedule is not automatically a certified recurrence. Synchronization of independently certified loops is not supported by this API.

| Exit code | Meaning |
|---:|---|
| 0 | Candidate file created, positive certificate verified, or verified query answered, as stated in JSON |
| 1 | Invalid document or failed proof; **not** target unreachability |
| 2 | Declared resource limit reached; no conclusion (also used by argparse for syntax errors) |
| 3 | Input/output error, including an existing output path |
| 4 | Producer returns no certificate: either bounded search inconclusive or unreachability by complete enumeration |

Inspect the JSON status as well as the exit code. Argument-parser errors go to stderr before JSON handling. No command creates a negative certificate.

## Resource and security scope

The default limits are 1 MiB per JSON file, dimension at most 32, integers at most 1,024 bits, 1,024 prime records, and 1,024 factor pairs per factorization. The reference producer allows at most 1,000,000 orbit steps and separately caps trial division and prime-witness search. Limit changes affect supported instance sizes, not mathematical claims.

The parser bounds the bytes read, rejects duplicate keys and excessive nesting errors, and uses exact arithmetic. These checks are not a claim of a hardened sandbox for hostile public uploads. Run untrusted inputs with ordinary operating-system resource controls. `VerifiedHits` is a Python result object, not an unforgeable capability: API callers must call `verify`, and the CLI enforces that order for queries.

The trusted code includes Python, the parser, modular arithmetic, matrix operations, and the certificate checker. Tests are independent corroboration, not a mechanized proof of the implementation. No network calls, external solver processes, or executable code from the certificate are used during verification.
