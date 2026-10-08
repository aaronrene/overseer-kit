# Overseer Kit v1 roadmap

Authority: [bounded scope reset](decisions/V1-SCOPE-RESET.md), 2026-10-08.
Session budget: 3 of 5–8 (implementation, review/finding closure, installation/rollback).
The session-2 status/NEXT checkpoint was achieved in session 1 across two
repositories using disposable fixtures.

| Milestone | State |
| --- | --- |
| Preserve original work and reconcile local Muse/Git base | Verified |
| Repository-bound status/init/sync/NEXT and atomic writer | Implemented and tested |
| Focused, two-repository, and supported-suite verification | Passed: 77 supported tests; prior 22 disposable fix checks |
| Architecture review | Passed for the bounded trusted-host design |
| Completed-build review | Closed: both P2 findings corrected and rechecked in session 2 |
| Clean installation and current/previous rollback exercise | Passed: two clean venv installations, six fixture lifecycle stages |
| Explicitly authorized noncritical consumer pilot | Pending; not authorized |

Evidence, exact commands and limitations: [validation](validation/V1-RECOVERY.md).
Latest supported suite: **77 passed, zero failed or skipped in 54.46s**, run from
the current disposable source with dependencies downloaded into its fresh venv.
Both fixtures preserved identity, NEXT, living documents, payload and launcher
through previous → current → previous at fixed installation paths. Temporary
installations and fixtures were removed. No production code changed in session 3.
Validation covers Python 3.14.4 on Darwin arm64 and these two source revisions;
packaged installation, migration and installation rebinding remain outside scope.

`docs/NEXT.md` is the sole current action and prompt:
**OVERSEER-V1-PILOT-AUTHORIZATION-1**, kind `stop`. Installation/rollback and the
review are closed; do not repeat them against unchanged code. The remaining pilot
requires separate explicit owner authorization naming a noncritical repository
and allowed operations. Final v1 is not complete or released. HANDOVER summarizes
evidence without a competing prompt. Former OCI/NXR/GSR/sole-writer chains remain
superseded. No push, mirror, main merge, release, deployment, real-consumer access,
consumer hook activation, or pilot is authorized.
