# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

<!-- overseer:next role=primary lane=product status=live -->
<!-- overseer:anchor:next-session -->
## NEXT SESSION — GSB-b Governance-sync dated-branch collision build

**Date:** 2026-07-31  
**Current position:** GSB-a freeze `pass` (GSB-r3) → GSB-b  
**Model:** Auto

### What just landed

| Slice | Deliverable |
| --- | --- |
| **GSB-a** | **DONE** — freeze `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` → `pass` (GSB-r3), stamp `sha256:30cfb999…`. Contract: C0 reconcile-before-ensure (ancestor/equal → FF tip without checkout-as-FF; else deterministic `-N` uniquify + frozen `PatchPlan` replace); Muse must never dirty Git; seven-tier §GSB.8. **No GSB-b Auto code this session.** |
| **PLS → main** | **DONE** (SD-21 land, PR [#58](https://github.com/aaronrene/overseer-kit/pull/58), `main` @ `433c5a3`). land-b closeout complete; live dogfood queued GSB. |

### THE ONE NEXT STEP — **Model: Auto**

Build exactly to the frozen GSB contract: reconcile an already-existing dated sync branch before dual-HEAD ensure; seven-tier same-day-collision `--write` on all three regimes; `/build-verification-review` → `pass` before DONE.

| | |
| --- | --- |
| **ID** | **GSB-b Governance-sync dated-branch collision build** |
| **Branch** | `feat/gsb-branch-collision` |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` (frozen ground truth); `docs/ROADMAP.md` (GSB-b row); `tools/governance_hygiene/engine.py` (`_ensure_feature_branch`); `docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` (compose — do not redesign) |
| **Hard stops** | Build exactly to freeze · no rollback / `commit_feature` / GSW order redesign · checkout `--force` forbidden · no merge to `main` (Tier 3) |
<!-- /overseer:anchor:next-session -->

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — GSB-b

```text
Model: Auto
ID: GSB-b Governance-sync dated-branch collision build

Build exactly to frozen docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md (GSB-r3 pass, stamp sha256:30cfb999…).

Deliver:
1. Implement C0 reconcile-before-ensure in tools/governance_hygiene/engine.py: when feat/governance-sync-<date> exists on either history, classify vs T_target (§GSB.3.2.1); ancestor/equal → FF tip without checkout-as-FF; else deterministic -N uniquify + dataclasses.replace (or threaded name) so commit/push/pr_url observe reconciled branch; then C1 dual-HEAD ensure. Muse must never dirty the Git tree (§GSB.3.4).
2. Seven-tier §GSB.8 green — mandatory same-day-collision --write on git-only, muse-only, AND muse+git-mirror.
3. /build-verification-review → pass before ROADMAP DONE.
4. Update ROADMAP (GSB-b DONE) + handover together; feature-branch commit (SD-17).

Hard stops: no rollback/commit_feature/GSW order redesign; no checkout --force; no merge to main (Tier 3).
```
<!-- /overseer:anchor:paste-ready-prompt -->

---

## Shared context (canonical — prepend only when paste fence omits it)

| | |
| --- | --- |
| **Project** | 🆗 Overseer Kit — repo-agnostic governance vendoring CLI |
| **Read** | `docs/OVERSEER-KIT-SPEC.md`; target phase in `docs/ROADMAP.md`; this handover |
| **Guardrails** | No secrets; fail-closed VCS reads; no MuseHub-only baseline features; no Tier-3 automation |
| **Tests** | Seven tiers per `policy/test-tiers.yaml` before DONE |
| **Close** | Update ROADMAP + this handover together; feature branch → PR (no commit/push without consent) |
| **Governance gates** | §KH1.9 **live** — `ok status` + `governance-sync` pending-gate reminders |
| **Muse dev tree** | `ok status --exit-code` must show `substrate.ok: true`, `muse_sync.ok: true`, **and** `footprint_self_integrity.ok: true` before phase DONE. Hollow substrate → `muse init --force .`; Muse behind Git (`muse_sync: pending`) → `muse code add -A && muse commit -m "…"`; declared-but-absent kit file (`footprint_self_integrity: missing`) → `ok sync` (all Tier 1) |
| **Handover shape (KH1)** | Every NEXT must include valid **`Model:`** from `policy/model-labels.yaml` **and** a `### Paste-ready prompt` fenced block (H7/H8). Never use `Operator choice` as a Model label. |

---

<!-- overseer:anchor:verified-snapshot -->
## Verified snapshot

| Area | State |
| --- | --- |
| **VCS regime** | `muse+git-mirror` |
| **GitHub main** | `433c5a37a737d4b657ad7959d9091b91b429cf3c` |
| **Canonical anchor** | `sha256:6e320c222667b7e17f8b355b8a64050af10a6e2e09656e5053e339c870bcdbe0` |
| **Canonical main** | `sha256:6e320c222667b7e17f8b355b8a64050af10a6e2e09656e5053e339c870bcdbe0` |
| **Branch** | `feat/gsb-branch-collision` (git + muse) |
| **Dirty** | `no` (after closing commit) |
| **Freeze** | `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` → `pass` (GSB-r3), stamp `sha256:30cfb999…` |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-07-31)

| Item | Value |
| --- | --- |
| Branch | `feat/gsb-branch-collision` (git + muse) |
| GitHub `main` | `433c5a37a737d4b657ad7959d9091b91b429cf3c` |
| Canonical anchor | `sha256:6e320c222667b7e17f8b355b8a64050af10a6e2e09656e5053e339c870bcdbe0` (.muse/git-bridge.toml:last_export.muse_commit_id) |
| Muse `main` | `sha256:6e320c222667b7e17f8b355b8a64050af10a6e2e09656e5053e339c870bcdbe0` |
| Dirty | no (after closing commit) |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
## Change log

- **2026-07-31** — governance-sync: drift (D1=drifted, D2=aligned, D3=drifted) @ `433c5a3`; realign: D2 aligned — skip realign; next_regen=regenerated:land-b

- **2026-07-31** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `c57a7b2`; realign: D2 aligned — skip realign; next_regen=regenerated

- **2026-07-31** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `dcab965`; realign: D2 aligned — skip realign; next_regen=regenerated

- **2026-07-31** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `4650171`; realign: D2 aligned — skip realign; next_regen=regenerated

- **2026-07-31** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `e895a35`; realign: D2 aligned — skip realign; next_regen=regenerated

- **2026-07-31** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `98615a8`; realign: D2 aligned — skip realign; next_regen=regenerated:land-b

| Date | Note |
| --- | --- |
| 2026-07-31 | **GSB-a DONE (Thinking freeze).** Authored + freeze-reviewed `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` → `pass` (GSB-r3), stamp `sha256:30cfb999…`. Contract: C0 reconcile-before-ensure; ancestor/equal → FF tip without checkout-as-FF; else deterministic `-N` uniquify; Muse never dirties Git; §GSB.8 three-regime same-day-collision matrix. **No GSB-b Auto code this session.** NEXT → GSB-b Auto on `feat/gsb-branch-collision`. |
| 2026-07-31 | **PLS → main DONE (SD-21, PR [#58](https://github.com/aaronrene/overseer-kit/pull/58) @ `433c5a3`).** land-b post-merge sync via `ok governance-sync --write`; `ok status --exit-code` → `0`; `ok land-closeout` → `0`. GSB dated-branch collision defect found live (stale same-day `feat/governance-sync-<date>` + Muse-first checkout dirties git tree) and queued. NEXT → GSB-a Thinking freeze. |
| 2026-07-31 | **PLS-b DONE (Auto build + BV `pass`, PLS-BV-r1).** Built exactly to frozen `docs/PHASE-PLS-POST-LAND-MAIN-SYNC.md`; seven-tier §PLS.10 **46** green; exit `36` (never `6`); default off. NEXT → PLS → main (land-a). |
| 2026-07-31 | **PLS-a DONE (Thinking freeze).** Authored + freeze-reviewed `docs/PHASE-PLS-POST-LAND-MAIN-SYNC.md` → `pass` (PLS-r4), stamp `sha256:7a31fb2b…`. Contract: `close_ritual.post_land_sync` default-off; after MERGED ff-only sync; dirty skip never clobber; exit `36`; `verify_landed` additive-only. **No PLS-b Auto code this session.** NEXT → PLS-b Auto on `feat/pls-a`. |
| 2026-07-31 | **GSW-FIX-b DONE** — BV `pass` (GSW-BV-r1); §GSW.10 **29** green (dirty-tree `--write` all three regimes). NEXT → GSW-FIX → main (land-a). |
| 2026-07-31 | **GSW-FIX-a DONE** — freeze `docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` → `pass` (GSW-r3, `sha256:63cfd176…`). NEXT → GSW-FIX-b Auto. |
| 2026-07-31 | **PMHF → main DONE (SD-21)** — Muse `sha256:72efabb7…` + PR [#52](https://github.com/aaronrene/overseer-kit/pull/52) @ `edbc3eb`; §PMHF.3.2 sync done; `ok land-closeout` → `0`. GSW-FIX defect queued. NEXT → GSW-FIX-a. |
| 2026-07-31 | **PMHF-b DONE** — BV `pass` (PMHF-BV-r1); §PMHF.10 **46** green. NEXT → PMHF → main (land-a). |
| 2026-07-31 | **PMHF-a DONE** — freeze `docs/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md` → `pass` (PMHF-r4, `sha256:7d02bb23…`). NEXT → PMHF-b Auto. |
| 2026-07-30 | **GS-PASTE → main DONE (SD-21)** — Muse `sha256:e7831636…` + PR [#49](https://github.com/aaronrene/overseer-kit/pull/49) @ `5a85ef2`. |
| 2026-07-30 | **GS-PASTE-b DONE** — BV `pass` (GSP-BV-r1); §GSP.10 **19** green. NEXT → SD-21 land. |
| 2026-07-30 | **GS-PASTE-a DONE** — freeze `docs/PHASE-GS-PASTE-READY-REGEN.md` → `pass` (GSP-r3, `sha256:123c2e68…`). |

- **2026-07-31** — **GSB-a DONE (Thinking freeze).** Authored + freeze-reviewed
  `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` → `pass` (GSB-r3), stamp
  `sha256:30cfb999…`. Contract closes the live PLS land-b same-day dated-branch
  collision: C0 reconcile before dual-HEAD ensure; `T_target` via base-ref rules
  (`O_H == B` → configured main); ancestor/equal → tip FF without checkout-as-FF;
  else deterministic `-N` uniquify with frozen `PatchPlan` replace + rebuilt
  `pr_url`; Muse must never dirty the Git tree; compose with GSW (no rollback /
  `commit_feature` redesign); checkout `--force` forbidden; seven-tier §GSB.8
  requires same-day-collision `--write` on all three regimes. **No GSB-b Auto
  code this session.** NEXT → GSB-b Auto on `feat/gsb-branch-collision`.
- **2026-07-31** — **PLS-b DONE (Auto build + BV `pass`, PLS-BV-r1, 0 findings).**
  Built exactly to frozen `docs/PHASE-PLS-POST-LAND-MAIN-SYNC.md`:
  `PostLandSyncConfig` + fail-closed `_parse_close_ritual` nesting
  (`adapters/config.py` — unknown keys / `strategy` ≠ `ff_only` /
  `require_clean_worktree` ≠ `true` / non-bool `enabled` → `ConfigError`; defaults
  off); new `tools/close_ritual/post_land_sync.py` implementing the frozen §PLS.4.2
  sequence (`git fetch` → `status --porcelain` → dirty `skipped_dirty` warn, never
  clobber → clean checkout `vcs.git.main_branch` + `git pull --ff-only` → exact
  §PLS.4.4 editor-buffer note); wired into `run_pr_land` / `cli/commands/pr_land.py`
  with `config` + `repo_root` (trigger only on `merged: true` + pre-sync exit `0` +
  not dry-run; already-merged OK path included; already-merged + checks-failed
  excluded); always-present `PrLandResult.post_land_sync` object (closed set
  `disabled|regime_skipped|skipped_dirty|synced|failed|not_applicable`; no-config
  callers default `disabled`); exit `36` = `EXIT_POST_LAND_SYNC` only on hard sync
  fail after a real merge — never reuses K4 integrity `6`; `muse-only` inert
  `regime_skipped` with zero git argv; `verify_landed` / `land_check.py` untouched.
  Seven-tier §PLS.10 **46** green (63 with adjacent close-ritual/config suites);
  15 pre-existing failures elsewhere (q1/q3/sync families) verified identical on the
  clean tree — zero regressions. Doc touchpoints: SPEC §5 additive `ok pr-land` row,
  `docs/PHASE-PR-LAND-AFTER-CHECKS.md` exit-36 row + PLS pointer, VF OVERSEER-SETUP
  `post_land_sync` knobs + §PLS.8 note. BV note: thinking-high Claude tiers were
  API-limited at review time; the independent verifier ran on grok-4.5-high with the
  full skill checklist + evidence table (test-output `sha256:649d262a…`).
  NEXT → **PLS → main (land-a)**, marker `land-phase=land-a`. No kit `main` merge
  this session.
- **2026-07-31** — **PLS-a DONE (Thinking freeze).** Authored + freeze-reviewed
  `docs/PHASE-PLS-POST-LAND-MAIN-SYNC.md` → `pass` (PLS-r4), stamp
  `sha256:7a31fb2b…`. Contract: nested `close_ritual.post_land_sync` (default off,
  `strategy: ff_only`, `require_clean_worktree: true`); additive `ok pr-land`
  post-step after MERGED — fetch, dirty → `skipped_dirty` (never clobber), clean →
  checkout main + `git pull --ff-only`; exit `36` (not K4 integrity `6`);
  always-present `PrLandResult.post_land_sync`; `verify_landed` unchanged; seven-tier
  §PLS.10. **No PLS-b Auto code this session.** NEXT → PLS-b Auto on `feat/pls-a`.
- **2026-07-31** — **GSW-FIX-b DONE (Auto build + BV `pass`, GSW-BV-r1).** Built
  exactly to frozen `docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md`:
  `_apply_plan` order capture → realign (original branch) → dual-HEAD feature-branch
  ensure (`muse+git-mirror`) → write docs → commit → marker (D1+D2 only after commit
  success) → push; rollback restores docs + prior marker + original branch(es)
  (best-effort dual restore; no `--force`); `commit_feature` already-on-branch
  short-circuit on all three adapters; Muse dirty-carry via `--autoshelf`.
  Seven-tier §GSW.10 **29** green including dirty-tree `--write` on **git-only**,
  **muse-only**, and **muse+git-mirror** (coverage-gap close for the live
  2026-07-31 incident). Independent BV round 1 → `pass` (reviewer re-run evidence
  `sha256:c506394a…`). ROADMAP GSW-FIX-b → DONE; queue adds **GSW-FIX → main**.
  Closeout also tightens `land_queue_conflict` so hyphen-split fragments alone
  (e.g. shared `FIX` between `GSW-FIX → main` and historical `GFG-D2-FIX → main`)
  are not slice-identifying — required for land-a dogfood to report
  `land_a_in_progress` rather than a false `land_phase_conflicts_queue_done`.
  NEXT → **GSW-FIX → main (land-a)**, marker `land-phase=land-a`. No kit `main`
  merge this session.
- **2026-07-31** — **GSW-FIX-a DONE (Thinking freeze).** Authored + freeze-reviewed
  `docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` → `pass` (GSW-r3), stamp
  `sha256:63cfd176…`. Contract: `_apply_plan` order capture → realign (original
  branch) → dual-HEAD feature-branch ensure → write docs → commit → marker;
  rollback restores docs + marker + original branch; Muse already-on-branch +
  dirty-carry; seven-tier dirty-tree `--write` on all regimes. **No GSW-FIX-b Auto
  code this session.** NEXT → GSW-FIX-b Auto on `feat/gsw-fix-governance-sync-write-path`.
- **2026-07-31** — **PMHF → main DONE (SD-21 land + post-merge sync).** Two paste
  steps per frozen §PMHF.3, dogfooded live on the protocol's own slice. First step:
  SD-21 criteria verified (BV `pass` PMHF-BV-r1; diff = kit CLI/tools/tests/docs +
  comment-only CI template; no secrets/posture/money) → Muse FF
  `feat/post-merge-handover-freshness` → `main` (`sha256:72efabb7…`) →
  `muse-bridge-deploy` → GitHub PR
  [#52](https://github.com/aaronrene/overseer-kit/pull/52) `muse-mirror` → `main` @
  `edbc3eb` (CI green; operator-approved merge). Second step: docs synced to merged
  `main`; `ok status --exit-code` → `0` + `ok land-closeout` → `0`. The closeout gate
  worked as frozen: it held `post_merge_incomplete` (exit `2`) from merge until this
  sync. **Defect found while dogfooding (queued as GSW-FIX):** `ok governance-sync
  --write` on `muse+git-mirror` fails fail-closed — `_apply_plan` writes doc patches
  before branch setup, `commit_feature`'s `muse checkout` refuses the dirty tree, and
  rollback strands git on the sync branch — so this sync was applied manually per
  §PMHF.3.2's own deliverables. NEXT → **GSW-FIX-a** (Thinking freeze). No further
  kit `main` merge this session.
- **2026-07-31** — **PMHF-b DONE (Auto build + BV `pass`, PMHF-BV-r1).** Built
  exactly to frozen `docs/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md`:
  `tools/land_closeout/` (`LandCloseoutReport` + `check_land_closeout`, §PMHF.5
  resolution order incl. `land_phase_conflicts_queue_done` via `phase_tokens`
  intersection); `ok land-closeout` (exit `0`/`2`; probe default on for git regimes,
  off `muse-only`; never merges/writes docs); `ok status --exit-code` folds
  `land_closeout.ok` into exit `2` (`land_a_in_progress` stays ok); enabled
  `land-check` refuses non-complete closeout with frozen §PMHF.6.5 tokens;
  `next_regen` `land-phase=` marker attribute + land-b emission (frozen §PMHF.3.2
  paste; dry-run shows planned body; mid-wait land-a paste preserved);
  `templates/ci/governance-closeout-github-actions.yml` (comment-only,
  `GITHUB_TOKEN`, never pushes/applies on `main`); handover template rule 8 +
  governance-sync skill + tier-authority rule touchpoints; SPEC §5 additive rows.
  Seven-tier §PMHF.10 **46** green (BV re-run evidence `sha256:929fb54d…`).
  ROADMAP PMHF-b → DONE; queue adds **PMHF → main** (land-a/land-b). NEXT →
  **PMHF → main (land-a)**, marker `land-phase=land-a` (dogfoods the new protocol).
  No kit `main` merge this session.
- **2026-07-31** — **PMHF-a DONE (Thinking freeze).** Authored + freeze-reviewed
  `docs/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md` → `pass` (PMHF-r4), stamp
  `sha256:7d02bb23…`. Contract: land-a/land-b paste protocol; fail-closed
  `land_closeout` on status/land-check/`ok land-closeout`; optional GitHub Actions
  closeout nudge (comment or feature-branch docs PR); never Cursor-only primary;
  never silent main writes; no freeze/BV redesign. **No PMHF-b Auto code this
  session.** NEXT → PMHF-b Auto on `feat/post-merge-handover-freshness`.
- **2026-07-30** — **GS-PASTE → main DONE (SD-21).** Muse FF
  `feat/gs-paste-ready-regen` → `main` (`sha256:e7831636…`, incl. Muse-only
  untrack of museignored `desktop/src-tauri/resources/`) → muse-bridge → GitHub PR
  [#49](https://github.com/aaronrene/overseer-kit/pull/49) `muse-mirror` → `main` @
  `5a85ef2`. Cloudflare Pages **pass**. No live consumer re-init. NEXT = kit queue
  idle (Operator pick from exploration backlog / Scooling PRIMARY).
- **2026-07-30** — **GS-PASTE-b DONE (Auto build + BV `pass`, GSP-BV-r1).** Built
  mechanically against frozen `docs/PHASE-GS-PASTE-READY-REGEN.md`: new
  `tools/governance_hygiene/next_regen.py`; `build_handover_patches` regenerates
  `next-session` + `paste-ready-prompt`; engine patches roadmap before handover;
  glance fail-closed when open-row count ≠ 1; ambiguity emits
  `next_regen: human_authorship_required`; git-only fixtures assert zero Muse argv;
  §GSP.5.3 region-bounded missing-anchor insert. Seven-tier §GSP.10 **19** green
  (evidence `sha256:00a42b4d…`). ROADMAP GS-PASTE-b → DONE. NEXT → SD-21 land
  (Operator + Auto). No kit `main` merge this session; no consumer re-init.
- **2026-07-30** — **GS-PASTE-a DONE (Thinking freeze).** Authored + freeze-reviewed
  `docs/PHASE-GS-PASTE-READY-REGEN.md` → `pass` (GSP-r3). Contract: regenerate
  `next-session` + `paste-ready-prompt` via `ok governance-sync` only; fail-closed
  ambiguous NEXT; git-only/no-Muse; §GSP.10 matrix. **No GS-PASTE-b Auto code this
  session.** NEXT → GS-PASTE-b Auto on `feat/gs-paste-ready-regen`.
- **2026-07-30** — **KIT-PRESERVE → main DONE (SD-21).** Muse FF
  `feat/preserve-shared-assets` → `main` (`sha256:746fa8e3…`) → muse-bridge →
  GitHub PR [#47](https://github.com/aaronrene/overseer-kit/pull/47) `muse-mirror` →
  `main` @ `302549e`. Cloudflare Pages **pass**. No live consumer re-init. NEXT =
  optional operator-gated consumer `ok sync` with `--preserve-shared-assets`.
- **2026-07-30** — **KIT-PRESERVE-SHARED-ASSETS (0.7b) DONE** on
  `feat/preserve-shared-assets`. Freeze `docs/PHASE-PRESERVE-SHARED-ASSETS.md` → `pass`
  (PSA-r1, `sha256:c8f1eacc…`). Auto: `ok init --preserve-shared-assets` preserves differing
  non-living footprint under migrate/greenfield (including `--force`); promote only with
  `--force --include-preserved`. Seven-tier §PSA.8 **28** green; BV `pass` (PSA-BV-r1).
  Land followed same day (see above).
- **2026-07-28** — **GFG-D2-FIX → Muse `main` DONE (Tier-3).** Fast-forward
  `feat/gfg-d2-muse-id-space` → Muse `main` (`sha256:4aebfa75…` + close-out
  `835bdd28…`). GitHub PR [#43](https://github.com/aaronrene/overseer-kit/pull/43)
  `muse-mirror` → `main` merged @ `972507c`. ROADMAP GFG-D2-FIX → main DONE.
  NEXT → consumer `ok sync` + re-stamp (Scooling first). Stub `~/overseer-kit` remains
  K1-era — operators must open `~/OVERSEER_KIT/overseer-kit`.
- **2026-07-28** — **GFG-D2-FIX DONE (Thinking + Auto).** Freeze
  `docs/PHASE-GFG-D2-MUSE-ID-SPACE.md` → `pass` (D2F-r2, `sha256:3148c577…`). Auto: under
  `muse+git-mirror`, R2 is `last_export.muse_commit_id` (same ID space as Muse tips);
  `git_sha` retained for realign `from_ref`/Git ancestry only; realign verify compares Muse
  IDs. §D2F.9 **22** green (`sha256:398f82d3…`). BV `pass` (D2F-BV-r1). Branch
  `feat/gfg-d2-muse-id-space`. Hard stop held: no default git-import on healthy bridges.
- **2026-07-28** — **GFG → main DONE (Tier-3).** Confirmed BV `pass` (GFG-BV-r1) + §GFG.9
  **26** green on feature tip. Muse merge `feat/governance-freshness-gate` → Muse `main`
  (`sha256:1e9ce2ae…`, `--strategy/--on-conflict theirs` — Muse `main` had been behind
  GitHub-only K13 lineage). Bridge: rebased `muse-mirror` onto `origin/main` + GFG commits
  (raw Muse export would have deleted GitHub-only files). PR [#41](https://github.com/aaronrene/overseer-kit/pull/41)
  `muse-mirror` → `main` merged @ `ccf44b4`. ROADMAP GFG → main DONE. NEXT was consumer
  `ok sync` + re-stamp — blocked by D2 ID-space bug until GFG-D2-FIX.
- **2026-07-28** — **GFG-b DONE (build-verified → `pass`, GFG-BV-r1).** Built frozen
  `docs/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md`: session-end Automation
  `cursor/automations/governance-sync-session-end.json`; `tools/governance_freshness/`
  (`check_governance_freshness`, D1/D2 + marker, skip R4/gh); enriched marker stamp on
  fully_aligned / dry-run D1–D2 aligned / `_apply_plan`; `ok status --exit-code` exit `2` +
  JSON `governance_freshness`; land-check when enabled; gitignore/museignore; Tier-2 Automation
  enable wording; skill dry-run carve-out. Seven-tier §GFG.9 **26** green (evidence
  `sha256:cf9b536b…`); mid-apply no-marker retained. ROADMAP GFG-b → DONE. NEXT → Tier-3 merge.
  No kit `main` merge this session.
- **2026-07-28** — **GFG-a DONE (freeze-review → `pass`, GFG-r3).** Froze
  `docs/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md` (stamp `sha256:fe8a3a15…`): session-end
  Automation for `ok governance-sync --dry-run` + fail-closed status/land-check on D1/D2 or
  stale marker; marker enrich + dry-run carve-out; non-goals locked. ROADMAP GFG-a → DONE;
  NEXT → **GFG-b Auto**. No kit code build this session.
- **2026-07-28** — **NEXT → GFG-a (governance freshness gate freeze).** K13 already on `main`
  (`6efef50`, PR #40). Consumer Scooling handover stale after finish land #219 despite live
  Overseer install — root cause: session-end Automation for `governance-sync` never shipped;
  agents sometimes skip SD-17 close. ROADMAP adds GFG-a / GFG-b. No kit code; no consumer
  hand-edit. Paste fence is THE ONE NEXT STEP (Thinking).
- **2026-07-27** — **K13 → `main` PR prepared.** Merged `origin/main` (Landing clarity #39
  `f5cde68`) into `feat/k13-multi-repo-workspace-lanes`; resolved ROADMAP/HANDOVER conflicts;
  NEXT → Tier-3 merge K13 (this PR). No merge performed (hard stop).
- **2026-07-27** — **Landing clarity pass DONE (build-verified → `pass`, LC-BV-r1).**
  Rebased branch onto `main` (clarity IA already live via #32/#36/#37/#38). Close-out:
  Download CTA restores Apple Silicon label; Path 1 says “Download link above” (CTA is no
  longer a button); foot-link CSS weight for `#cta-download-mac`; stress fixture copies
  `docs.html`. Seven-tier landing+LAC **53** green
  (`sha256:e970720253d49a5a19cd791a6f8d1b89a28301b4a9ba93139f7bd1de20e82ed1`). ROADMAP → DONE.
  NEXT → Tier-3 merge + optional DNS §LAC.9.
- **2026-07-27** — **Check OK PR #35 Tier-3 merge confirmed already complete.**
  State `MERGED` (2026-07-18, operator `aaronrene`); merge commit `b8b51c1` on
  `origin/main`; Cloudflare Pages green; BV `pass` (CIO-BV-r1 + CIO-r2) in
  `docs/PHASE-CHECK-OK.md`. No second merge performed (hard stop held). Handover NEXT
  advanced → Landing clarity pass (`feat/landing-clarity-pass`).
- **2026-07-27** — **K13-BRAIN DONE (Operator + Auto).** Optional Brain edge member:
  `BRAIN_ROOT=~/theBRAIN/the-brain`; boards `THE-BRAIN-OVERSEER-HANDOVER.md` /
  `THE-BRAIN-ROADMAP.md` + titles; `workspace:` → `scooling-stack`; Scooling `workspace.yaml`
  brain root + `regime: git-only` (`required: false`). Verified member `status=ok`;
  `ok workspace check-next` → `0`; doctor clean of `board_name_violation`. Commits: Brain
  `feat/k13-brain-edge-member` `bc0c0e6`; Scooling `95519638…`. §MR.12.3 dogfood order complete.
  **Confirmed:** multi-repo workspace is kit-generic (any constellation); scooling-stack was
  first live proof, not a kit special case. ROADMAP K13-BRAIN → DONE.
  NEXT was Check OK PR #35 Tier-3 merge (later confirmed already merged 2026-07-18).
- **2026-07-27** — **K13-MUSEHUB DONE (Operator + Auto).** Optional MuseHub enrichment member:
  checkout `~/MUSE_HUB/musehub` (`MUSEHUB_ROOT`); boards `MUSEHUB-OVERSEER-HANDOVER.md` /
  `MUSEHUB-ROADMAP.md` + titles; `.overseer/config.yaml` muse-only + `workspace:` →
  `scooling-stack` / `product_order_root` Scooling; Scooling `workspace.yaml` musehub root
  default `~/MUSE_HUB/musehub`. Verified member `status=ok`; `ok workspace check-next` → `0`;
  doctor clean of `board_name_violation`; `muse_only_skip_git` (no git/gh). Muse commits:
  MuseHub `feat/k13-musehub-enrichment` `ae779f3e…`; Scooling `feat/k13-dogfood-workspace`
  `1ba29c19…`. Does **not** claim product PRIMARY. ROADMAP K13-MUSEHUB → DONE.
  Spelling correction: constellation/member id `scoaling`→`scooling`.
  NEXT → K13-BRAIN (optional edge; skip if path unknown).
- **2026-07-27** — **K13-DOGFOOD DONE (Operator + Auto).** Live constellation `scooling-stack`:
  Scooling boards → `SCOOLING-OVERSEER-HANDOVER.md` / `SCOOLING-ROADMAP.md` +
  `.overseer/workspace.yaml` (product_order); Knowtation → `KNOWTATION-*` + `workspace:` +
  ownership PRIMARY + PRODUCT RELAY `tip_hash` matching scooling; archived NEXT headings →
  `## ARCHIVED SESSION —`. Verified `ok workspace check-next` → `0`; doctor clean of
  `board_name_violation`. Muse commits on `feat/k13-dogfood-workspace` (merge Tier 3).
  ROADMAP K13-DOGFOOD → DONE. NEXT → K13-MUSEHUB (optional enrichment).
- **2026-07-27** — **K13b Multi-repo workspace lanes DONE (build-verified → `pass`, K13b-BV-r1).**
  Shipped `tools/workspace/` + `ok workspace status|check-next|doctor`, exit `35`
  (`2 > 6 > 35 > 3 > 0`), additive `workspace:` + Option B manifest loader, PRIMARY/RELAY/
  PRODUCT RELAY/ARCHIVED/LANE TIP + tip_hash freshness, §MR.6.5 prefixed init defaults +
  doctor `board_name_violation`, handover template + workspace-authority rule/skills,
  governance-sync `workspace_relay` footer (read-only), fixtures S1–S12, seven-tier §MR.10
  green (evidence `sha256:e06a5e9a…`). No live consumer renames. ROADMAP K13b → DONE.
  NEXT → K13-DOGFOOD Operator + Auto (Scooling + Knowtation).
- **2026-07-27** — **K13a-r3 amendment: §MR.6.5 board filename identity.**
  Freeze requires `{REPO_SLUG}-OVERSEER-HANDOVER.md` / `{REPO_SLUG}-ROADMAP.md` (and lane
  variants) when `workspace:` is configured; rejects bare duplicate tab names. Stamp
  refreshed `sha256:df3d2754…`. K13b prompt updated (init defaults + doctor warnings + S12;
  no live consumer renames in Auto).
- **2026-07-27** — **K13a Freeze multi-repo workspace lanes DONE (reviewed → `pass`, K13a-r2).**
  Froze `docs/MULTI-REPO-WORKSPACE-LANES-FREEZE.md` (stamp `sha256:086d79ef…`): constellation
  manifest Option B (product_order `.overseer/workspace.yaml`), PRIMARY/RELAY/PRODUCT RELAY/
  ARCHIVED/LANE TIP markers, `ok workspace status|check-next|doctor`, exit `35`, SD-17 sibling
  gate, S1–S11 + seven-tier §MR.10. Response to 2026-07-27 multi-root stale-relay incident.
  **Spec-only.** ROADMAP K13a → DONE; K13b → TODO. NEXT → K13b Auto.
- **2026-07-17** — **Landing hero: Check OK terminal + honesty-loop art.** Hero CTAs demoted to
  quiet Download / Clone links; scenarios/docs/releases quieter; CLI mock shows `ok check-ok`;
  pyramid PNG replaced by `assets/diagrams/honesty-loop.svg` (freeze / re-review / build /
  re-verify loop). Landing tests green. On `feat/check-if-ok` (PR #35).
- **2026-07-17** — **Check OK (ad-hoc honesty) DONE (CIO-BV-r1 + CIO-r2).**
  Renamed to **Check OK** (`/check-ok`, `ok check-ok`); skills vendor to `.cursor/skills/`
  **and** `.claude/skills/`; paste `docs/CHECK-OK.md` for Copilot/any assistant; always-on
  `check-ok-thinking.mdc`; same K5 `review --freeze` engine; no new lanes. Branch
  `feat/check-if-ok` (PR #35). NEXT → Tier-3 merge + consumer `ok sync`.
- **2026-07-14** — **K12 LICENSE → MIT DONE (freeze `pass` MIT-r1 + BV `pass` MIT-BV-r1).**
  Operator SPDX flip: root MIT `LICENSE`, `pyproject.toml`, landing/scenarios footers, Path B
  console copy, `tools/landing/validate.py` fail-closed MIT, K12 §K12.4/§K12.7 amended via
  `docs/PHASE-K12-LICENSE-MIT-AMENDMENT.md`. Stress fixture copies favicon assets. Full suite
  **936** green (1 deselected: localhost:8765 already bound). NEXT → DNS / dogfood.
- **2026-07-14** — **Landing + access clarity Auto DONE (build-verified → `pass`, LAC-BV-r1).**
  Implemented frozen `docs/PHASE-LANDING-ACCESS-CLARITY.md`: `docs/landing/` IA §LAC.3 + four
  offline SVGs; primary Download CTA → signed Mac `v0.1.0` `.dmg`; Paths 1–3 on README + landing
  + Path B Overview; HOSTING §LAC.8; Path B chrome (collapse Session bootstrap, bound repo from
  `api/health` → `result.repo_root`, tab explainers, Status auto-refresh once); validator enforce
  + seven-tier §LAC.12; full suite **931** green. Q0 bind/auth closed except health additive.
  ROADMAP Auto → **DONE**. NEXT → Operator DNS (§LAC.9) / dogfood (**Model: Operator + Auto**).
- **2026-07-14** — **Landing + access clarity Thinking freeze DONE (reviewed → `pass`, LAC-r2).**
  Froze `docs/PHASE-LANDING-ACCESS-CLARITY.md`: public IA (strip DONE residue; four offline SVGs
  on main page); Download CTA → signed Mac `v0.1.0` `.dmg` + Python 3.11+; Paths 1–3 playbook;
  Path B chrome (collapse bootstrap, health `repo_root` additive, Status auto-refresh once);
  `OVERSEER_REPO_ROOT` honesty (no folder picker); `overseerkit.com` apex static-only; pre-public
  DNS gate §LAC.9; seven-tier §LAC.12. Stamp `sha256:c0ac8162…`. **Spec-only — no UI rewrite.**
  ROADMAP Thinking → **DONE**; Auto → **TODO**. NEXT → Landing + access clarity Auto.
- **2026-07-14** — **Operator steer: expand NEXT to landing + access clarity + optional Path C finish.**
  Confirmed browser Path B works after terminal paste; obscurity remains. Regenerated Thinking
  prompt: professional `docs/landing/` with flowcharts; README/site/console access story;
  overseerkit.com apex = static only; prefer finishing signed desktop download over half-wired UX.
- **2026-07-14** — **Operator steer: public landing redesign is NEXT (Thinking).** Path B console
  stays local/auth-gated (Q0); convenient access path = desktop auto-fill (already shipped) or
  paste-from-terminal in browser. Regenerated NEXT for professional `docs/landing/` redesign
  freeze (strip WIP/dev residue; no public CSRF mint). Dogfood/hosting remain parallel options.
- **2026-07-13** — **Track Q / Q4b Path B UI redesign DONE (build-verified → `pass`, Q4b-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-Q-Q4A-UI-REDESIGN.md`: rewrote
  `tools/app/static/` (Overview default after auth + Structure gallery; honesty strip; `ok app`
  auth copy; Apache-2.0 footer; suite CTAs §Q4A.7; status humanization + expandable raw JSON);
  committed four offline SVGs under `assets/diagrams/` (lanes / regimes / layers / kit-consumer);
  seven-tier §Q4A.15 (**17** green); full suite **905**. Downstream brand assertion updates in Q1/Q3
  app tests; landing stress stubs for Knowtation/Scooling links. Closed Q0 `api/*/bind/auth`
  untouched; no `LICENSE` / `desktop/` / engine Python edits. ROADMAP: Q4b → **DONE**. Handover
  NEXT → live VF/Scooling dogfood and/or overseerkit.com hosting (**Model: Operator + Auto**).
- **2026-07-13** — **Track Q / Q4a Freeze Path B UI redesign DONE (reviewed → `pass`, Q4a-r2).**
  Drafted and froze `docs/PHASE-TRACK-Q-Q4A-UI-REDESIGN.md`: developer/operator `ok app`
  presentation (Overview + Structure), L0→L3 / kit-vs-sister-door copy, four offline SVG
  structure diagrams (lanes / regimes / layers / kit→consumer), suite CTAs, closed Q0
  `api/*`+bind/auth non-reopen, no LICENSE flip, seven-tier §Q4A.15. Freeze-review: r1 semantic
  findings → fixed; **Q4a-r2 → `pass`**. **Spec-only — no UI code landed.** ROADMAP: Q4a →
  **DONE (Thinking)**; NEXT → **Track Q / Q4b** Auto.
- **2026-07-13** — **Way forward: UI redesign reinstated + license honesty.** Apache-2.0 already
  is open source; MIT optional via K12 amendment. Handover NEXT was Track Q UI redesign Thinking
  (developer tool + structure flowcharts); VF/Scooling dogfood parallel/optional.
- **2026-07-13** — **Developer-centric way forward (docs).** Public site = explain + suite doors
  (GitHub / MuseHub / Knowtation / consumers); Scooling clarified as product runtime that
  *consumes* kit governance.
- **2026-07-13** — **Consumer + public-path honesty (docs).** Revised
  `docs/consumers/videofactory/OVERSEER-SETUP.md` so K8 `docs.lanes` is documented as **shipped**
  (not future); Path A / website honesty in `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` +
  `docs/CONSUMER-ADAPTER-PATTERN.md`; landing uses canonical `ok` CLI; added
  `docs/landing/HOSTING.md` for `overseerkit.com` static front door.

- **2026-07-13** — **Q3-release Auto build DONE (build-verified → `pass`, Q3R-BV-r1).**
  Shipped mechanical §QR.4–§QR.13 against frozen `docs/PHASE-Q3-RELEASE-DESKTOP-INSTALLERS.md`:
  `.github/workflows/desktop-release.yml` (tag/`workflow_dispatch`; macOS-14/Windows/ubuntu-22.04;
  fail-closed signing; `softprops/action-gh-release`; least-privilege `contents: write`); optional
  unsigned Linux smoke; `templates/ci/desktop-release-github-actions.yml`; `tools/desktop_release/`
  (version-align, manifest, allowlist, refuse, checksums, finalize, workflow lint); `desktop/keys/`
  public minisign placeholder + README; runbook §Signed installers + Python 3.11+ honesty; SPEC §5
  additive distribution note; `.gitignore`/`.museignore` signing patterns. Seven-tier §QR.13 (**39**
  green); full suite **887**. Track Q `tools/app` / launcher untouched. Live Apple/Windows
  notarization and GitHub Release upload **not** claimed (operator Tier-3 secrets). ROADMAP Auto →
  **DONE**. Handover NEXT → operator first signed Release (or next Thinking).
- **2026-07-13** — **Q3-release Thinking freeze DONE (reviewed → `pass`, QR-r3).**
  Froze CI publish of signed Tauri installers in `docs/PHASE-Q3-RELEASE-DESKTOP-INSTALLERS.md`:
  runner matrix + arches; publish allowlist (`.dmg`/`.msi`/`.AppImage` + manifest + sums);
  Apple Developer ID + notarization (hardened runtime/timestamp), Windows Authenticode, Linux
  minisign/GPG detached sig; GitHub Actions secret-name boundary (no in-repo secrets); release
  manifest schema; rejection table; Auto deliverables (`.github/workflows/`, `tools/desktop_release/`,
  template, runbook); seven-tier §QR.13. Honesty: Auto v1 still requires host Python 3.11+ (no
  embedded interpreter). Freeze-review loop: r1 (arches/allowlist/permissions/fail-closed) → fixed;
  r2 (Python honesty, hardened runtime, runner pin, Apple API-key names, dispatch inputs) → fixed;
  **QR-r3 → `pass`**; stamp `sha256:91d39951…`. **Spec-only — no workflow/secrets landed.** Hard
  stops held (no Track Q rewrite; no Tier-3 merge). ROADMAP: Thinking → **DONE**; Auto → **TODO**.
  Handover NEXT → **Q3-release Auto**.
- **2026-07-13** — **Hosted governance dashboard Auto build DONE (build-verified → `pass`, HGD-BV-r1).**
  Built mechanically against frozen `docs/PHASE-HOSTED-GOVERNANCE-DASHBOARD.md`: `tools/hosted_dashboard/`
  adapters (`github_contents`/`github_meta`; optional `github_checks_advisory`/`musehub_read`); closed
  GET-only `api/*` (§HGD.5); Bearer viewer auth (§HGD.6); document-derived + advisory gates; ephemeral
  cache; `ok hosted-dashboard` (default `127.0.0.1:8766`); static UI + honesty banner; operator runbook;
  SPEC §5 additive row; `hosted_dashboard` config block. Seven-tier §HGD.12 (**50** green). Track Q
  surfaces unchanged. Hard stops held (no remote write; no product data store; no CD/probes; no Tier-3
  merge). ROADMAP Auto → **DONE**. Handover NEXT → **Q3-release** Thinking (exploration backlog).
- **2026-07-13** — **Hosted governance dashboard Thinking freeze DONE (reviewed → `pass`, HGD-r3).**
  Froze read-only remote org/repo governance glance in `docs/PHASE-HOSTED-GOVERNANCE-DASHBOARD.md`:
  GitHub/MuseHub read APIs; closed GET-only `api/*`; Bearer viewer auth; document-derived vs
  advisory gates; Track Q contrast; rejection + capability tiers; Auto deliverables
  (`tools/hosted_dashboard/`, `ok hosted-dashboard`, runbook); seven-tier §HGD.12. Freeze-review
  loop: r1 (response schemas, allowlist bounds, auth, HTTP tokens) → fixed; r2 (upstream host
  allowlist, SSRF `403`, UI Bearer bootstrap) → fixed; **HGD-r3 → `pass`**; stamp
  `sha256:af8419e1…`. **Spec-only — no code landed.** Hard stops held (no Track Q rewrite; no
  remote write; no product data store; no Tier-3 merge). ROADMAP: Thinking → **DONE**; Auto build
  **TODO**. Handover NEXT → **Hosted governance dashboard Auto**.
- **2026-07-13** — **Track P / P-deploy Auto build DONE (build-verified → `pass`, P-deploy-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-DEPLOY.md`: `honesty.require_deploy_health`
  (`off|warn|require`, default `off`; `HONESTY_KEYS` + `HonestyConfig`); `find_matching_deploy_health`;
  honesty-status Mode C (`--deploy-health`, shared `--frozen-spec`, §PD.5.0); exit `34` +
  `missing_deploy_health` + Mode C JSON block; twin `/deploy-verification-review` (D1–D8); optional
  pointer in `build-verification-required.mdc`. Seven-tier §PD.9 (**+37**); full suite **798** green.
  No kit-side deploy/HTTP probe; no Track O redesign; no Tier-3 merge. ROADMAP: P-deploy build →
  **DONE**. Handover NEXT → **Hosted governance dashboard** Thinking (exploration backlog).
- **2026-07-13** — **Track P / P-deploy Thinking freeze DONE (reviewed → `pass`, P-deploy-r3).**
  Froze the live-deploy sibling of build-verification in `docs/PHASE-TRACK-P-P-DEPLOY.md`: reuses
  P-evidence `verification_evidence` + `deploy_health` (no new ledger kind); `honesty.require_deploy_health`
  (`off|warn|require`, default `off`; `HONESTY_KEYS` + `HonestyConfig`); honesty-status Mode C
  (`--deploy-health`, shared `--frozen-spec`, §PD.5.0 resolution algorithm); exit `34` +
  `missing_deploy_health`; twin `/deploy-verification-review` skill (D1–D8); boundary + rejection
  table; seven-tier §PD.9. Freeze-review loop: r1 (Mode C/`--frozen-spec` resolution + CLI wiring) →
  fixed; r2 (`HonestyConfig` field; "by default" probe weasel; BV-waiver wording) → fixed;
  **P-deploy-r3 → `pass`**; stamp `sha256:a9fe1cd9…`. **Spec-only — no code landed.** Hard stops
  held (no deploy/probe code; no Track O redesign; no Tier-3 merge). ROADMAP: P-deploy Thinking →
  **DONE**; added **Track P / P-deploy build** (Auto, TODO). Handover NEXT → **P-deploy Auto build**.
- **2026-07-13** — **Track O / O3 Stage 3 upgrade-regime build DONE (build-verified → `pass`, O3-BV-r2).**
  Shipped `ok upgrade-regime` against frozen O2: `--from muse-only --to muse+git-mirror` with
  `--dry-run` / `--apply` / `--live-bridge` / `--force` / `-y`; C0–C5 fail-closed; G1–G8; hard-stop
  before C8; composes sync/status + K7 bridge invariants (no adapter rewrite). Runbook
  `docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md`; product-contract Stage 3 + `tools/track_o/`
  harness retargeted together (no “deferred to O2” shipping claim; one-click still gated on §O2.6);
  SPEC §5 row. Seven-tier §O2.9 (**+33**); full suite **761** green. BV r1 findings (data-integrity
  mid-write; regime-only mutation honesty; COMPLETE_UPGRADE unit) → fixed; **O3-BV-r2 → `pass`**
  ([verifier](38527ede-ac3d-4c55-ba9f-6d8e4f4a4ad2)). Hard stops held. ROADMAP: O3 → DONE; Track O
  promoted complete. Handover NEXT → **Track P / P-deploy** Thinking.
- **2026-07-13** — **Track O / O2 Stage 3 kit upgrade ceremony freeze DONE (reviewed → `pass`, O2-r3).**
  Closed §O0.3.3 deferral in `docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`: C0–C8 ceremony for
  `muse-only` → `muse+git-mirror`; complete config write (no silent `vcs.regime` edit); footprint
  re-seed via sync/migrate + `--force` rules; bridge dry-run gates G1–G8 (SD-14); product unlock
  §O2.6 (one-click only after O3 BV `pass`); O3 deliverable `ok upgrade-regime` + runbook +
  contract/harness retarget; seven-tier §O2.9. Freeze-review loop: r1 (C1 repair / G8 / CLI flags) →
  fixed; r2 (product-contract retarget deferred to O3 for harness atomicity) → fixed; **O2-r3 →
  `pass`**; stamp `sha256:ac970077…`. **Spec-only — no ceremony code landed.** ROADMAP: O2 → DONE;
  O3 Auto queued. Handover NEXT → **Track O / O3**.
- **2026-07-13** — **Track O / O1 Normie custody product contracts DONE (build-verified → `pass`, O1-BV-r1).**
  Built mechanically against frozen O0: shipped `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`
  (Stages 1–4, §O0.3.3 deferred Stage 3 ceremony, boundary + rejection tables — no redesign);
  Scooling `OVERSEER-SETUP.md` Track O cross-link (live init remains operator-gated); Knowtation
  stub `docs/consumers/knowtation/OVERSEER-SETUP.md` (Stage 4 pointer; no live init); optional
  `tools/track_o/` validator + mandatory seven-tier §O0.8 harness under `tests/` (**+32**; full
  suite **728** green). `/build-verification-review` → **`pass` (O1-BV-r1)**
  ([verifier](56bd3073-49be-4bad-bc94-5ebe858a008f)). Hard stops held: no signup UI, no Stage 3
  ceremony, no live consumer init, no new CLI/adapters. ROADMAP: O1 → DONE; O2 Thinking queued.
  Handover NEXT → **Track O / O2**.
- **2026-07-13** — **Track O / O0 Normie custody funnel freeze DONE (reviewed → `pass`, O0-r3).**
  Refined draft seed into freeze contract `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md`: Track O
  vs K6/Q identity; Stages 1–4; §O0.3.3 Stage 3 kit upgrade ceremony deferred (no silent
  `vcs.regime` edit; product one-click blocked until O2); custody identity; kit vs
  Scooling/Knowtation/MuseHub boundary; rejection table; O1 product-contracts-only deliverables
  (exact paths); seven-tier §O0.8. Freeze-review loop: r1 findings (Stage 3 ceremony gap; stress
  tier; Knowtation path; exact contract path; backlog wording) → fixed; r2 residual Stage 3
  consistency → fixed; **O0-r3 → `pass`**; stamp `sha256:642076c9…`. **Spec-only — no code landed.**
  ROADMAP: O0 → DONE; O1 Auto queued; exploration backlog promoted. Handover NEXT → **Track O / O1**.
- **2026-07-13** — **K6-Scooling consumer runbook + KH1 handover repair + Track O seed.**
  Added `docs/consumers/scooling/OVERSEER-SETUP.md`; cross-linked K6 operator runbook +
  `CONSUMER-ADAPTER-PATTERN.md`; queued Track O / O0 draft
  `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` (not frozen). Fixed Q3 close-out failure:
  NEXT had used invalid `Model: Operator choice` and omitted the paste-ready fence (KH1 H7/H8).
  ROADMAP: K6-Scooling → **DONE**; Track O / O0 → **TODO (Thinking)**; NEXT → Track O / O0.
- **2026-07-13** — **Track Q / Q3 Tauri desktop packaging DONE (build-verified → `pass`, Q3-BV-r1).**
  Shipped cross-platform Tauri shell (`desktop/`): Rust launcher spawns canonical **`ok app`**,
  parses one-time stderr banner (`url`, `session_credential`, `csrf_token`), loads Q1 loopback UI
  via `WebviewUrl::External`, and injects in-memory auth bootstrap (no `localStorage`). Python
  packaging contract in `tools/desktop/` (launcher argv builder, banner parser, manifest validator,
  init-script generator); `scripts/bundle-desktop-kit.sh` copies engine into Tauri resources for
  release builds. **No** new engine subcommands, exit codes, or `api/*` surface changes. Seven-tier
  §Q3: **28** new tests (**696** total green). `/build-verification-review` round 1 → **`pass`**
  (V1–V8 clean). ROADMAP: Track Q / Q3 → **DONE**; Track Q chain complete; NEXT was briefly
  mis-set to operator-choice without paste fence (repaired same day in K6-Scooling close-out).
- **2026-07-13** — **Track Q / Q2b OK CLI entrypoint build DONE (build-verified → `pass`, Q2b-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md`: shipped `cli/ok`
  canonical POSIX shim + `cli/overseer` compatibility shim (exact one-line stderr deprecation);
  `argparse` prog `ok`; operator-facing remediation/banner strings → `ok`; operator docs/templates/
  twin `.cursor/` + `cursor/` skills/CI examples → `ok`; SPEC §5 command table + K4.1 invocation
  amended; footprint integrity + muse-sync remediation strings updated; engine shims explicitly
  excluded from `resolve_footprint` / `version.lock`. Seven-tier §Q2A.10: **14** new tests (**668**
  total green). `/build-verification-review` round 1 → **`pass`** (V1–V8 clean). ROADMAP: Track Q /
  Q2b → **DONE**; NEXT → **Track Q / Q3** Tauri (`ok app` launcher).
- **2026-07-13** — **Track Q / Q2a Freeze OK CLI entrypoint DONE (reviewed → `pass`, Q2a-r2).**
  Drafted and froze `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md`: canonical CLI name `ok`
  (`cli/ok` → `python -m cli.main`; `argparse` prog `ok`); `cli/overseer` remains compatibility
  shim with exact one-line stderr deprecation per process; no subcommand/exit-code/`.overseer/`
  path changes; engine shims explicitly **not** footprint members (supersedes earlier Q2b
  “footprint + version.lock entry” wording); SPEC §5 command table must rewrite to `ok …` in Q2b;
  existing-test stderr migration rule; twin `.cursor/` + `cursor/` skill doc pass; seven-tier
  §Q2A.10. Freeze-review loop: r1 findings (C4 path placeholder; existing-test migration; SPEC
  rewrite mandate; DoD shim spelling; twin skills) → fixed; **Q2a-r2 → `pass`**; stamp
  `sha256:dbfbf9ad…`. **Spec-only — no code landed.** ROADMAP: Track Q / Q2a → **DONE (Thinking)**;
  NEXT → **Track Q / Q2b**.
- **2026-07-13** — **Track Q / Q0 Freeze Overseer App DONE (reviewed → `pass`, Q0-r2).**
  Drafted and froze `docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md`: local-only `overseer app` web UI over
  the existing Python engine (zero rewrite). Frozen surface — CLI `overseer app`; bind default
  `127.0.0.1` (allow `localhost`/`::1`; refuse non-loopback); Bearer + CSRF-header auth (cookies
  deferred); stdlib HTTP server (FastAPI not required); closed `api/*` read/act set (status,
  ROADMAP/HANDOVER, review --freeze, governance-sync, ledger, honesty-status) with §Q0.7.6 body
  schemas; fail-closed CLI parity; seven-tier §Q0.12. Freeze-review loop: r1 findings (path
  notation C4 false positive; CORS/`::1`; POST schemas; status exit_code semantics; auth narrowed;
  multi-lane CLI-only) → fixed; **Q0-r2 → `pass`**; stamp `sha256:3c3f6229…`. **Spec-only — no
  code landed.** ROADMAP: Track Q / Q0 → **DONE (Thinking)**; NEXT → **Track Q / Q1**.

- **2026-07-13** — **Track P / P-evidence Auto build DONE (build-verified → `pass`, P-evidence-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-EVIDENCE.md` (no redesign): ledger kind
  `verification_evidence` + `validate_verification_artifacts` (§PE.3–§PE.4); genesis forbid-list
  extended; `honesty.require_verification_evidence: off|warn|require` (default `off`; `HONESTY_KEYS`
  membership); honesty-status Mode B (`--verification-evidence` / `--frozen-spec`) with Mode A/B
  mutual exclusion; exit `33` + `missing_verification_evidence`; twin build-verification V8 + Evidence
  table skill delta (`.cursor/` + `cursor/` paths). Seven-tier §PE.10 matrix: **43** new tests
  (**612** total green). `/build-verification-review` round 1 → **`pass`** (V1–V8 clean). ROADMAP
  P-evidence build → **DONE**; NEXT was **Track Q / Q0** (now also DONE this session).

- **2026-07-13** — **Track P / P-evidence Thinking freeze DONE (reviewed → `pass`, P-evidence-r3).**
  Drafted and froze `docs/PHASE-TRACK-P-P-EVIDENCE.md`: verification-evidence capture that closes
  build-verification V8's durability gap. Frozen surface — ledger kind `verification_evidence`
  (additive K9a enum amendment; `actor_role=verifier`); closed artifact types
  `test_output`\|`deploy_health`\|`screenshot` (content hashes + opaque refs; no blobs in ledger;
  kit never deploys / HTTP-probes / screenshots); `honesty.require_verification_evidence:
  off\|warn\|require` (default `off`; must join `HONESTY_KEYS`); honesty-status Mode A/B mutual
  exclusion (`--verification-evidence` / `--frozen-spec`); exit `33` +
  `missing_verification_evidence`; normative build-verification skill V8 + Evidence table delta
  (both twin paths); seven-tier §PE.10 matrix. Freeze-review loop: r1 findings (Mode B JSON/token,
  Mode A/B mutual exclusion, `frozen_spec` opacity, flag names, K9a amendment note) → fixed; r2
  findings (`HONESTY_KEYS`, `off` wording) → fixed; **P-evidence-r3 → `pass`**; stamp written by
  `overseer review --freeze` (digest `sha256:c1b9fb3…`). **Spec-only — no code landed.** ROADMAP:
  Track P / P-evidence → **DONE (Thinking)**; added **Track P / P-evidence build** (Auto, TODO).
  Handover NEXT flips to the P-evidence Auto build. **569** tests unchanged.

- **2026-07-13** — **Track P / P-cost Auto build DONE (build-verified → `pass`, P-cost-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` (no redesign): optional
  `cost_class` on `model_tiers` (closed vocabulary `free|low|moderate|high`; recognized key); deterministic
  `paid_step_before_spend` derivation; additive `cost_class` + `paid_step_before_spend` on read-only
  `overseer route` (resolution unchanged); optional default-inert `cost_awareness:` config; active-slice
  spend-awareness surface on `overseer status` (+ `--json`) and `governance-sync` footer (reuses §KH1.9
  scan; reminder-only); exit `32` confined to `overseer route` (status/governance-sync degrade to warning);
  handover template spend-awareness reminder. New module `tools/cost_awareness/`; seven-tier §PC.9 matrix:
  **40** new tests (**569** total green). `/build-verification-review` round 1 → **`pass`** (V1–V8 clean).
  ROADMAP P-cost build → **DONE**; NEXT → **Track P / P-evidence Thinking freeze**.
- **2026-07-13** — **Track P / P-cost Thinking freeze DONE (reviewed → `pass`, P-cost-r2).** Drafted
  and froze `docs/PHASE-TRACK-P-P-COST-AWARENESS.md`: a **cost-*awareness* surface, not a dollar
  pricer**. Frozen surface — an optional, ordinal, **currency-free** `cost_class`
  (`free < low < moderate < high`) on each `model_tiers[]` entry; a deterministic
  `paid_step_before_spend` derivation (`free` + the reserved `human` terminal are unpaid; any other
  band — and, conservatively, an **absent** band → `unknown` — is paid, mirroring vision §1.2
  fail-closed-before-spend); an **additive** `cost_class` + `paid_step_before_spend` annotation on the
  read-only `overseer route` output (routing resolution itself unchanged); an optional default-inert
  `cost_awareness:` config block (`enabled: false`, `surfaces: [status, governance-sync]`); a
  read-only **active-slice spend-awareness surface** on `overseer status` (+ `--json` key) and the
  `overseer governance-sync` footer that reuses the existing §KH1.9 active-slice scan (derives
  `phase_tier` from the slice `Model:` label and `gate` from any pending governance gate; `position`
  stays `None` — deliberate coarseness, the runtime resolves precisely via `overseer route`),
  **reminder-only and never blocking**; a single new non-overlapping exit code `32` (malformed cost
  metadata, **confined to `overseer route`** — `status`/`governance-sync` degrade to a
  `cost_awareness: invalid` warning, matching the frozen `model_routing: invalid` precedent); the
  rule-holder-not-spender boundary table; and the §PC.9 seven-tier matrix. **Boundary held (K7 /
  `AGENTS.md`):** the kit declares the bands and derives the paid flag; the runtime (Cursor /
  OpenRouter / Scooling 9A) converts a band into money and decides spend. **No dollar amount,
  currency, price, budget, spend cap, network connection, or model call in the kit.**
  `/freeze-review-loop`: CLI checklist gate clean both rounds; **P-cost-r1** raised one
  non-escalating MAJOR internal-consistency finding (R1-M1: the exit-code section described a
  malformed-cost-metadata fault as both exit `32` and the existing `2` fail-closed tier on
  `overseer status`, contradicting the warning-only `model_routing` precedent) → fixed minimally by
  confining `32` to `overseer route` and degrading the informational surfaces to a warning;
  **P-cost-r2 → `pass`**; stamp written by `overseer review --freeze` (digest `sha256:9f26678…`).
  **Spec-only — no code landed.** ROADMAP: Track P / P-cost → **DONE (Thinking)**; added **Track P /
  P-cost build** (Auto, TODO). Handover NEXT flips to the P-cost Auto build. **529** tests unchanged.
- **2026-07-13** — **Track P / P-route Auto build DONE (build-verified → `pass`, P-route-BV-r1).**
  Built mechanically against frozen `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` (no redesign):
  vendored `policy/model-routing.yaml` (v1; first-match-wins + mandatory `defaults`; `fallback[0] ==
  model_tier` terminating in `human`); extended `policy/model-labels.yaml` with `model_tiers`
  (abstract capability tiers, no vendor slugs); optional default-inert `model_routing:` config block;
  read-only `overseer route` (resolve / `--validate` / explain — no model call, no network, no
  dispatch, no key); exit codes `30` (malformed policy) / `31` (missing/unreadable policy);
  `overseer status` routing-validity line when `model_routing.enabled: true`. New module
  `tools/model_routing/`; seven-tier §PR.8 matrix: **43** new tests (**529** total green).
  `/build-verification-review` round 1 → **`pass`** (V1–V8 clean). ROADMAP P-route build → **DONE**;
  NEXT → **Track P / P-cost Thinking freeze**.

- **2026-07-13** — **KH3 Footprint self-integrity hard gate DONE (Thinking + Auto, same session —
  permanent fix for this repo's own self-footprint drift).** Direct follow-on to the seed-fix below:
  after seeding the 13 missing files, closed *why* they were ever silently missing for three days.
  Root cause: `overseer status --check-footprint` (the only existing check that could see this) is an
  opt-in flag, and is not wired into `review --freeze` or `governance-sync` at all — confirmed by
  direct search of both modules. **Freeze** (`docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md`,
  self-reviewed via `overseer review --freeze` checklist + semantic pass; round 1 raised one
  non-escalating MAJOR scope-risk finding — R1-M1: the initial draft trigger was "any kit-owned
  digest mismatch," which would fail-close `review --freeze`/`governance-sync` for *any* consumer
  repo with a legitimate, not-yet-`preserved` content drift (the exact false-positive class this
  session's prior hygiene fix hit for `scripts/muse-bridge-deploy.sh`) — narrowed to
  **declared-but-absent-from-disk only**; **KH3-r2 → `pass`**, stamp digest
  `sha256:4ad2c038…`): new `tools/footprint_integrity/` (`FootprintIntegrityReport`/
  `check_footprint_integrity`) checks every non-`preserved` entry **already recorded in
  `version.lock`** for existence on disk — deliberately never re-resolves the current kit templates
  and never hashes content, so it cannot fail-close on benign drift or on lightweight test fixtures.
  **Auto build** wires it into the same three fail-closed choke points KH1b/KH2 use — `overseer
  status --exit-code` (always-on, no flag — new additive `footprint_self_integrity` JSON key,
  distinct from the existing opt-in `footprint_integrity` string key, which is byte-for-byte
  unchanged), `overseer review --freeze`, `overseer governance-sync` — all reusing the existing exit
  code `2`. **Build-time refinement from the frozen §KH3.4 draft** (documented transparently, not a
  redesign): switched from checking against a fresh `resolve_footprint()` re-render to checking only
  what `version.lock` itself already declares — strictly narrower and more faithful to the actual
  incident (a kit template that has never been through a completed `sync` yet is *drift*, already
  covered by the existing `overseer status` drift check, not "declared but missing"), and this
  change alone took the initial implementation from 31 failing pre-existing tests (fixtures with
  synthetic/empty locks that don't declare the full self-footprint) down to 0. Seven-tier KH3 matrix:
  **30** new tests (**486** total green). Verified live on this repo: `overseer status
  --check-footprint --exit-code` exits `0` with `footprint_self_integrity: {state: ok}` post-fix.
  ROADMAP: added **KH3a** (Thinking, DONE) + **KH3b** (Auto, DONE). NEXT reverts to the **Track P /
  P-route Auto build** (unchanged from before this detour, same as KH2's precedent).

- **2026-07-13** — **Hygiene: seed 13 self-footprint files that were declared in
  `.overseer/version.lock` since K4b (2026-07-10) but never actually existed on disk** — `.cursor/rules/*`
  (4 files), `.cursor/skills/*/SKILL.md` (4 files), `.overseer/policy/*.yaml` (3 files),
  `.overseer/STANDING-DECISIONS.reference.md`. Root cause: the K4b commit (`042ac5c`) hand-authored the
  full manifest shape in `version.lock` to spec out §K4 without ever running `overseer init`/`sync`
  against this dogfood repo itself, and no later phase closed that gap — `overseer status
  --check-footprint` never caught it because `MISSING` classification only blocks `overseer sync`
  (needs a write), it does not fail `status`'s digest check the way `both-changed` does. Confirmed this
  is the exact, already-frozen §K7.3 "new destination absent on disk → seed" path (`docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`
  line 285), so ran `overseer sync --yes` for real (no `--force` needed — none of the 13 were
  conflicts, only `missing`). Verified: no unsubstituted `{{token}}` leakage bugs — `.mdc`/`SKILL.md`/
  policy `*.yaml` files are copied **verbatim** by design (§K4.5, `cli/footprint.py`); the `{{docs.*}}` /
  `{{vcs.*}}` notation inside them is intentional human-readable prose, not a live template token (only
  `ROADMAP.template.md`, `OVERSEER-HANDOVER.template.md`, `STANDING-DECISIONS.template.md`,
  `MUSE-BRIDGE-WORKFLOW.template.md`, and `muse-bridge-deploy.sh.template` go through real
  `render_template()` substitution). No secrets in any seeded file (scanned). `overseer status
  --check-footprint` now reports `footprint_integrity: ok` with `preserved_living` correctly listing only
  the two living docs. 456/456 tests green post-fix.

- **2026-07-12** — **Hygiene: reclassify `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` as
  `origin: preserved` in `.overseer/version.lock`; refresh stale `scripts/muse-bridge-deploy.sh` hash.**
  Root-caused a `footprint_integrity: mismatch` on `overseer status --check-footprint`. Verified by
  rendering each file fresh from its current template + `.overseer/config.yaml` and diffing byte-for-byte
  against the live file: `ROADMAP.md`/`OVERSEER-HANDOVER.md` render to a ~2KB generic seed skeleton vs.
  ~20–28KB live content — genuine, intentional living-doc growth, not drift, confirmed **not** a
  section-structure problem (headers identical `aa9cf74`→`HEAD`, single `NEXT SESSION` block +
  fenced `Paste-ready prompt` stable since `aa9cf74` 2026-07-12 09:25; the multi-block/table regression
  the operator recalled was `3061b5d`→`343093c`, 2026-07-11 08:19–14:12, already self-corrected before
  this fix). `scripts/muse-bridge-deploy.sh`'s fresh render was **byte-identical** to the live file — not
  a customization at all, just a stale `version.lock` hash from before the last real edit; kept
  `origin: kit` and refreshed via `overseer sync --force --only scripts/muse-bridge-deploy.sh` (file
  bytes unchanged, confirmed via `git diff --stat`). Root cause of why `origin: preserved` had to be set
  by hand: `cli/commands/sync.py::_is_preserved_path` only falls back to config's `living_doc_destinations()`
  when a path has **no** prior lock entry; once an entry exists (as here, from initial install) its
  explicit/default `origin` wins, so a living doc that got its first lock entry as `kit` stays `kit`
  forever without a manual reclassification — this is the supported §K6.4 mechanism, not a workaround.
  456/456 tests green post-fix. **New finding surfacing separately (not yet actioned):** `overseer status
  --check-footprint` still reports `mismatch` for a different, unrelated reason — `.cursor/rules/`,
  `.cursor/skills/`, `.overseer/policy/*.yaml`, and `.overseer/STANDING-DECISIONS.reference.md` are all
  declared in `version.lock` but do not exist anywhere in the working tree or git history (no
  `.gitignore` exclusion either) — flagged to the operator for a decision before touching it.

- **2026-07-12** — **KH2 Muse-sync hard gate DONE (Thinking + Auto, same session — permanent fix for
  live MuseHub/GitHub drift).** Diagnosed why Muse fell behind Git on this repo: two git commits
  (`52b7e6e`, `4eb6d26`) landed with no matching `muse commit`, despite `muse+git-mirror` declaring
  Muse canonical (`AGENTS.md`) — a **process gap**, not a tooling defect: `tools/substrate_health/`
  (KH1b) only ever checked that `.muse/HEAD`/`repo.json`/`config.toml` **exist**, never that Muse's
  tracked **content** was current, so nothing could have caught it. Ran the catch-up
  `muse code add -A && muse commit` first (Tier 1; commit `sha256:3e14450f…`), then froze and built
  the permanent gate in the same session so this cannot recur silently. **Freeze**
  (`docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md`, self-reviewed via `/freeze-review-loop`; round 1 raised one
  non-escalating MAJOR internal-consistency finding — R1-M1, the `governance-sync` wiring row
  described `StatusResult` as available before `adapter.status()` is actually called in
  `tools/governance_hygiene/reads.py`, contradicting the verified call order — fixed; **KH2-r2 →
  `pass`**): adds `StatusResult.muse_dirty`/`git_dirty` (populated by all three adapters, defaulted
  `None` — fully additive, existing `.dirty` meaning unchanged); a new `tools/muse_sync/` probe
  (`MuseSyncReport`/`check_muse_sync`) whose **frozen trigger** is precisely `muse_dirty and not
  git_dirty` — Git already clean (committed) while Muse's tracked snapshot still differs — so normal
  mid-edit work (both dirty, nothing committed anywhere yet) is a **frozen non-trigger** and is never
  falsely blocked; `not_applicable` for `muse-only`/`git-only` (single-history regimes have no
  cross-VCS gap). **Auto build** wires `check_muse_sync` into the same three fail-closed choke points
  `substrate_health` already uses — `overseer status --exit-code`, `overseer review --freeze`,
  `overseer governance-sync` — all reusing the **existing exit code `2`** (no renumbering of the
  frozen `status` precedence `2 > 6 > 3 > 0`). Documented boundary (§KH2.6, stated plainly, not
  oversold): does not catch drift re-masked by a *later* uncommitted edit stacked on top of an
  already-missed git commit — closing that fully needs a persisted Git-SHA anchor, deliberately
  deferred as separate scope. Seven-tier KH2 matrix: **27** new tests (**456** total green). Verified
  live on this repo: `overseer status --exit-code` now exits `0` post-catch-up, and would have exited
  `2` at the exact moment the drift first occurred had this gate existed then. ROADMAP: added **KH2a**
  (Thinking, DONE) + **KH2b** (Auto, DONE). Branch `feat/kh2-muse-sync-hard-gate` (kept separate from
  the still-open P-route PR #16 to keep both PRs single-concern). NEXT reverts to the **Track P /
  P-route Auto build** (unchanged from before this detour).
- **2026-07-12** — **Track P / P-route Thinking freeze DONE (reviewed → `pass`).** Drafted and froze
  `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md`: a **declarative model-routing policy** (not a runtime
  dispatcher). Frozen surface — `policy/model-routing.yaml` (`version 1`) mapping the selector triple
  `{position, phase_tier, gate}` → `model_tier` + ordered `fallback`, resolved by first-match-wins
  with a mandatory `defaults` terminal (total resolution); `fallback[0] == model_tier` and every chain
  terminates in `human` (fail-closed, mirrors the freeze-reviewer `fallback: human`); the additive
  `model_tiers` section extending (not forking) `policy/model-labels.yaml` with abstract capability
  tiers (no vendor slugs / endpoints / prices / keys); an optional default-inert `model_routing:`
  config block; a read-only `overseer route` surface (resolve / `--validate` / explain — no model
  call, no network, no dispatch, no key); non-overlapping exit codes `30` (malformed policy) / `31`
  (missing/unreadable policy); the rule-holder-not-executor boundary table; and the §PR.8 seven-tier
  matrix. **Boundary held (K7 / AGENTS.md):** the kit holds and validates the rulebook; the runtime
  (Cursor / OpenRouter / Scooling 9A) maps a tier to a concrete model and executes. `/freeze-review-loop`:
  checklist gate clean both rounds; **P-route-r1** raised two non-escalating MINOR consistency findings
  (R1-N1 exit-`31` wording vs. the `enabled:false` explicit-`route` path; R1-N2 unspecified
  `model_tier`↔`fallback[0]` relationship) → fixed minimally; **P-route-r2 → `pass`**; stamp written by
  `overseer review --freeze` (digest `sha256:ab6b6a9…`). **Spec-only — no code landed.** ROADMAP:
  Track P / P-route → **DONE (Thinking)**; added **Track P / P-route build** (Auto, TODO). Handover NEXT
  flips to the P-route Auto build. **429** tests unchanged.
- **2026-07-12** — **Muse adapter plain-text SHA fix + first muse canonical commit + GitHub bridge (PR #15).**
  Follow-up to the earlier `rev-parse` compat fix: discovered `muse rev-parse` (0.2.x) returns a
  **bare SHA string** on success (exit 0) and JSON only on failure (exit 1); the prior helper tried to
  parse JSON on the success path, causing `governance-sync --dry-run` to emit `invalid JSON in
  rev-parse output` after the first muse commit existed. Fixed `_muse_rev_parse_sha` in
  `adapters/base.py` to read `result.stdout.strip()` directly; updated 6 test mocks (3 e2e + 1 perf
  + 1 security + 1 unit) from JSON-wrapped responses to plain SHA strings.
  `governance-sync --dry-run` now exits 0. First **muse canonical commit** created:
  `sha256:4671b7f...` (316 files, branch `main`, author `aaronrene`, agent `cursor-agent`).
  **GitHub bridge** via `scripts/muse-bridge-deploy.sh`: exported 316 files to git `muse-mirror`
  branch; PR #15 opened (`muse-mirror -> main`). **429** tests still green.
- **2026-07-12** — **Muse adapter compat fix: `muse log --format=%H` → `rev-parse` + JSON.** Muse
  0.2.0rc15 removed the git-style `--format=%H` flag from `muse log`; all four call sites in
  `adapters/muse_only/adapter.py` + `adapters/muse_git_mirror/adapter.py` now use
  `muse rev-parse <ref>` and parse the `commit_id` field from JSON output (same pattern as
  `_muse_dirty`). Added `_muse_rev_parse_sha` helper to `adapters/base.py`. Updated 7 test mocks
  to use the new command. `governance-sync --dry-run` error now reads `muse rev-parse main: not found`
  (accurate: muse substrate has no commits on this dogfood tree) instead of an `--format=%H` syntax
  crash. **429** tests still green.
- **2026-07-12** — **Track P / P1 DONE — build verified → `pass` (P1-BV-r2).** Ran
  `/build-verification-review` (V1–V8) against frozen `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md`.
  V1/V3/V4/V5/V6/V7/V8 clean on first pass; **428** tests confirmed green; §P0.8 seven-tier matrix
  (29 tests) exercises real paths; no social features; no secrets; K7 git-only guardrail intact
  (`config.py:346` forbids `require_agent_signature` under git-only, exit `26`). **Round 1 finding
  BV1** (V2, MAJOR): §P0.6 names `verify` as a surface for exit `2` (malformed provenance), but
  `verify_chain` (`tools/honesty/ledger.py`) validated provenance structure only at append — a
  hash-consistent but structurally malformed `provenance` (unknown key) returned `0` instead of `2`.
  **Fix (feature branch, no commit):** `verify_chain` now runs `validate_provenance` per non-genesis
  entry → exit `2`; `cli/commands/ledger.py` verify path emits "malformed provenance envelope";
  added data-integrity regression `test_verify_flags_malformed_provenance_exit_2`. **Round 2 → `pass`**;
  **429** tests green (+30 §P0.8). ROADMAP P1 → **DONE**; NEXT flips to Track P / P-route Thinking freeze.
- **2026-07-12** — **Track P / P1 Auto build landed (WIP).** Shipped optional `provenance` envelope
  (`agent_id`/`model_id`/Ed25519 `sig`/`pubkey`) on non-genesis ledger entries; extended
  `compute_entry_hash` to exclude `provenance.sig` (v1 chain unbroken); `honesty.require_agent_signature`
  config (git-only `true` → config exit `26`); ledger/honesty-status verify exit `25`/`26`; Muse key
  registry seam; `cryptography` dependency for verify-only path. Seven-tier §P0.8 matrix: **29** new
  tests; **428** total green. ROADMAP P1 → **WIP** pending mandatory `/build-verification-review`.
- **2026-07-12** — **Track Q — Overseer App queued (promoted from exploration backlog).** Added
  **Q0** (Thinking freeze — `overseer app` scope: local-only web UI over the existing Python engine,
  zero engine rewrite, `127.0.0.1`-only, same fail-closed gates as the CLI), **Q1** (Auto — build the
  local web UI), **Q2** (Auto — package Q1 with **Tauri** into an installable cross-platform desktop
  app; native macOS/SwiftUI explicitly deferred) to the ROADMAP build queue. Removed the now-queued
  Track Q entry from the exploration backlog (P-deploy, hosted dashboard, P-route reference remain
  ideas-only). Verified `overseer status` gate scanner parses the new rows cleanly (0 pending gates).
  NEXT unchanged — **Track P / P1** remains the active build; Track Q awaits its own Q0 freeze session.
- **2026-07-12** — **Roadmap slices + exploration backlog added.** Queued **Track P / P-route**
  (declarative model-routing *policy*, not a dispatcher), **P-cost** (cost-*awareness* surface, not a
  dollar pricer), **P-evidence** (verification evidence capture) as TODO (each needs a Thinking freeze
  before build). Added an **Exploration backlog** section: **P-deploy** (deployment gate), **Track Q —
  Overseer App** (local GUI over the Python engine → Tauri desktop; Swift/native deferred; hosted
  read-only dashboard as a separate variant), hosted governance dashboard, and a P-route runtime
  reference (consumer-side). All captured as ideas only; boundary held: kit = governance/frontend,
  never runtime/dispatcher/model-host. NEXT unchanged (Track P / P1 build).
- **2026-07-12** — **Track P / P0 DONE (freeze reviewed → `pass`).** Ran `/freeze-review-loop` on
  `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md`: round 1 checklist gate raised F1 (C8 citation
  discipline) + F2 (C4 path-like token `/api/social/...` in §P0.9) — both non-escalating heuristic
  surfaces, fixed minimally; round 2 checklist clean + semantic review clean → `overseer review
  --freeze` wrote a `pass` stamp (digest `sha256:7db8681…`). ROADMAP P0 → DONE, added P1 (Auto)
  row; handover NEXT → Track P / P1 build.
- **2026-07-12** — **Track P / P0 scope LOCKED + contract drafted.** After reviewing the Muse social
  domain (issue #6) and the Abacus/GPT-5.6 orchestration transcript, held the kit boundary:
  **no social features in the kit.** Track P narrowed to **agent identity & signed provenance** —
  drafted `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md` (optional `provenance` envelope on ledger
  entries; canonical hash excludes `provenance.sig`; `v` stays 1; soft under git-only, hard under
  Muse; shared schema with Muse social). Social confirmed consumer-only (Muse protocol +
  Schooling UI). Pending freeze-review `pass` before P1 Auto build.
- **2026-07-12** — **Session git commit `aa9cf74`.** Synced the git branch with muse-mirrored
  K9b/K10/K11/K12 work (branch was far behind the working tree) and landed this session's KH1b +
  KH1 close-out. `.muse/` added to `.gitignore`; no secrets; 143 files, **399** tests green.
- **2026-07-12** — **KH1 DONE (close-out §KH1.6).** Locked public branding **🆗 Overseer Kit** in
  `templates/OVERSEER-HANDOVER.template.md` + `templates/README.md` token guidance; seeded **Track P / P0**
  row in ROADMAP; flipped handover NEXT → **Track P / P0 (freeze)**. KH1 + KH1b both **DONE**. **399** tests green.
- **2026-07-12** — **KH1b DONE (Auto).** Shipped §KH1.9 gate reminders:
  `tools/governance_gates/` read-only scan; `governance_gates` config schema;
  `overseer status` pending-gates JSON + human section; `governance-sync` dry-run footer;
  handover template Governance gates checklist. Seven-tier KH1b matrix (**19** new tests);
  **399** total green.
- **2026-07-12** — **Substrate health shipped (KH1b §1).** `tools/substrate_health/` probes
  `.muse/HEAD` + `repo.json` + `config.toml` when config is Muse-backed. `overseer status`
  (`--exit-code` → 2), `review --freeze`, and `governance-sync` fail-closed with remediation hint.
  **Postmortem:** K7 marked D2 DONE in docs while this checkout had hollow `.muse/`; tests used
  injected runners (K7.P4–P8), not live tree; K9a logged CLI blocked nine rounds but treated as
  workaround not blocker. ROADMAP now mandates `substrate.ok` before phase DONE.
- **2026-07-12** — **Muse dogfood repair.** Dev tree had hollow `.muse/` (`.museattributes` present but no
  `HEAD`/`repo.json` — K7 D2 never completed on this checkout). Ran `muse init --force` (Tier 1).
  Fixed muse adapters: `status --json` for Muse 0.2+ with `--porcelain` fallback. Dogfood CLI now
  green: `overseer review --freeze` + `status` on default config. §KH1.9 gate reminders
  **operator-approved**; KH1b Auto queued (reminders not automatic yet).
- **2026-07-12** — **KH1-r2 → `pass`.** Freeze-review loop (rounds 1–2) on
  `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md`: R1-M1–M4 + R1-N1 resolved; §KH1.9 governance gate
  reminder spec frozen. CLI checklist `pass` + `review_stamp` via
  `overseer --config tests/fixtures/config-git-only.yaml review --freeze …` (muse+git-mirror dev tree
  still blocked without `muse init`). Handover/contract aligned to K4/K9a ceremony. Next: **KH1 close-out**.
- **2026-07-12** — **KH1 Thinking freeze (draft).** Frozen handover relay standard
  (`docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md`): canonical NEXT SESSION shape, H1–H12 D4
  checklist for `governance-sync`, anchor map, dogfood rules. Aligned `docs/OVERSEER-HANDOVER.md`
  to `templates/OVERSEER-HANDOVER.template.md` (NEXT block, VCS table, hard stops, regeneration
  rules). Close-out deferred per §KH1.6 (branding lock + Track P seed). **380** tests unchanged.
  Next: **KH1 close-out**.
- **2026-07-12** — **K12 DONE (Thinking → Auto).** Shipped Track N public presence:
  `docs/landing/index.html` (§8 sections + GitHub→MuseHub funnel),
  `docs/landing/scenarios/index.html` (personas A–E with dogfood/reference/aspirational badges),
  Apache-2.0 `LICENSE`, `SECURITY.md`, `docs/landing/manifest.yaml`,
  `tools/landing/validate.py`, freeze contract `docs/PHASE-K12-TRACK-N-LANDING-CONTRACT.md`.
  Seven-tier K12 matrix: **19** new tests; **380** total green. No L1/L2/CLI changes. Next: **KH1**.
- **2026-07-12** — **K11 DONE (Auto).** Shipped headless API freeze provider:
  `tools/freeze_reviewer/providers/api_client.py` (`GET /health`, `POST /review`),
  injection-safe delimited artifact payloads, model-hint resolution from
  `policy/model-labels.yaml`, `OVERSEER_REVIEW_API_KEY` + `OVERSEER_REVIEW_API_URL`
  env gate (never in config), API transport/review failures → `provider_unreachable`
  exit `8`, `.github/workflows/freeze-review.yml` + `templates/ci/freeze-review-github-actions.yml`,
  `tools/freeze_reviewer/README.md` API/CI docs. Seven-tier K11 matrix: **21** new tests;
  **361** total green. No L1/L2 changes. Next: **K12 / Track N**.
- **2026-07-12** — **K10 DONE (Auto).** Shipped L2 honesty module:
  `overseer honesty-status`, `overseer ledger {append,verify,show}`, `tools/honesty/` (canonical
  JSON hash chain, genesis bootstrap, role gates, co-requirement hooks, `require_verdict_on`
  allowlist, `roles_file` v1 warn/ignore), neutral fixture pack under `tests/fixtures/honesty/`,
  SPEC §5 command table update. Seven-tier K10 matrix: **38** new tests; **340** total green.
  No L1 orchestrator changes. Next: **K11** API/CI freeze provider.
<!-- /overseer:anchor:change-log -->

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `docs/ROADMAP.md` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Build verification (mandatory):** after `{step}b`, run `/build-verification-review` before ROADMAP status → **DONE**.
5. **Closing commit:** the session-ending commit bundles code/tests + `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md`.

See `docs/ROADMAP.md` → Model-split handover protocol (SD-3) and governance sync (SD-17).

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| PR #51 | Mirror: mirror: GS-PASTE D1 VCS table align (merged 2026-07-30) |
| PR #50 | Mirror: mirror: GS-PASTE land close-out docs (merged 2026-07-30) |
<!-- /overseer:anchor:done-recently -->
