# Qualification before the CI portability corrections

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

[BEFORE_EXIT_TRANSITION_RETRY.tar.gz](BEFORE_EXIT_TRANSITION_RETRY.tar.gz)
preserves the subsequent qualification, supervisor and protocol freeze from
PR commit `86addf76fa6b86f8f415ddb479174cc3d6c0ee36` (303 files). Archive SHA-256:
`fe505781177f4d7d04d56a3da0c4f0c0c3c723600444e9eff19e5d26158bd410`.

The final correction handles descriptor access being revoked just before exit
becomes visible in process status. It retries fresh status reads for at most
50 ms, yielding for up to 1 ms between reads. A denial is ignored only after
the process vanishes, or its unchanged start time identifies a terminal process
with at most one remaining thread. A reused identifier or persistent live
denial still fails closed. Retry time counts toward the total workflow deadline
and the recorded polling gap; it is not an extra solver allowance.

The current qualification directory contains four fresh executions with the
final supervisor, followed by independent proof/counterexample replay.
The protocol was frozen again before any comparative measurement. No benchmark
case, resource allowance, acceptance condition or solver strategy changed.
The earlier observations were not rewritten to make the new source hash match.
