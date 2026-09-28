# Learning the safety-witness construction

[Overview](../README.md) · [Book route](LEARNING_PATH.md) · [Tutorial](TUTORIAL.md) · [Lab](REPRODUCING.md)

Start here to understand the completed hardware-witness case study. The goal is
to explain how an algebraic observation becomes a candidate circuit, why added
history supports an inductive safety argument, and what external acceptance
actually establishes.

The separate production `alc/` package certifies periodic target hits for a
supplied recurrence. The hardware study instead checks safety of an original
circuit with unrestricted inputs. Its exporter does not use the complete orbit
engine. Keep these two contracts distinct while reading.

## A first pass

1. Read the [tutorial](TUTORIAL.md) for the worked construction and vocabulary.
2. Follow the book route below, returning to the linked repository material.
3. Use [reproducing the evidence](REPRODUCING.md) to check retained artifacts.
4. Read the [final assessment](../research/CONTRIBUTION_ASSESSMENT_18.md) before
   interpreting the comparison as a research contribution.

Understanding the proof is the first goal. Running the native comparison again
is not a prerequisite for learning from its retained evidence.

## One book anchor

Use **Zohar Manna and Amir Pnueli, _Temporal Verification of Reactive Systems:
Safety_ (Springer, 1995)**. See the [publisher's book page](https://link.springer.com/book/10.1007/978-1-4612-4222-2)
and [official preface and contents](https://link.springer.com/content/pdf/bfm:978-1-4612-4222-2/1).

The preface describes this volume as largely self-contained: Chapter 0 supplies
the relevant earlier material. Familiarity with programming and first-order
logic is assumed; concurrency background helps. Prior temporal logic is not
required. There is no second required textbook.

| Book route | Question to carry into the reading |
|---|---|
| **1.** Chapter 0; especially §0.1, Fair Transition System, p. 2 | What are the state, inputs, initial condition and transition relation? |
| **2.** Chapter 1, §§1.1–1.5; §1.2, Invariance Rule, p. 87 | What holds initially, survives every step and implies safety? |
| **3.** §§1.3–1.5, pp. 104, 111, 127 | Why can safety alone be too weak for induction? |
| **4.** §2.6, Finite-State Algorithmic Verification, p. 227 | How do finite checks differ from a general proof? |
| **5.** §§4.1–4.7; §4.7, History Variables, pp. 357–362 | How can a witness remember a phase without restricting the source? |

The locations and prerequisites above were checked against the publisher's
preface and contents. The full chapter text was not inspected for this guide.
The explanations below are a repository-specific learning map, not an adaptation
of the book's examples or a claim that the book contains this exporter.

## Connect the ideas to the implementation

| Repository stop | Explain before moving on |
|---|---|
| **Problem:** [witness contract](../research/odd_order_witness_v1/CONTRACT.md) | Original updates, initialization and bad detector stay fixed. |
| **Candidate:** [period and history theory](../research/odd_order_witness_v1/THEORY.md) | A factored odd multiple of the matrix order yields each seed's exact period. |
| **Compilation:** [producer](../research/odd_order_witness_v1/produce.py) | Matrix tests and Boolean arithmetic implement the predicate. Emission is not acceptance. |
| **Small cases:** [independent controls](../research/odd_order_witness_v1/verify_theory.py) | Separate stepping checks identities and catches incorrect selectors. |
| **Acceptance:** [native protocol](../research/odd_order_witness_v1/NATIVE_PROTOCOL.md) | Original model and candidate enter the checker separately. |
| **Measurements:** [completed comparison](../research/BOUNDED_COMPARISON_GATE_17.md) | Accepted witnesses, decisions and UNKNOWN are different outcomes. |

Read the mathematical argument before reading the constructor's optimizations.
Kernel sharing changes how a predicate is represented; it does not change the
predicate that the proof must justify.

For the active branch, be able to interpret each part of

```math
\begin{aligned}
&s \ne 0,\qquad 0 \le t < P(s),\\
&r = A^t s,\\
&c = t \bmod 2.
\end{aligned}
```

Here `P(s)` is the exact seed period and `t` is added history. Follow reseeding,
ordinary advancement and return separately. Then handle the inactive zero-state
branch, where parity is unrestricted. The original bad detector remains part of
the obligation even when a branch seems intuitively harmless.

The proof covers every original input sequence. It makes no fairness assumption
about when reseeding occurs, which inputs recur, or which transitions are taken.
The history update must be defined on every step. Discarding history recovers the
original behavior; adding it must not eliminate an inconvenient execution.

## Bridges supplied by the tutorial

The book anchors the verification reasoning. The [tutorial](TUTORIAL.md) supplies
the following connections needed for this repository:

- **Binary algebra:** XOR arithmetic, matrix powers, point periods and extraction
  from a completely factored odd exponent. This is arithmetic over `F_2`, not
  integer wraparound arithmetic modulo a machine-word size.
- **Source semantics:** the supported LFSR wrapper, arbitrary reseeding, parity
  and the precise bad condition. The matrix theorem does not make the frontend
  a recognizer for arbitrary circuits.
- **Witness representation:** original latches and inputs, additional history,
  the strengthened bad output, and the AIGER/Certifaiger boundary.
- **Proof artifacts:** why Boolean obligations become CNFs, what an UNSAT proof
  establishes, and which translations remain trusted after independent replay.

These bridges connect established methods to the actual files. They do not add
new arithmetic rules to the native checker or replace its source-binding checks.

## Read the evidence after the proof

The [reproducibility guide](REPRODUCING.md) separates checking retained evidence
from reconstructing a native tool environment. Follow its commands and scope
notes before treating a successful local command as reproduction of a timing.

In the completed amended study, width 8 has three accepted exporter witnesses
and three deadlines for the fixed rIC3 configuration. This is a bounded coverage
result. A deadline is not a measured completion time, and it is not an unsafe
verdict. The structural route has a different, decision-only output contract.

Independent CNF proof replay strengthens confidence in the supplied formulas.
Parsing the original circuit, constructing the witness obligations and converting
them to CNF remain trusted. Learning to identify that boundary is part of learning
the result, not an optional qualification after the experiment.

## A useful stopping point

You are ready to discuss this construction when you can:

1. Derive the seed-period tests and explain why an odd return gives safe parity.
2. Check initiation, each transition case and safety, including the zero branch.
3. Explain why total history updates preserve every original input behavior.
4. Trace a candidate to native acceptance and then to retained CNF proof replay.
5. State both the width-8 observation and its limits without claiming a general
   speedup, a new history principle or a benefit for the complete orbit engine.

The [source dossier](../research/contribution_v1/SOURCES.md) records the separate
priority assessment. Classical methods support a valid construction; they do not
by themselves settle the exact combination's originality or significance. The
current checkpoint is a completed integration study, with standalone research
readiness uncleared. The repository is an educational and reproducibility
resource; its content is not aimed for publication. See
[status and collaboration](../README.md#status-and-collaboration) for contact
information.

---

[Overview](../README.md) · [Book route](LEARNING_PATH.md) · [Tutorial](TUTORIAL.md) · [Lab](REPRODUCING.md)
