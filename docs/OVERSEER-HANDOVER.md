# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

<!-- overseer:next role=primary lane=product status=live -->
<!-- overseer:anchor:next-session -->
## NEXT SESSION — NXP-b NEXT provenance build

**Date:** 2026-09-04  
**Current position:** NXP-a freeze **`pass` (NXP-r3)**, stamp `sha256:53a5999d…` → NXP-b cleared to build  
**Model:** Auto

### What just landed

| Slice | Deliverable |
| --- | --- |
| **Session-start hook fix** | Multi-lane repos printed only the default lane, hiding queued work in other lanes. Fixed in `cursor/hooks/session-start-next.sh` + `.cursor/hooks/…`; Muse commit `1927dd90` on `fix/session-start-hook-multi-lane` (was stranded in Git only). |
| **Governance freshness** | D1 drift cleared via `ok governance-sync --write` → `970cbd44`; `governance-sync: aligned (D1–D3)` confirmed. |
| **NXP-a freeze** | `docs/archive/phases/PHASE-NXP-NEXT-PROVENANCE.md` — `pass` (NXP-r3). N1 provenance line, N2 JSON identity keys, N3 non-silent `check-next`, N4 board-name advisory (warn), N5 hook sequencing. |

### Verified root cause (do not re-derive)

Two repos injected byte-identical `## CURRENT NEXT — paste this` headings into one chat with no
attribution. The identity data **already exists** in `CurrentNextResult` (`tools/print_next/extract.py:35-41`)
and is simply never emitted on the human surface; `--json` already carries it. Separately, K13
§MR.6.5 repo-prefixed board names are **already built** (K13b DONE) but inert — `ok workspace
check-next` exits `0` with "workspace not configured", so nothing ever nudges a repo to adopt them.

### THE ONE NEXT STEP — **Model: Auto**

Build NXP-b mechanically against the frozen spec. No redesign.

| | |
| --- | --- |
| **ID** | **NXP-b** |
| **Repo** | overseer-kit |
| **Read first** | `docs/archive/phases/PHASE-NXP-NEXT-PROVENANCE.md` §NXP.3–§NXP.8; `docs/ROADMAP.md` NXP rows |
| **Hard stops** | No merge to `main` without Tier 3 · no secrets · **do not disable hooks** · no consumer renames · no `workspace.yaml` authoring · no fence-body or heading byte changes · no hook auto-enable |
<!-- /overseer:anchor:next-session -->

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — NXP-b NEXT provenance build

```text
overseer-kit — NXP-b NEXT provenance build (Auto)

Model: Auto
Repo: overseer-kit
Step: NXP-b
Authority: ROADMAP row NXP-b
Consumes: docs/archive/phases/PHASE-NXP-NEXT-PROVENANCE.md (frozen: true, pass NXP-r3)

Context: `ok next` prints a block whose heading is byte-identical in every repo, so when two
repos inject blocks into one chat neither the operator nor the agent can tell which authority
each carries. The identity data already exists in CurrentNextResult and is simply not emitted.
Separately, K13 repo-prefixed board names are already built but inert because
`ok workspace check-next` exits 0 when no workspace manifest is configured.

Do:
 1. Read docs/archive/phases/PHASE-NXP-NEXT-PROVENANCE.md in full — build only what §NXP.3-§NXP.6 freeze
 2. N1: provenance line on `ok next` human stdout per §NXP.3.1 twelve-step layout + §NXP.3.2 template
 3. N2: additive --json keys repo_name / repo_root / read_at (§NXP.4)
 4. N3: `ok workspace check-next` advisory instead of silent exit-0 success (§NXP.5)
 5. N4: bare-board-name advisory in `ok status` — warn only, never a gate (§NXP.6)
 6. Update the existing ONS §ONS.5.4 layout assertions per §NXP.3.3 — expected, not a regression
 7. Add the injectable clock seam per §NXP.3.4
 8. Run seven-tier §NXP.8 + full suite; then /build-verification-review until pass

Do not: disable or remove session hooks · auto-enable hooks anywhere · rename any consumer
handover · author any workspace.yaml · change fence-body bytes or CURRENT_NEXT_HEADING ·
make board naming a blocking gate · print a NEXT block without provenance as a degrade path ·
merge to main without Tier 3

Hard stops: No kit main merge without Tier 3 · no secrets · no live posture flips
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
| **GitHub main** | `ce16f9bd87765a854b447500ba0b58d24e1b3a4c` |
| **Canonical anchor** | `sha256:6abcf1fa82a7a621ccbc945f19acdba5bc0db54569599404a1452fb4a096a199` |
| **Canonical main** | `sha256:6abcf1fa82a7a621ccbc945f19acdba5bc0db54569599404a1452fb4a096a199` |
| **Branch** | `fix/session-start-hook-multi-lane` |
| **Dirty** | `no` |
| **Drift** | D1=drifted, D2=aligned, D3=aligned |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-09-04)

| Item | Value |
| --- | --- |
| Branch | `fix/session-start-hook-multi-lane` |
| GitHub `main` | `ce16f9bd87765a854b447500ba0b58d24e1b3a4c` |
| Canonical anchor | `sha256:6abcf1fa82a7a621ccbc945f19acdba5bc0db54569599404a1452fb4a096a199` (.muse/git-bridge.toml:last_export.muse_commit_id) |
| Muse `main` | `sha256:6abcf1fa82a7a621ccbc945f19acdba5bc0db54569599404a1452fb4a096a199` |
| Dirty | no |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
- **2026-09-02** — **ISR default → `require`** (operator posture). Absent key / shipped default is now `require` (was `off`); kit dogfood `require` (was `warn`). Opt out: `off` or `warn`. PHASE-ISR operator amend recorded. Closed-loop premise.

- **2026-09-02** — **ISR → main + MuseHub solidify DONE.** Hub → staging; created `aaronrene/overseer-kit`; pushed 85 commits; PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) @ `84db8c8`. NEXT → **queue-idle**.

- **2026-09-02** — **MuseHub-first before ISR merge** — Gap confirmed: hub `localhost:1337` dead; `aaronrene/overseer-kit` 404 on staging/production. Operator: solidify MuseHub staging then merge PR #74. Handover + paste + `MUSE-BRIDGE-WORKFLOW.md` retargeted.

- **2026-09-02** — **ISR → main land-a** — Muse FF `feat/isr-independent-second-reviewer` → `main` (`sha256:f59d4cc6…`) → muse-bridge → GitHub PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) OPEN/mergeable. Rebased stale `muse-mirror` onto `main` before re-export (LT #72/#73 had bypassed mirror). Merge held for MuseHub-first. `require_independent_second_reviewer` remains kit dogfood **warn**.

- **2026-09-02** — **ISR-b DONE** (Auto + second-chat BV `pass`, ISR-b-BV-r1). V1–V8 against freeze + branch diff; `independent_second_review` pass (actor `c72e9414…` ≠ producer `62762b24…`); Mode B `verification_evidence` (`test_output` sha256:`4a82e963…`). `test_isr_` **48** green. NEXT → **ISR → main (land-a)**. No merge this session.

- **2026-09-02** — **ISR-a DONE (Thinking freeze).** `docs/archive/phases/PHASE-ISR-INDEPENDENT-SECOND-REVIEWER.md` → `pass` (ISR-r4), stamp `sha256:e6284150…`. Second-chat / separate-verifier gate before Auto DONE; kit records/gates only; no model dispatch; portable CLI+docs primary; seven-tier §ISR.11 frozen. **No ISR-b Auto code this session.** NEXT → ISR-b Auto on `feat/isr-independent-second-reviewer`.

- **2026-09-02** — **consumer-lt-rollout DONE.** `ok sync` LT footprint into Knowtation, Scooling, VideoFactory, the-brain, bornfree-hub, ourware, scooling-lab, scooling-sc-brain. Knowtation/Scooling: `session_bookends` + honesty warn + hooks; VF/the-brain: bookends + hooks (honesty tip deferred). Knowtation/VF used `--only` to avoid clobbering living docs / consumer-modified policy. All synced repos `footprint_coverage: ok`. Deferred: MuseHub (no config.yaml), bornfree/ourware/lab bookends, VF full `--force` on customized tiers/rules, Knowtation `origin:kit` living-doc lock hygiene. NEXT → **ISR-a** (Independent second reviewer Thinking freeze).

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
| PR #73 | docs: LT land-b closeout + consumer rollout NEXT (merged 2026-09-02) |
| PR #71 | Mirror: mirror: public visibility flip DONE + queue-idle NEXT (merged 2026-08-13) |
| **MuseHub solidify** | Hub → `staging.musehub.ai`; public `aaronrene/overseer-kit`; first `muse push -u staging main` (85 commits). Kit dogfood matches Knowtation/Scooling hub posture. |
| **ISR → main** | PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) merged @ `84db8c8` (ISR-a freeze + ISR-b + MuseHub docs). |
| **ISR-a + ISR-b** | Freeze `pass` (ISR-r4) + BV `pass` (ISR-b-BV-r1); `require` stays off for consumers (kit dogfood **warn**). |
<!-- /overseer:anchor:done-recently -->

## Change log

- **2026-09-04** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `ce16f9b`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-02** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `fc2ecb0`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-02** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `945d034`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows

- **2026-09-02** — **ISR → main + MuseHub solidify DONE.** PR [#74](https://github.com/aaronrene/overseer-kit/pull/74) @ `84db8c8`; staging hub hosts kit. NEXT → **queue-idle**.
- **2026-09-02** — **MuseHub solidify DONE** — connected `staging.musehub.ai`; created public `aaronrene/overseer-kit`; first push 85 commits.
- **2026-09-02** — **ISR-b DONE** (Auto + BV `pass`, ISR-b-BV-r1).
- **2026-09-02** — **ISR-a DONE (Thinking freeze).** PHASE-ISR → `pass` (ISR-r4).
- **2026-09-02** — **consumer-lt-rollout DONE.** LT synced to live consumers.
- **2026-09-02** — **LT → main DONE (land-b).** PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) @ `ff737cc`.
