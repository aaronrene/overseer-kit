# Overseer Kit — bounded v1 roadmap

Authority: [scope reset](decisions/V1-SCOPE-RESET.md), 2026-10-14.
The former sole-writer/NXR-GSR chain is historical and is not the living NEXT.

| Milestone | State |
| --- | --- |
| Preserve dirty checkout and reconcile local base | Complete |
| Repository-bound status/init/sync and canonical NEXT | Complete; locally verified |
| Supported tests and two-repository isolation matrix | Complete; 153 supported tests passed |
| Independent architecture and completed-build review | Pending |
| Clean installation and current/previous rollback | Pending |
| Separately authorized noncritical pilot | Not authorized |

The exact current action lives only in `docs/NEXT.md`; use `ok -C ROOT next`.
Update this summary and HANDOVER together. No release or remote operation is
authorized. See `docs/validation/V1-RECOVERY.md` for the supported test matrix and
results; historical suites are not silently treated as passing.
