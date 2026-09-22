# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

> **NEXT right now = OCI-a (Thinking, new branch/worktree).**
> AFF-b is DONE: BV-r4 `pass` + ISR `pass`. Do not continue AFF on this branch.

---

<!-- overseer:next role=primary lane=product status=live -->
<!-- overseer:anchor:next-session -->
## NEXT SESSION — OCI-a Overseer context isolation freeze

**Date:** 2026-09-20  
**Current position:** AFF-b DONE → **OCI-a**
**Model:** Thinking

### What just landed

| Slice | Deliverable |
| --- | --- |
| **AFF-b-ISR** | Independent V1–V8 **`pass`**. Stamp re-derived `sha256:5b8a9aa5…`; `test_aff_` **101** green (`test_output` sha256:`89b76e1c…`). ISR ledger entry `a069d8ad…`. AFF-b → **DONE**. |
| **AFF-b** | Adversarial-freeze honesty gate build complete (BV-r4 + ISR). |

### THE ONE NEXT STEP — **Model: Thinking**

Freeze Overseer context isolation on a **new dedicated branch/worktree**. Do not reuse `feat/adversarial-freeze-honesty-gate`. Spec-only — no Auto.

| | |
| --- | --- |
| **ID** | **OCI-a** |
| **Branch** | `feat/overseer-context-isolation` |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/ROADMAP.md` (OCI-a row); `docs/OVERSEER-HANDOVER.md`; `docs/OVERSEER-KIT-SPEC.md` |
| **Hard stops** | New branch/worktree · no AFF reuse · no Auto · no consumer sync · no launcher replacement · no Bornfree/VideoFactory edit · no merge to `main` · no secrets · no live posture flips |
<!-- /overseer:anchor:next-session -->

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — OCI-a

```text
OCI-a — Overseer context isolation freeze (overseer-kit).

Model: Thinking
Repo: overseer-kit
Step: OCI-a
Authority: authoritative
Posture: freeze WHAT/HOW; no Auto implementation

AFF-b is DONE (BV-r4 pass + ISR pass). Start this freeze on a new dedicated
branch/worktree: feat/overseer-context-isolation. Never reuse
feat/adversarial-freeze-honesty-gate.

Read first: docs/ROADMAP.md (OCI-a row); docs/OVERSEER-HANDOVER.md;
docs/OVERSEER-KIT-SPEC.md.

Verified problem (shared kit defect reported from Bornfree / VideoFactory /
Movie Maker):
- stable consumers can execute a live unfinished kit checkout
- inherited cwd can select the wrong repo
- default-lane fallback can inject another lane's NEXT

Freeze:
- stable vs development runtime identity
- consumer-lock compatibility
- repository-bound hooks using explicit -C
- fail-closed lane/window binding
- installer/upgrade rollback
- migration
- seven-tier coverage

Create a frozen: true artifact. Run /freeze-review-loop to pass. Do not start
Auto. Do not append adversarial_freeze in the author session.

Hard stops: No consumer sync · no launcher replacement · no Bornfree /
VideoFactory edit · no merge to main without Tier 3 · no secrets · no live
posture flips · no Auto implementation during Thinking
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
| **Muse dev tree** | `ok status --exit-code` must show `substrate.ok: true`, `muse_sync.ok: true`, **and** `footprint_self_integrity.ok: true` before phase DONE |
| **Handover shape (KH1)** | Every NEXT must include valid **`Model:`** from `policy/model-labels.yaml` **and** a `### Paste-ready prompt` fenced block (H7/H8). |

---

<!-- overseer:anchor:verified-snapshot -->
## Verified snapshot

| Area | State |
| --- | --- |
| **VCS regime** | `muse+git-mirror` |
| **GitHub main** | `ebaf51831770c59d3705da85e9d72108908a8bf2` |
| **Feature tip (Git)** | `7a71efa188f22837a696a8b20f83eb0314f9094e` |
| **Feature tip (Muse)** | `sha256:b693b50c47c6c0dd0bfcfa3c3dca360f9732b93932e258c34e71080fbc3f47ae` |
| **Branch** | `feat/adversarial-freeze-honesty-gate` (AFF-b closeout). OCI-a must use a **new** branch. |
| **Dirty** | `no` |
| **Drift** | D1 drifted vs `main` until land (expected on feature branch) |
| **AFF-b** | **DONE** — BV-r4 `pass` + ISR `pass` |
| **AFF-b-ISR** | **`pass`**; verifier `cc0054de-21be-4972-ac80-22822646e805`; producer `d7f82f3d-9259-42cf-bd61-e32193d71c0a`; entry `a069d8ad…`; round 4 |
| **AFF-b-BV-r4** | **`pass`**; verifier `969C4CFD…`; evidence `f95fe2b5…`; `test_aff_` **101**; `test_output` sha256:`d47e56e52e81c53baf71813ef360beb27bd239ccda222b63c58e87e58047697e` |
| **ISR independent `test_aff_`** | **101** passed; `test_output` sha256:`89b76e1cddaabd347f7384d5c9a5a6ac689e118bb51d78bbc4888bb070c4768e` |
| **Stamp** | `sha256:5b8a9aa52ee25e9d4824e72b1df4154f8c184cc82bd30703a9b1bb5737eb96c3` (re-derived) |
| **Producer nonce** | `d7f82f3d-9259-42cf-bd61-e32193d71c0a` |
| **Muse sync** | synced |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-09-20)

| Item | Value |
| --- | --- |
| Branch | `feat/adversarial-freeze-honesty-gate` |
| GitHub `main` | `ebaf51831770c59d3705da85e9d72108908a8bf2` |
| Dirty | no |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)
- OCI-a: new branch/worktree; no consumer sync; no launcher replacement

<!-- overseer:anchor:change-log -->
- **2026-09-20** — **AFF-b-ISR → `pass`; AFF-b → DONE.** Independent verifier `cc0054de-21be-4972-ac80-22822646e805` ≠ producer `d7f82f3d…` ≠ BV-r4 `969C4CFD…`. Re-derived stamp `sha256:5b8a9aa5…`; V1–V8 clean; `test_aff_` **101** (`test_output` sha256:`89b76e1c…`). Confirmed Mode B evidence `f95fe2b5…`. Appended `independent_second_review` pass round 4, entry `a069d8ad…`. Mode D → `0`. NEXT → **OCI-a** (Thinking, new branch/worktree). No OCI-a start in this chat. No merge.

- **2026-09-20** — **AFF-b-BV-r4 → `pass`; AFF-b remains WIP pending ISR.** Independent verifier `969C4CFD-BD3F-43E7-9A51-2CBED235C114` re-derived stamp `sha256:5b8a9aa5…`; V1–V8 clean; BV3-M1/M2 closed on real `render_paste_ready`. Seven-tier `test_aff_` **101 passed** (`test_output` sha256:`d47e56e52e81c53baf71813ef360beb27bd239ccda222b63c58e87e58047697e`). Full suite **1480 passed / 15 pre-existing failures**; all 15 reproduced on parent `ebaf518`. Appended `verification_evidence` pass round 4, entry `f95fe2b5…`. No ISR, no DONE, no OCI-a, no merge. NEXT → **AFF-b-ISR**.

- **2026-09-20** — **AFF-b-FIX complete; AFF-b remains WIP.** Closed BV-r3 BV3-M1–M2 only: adversarial paste pass instruction emits full §AFF.5.2 field set; e2e asserts exact “The kit performs no model call and holds no key.” and the complete pass-field instruction from `render_paste_ready`. Seven tiers: **101 passed** (`test_output` sha256:`9aac8ce3aca73de15887fc9901d4b77d65260b4b7a1e69463a6ab449c0f06ff8`). Fixer producer_session_id `d7f82f3d-9259-42cf-bd61-e32193d71c0a`. No verification_evidence/ISR pass; no DONE; no `auto_may_start: true`; no merge. NEXT → **AFF-b-BV** (fresh Thinking chat), then ISR.

- **2026-09-20** — **AFF-b-BV-r3 → `findings`; AFF-b remains WIP.** Independent verifier `A3FD0F5F-AD08-43A0-B262-C5F7E81DDF02`. V3 failed: paste pass instruction omitted §AFF.5.2 fields (`actor_role`, `actor_session_id`, `phase_id`, `round`, `reviewer_model`); e2e asserted incomplete no-key sentence and did not assert the complete pass-field instruction. No verification_evidence/ISR pass. NEXT → **AFF-b-FIX** (cited lines only). No DONE. No OCI-a. No merge.

- **2026-09-20** — **AFF-b-FIX complete; AFF-b remains WIP.** Closed BV-r2 V3 only: §AFF.7.2 paste/`render_next_session` assertions complete; suggest+absent public `ok status --json --exit-code` restored (`state: absent`, exact §AFF.9 warning) with governance-sync retained. Seven tiers: **101 passed** (`test_output` sha256:`1bbccffea4cd7370e81c1b59bfefa9a2558239ef89fead6c51c2c530343aa575`). Fixer producer_session_id `70B57C08-5CDD-476B-AB5D-ACDDA6FC6B22`. No verification_evidence/ISR pass; no DONE; no `auto_may_start: true`; no merge. NEXT → **AFF-b-BV** (fresh Thinking chat), then ISR.

- **2026-09-20** — **AFF-b-BV-r2 → `findings`; AFF-b remains WIP.** Independent verifier re-derived stamp `sha256:5b8a9aa5…` and reproduced `test_aff_` **101** green (`test_output` sha256:`2714f0c2bb53db8b986d4c0503f8a07994be246c2ac83132bd96916c4e470e92`). V1/V2/V4–V7 clean for Mode E CLI, require `ok status --json --exit-code`, governance-sync footer, two-row + `Thinking → Auto` split, exact `type(v) is int` / non-blank `ts` / `type(round) is int`, no secrets, no `auto_may_start: true`. V3 failed: paste test still omits several §AFF.7.2 bullets (including `render_next_session`); suggest+absent public status JSON was dropped. No verification_evidence/ISR pass. NEXT → **AFF-b-FIX** (cited lines only). No DONE. No OCI-a. No merge.

- **2026-09-20** — **AFF-b-FIX complete; AFF-b remains WIP.** Repaired exactly BV-r1's public-path coverage gaps. New `test_aff_` coverage executes `ok status --json --exit-code` and governance-sync, Mode-E CLI parser/command wiring, the frozen `Thinking → Auto` split, and all §AFF.7.2 adversarial paste requirements. The require-mode governance footer now emits its fail-closed message and returns `2`. Seven tiers: **101 passed** (`test_output` sha256:`17b3cb961cade1cbe06a7ac12efd8d7c11fba2196b71a094c3bd8add7d4a33ac`). Full suite by test-directory partition: **1100 passed / 7 pre-existing non-AFF failures**; the recorded historical 15-failure baseline was not reproducible in this checkout. Fixer producer_session_id `245D25BC-C44E-4995-9687-03422D0DAB92`. No verification_evidence/ISR pass appended; no DONE; no `auto_may_start: true`; no merge. NEXT → **AFF-b-BV** (fresh Thinking chat), then ISR.

- **2026-09-20** — **AFF-b-BV-r1 → `findings`; AFF-b remains WIP.** Independent verifier reproduced seven-tier `test_aff_` **100** green (`test_output` sha256:`24051cf4…`) and full suite **1479 passed / 15 pre-existing failures**. Static/runtime V1–V2 and V4–V8 were clean, including exact `type(v) is int`, non-blank `ts`, exact `type(round) is int`, no secrets, and no `auto_may_start: true`. V3 failed: helper-only status test did not execute `ok status --exit-code` or governance-sync; no AFF test exercised Mode-E CLI parsing/command wiring; frozen `Thinking → Auto` split e2e was absent; and the adversarial NEXT assertion did not prove all §AFF.7.2 requirements. No verification-evidence pass or ISR pass appended. NEXT → **AFF-b-FIX**. OCI-a context isolation queued after AFF-b DONE on a new branch/worktree; do not bundle it into AFF.

- **2026-09-20** — **AFF-b Auto code complete (not DONE).** Built §AFF.2–§AFF.14 / §AFF.16: ledger kind `adversarial_freeze`, Mode E exit `40`, NEXT Trigger A/B + adversarial paste, status/governance-sync `adversarial_freeze_gate`, twin skill `docs/ADVERSARIAL-FREEZE-REVIEW.md` + `/adversarial-freeze-review`, dogfood `adversarial_freeze: suggest`, shared envelope (`type(v) is int`, non-blank `ts`) + `type(round) is int` on all round-bearing kinds + AFF resolver. `test_aff_` **100** green (`test_output` sha256:`b64bac0e…`). Producer nonce `AED44535-4E5B-4F56-BA72-81B44E222C16`. Circular-import fix committed (`d8cffc6`). No `auto_may_start: true`. No model dispatch. No merge. NEXT → **AFF-b-BV** (Thinking, second chat) then ISR (`require`).

- **2026-09-20** — **AFF-ADV-r5 → `pass`; AFF-a DONE.** Mechanical restamp `sha256:5b8a9aa5…`. Reviewer nonce `aff-adv-r5-2026-09-20` ≠ author `aff-a-author-fix-r4-2026-09-20`. NEXT was **AFF-b** (Auto).

- **2026-09-20** — **AFF-r7 author repair → `pass` (AFF-a still WIP).** Closed ADV4-M1–M2. Mechanical stamp `sha256:04dda1dc…`.

- **2026-09-20** — **AFF-ADV-r4 → `findings` (AFF-a still WIP).** ADV4-M1–M2 recorded.

- **2026-09-20** — **AFF-r6 author repair → `pass` (AFF-a still WIP).** Closed ADV3-M1–M3.

- **2026-09-20** — **AFF-ADV-r3 → `findings` (AFF-a stays WIP).** ADV3-M1–M3 recorded.

- **2026-09-20** — **AFF-r5 author repair → `pass` (AFF-a still WIP).** Closed ADV2 findings.

- Older entries: docs/archive/handover/CHANGE-LOG.md
<!-- /overseer:anchor:change-log -->

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `docs/ROADMAP.md` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Build verification (mandatory):** after `{step}b`, run `/build-verification-review` before ROADMAP status → **DONE**.
5. **Closing commit:** the session-ending commit bundles code/tests + `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md`.
6. **Change log compaction:** living change log keeps the newest 15 dated bullets via `ok handover-compact --write`.

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| **AFF-b-ISR** | **`pass`** — V1–V8 clean; ISR entry `a069d8ad…`; AFF-b → DONE. |
| **AFF-b-BV-r4** | **`pass`** — V1–V8 clean; evidence `f95fe2b5…`. |
| **AFF-b-FIX** | Closed BV-r3 BV3-M1/M2; `test_aff_` **101**. |
| **AFF-b-BV-r3** | **`findings`** — incomplete §AFF.5.2 pass-field instruction + incomplete no-key e2e. |
| **AFF-b-FIX (BV-r2)** | Closed BV-r2 V3; `test_aff_` **101**. |
| **AFF-b-BV-r2** | **`findings`** — incomplete §AFF.7.2 assertions + dropped suggest+absent status JSON. |
| **AFF-b-BV-r1** | **`findings`** — public status/governance and Mode-E CLI coverage plus split-flow e2e repair required. |
| **AFF-b Auto** | Code complete then BV+ISR. §AFF.2–§AFF.14; dogfood `suggest`; Mode E `40`. |
| **AFF-ADV-r5** | Different-chat attack review → **`pass`**. AFF-a DONE. Stamp `sha256:5b8a9aa5…`. |
| **AFF-a** | Adversarial-freeze honesty gate freeze **`pass`**. Spec-only. |
| **FRV-b** | F1–F7 **DONE** — BV `pass` + ISR `pass`. |
<!-- /overseer:anchor:done-recently -->

## Change log

- **2026-09-20** — **AFF-b-ISR → `pass`; AFF-b → DONE.** Independent `test_aff_` **101** (`sha256:89b76e1c…`); ISR entry `a069d8ad…`. NEXT → **OCI-a** (new branch/worktree).

- **2026-09-20** — **AFF-b-BV-r4 → `pass`; AFF-b remains WIP.** `test_aff_` **101** (`sha256:d47e56e…`); evidence `f95fe2b5…`; full-suite 15/15 failures reproduced on parent. NEXT → **AFF-b-ISR**.

- **2026-09-20** — **AFF-b-FIX complete; AFF-b remains WIP.** Closed BV-r3 BV3-M1–M2; `test_aff_` **101** (`sha256:9aac8ce3…`). NEXT → **AFF-b-BV**.

- **2026-09-20** — **AFF-b-BV-r3 → `findings`; AFF-b remains WIP.** Verifier `A3FD0F5F…`. V3: incomplete §AFF.5.2 pass fields + incomplete no-key e2e. NEXT → **AFF-b-FIX**.

- **2026-09-20** — **AFF-b-FIX complete; AFF-b remains WIP.** Closed BV-r2 V3; `test_aff_` **101** (`sha256:1bbccffe…`). NEXT → **AFF-b-BV**.

- **2026-09-20** — **AFF-b-BV-r2 → `findings`; AFF-b remains WIP.** Independent `test_aff_` **101** (`sha256:2714f0c2…`). V3: incomplete §AFF.7.2 assertions + dropped suggest+absent status JSON. NEXT → **AFF-b-FIX**.

- **2026-09-20** — **AFF-b-FIX (BV-r1)** repaired public status/governance-sync, Mode-E CLI, and `Thinking → Auto` split. `test_aff_` **101**. NEXT was AFF-b-BV.

- **2026-09-20** — **AFF-b-BV-r1 → `findings`; AFF-b remains WIP.** Independent `test_aff_` **100**; full suite **1479 / 15 pre-existing**. NEXT → **AFF-b-FIX**. OCI-a queued separately after AFF closes.

- **2026-09-20** — **AFF-b Auto code complete (not DONE).** `test_aff_` **100**; producer `AED44535…`; NEXT → **AFF-b-BV** then ISR. No DONE, no merge, no `auto_may_start: true`.

- **2026-09-20** — **AFF-ADV-r5 → `pass`; AFF-a DONE.** Mechanical restamp `sha256:5b8a9aa5…`. NEXT was **AFF-b** (Auto).

- **2026-09-20** — **AFF-r7 author repair → `pass`; AFF-a remains WIP.** NEXT was AFF-ADV-r5.

- **2026-09-20** — **AFF-ADV-r4 → `findings`; AFF-a remains WIP.** ADV4-M1–M2 recorded.

- **2026-09-20** — **AFF-r6 author repair → `pass`; AFF-a remains WIP.**

- **2026-09-20** — **AFF-ADV-r3 → `findings`; AFF-a remains WIP.**

- **2026-09-20** — **AFF-r5 author repair → `pass`; AFF-a remains WIP.**
