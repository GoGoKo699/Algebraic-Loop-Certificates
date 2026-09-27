# Qualification before the CI portability correction

[BEFORE_CI_PORTABILITY_FIX.tar.gz](BEFORE_CI_PORTABILITY_FIX.tar.gz) preserves
all 301 original qualification files, the exact original resource supervisor,
and the first protocol freeze from PR commit
`56d230b0e4e987e66abb16855a1be3b3460e1221` (303 files total). Archive SHA-256:
`718eabd8feb799b5ac45ab829f96f9194275954cd2f4cfa12fe3b96c0c8deb4d`.

The initial local qualification passed. Unprivileged CI then exposed a race:
reading a just-exited child's descriptor directory can raise PermissionError.
The corrected supervisor ignores that denial only for a vanished process or a
same-identity terminal process whose descriptors have closed; live or reused
process identifiers still fail closed. A deterministic regression covers both
branches.

The current qualification directory contains four fresh executions with the
corrected supervisor, followed by independent proof/counterexample replay.
The protocol was frozen again before any comparative measurement. No benchmark
case, resource allowance, acceptance condition or solver strategy changed.
The earlier observations were not rewritten to make the new source hash match.
