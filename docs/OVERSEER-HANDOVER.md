# 🆗 Overseer Kit — overseer-kit

**Public product name:** 🆗 Overseer Kit — `overseer-kit` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit.** Paste the **Paste-ready prompt** fence into a fresh chat.

---

## NEXT SESSION — Track P / P-route Thinking freeze (▶ NEXT)

**Date:** 2026-07-12  
**Current position:** **Track P / P1 DONE** — build verified → `pass` (P1-BV-r2). Build-verification round 1 raised **BV1** (§P0.6 parity: `verify` did not emit exit `2` on a hash-consistent but structurally malformed `provenance`); fixed in `tools/honesty/ledger.py` `verify_chain` + CLI message + regression test; round 2 `pass`. **429** tests green (+30 §P0.8). Track P provenance primitive is now shipped and verified.  
**Model:** **thinking-high** (Thinking freeze — design + freeze the next contract before any Auto build)  
**Operator choice:** the default next slice below is **Track P / P-route** (declarative model-routing *policy*). Operator may instead pick **Track P / P-cost**, **Track P / P-evidence**, or **Track Q / Q0** (Overseer App freeze) — each is a Thinking freeze and each must clear the "governance, not runtime" boundary.

<!-- overseer:anchor:done-recently -->
### What just landed

| Slice | Deliverable |
| --- | --- |
| **Track P / P1 DONE (build-verified)** | `provenance` envelope on non-genesis ledger entries; `compute_entry_hash` excludes `provenance.sig` (legacy hashes unchanged); Ed25519 verify in `ledger verify` + `honesty-status`; `honesty.require_agent_signature` (git-only `true` → config exit `26`); append/verify exit `25`/`26`; Muse registry seam (`tools/honesty/muse_registry.py`); `cryptography` dep for verify-only path |
| **Build verification** | `/build-verification-review` V1–V8 vs frozen §P0. Round 1 → **BV1** (§P0.6: `verify` must emit `2` on malformed provenance) → fixed (`verify_chain` structural validation + CLI message + regression test). Round 2 → **`pass`** |
| **Tests** | Seven-tier §P0.8 matrix — **30** new tests; **429** total green |
| **Track P / P0 DONE** | Contract reviewed → `pass` (P0-r2); stamp `sha256:7db8681…` |
| **KH1b** | Substrate health + gate reminders live |
<!-- /overseer:anchor:done-recently -->

### THE ONE NEXT STEP — **Model: thinking-high (Thinking freeze: Track P / P-route)**

Draft and freeze the **Track P / P-route** contract (P0-style): a **declarative model-routing policy** in `policy/model-routing.yaml` mapping `position / phase-tier / gate → model tier + fallback`, consumed by the *runtime* (Cursor / OpenRouter / Scooling). The kit stays the rule-holder, never the executor — **no model calls added to the kit.** Freeze WHAT + HOW + the seven-tier test matrix before any Auto build. (Operator may instead pick P-cost, P-evidence, or Track Q / Q0.)

| | |
| --- | --- |
| **ID** | **Track P / P-route freeze** |
| **Branch** | `feat/track-p-route-freeze` (slug = `track-p-route-freeze`) |
| **Read first** | `docs/ROADMAP.md` (Track P / P-route row + Exploration backlog); `policy/model-labels.yaml`; `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md` (freeze-doc shape); `docs/OVERSEER-KIT-SPEC.md` §6 (freeze ceremony) |
| **Freeze** | Contract doc `docs/PHASE-TRACK-P-P-ROUTE-*.md`; extends (does not fork) `policy/model-labels.yaml`; seven-tier matrix; boundary = policy only, no dispatcher/model-host |
| **Hard stops** | No Auto build until freeze reviewed → `pass`; no model calls / runtime dispatch in the kit; no Tier-3 merge without authorization |

<!-- overseer:anchor:paste-ready-prompt -->
### Paste-ready prompt — Track P / P-route Thinking freeze

```
Phase Track P / P-route — Thinking freeze (overseer-kit).

Model: thinking-high (design + freeze the contract; NOT an Auto build session).

Shared context:
- Project: 🆗 Overseer Kit — repo-agnostic governance vendoring CLI
- Read first: docs/ROADMAP.md (Track P / P-route row + Exploration backlog);
  policy/model-labels.yaml; docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md (freeze-doc shape);
  docs/OVERSEER-KIT-SPEC.md §6 (freeze ceremony)
- Predecessor: Track P / P1 DONE (agent provenance shipped + build-verified, 429 tests green)
- Boundary (K7 / AGENTS.md): the kit is governance/frontend, NEVER a runtime/dispatcher/model-host

Task:
- Draft docs/PHASE-TRACK-P-P-ROUTE-*.md freezing a DECLARATIVE model-routing POLICY:
  policy/model-routing.yaml mapping position / phase-tier / gate -> model tier + fallback,
  consumed by the runtime (Cursor / OpenRouter / Scooling). Extend (do not fork) model-labels.yaml.
- Freeze WHAT + HOW + a seven-tier test matrix the Auto build must satisfy. NO model calls in the kit.
- Run /freeze-review-loop until `pass`; write the review stamp via `overseer review --freeze`.
- On pass: ROADMAP Track P / P-route -> (freeze DONE, queue P-route Auto build); update this handover.

Governance gates (mandatory — remind only; silence is not pass):
- Freeze review: this session freezes the contract; no Auto build until reviewed -> `pass`
- overseer status and overseer governance-sync emit pending gates for the active slice
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
| **K12 / Track N** | **DONE** — landing + scenario gallery + LICENSE + funnel |
| **KH1 Handover relay** | **DONE** — contract `pass` (KH1-r2); §KH1.6 close-out complete |
| **Track P / P0** | **DONE** — agent identity & signed provenance; contract reviewed → `pass` (P0-r2), stamp `sha256:7db8681…` |
| **Track P / P1** | **DONE** — agent provenance build-verified → `pass` (P1-BV-r2); BV1 (§P0.6 verify-surface parity) fixed; **429** tests green (+30 §P0.8) |
| **Track Q / Q0–Q2** | **TODO** — Overseer App: local web UI over the existing engine (Q1) packaged with **Tauri** into a cross-platform desktop app (Q2); needs Q0 Thinking freeze first; not yet started |
| **Muse dogfood** | **D2 repaired** + substrate health + gate reminders live; `muse rev-parse` reads plain-text SHA (0.2.x returns bare SHA on success; JSON only on failure/non-zero); `governance-sync --dry-run` exits 0; muse canonical HEAD `sha256:4671b7f…` |
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
| HEAD | `03ecf33` |
| Muse HEAD | `sha256:4671b7f…` (branch `main`, 316 files, first muse commit) |
| GitHub bridge | PR #15 — `muse-mirror → main` |
| Dirty | yes (adapter plain-text SHA fix + 6 test mocks + bridge sentinel) |
<!-- /overseer:anchor:vcs-table -->

## Hard stops (unchanged)

- No merge to `main` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)

<!-- overseer:anchor:change-log -->
## Change log

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
