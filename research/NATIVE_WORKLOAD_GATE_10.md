# A smaller proof for an existing circuit-safety workload

27 September 2026. Manuscript preparation remains on hold. This pass follows
the failed [supplied-invariant gate](VERIFICATION_GATE_09.md) by starting from
existing workloads and preserving their actual output requirements.

## What changed

The [native LFSR gate](../audits/native_lfsr_v1/README.md) ran SmokeRand's own
eight advertised controls. All were resolved: four maximal periods, two false
maximal-period claims, and two inputs outside the supported binary-linear
model. Our unchanged root checker agrees on the four matched 32-bit cases.
This closes maximal-period discovery as another proposed capability gap for
the complete orbit compiler, within this tested workload.

A different existing consumer gives a concrete integration result. The
`lfsr-period` family in `tniessen/aiger-safety-properties` asks whether an
input-dependent circuit can reach its bad output under arbitrary reseeding.
The new [raw-circuit checker](aiger_lfsr_v1/README.md) binds a small algebraic
argument to all 23 original ASCII AIGER circuits, widths 2 through 24. It
checks every latch update, the bad-output logic, and zero initialization.
Neither filenames nor the author's expected-result comments are accepted
as evidence of safety.

## The useful simplification

Let A be the binary-linear update. For the checked wrapper, a positive odd M
with

$$
A^M=I
$$

is enough. This implies invertibility and odd periods for every state. A
nonzero reseed cannot subsequently become zero. The parity monitor cannot
report an even first return, and it is reset both by reseeding and by a match.
The proof covers all future input sequences; it is not a bounded trace check.

No least period, discrete logarithm, irreducible decomposition, prime proof,
or general orbit recognizer is required. A safe source may have many short
odd cycles. Maximality is strictly more than this consumer needs.

There is an even simpler conventional source-aware decision route: for this
companion matrix, a nonzero constant coefficient and squarefree characteristic
polynomial are equivalent to odd order. The separately implemented Euclidean
gcd test agrees on all 23 sources. It needs no supplied exponent. Thus the
algebraic condition is not a new theorem or a superiority claim over familiar
LFSR mathematics; the concrete progress is checking it against real circuit
bytes with their complete wrapper semantics.

## Evidence and limits

The [module record](aiger_lfsr_v1/README.md) supplies the exact contract, ordinary
soundness proof, original MIT-licensed circuit bytes, source hashes, independent
raw-gate evaluation, exhaustive small-matrix controls and corrupted-circuit
tests. The [native protocol](aiger_lfsr_v1/NATIVE_PROTOCOL.md) fixes a six-width
ABC PDR comparison and its limits; the native record distinguishes solver
verdicts from timeouts and from independent proof replay.

The executed native probe reported SAFE for widths 2 and 4. Widths 8, 12, 16,
and 24 reached the fixed 10-second limit and remain UNKNOWN to that run.
This demonstrates a concrete use for the small source-aware route in the
tested setup. It does not establish a performance ratio, a general limitation
of PDR, or an advantage over the squarefree-polynomial method above.

The checker recognizes one specified wrapper family and fails closed outside
it. It is not a general AIGER frontend or a formally verified implementation.
Its interned Boolean representation and explicit work budget avoid recursively
expanding malformed shared gate graphs. Resource rejection is inconclusive.
The root `alc/` API and every earlier expected mathematical fixture are unchanged.

## Next research decision

Keep this as the first concrete circuit-integration candidate. Before expanding
the engine or corpus, determine whether the checked source reduction and safety
argument can be delivered through an existing verifier's independently checked
proof interface. Compare against structural LFSR recognition and ordinary
squarefree-polynomial reasoning at that same interface. A measured weakness of
one generic solver would not establish superiority over the source-aware route.

The proposed benefit must concern the whole source-to-safety proof contract,
its trusted code and its cost, rather than the familiar odd-order algebra alone.
The present result makes that question concrete and falsifiable. It does not
yet establish a new publishable proof system or scientific completion.
