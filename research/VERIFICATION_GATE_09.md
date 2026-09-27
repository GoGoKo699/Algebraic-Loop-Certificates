# A native verifier already handles the proposed invariant task

27 September 2026. Manuscript writing remains on hold. This is a completed
feasibility gate for a concrete consumer, not another equivalent orbit format.

## Proposed benefit and fixed test

The obligation was to validate initiation and universal one-step preservation
of an already supplied algebraic invariant. This is a smaller task than building
an exact orbit recognizer. The experiment compared the existing certificate
checker with native cvc5 direct counterexample queries and an ordinary compact
multiplication-DAG decomposition. The protocol, twenty cases, encodings and
resource limits were committed before the native run.

[The result and exact provenance](../audits/invariant_validation_v1/README.md)
are now recorded. Native cvc5 solved all ten valid invariants directly and nine
of ten broken controls. The one remaining broken control returned unknown.
The frozen decomposed encoding solved four valid and ten broken controls and
left six valid controls unknown. Every conclusive answer agreed with the proved
control. Our local certificate path accepted/rejected all cases as expected,
but no matched native-versus-certificate timing or proof-assistant replay was run.

## Decision

Do NOT advance this family as evidence that an exact orbit engine is needed to
validate supplied invariants. The raw native solver already discharges every
positive obligation in the frozen corpus; the characteristic/high-power structure
does not, here, create the sought capability gap. The decomposition's six unknowns
are preserved rather than tuned away. They concern this batched encoding only.

This is a failed application-benefit hypothesis, not a failed correctness result.
There is no conclusion that all orbit applications are unhelpful or that the
certificate route cannot have a measurable advantage on another justified task.
There is also no basis for claiming a performance advantage from an unmeasured
Python checker or for calling solver verdicts independent proof replay.

## Current proof landscape

The [primary-source dossier](../audits/invariant_validation_v1/SOURCES.md) includes
September 2026 work on finite-field proof production in cvc5 with Pacheck and
Lean checking. Consequently 'make the answer independently checkable' is not a
sufficient unqualified research gap. Actual proof contracts, trusted components,
coverage and cost must be compared. That paper's artifact was not executed here.

## What the result changes in our search

Do not infer a verifier need from the complexity of our internal orbit engine.
A consumer asking about one proposed relation can often avoid orbit construction
entirely. The next candidate should begin with an independently specified task
and an existing baseline that leaves something meaningful unresolved. It should
not begin with a new capability and search afterward for an example to need it.

A useful next evidence package would identify an existing workload or documented
verification requirement, retain its natural input/output contract, execute its
native baseline, and state a falsifiable improvement before writing new source
machinery. A new performance/assurance claim must survive an equally compact,
source-aware comparator. Broader domains, larger exponents and more synthetic
tests alone are not the next objective.

The existing complete algebraic engine, query-boundary results and two recognition
paths remain supporting infrastructure. Scientific readiness is still incomplete:
this gate provides negative selection evidence, not the missing original result.
No manuscript, release, external contact, paid computing or parent-project edit
is included. All prior source, fixtures, manifests and license are preserved.
