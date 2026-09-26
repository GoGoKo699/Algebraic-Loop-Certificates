# Scientific completion ledger

26 September 2026. Manuscript drafting is on hold. See also the
[combined completion ledger](../RESEARCH_COMPLETION.md) and the separately scoped
[modular precision result](../modular_lifting_v1/THEORY.md). This file records scientific
work, including the evidence eventually needed for opening and closing claims.
It is not a manuscript outline to be filled by persuasive prose.

**Overall: research is NOT yet complete for a submission.** The complete
certificate construction below is a substantial executable advance beyond the
positive-only baseline, but novelty, significance and a matched consumer-level
comparison have not all been established.

| Obligation | Current status | Completion evidence / outstanding work |
|---|---|---|
| Exact input and output semantics | Specified | FORMAT.md; prime fields, invertible affine map, fixed initial/full target |
| Complete mathematical coverage of positive and negative outcomes | Derived | THEORY T1-T9, including repeated factors and every rejection mechanism |
| Polynomial certificate size and deterministic verification | Derived | THEORY T9; includes primality, irreducibility, CRT and unipotent arithmetic |
| Non-enumerative reference production | Implemented | Trial factorization plus BSGS; no claim these searches are uniformly fast |
| Sound distinction between rejection, no-hit and resource limit | Implemented/tested | Experimental checker computes verdict; producer budget returns unknown |
| Independent finite validation | Executed | 6,205 state/target cases and opposite-claim controls; 403 unipotent-ring cases |
| Existing primary positive checker compatibility | Executed | 2,374 positive results translated and replayed with unchanged production verifier |
| Native exact-arithmetic comparison | Executed, limited | SymPy 1.14.0: 81 factorizations and 300 scalar cases; not full matrix performance |
| Broad falsification coverage | Partial | 16 proof mutations, input binding, 1,093 mixed-factor cases, irreducibility and budget controls; more fuzzing is possible |
| Formal checker verification | Not performed | Not to be implied by exact arithmetic or finite tests |
| Predecessor replay | Executed for available subset | Existing independent-audit archive passed unchanged; original missing scout remains missing |
| Direct prior theorem comparison | Incomplete | S1 read; S2 abstract and one primary PDF page read, remainder unavailable |
| Novelty/significance decision | Open | Treat certificate result as a reformulation until equation-level audit establishes more |
| Useful complete workflow / strongest classical comparison | Open | No native full matrix-orbit or program-analyzer comparison yet |
| Background support for future abstract/introduction/conclusion | Initial evidence assembled | LITERATURE claim map; unsupported claims explicitly prohibited |
| Repository integration | Additive research branch | Actual publication and CI status are recorded in Git history and the delivery receipt, not inferred from this ledger |

## Scientific result obtained in this pass

The earlier gap was an in-span unreachable target whose only implemented
negative evidence listed its entire orbit. The new system reduces a candidate
answer to checked field congruences and a deterministic cyclic-unipotent
membership calculation. It admits polynomial-size evidence for either outcome
without making discrete-logarithm search part of the checker.

This is not a new fast discrete-logarithm algorithm. Existing matrix-logarithm
reductions are its direct intellectual predecessor. Its possible contribution
is the full proof-producing formulation, explicit no-hit coverage, verified
period output, and subsequent exact consumers. Whether that combination is
sufficiently new or consequential remains a research question.

## The evidence required before calling research complete

1. Resolve the strongest direct predecessor at equation level. Identify exactly
   what this proof system adds, or classify it as a corollary and find a stronger
   consequence. Failed retrieval is a known gap, not proof of absence.
2. Select a mathematically useful contribution/consumer and compare its actual
   task with source-aware classical methods. A theoretically novel certificate
   bound can be central, but an easy toy and a large time horizon cannot stand
   in for one. Empirical performance claims require matched executed baselines.
3. Close the claims ledger: every proposed statement must have a proof, executed
   evidence, or an appropriate primary source. Separate parameterized theorem
   guarantees from the implementation's default limits and the producer's costs.
4. Re-run the unchanged production verifier, independent audit, new checks and
   mutation controls on the integrated commit, and preserve exact artifacts.
   A reference-subset run is not a full-root verification claim.

No manuscript section should be written to conceal an unresolved item. The
remaining work is scientific and comparative, not just editorial preparation.

## Next research order

Prioritize S2 and related finite-field/group membership certification results.
The question is whether a distinct theorem follows from the new proof interface
(for instance, a justified certificate-size bound for a compositional consumer),
not whether more examples can be produced. The separately derived modular precision lemma has an explicit word-arithmetic
semantics justification; it is not a license to broaden to arbitrary guards or
change the consumer merely to manufacture difficulty.

Keep the root production API stable until a format promotion has its own
compatibility plan. The experimental code can be added and tested without
changing the old examples, checker, manifests, or archived audit evidence.

## Continuation result

The original complete-certificate and modular proofs were rerun. A source-aware scalar reduction now permits native SymPy comparison on 13,602 cases, with 1,122 paired proof-path checks. It rules out a solution-time advantage on the recorded scalar controls. See [the deeper predecessor comparison](../PRIOR_WORK_COMPARISON_02.md); it identifies substantial finite-ring lifting overlap and retains the incomplete whole-paper audit as an open item. Overall scientific completion remains false.
