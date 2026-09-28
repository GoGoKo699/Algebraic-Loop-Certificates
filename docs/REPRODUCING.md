# A reader's reproducibility lab

[Overview](../README.md) · [Book route](LEARNING_PATH.md) · [Tutorial](TUTORIAL.md) · [Lab](REPRODUCING.md)

Use this lab alongside Manna and Pnueli's *Temporal Verification of Reactive
Systems: Safety*. For each example, identify the state, initial condition,
transition relation and claimed property before inspecting its certificate.
The arithmetic example and the hardware safety study have different contracts.
The [learning path](LEARNING_PATH.md) and [worked tutorial](TUTORIAL.md) provide
the reading sequence and proof details for this lab.

## 1. Prepare the checkout and run the full check

Run every command below from the repository root, where `verify.py` resides.
Use Python 3.10 or later with its standard library; no `pip install`, solver
download or native build is needed for the retained-evidence checks.

```sh
python --version
python verify.py
```

The complete suite targets **Linux**. The [CI workflow](../.github/workflows/verify.yml)
runs this command on `ubuntu-latest` with Python **3.10 and 3.12**. Supervisor
controls use Linux CPU affinity, process limits and `/proc`; the whole suite
is not promised to run on Windows or macOS. The production arithmetic CLI
below does not need those Linux controls.

At this documented checkpoint, expect **113 tests**, `OK`, and:

```text
PASS: source hashes, regression tests, and exact 4,772-case finite audit.
This is a positive-certificate prototype, not an advantage or novelty certificate.
```

The command checks committed hashes, starts tests in a fresh Python process,
and regenerates the small finite audit in temporary storage for byte comparison.
It also exercises small supervisor controls and replays retained research proofs.
It does not rerun the 54 native comparison trials. Allow time and temporary
disk space for archive extraction and proof replay; this is more than a unit-test
smoke check. Keep the complete checkout, including all archive-part files.

## 2. Verify one complete arithmetic hit set

Inspect [the problem](../examples/fibonacci_f7/problem.json) and
[its separate certificate](../examples/fibonacci_f7/certificate.json).
The recurrence is `(x,y) -> (x+y,x) mod 7`, with initial state `(1,0)`
and full-state target `(4,5)`.

```sh
python -m alc verify \
  --problem examples/fibonacci_f7/problem.json \
  --certificate examples/fibonacci_f7/certificate.json
```

Expected JSON includes `status: "valid"`, `claim: "complete_positive_hit_set"`,
`first: 11` and `period: 16`. Thus `t0 = 11`, `r = 16`, and **every** hit is
`11 + 16*j` for an integer `j >= 0`. This is stronger than observing one hit.

Read the [positive-certificate proof](SPECIFICATION.md): the checker establishes
the field and inverse witness, a return at `r`, nonreturns at `r/q` for every
proved prime divisor `q` of `r`, and the target at `t0`. The complete proved-prime
factorization matters. A return alone need not be the least return.

Now ask about a distant inclusive time window:

```sh
python -m alc query \
  --problem examples/fibonacci_f7/problem.json \
  --certificate examples/fibonacci_f7/certificate.json \
  --from 1000000000000000000000000000000 \
  --through 1000000000000000000000000000100
```

Expect `window.count: 6`, first hit `10^30 + 11` and last hit `10^30 + 91`.
The command verifies the certificate again, then computes with the progression;
it does not simulate `10^30` loop iterations. See the [CLI contract](FORMAT.md)
for exact JSON fields, bounds and exit codes.

Optional: create and check a fresh candidate in a new temporary directory:

```sh
python - <<'PY'
from pathlib import Path
import subprocess
import sys
import tempfile
with tempfile.TemporaryDirectory(prefix="alc-reader-") as directory:
    candidate = str(Path(directory) / "candidate.json")
    problem = "examples/fibonacci_f7/problem.json"
    subprocess.run(
        [sys.executable, "-m", "alc", "produce",
         "--problem", problem,
         "--output", candidate,
         "--max-steps", "1000"],
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "alc", "verify",
         "--problem", problem,
         "--certificate", candidate],
        check=True,
    )
PY
```

This bounded enumerating producer is distinct from the independent checker.
Candidate creation is not acceptance; budget exhaustion supplies no certificate.
The temporary example leaves the committed artifacts unchanged.

## 3. Follow the safety argument into a hardware witness

Read the [odd-order contract](../research/odd_order_witness_v1/CONTRACT.md)
and [its proof](../research/odd_order_witness_v1/THEORY.md). Here the trusted input
is an original AIGER circuit with unrestricted inputs, including reseeding.
The witness adds history state and a seed-dependent period predicate.

Apply the book's safety-proof viewpoint: establish the invariant initially,
preserve it across every transition, and use it to exclude the bad condition.
History must also preserve the original behaviors; restricting the original
inputs would change the problem. These proof tasks do not replace the actual
native interface's nine recorded acceptance obligations.

```sh
python -m research.odd_order_witness_v1.verify
```

Expect the checkpoint's `PASS` message and **37 completed CNF proofs** replayed:
27 from three accepted witnesses and ten completed before two bad selectors
were rejected. This command also runs finite mathematical/source controls and
Python candidate-reproducibility checks. It invokes no native solver.
The rejected selectors are invalid witnesses for safe models, not reachable
source counterexamples. These earlier controls are separate from Gate 17.

## 4. Replay the completed comparison's retained evidence

```sh
python -m research.completion_v2.verify_qualification
python -m research.completion_v2.verify_study
```

Qualification checks **23 completed proofs and two negative SAT assignments**
from four tiny controls. The study command independently reconstructs the
[retained report](../research/completion_v2/STUDY_REPORT.json): `status: "complete"`,
`observed_trials: 54`, `proofs_replayed: 180`, and
`primary_outcome: "added_coverage"`. Forty-five of those proofs precede stopped
exporter solves; partial completed proofs do not make a whole witness accepted.

The verifier discovers the distributed archive parts, checks their hashes,
reassembles and extracts them in temporary storage, then checks the evidence.
It validates source bindings, trial order, outcomes, commands and proof contents.
Neither command constructs a new study witness or launches a native tool.

[Gate 17](../research/BOUNDED_COMPARISON_GATE_17.md) reports three accepted
exporter witnesses at width 8 versus three rIC3 deadline UNKNOWN outcomes.
Both witness routes pass widths 2 and 4; neither passes widths 12, 16 and 24
within the fixed budgets. The structural reference decides all six widths
but supplies a Boolean decision, not the required externally accepted witness.
A deadline is not a completion time, so it does not yield a measured speedup ratio.

[Gate 16](../research/BOUNDED_COMPARISON_GATE_16.md) remains a separate suspended
32-trial prefix with 115 completed proofs and an unevaluated primary criterion.
Its trials are not pooled with the fresh amended Gate 17 sequence.
[Gate 18](../research/CONTRIBUTION_ASSESSMENT_18.md) retains an integration case
study; priority and significance for a standalone contribution remain uncleared.

## 5. Connect the claims, implementation and evidence

1. **Complete positive hit set for one prime-field affine recurrence.**
   Inspect [`alc/checker.py`](../alc/checker.py), especially `verify` and
   `prime_proofs`. Read the [specification](SPECIFICATION.md) and
   [finite audit](../evidence/README.md).

2. **Inclusive window over an accepted progression.**
   Inspect `window` in [`alc/consumer.py`](../alc/consumer.py).
   Read the [format contract](FORMAT.md) and the six-hit example above.

3. **Exact seed period and an inductive history extension.**
   Inspect the [witness producer](../research/odd_order_witness_v1/produce.py).
   Read the [theory](../research/odd_order_witness_v1/THEORY.md) and checkpoint
   controls.

4. **Independent checking of retained CNF proofs.**
   Inspect the [LRAT checker](../research/proof_interface_v1/lrat.py) and
   [native replay](../research/odd_order_witness_v1/verify_native.py).

5. **Accepted-witness coverage under a fixed resource policy.**
   Inspect the [study verifier](../research/completion_v2/verify_study.py).
   Read the [Gate 17 report](../research/completion_v2/STUDY_REPORT.json) and
   [assessment](../research/CONTRIBUTION_ASSESSMENT_18.md).

The production checker trusts the supplied recurrence, Python and its own exact
arithmetic implementation. It does not prove that a larger program was correctly
translated into that recurrence. Its supported domain remains invertible affine
maps over prime fields with full-state targets, not arbitrary program guards.

For hardware evidence, independent LRAT replay proves the **retained CNFs**
unsatisfiable. Original-model parsing, witness mapping, obligation construction
and AIGER-to-CNF translation remain trusted even when every proof replays.
Hashes bind bytes; they are not signatures or authenticated execution records.
Tests corroborate these implementations rather than mechanically proving them.
Timeout, rejection and unsupported input are distinct from mathematical falsity.

## Advanced: a fresh native execution is a different task

Rebuilding pinned native tools and measuring new runs requires the documented
[native setup](../research/odd_order_witness_v1/NATIVE_PROTOCOL.md) and
[amended execution protocol](../research/completion_v2/EXECUTABLE_PROTOCOL.md).
Those steps involve external toolchains, Linux resource supervision and new
output directories. They are not prerequisites for this lab and are not what
the replay commands reproduce. Preserve the frozen sources, protocols and
artifacts; the current [work order](../work_orders/CURRENT.md) schedules no
new experiment. A local replay's elapsed time is not a new benchmark observation.

---

[Overview](../README.md) · [Book route](LEARNING_PATH.md) · [Tutorial](TUTORIAL.md) · [Lab](REPRODUCING.md)
