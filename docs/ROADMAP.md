# Overseer Kit — bounded v1 roadmap

Authority: [scope reset](decisions/V1-SCOPE-RESET.md), 2026-10-14.
The former sole-writer/NXR-GSR chain is historical and is not the living NEXT.

| Milestone | State |
| --- | --- |
| Preserve dirty checkout and reconcile local base | Complete |
| Repository-bound status/init/sync and canonical NEXT | Implemented; R1/R2 repaired |
| Supported tests and two-repository isolation matrix | Complete; 173 supported tests passed |
| Independent architecture and completed-build review | Complete; original findings verdict preserved |
| Repair writer context and reader revision findings | Complete; 20 deterministic regressions passed |
| Clean installation and current/previous rollback | Complete; 43 disposable exercise checks passed |
| Separately authorized noncritical pilot | Not authorized; sole successor is the stop/authorization gate |

The exact current action lives only in `docs/NEXT.md`; use `ok -C ROOT next`.
Update this summary and HANDOVER together. No release or remote operation is
authorized. See `docs/validation/V1-RECOVERY.md` for the supported test matrix and
results; historical suites are not silently treated as passing.

The [independent review](reviews/V1-RECOVERY-REVIEW.md) reproduced stale writer
publication after a Git context change and mixed-revision NEXT validation. Its
complete supported run passed 153 tests; those passes do not waive the findings
or establish final-v1 completion. The [subsequent repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14)
records both fixes and a 173-pass supported run without rewriting that verdict.
The completed review is not pending again. [Installation/rollback evidence](validation/V1-RECOVERY.md#clean-source-installation-and-rollback--2026-10-14)
records current `348e0f3` to previous `333f81e` to current, with explicit runtime
refresh and preserved UUID, living documents and NEXT. The previous build retains
known R1/R2 findings. The current complete supported suite passed **173 tests in
130.93 seconds**; an initial fixture-location error and the historical failures
remain recorded. A separately authorized noncritical pilot remains before final
v1. This handoff grants no pilot, consumer access or remote-operation authority.
