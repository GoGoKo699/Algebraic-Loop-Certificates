# Complete algebraic orbit certificates — research module

**Prime-field invertible affine dynamics; one supplied initial state and one
full-state target.** This module develops a certificate system for both outcomes:
no target visit, or every visit described by one exact arithmetic progression.

It is experimental. The root `alc.certificate.v1` format remains unchanged and
positive-only. This module's format is `alc.algebraic-decision.v1`; never submit
it to the old CLI and assume that negative evidence has been added to production.
The checker uses checked algebraic witnesses, not a trajectory listing. The
reference producer uses trial factorization and baby-step/giant-step searches;
these can still be expensive. No general fast classical discrete logarithm
algorithm is claimed.

## Read the scientific material

[THEORY.md](THEORY.md) gives the soundness/completeness argument, including
repeated factors, all negative outcomes, and polynomial certificate/checker
bounds. [FORMAT.md](FORMAT.md) gives the executable contract and trust boundary.
[LITERATURE.md](LITERATURE.md) maps the background, direct predecessors, and
permitted claims. [RESEARCH_STATUS.md](RESEARCH_STATUS.md) separates completed
mathematics and experiments from the unresolved novelty and usefulness audit.
[CLAIMS.json](CLAIMS.json) is the machine-readable evidence ledger.

**The scientific work needed for submission is not yet complete.** Manuscript
writing remains on hold. These documents are derivations, evidence and research
records, not drafts of manuscript sections. Scientific claims must follow established results and evidence.

## Reproduce

Python 3.10+; standard library for the checker and core tests. From the root of
a repository checkout or the supplied labeled source subset:

```sh
python research/complete_orbits_v1/verify.py
python -O research/complete_orbits_v1/verify.py
```

The optional native comparison requires an already installed SymPy:

```sh
python research/complete_orbits_v1/verify.py --sympy
```

No command installs dependencies or downloads data. Temporary output paths are
used; the saved reports are not replaced. The recorded native comparison used
SymPy 1.14.0 and checks 81 factorizations and 300 scalar cases, not matrix-orbit
runtime or program-analyzer performance.

The core audit checks 6,205 state/target cases: the 4,834-case baseline family,
273 repeated-factor cases, 1,093 mixed-factor cases, and five named fixtures.
Some fixtures overlap earlier families; these are executed comparisons, not a
count of distinct mathematical problems. It independently enumerates the small
test trajectories; neither the producer nor the checker traverses those orbits.
Every one of the 2,374 positive results is translated to the unchanged primary
format and rechecked. Additional controls cover arbitrary elements of small
unipotent rings, irreducibility, malformed proofs and exhausted budgets.

## Inspect an example

The following code only consumes a recorded fixture after validating it:

```python
import gzip
import json
from pathlib import Path
from research.complete_orbits_v1.checker import decide

path = Path('research/complete_orbits_v1/expected.json.gz')
fixture = next(f for f in json.loads(gzip.decompress(path.read_bytes()))['fixtures']
               if f['name'] == 'congruence_conflict')
answer = decide(fixture['problem'], fixture['certificate'])
print(answer['status'], answer['reason'])
# unreachable incompatible_field_congruences
```

Over F13, reaching `(10,12)` from `(1,1)` under multiplication by `diag(4,5)`
would require both `t=5 mod 6` and `t=2 mod 4`. Their parity constraints conflict.
The theorem handles not only this easy example but also repeated polynomial
factors, where these field-level congruences alone are insufficient.
`consumer.query(problem, certificate, low, high)` rechecks the proof, then counts
all hits in the inclusive interval (zero for a verified unreachable target).
It also returns the first/last interval hit and the next hit at or after `low`.
This uses the complete verified schedule, not a simulator loop up to `high`.

## Integration and limits

The provided patch is additive: the research directory and
`tests/test_complete_orbit_research.py`. The latter joins the normal test
discovery when integrated. No existing source, schema, example, manifest, license
or historical evidence is overwritten. The new manifest pins the primary parser
and checker on which this module relies, as well as all added research files.
An intentional primary change requires reviewing and rerunning this audit.

The delivery receipt records the exact public baseline and which local or
remote checks were actually completed. The research format must undergo an
explicit compatibility review before promotion to the primary API.

There is no verified program frontend, arbitrary-guard support, extension-field
input format, singular-map/transient support, or formal proof-assistant
verification. The mathematical certificate bound is not a bound on the cost of
finding all its algebraic witnesses. Current default resource limits are an
implementation policy, not a change in the theorem's quantified domain.

## Subsequent comparison

[The closer-prior audit](../PRIOR_WORK_COMPARISON_02.md) and [native scalar comparison](../scalar_comparison_v1/README.md) update the novelty and cost assessment. The large scalar examples are not performance advantages. The raw original result bytes are retained in deterministic gzip form; RESULTS_SUMMARY.json provides a readable summary and the uncompressed digest.
