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
| Clean installation and current/previous rollback | Pending; sole successor |
| Separately authorized noncritical pilot | Not authorized |

The exact current action lives only in `docs/NEXT.md`; use `ok -C ROOT next`.
Update this summary and HANDOVER together. No release or remote operation is
authorized. See `docs/validation/V1-RECOVERY.md` for the supported test matrix and
results; historical suites are not silently treated as passing.

The [independent review](reviews/V1-RECOVERY-REVIEW.md) reproduced stale writer
publication after a Git context change and mixed-revision NEXT validation. Its
complete supported run passed 153 tests; those passes do not waive the findings
or establish final-v1 completion. The [subsequent repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14)
records both fixes and a 173-pass supported run without rewriting that verdict.
The completed review is not pending again. Installation/rollback and a separately
authorized pilot remain before final v1.
