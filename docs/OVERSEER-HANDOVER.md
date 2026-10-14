# Overseer Kit — bounded v1 handover

Authority: [scope reset](decisions/V1-SCOPE-RESET.md), 2026-10-14.
Active implementation: `overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, reconciled base `d47291d`.
Both older dirty worktrees remain untouched.

Preservation and local Muse/base reconciliation are complete. The independent
architecture/completed-build review of `d8f10d8` against `d47291d` is complete with
an original **FINDINGS** verdict, preserved unchanged. The subsequent repair of
R1/R2 at base `333f81e9bf847dcd418b305b931b1279da3c7ade` is complete: writer context
is rechecked after locking and before replacement; closing-commit checks use one
captured commit ID, and readers recheck context before output.

The latest local `.venv` complete supported suite passed **173 tests in 107.49 seconds**,
with zero failures, errors or skips. This includes 20 new deterministic regression
cases (19 failed before repair), existing concurrent CAS and unborn/closing-commit
behavior, both isolation directions and 55 retained original tests. All 393
original test/support files retain their hashes. An initial installation/rollback
validation run had 171 passes and two failures because the maintainer placed
pytest's fixtures inside this Git
checkout; those tests require a nonrepository parent. The unchanged complete suite
passed after moving fixtures to a new `/private/tmp` directory. Both runs are
recorded. Historical failures remain unresolved; no failure was waived as an
environment restriction.

Clean source installation and current-to-previous-to-current rollback are complete:
**43 disposable exercise checks passed**. Committed source `348e0f3` → `333f81e` →
`348e0f3` came only from this worktree's Git objects. Fresh symlinked venvs used
offline PyYAML from the local `.venv`. Source changed at a fixed installation root;
commands refused until explicit sync, which preserved UUID, living documents and
NEXT. Recovery restored the current runtime digest. The previous build still has
known R1/R2 limitations; rollback operability does not clear them. See
[reproducible evidence](validation/V1-RECOVERY.md#clean-source-installation-and-rollback--2026-10-14).

The owner separately authorized the **newly created test-repository pilot** at
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-v1-pilot-20261014`. It is complete:
branch `pilot/overseer-v1-20261014`, UUID `8520ff03-a248-4dbd-8f21-ec53de6c967b`,
final local HEAD `50b5a19b7d6f1c964368140ed0dc3dc91504de16`. It uses this recovery
installation's conventional `.venv` and unchanged repaired runtime. Init without
hooks, status, NEXT, sync dry-run/sync, explicit-context digest-checked publication,
stale-writer refusal and readback after two closing commits passed. The one
documentation task produced `docs/PILOT-OPERATIONS.md` in the pilot. Both pilot
summaries and its canonical completion stop are committed; final status is clean.

[Pilot evidence](validation/V1-RECOVERY.md#newly-created-test-repository-pilot--2026-10-14)
records the exact commits, digests, supported run and preservation checks. This
was one maintainer in one session in a new repository; no existing consumer
migration, sustained use, independent operator, consumer hooks or provider access
was exercised. The pilot has no remotes and Git hooks are disabled. An incorrect
digest supplied during recovery readback correctly refused; corrected readback
passed. This operator input error is recorded, not a waived product failure.

The [final certification adjudication](validation/V1-CERTIFICATION.md) is
**CERTIFIED** for repository-bound source v1 for local POSIX Git repositories
under the trusted-host model, validated on Python 3.14.4, with the public
`status`, `init`, `sync`, `next` and `next-write` surface. R1/R2 are resolved for
this claim on [author repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14);
the original independent **FINDINGS** verdict remains unchanged. Historical
baseline **1,391 passed / 104 failed** remains unresolved and was not rerun.

The sole successor is a **certified completion stop**. Release or distribution
requires a separate owner decision. No further implementation task is selected
or authorized; certification grants no release, merge, push, publication or
deployment authority. Do not repeat the completed
[review](reviews/V1-RECOVERY-REVIEW.md), installation/rollback or pilot.
Packaged installation, other platforms, existing-consumer migration, sustained
or multi-user operation, consumer hooks and providers remain outside the claim.
The old sole-writer/NXR-GSR NEXT is superseded.

Read the exact current action with `./cli/ok -C . next`. Only `next-write` publishes
canonical `docs/NEXT.md`; do not regenerate a prompt from this summary or ROADMAP.
At turn start verify physical cwd, Git root, branch, HEAD and configured name.
Use disposable repositories for all isolation tests. Current user repository
scope overrides inherited handoffs. Validation belongs in
`docs/validation/V1-RECOVERY.md`; update this handover and ROADMAP together.
