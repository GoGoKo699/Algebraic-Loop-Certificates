# Fixed native model-checking comparison

27 September 2026. Fix these cases and limits before running the native tool.
The full source-aware experiment is narrower than general AIGER verification.

- Corpus: `tniessen/aiger-safety-properties` at
  `c8efd0251c0548dd46168db8410e6777c5f82b73`, `lfsr-period/`.
- Fixed subset: widths 2, 4, 8, 12, 16, and 24; the raw upstream bad-output
  property, inputs, zero-initialized latches and reseeding semantics are retained.
- Native solver: official Berkeley ABC at
  `ab2139ee0c418f54136deb4e8e89eeea3b87efc8`, its `pdr` command.
- Format conversion: official AIGER `aigtoaig` at
  `039ec1a2cc37d3093ac35c4b6df65336b346f409`, ASCII to binary AIGER.
- One cold solver process per case, a 10-second external wall-time limit and
  1 GiB address-space limit. Preserve conversion commands, exact input/output
  hashes, stdout, stderr, exits and timeouts. No post-result tuning of cases,
  limits, or solver strategy.
- Build failures and compilation logs remain separate from solver verdicts.
  If an optional dependency configuration cannot link, use the upstream default
  configuration without modifying source, and record that build adjustment.
- A timeout is inconclusive, never a claim of unsafety or intrinsic hardness.
  A SAFE verdict is a native result, not independent replay of its proof.

This is a small feasibility probe of one generic native method. It cannot
establish superiority over all hardware verifiers. In particular, the strongest
source-aware comparator is an ordinary odd-order test of the linear core, once
the source-to-core reduction is justified. A squarefree companion polynomial
with nonzero constant coefficient proves odd order in characteristic two.
The independent checker must compare to that route too, not only to PDR.

The positive integration question is whether the compact odd-order argument
can be checked against the actual raw benchmark gates and full input-dependent
wrapper. It is not whether maximal-period algebra is new. Rejecting an unmatched
wrapper or a failed supplied witness gives no unsafe verdict. Manuscript work,
general frontend claims, and scientific-priority claims remain out of scope.
