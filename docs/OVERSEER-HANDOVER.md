# Overseer Kit v1 handover

2026-10-09 — **Bounded local legacy-mirror reconciliation is implemented;
remote publication remains held.** `mirror reconcile` now imports an explicitly
reviewed local history bundle into a new engine-owned bare target and creates a
source-exact commit whose first parent is the approved legacy mirror and second
parent is the approved GitHub base. It preserves both histories and retains the
ordinary fresh-target refusal, source/target ownership, exact delta, correspondence,
drift and retry checks. Later exports use one verified prior mirror parent.

Git delivery has a per-command credential helper restricted to the approved GitHub
HTTPS path and physical `gh` executable. Credentials stay in memory/Git pipes;
redirects and inherited askpass programs are disabled. Fixture credentials validate
the wiring. Actual remote authentication and write acceptance remain unvalidated.

The [publication decision](decisions/V1-MUSE-PUBLICATION.md) and
[mirror runbook](../MUSE-BRIDGE-WORKFLOW.md) describe the operation and its limits.
The exact committed Git candidate, reconciled Muse revision/snapshot and disposable
projection identities are frozen together in
[candidate.json](../../RECOVERY-RUNS/20261009-mirror-reconciliation/candidate.json).
[source-latest.json](../../RECOVERY-RUNS/20261009-mirror-reconciliation/source-latest.json)
contains every source path/hash/mode, executable list and the complete resulting
delta; the paired projection record verifies all of them. These records are made
after the commit so the candidate does not contain its own hash.

The starting [110-path delta](decisions/V1-MUSE-PUBLICATION-DELTA.json) is retained:
46 additions, 32 modifications, 32 removals. A disposable projection of the actual
855-file starting candidate passed against both retained GitHub histories at
`3e21496f7c4eab64b6d9ab3f868c5cdcaf8cfcde` and
`d47291d5d9030de5ebef713da95efa978c4d8c6e`, including all ten executable paths,
both ancestry relationships, verification and no-change retry. The new candidate
adds the six implementation/test/decision files and includes all reviewed edits.
No original file content was automatically merged from GitHub.

| Local matrix | Actual final result | Pytest duration |
| --- | --- | --- |
| Git-only, Python 3.11.15 | **131 passed** | 52.59s |
| Git-only, Python 3.14.4 | **131 passed** | 61.28s |
| Combined Muse, Python 3.14.4 | **264 passed** | 360.10s |

All final rows have zero failures/errors/skips. The matrix adds 14 credential
protocol tests and 25 reconciliation tests. The validation record retains fixture
corrections and earlier runs; no unresolved supported-test failure is hidden.
Unchanged closed reviews were not repeated. No hosted CI was dispatched. Previous
[hosted run 37948400522](https://github.com/aaronrene/overseer-kit/actions/runs/37948400522)
remains evidence only for Git `2d689a8398002ce667743ac7fefd12291b8973bf`
(117/117/225 passes), not the new candidate.

Exact recovery wheel/source pins and the repository Actions URL are unchanged.
The original rc5 archive remains unavailable; this recovery is not an upstream
release. Git-only remains a permanent mode without Muse installation or login;
Muse adoption stays explicit. The recovery runtime is now
`d86f8903fb177f3109da914fa43e4223bdd3100f64c8e4fefd9cbc8385cc9133`; local `sync` refreshes its binding without hooks.

Original refs/edits, original identity/trust/configuration and the clean held
release `06f988e5a078ede81c9dc664520833980a9a19a3` remain preserved. The existing
isolated Muse feature advances locally; its main stays at the observed staging
base. The proposed real delivery paths remain absent. No remote write or query,
main merge/push, PR, tag/release, real mirror delivery, consumer access, production
trust reset, automatic hook or OCI operation is included. No complete-product
readiness claim is made.

The [validation closeout](validation/V1-RECOVERY.md#local-legacy-mirror-reconciliation--2026-10-09)
and `../RECOVERY-RUNS/20261009-mirror-reconciliation/` retain actual evidence.
New remote operations require explicit owner authorization for the frozen resulting
candidate. Both summaries were refreshed together; canonical `docs/NEXT.md`,
published only through `next-write`, carries the remaining owner decision.
