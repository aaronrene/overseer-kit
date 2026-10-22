# Overseer Kit roadmap

## OK-NEXT-MODEL (F9) — N1-PR DONE (draft PR #95), 2026-10-22

**N1-PR DONE.** Pushed `feat/next-model-select-20261020` to
`github.com/aaronrene/overseer-kit` and opened stacked draft
[PR #95](https://github.com/aaronrene/overseer-kit/pull/95) onto
`fix/knowtation-migration-compat-20261020` (compat draft
[#94](https://github.com/aaronrene/overseer-kit/pull/94) @ `069fe3b`). Merge of
either draft PR to `main` is Tier 3 and is **not** authorized here.

**N1-R PASS** remains recorded in `docs/reviews/OK-NEXT-MODEL-N1-R.md` over
`99e2e5bcfd6de0eb45b4f48872653f396aaa9850..de711aec04396d9fd5c79b18f37eb672689e24fd`
against freeze sha256 `3d521241c0610a6ca278074cfb7bce06e75760735b3b13b2a3af4b93733ad70e`.
Knowtation runtime `559e1635299830b4d4c814dceac2acc7b89413a1a33929ae1cb3faa276ba52a7`;
rebind plan `d94b35798932e783552163ba97f7afc5795d10d351955c5284dbf8589026f322`.
No unfinished authorized N1 task remains. Do not invent merge work.

**N1b DONE.** Build-verification round 2 recorded **pass** in
`RECOVERY-RUNS/knowtation-next-model-select-20261020/build-verification.json`
(reviewer session `cursor-grok-4.7-bv-r2-2026-10-21T19:01:34Z`). Tip at that
review `ef24c6547abda5b3c43455e64973e26e3c703db9`. Commit 3
`29db9e267ded73bc127e2da9867f3c15a8dca25f` (parent `1571b921be817d5b68f7dfa60fcfe91409a11ff3`)
is the section-13 rebuild. **N1c is DONE.** Receipt:
`knowtation/docs/evidence/B02/overseer-next-model-select-20261020/README.md`.

N1a freeze review **pass** (mechanical) for the pre-amendment freeze; the amended
freeze used for N1b/N1c is sha256 `3d521241…`. Option A: single-lane NEXT `Model:`
is a recommendation under a strict `model_label` grammar.

N1b on local branch `feat/next-model-select-20261020` in worktree
`overseer-kit-next-model-select-20261020`:

- Commit 1 (code/tests/docs except ROADMAP/HANDOVER):
  `6a04ce18ad53a2fb1e3704f89935fdf7163fe67a`
- Commit 3 (BV1 replace-window amendment): `29db9e267ded73bc127e2da9867f3c15a8dca25f`
- Prepared runtime `PREPARED-RUNTIMES/knowtation-next-model-select-20261020`
  sha256 `559e1635299830b4d4c814dceac2acc7b89413a1a33929ae1cb3faa276ba52a7`
- Evidence run `RECOVERY-RUNS/knowtation-next-model-select-20261020/`
  (`runtime.json`; build-verification round 2 **pass**)
- Baseline tests: 766 passed, 8 failed, 2 errors. After change / b2 group:
  817 passed, 8 failed, 2 errors. Failure/error IDs unchanged from baseline.

Finding **F11** (Low, pre-existing general `label()` admits DEL/C1/U+2028/bidi) is
queued for **H1**. N1a–N1-PR are done. No unfinished authorized N1 task remains.

| Step | Model | Status | Deliverable |
| --- | --- | --- | --- |
| N1a | Thinking → Auto (a: Thinking) | **DONE** (mechanical freeze pass) | Pre-amendment freeze review pass; option A recommendation + `model_label`. |
| N1b | Thinking → Auto (b: Auto) | **DONE** (BV round 2 pass) | Commit 3 `29db9e2…`; tip `ef24c654…`; runtime `559e1635…`; freeze `3d521241…`; reviewer `cursor-grok-4.7-bv-r2-2026-10-21T19:01:34Z`. |
| N1c | Thinking → Auto (b: Auto) | **DONE** 2026-10-21 | Knowtation rebound to runtime `559e1635…`. Published NEXT `3a878755…` (`C2-PROPOSAL-REVISION-1`). Rebind plan `d94b3579…`. |
| N1-R | Thinking, independent model | **DONE** (PASS, 2026-10-21) | `docs/reviews/OK-NEXT-MODEL-N1-R.md`. Range `99e2e5b..de711ae`. Reviewer is not the N1b builder and not BV round 2. |
| N1-PR | Operator + Auto | **DONE** 2026-10-22 | Stacked draft [PR #95](https://github.com/aaronrene/overseer-kit/pull/95) on #94. Merge is Tier 3. |

## Migration compatibility + Muse rc11 — R3 draft PR open, 2026-10-21

Local commit `30f5cb4` on `fix/knowtation-migration-compat-20261020` (parent `d54a228`)
covers several changes:

- legacy `kit` metadata is kept as inert `legacy_kit`;
- living documents up to 16 MiB are preserved;
- historical prompts stay inert drafts;
- Muse 0.2.1rc11 support uses an exact allowlist;
- adds `adopt --rebind-muse-runtime`.

Knowtation (rebind and C2 publication) and BornFree (migration and publication)
adopted the prepared runtime `309ac668…` built from this exact commit.

The [independent review](reviews/MIGRATION-COMPAT-RC11-INDEPENDENT-REVIEW.md) of
`30f5cb4` returned **PASS** with no blockers. The owner accepted all of its
recommendations. **F1** and **F2** are fixed at `68952c7`. The independent
re-review passed
([MIGRATION-COMPAT-RC11-R2-REVIEW.md](reviews/MIGRATION-COMPAT-RC11-R2-REVIEW.md)).
F3–F8, F10–F11, A1, and D1 stay queued below. N1a–N1-PR are done (draft PR #95). R3 pushed the branch and opened draft
[PR #94](https://github.com/aaronrene/overseer-kit/pull/94). Merge to main
remains Tier 3.

Phase Model Key: Thinking = freeze WHAT/HOW; Auto = build exactly to the frozen spec;
Thinking → Auto = step `a` then step `b`; Operator + Auto = human Tier-3 gate plus
Auto doc sync.

| Step | Model | Status | Deliverable |
| --- | --- | --- | --- |
| R1a | Thinking → Auto (a: Thinking) | **DONE** 2026-10-20 | Frozen spec [MIGRATION-COMPAT-RC11-R1-SPEC.md](reviews/MIGRATION-COMPAT-RC11-R1-SPEC.md) for **F1** and **F2**; freeze-review loop **pass** (round 3). `ok review --freeze` cannot stamp this checkout (`config_repository_mismatch` / `launcher_repository_mismatch`). |
| R1b | Thinking → Auto (b: Auto) | **DONE** 2026-10-21 | Built F1/F2 exactly to the R1a spec. Seven tiers + E2/E3 recorded in [MIGRATION-COMPAT-RC11-R1-BUILD.md](reviews/MIGRATION-COMPAT-RC11-R1-BUILD.md). `/build-verification-review` → **pass**. Feature-branch commit. No push. |
| R2 | Thinking | **DONE** 2026-10-21 | Independent re-review of `d54a228..68952c7` **pass**. Record: [MIGRATION-COMPAT-RC11-R2-REVIEW.md](reviews/MIGRATION-COMPAT-RC11-R2-REVIEW.md). Reviewer was not the R1b builder. No push. |
| R3 | Operator + Auto | **DONE** 2026-10-21 | Pushed `fix/knowtation-migration-compat-20261020` and opened draft [PR #94](https://github.com/aaronrene/overseer-kit/pull/94) against `main`. Merge to main needs a separate approval. |
| A1 | Operator + Auto | Queued after merge | Reviewed rc11 distribution artifact contract, plus owner authorization for hosting it and for any hosted rc11 `supported-v1.yml` job. No URLs or secrets in R1. |
| H1 | Thinking → Auto | Queued after merge | Hardening: **F3**, **F4**, **F5**, **F6**, **F7**, and **F11** (pre-existing loose `label()` grammar; recorded in the N1 freeze). |
| D1 | Operator + Auto | Queued after merge | Decide how consumers move off prepared runtime `309ac668…` (**F8**). |
| N1a | Thinking → Auto (a: Thinking) | **DONE** 2026-10-20 | Option A. Amended freeze sha256 `3d521241…`. The allowlist design and freeze `cc79cfff…` are superseded. |
| N1b | Thinking → Auto (b: Auto) | **DONE** 2026-10-21 | Sibling worktree `overseer-kit-next-model-select-20261020`, branch `feat/next-model-select-20261020`. Runtime `559e1635…`. BV round 2 pass. |
| N1c | Auto | **DONE** 2026-10-21 | Knowtation rebound to `559e1635…`. Published `C2-PROPOSAL-REVISION-1`. Receipt beside that freeze. |
| N1-R | Thinking, independent model | **DONE** (PASS, 2026-10-21) | `docs/reviews/OK-NEXT-MODEL-N1-R.md`. Range `99e2e5b..de711ae`. Reviewer is not the N1b builder and not BV round 2. |
| N1-PR | Operator + Auto | **DONE** 2026-10-22 | Stacked draft [PR #95](https://github.com/aaronrene/overseer-kit/pull/95) on #94. Merge is Tier 3. |
| M1a | Thinking → Auto (a: Thinking) | Queued; first step after the R3 merge | Freeze the checkout-local ignore fix (**F10**) for migration, Git-only init and already-migrated consumers. |
| M1b | Thinking → Auto (b: Auto) | Blocked on M1a | Build, seven tiers, `/build-verification-review` → **pass**, independent review, PR. Then each consumer applies it through the kit's previewable path. |
| C1 | Operator + Auto | Partly done; baseline removal unblocked, not done in the R2 close | Done: the review scratch folders under `/tmp` (about 2.5 GB) were deleted with owner approval. The cited probe scripts were kept in `RECOVERY-RUNS/migration-compat-rc11-20261020/probes/`. R2 passed 2026-10-21. Remaining, not done here: remove the `overseer-kit-knowtation-baseline-20261020` worktree (117 MB, a `d54a228` checkout that can be recreated). Once the PR is merged, archive `RECOVERY-RUNS/migration-compat-rc11-20261020/`. |

Order of work:

1. Done: R1b, R2, and R3 (draft [PR #94](https://github.com/aaronrene/overseer-kit/pull/94)). N1a–N1-PR are done (stacked draft [PR #95](https://github.com/aaronrene/overseer-kit/pull/95)).
2. No unfinished authorized N1 task remains. Do not invent merge work.
3. Merge of either draft PR to main needs a separate owner approval (Tier 3).
4. After both merges: M1, H1 (including F11), D1, A1 and C1.

Consumer guard until M1 lands (Knowtation and BornFree): stage explicit paths only.
Never run `git add -A`, `git add .` or `muse code add .` there, because
`.overseer/bin/`, `.overseer/local/`, `.overseer/migrations/` and `docs/NEXT.md` are
neither tracked nor ignored.

What each finding is (details and line evidence are in the review):

- **F1 (Medium, pre-PR). Fixed** at `68952c7`. R2 **pass**. The CI probe accepts
  only an exact `MUSE_RUNTIMES` pair; current and stale come from the probed
  venv; both compatibility files are on the driver command; the FPR-4 successor
  runs under the probed runtime. No hosted rc11 job (A1).
- **F2 (Low, pre-PR). Fixed** at `68952c7`. R2 **pass**. An interrupted rebind
  refuses with the backup-restore hint first. Init, sync, adopt, and
  upgrade-regime keep the previous sync sentence.
- **F3 (Low).** Rebind backups are always 0644 or 0755 instead of the original
  mode, so a 0600 config gets a 0644 backup.
- **F4 (Low).** `docs/MUSE-RC11-COMPATIBILITY.md:82-83` says "shared directory
  lock", but `next-write` locks `docs/`, not `.overseer/`.
- **F5 (Medium, pre-existing).** The `_legacy_drafts` pattern
  (`product_migration.py:271`) backtracks exponentially on blank lines after a
  `### Paste-ready prompt` heading. Use `(?:[ \t]*\n)*`.
- **F6 (Low, pre-existing).** The Muse source digest covers `*.py` only, and
  `muse/__init__` runs before the check. Hash before importing; enforce
  hash-checked bytecode or include it in the digest.
- **F7 (Low).** The rebind drift tests assert only exit code 2. Assert the named
  refusals, and add tests for the interrupted-rebind restore, a symlinked or
  planted backup, and backup modes.
- **F8 (operator decision; source-verified, not run).** No command relocates a
  **Git-authority** repository to a Kit installation at a different path
  (`cli/v1.py:175`, `cli/product_config.py:393-394`). Only the Muse rebind
  relocates. BornFree is Git-only.
  - Choose between updating the prepared runtime in place followed by that
    installation's explicit `sync`, or a reviewed relocation command.
  - Knowtation moved to `559e1635…` at N1c. BornFree stays on `309ac668…` until D1.
  - BornFree also cannot take the N1 runtime until D1 is settled.
- **F9 (owner-found while using Knowtation; source-verified).** A single-lane NEXT
  could not name a model other than `context.model`: `cli/v1.py:273-274` raised
  `next_model_mismatch` on both write and read. No supported command changes
  `context.model`; `adopt` and the rebind require `--model` to equal it
  (`cli/product_authority.py:176-178`, `cli/main.py:196-199`).
  - Multi-lane NEXT already accepts any validated model; only explicit `--model`
    expectations are checked (`cli/v1.py:207-211`).
  - **Decided (N1a, option A):** the NEXT `Model:` line is a recommendation. A
    single-lane NEXT may name any label that passes a strict grammar;
    `context.model` stays the default. No allowlist and no `ok next-models`
    command. A valid hand-edited label is displayed; `--expect-next` catches any
    byte change. Multi-lane is unchanged. Model labels confer no authority.
  - **Addressed in N1b commit `6a04ce1…`.** Knowtation installed that runtime at
    N1c. N1-R **PASS** (`docs/reviews/OK-NEXT-MODEL-N1-R.md`).
- **F11 (Low, pre-existing; recorded in the N1a freeze).** The general `label()`
  check (`cli/v1.py:82-85`) admits DEL, C1 controls such as U+0085, U+2028 and
  bidirectional overrides. It still governs `context.model` and multi-lane
  labels. Tightening it would change behavior for existing multi-lane and
  default labels. Queued for **H1**.
- **F10 (Medium, pre-existing; owner-recorded in Knowtation's rc11 receipt,
  source-verified).** Checkout-local Kit files are never excluded after a
  migration.
  - `cli/v1_policy.py:10-12` lists them, and `ignore_assets` adds the matching
    `.gitignore` and `.museignore` rules.
  - Only fresh Muse init (`cli/v1.py:444-449`) and authority changes
    (`cli/product_authority.py:199`) call it. Migration
    (`cli/product_migration.py`), the rebind and fresh Git-only init do not. The
    same was true at `d54a228`.
  - Knowtation (`muse status`) and BornFree (`git status`) both show `.overseer/bin/`,
    `.overseer/local/`, `.overseer/migrations/` and `docs/NEXT.md` as untracked
    and not ignored.
  - Knowtation's `docs/AGENT-ORCHESTRATION.md:105` documents `muse code add .`.
    That command would commit rebind and migration backups, which contain absolute
    local paths.
  - The M1a freeze must cover three things. First, the same additive, previewable
    ignore block for migration and for Git-only init. Second, a supported way for
    already-migrated consumers to add it. Third, the policy conflict:
    `.overseer/config.yaml`, `.cursor/` and `docs/NEXT.md` are listed as local, but
    both consumers track the config with `--tracked-bindings preserve`, and Git
    freshness accepts a committed NEXT (`cli/v1.py:282-290`).
- **Rollback chain for Knowtation after N1:** undo the N1 rebind first (its
  `.overseer/local/rebind-<72c2f1fc…>` backups), then the rc11 rebind
  (`rebind-3899dd65…`), then the original migration rollback package.

Definition of Done for this milestone:

1. Done: F1 and F2 are fixed with seven-tier tests (`68952c7`).
2. Done: build verification and the R2 re-review both pass.
3. The PR is opened under owner authorization.
4. H1 and D1 are tracked in a successor roadmap section.
5. N1 is either merged through its own reviewed stacked PR or carried forward explicitly.
6. M1 and C1 are tracked in the successor roadmap section.

This branch's [NEXT](NEXT.md) is stale (PR #93). It cannot be republished from this
checkout: the tracked binding points to the publication checkout, so the bound
launcher refuses with `launcher_repository_mismatch`. R3 is done (draft PR #94).
N1a–N1-PR are done (draft PR #95). Merge of PR #94 or #95 remains Tier 3.

## PR #93 — hosting verified; owner-authorized merge in progress, 2026-10-18

[Authenticated evidence](validation/PR-93-HOSTING-VERIFICATION.md) confirms the
expected Cloudflare account/project, GitHub source/main branch, successful canonical
production deployment of `87d4074`, and active `overseerkit.com` domain/zone association.
Existing Wrangler authentication was sufficient. Only read-only requests were made.
The Web Analytics settings endpoint returns HTTP 403; full analytics settings and
a historical control baseline remain unverified, as explicitly accepted by the owner.

The owner authorizes marking [PR #93](https://github.com/aaronrene/overseer-kit/pull/93)
ready and merging its exact checked final head, including automatic production
deployment, once final checks remain good. Reconfirm main/head/checks and applicable
rules, then verify the resulting merge, deployment, controls and public content.
This documentation-only change preserves runtime/site code and existing acceptance.
No release, existing-project installation or hosting-settings change is authorized.
PR #92 is already merged. Preserve source and older worktrees. Earlier milestones
are historical; canonical [NEXT](NEXT.md) is the sole current prompt source.
Model: GPT-6 Astra; reasoning: High.

## Hosting follow-up — draft PR #93; authenticated checks blocked

[PR #92](https://github.com/aaronrene/overseer-kit/pull/92) remains merged at
`87d40740081c0f5855e75f7aa2df7f16528d4e5c`; fresh GitHub reads confirm current main.
The [hosting guide](landing/HOSTING.md) now distinguishes repository assets from
hosting-injected analytics and correctly requires checks of four public pages.
[Follow-up record](validation/HOSTING-FOLLOWUP.md) captures scope and focused checks.
Runtime and website executable assets are unchanged; existing merge evidence is
reused without claiming new acceptance or repeating a general review.

Authenticated Cloudflare verification is blocked: no supported connector or token
is configured. With read-only access, verify the project's production identity,
domain, controls and analytics settings; do not change settings. The documentation
correction and formerly local merge receipts are published in
[draft PR #93](https://github.com/aaronrene/overseer-kit/pull/93). Focused checks pass.
Its merge needs an exact-head decision including automatic production deployment. No new merge,
release, deployment command or existing-project install occurred.
Preserve accepted source `97f0529`, its manual release, source and older worktrees.
Earlier milestones below are historical. Canonical [NEXT](NEXT.md) remains the
sole prompt source. Model: GPT-6 Astra; reasoning: High.

## PR #92 — merged with owner approval, 2026-10-17

[PR #92](https://github.com/aaronrene/overseer-kit/pull/92) is merged at
`87d40740081c0f5855e75f7aa2df7f16528d4e5c`. The owner approved the successor delta
and existing automatic website deployment. Immediately rechecked approved head
`18608de`, main `ff9091c` and green checks, marked ready, then merged with an exact
head guard and merge commit. Both histories are preserved; the resulting main tree
exactly equals the approved PR tree. The owner-decision gate below is completed.

[Merge record](validation/PR-92-MERGE.md) contains exact identities and receipts.
Cloudflare's GitHub app reports successful deployment of the merge commit. Four
public pages and two assets return 200; assets match exactly, and HTML matches after
removing only one hosting-injected Cloudflare analytics script plus newline per page.
This reveals a narrow HOSTING.md wording discrepancy about tracking. Authenticated
Cloudflare account/domain/project-control checks remain unverified because no
configured read-only connection/token is available. Do not infer those checks from
the app receipt, change hosting settings, or repeat the completed merge.

No unfinished merge operation remains. The next owner choices are the hosting-doc
clarification/control verification, if pursued, and any separately scoped release.
Release needs exact source/version/distribution approval and candidate-specific
acceptance, artifact, manifest, checksums and notes. Existing-project installation
stays held. Accepted source `97f0529` and its manual release keep their original
limits; merge approval is not independent successor acceptance.

This local closeout updates paired summaries and bound NEXT without an extra main
write or new PR. Source and older worktrees remain unchanged. Earlier milestones
below are historical; canonical [NEXT](NEXT.md) is the sole prompt source.
Model: GPT-6 Astra; reasoning: High.

## PR #92 follow-up — complete, awaiting owner merge decision

[Draft PR #92](https://github.com/aaronrene/overseer-kit/pull/92) received a focused
author review of the main reconciliation and post-acceptance delta. The
[review record](reviews/PR-92-INTEGRATION-FOLLOWUP.md) records five resolved
documentation findings: mirror flags/preservation policy, historical evidence
link, static-site versus explicit CLI behavior, and small operating-guide errors.
No unresolved finding remains in this scoped author review. Runtime is unchanged;
all 295 runtime files match completed source. Existing 25-check lane-guard evidence
was verified by source/test hashes and reused, not rerun or relabelled independent.

Fresh landing, HTML/link, 22 guide-link, CLI-help, asset/layout and preservation
checks pass. Main remains `ff9091c` at review; final-head GitHub checks are confirmed
after pushing this documentation closeout and recorded in the PR. Original
preparation receipts, whole-product README, accepted source `97f0529`, acceptance
and local manual release remain unchanged. No general review or suite repeated.

Next owner decision: approve this successor delta and authorize marking the draft
ready and merging the final PR head, including the existing main-site deployment
consequence. Recheck main/head/checks immediately before merge. Independent
successor acceptance is not claimed; a non-author may review only this bounded
delta if separately appointed. Release still requires an explicit source/version/
distribution decision, candidate-specific acceptance and verified/approved artifacts,
manifest, checksums and notes. Existing-project installation remains on hold.

No unfinished authorized follow-up task remains. No merge, release, production
deployment or existing-project installation occurred. Prior milestones below are
historical; canonical [NEXT](NEXT.md) is the sole prompt source.
Model: GPT-6 Astra; reasoning: High.

## Draft PR publication — complete, 2026-10-17

Draft PR: https://github.com/aaronrene/overseer-kit/pull/92.
Branch: `feat/overseer-publication-20261017`, based on current main
`ff9091cc2f3bdb54c679ea2cd27f4d5280d83603` and completed source `f6a314c`.
The whole-product README and accepted manual release are preserved; main's
website presentation and governance-loop improvements remain, with delivery
copy reconciled to the manual source boundary. All 295 runtime files match the
completed source. This is later work, not acceptance of a new release.

[Publication record](validation/PUBLICATION-PREPARATION.md) records per-path
reconciliation, focused checks, preserved evidence, and exact merge/release steps.
Landing validation, four HTML pages, 57 local links, 15 unchanged website assets,
repository-document links and layout preservation pass. Reuse the accepted
snapshot's evidence and the later bookend repair's 25 author checks; no general
review or suite was repeated. Manual-use and evidence-custody limits remain.

Before merge, resolve focused PR findings and the post-acceptance delta, confirm
main/final-head checks, and obtain explicit owner merge approval including the
existing hosting consequence. Before release, select/authorize the exact source,
version and distribution, bind acceptance to that candidate, and verify/approve
its artifact, manifest, checksums and notes. No required GitHub checks or branch
rules were configured at preparation; absence of checks is not a passing CI run.
Existing-project installation remains separately held. No merge, release,
production deployment, other-project change or older-worktree change was performed.
The existing hosting integration may run an automatic branch-preview check.

No unfinished publication-preparation task remains. Await owner direction.
Canonical [NEXT](NEXT.md) is the sole prompt authority. The prior milestones below
are historical; their completed tasks and old stops are not new work.
Model: GPT-6 Astra; reasoning: High.

## Small-task manual handover — complete, 2026-10-17

The owner authorized one small task in this repository to demonstrate everyday
manual use. Added the [start-to-handover checklist](PRINT-NEXT.md#one-small-task-from-start-to-handover).
The bound reader displayed the prior stop, then the explicitly published task
`OVERSEER-MANUAL-HANDOVER-EXAMPLE-1` with GPT-6 Astra / High. Documentation checks
cover links, matching paired summaries and preservation of the prior text.
Closeout publishes `OVERSEER-MANUAL-HANDOVER-COMPLETE-1` through the bound writer,
followed by a local commit and fresh validated readback. Command receipts are in
`.overseer/scratch/manual-handover-example/` locally.

No unfinished authorized task remains. The accepted source/release and runtime
are preserved; other repositories are unchanged. Existing-project installation
remains on hold. This small documentation task does not repeat or broaden the
completed acceptance or pilot. Canonical [NEXT](NEXT.md) remains the prompt source.

## Preserved manual-display milestone

Current authority: the owner's [current-prompt display decision](decisions/CURRENT-PROMPT-DISPLAY-SCOPE.md),
which supersedes the FPR-6 external-dependency stop and automatic completion plan
for this task.

**Manual current-prompt display is complete. No unfinished authorized task remains.**
The existing bound reader displays the selected project's saved canonical NEXT
prompt and recommended model. The browser uses the same validated service. No
display-code gap was demonstrated; this closeout updates scope, operating guidance
and session instructions and publishes a completion stop through the existing
writer. [Verification record](validation/CURRENT-PROMPT-DISPLAY.md).

Select the physical project and lane, then read its bound
`.overseer/bin/ok -C ROOT next --lane LANE` at entry and before each new task.
Check root/UUID, branch/revision, lane, model and action context; display the
validated prompt verbatim with its model. Report any refusal without reconstructing
a task. At closeout publish only the actual next unfinished authorized task through
`next-write` with explicit context and the expected prior digest, make the local
closing commit, then read and display NEXT again. If work is complete, publish a
completion stop. Canonical [NEXT](NEXT.md) is the sole prompt source; these paired
summaries are not alternative prompts. [Manual instructions](PRINT-NEXT.md).

Automatic Cursor events, vendor execution protection and shared-chat investigation
are outside this task. Their historical NOT VERIFIED / UNQUALIFIED / UNRESOLVED
statuses remain unchanged. Dependency requests remain UNSENT and are not the next
action. No vendor assistance or another general review is queued.

Preserve the accepted manual source `97f052949146c3cf337478927e6d345e353d2063`,
[independent acceptance](reviews/FPR-5-MANUAL-ACCEPTANCE.md) and
[local release](releases/FPR-5-MANUAL-LOCAL-RELEASE.md) with their recorded limits.
The development runtime remains
`bb3108ae8ea0d03190291b2104e4f9e3aab2ac1690b4da9d226a09f6afa2bba0`, version
`1.0.0.dev1`; this documentation closeout does not create a new release.

**Existing-project installation remains on hold.** No external contact, network
calls, profile/account/keychain access, vendor/shared-command changes, release or
installation into existing projects. Hooks, original evidence, old worktrees and
Muse history remain preserved. Reuse completed evidence; do not repeat completed
general reviews, test suites, experiments or the blocked launch. Documentation
checks and validated readback suffice for this documentation-only change.
Model: GPT-6 Astra; reasoning: High.

## Historical FPR-6 closeout and earlier milestones

Everything below is preserved from the prior summary. Its then-current authority,
external-dependency next step and reopened automatic requirements are superseded
by the current decision above. They are historical statements, not instructions
to resume work or repeat acceptance/release.

Current authority: the owner's [automatic completion plan](decisions/FPR-6-AUTOMATIC-COMPLETION-PLAN.md).
The [manual scope](decisions/FPR-5-MANUAL-DELIVERY-SCOPE.md) and
[local release](releases/FPR-5-MANUAL-LOCAL-RELEASE.md) remain preserved milestones.

**FPR-6 local execution completed; automatic experience remains blocked.**
The [execution record](validation/FPR-6-AUTOMATIC-COMPLETION.md) preserves the
outcome and evidence. A demonstrated adapter defect is repaired: JSON array/object
lane assertions now return a bounded refusal instead of a traceback. Four new
regressions failed before repair; all 25 new/affected checks passed afterward.
No completed suite, investigation, pilot, review or failed launch was repeated.

| Completion work | Current state / exact remaining dependency |
| --- | --- |
| A — automatic start/end NEXT | NOT VERIFIED. Local malformed-lane repair passed fixtures. Cursor lifecycle/environment owner must supply a supported isolated real-event path without account/keychain/provider effects; none is established |
| B — wrong-project work prevention | UNQUALIFIED. Codex extension/execution maintainers must supply supported host/task/owner binding and actual admission/permission/tool evidence; no editable integration is present here |
| C — shared-chat display cause | UNRESOLVED. Client selection/state owner must supply a correlated route-origin/state-key/window/client/task/owner discriminator; existing distinct-route result is preserved |
| D — full automatic workflow | NOT VERIFIED. Integration owner needs qualified A/B on the same build/context before a narrow disposable continuity check, retaining C's separate disposition |

Installed Cursor is now 3.25.6 (not silently qualified as the historical 3.24.18).
Narrow read-only source inspection still ties stop to turn completion and possible
follow-up submission; no permitted prerequisite for another launch is established.
The recorded Codex extension/renderer hashes match. No real profile or account
was read, no host launched and no external execution enforcement inferred.
The [prepared dependency requests](decisions/FPR-6-AUTOMATIC-DEPENDENCIES.md)
remain UNSENT. All independent useful authorized local work is exhausted; the
smallest next step needs a supported isolated host/client capability and owner,
or separate authority to route the sanitized requests. Existing-project rollout
stays held. The preserved manual release retains its original scope and identity.

Development successor runtime is
`bb3108ae8ea0d03190291b2104e4f9e3aab2ac1690b4da9d226a09f6afa2bba0`, version
`1.0.0.dev1`. Bound narrow maintenance preserves identity/settings/NEXT and existing
hooks. This candidate has author checks only; no expanded independent acceptance
or successor release is claimed. Accepted-release runtime below is historical.

**Independent acceptance completed on 2026-10-17: ACCEPTED for the revised
manual-delivery scope**, candidate `97f052949146c3cf337478927e6d345e353d2063`.
The owner-appointed fresh GPT-6 Astra / High non-author reviewer decided R1–R6,
all 16 packet requirement rows, all 12 command families and custody sufficiency
in [the reviewer record](reviews/FPR-5-MANUAL-ACCEPTANCE.md). No retained-requirement
acceptance blocker remains. Original FINDINGS and raw failures are preserved.
The review closing commit contains documentation/handoff only; it does not
replace the accepted implementation candidate or constitute a release artifact.

Retained scope: macOS 15.7.2 arm64 source installation, maintained CLI, local
browser app, owner-observed actual desktop, local read-only hosted surface,
Git-only/Muse-only/Muse-with-Git-mirror, selected Python 3.11.15 and 3.14.4 cells
and pinned Muse 0.2.1rc5, identity/lanes/settings, source installation/migration/
update/rollback and the completed local integrated workflow. Accepted-release runtime remains
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`;
native configuration remains
`d65242ef9ca4be228e791d7596bd2a60ff90ba200445c0d5dbf58229c5eecab6`.

Keep automatic prompt display as a convenience. Before each new task, an agent
or operator must retrieve fresh repository-bound NEXT and check physical root,
UUID, branch/revision, lane, model and action context. Use that validated result;
stop on refusal or mismatch. No additional button click is required after an
agent's checked read. This is per task, not per message. Publish canonical NEXT
only through bound next-write with explicit context and expected prior digest.
The manual-release implementation and existing disabled hooks remain unchanged;
the development successor has only the adapter type-check repair described above.

For the preserved manual release, actual Cursor events and automatic continuity
were **DEFERRED / NOT VERIFIED**, and restored/forwarded protection was
**DEFERRED / UNQUALIFIED**. FPR-6 now reopens those requirements; their verification
status has not improved. Shared chat-history behavior remains **UNRESOLVED**.
The prepared vendor request remains **UNSENT**; any external routing needs
separate authority. The original full automatic-pilot acceptance remains false.

Acceptance uses surviving curated records and historical owner observation.
Missing screenshot pixels, original logs, binary/profile/cache and pilot fixture
custody are not supplied by hashes. The reviewer also records that the file
labelled as invalid ENOSPC-truncated JSON is actually a valid 399-byte prior-attempt
note; it supplies no successful execution evidence. No original was reconstructed,
and no test, experiment, pilot or launch was rerun.

**Owner-authorized local source release completed on 2026-10-17.**
Version remains `1.0.0.dev1`; the exact accepted source was packaged with the
existing tool at `/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RELEASES/fpr5-manual-97f0529/`.
The [release record](releases/FPR-5-MANUAL-LOCAL-RELEASE.md) records archive,
manifest and acceptance provenance hashes. New archive integrity and all 791
retained component entries passed; completed tests/reviews were not rerun.
The independent acceptance record is a separate byte-exact companion from
`a6d2576dfeb00f8209e56908bef8d192431312cf`; it is not inserted into the source.

**Next: dependency stop after completed FPR-6 local work.**
Canonical [NEXT](NEXT.md) is the sole actionable prompt. Obtain the exact supported
host/client capability and responsible owner described in the prepared request;
external routing needs separate authority. Do not repeat the completed local
execution, failed launch or old experiments. Automatic acceptance remains open;
Overseer prompt checks do not enforce client tool execution.

**Existing-project installation remains on hold.** Later rollout still requires
named targets/effects, modern binding or separately scoped legacy source changes,
footprint assessment, exact context readback/mismatch refusal and preserved
owner content/history/NEXT/guarded rollback. Existing hooks and shared commands
remain unchanged. No account/keychain access, network, vendor contact,
publication, push, merge, tag, signing, deployment or native build is authorized.
Preserve release artifacts, original evidence, old worktrees and Muse history.
Model: GPT-6 Astra; reasoning: High.

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
| Final manual-delivery adjudication / owner release | **ACCEPTED** at `97f052949146c3cf337478927e6d345e353d2063`; [independent verdict](reviews/FPR-5-MANUAL-ACCEPTANCE.md). All retained requirements and R1–R6 decided. Owner-authorized local source release complete; installation/rollout remains separately gated; B1/B2 remain excluded from that manual-release claim and are reopened under FPR-6 |
| FPR-6 — automatic experience completion | **LOCAL EXECUTION COMPLETE; EXTERNAL CAPABILITIES REQUIRED.** [Execution/evidence](validation/FPR-6-AUTOMATIC-COMPLETION.md): lane-type refusal repaired; 25 focused checks passed. A/D NOT VERIFIED, B UNQUALIFIED, C UNRESOLVED. Existing-project rollout held; [dependency requests](decisions/FPR-6-AUTOMATIC-DEPENDENCIES.md) UNSENT |
| FPR-OPS-1 — unexplained cross-window conversation restoration | **Shared chat-history behavior unresolved; client protection unqualified and reopened under FPR-6** — [client request](decisions/FPR-OPS-1-CLIENT-CHANGE-REQUEST.md) active for FPR-6 and unsent. No vendor response or client guard was required for the preserved manual delivery; FPR-6 reopens protection for the expanded goal; no fix is claimed |
| FPR-OPS-2 — broken shared legacy `ok` environment | **Confined dependency repair complete** — [repair and verified rollback](validation/FPR-5-LEGACY-CLI-REPAIR.md). Only stable `.venv` changed; existing source/interpreter/global wrapper preserved. Imports, native dependencies, CLI startup and disposable root/path-confinement checks pass. Legacy UUID/branch/digest-bound NEXT remains unsupported; no consumer qualification or FPR-OPS-1 resolution claimed |
| FPR-EVID-1 — external temporary originals unavailable | **Sufficient for the limited accepted claim**, with missing-original limits and the 399-byte attempt-note discrepancy in the reviewer record. No reconstructed originals or independent pixel inspection; no acquisition queued |

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
