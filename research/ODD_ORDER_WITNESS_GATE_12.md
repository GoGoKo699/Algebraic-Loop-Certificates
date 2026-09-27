# Gate 12: retain the odd-order premise at the native proof interface

27 September 2026. Manuscript preparation remains on hold.

## Decision

The premise gap recorded in [gate 11](PROOF_INTERFACE_GATE_11.md) is closed for
the supported wrapper. A seed-dependent period circuit replaces the old
constant maximal-period bound. Three frozen positive witnesses pass all nine
Certifaiger obligations, including two controls with mixed seed periods and
nonminimal supplied exponents. Two wrong period selectors fail induction.
All 37 completed CNF proofs independently replay.

This is an integration of established order extraction and history variables.
It establishes neither new algebra nor an advantage over conventional
source-aware methods, which can emit the same circuit. The active question is
now the significance and priority of the original-state evaluation/history
distinction, not how to invent another certificate format.

## Exact premise and construction

Let A be the binary update matrix and let M>0 be odd with A^M=I. For the
complete prime factorization M=product p^e, define

```
P(s) = product over p and k=1,...,e of
       (1 if A^(M/p^k) s = s else p).
```

The seed period T_s divides M. Exactly v_p(T_s) tests fail for prime p, so
P(s)=T_s. This includes zero, for which P(0)=1. Neither minimality of M nor
uniformity of nonzero seed periods is needed. The one-bit M=1 case belongs to
the general theorem even though the restricted companion frontend does not
represent every matrix in that theorem.

The history counter t starts at zero, resets on reseeding, inactivity or
imminent return, and otherwise increments. With L=max(1,bit_length(M)), use

```
H = (r=s=0 and t=0)
    or (s!=0 and t<P(s) and r=A^t s and c=t mod 2).
```

The inactive branch leaves c unrestricted. Every original input and latch is
retained and explicitly mapped; only history is added. The strengthened bad
output is original_bad OR NOT H. In particular, the original second bad
condition is not accidentally gated by the input. Arbitrary nonzero reseeding
remains allowed. [The contract](odd_order_witness_v1/CONTRACT.md) and
[ordinary proof](odd_order_witness_v1/THEORY.md) specify initiation, induction,
safety, reset behavior and the exact original monitor.

Given the factorization, canonical row-reduced fixed-space tests, controlled
matrix powers, and fixed-prime shift/add multiplication give circuit size
O(n²E+n²L+L²), where E=sum e<=L. Naive matrix precomputation costs
O(E n³L) bit operations. Obtaining the factors is additional work. The bounded
implementation uses complete deterministic trial division for odd M<2^24 and
widths 2 through 24; no polynomial total-construction or factorization-free
claim follows. Canonical kernel sharing was fixed before native execution.

## Frozen experiment and measured costs

The cases, mutations, simplification variant and limits were fixed before any
native run. The local pre-execution source/candidate commit is recorded in
`odd_order_witness_v1/native/EXECUTION.json`; its freeze hashes are retained
independently in `BUILD_PROVENANCE.json`. Each case was run once through the
unchanged gate-11 driver with the same pinned tools, ten seconds per process,
1 GiB address space and 64 MiB raw artifacts per case.

| Case | Status | Witness bytes | Raw LRAT bytes | Construction seconds | Native replay seconds |
|---|---|---:|---:|---:|---:|
| Synthetic rotation3, M=9 | 9/9 accepted | 1,920 | 27,776 | 0.0410 | 0.0793 |
| Synthetic mixed5, M=63 | 9/9 accepted | 4,937 | 587,449 | 0.0379 | 0.1117 |
| Original published8, M=255 | 9/9 accepted | 11,872 | 24,898,388 | 0.0436 | 3.3326 |
| rotation3, constant global bound | Inductive rejected | 1,861 | Valid prefix retained | 0.0514 | 0.0499 |
| mixed5, repeated-prime test omitted | Inductive rejected | 4,820 | Valid prefix retained | 0.0426 | 0.0570 |

The synthetic models independently implement the same wrapper equations. Their
nonzero period histograms are {1:1, 3:6} and {3:3, 7:7, 21:21}, respectively.
They are premise controls, not newly discovered published workloads. The
published 8-bit circuit is unchanged from earlier gates. The old maximal-period
producer correctly refuses the two unsupported controls; that refusal is not
a solver failure.

Construction timing includes fresh-process imports, factoring, algebra and AAG
file output, before native verification. Replay includes native obligation
generation, CNF conversion, SAT search and native proof checking, excluding
builds and later Python replay. Exact records and compressed artifacts are
retained. There were no UNKNOWN outcomes. A rejected witness does not show
that the source is unsafe.

The earlier 8-bit witness occupied 11,211 bytes and produced 25,813,066 LRAT
bytes in a 3.417-second native replay. The new witness occupies 11,872 bytes
and produces 24,898,388 LRAT bytes in 3.333 seconds. These isolated observations
show the implemented weaker-premise route remains feasible on the same input;
they do not establish a speedup, a general proof-size reduction or scaling.

## Verification and remaining trust

Independent small-matrix reasoning covers all 109 odd-order matrices in
dimensions 1 through 3, including nonminimal exponents and malformed-factor
controls. Independent raw-gate checks cover all 66,560 source assignments for
the two synthetic models and 16,384 augmented assignments for rotation3.
Additional period, transition and counterfeit checks are documented in the
[module README](odd_order_witness_v1/README.md).

All 27 positive obligations and five completed obligations before each negative
failure have valid retained LRAT proofs. The unchanged independent Python
checker replays all 37. This establishes unsatisfiability of the supplied CNFs.
Certifaiger's model/witness-to-obligation construction and AIGER-to-CNF
translation remain trusted. Hashes and successful replay do not turn these
native transformations into a formally verified frontend.

## Comparison and next stopping rule

The existing odd-order checker and conventional squarefree-polynomial route
both accept all three source cases. Their established order structure permits
the same period selector and native witness; there is no exclusive capability
for this repository's orbit engine. No new ABC timing experiment was run on
the synthetic controls, and no comparative runtime claim rests on them.

The [primary-source dossier](odd_order_witness_v1/SOURCES.md) reviews existing
finite-field proof interfaces, FSR period routines, history-variable methods,
discrete-log bit extraction and invariant-inference lower bounds. Source
inspection of the finite-field systems was not execution of their artifact.
Their field-equation proof contract does not itself discharge the temporal
source-to-safety bridge. A new finite-field frontend is not justified merely
to restate this now-working native witness.

Next, state and compare the exact forced original-state phase predicate and
its oracle reduction against direct predecessors, especially history-variable
and phase-bit results. Keep evaluation of an already supplied predicate
distinct from black-box inference of an invariant. Neither a discrete-log
reduction nor the current native experiment proves an unconditional invariant
size lower bound. Continue only if a precise theorem, useful cost/assurance
separation or documented integration requirement survives that comparison.
If the distinction is already implied by prior work, record that outcome and
stop expanding this construction. Manuscript work and originality claims
remain on hold.
