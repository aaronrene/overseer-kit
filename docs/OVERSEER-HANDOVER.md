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

The local `.venv` complete supported suite passed **173 tests in 132.21 seconds**,
with zero failures, errors or skips. This includes 20 new deterministic regression
cases (19 failed before repair), existing concurrent CAS and unborn/closing-commit
behavior, both isolation directions and 55 retained original tests. All 393
original test/support files retain their hashes. Historical failures remain
unresolved; no failure was waived as an environment restriction.

The sole successor is clean installation/current-previous rollback validation in
disposable fixtures. [Repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14)
is author validation, not another independent review. Do not queue the completed
[review](reviews/V1-RECOVERY-REVIEW.md) again. No pilot or remote publication is
authorized, and final v1 is not complete. The old sole-writer/NXR-GSR NEXT is
superseded.

Read the exact current action with `./cli/ok -C . next`. Only `next-write` publishes
canonical `docs/NEXT.md`; do not regenerate a prompt from this summary or ROADMAP.
At turn start verify physical cwd, Git root, branch, HEAD and configured name.
Use disposable repositories for all isolation tests. Current user repository
scope overrides inherited handoffs. Validation belongs in
`docs/validation/V1-RECOVERY.md`; update this handover and ROADMAP together.
