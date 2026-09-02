# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

<!-- overseer:next role=primary lane=product status=live -->
<!-- overseer:anchor:next-session -->
## NEXT SESSION — Consumer LT rollout (Operator)

**Date:** 2026-09-02  
**Current position:** LT → main DONE (PR #72 @ `ff737cc`) → consumer rollout  
**Model:** Operator

### What just landed

| Slice | Deliverable |
| --- | --- |
| **LT → main (land-b)** | PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) merged @ `ff737cc`. Footprint coverage; session bookends; honesty warn; `ok handover-compact`; optional-feature tips. |
| **LT-b** | Loop tightening build on `main` (BV `pass`, LT-b-BV-r1; §LT.10 **34** green). |

### THE ONE NEXT STEP — **Model: Operator**

Roll LT out to consumer repos that already vendor the kit: in each repo run `ok sync` (use `--force` only when sync reports kit-owned conflicts you accept). Optionally enable `session_bookends.enabled: true` and/or honesty warn per repo. Do **not** invent a new kit phase until rollout is done or you consciously defer it.

| | |
| --- | --- |
| **ID** | **consumer-lt-rollout** |
| **Branch** | (per consumer repo) |
| **Repo** | consumer repos using overseer-kit (Knowtation, Scooling, VideoFactory, …) |
| **Read first** | this handover; `cursor/hooks/README.md`; each consumer `.overseer/config.yaml` |
| **Hard stops** | No merge to kit `main` without Tier 3 · no secrets · no live posture flips · no `--include-preserved` wipe of living docs |
<!-- /overseer:anchor:next-session -->

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — consumer LT rollout

```text
Consumer LT rollout — after overseer-kit PR #72 on main.

Model: Operator
Repo: each consumer that vendors overseer-kit
Step: consumer-lt-rollout
Authority: authoritative

Read first: overseer-kit `docs/OVERSEER-HANDOVER.md` (this NEXT); consumer `.overseer/config.yaml`; `cursor/hooks/README.md`.

Deliverables:
- In each consumer repo: `ok sync` (resolve conflicts with `--force` only when intentional; never `--include-preserved` unless wiping living docs on purpose).
- Optional per repo: set `session_bookends.enabled: true` then re-sync for Cursor start/end nudges; set honesty warn if desired.
- Confirm `ok status` shows footprint_coverage ok (when hooks expected) and no unexpected tips you already enabled.
- When rollout is done (or deferred), pick next kit backlog freeze from `docs/ROADMAP.md` exploration backlog.

Hard stops: No kit main merge without Tier 3 · no secrets · no live posture flips · do not clobber preserved living docs

Governance sync: update kit handover when rollout completes or is deferred.
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
| **GitHub main** | `ff737ccabdfd165232f0b0173cd912142b9b48b7` |
| **Canonical anchor** | `sha256:fdd10e9dde18c4e14eec5d9a910dcc9d47b00d26c6cc0a144cc5d58af1237c65` |
| **Canonical main** | `sha256:fdd10e9dde18c4e14eec5d9a910dcc9d47b00d26c6cc0a144cc5d58af1237c65` |
| **Branch** | `main` |
| **Dirty** | `yes` |
| **Drift** | D1=drifted, D2=aligned, D3=aligned |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-09-02)

| Item | Value |
| --- | --- |
| Branch | `main` |
| GitHub `main` | `ff737ccabdfd165232f0b0173cd912142b9b48b7` |
| Canonical anchor | `sha256:fdd10e9dde18c4e14eec5d9a910dcc9d47b00d26c6cc0a144cc5d58af1237c65` (.muse/git-bridge.toml:last_export.muse_commit_id) |
| Muse `main` | `sha256:fdd10e9dde18c4e14eec5d9a910dcc9d47b00d26c6cc0a144cc5d58af1237c65` |
| Dirty | yes |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
- **2026-09-02** — **LT → main DONE (land-b).** GitHub PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) merged @ `ff737cc` (LT-a freeze + LT-b build). Local `main` FF; post-merge hygiene; NEXT → **consumer-lt-rollout**.

- **2026-09-01** — **LT-b DONE (Auto build + BV `pass`, LT-b-BV-r1).** Built exactly to frozen `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md`: footprint coverage gate; `session_bookends` (default off, dogfood enabled + hooks synced); kit honesty warn + active-slice Mode B; `ok handover-compact` + dogfood compact (**88** archived); optional-feature tips on `ok status`; workspace-root docs; §LT.10 **34** green. `ok sync --force` applied; `footprint_coverage: ok`. No consumer defaults; no tab-reload claim. NEXT → **queue-idle**.

- **2026-09-01** — **LT-a DONE (Thinking freeze).** `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md` → `pass` (LT-r2), stamp `sha256:6a5aafb5…`. Slices 1–4 frozen. **No LT-b Auto code this session.** NEXT → LT-b Auto on `feat/loop-tightening`.

- **2026-09-01** — **LT-a drafted (Thinking freeze, review pending).** Slices 1–4 in `docs/archive/phases/PHASE-LT-LOOP-TIGHTENING.md` on `feat/loop-tightening`. Backlog captured: independent second reviewer, KH2 remask, session-type bookends, auto-enable hooks, host tab reload. No Auto code.

- **2026-08-12** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `31a4da1`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-08-12** — **Public repository visibility flip DONE (docs sync).** GitHub repo already **public**; marked ROADMAP + checklist; NEXT → **queue-idle** (zero open rows). Tip refresh to GitHub `main` @ `31a4da1`.

- **2026-08-12** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `cc63529`; realign: D2 aligned — skip realign; next_regen=regenerated

- **2026-08-12** — **ONS → main DONE (land-b).** Muse FF `sha256:3e21a881…` → GitHub PR [#68](https://github.com/aaronrene/overseer-kit/pull/68) @ `588da95`; post-merge sync; D3 `pr_matches_row` generic-token harden (visibility/checklist false-stamp); NEXT → **Public repository visibility flip**. `ok land-closeout` → `0`.

- **2026-08-12** — governance-sync: drift (D1=drifted, D2=aligned, D3=drifted) @ `588da95`; realign: D2 aligned — skip realign; next_regen=regenerated:land-b

- **2026-08-12** — **ONS-b DONE (Auto build + BV `pass`, ONS-BV-r1, 0 findings).**
  Built exactly to frozen `docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md`:
  `tools/print_next/` (`extract_current_next` / `format_current_next`, reuses
  `extract_paste_fence_body`); `cli/commands/next.py` (`EXIT_NEXT_MALFORMED=37`);
  `ok next` + `ok governance-sync --print-next` short-circuit (mutually exclusive with
  `--write` / `--all-lanes`); skill + alwaysApply rule; `docs/PRINT-NEXT.md` + AGENTS +
  consumer stubs; SPEC §5 additive row; optional `cursor/hooks/` fail-open template
  **not** in footprint. Seven-tier §ONS.12 **24** green
  (`test_output` sha256:`973cb70ffa10b65de4793fb9ea3599035e60efe5c3f1b5e72ad46ab476d66973`).
  Host niceties are **not** a DONE gate; no tab-reload claim. NEXT → **ONS → main (land-a)**.

- **2026-08-12** — **ONS-a DONE (Thinking freeze).** Authored + freeze-reviewed
  `docs/archive/phases/PHASE-ONS-OPERATOR-NEXT-SURFACING.md` → `pass` (ONS-r2), stamp
  `sha256:242e318f…`. Portable contract: `ok next` / `ok governance-sync --print-next`
  (read-only extract, fail-closed exit `37`); skill + alwaysApply rule via `ok sync`;
  Copilot `docs/PRINT-NEXT.md`; host niceties best-effort and **not** a DONE gate.
  Does not claim IDE tab reload; no per-branch handover names; GS-PASTE regen unchanged.
  **No ONS-b Auto code this session.** NEXT → ONS-b Auto on `feat/ons-operator-next-surfacing`.
  Public visibility flip remains queued (operator Tier 3).

- **2026-08-04** — **Contributor → main DONE (SD-21).** Product PR [#63](https://github.com/aaronrene/overseer-kit/pull/63) @ `0e80a42` (Muse FF `sha256:9c9e489…` → bridge → `ok pr-land`). land-b docs PR [#65](https://github.com/aaronrene/overseer-kit/pull/65) @ `8a37818` (PR #64 closed — squash-history conflict on muse-mirror). NEXT remains **Public visibility flip**. Repo still **private**.

- **2026-08-04** — **Contributor prep DONE** on `feat/contributor`: authored `CONTRIBUTING.md` + `docs/MIGRATE-EXISTING-REPO.md` + `docs/PUBLIC-VISIBILITY-CHECKLIST.md`; removed non-public laundry (`docs/archive/personal|operators|consumers`); secrets/history pass clean on working tree (`desktop/keys` public-only). NEXT → **Public visibility flip** (Tier 3 operator). Repo still **private** until operator flips.

- **2026-08-04** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `dfc77b8`; realign: D2 aligned — skip realign; next_regen=regenerated

- **2026-08-04** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `bdee603`; realign: D2 aligned — skip realign; next_regen=regenerated

- Older entries: docs/archive/handover/CHANGE-LOG.md
<!-- /overseer:anchor:change-log -->

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `docs/ROADMAP.md` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Build verification (mandatory):** after `{step}b`, run `/build-verification-review` before ROADMAP status → **DONE**.
5. **Closing commit:** the session-ending commit bundles code/tests + `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md`.
6. **Change log compaction:** living change log keeps the newest 15 dated bullets. Older bullets move via `ok handover-compact --write` to `docs/archive/handover/CHANGE-LOG.md`.

See `docs/ROADMAP.md` → Model-split handover protocol (SD-3) and governance sync (SD-17).

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| **LT → main** | PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) @ `ff737cc` (merged 2026-09-02) |
| **LT-b** | Loop tightening build: footprint coverage; session bookends; honesty warn; `ok handover-compact`; optional-feature tips on `ok status`; §LT.10 **34** green; BV **`pass`** (LT-b-BV-r1). |
<!-- /overseer:anchor:done-recently -->

## Change log

- **2026-09-02** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `ff737cc`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows
