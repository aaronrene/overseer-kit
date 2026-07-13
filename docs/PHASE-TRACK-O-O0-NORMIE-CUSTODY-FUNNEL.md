# Phase Track O / O0 — Freeze Normie custody funnel (Thinking freeze)

Status: **Reviewed → `pass` (O0-r3).** O0 Thinking is **spec-only** and now frozen; no product
UI, no account glue, and no live consumer `ok init` land in this phase. The Track O / O1 Auto
build (`{step}b`) is cleared to implement **product contracts only** as scoped below. Do **not**
re-derive this contract during the Auto build.

```yaml
phase: TRACK-O-O0
outputs:
- id: track-o-o0-normie-custody-funnel
  path: docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md
  frozen: true
frozen_inputs:
- id: kit-spec-regimes
  path: docs/OVERSEER-KIT-SPEC.md#4
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: k6-pilot-matrix
  path: docs/PHASE-K6-PILOT-INSTALL-MATRIX.md
- id: k7-dogfood-guardrail
  path: docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
- id: k6-scooling-runbook
  path: docs/consumers/scooling/OVERSEER-SETUP.md
- id: consumer-adapter-pattern
  path: docs/CONSUMER-ADAPTER-PATTERN.md
- id: track-q-desktop-runbook
  path: docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: roadmap-track-o-rows
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T19:44:54Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:642076c9a7dc341cc69f5d214342c4d65233c0c6c61a300d7825b1d3e9337961
```

**Downstream edge:** the Track O / O1 Normie custody product-contracts Auto build treats this
document as ground truth without re-deriving it (SPEC §6 mandatory reviewed freeze). Later
product UX in Scooling or Knowtation may implement wizards against this contract, but those
product repos are **not** cleared to invent kit regimes, CLI semantics, or MuseHub-only baseline
features from this freeze. Track Q desktop remains an operator UI surface; it does not reopen
this onboarding scope.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| O0-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist clean (0 findings). Semantic review raised non-escalating findings below. No `security`/`irreversible`/`real_money`/`gates_tier3` escalation. |
| O0-r1 fix | Author (cited items only) | — | **R1-M1** fixed: §O0.3.3 freezes Stage 3 kit upgrade ceremony as **out of O0/O1** (no silent `vcs.regime` edit; no new CLI). **R1-M2** fixed: §O0.8 docs-only stress/performance paths made mandatory and concrete. **R1-M3** fixed: O1 Knowtation consumer stub path frozen. **R1-N1** fixed: product-contract path exact. **R1-N2** fixed: exploration-backlog close-out wording exact. |
| O0-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Residual consistency: §O0.3.1 / §O0.5 / §O0.0 still implied product Stage 3 one-click before O2. No escalation. |
| O0-r2 fix | Author (cited items only) | — | **R2-M1** fixed: §O0.3.1 who-column aligned to operator-today / product-after-O2. **R2-M2** fixed: §O0.5 backup-button wraps gated on O2. **R2-N1** fixed: §O0.0 summary notes O2-deferred backup ceremony. |
| O0-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings). Semantic re-read confirmed R1/R2 items RESOLVED: Track O identity vs K6/Q; Stages 1–4 with §O0.3.3 deferred Stage 3 ceremony; custody identity; boundary + rejection tables; O1 product-contracts-only deliverables with exact paths; seven-tier §O0.8 complete; K7 MuseHub-optional guardrail held; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §O0.0 — Simple summary

People who are not developers still want ownership of what they produce with AI: notes, plans,
decisions, and memory that follow *them* across chatbots. Overseer Kit already provides regimes,
living docs, and the `ok` CLI. What they need next is a **clear product path**: create a personal
space (Muse-first preferred, no Git required to start), optionally add GitHub backup later (kit
upgrade ceremony deferred to O2), and optionally bind a Knowtation vault — without teaching bare
`git` or bridge scripts.

**Technical summary:** freeze Track O as an onboarding **contract** that composes the existing
three regimes (`muse-only`, `git-only`, `muse+git-mirror`) with consumer product UX. The kit
remains **rule-holder + CLI**; products own signup wizards that call `ok init`, governance-sync,
and (later) mirror under the hood. Baseline governance stays fully usable without Muse, without
Scooling, and without Knowtation.

---

## §O0.1 — Scope

**In scope (freeze only — this phase writes no code):**

- Track O identity vs K6 consumer pilots vs Track Q desktop (§O0.2).
- Normie path stages and allowed regime transitions (§O0.3), including deferred Stage 3 ceremony
  (§O0.3.3).
- Custody-identity definition (§O0.4).
- Boundary table: kit vs Scooling vs Knowtation vs MuseHub (§O0.5).
- Explicit non-requirements / rejection table (§O0.6).
- O1 Auto deliverable list — **product contracts only** (§O0.7).
- Seven-tier matrix O1 must satisfy (§O0.8).
- Hard stops + tier linkage (§O0.9).
- Close-out rules after freeze `pass` (§O0.10).

**Out of scope (explicit non-goals — prevent creep):**

- **Any signup UI, account creation, OAuth, or marketplace plugin** in overseer-kit.
- **Live consumer `ok init`** on Scooling, Knowtation, or any named production tree (operator-gated;
  unchanged from K6).
- **New VCS regimes** beyond the frozen three in SPEC §4.
- **New core CLI subcommands** in O0 or O1 (products wrap existing `ok` surfaces).
- **Engine rewrite** of adapters, footprint, honesty, or Track Q app server.
- **Making Scooling, Knowtation, MuseHub, Cursor, or Track Q desktop mandatory** to use the kit.
- **MuseHub-only baseline features** (K7 frozen guardrail).
- **Tier-3 merge, staging push, or live capability flips** — this freeze never authorizes them.
- **Storing vault bytes, Knowtation credentials, or GitHub tokens inside the kit.**

---

## §O0.2 — Track identity (frozen)

| Track | Audience | What it freezes / ships | Not this track |
| --- | --- | --- | --- |
| **K6** | Operators installing the kit into **existing** consumer repos | Pilot install matrix, fixtures, operator runbooks | Normie first-run UX |
| **Track Q** | Operators who already have a local governed tree | Local `ok app` + Tauri shell over the engine | Signup / vault onboarding |
| **Track O** | Non-developers ("normies") and product teams wrapping the kit | Onboarding **contract**: Muse-first start → optional GitHub backup (ceremony deferred O2) → optional Knowtation bind | Product runtime, vault store, social network |

**Frozen one-liner:** Track O is the **custody onboarding contract** for personal AI work; it is
not a fourth VCS regime, not a vault, and not a Scooling dependency.

---

## §O0.3 — Normie stages (frozen)

```text
Stage 1 — Start
  Preferred: create personal space under muse-only (no Git required).
  Also fully supported: git-only (K7 baseline — no Muse required).
  Product may wrap: ok init (+ regime selection) for a new or empty tree.

Stage 2 — Work
  Living docs (ROADMAP + HANDOVER) + paste-ready prompts into any chatbot.
  Product may hide ok governance-sync / status behind UX; kit CLI remains authority.
  Cursor rules/skills are optional boosters, never required.

Stage 3 — Optional GitHub backup
  Allowed transition: muse-only → muse+git-mirror (existing adapters + SD-14 bridge).
  Kit automated upgrade ceremony: deferred (§O0.3.3); products must not ship one-click yet.
  Never required to start; never invent a push-to-main shortcut.

Stage 4 — Optional Knowtation bind
  Bind a Knowtation vault root to the same custody identity (§O0.4).
  Knowtation owns vault bytes + bind UX; kit does not become the vault.
```

### §O0.3.1 — Allowed regime transitions (frozen)

| From | To | Who may perform | Rule |
| --- | --- | --- | --- |
| *(none)* | `muse-only` | Product wizard or operator `ok init` | Preferred Stage 1 start |
| *(none)* | `git-only` | Product wizard or operator `ok init` | Full baseline; no Muse |
| *(none)* | `muse+git-mirror` | Product wizard or operator `ok init` | Allowed when both substrates are ready at start (K6 Scooling shape) |
| `muse-only` | `muse+git-mirror` | Operator today; product UX only after O2 ceremony freeze (§O0.3.3) | Stage 3 **allowed transition**; must use existing bridge contract (isolated mirror → `muse-mirror` PR); never `git push` canonical `main`; silent config edit forbidden |
| `git-only` | `muse+git-mirror` | Operator / later product | Allowed only with explicit Muse substrate init; not required for normie Stage 1 |
| Any | Any other pair | — | **Forbidden in O1** without a later Thinking freeze |

Products **must not** invent a fourth regime string or a silent dual-write outside the adapter
interface.

### §O0.3.2 — Dev / operator path (informative, not replaced)

Terminal + `cli/ok` + K6/K7 runbooks remain the operator path. Normie stages use the **same**
adapters and commands behind a simpler product shell. Track Q may later surface Stage 2 status for
operators; it does not replace Stage 1–4 product ownership.

### §O0.3.3 — Stage 3 kit upgrade ceremony (frozen — deferred)

§O0.3.1 **declares** that `muse-only` → `muse+git-mirror` is an allowed transition. It does **not**
authorize O1 (or any product) to invent the kit mechanism.

| Rule | Requirement |
| --- | --- |
| Silent config edit | **Forbidden.** Editing only `vcs.regime` in `.overseer/config.yaml` without a footprint re-resolve leaves a muse-only tree missing K7 bridge destinations — that is the exact class of drift KH3/K7 exist to prevent. |
| New CLI / adapter for upgrade | **Forbidden in O0 and O1.** No `ok upgrade-regime`, no adapter rewrite. |
| O1 scope | Documents the **allowed transition** and the rejection of silent edits; does **not** ship an automated upgrade wizard or kit ceremony. |
| Product Stage 3 UX | **Contract-blocked from shipping** until a later Thinking freeze (suggested **O2**) defines the kit upgrade ceremony (footprint re-seed, `--migrate`/`--force` interaction, bridge dry-run gates). Until then, products may only **describe** Stage 3 as coming soon / operator-assisted. |
| Operator today | May still use existing K6/K7 operator runbooks on a feature branch with explicit consent — that is operator dogfood, not Track O Auto scope. |

---

## §O0.4 — Custody identity (frozen)

**Custody identity** for Track O means the durable association of:

1. One repo working tree (personal space),
2. That tree's `.overseer/config.yaml` (regime + doc paths),
3. The VCS history selected by the regime (Muse and/or Git),
4. Optionally, a Knowtation vault root bound by the **product** to that same tree.

| Fact | Rule |
| --- | --- |
| Kit stores | Config, footprint, living-doc paths, adapter state — never vault blobs |
| Knowtation stores | Vault markdown/media under its own data roots |
| Scooling stores | Product accounts / runtime — never required for kit custody |
| Shared "same person" claim | Product-owned bind metadata; kit does not mint a global user id |

O1 must not invent a kit-side identity registry, SSO, or cross-product account table.

---

## §O0.5 — Boundary table (frozen)

| Concern | Overseer Kit | Scooling | Knowtation | MuseHub |
| --- | --- | --- | --- | --- |
| `ok init` / regimes / adapters | **Owns** | Consumes | Consumes | `muse-only` dogfood substrate |
| Normie signup / Stage 1–4 wizard | Declares **contract only** | May host entry UX (optional) | Vault bind UX (optional) | Substrate only |
| Personal vault bytes | **Never** | **Never** | **Owns** vault store | History substrate |
| GitHub create-repo / backup button | No UI; ships bridge scripts + regimes | Wrap **only after O2** ceremony freeze (§O0.3.3) | Wrap **only after O2** (§O0.3.3) | N/A |
| Operator bridge (SD-14) | Ships K7 scripts + dogfood docs | May wrap later | May wrap later | — |
| Multi-agent runtime (`src/phase9a/`) | Reference only (`AGENTS.md`) | **Owns** product runtime | — | — |
| Local governance UI | Track Q `ok app` / Tauri (operator) | May point at consumer tree | May point at consumer tree | — |

**Frozen guardrail (K7):** no core governance feature may be MuseHub-only. Every baseline capability
(`init` / `sync` / `status`, drift, footprint, templates, policy, freeze review, governance-sync)
remains fully functional on `git-only`.

**Frozen product rule:** a Scooling account is **not** required to use Overseer Kit. Scooling is an
optional entry product, not a kit dependency.

---

## §O0.6 — Rejection table (frozen)

| Proposal | Verdict |
| --- | --- |
| Require Scooling signup before `ok init` | **Reject** |
| Require Knowtation vault before governance works | **Reject** |
| Require MuseHub for baseline `ok status` / freeze review | **Reject** (K7) |
| Require Cursor IDE for Stage 2 work | **Reject** |
| Require Track Q desktop for Stage 1 | **Reject** |
| Add a fourth VCS regime for "normie mode" | **Reject** |
| Kit hosts vault bytes or Knowtation credentials | **Reject** |
| Product pushes directly to GitHub `main` bypassing `muse-mirror` | **Reject** (SD-14) |
| O1 ships signup UI inside overseer-kit | **Reject** |
| O1 performs live Scooling/Knowtation `ok init` | **Reject** (operator-gated) |
| Silent `vcs.regime` edit for Stage 3 without footprint re-seed | **Reject** (§O0.3.3) |
| Product ships Stage 3 one-click backup before O2 kit ceremony freeze | **Reject** (§O0.3.3) |

---

## §O0.7 — O1 Auto deliverables (product contracts only)

After this freeze is stamped `pass`, **Track O / O1** may ship **only** the following kit-side
artifacts:

1. **Normative product contract document** at the exact path
   `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md` that restates Stages 1–4, §O0.3.3 deferred
   Stage 3 ceremony, the boundary table, and the rejection table for product implementers — no
   redesign of §O0.3–§O0.6.
2. **Consumer cross-links:**
   - Update `docs/consumers/scooling/OVERSEER-SETUP.md` to point at Track O stages as the normie
     path (keeping live init operator-gated).
   - Create `docs/consumers/knowtation/OVERSEER-SETUP.md` as a **kit-side stub** (regime note +
     Track O Stage 4 pointer + hard stop: no live Knowtation `ok init` in O1). Full Knowtation
     pilot parity remains a later operator/K6-style phase.
3. **Docs integrity harness** under `tests/` (required). An **optional** thin validator under
   `tools/` may factor the same checks, but the harness alone is sufficient for O1.
4. **Seven-tier tests** for the harness (and validator if shipped) per §O0.8.
5. **ROADMAP + HANDOVER** sync marking O1 DONE only after `/build-verification-review` → `pass`.

**O1 must not ship:** signup UI, account APIs, OAuth, marketplace plugins, new CLI subcommands,
regime adapter changes, Stage 3 automated upgrade ceremony, live consumer installs, or vault
storage.

If a later phase needs product UI inside a **consumer** repo, that work lives in the consumer and
consumes this contract — it is not O1 kit scope.

---

## §O0.8 — Seven-tier test matrix (O1 Auto build must satisfy)

The O1 Auto build ships all seven tiers green locally before DONE (`policy/test-tiers.yaml`).
Skipping a tier is **forbidden**. The **docs integrity harness** under `tests/` is the mandatory
surface; a `tools/` validator is optional and, if present, must be covered by the same tiers.

| Tier | Proves |
| --- | --- |
| **unit** | Product-contract doc parse/presence helpers: required stage labels (Start / Work / GitHub backup / Knowtation bind); §O0.3.3 deferred-ceremony keywords present; rejection keywords present; no absolute machine paths; no secret-assignment patterns in the contract pack. |
| **integration** | Harness composes with fixture contract docs: valid fixture → ok; missing Stage 3/4 heading → fail-closed; mutated boundary table missing kit-owns language → fail-closed; fixture that claims Stage 3 one-click is shipped without O2 → fail-closed. |
| **e2e** | Real paths resolve: `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`, `docs/consumers/scooling/OVERSEER-SETUP.md`, `docs/consumers/knowtation/OVERSEER-SETUP.md`; Scooling + Knowtation stubs still state live init is operator-gated; Track O stages do not claim Scooling is mandatory; Stage 3 shipping remains deferred per §O0.3.3. |
| **stress** | Harness runs against a large duplicated-heading fixture (and, separately, against the real contract doc repeated N≥20 times in one test) without unbounded memory growth or hang; bounded runtime asserted in the test. |
| **data-integrity** | Harness is idempotent (same input twice → same verdict); contract doc bytes are not rewritten by the harness/validator; no partial write on induced failure. |
| **performance** | Single harness pass over the real contract pack completes within a bounded time documented in the test; no unbounded filesystem walk outside the declared paths. |
| **security** | No credentials, tokens, or vault paths with secrets in contract docs; no network calls on the harness/validator path; fail-closed on path-escape outside the repo root; K7 "no MuseHub-only baseline" statement remains in the contract pack; silent-regime-edit rejection text remains present. |

---

## §O0.9 — Hard stops + tier linkage (frozen)

| Action | Tier | O0/O1 rule |
| --- | --- | --- |
| Feature-branch commits for this freeze / O1 docs | Tier 1 | Allowed |
| `git push` feature branch / open PR | Tier 1 / SD-17 | Allowed |
| Merge to `main` | Tier 3 | **Stop** — never part of freeze loop |
| Live consumer `ok init` | Operator / Tier 3 against consumer | **Stop** |
| `muse push` staging / live gate flip | Tier 3 | **Stop** |
| Regime persistence shape changes beyond §O0.3.1 | Tier 2 | Confirm once + ADR; not O1 default |
| Real payments / account billing | Tier 3 + `real_money` | **Out of kit** |

This freeze does **not** gate merge, staging, or live flips by itself. Consuming this artifact for a
Tier-3 action still requires separate operator authorization (SPEC §6.4).

---

## §O0.10 — Definition of Done (Thinking) + close-out

**O0 Thinking DoD:**

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [x] `frozen: true` + non-empty `review_stamp` filled by the CLI
- [x] ROADMAP Track O / O0 → **DONE (Thinking)**; Track O / O1 Auto row queued against this contract
- [x] Handover NEXT flips to O1 with valid `Model: Auto` + paste-ready fence (KH1 H7/H8)
- [x] No product UI code landed in the Thinking phase
- [x] No Tier-3 merge performed as part of freeze

**Close-out sequence (execute only when O0 freeze marked DONE):**

1. Freeze-review `pass` recorded in the Review record table; stamp written by `ok review --freeze`.
2. ROADMAP: Track O / O0 → DONE; add **Track O / O1** (Auto, TODO) product-contracts build.
3. Exploration backlog row **Track O / O-onboard**: replace Sketch/Boundary with
   `Promoted → Track O / O0 (freeze) + O1 (Auto product contracts); Stage 3 ceremony deferred to later Thinking (O2)`.
4. Handover NEXT → Track O / O1 Auto with paste-ready prompt.
5. Governance sync: `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17).

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §4 regimes, §5 CLI, §6 freeze ceremony, §8 migration
- `docs/PHASE-K6-PILOT-INSTALL-MATRIX.md` — operator (dev) install path
- `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` — MuseHub-optional guardrail + bridge
- `docs/K6-PILOT-OPERATOR-RUNBOOK.md` — operator day-to-day
- `docs/consumers/scooling/OVERSEER-SETUP.md` — first consumer; points normies to Track O
- `docs/CONSUMER-ADAPTER-PATTERN.md` — kit vs consumer ownership
- `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` — operator UI surfaces (not Stage 1 signup)
- `docs/ROADMAP.md` — Track O / O0 row + exploration backlog
- `policy/test-tiers.yaml` — seven-tier requirement
- `policy/tiers.yaml` — Tier 1/2/3 authority
