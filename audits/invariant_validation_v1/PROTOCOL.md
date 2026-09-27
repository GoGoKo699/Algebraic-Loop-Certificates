# Gate 09: a real verification obligation, before more orbit machinery

Protocol fixed on 27 September 2026, before any native solver measurements.
Manuscript writing remains on hold. This is a bounded feasibility gate, not
an industrial benchmark or a new orbit/invariant format.

## Consumer and exact obligation

An invariant-based program verifier receives an invertible affine prime-field
update, a supplied initial state, and a proposed preserved relation. It needs
initiation I(a) and consecution: I(x) implies I(F(x)) for every state, not just
points observed on the initial orbit. This is useful even when the invariant
is only an overapproximation. It does not require a full orbit, least period,
field-order decomposition or a target logarithm.

For this gate use two linear observations U=L1*x and V=L2*x, with invariant
U^e=V^f. The update has checked observation multipliers alpha,beta. Test the
same source and invariant through three routes:

1. The existing separating-invariant checker, using a fully bound certificate.
2. cvc5 on the direct counterexample condition I(x) and not I(F(x)).
3. cvc5 on ordinary, explicitly justified multiplication-DAG obligations.

The third route prevents an expanded/difficult raw encoding from masquerading
as a scientific advantage. Both native paths use prime-field arithmetic, not
integer or bitvector approximations. No solver input assumes the conclusion.

## Why the decomposition is a proof, not a trusted shortcut

First establish L_i*F=alpha_i*L_i by the actual linear polynomial equality.
For each multiplication-DAG node u_k=u_i*u_j, derive v_k=c_k*u_k from
v_i=c_i*u_i and v_j=c_j*u_j, where c_k=c_i*c_j in the same field. The obligations
are polynomial equalities of degree at most two, regardless of the exponents.
The final implication uses U^e=V^f and alpha^e=beta^f. Every multiplication
node refers only to earlier nodes. Each universally valid lemma is checked by
asking whether its negation has a model. A disjunction of lemma violations is
unsatisfiable exactly when all lemmas are universally valid. The final
implication is included, not assumed. DAG induction then proves consecution.

The initial observations are both one, checked separately. In each broken
case beta is multiplied by the source-visible base g, and alpha^e != beta^f.
The initial state itself is then an explicit one-step counterexample. A SAT
result is not accepted as a safety conclusion; a timeout or error is inconclusive.

This is elementary congruence and field-ring rewriting. It is not a new proof
calculus, and cvc5 verdicts alone are not independent proof-assistant replay.

## Frozen corpus and resources

Twenty cases: pairs (p,g,e,f) = (13,2,3,2), (257,3,17,16),
(65537,3,65,64), (65537,3,257,256), (65537,3,1025,1024).
For each take either identity observations or S=[[1,1],[1,2]]. Set
alpha=g^f, beta=g^e, a=S^{-1}(1,1), A=S^{-1}diag(alpha,beta)S.
Use the valid update and the one-multiplier perturbation. These are explicit
algebraic controls with easy construction. They are not naturally occurring
hard application inputs. All are retained, including failures/timeouts.

SMT exponents are represented by named repeated-squaring DAGs in BOTH inputs,
not unary unrolling or an exponentially expanded expression. The transformed
observation tests give the raw solver the actual affine update. The decomposed
route also proves those tests; it does not receive an unchecked eigenbasis.
Input generation, solver startup and native solving are separately identified.
A single cold solver process is used per case and route. Fixed internal limit
2,000 ms, external grace 3 seconds, and 1,536 MiB address-space limit on Linux.
No performance significance from one timing sample is inferred. The run is a
capability/scaling probe, not a statistical runtime study or tuning campaign.

Native executable: cvc5 1.4.1, official Linux x86_64 static GPL release (CoCoA
support), archive SHA256 d0b54324ec2129697975da8753767fd255309947b87832917d32a78da7d16666.
It is downloaded only in the dedicated CI job, not by normal repository tests.
The binary, its GPL dependencies and fonts are NOT redistributed in our archive.

## Decision criteria and explicit failure conditions

A native verdict contradicting the exact controls fails the experiment and
requires diagnosis; it is not silently discarded. Unsupported finite fields,
proof options, timeouts, OOM and setup errors are reported separately.

A useful raw-encoding improvement is only a candidate integration observation.
It does NOT clear a contribution if ordinary, equally compact decomposition
also handles the obligations, or if it depends on omitting initiation or source
translation. Novel assurance additionally needs actual independent proof replay
and a comparison with existing finite-field proof production. This run makes
neither that assurance claim nor a proof-production priority claim.

Advance to a larger application study only after identifying what remains beyond
the decomposed native baseline. No automatic claim that these twenty controls
establish application value. Failure of this gate retires this proposed use of
the full orbit compiler, not every possible application of the repository.
