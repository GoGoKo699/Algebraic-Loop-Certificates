# Existing proof interface, native provenance and limitations

Primary sources inspected 27 September 2026. This checkpoint uses an existing
certificate interface; it does not introduce an ALC-only format and call that
an external verification result.

## Certifaiger witness circuits

The original model and a candidate witness are separate AIGER circuits. Mapped
shared variables establish correspondence; additional witness state may support
an inductive invariant. The checker constructs simulation and induction
obligations, including an implication to the original safety property. Thus
the witness may strengthen the property while preserving the original task.

- Froleyks, Yu, Preiner, Biere and Heljanko,
  [Introducing Certificates to the Hardware Model Checking Competition](https://cca.informatik.uni-freiburg.de/papers/FroleyksYuPreinerBiereHeljanko-CAV25.pdf),
  CAV 2025, [DOI 10.1007/978-3-031-98668-0_14](https://doi.org/10.1007/978-3-031-98668-0_14).
  Definition 1 and its soundness theorem give the five safety obligations and
  the stratified-reset condition. The paper documents actual competition use.
- Froleyks and Yu,
  [Hardware Model Checking Certification with Certifaiger and Cerbtora](https://froleyks.de/assets/pdf/Froleyks%20et%20al.%20-%202026%20-%20Hardware%20Model%20Checking%20Certification%20with%20Certifaiger%20and%20Cerbtora.pdf),
  IJCAR 2026, [DOI 10.1007/978-3-032-32589-1_17](https://doi.org/10.1007/978-3-032-32589-1_17).
  Describes model/witness parsing, obligation generation, AIG splitting and CNF
  translation as the concrete certification workflow.
- [Current format and tool documentation](https://github.com/Froleyks/certifaiger/blob/27d526e3e979074c3e92582768f577dc6eddb0da/README.org),
  git blob `c7f719cdd1424d101f32efae6b08358d9268f9ee`.
  This newer revision also includes liveness obligations. Our safety-only
  cases generate nine outputs: five safety checks and four trivial liveness
  checks. All nine are retained and checked, rather than relying on a paper's
  earlier output count.

The observed invocation runs unchanged native obligation-generator sources,
followed by the same splitting/CNF/SAT/proof-checking stages as the upstream
pipeline. Our bounded Python driver replaces shell orchestration; it does not
claim that the upstream `check` shell script itself was executed.

## Exact executed source pins

| Component | Repository and executed commit | Role |
|---|---|---|
| Certifaiger 10.3.0 | [Froleyks/certifaiger](https://github.com/Froleyks/certifaiger/tree/27d526e3e979074c3e92582768f577dc6eddb0da) | Model/witness mapping, reset stratification and obligation construction |
| AIGER | [arminbiere/aiger](https://github.com/arminbiere/aiger/tree/039ec1a2cc37d3093ac35c4b6df65336b346f409) | AIGER parser/library, `aigsplit`, `aigtocnf` |
| CaDiCaL 3.0.1 | [arminbiere/cadical](https://github.com/arminbiere/cadical/tree/c60730422e758ef1cebe7aeddf2dda31c996bf04) | SAT search and emitted ASCII LRAT |
| lrat-trim | [arminbiere/lrat-trim](https://github.com/arminbiere/lrat-trim/tree/adba6e61368e91957c79bf952b29800f05dbee51) | Independent native LRAT replay |

The inspected Certifaiger implementation is `src/certifaiger.cpp`, blob
`ad231ed4aa2f19a5ade9c683b8cffc7265c5f305`. Its upstream proof-checking script is
`scripts/check_unsat.in`, blob `edc3412deaec19f232a584b379425da384d42e4e`.
CaDiCaL's `src/lrattracer.cpp` has blob
`662280201b88ae461505a5d3254298f92a9a312e`; native `lrat-trim.c` has blob
`8bd5de0bdc2d6f4cc3b7c504aef04e6a7183b774`.

[BUILD_PROVENANCE.json](native/BUILD_PROVENANCE.json) records source trees,
tracked-source status, compiler versions, exact argument arrays and binary
hashes. CMake was unavailable in this environment, so the unchanged
Certifaiger/AIGER sources were compiled directly with GCC/G++ 13.3.0. Their
assertions remained enabled. CaDiCaL used its own `configure` and Makefile;
its SAT search is separately checked. No solver/checker source or binary is
vendored, and no tool-build timing was measured.

The driver uses `--lrat --no-binary --no-factor` to retain readable proof traces
without the factoring extension. Native lrat-trim accepted every completed
UNSAT trace. The independent repository checker accepts only the observed
positive-hint RUP subset and rejects unsupported syntax/rules. It replays all
45 positive-case proofs and the 12 completed proofs preceding the four negative
case rejections. Neither checker reruns SAT search during offline verification.

## What is still trusted

Independently replaying a CNF proof removes the SAT solver and witness producer
from the proof-search trust boundary. It does not verify the correspondence
between AIGER models and the generated CNFs. Certifaiger's parsing, variable
mapping, obligation construction, AIGER splitting/CNF translation, and the
executed checkers/runtime remain trusted. Source pins and hashes record that
boundary; they are not a formal proof of those components.

The [verified `lrat_isa` checker](https://github.com/lammich/lrat_isa) is an
existing option mentioned by Certifaiger. It was inspected as an alternative
but not built or executed here. Replacing LRAT replay alone with that tool
would still leave the native model-to-CNF translation outside its theorem.
Likewise, the [ACL2 AIGNET ABC wrapper](https://github.com/acl2/acl2/blob/master/books/centaur/aignet/abc.lisp)
uses a trusted clause processor; invoking that wrapper is not independent replay
of ABC's sequential proof. No such assurance shortcut is claimed in this audit.

## Benchmark bytes and untrusted witness producers

The original circuits come from
[tniessen/aiger-safety-properties](https://github.com/tniessen/aiger-safety-properties/tree/c8efd0251c0548dd46168db8410e6777c5f82b73),
commit `c8efd0251c0548dd46168db8410e6777c5f82b73`. Their provenance and MIT
license were preserved in the preceding checkpoint:
[source manifest](../aiger_lfsr_v1/SOURCE_MANIFEST.json),
[license](../aiger_lfsr_v1/upstream/LICENSE). Each native case retains an exact
copy of its input model; offline validation checks both the repository original
and the pinned upstream git-blob identity. No input is constrained to suppress
reseeding, and the ungated zero-state bad disjunct remains intact.

ABC's existing PDR forbidden-cube exports provide the two ordinary invariant
witnesses. The PLA-to-AIGER adapter is untrusted: the external checker must prove
its result against the original model. The history producer is also untrusted,
and its current primitive/common-period premise is stronger than odd order.
Ordinary primitive-polynomial reasoning can emit precisely the same witness.
Squarefreeness alone proves odd order but does not validate this single shared
phase modulus in a nonprimitive example; the theorem and controls retain that
distinction. The complete orbit compiler is not used by this integration.

The preserved [ABC export plan, observations and adapter](native/abc_export/README.md)
pin ABC to `ab2139ee0c418f54136deb4e8e89eeea3b87efc8`. Export runs took
0.0414 s and 0.3782 s for widths 2 and 4, respectively; initial adapter timing
was unmeasured, as recorded in [CONSTRUCTION_ABC.json](native/CONSTRUCTION_ABC.json).
[CONSTRUCTION_PHASE.json](native/CONSTRUCTION_PHASE.json) separately records
post-replay cold-process reconstruction observations of 0.0665 s, 0.0367 s and
0.1720 s for widths 2, 4 and 8. Their regenerated bytes equal the consumed
witnesses. Initial history-construction timings were unmeasured, and these later
single observations do not reconstruct the original end-to-end wall time.

## Replaying and interpreting the stored artifacts

`native/ARTIFACTS.json` maps original filenames to stored bytes. Files above
64 KiB use deterministic gzip with modification time zero; the manifest records
both raw and stored hashes/sizes. `RESULTS.json` keeps the actual raw measurements,
paths and argv unchanged. The original ABC-width-2 driver hashed input source
paths after copying; `runner_initial.py.txt` preserves that version. Every
consumed copy is independently checked to have exactly the recorded hash.
Later runs hash the consumed copies directly.

Run the portable offline replay from the repository root:

```sh
python research/proof_interface_v1/verify_native.py
```

To repeat native checking after building the pinned tools, point the driver to
a directory containing `certifaiger`, `aigsplit`, `aigtocnf`, `cadical` and
`lrat-trim`. It refuses to overwrite an existing output directory:

```sh
python research/proof_interface_v1/run_native.py --tools /path/to/native-bin --model research/aiger_lfsr_v1/upstream/fibonacci-08-0xb8.aag --witness research/proof_interface_v1/native/phase08/witness.aag --output /tmp/new-phase08-replay
```

The reported native pipeline time starts before obligation generation and
includes the SAT/proof checks, subprocess launches and recorded outputs. It
excludes tool building and witness construction. Construction/export observations
are separately labeled; a later reconstruction measurement is not retroactively
the cost of the initial run. Large proof traces, encoding cost and the remaining
trusted translation are material parts of the result, not omitted overhead.
