# Inverse indexing of an algebraic process

26 September 2026. Phase 2; PRX Quantum target; manuscript remains on hold.
Base: bfac45d103c422e2c364eaeb49b1b79aacab6293.
Condensed source-led scout; expanded derivation, code and exact results are in
Quantum_Discovery_Algebraic_Orbit_Scout.zip. No new quantum algorithm, performance
benchmark, or useful end-to-end advantage is claimed.

## 1. A noncryptographic bridge with an important classical escape route

LFSR counters and sequence-based position encoders use discrete logarithms to
recover an index from an algebraic register state. Sachs [1,2] presents concrete
implementations and design discussions. Clark--Weng's 1994 paper [3] explicitly
connects event counters and easy discrete logs, but its full text was unavailable
in this pass. These references establish an existing task, not a quantum-worthy
parameter regime or a measured deployment benefit.

The design literature deliberately chooses smooth group orders to make classical
decoding inexpensive. That option is part of the competitor. Making the counter
harder solely so Shor becomes useful would manufacture an advantage. We need a
reason a fixed or independently valuable process requires inverse information
that remains costly classically. That positive application condition is open.

## 2. Compact question and answer

Given an explicit finite field F_q, an invertible d-by-d matrix A and vectors a,b,
find all nonnegative t such that A^t a=b. The required field representation and
arithmetic are supplied explicitly, not through an unpriced large lookup oracle.

The trajectory is a pure cycle. The answer is empty or t=t0+kr (k>=0), where
0<=t0<r and r is the period of a. Both integers have O(d log q) bits. The input
matrix has O(d^2 log q) bits plus field-representation overhead. For a=0, the
only reachable state is zero and its period is one.

Repeated squaring evaluates a specified A^t efficiently in the bit length of t.
It does not find t from a target by itself. The output contains no orbit table
and requires no state tomography. It must not be conflated with rational
arithmetic, integer overflow modulo 2^n, arbitrary nonlinear programs or an
unknown physical process.

## 3. The efficient quantum algorithm is established

Imran--Ivanyos [4, Section 3.3] explicitly describe finite-field orbit membership
in quantum polynomial time, using the Kannan--Lipton cyclic-subspace reduction.
For a!=0 form W=span(a,Aa,...), stopping at the first linear dependence. If b is
outside W, reject. In one basis of W, write A_W for the restricted matrix and

    C=[a,Aa,...,A^(s-1)a], D=[b,Ab,...,A^(s-1)b], B=D C^(-1),

where s=dim W and C is invertible. Then

    A^t a=b iff A_W^t C=D iff A_W^t=B.

The implication uses equality on the entire cyclic basis; the converse uses its
first column. B is calculated without the unknown time. A singular B is ruled
out for invertible A. The remaining cyclic-matrix power problem uses standard
quantum order and discrete-logarithm machinery. The order of A_W is the point
period because a generates W. This is prior algebra, not our new reduction.

The full implementation must pay for explicit reversible field arithmetic,
controlled powering, order/log recovery, classical reconstruction and confidence.
We have not compiled a resource estimate. A check of A^t a=b verifies a proposed
hit, not by itself the least period, completeness, or an unreachability answer.

Generic efficiently powered actions can instead lead to hidden-shift problems;
compactness and periodicity alone do not imply Shor-polynomial recovery [4].
The usable matrix algebra is an extra substantive capability.

## 4. The reusable classical consequence and its boundary

For a fixed initial state and target, t0 and r answer later time-window questions
by arithmetic: first hit on/after H is t0+r max(0,ceil((H-t0)/r)); count through H
is zero if H<t0 and otherwise floor((H-t0)/r)+1. Known schedules can be combined
by the generalized Chinese remainder theorem. These are elementary consequences,
not new algorithms. Another target can require another logarithm; this is not a
universal precomputed decoder for all future states.

Exact example: over F_13, A=diag(4,5), a=(1,1), target (10,8) gives t=11 mod12.
The component requirements are t=5 mod6 and t=3 mod4. Target (10,12) is impossible
because the required residues disagree modulo2. The calculation is trivial
classically and is used only to test the output meaning.

For the same orbit, the predicate coordinate_0<coordinate_1 on the integer
representatives holds at residues {1,2,6,7,10}. Those five residues are not one
coset in the 12-cycle. A short multi-state predicate does not automatically
inherit the point-target reduction. This proves no hardness result for predicates.
Partial observations, noise and model uncertainty are distinct tasks.

## 5. Classical methods and other leads remain available

Fixed-characteristic finite-field discrete logs admit the expected
quasi-polynomial classical algorithm of Kleinjung--Wesolowski [5], including
characteristic two. This is not polynomial time, but also not an exponential
classical lower bound. Parameter-specific logarithm methods, invariant subspaces,
special orders and shared preprocessing remain valid competitors.

Over rationals the point-orbit problem is classically polynomial [6]. Explicit
permutations acting on strings have a linear-time orbit algorithm [7]. Similar
wording therefore does not imply the same hard problem or input representation.

Two other algebraic bridges were screened, not implemented: modern sparse
polynomial interpolation has strong soft-linear classical methods with specified
modular evaluation access [8]; factoring-assisted Clifford+T synthesis has a
near-optimal non-factoring alternative under stated assumptions [9]. The latter
also changes the deployed output from a classical method to a quantum circuit.
Merely finding a logarithm/factoring dependency in an older algorithm is not an
end-to-end advantage against the best adequate task solution.

## 6. Exact checks and next research obligation

The new standard-library diagnostic exhausts all54 invertible 2-by-2 matrices
over F_2,F_3 and3984 state-target pairs. It checks456 zero-initial cases,588
outside-span rejections,2940 reduced pairs,13956 point/power equivalences and11952
timing queries. Both the original orbits and matrix powers are enumerated
classically. The F_13 example and non-coset guard are additional exact controls.
The report regenerated byte-for-byte. No quantum circuit, native counter/encoder,
production algebra package, hardware, or historical verifier was run.

Source SHA256:3139bda5a3ef11c82546495e82ae9349785841d9c5f8fc4cdd25535820634bd4
Result SHA256:f0b118f4cd3686f23ad9c66fc08d84f4fabaebf0a26150176b4e097308af9ad5

Retain inverse algebraic indexing as a concrete compact-input/compact-output
capability with independent uses, not an accepted advantage workload. The next
question is where global phase/timing/composition relations remove a real
computational limitation after classical redesign and simplification are allowed.
Do not enlarge a toy or deliberately choose a needlessly difficult encoding.
Other algebraic mechanisms remain open. Manuscript, external contact, paid work
and submission remain on hold.

## Primary sources and inspection scope

[1] Sachs, LFSRs Part IV: Easy Discrete Logarithms (2017).
https://www.embeddedrelated.com/showarticle/1088.php
Author implementation/design discussion read; no quantitative hardware claim.
[2] Sachs, LFSRs Part X: Counters and Encoders (2017).
https://www.embeddedrelated.com/showarticle/1118.php
Author's sequence/position example read; not a deployment or advantage survey.
[3] Clark--Weng, IEEE TC43,560-568 (1994), DOI10.1109/12.280803.
Metadata and citation in [1] checked; full-paper retrieval failed.
[4] Imran--Ivanyos, Designs,Codes and Cryptography92,2825-2843 (2024).
https://doi.org/10.1007/s10623-024-01416-8
Full HTML Sections1,3.1,3.3 inspected; no implementation or benchmark reproduced.
[5] Kleinjung--Wesolowski, https://arxiv.org/abs/1906.10668
Primary abstract and precise expected-time scope checked.
[6] Luca--Ouaknine--Worrell, Algebraic Model Checking for Discrete Linear Dynamical
Systems (2022), https://doi.org/10.1007/978-3-031-15839-1_1
Primary overview/point-orbit discussion read; no claim about current open problems.
[7] Lin--Zhou, https://arxiv.org/abs/1411.3164
Primary abstract and explicit permutation action model read.
[8] Giorgi et al., https://arxiv.org/abs/2202.08106
Primary abstract/modular evaluation interface checked; no native run.
[9] Ross--Selinger, https://arxiv.org/abs/1403.2975
Primary abstract and factoring/near-optimality qualifications checked.
