# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

## NEXT SESSION — Track P / P0 (freeze) (▶ NEXT)

**Date:** 2026-07-12  
**Current position:** **KH1 DONE** (§KH1.6 close-out complete); **KH1b DONE**; **399** tests green. Track P seeded — **P0 Thinking freeze** is next (scope at session).  
**Model:** **Thinking** (Track P / P0 — spec freeze only; no code)

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| **KH1 close-out** | 🆗 branding lock in template + `templates/README.md`; Track P row seeded; KH1 → **DONE** |
| **KH1b** | Substrate health + §KH1.9 gate reminders live (`tools/governance_gates/`) |
| **KH1-r2** | Handover relay standard frozen + reviewed → **`pass`** |
| **Muse dogfood** | D2 repaired; substrate + gate reminders on `status`/`review`/`governance-sync` |
| **K12 / Track N** | Public landing + scenario gallery (**399** tests green) |
<!-- /overseer:anchor:done-recently -->

### THE ONE NEXT STEP — **Model: Thinking (Track P / P0 freeze)**

Freeze Track P **P0** scope in a `docs/PHASE-TRACK-P-P0-*.md` contract (Thinking only — no Auto build).

| | |
| --- | --- |
| **ID** | **Track P / P0** |
| **Branch** | `feat/track-p-p0` (slug = `track-p-p0`) |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/ROADMAP.md`; `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md`; this handover |
| **Hard stops** | No secrets; no commit/push without consent; **P0 = spec freeze only — no code** |

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — Track P / P0 (freeze)

```
Phase Track P / P0 — Product lane bootstrap freeze (overseer-kit).

Model: Thinking.

Shared context:
- Project: 🆗 Overseer Kit — repo-agnostic governance vendoring CLI
- Read: docs/ROADMAP.md; docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md; docs/OVERSEER-HANDOVER.md
- Guardrails: no secrets; fail-closed; no commit/push without consent
- Close: update docs/ROADMAP.md + docs/OVERSEER-HANDOVER.md together

Task (P0 Thinking freeze only — no Auto build):
- Define Track P product-lane scope with operator (what P builds after P0 passes).
- Freeze contract at docs/PHASE-TRACK-P-P0-<slug>.md with frozen: true YAML block + Review record.
- Run /freeze-review-loop then overseer review --freeze when CLI green.
- Flip handover NEXT to Track P / P1 or first P build slice after pass.

Governance gates (mandatory — remind only; silence is not pass):
- Freeze review: /freeze-review-loop before Thinking freeze → DONE; overseer review --freeze when CLI green
- Build verification: /build-verification-review after every Auto {step}b before ROADMAP DONE
- overseer status and overseer governance-sync emit pending gates for the active slice

Governance sync: update docs/ROADMAP.md + docs/OVERSEER-HANDOVER.md on completion.
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
| **Governance gates** | §KH1.9 **live** — `overseer status` + `governance-sync` pending-gate reminders |
| **Muse dev tree** | `overseer status --exit-code` must show `substrate.ok: true` before phase DONE. Hollow → `muse init --force .` (Tier 1) |

---

<!-- overseer:anchor:verified-snapshot -->
## Verified snapshot

| Area | State |
| --- | --- |
| **Repo** | overseer-kit |
| **VCS regime** | `muse+git-mirror` (canonical: muse) |
| **Governance docs** | `docs/OVERSEER-HANDOVER.md`, `docs/ROADMAP.md` |
| **KH1 contract** | `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` — **reviewed → `pass` (KH1-r2)** |
| **Kit version** | `0.1.0` (`VERSION`) |
| **K12 / Track N** | **DONE** — landing + scenario gallery + LICENSE + funnel; **399** tests green |
| **KH1 Handover relay** | **DONE** — contract `pass` (KH1-r2); §KH1.6 close-out complete |
| **Track P / P0** | **TODO** — product lane bootstrap; P0 Thinking freeze next |
| **Muse dogfood** | **D2 repaired** + substrate health + gate reminders live |
| **KH1b** | **DONE** — substrate §1 + gate reminders §2 |
| **Public brand** | **🆗 Overseer Kit** (locked in template + landing) |
| **CLI** | `init` \| `sync` \| `status` \| `review --freeze` \| `governance-sync` \| `verify-step` \| `honesty-status` \| `ledger` |
| **Public landing** | `docs/landing/index.html` · scenario gallery `docs/landing/scenarios/index.html` |
<!-- /overseer:anchor:verified-snapshot -->

<!-- overseer:anchor:vcs-table -->
## VCS (verified 2026-07-12)

| Item | Value |
| --- | --- |
| Branch | `docs/k9-layered-honesty-vision` |
| HEAD | `343093cfdbc226172521b96ed7ce21f625c24c33` |
| Dirty | yes |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
## Change log

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
