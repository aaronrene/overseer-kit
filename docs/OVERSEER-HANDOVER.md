# Overseer Kit — bounded v1 handover

Authority: [scope reset](decisions/V1-SCOPE-RESET.md), 2026-10-14.
Active implementation: `overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, reconciled base `d47291d`.
Both older dirty worktrees remain untouched.

Preservation and local Muse/base reconciliation are complete. The independent
architecture/completed-build review of `d8f10d8` against `d47291d` is complete with
**findings; milestone acceptance is blocked**. Its supported suite passed 153
tests with zero failures or skips, including the 34-case isolation matrix in both
directions. All 393 original test/support files match the base; historical failures
remain unresolved rather than silently passing.

The sole successor repairs [review R1/R2](reviews/V1-RECOVERY-REVIEW.md): a writer
can publish stale context after waiting for its lock, and the NEXT reader can mix
parents and file bytes from different revisions. Add deterministic regressions
and run the full supported suite. No product changes were made during review.
Do not queue this completed review again. Clean installation/current-previous
rollback remains pending after repair. No pilot or publication is authorized,
and final v1 is not complete. The old sole-writer/NXR-GSR NEXT is superseded.

Read the exact current action with `./cli/ok -C . next`. Only `next-write` publishes
canonical `docs/NEXT.md`; do not regenerate a prompt from this summary or ROADMAP.
At turn start verify physical cwd, Git root, branch, HEAD and configured name.
Use disposable repositories for all isolation tests. Current user repository
scope overrides inherited handoffs. Validation belongs in
`docs/validation/V1-RECOVERY.md`; update this handover and ROADMAP together.
