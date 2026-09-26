# Direct positive modular certificates

A complete positive hit set does not need a full precision chain. For an
invertible affine map over Z/NZ, it suffices to provide a hit offset t, the
least point period r, a ring inverse of the linear part, and proved prime
factors of r. There is no mathematical need to factor N for this positive
certificate. This is the standard finite-permutation order argument, not a
new order theorem or a general negative certificate.

The experimental schema is `alc.modular-hits.v1`, separate from the unchanged
primary API and from the complete modular yes/no schema. It checks:

    F^t(a)=b,  F^r(a)=a,  F^(r/q)(a)!=a for every prime q dividing r.

Require `0<=t<r`, exact factorization of r, recursive prime proofs for those
factors, and the supplied inverse on both sides modulo N. Invertibility makes
the orbit a pure cycle. If its true period s properly divided r, some prime q
would divide r/s and force a return at r/q. Thus the checked r is minimal and
the complete hit set is t+r*j for j>=0. Checking uses binary affine powering,
not traversal of that many iterations. The modulus can be composite; none of
the proof equations treats it as a field.

The certificate size is polynomial in the explicit matrix dimension and the
bit lengths of N and r, including the Pratt evidence. An exact factorization
of N is absent from the interface. This strengthens the implementation's cost
accounting; it is not a new complexity separation from established group/order
certification. The fuller negative proof still needs its own algebraic reasons.

## Constructing and checking are distinct

`producer.assemble(document, first, period)` packages candidate times supplied
by a solver. It factors r by bounded trial arithmetic and builds prime proofs.
It does not discover first or period. A caller must separately charge the
solver, invoke `checker.verify`, and never trust the word `candidate` as truth.
The checker imports no producer, factor search, or discrete-log routine.

A producer budget failure is unknown, not nonmembership. A rejected positive
certificate is not a proof of an empty hit set. Invalid data and unsupported
noninvertible dynamics remain errors, not guessed answers.

## Evidence and matched comparison

The independent audit covers all scalar invertible affine instances for moduli
2 through12 and all invertible two-dimensional linear parts modulo4 with two
translations. Each reachable target is checked and unreachable targets receive
false positive claims that must fail. Nonminimal periods, field/ring confusion,
bad inputs, and producer-import boundaries are tested. The counts and checksum
are in `expected.json`.

A second comparison uses the same three scalar congruential instances as the
native scalar audit. The two proof paths deliver the same complete positive
schedule and independent checking, although their witness structures differ.
One path runs the native scalar solver, assembles a direct proof, and checks it.
The other produces and checks the general precision chain. Neither receives
factorization/order hints. Inputs are fixed before timings; both paths are
warmed, repeat order alternates, all results are checked, and imports/target
construction are excluded. The outputs are deliberately easy algebraic controls.

For the 64-bit example, canonical compact JSON is **292 bytes** for the direct
proof versus **21,744 bytes** for the precision chain. The seven-repeat median
native solve, direct assembly, and direct checking times were respectively
0.739009, 0.048011, and 0.564953 milliseconds. The layered producer/checker
medians were 15.655039 and 25.658976 milliseconds. These are local measurements,
not universal performance ratios or an improvement over all known certifiers.
The native solve must be included: direct assembly by itself is not an algorithm
for discovering the answer.

This repairs unnecessary work in our own earlier proof representation. It is a
concrete implementation improvement using established mathematics. It must not
be advertised as the publication's novel result without a separate contribution.
The prior, heavier fixtures are retained unchanged for regression.

## Reproduce

From the repository root, Python standard library:

    python research/direct_modular_hits_v1/verify.py

The optional comparison uses already installed SymPy:

    python research/direct_modular_hits_v1/verify.py --sympy

The verifier writes only to temporary paths. It compares exact audit outcomes;
with `--sympy` it additionally checks the deterministic proof/answer fields of
fresh benchmarks. It never expects machine timings to reproduce byte-for-byte.
The recorded fixture and timings remain unchanged. No dependency is installed.

The primary root API remains positive prime-field only; use the explicit
research imports for ring inputs. Manuscript preparation remains on hold.
