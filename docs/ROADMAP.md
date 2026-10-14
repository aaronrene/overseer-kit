# Overseer Kit roadmap

Current authority: owner direction on 2026-10-14 to restore the complete product
without discarding the certified safety work. The [scope reset](decisions/V1-SCOPE-RESET.md)
and [bounded certification](validation/V1-CERTIFICATION.md) remain the exact record
for that source snapshot; they do not define the desired full-product endpoint.
The former sole-writer/NXR-GSR chain remains historical and is not the living NEXT.

| Milestone | State |
| --- | --- |
| Preserve dirty checkout and reconcile local base | Complete |
| Repository-bound status/init/sync and canonical NEXT | Implemented; R1/R2 repaired |
| Supported tests and two-repository isolation matrix | Complete; 173 supported tests passed |
| Independent architecture and completed-build review | Complete; original findings verdict preserved |
| Repair writer context and reader revision findings | Complete; 20 deterministic regressions passed |
| Clean installation and current/previous rollback | Complete; 43 disposable exercise checks passed |
| Separately authorized noncritical pilot | Complete in newly created test repository; one documentation handoff cycle |
| Final bounded-v1 certification | CERTIFIED; exact claim and limits in the final adjudication |
| Offline bounded source snapshot | Complete locally; retain as an internal reference, not the complete product release |
| FPR-0 — full-product reconciliation analysis | **NEXT** — compare preserved product, Muse/mirror and bounded-safety lines; freeze one integration plan |
| FPR-1 — unified foundation and automatic handoff | Planned after FPR-0 — one active CLI/config, safe repository binding, migration and automatic validated NEXT bookends |
| FPR-2 — Muse authority, mirror and repository lanes | Planned after FPR-1 — Git-only, Muse-only and Muse-with-Git-mirror with isolated mirroring and per-repository lanes |
| FPR-3 — complete product surface | Planned after FPR-2 — restore governance, review, workspace, verification, routing, landing and local app/desktop/dashboard features |
| FPR-4 — combined validation | Planned after FPR-3 — one integrated matrix, clean installation/migration/rollback and one noncritical full-flow pilot |
| FPR-5 — independent final review and release decision | Planned after FPR-4 — one independent review of the integrated build, bounded repairs if required, then owner release decision |

The exact current action lives only in `docs/NEXT.md`; use `ok -C ROOT next`.
Update this summary and HANDOVER together. No release or remote operation is
authorized. See `docs/validation/V1-RECOVERY.md` for the bounded test matrix and
results; historical suites are not silently treated as passing.

FPR-0 must reconcile three preserved lines without modifying their existing
worktrees: the complete product and lane work at `feat/overseer-context-isolation`
(`e9be0c4`), the newer Muse authority/mirror/reconciliation work at
`feat/overseer-v1-recovery` (`32254cd`), and the certified repository-bound NEXT
safety work at `feat/overseer-v1-recovery-20261014` (`3ed3b7d`). It must inventory
user-visible behavior, select authoritative implementations with evidence, define
one compatible configuration and migration path, and freeze explicit acceptance
criteria before implementation. Preserved code is the starting point; do not
rewrite working features merely because they live on different branches.

To avoid another long chain of reviews, the restoration uses one high-reasoning
architecture analysis, focused mechanical checks during three implementation
waves, one combined validation exercise, and one independent review of the final
integrated build. Do not schedule independent or adversarial reviews for every
wave unless FPR-0 identifies a specific irreversible or security-critical boundary.
No milestone is complete until the main `cli/ok` exposes the intended feature,
the documentation describes the actual behavior, and the relevant focused checks
pass.

The desired product includes automatic validated NEXT display at supported
session start/end, manual `next` fallback, per-repository identity and lanes,
Git-only/Muse-only/Muse-with-Git-mirror choices, isolated operator-controlled
mirroring, the full maintained CLI workflow, and local app/desktop/dashboard
surfaces. OCI registry machinery, native/Mach GSR, UID sole-writer storage,
historical identity bridges and packet chains are not product requirements. FPR-0
must preserve any unique user outcome they once supplied without restoring those
specific mechanisms unless the owner explicitly chooses otherwise.

The [independent review](reviews/V1-RECOVERY-REVIEW.md) reproduced stale writer
publication after a Git context change and mixed-revision NEXT validation. Its
complete supported run passed 153 tests; those passes do not waive the findings
or establish final-v1 completion. The [subsequent repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14)
records both fixes and a 173-pass supported run without rewriting that verdict.
The completed review is not pending again. [Installation/rollback evidence](validation/V1-RECOVERY.md#clean-source-installation-and-rollback--2026-10-14)
records current `348e0f3` to previous `333f81e` to current, with explicit runtime
refresh and preserved UUID, living documents and NEXT. The previous build retains
known R1/R2 findings. The latest complete supported suite passed **173 tests in
107.49 seconds**; the prior fixture-location error and historical failures remain
recorded.

The owner authorized only the newly created local repository
`overseer-v1-pilot-20261014`, branch `pilot/overseer-v1-20261014`. Initialization
without hooks, status/NEXT, both sync modes, digest-checked handoffs, and one
documentation task with local closing commits passed. See the
[pilot evidence](validation/V1-RECOVERY.md#newly-created-test-repository-pilot--2026-10-14).
This was one maintainer in one session, with no preexisting consumer workflow.
The [final certification adjudication](validation/V1-CERTIFICATION.md) now
certifies repository-bound source v1 for local POSIX Git repositories under the
trusted-host model, validated on Python 3.14.4, for `status`, `init`, `sync`,
`next` and `next-write`. It resolves R1/R2 on the separately recorded author
repair evidence while preserving the independent **FINDINGS** verdict.
Historical baseline **1,391 passed / 104 failed** remains unchanged.

The canonical successor is **FPR-0**, a read-only full-product reconciliation
analysis. It authorizes repository/Git-object inspection and a documentation-only
integration plan, not implementation, consumer access, hooks, network/provider
access, merge, push, publication or deployment.
