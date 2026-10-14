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

The latest local `.venv` complete supported suite passed **173 tests in 130.93 seconds**,
with zero failures, errors or skips. This includes 20 new deterministic regression
cases (19 failed before repair), existing concurrent CAS and unborn/closing-commit
behavior, both isolation directions and 55 retained original tests. All 393
original test/support files retain their hashes. An initial run had 171 passes and
two failures because the maintainer placed pytest's fixtures inside this Git
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

The sole successor is a **stop pending separate owner authorization for a
noncritical pilot**. It grants no pilot or consumer access. [Repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14)
is author validation, not another independent review. Do not queue the completed
[review](reviews/V1-RECOVERY-REVIEW.md) again. No remote publication is authorized,
and final v1 is not complete. The old sole-writer/NXR-GSR NEXT is superseded.

Read the exact current action with `./cli/ok -C . next`. Only `next-write` publishes
canonical `docs/NEXT.md`; do not regenerate a prompt from this summary or ROADMAP.
At turn start verify physical cwd, Git root, branch, HEAD and configured name.
Use disposable repositories for all isolation tests. Current user repository
scope overrides inherited handoffs. Validation belongs in
`docs/validation/V1-RECOVERY.md`; update this handover and ROADMAP together.
