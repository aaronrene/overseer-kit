# Overseer Kit roadmap

Current authority: the owner's [manual delivery scope decision](decisions/FPR-5-MANUAL-DELIVERY-SCOPE.md)
on 2026-10-17. Deliver the existing features, browser and explicit repository-bound
NEXT workflow. Retain the maintained CLI, local app, actual desktop, local
read-only hosted surface, all three authority modes, selected Python cells and
source installation/migration/update/rollback requirements. The browser is
sufficient; the product is not reverted to the older bounded snapshot.

**Owner decision, 2026-10-17:** keep automatic prompt display for convenience.
Before each new task, explicitly retrieve fresh NEXT from the selected
repository's bound reader and check its identity/context; use that result rather
than an earlier displayed prompt. An agent may do this read, so a button click
is not required when a fresh validated read has already occurred. On refusal or
wrong context, stop. This is required per new task, not per message. Existing
implementation and hook settings are preserved, including disabled hooks;
no client code change, hook activation or automatic-freshness fix is claimed.

Actual Cursor sessionStart/stop and dependent automatic-pilot continuity are
**DEFERRED / NOT VERIFIED**. Client-level protection against restored/forwarded
conversations acting in the wrong project is **DEFERRED / UNQUALIFIED**. These
are excluded from this delivery, not passed. Shared chat-history behavior remains
**UNRESOLVED**. The [vendor request](decisions/FPR-OPS-1-CLIENT-CHANGE-REQUEST.md)
is **OPTIONAL / UNSENT**, not a release prerequisite. No vendor response, host
contract, guard build or speculative adapter is required for this delivery.

Implementation, six repairs, both investigations, dependency repair and completed
validation remain done. The local pilot workflow and owner-observed desktop
records are submitted with their original provenance. The original full automatic
pilot remains unaccepted. Preserve original FINDINGS, raw failures and unavailable
original-artifact limitations; no tests, pilots, launches or reviews are repeated.
The final non-author decides whether the surviving evidence supports the retained
claim. No screenshot reconstruction or new acquisition is queued.

The [acceptance packet](validation/FPR-5-ACCEPTANCE-PACKET.md) contains the revised
claim, evidence map and single non-author brief. **Remaining path:** owner appoints
one independent non-author session to decide acceptance of the exact closing
candidate, all retained requirements and R1–R6; after ACCEPTED, the owner makes a
separate release decision identifying artifact/version, destination and permitted
effects. If BLOCKED, the reviewer must name the precise retained requirement and
evidence gap. No review or release starts in this documentation action.
The owner appoints the fresh reviewer by supplying the prepared canonical NEXT
review prompt to that session. The author/coordinator must not execute it.

Use the bound `ok -C ROOT next` for the selected repository/lane and check the
returned identity/context; publish only through `next-write` with explicit context
and expected prior digest. These are manual repository checks, not a guarantee
that the editor isolates conversations or enforces every tool operation.
Canonical NEXT alone carries the pending action; ROADMAP/HANDOVER are summaries.
Model: GPT-6 Astra; reasoning: High. Active checkout:
`overseer-kit-v1-recovery-20261014`, branch `feat/overseer-v1-recovery-20261014`.

Preserve legacy repair backup/rollback, old worktrees, protected refs, Muse
history, runtime/tests, dependencies and disabled hooks. Legacy handoff binding
and installation-footprint drift remain separate consumer-rollout conditions.
No profiles/accounts, permission changes, installed/global/consumer mutations,
hooks, vendor contact, provider/network access, live delivery/export, fetch/push,
main merge, tags, signing, deployment or release are authorized here.

| Milestone | State |
| --- | --- |
| Automatic display with fresh NEXT confirmation | Owner decision recorded — retain automatic display as a convenience; require a fresh bound NEXT read before each new task. Automatic freshness and lifecycle delivery remain unverified |
| Preserve dirty checkout and reconcile local base | Complete |
| Repository-bound status/init/sync and canonical NEXT | Implemented; R1/R2 repaired |
| Supported tests and two-repository isolation matrix | Complete; 173 supported tests passed |
| Independent architecture and completed-build review | Complete; original findings verdict preserved |
| Repair writer context and reader revision findings | Complete; 20 deterministic regressions passed |
| Clean installation and current/previous rollback | Complete; 43 disposable exercise checks passed |
| Separately authorized noncritical pilot | Complete in newly created test repository; one documentation handoff cycle |
| Final bounded-v1 certification | CERTIFIED; exact claim and limits in the final adjudication |
| Offline bounded source snapshot | Complete locally; retain as an internal reference, not the complete product release |
| FPR-0 — full-product reconciliation analysis | Complete — [integration plan](decisions/FULL-PRODUCT-RESTORATION-PLAN.md); committed-object analysis and documentation only |
| FPR-1 — unified foundation and automatic handoff | Complete locally — unified dispatcher/schema-3 migration, preserved bindings/settings, canonical Cursor fixture bookends; [focused evidence](validation/FPR-1-FOUNDATION.md) |
| FPR-2 — Muse authority, mirror and repository lanes | Complete locally — selected authority, controlled mirrors, explicit adoption/rollback and canonical lane collection; [focused evidence](validation/FPR-2-AUTHORITY.md) |
| FPR-3 — complete product surface | Complete locally — unified maintained commands, bound app/desktop/hosted surfaces, full footprint and local source packaging; [focused evidence](validation/FPR-3-SURFACES.md) |
| FPR-4 — combined validation | Local matrix, bounded repairs, package and rollback evidence recorded; missing Python 3.11 cell now has complete passing coverage in the acceptance record; desktop owner evidence recorded; actual Cursor events are deferred/not verified |
| FPR-5 — independent final review | Complete — original **FINDINGS** verdict and evidence preserved in [the review](reviews/FPR-5-REVIEW.md) |
| FPR-5 bounded repairs | All six implemented; 1,361 selected cases have passing evidence across the new combined run and affected rerun; [author evidence](validation/FPR-5-REPAIRS.md) |
| Remaining acceptance, final adjudication and release decision | **Manual delivery scope revised; independent acceptance pending** — [packet](validation/FPR-5-ACCEPTANCE-PACKET.md) retains the revised claim and one non-author brief pending owner appointment. B1/B2 are deferred exclusions, not passes. Surviving-evidence submission basis is recorded; owner release remains separate |
| FPR-OPS-1 — unexplained cross-window conversation restoration | **Shared chat-history behavior unresolved; client protection deferred/unqualified** — [vendor request](decisions/FPR-OPS-1-CLIENT-CHANGE-REQUEST.md) optional and unsent. No vendor response or client guard is required for this delivery; no fix is claimed |
| FPR-OPS-2 — broken shared legacy `ok` environment | **Confined dependency repair complete** — [repair and verified rollback](validation/FPR-5-LEGACY-CLI-REPAIR.md). Only stable `.venv` changed; existing source/interpreter/global wrapper preserved. Imports, native dependencies, CLI startup and disposable root/path-confinement checks pass. Legacy UUID/branch/digest-bound NEXT remains unsupported; no consumer qualification or FPR-OPS-1 resolution claimed |
| FPR-EVID-1 — external temporary originals unavailable | **Surviving-evidence submission basis recorded under current owner instruction** — 40 interactive, 79 host and 28 pilot curated records retain their original provenance/limits. No missing original is identified as indispensable to the proposed custody-limited claim; no new acquisition or owner approval is queued. Final non-author decides sufficiency for the revised manual delivery claim |

## Historical implementation and validation record

The following results and then-pending prerequisites retain their original scope.
The manual delivery decision above supersedes automatic-host requirements; earlier
full-product language does not silently restore those as current release gates.

FPR-0 reconciled the pinned product/lane line (`e9be0c4`), newer Muse line
(`32254cd`), repaired safety implementation (`348e0f3`) and main baseline
(`d47291d`) through committed objects. The [plan](decisions/FULL-PRODUCT-RESTORATION-PLAN.md)
selects this branch at opening HEAD `0b763df6d7c9066582d27b349a731a4ff70a43e2`
as the integration base: its D-derived full-product engines remain present,
and its B-derived NEXT repairs must survive selective Muse integration. No blind
merge, wholesale revert or rewrite is needed. The historical CLI's 20 names,
all maintained capabilities, config migrations and acceptance boundaries are
inventoried. Product code and tests remain unchanged by FPR-0.

The target is one schema-3 normalized configuration accepting legacy full and
bounded inputs, one `cli/ok`, and one canonical `docs/NEXT.md` service. Preserve
all settings/lanes/identity and refuse contradictions. Do not import M's blanket
local-binding ignore policy over the tracked Git NEXT closing-commit contract.
The plan separates canonical publication from governance hygiene and isolates
operator-controlled Muse mirroring. Three implementation waves lead to one
combined FPR-4 matrix and one independent FPR-5 review, bounded repairs if needed,
one final adjudication and one owner release decision.

The FPR-0 plan recorded owner choices about hosts, platform/distribution claims
and the integrated pilot. The current acceptance record resolves those choices
within the explicitly selected local scope; actual acceptance evidence remains
required. Expanded Muse transport and other external operations remain outside
authorization.

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
known R1/R2 findings. The last preserved bounded supported suite passed **173 tests in
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

FPR-3 restores all historical commands/subcommands through the unified dispatcher,
full status/governance/review/workspace/checkpoints/evidence/ledger/routing/landing/
compaction, bound loopback app and desktop, read-only hosted projections, full
owned footprint and truthful guidance. Canonical NEXT remains the sole action
source. Local mutation, remote transport and release effects are explicit.
See [FPR-3 focused evidence and source/test disposition](validation/FPR-3-SURFACES.md)
and [operation notes](FPR-3-PRODUCT-SURFACES.md).

The final focused surface/artifact/native selection passed **70 checks**. The
retained engine/security selection passed **314 checks**; the closing hosted/parser
selection passed **73 checks** after restoring its public parser factory. Across recorded focused
runs, **529 distinct cases have passing latest outcomes**; this is not a combined
matrix. Initial failures and their fixes remain in the logs, including migration
record size, an atomic-reader replacement race, full-footprint fixture assertions
and socket prerequisites. The explicit local Rust 1.88 toolchain built the native
shell offline. A deterministic resource archive launched the actual CLI/app with
its own conventional venv and verified UUID/root/runtime health. No native GUI,
new signed installer, publication or deployment is claimed.

All 393 original test/support files retain their hashes, and all 104 historical
failures have an explicit requirement/replacement/mechanism disposition before
FPR-4. This installation remains Git-only; its explicit runtime refresh preserved
UUID/root/lane/model, full settings, canonical NEXT and disabled hooks. The retained
installation footprint still reports old lock/asset drift; no forced full sync or
hook activation was performed. See the focused closing record for exact paths. Controlled
Muse tests used only pinned local prerequisites and disposable fixtures. Other
refs, old worktrees/Muse history, snapshots, rollback fixtures, completed bounded
pilot and bounded source-release directory are preserved.

FPR-4 records the integrated section-9 matrix and bounded repairs in
[combined evidence](validation/FPR-4-COMBINED.md). The opening run recorded
**1,159 passed / 11 failed**. The repaired-source combined run recorded
**1,207 passed / 1 failed, zero errors/skips**; the explicit clean-process successor then passed
**2 cases** on the same production runtime and dependencies.
The raw failure, its changed-contract disposition and affected rerun remain
separate. All selected cases executed exactly once; no skip supplies acceptance.
The earlier focused repair run passed 32 cases, and the new compatible/bounded
upgrade and rollback exercise passed 13 checks. These separate runs are not
summed into a single combined count.

Repairs preserve existing portable consumer assets during initialization, restore
configured-path/build-verification guidance, correct app installation guidance,
and make repeated desktop resource bundling reserve distinct private directories.
Runtime `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`
was explicitly refreshed while preserving identity, all non-runtime settings,
NEXT and disabled hooks. No full-footprint overwrite was performed.

Fresh packaged Python 3.14.4 CLI/app/desktop-child checks and the macOS arm64
Rust 1.88 locked/offline native build passed. The complete Python 3.11 cell is
unresolved because pinned cffi 2.1.0 for cp311 is unavailable locally. Named
automatic host/version and platform/distribution acceptance, authorization for
the separate new integrated pilot remain pending. The original FPR-5 reviewer
appointment is satisfied and that review is complete. The new pilot was not run;
the completed bounded pilot and its certification were preserved. Native GUI,
native host lifecycle delivery, signed
installers and live providers remain unverified.

All 393 original test/support files and the historical **1,391 passed / 104 failed**
record remain unchanged. The final disposition maps every historical failure to
retained or explicit successor coverage. Author checks do not count as independent
review. FPR-5 and its bounded author repairs are now complete; the current
successor concerns unresolved acceptance inputs, with GPT-6 Astra and Max
reasoning. Required evidence gaps prevent a release-readiness claim. One final
independent adjudication of complete repaired-source/acceptance evidence and a
separate owner release decision remain. No additional review cycle or release
authority is introduced.

FPR-2 focused evidence covers 559 distinct maintained passing cases across
recorded runs. Final affected reruns passed 169 Git/config/lane and 41 native
cases; the complete mirror/reconciliation run passed 102. One unchanged historical
native-export/automatic-push assertion is explicitly superseded by real controlled
wrapper checks. This is not one combined final-product run or release validation.

FPR-5 repairs (2026-10-15) close the six implementation findings within the
existing architecture: hosted redirect refusal, configured PR identity binding,
owner collision preservation, exact desktop resource membership, repeat init for
multi-lane NEXT, and no-execution configured orchestrator plans. Repaired runtime
is `cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.
The single repair closing commit has sole parent
`4c62c17cff6c606a5e1ddf565e12353973b3bcad`. Its combined run is 1,360 passes/one
preserved scheduling failure; the separate two-pass affected rerun completes
passing coverage of all 1,361 selected cases. See the repair record for exact
source hashes, raw failures and open acceptance requirements. This is author
validation, not independent certification or an owner release decision.
