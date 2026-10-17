# Full-product draft PR preparation — 2026-10-17

The publication candidate carries the completed full kit into current GitHub main:
CLI, local browser app, desktop launcher, policies, model guidance, review and
verification, evidence ledger, workspace/lanes, source maintenance and optional
Muse authority/mirroring. Explicit repository-bound NEXT remains the manual task
boundary; hooks do not generate or execute tasks or enforce vendor permissions.
The whole-product README is preserved byte-for-byte.

## Source and integration identities

| Role | Exact identity |
| --- | --- |
| Completed source | `f6a314c0f862a921ed333688362b35f32493ae09` |
| Current GitHub main compared | `ff9091cc2f3bdb54c679ea2cd27f4d5280d83603` |
| Shared merge base | `d47291d5d9030de5ebef713da95efa978c4d8c6e` |
| Accepted manual source | `97f052949146c3cf337478927e6d345e353d2063` |
| Acceptance documentation | `a6d2576dfeb00f8209e56908bef8d192431312cf` |
| Integration branch | `feat/overseer-publication-20261017` |

[Owner scope and checkout binding](../decisions/PUBLICATION-PREPARATION-SCOPE.md).
The integration is an independent clone with its own Git metadata and environment;
source and older worktrees are unchanged. No source ref was force-updated.

## Reconciliation decisions

Main had six commits beyond the common base, including the bounded CLI publication
and website changes through PR #91. Its 166 changed paths overlap 104 source paths;
87 overlapping paths differ. The old seven-command reset is superseded by the
completed full-product source. Retain that source's runtime, tests, dependencies,
source packaging, templates, current instructions and evidence. This preserves
all 295 runtime paths exactly, including the later bookend type-check repair.
The [per-path disposition](publication-20261017/main-change-dispositions.json)
records all 166 main changes; the merge retains both parents and history.

Preserve main's website layout, responsive/theme styles, diagrams and assets,
governance-loop copy and scenario explanations. Reconcile delivery wording:
primary action opens the manual source guide; rc.1 links are explicitly historical;
existing-project installation remains held. Correct the stale README fragment.
Keep the source landing validator, whose full-product source-route contract applies;
main's older validator requires the superseded seven-command presentation.
The first focused validation found three badge/class mismatches. Add the retained
CSS identifiers to the manifest alongside visible status labels; final validation
passes without runtime changes. The layout attributes and all 15 assets remain
identical to main. No new visual/browser pass is claimed.

Keep main's publication decisions, rc.1 release guides, public evidence, archived
bindings and retained digest tests. Keep the improved mirror runbook and private
GitHub security reporting; update security/contributor/changelog wording to match
the full-product source and its acceptance limits. Source assistant rules and
skills supersede main's old historical-only disclaimers. Hooks remain disabled.
No hosted workflow is dispatched; the retained workflow is manual-only.

## Evidence and checks

New focused checks, recorded in [integration checks](publication-20261017/integration-checks.json):

- All 295 runtime files and their path set match the completed source; digest
  `bb3108ae8ea0d03190291b2104e4f9e3aab2ac1690b4da9d226a09f6afa2bba0`.
- README, independent acceptance and local release record are byte-identical to source.
- All 15 website assets and the three main pages' layout attributes match main.
- Four HTML pages pass nesting/duplicate-ID/image-alt checks; 57 local links and
  repository-document targets/fragments resolve.
- `python -m tools.landing.validate`: PASS after the manifest correction.
- Diff whitespace, paired summaries, summary-lock maintenance and final bound NEXT
  readback are required for the closing commit; receipts accompany closeout.

Reuse the [independent acceptance](../reviews/FPR-5-MANUAL-ACCEPTANCE.md): 1,361
Python 3.14 distinct cases and 1,196 Python 3.11 distinct cases have passing evidence
with the documented targeted reconciliations, not all-green original raw runs.
The original 1,391-pass/104-failure historical baseline remains preserved.
No general suite, review, pilot, installation or failed launch was repeated.

The [FPR-6 record](FPR-6-AUTOMATIC-COMPLETION.md) covers the post-acceptance
`cli/product_bookends.py` repair: four new regressions and 21 affected cases passed.
That is existing author evidence for later code, not the accepted manual snapshot
and not a new independent acceptance. The integration adds documentation and
binding changes only; it does not alter runtime code from the completed source.

## Acceptance, release and manual-use limits

The [local release](../releases/FPR-5-MANUAL-LOCAL-RELEASE.md) remains exact source
`97f0529`, version `1.0.0.dev1`, archive SHA-256
`e33d9d49dc3506733fe62c977b1319b304fc977aaaf0868a3c52f7a1fe54e376`.
Its accepted runtime digest is
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`, distinct
from the successor runtime above. No artifact is rebuilt or relabelled here.
No acceptance is transferred to the integration or later bookend code.

The accepted environment is the recorded macOS arm64 source installation and
selected Python/Muse cells. Automatic Cursor events remain NOT VERIFIED; vendor
execution protection UNQUALIFIED; shared-chat behavior UNRESOLVED. Native desktop
observations retain their missing-original-artifact/custody limitations. No new
Windows/Linux qualification, signed/notarized full-product installer, live provider,
production mirror, real-consumer migration or hosted CI qualification is claimed.
Existing-project installation remains on hold and requires separate named targets,
backups, preserved owner content/history and drift-guarded rollback authority.

## Exact remaining decisions

Before merge:

1. Review this draft's reconciliation and post-acceptance delta against the pinned
   source and existing evidence. Decide whether the later bookend repair is accepted
   for the merge candidate; do not reuse `97f0529` acceptance for it. No general
   product review is queued. Resolve concrete findings with focused checks.
2. Reconfirm main and PR head. If main advances, reconcile the new delta and refresh
   bound NEXT, summaries and affected checks. Confirm GitHub checks on the final head.
   At preparation, branch rules are empty and main is unprotected; there are no
   required status checks to report as passed. No hosted run was dispatched.
3. Obtain explicit owner approval to mark ready and merge, including acknowledgement
   that the existing main hosting integration normally triggers website deployment.
   Do not merge or deploy under the draft-preparation authorization.

Before a new release:

4. Obtain an owner decision on exact source/version and distribution scope. Either
   retain/publish the unchanged accepted snapshot with its original provenance under
   separate authorization, or accept the specific successor delta and create new
   provenance for that exact source. Keep historical rc.1 and the local manual
   release immutable; do not imply a stable or full-product binary release.
5. Under separate authorization, build/verify the selected source artifact, manifest,
   checksums and acceptance companion, and approve its exact release notes/assets
   before tagging or publishing. New platform/automatic/installer claims require
   their own evidence only if included in that release's scope.

Rollout into existing projects remains a separate held task, not a prerequisite
silently included in merge or release. No merge, release, deployment or rollout
was performed by this preparation.
