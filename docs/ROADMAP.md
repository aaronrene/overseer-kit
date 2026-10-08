# Overseer Kit v1 roadmap

Authority: [bounded scope reset](decisions/V1-SCOPE-RESET.md), 2026-10-08.
Session budget: 1 of 5–8. The session-2 checkpoint is achieved in session 1:
repository-bound status and canonical NEXT work across two disposable repositories.

| Milestone | State |
| --- | --- |
| Preserve original work and reconcile local Muse/Git base | Verified |
| Repository-bound status/init/sync/NEXT and atomic writer | Implemented and tested |
| Focused, two-repository, and supported-suite verification | Passed: 77 supported tests; 14 isolation matrix tests |
| Architecture and completed-build reviews | Pending — current action OVERSEER-V1-REVIEW-1 |
| Clean installation and current/previous rollback exercise | Pending |
| Explicitly authorized noncritical consumer pilot | Pending; not authorized |

Evidence and historical failures: [validation](validation/V1-RECOVERY.md).
The first implementation milestone passed; final v1 is not complete or released.

`docs/NEXT.md` is the sole current action and prompt. HANDOVER summarizes evidence;
it does not contain a competing prompt. Former OCI/NXR/GSR/sole-writer NEXT and
approval chains are historical and must not be resumed. No push, mirror, main
merge, release, deployment, real-consumer hook activation, or pilot is authorized.
