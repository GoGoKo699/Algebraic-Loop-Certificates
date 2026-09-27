# Storage amendment for a fresh bounded comparison

27 September 2026. This decision precedes the new comparison but follows the
observations in [Gate 16](../BOUNDED_COMPARISON_GATE_16.md). It is an
**outcome-informed protocol repair**, not a blind preregistration. Manuscript
preparation remains on hold.

## Decision and rationale

Use separate sampled acceptance budgets of **64 MiB for raw artifacts** and
**64 MiB for the explicitly identified metadata and logs**. Their sum supplies
a conservative 128 MiB all-file guard. Keep every other scientific condition,
including the original raw-artifact budget, fixed.

The first study stopped after 32 of 54 trials. Its final trial had 67,098,722
raw bytes and 71,614 metadata/log bytes: raw artifacts were below 64 MiB while
their sum exceeded it. The old guard therefore made the usable raw-artifact
allowance depend on the amount of diagnostic evidence. That suspension remains
an execution issue under its original protocol. It is neither reclassified nor
used as an eligible resource-limit observation.

Separating the two budgets lets the raw-artifact criterion retain its stated
meaning while bounding the cost of observation. The metadata budget reuses the
existing 64 MiB control scale. It is a simple shared convention, not a claim of
minimality, optimality, or a value inferred from the observed 71,614 bytes. In
particular, the budget does not guarantee that every possible collection of
individually bounded streams and JSON records will fit.

Adding only the observed number of bytes as padding would fit the amendment to
one outcome. Dropping logs would lose evidence. Leaving metadata unbounded
would remove an execution safeguard. The separate fixed budget avoids those
choices while applying equally to all routes. It increases permitted combined
storage from 64 to 128 MiB; results from the two policies must remain separate.

## Classification and failure boundaries

The exact path allowlist in the [executable protocol](EXECUTABLE_PROTOCOL.md)
defines metadata. File extensions alone do not grant this classification.
Unknown files, all files in the isolated temporary directory, and every visible
open deleted file count as raw artifacts. Recognized atomic JSON copies count
as metadata while present; after deletion, an open copy is conservatively raw.
This is a recorded rule for the inspected research programs, not protection
against hostile programs that rename outputs or escape their trial directory.

Both component budgets and the combined guard are sampled acceptance limits,
not instantaneous aggregate filesystem quotas. Every observed excess remains
disqualifying after deletion or shrinking. The hard per-file limit stays
64 MiB, and each stdout/stderr capture stays capped at 1 MiB.

Metadata exhaustion has reason `metadata_limit` and remains an execution issue.
It suspends the study even when raw excess or a deadline is also observed.
Output truncation, correctness failures, failed proof replay, incomplete cleanup,
and unattributed failures likewise cannot become resource-based coverage wins.
Only a declared deadline or observed raw-artifact excess without conflicting
failure evidence allows the predetermined sequence to continue with UNKNOWN.

## Fresh sequence and stopping commitment

Preserve the entire first protocol, freeze, qualification, 32-trial prefix,
classification, report and retained evidence byte-for-byte. Freeze the amended
sources, exact classification rule, budgets, inputs and executables before any
new comparison measurement. Regression checks must exercise both components,
unknown and temporary paths, and simultaneous failures.

Execute one fresh whole 54-trial sequence with the original six cases, explicit
exporter hints, pinned binaries, commands, seed, route order and three
repetitions. Do not resume at trial 33, combine repetitions across policies,
selectively repeat a trial, or enlarge the corpus. Every new outcome is retained.
A new infrastructure or correctness issue suspends again; it does not authorize
an automatic rerun or another budget adjustment.

The original three-of-three added-coverage rule and completed-negative stopping
rule still apply. A positive result would support only a comparison with the
fixed qualified configuration on this hand-designed corpus, followed by a
focused significance and priority assessment. It would not establish general
solver superiority, a new algebraic theorem, or a benefit for the complete
orbit engine. A completed negative result closes this benefit route without
post-hoc replacement by a timing claim.
