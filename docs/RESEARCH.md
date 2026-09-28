# Research assessment

For a first reading, use the [Manna–Pnueli learning path](LEARNING_PATH.md),
the [worked safety tutorial](TUTORIAL.md), and the [reproduction guide](REPRODUCING.md).
They introduce the existing results; this page records the claims and their limits.

The repository is an educational and reproducibility resource. Its content is
not aimed for publication. See [status and collaboration](../README.md#status-and-collaboration)
for the current purpose and contact information.

## Current assessment

The [final bounded assessment](../research/CONTRIBUTION_ASSESSMENT_18.md) closed the
literature, assurance and claim review. It supports a reproducible integration
case study, without establishing a distinct new contribution or general solver
advantage. Existing witness/history constructions and specialized certified
workflows are direct predecessors; the exact exporter's priority remains
unresolved. The [source dossier](../research/contribution_v1/SOURCES.md) records
the inspected primary texts and access limits.

The [amended comparison](../research/BOUNDED_COMPARISON_GATE_17.md) completed 54
trials and met its three-of-three added-coverage criterion at width 8: accepted
exporter witnesses took 4.397–4.713 seconds, while pinned rIC3 reached the
30-second deadline in all three repetitions. A deadline is not a measured
completion time or an unsafe verdict. All 180 completed CNF proofs replay
independently; native source, obligation and CNF translations remain trusted.
The observation applies to the fixed hinted source family and configuration.
The exporter does not use the complete orbit engine, so this result establishes
no benefit for that engine.

The [requirement audit](../research/SCIENTIFIC_CLOSURE_GATE_14.md) specified an
accepted safety certificate for the original circuit as the consumer's output.
The [qualification gate](../research/BASELINE_QUALIFICATION_GATE_15.md) established
the compatible pinned baseline. The completed comparison used these roles:

| Route | Role and boundary |
|---|---|
| Pinned rIC3 | Required certifying baseline through the same accepted-artifact interface |
| ABC | Earlier diagnostic observations, not the matched comparison |
| Direct squarefree structural checker | Source-aware cost and trust reference; decides safety but does not itself supply the requested standard witness |
| Conventional algebraic reasoning | Can emit the same witness as the exporter; it is not a weaker competitor forced to enumerate an orbit |

The outcome-informed [storage amendment](../research/completion_v2/STORAGE_AMENDMENT.md)
retained the 64 MiB raw budget and added a separate 64 MiB allowance for exact
known metadata, increasing possible combined storage. Fresh qualification and a
published freeze preceded the new measurements; this was not a blind
preregistration. The [suspended experiment](../research/BOUNDED_COMPARISON_GATE_16.md)
remains separate, without pooling or selective continuation. The original
[study design](../research/completion_v1/STUDY_DESIGN.md) and
[amended protocol](../research/completion_v2/EXECUTABLE_PROTOCOL.md) preserve the
criterion, corpus and execution rules.

Earlier stage-level observations in the [cost audit](../research/completion_v1/README.md)
exclude some construction costs and are not complete workflow timings.
Qualification controls establish compatibility and rejection behavior, not
performance. No further experiment is scheduled; the
[current work order](../work_orders/CURRENT.md) records the conditions for
reopening scientific work. Maintenance does not reopen the frozen studies.

## Earlier decisions and preserved evidence

These checkpoints explain how the scope narrowed. Their dated recommendations
are historical; Gate 18 and the current work order govern present work.

| Checkpoint | Retained conclusion |
|---|---|
| [Gate 08: constructive comparison](../research/CONTRIBUTION_ASSESSMENT_08.md) | Conventional character/Taylor reasoning supplies the same source-recognition contract at comparable coarse polynomial bounds. The direct matrix-logarithm source was read; this was neither a native performance benchmark nor an exhaustive priority finding. |
| [Gate 09: supplied invariants](../research/VERIFICATION_GATE_09.md) | Native cvc5 solved all ten valid invariants. This corpus showed no capability gap requiring the engine; no matched timing or proof-assistant replay was performed. |
| [Gate 10: existing workloads](../research/NATIVE_WORKLOAD_GATE_10.md) | Native LFSR analysis and 23 published AIGER circuits provided a source-to-safety case; source-aware squarefree reasoning reached the same algebraic decision. |
| [Gate 11: proof interface](../research/PROOF_INTERFACE_GATE_11.md) | History witnesses passed Certifaiger obligations with SAT-proof replay under a maximal-period premise. The phase-parity argument established no size lower bound. |
| [Gate 12: odd-order witnesses](../research/ODD_ORDER_WITNESS_GATE_12.md) | Exact seed periods removed the maximal-period premise, supporting mixed periods and nonminimal exponents. Factorization remains construction work; conventional reasoning can emit the same witness. |
| [Gate 13: invariant/history audit](../research/INVARIANT_HISTORY_GATE_13.md) | The forced predicate instantiates an established inverse-bit separator; history retains its inverse witness. This supplies neither standalone novelty, a general circuit lower bound nor a matched advantage. |

The [research index](../research/README.md) maps the experimental modules and
independent audits. They do not change the production API.

## Production contract

The production producer performs bounded discovery; its checker verifies an
untrusted candidate against a separately supplied recurrence, including
primality proofs. The consumer can then query the complete positive hit
progression and supplied schedules without rerunning discovery. This is
engineering around established mathematics, distinct from the hardware-safety
contract above.

As specified in [the production contract](SPECIFICATION.md), v1 supports prime
fields only. It does not approximate unsupported extension fields, singular
dynamics, arbitrary guards or general unreachability proofs. Its deliberately
elementary producer is not a fast general classical discrete-log solver.
Larger execution horizons alone establish no advantage over source-level
simplification or established finite-field and matrix-order routines.

## Source-by-source baseline

| Primary source | Established result or relevance | What this repository does not claim |
|---|---|---|
| Imran and Ivanyos, *Efficient quantum algorithms for some instances of the semidirect discrete logarithm problem*, Designs, Codes and Cryptography 92 (2024), [Section 3.3](https://doi.org/10.1007/s10623-024-01416-8) | Finite-field orbit membership via cyclic-subspace/matrix-power methods and established quantum algorithms | That the orbit reduction or a polynomial quantum producer is new; no quantum backend was run |
| Frohn and Fuhs, *A calculus for modular loop acceleration and non-termination proofs*, STTT (2022), [article](https://doi.org/10.1007/s10009-022-00670-2) | Loop acceleration as reusable program-analysis information; modular composition of classical techniques | That a full-state prime-field target certifies general integer-program safety or automatically beats their methods; no native comparison was run |
| Pratt, *Every Prime Has a Succinct Certificate*, SIAM J. Comput. 4 (1975), [article](https://doi.org/10.1137/0204018) | Short checkable primality certificates, using factorizations and multiplicative-order witnesses | That supplying a factor list alone establishes primality, or that making the proof is always cheap |
| [Pratt's Primality Certificates, Archive of Formal Proofs](https://isa-afp.org/entries/Pratt_Certificate.html) | Existing machine-checked formalization of a related proof system | That our Python checker is covered by that formalization |

The arithmetic-progression consumer and Chinese remainder combination are
elementary. This source review records direct predecessors, not an exhaustive
novelty audit. No quantum backend was run.
