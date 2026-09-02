# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

<!-- overseer:next role=primary lane=product status=live land-phase=land-a -->
<!-- overseer:anchor:next-session -->
## NEXT SESSION — ISR → main (land-a)

**Date:** 2026-09-02  
**Current position:** ISR-b BV `pass` → Muse FF + muse-bridge PR → **stop for Tier 3 merge**  
**Model:** Operator + Auto  
**land-phase:** land-a

### What just landed

| Slice | Deliverable |
| --- | --- |
| **ISR-b (Auto + BV)** | Built exactly to freeze; second-chat `/build-verification-review` **V1–V8 `pass`** (ISR-b-BV-r1). Ledger `independent_second_review` + Mode B `verification_evidence` appended. `actor_session_id` `c72e9414-24f0-4446-9a1b-d9ff5d60bd99` ≠ producer `62762b24-69e5-4c95-b38e-cadbf261f9af`. `test_isr_` **48** green. ROADMAP ISR-b **DONE**. |
| **ISR-a** | Freeze → `pass` (ISR-r4), stamp `sha256:e6284150…`. |

### THE ONE NEXT STEP — **Model: Operator + Auto**

SD-21 land-a: Muse FF `feat/isr-independent-second-reviewer` → `main` → muse-bridge → GitHub PR `muse-mirror` → `main`. **Stop for Tier 3 merge authorization.** Do not merge without authorization. Kit does not run another model. Do not enable consumer `require`.

| | |
| --- | --- |
| **ID** | **ISR → main (land-a)** |
| **land-phase** | `land-a` |
| **Branch** | `feat/isr-independent-second-reviewer` |
| **Repo** | overseer-kit |
| **Read first** | this handover; `docs/ROADMAP.md` ISR → main row; SD-21 land ritual |
| **Hard stops** | No merge to kit `main` without Tier 3 · no secrets · no live posture flips · no model dispatch · no consumer `require` |
<!-- /overseer:anchor:next-session -->

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — ISR → main (land-a)

```text
ISR → main land-a (SD-21).

Model: Operator + Auto
Repo: overseer-kit
Step: ISR-land-a
Branch: feat/isr-independent-second-reviewer
Authority: authoritative

Read first: docs/OVERSEER-HANDOVER.md (this NEXT); docs/ROADMAP.md ISR → main row.

ISR-a freeze + ISR-b Auto are DONE. Second-chat BV pass (ISR-b-BV-r1). Land on operator Tier-3 authorization only:

1. Muse FF feat/isr-independent-second-reviewer → main.
2. muse-bridge → GitHub PR muse-mirror → main.
3. Do not merge without explicit Tier 3 authorization.
4. Kit does not run another model. Do not enable consumer require.

Hard stops: No kit main merge without Tier 3 · no secrets · no live posture flips · no model dispatch
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
| **Branch** | `feat/isr-independent-second-reviewer` |
| **Dirty** | `yes` |
| **Drift** | D1=drifted, D2=aligned, D3=aligned |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-09-02)

| Item | Value |
| --- | --- |
| Branch | `feat/isr-independent-second-reviewer` |
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
| **ISR-b** | Independent second reviewer Auto + BV `pass` (ISR-b-BV-r1); `test_isr_` 48 green; ISR ledger pass from second chat |
| **ISR-a** | Independent second reviewer freeze → `pass` (ISR-r4), stamp `sha256:e6284150…`. Spec-only; no Auto code. |
| **consumer-lt-rollout** | LT sync across live consumers; bookends/honesty opted in on primary Cursor repos; `footprint_coverage: ok` |
| **LT → main** | PR [#72](https://github.com/aaronrene/overseer-kit/pull/72) @ `ff737cc` (merged 2026-09-02) |
<!-- /overseer:anchor:done-recently -->

## Change log

- **2026-09-02** — **ISR-b DONE** (Auto + BV `pass`, ISR-b-BV-r1). Second-chat ISR + Mode B evidence; NEXT → **ISR → main (land-a)**.
- **2026-09-02** — **ISR-a DONE (Thinking freeze).** PHASE-ISR → `pass` (ISR-r4). NEXT → **ISR-b**.
- **2026-09-02** — **consumer-lt-rollout DONE.** LT synced to live consumers; bookends/honesty on primary repos; NEXT → **ISR-a**.
- **2026-09-02** — governance-sync: drift (D1=drifted, D2=aligned, D3=aligned) @ `ff737cc`; realign: D2 aligned — skip realign; next_regen=human_authorship_required:zero_open_rows
