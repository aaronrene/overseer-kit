# Phase Track P / P-cost — Cost-awareness surface (Thinking freeze)

Status: **Reviewed → `pass` (P-cost-r2).** P-cost Thinking is **spec-only** and now frozen; no code,
no policy edit, and no `policy/model-labels.yaml` change land in this phase. The P-cost Auto build
(`{step}b`) is cleared to start mechanically against this frozen contract; it is the only phase that
writes files. Do **not** re-derive this contract during the Auto build.

```yaml
phase: TRACK-P-P-COST
outputs:
- id: track-p-p-cost-awareness
  path: docs/PHASE-TRACK-P-P-COST-AWARENESS.md
  frozen: true
frozen_inputs:
- id: model-labels
  path: policy/model-labels.yaml
- id: model-routing-policy
  path: policy/model-routing.yaml
- id: p-route-contract
  path: docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: layered-honesty-vision-spend
  path: docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md#12-insight-videofactory-2026-07
- id: gate-reminder-surface
  path: tools/governance_gates
- id: roadmap-p-cost-row
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T09:12:10Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:9f266786ec4bca71855c0b9dbdaa753cc0b97c468bcf36443e153f5163bf2a83
```

**Downstream edge:** the P-cost Auto build (`{step}b`) treats this document as ground truth without
re-deriving it (SPEC §6 mandatory reviewed freeze). Consumer runtimes (Cursor, OpenRouter, Scooling
9A) read the frozen cost-awareness shape as ground truth for what a *spend posture* looks like — but
the runtime, never the kit, converts a cost band into an actual price, budget, or spend decision.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| P-cost-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist gate clean (0 findings). Semantic review raised one non-escalating MAJOR internal-consistency finding — **R1-M1** (§PC.7 exit-code table + bullet described a malformed-cost-metadata fault as both exit `32` and the existing `2` fail-closed tier on `overseer status`, contradicting the frozen `model_routing: invalid` warning-only precedent in `cli/commands/status.py`). Fixed minimally: exit `32` confined to `overseer route`; `status` / `governance-sync` degrade to a read-only `cost_awareness: invalid` warning with no exit-code change. No `security`/`irreversible`/`real_money`/`gates_tier3` escalation. |
| P-cost-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings). Semantic re-read confirmed R1-M1 RESOLVED; exit `32` non-overlapping with `1`,`2`,`4`,`5`,`7`,`8`,`10`–`11`,`20`–`26`,`30`–`31`; boundary held (kit declares bands + derives the paid flag; runtime converts to dollars and decides spend — no price, currency, budget, network, or model call in the kit); `real_money` explicitly checked and does **not** apply (the kit never spends; §PC.1 + §PC.8); seven-tier matrix complete; reminder-only posture consistent across §PC.1 / §PC.7 / §PC.8. Stamp written by `overseer review --freeze`. |

---

## §PC.0 — Simple summary

Some governance steps quietly cost money. Freezing a contract or ruling on a dispute routes to a
strong, expensive reasoning model; a quick build step routes to a cheap one; an offline step costs
nothing metered. Today the operator only learns a step was "paid" **after** the spend already
happened. The VideoFactory lesson (vision §1.2) is blunt: by the time anyone checks, the money may
already be burned — so the warning has to arrive **before** the spend, not after.

**Track P / P-cost adds a cost-*awareness* surface, not a dollar pricer.** It labels each abstract
model tier with a relative, currency-free **cost band** (`free`, `low`, `moderate`, `high`) and
surfaces, for the work that is about to happen, a single honest flag: **"paid step before spend."**
That flag says *this next governance step will engage a metered model tier* so a human or runtime can
decide **before** committing the spend. The Overseer Kit never names a dollar amount, never reads a
provider price list, never sets a budget, and never blocks on spend it cannot measure — the runtime
that knows its own provider prices does all of that. The kit only makes the *paid-ness* of the next
step visible in advance.

**Technical summary:** extend each `model_tiers[]` entry in `policy/model-labels.yaml` with an
optional, ordinal, price-free `cost_class` (`free < low < moderate < high`); derive a boolean
`paid_step_before_spend` per resolved tier (`free` and the reserved `human` terminal are unpaid; any
other band — and, conservatively, an absent band — is paid). Annotate the existing read-only
`overseer route` decision output with `cost_class` + `paid_step_before_spend` (additive, no behavior
change to resolution). Add an optional, default-inert `cost_awareness:` config block and a read-only
**spend-awareness surface** that, for the active handover/roadmap slice, reports the resolved tier's
cost band and paid flag on `overseer status` and in the `overseer governance-sync` footer (the
handover-facing surface). The kit performs no model call, holds no key, opens no network connection,
names no currency, and computes no dollar total — it is the cost-awareness *rule-holder*, never the
spender.

---

## §PC.1 — Scope

**In scope (freeze only — this phase writes no code):**

- The optional `cost_class` extension to each `model_tiers[]` entry in `policy/model-labels.yaml`,
  its frozen ordinal vocabulary, and its validation rules (§PC.3).
- The deterministic `paid_step_before_spend` derivation from a resolved `model_tier` (§PC.4).
- The additive `cost_class` + `paid_step_before_spend` annotation on the `overseer route` decision
  output (§PC.5).
- The optional `cost_awareness:` config block and its regime interaction (§PC.6).
- The read-only active-slice spend-awareness surface on `overseer status` and the
  `overseer governance-sync` footer, plus the new exit code (§PC.7).
- The boundary + capability table that keeps the kit a cost-awareness rule-holder, not a spender
  (§PC.8).
- The seven-tier test matrix the P-cost Auto build must satisfy (§PC.9).
- The informative shared-contract note for consumer runtimes (§PC.10).

**Out of scope (explicit non-goals — prevent creep):**

- **Any dollar amount, currency, price, price list, or provider rate card in the kit.** `cost_class`
  is a relative ordinal band, never a number and never a currency. Mapping a band to a real price is
  the runtime's job.
- **Any budget, spend cap, quota, or accumulated-spend total.** The kit tracks no running cost, sets
  no ceiling, and stores no spend history. It cannot measure spend, so it never claims to.
- **Any hard block, gate failure, or refusal based on cost.** The spend-awareness surface is a
  **reminder only** (the same posture as the §KH1.9 governance-gate reminders: "silence is not
  pass"). It never fails a build, never blocks a merge, and never changes an exit code on the basis
  of a step merely being paid. The only fail-closed path is malformed cost metadata (§PC.7), which is
  a data-integrity fault, not a spend decision.
- **Any model call, network connection, dispatch, or provider price lookup.** Identical to the
  P-route boundary — the kit resolves and annotates data; it never contacts a provider.
- **Changing P-route resolution.** The routing algorithm, `model-routing.yaml` schema, `model_tiers`
  ids, and exit codes `30`/`31` from `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` are frozen and
  untouched. P-cost only *reads* the resolved tier and *annotates* it.
- **Verification-evidence capture (P-evidence).** A separate slice; not touched here.
- **Making cost-awareness mandatory.** `cost_awareness.enabled` defaults `false`; a repo that never
  opts in is byte-for-byte unaffected. Cost-awareness is a `git-only` baseline capability with no
  Muse dependency (K7 guardrail: no baseline feature may be substrate-gated).

---

## §PC.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Abstract model tiers | `model_tiers[]` = `deep-reasoning`, `standard`, `fast`, `local-offline`; each an `id` + `display` + `meaning` + advisory `cursor_model_hint`; no vendor slugs | `policy/model-labels.yaml` |
| Model-tier entry keys | Strict key set `{id, display, meaning, cursor_model_hint}`; unknown keys fail closed | `tools/model_routing/labels.py` |
| Reserved terminal | `human` is a reserved fallback terminal tier id, never declared in `model_tiers` | `tools/model_routing/labels.py` |
| Routing policy | `policy/model-routing.yaml` maps `{position, phase_tier, gate}` → `model_tier` + ordered `fallback`; first-match-wins + mandatory `defaults` | `policy/model-routing.yaml` |
| Routing resolution | Pure, deterministic `resolve_route(policy, query)` → `RouteDecision(route_id, model_tier, fallback)` | `tools/model_routing/resolve.py` |
| `overseer route` | Read-only resolve / `--validate`; JSON emits `route_id`, `model_tier`, `fallback`, `query`, `policy`; exit `30`/`31` | `cli/commands/route.py` |
| `model_routing:` config | Optional, default `enabled: false`, `policy: policy/model-routing.yaml`; path-confined | `adapters/config.py` |
| Status routing line | When `model_routing.enabled: true`, `overseer status` adds a read-only routing-validity line + `model_routing` JSON key | `cli/commands/status.py` |
| Gate-reminder surface | `tools/governance_gates/` scans the active slice; read-only "reminders only" lines on `overseer status` + the `governance-sync` footer; JSON payload | `tools/governance_gates/`, `cli/commands/status.py`, `tools/governance_hygiene/engine.py` |
| Active-slice scan | `scan_governance_gates` already computes `active_phases` from the handover NEXT id + roadmap `WIP/TODO/BLOCKED` rows | `tools/governance_gates/scan.py` |
| Fail-closed reviewer analogy | `fallback: human` — unreachable provider falls back to a human, never a fake pass | `docs/OVERSEER-KIT-SPEC.md#6` |
| Seven-tier contract | Every code-adding build phase ships all seven tiers before DONE | `policy/test-tiers.yaml` |
| Boundary | The kit is repo-agnostic governance/frontend, **never** a runtime, dispatcher, model-host, or spender; Scooling 9A router is reference-only | `AGENTS.md` |

P-cost **must not** change existing `model_tiers` ids, the routing schema/algorithm, existing config
blocks, existing status output when its features are disabled, or any existing exit code. It only
**adds** an optional `cost_class` key, additive `route` output fields, an optional `cost_awareness:`
config block, an active-slice spend-awareness surface, and one new non-overlapping exit code.

---

## §PC.3 — `cost_class` extension for `model_tiers` (frozen schema)

The Auto build adds one **optional** key, `cost_class`, to each `model_tiers[]` entry in the existing
`policy/model-labels.yaml`. Existing `labels`, `reviewer_models`, and every current `model_tiers`
field are untouched. `cost_class` is a **relative, currency-free ordinal band** — never a price.

```yaml
model_tiers:
  - id: deep-reasoning
    display: Deep reasoning
    meaning: >
      Extended-thinking / frontier-class reasoning for contract freezes, disputes,
      overseer rulings, and security-sensitive review.
    cursor_model_hint: extended thinking / Opus-class     # HINT ONLY, non-binding
    cost_class: high            # relative ordinal band — NOT a price, NOT a currency
  - id: standard
    display: Standard
    meaning: >
      Balanced capability for mechanical builds against a frozen spec and routine
      verification steps.
    cursor_model_hint: default / Composer / Sonnet-class
    cost_class: moderate
  - id: fast
    display: Fast
    meaning: >
      Low-latency, low-cost tier for trivial or high-volume low-stakes steps.
    cursor_model_hint: fast / mini-class
    cost_class: low
  - id: local-offline
    display: Local (offline)
    meaning: >
      Locally hosted model for offline or privacy-first runtimes; preserves the
      kit's offline promise. The kit still performs no call — the runtime does.
    cursor_model_hint: local / on-device
    cost_class: free            # no metered provider spend
```

Rules (frozen):

1. `cost_class` is **optional**. When present it MUST be one of the frozen ordinal vocabulary values,
   lowercase, from the closed set: `free`, `low`, `moderate`, `high`. Any other value (or a
   non-string) is malformed cost metadata and fails closed (exit `32`, §PC.7).
2. The vocabulary is **ordinal**: `free (0) < low (1) < moderate (2) < high (3)`. The order encodes
   *relative spend intent set by policy* — it is explicitly **not** a claim about, guarantee of, or
   proxy for any actual dollar figure. A consumer whose real prices order differently overrides the
   policy in its own repo.
3. `cost_class` MUST NOT contain a vendor slug, endpoint, price, currency symbol, or numeric amount.
   The value set is closed to the four ordinal words above, so this is enforced by the closed
   vocabulary; the Auto build also adds `cost_class` to the strict `model_tiers` entry key set so the
   key itself is recognized rather than rejected as unknown.
4. The reserved `human` terminal tier (§PC.2) is **not** declared in `model_tiers` and therefore
   carries no `cost_class`; for cost purposes it is treated as unpaid (`free`) — a human fallback is a
   person's judgment, not a metered model step.
5. The four vendored defaults above are the kit's shipped bands; they are **overridable per repo**
   exactly like every other vendored policy value. The kit asserts only the *relative ordering
   intent* of its own four tiers, not any repo's real prices.

---

## §PC.4 — `paid_step_before_spend` derivation (frozen, deterministic)

Given a resolved `model_tier` (from an `overseer route` decision or the active-slice resolution of
§PC.7) and the `model_tiers` cost bands, the paid flag is a pure function:

1. If `model_tier` is the reserved `human` terminal → `cost_class = free`, `paid_step_before_spend =
   false`.
2. Else look up the tier's `cost_class` in `model_tiers`:
   - `free` → `paid_step_before_spend = false`.
   - `low` | `moderate` | `high` → `paid_step_before_spend = true`.
   - **absent / not declared** → `cost_class = unknown`, `paid_step_before_spend = true`
     (**conservative fail-safe**: an undeclared band is assumed to be a metered step, so the operator
     is warned rather than lulled — this mirrors the fail-closed-before-spend posture of vision
     §1.2).
3. The derivation is **pure and deterministic**: identical tier + identical `model_tiers` always
   yields the identical `(cost_class, paid_step_before_spend)` pair, with no I/O, no network, and no
   randomness.

`unknown` is a **surfaced-only** state (it appears in output to signal a caution), never a valid
*declared* `cost_class` value — declaring `cost_class: unknown` in policy is malformed (§PC.3 rule 1,
exit `32`).

---

## §PC.5 — `overseer route` cost annotation (frozen, additive)

The Auto build annotates the existing read-only `overseer route` decision output with two additive
fields. **Routing resolution itself is unchanged** — the matched `route_id`, `model_tier`, and
`fallback` are byte-for-byte what P-route already produces; P-cost only appends the cost view of the
already-resolved tier.

`overseer route --json` gains (additive keys; existing keys unchanged):

```json
{
  "route_id": "auto-build",
  "model_tier": "standard",
  "fallback": ["standard", "human"],
  "query": { "position": null, "phase_tier": "auto", "gate": null },
  "policy": "policy/model-routing.yaml",
  "cost_class": "moderate",
  "paid_step_before_spend": true
}
```

- The human (non-JSON) `overseer route` output gains one line: `cost_class: <band>` and
  `paid_step_before_spend: <true|false>` (or `cost_class: unknown` when the resolved tier declares no
  band).
- The annotation reads `cost_class` for the **resolved** `model_tier` only; the `fallback` chain is
  not annotated per-entry (the runtime, which walks the chain, resolves each tier's cost itself).
- If cost metadata is malformed (§PC.3), `overseer route` fails closed with exit `32` and a cited
  violation — because the `model_tiers` file it must read is invalid. The routing decision is not
  emitted in that case (a malformed shared label file is a hard data fault, identical in spirit to a
  vendor slug already breaking every `model_tiers` reader today).

---

## §PC.6 — Config block & regime interaction (frozen)

Add an optional, additive `cost_awareness:` block to `.overseer/config.yaml` (default preserves
current behavior — cost-awareness is off and inert):

```yaml
cost_awareness:
  enabled: false                       # default false — inert; opt-in
  surfaces: [status, governance-sync]   # optional; default both
```

| Field | Default | Meaning |
| --- | --- | --- |
| `enabled` | `false` | When `false`, no spend-awareness surface is emitted and `overseer status` / `governance-sync` are unchanged. `overseer route` still annotates cost on explicit request (informational; annotation is not gated on `enabled`). When `true`, the active-slice spend-awareness surface (§PC.7) is emitted on the configured surfaces. |
| `surfaces` | `[status, governance-sync]` | Optional non-empty list; closed vocabulary `status`, `governance-sync`. Selects which read-only surfaces emit the spend-awareness lines. Unknown surface value fails closed (config parse, exit `2`), consistent with `governance_gates.surfaces`. |

- Cost-awareness resolves the active slice's tier by reading the routing policy at
  `model_routing.policy` (the same confined path `overseer route` uses). It does **not** require
  `model_routing.enabled: true` — reading the rulebook to compute a *tier* is independent of a repo
  opting routing on. If the policy file is missing/unreadable while `cost_awareness.enabled: true`,
  the surface fails closed with exit `31` (reusing the P-route missing-policy code), never silently
  showing "free."
- The handover is covered through the `governance-sync` surface: the `governance-sync` footer is the
  handover-regeneration surface, so emitting the spend-awareness lines there is how the posture
  reaches the handover NEXT block. The Auto build additionally adds a static one-line "Spend
  awareness" reminder to `templates/OVERSEER-HANDOVER.template.md` so a freshly generated handover
  names the posture by convention. No new fail-able handover gate is introduced.

Regime interaction: cost-awareness is **regime-agnostic** and a `git-only` baseline capability.
Behavior is byte-identical across `git-only`, `muse+git-mirror`, and `muse-only` — there is no Muse
dependency and no substrate gate (K7 guardrail). Enabling cost-awareness **never** causes a model
call, a network connection, or a price lookup under any regime.

---

## §PC.7 — Spend-awareness surface & exit code (frozen)

When `cost_awareness.enabled: true`, the Auto build adds a **read-only** active-slice spend-awareness
surface. It performs no model call, opens no network connection, computes no dollar total, and
**never blocks** on the basis of a step being paid.

**Resolution of the active slice (frozen):**

1. Reuse the existing `scan_governance_gates` active-slice detection (`active_phases`, and any pending
   gate for a phase) — no new scanner. For each active phase the surface builds a routing query:
   - `phase_tier` — derived from that slice's `Model:` label by normalizing to a `labels[]` id
     (`Thinking → thinking`, `Auto → auto`); a label that does not normalize to a known `labels[]`
     id yields `phase_tier = None` (wildcard).
   - `gate` — derived from the phase's pending governance gate when one is detected: a pending
     `freeze_review` gate → `gate = freeze_review`; a pending `build_verification` gate → `gate =
     build_verification`; otherwise `gate = None`. (`handover_paste` gates have no routing gate → 
     `None`.)
   - `position` — always `None` at this surface. The kit does not know the org-chart *position* of a
     governance phase; a runtime that does gets a more precise decision via `overseer route`. This
     coarseness is deliberate and documented, not a defect.
2. Resolve each query with the frozen P-route `resolve_route` (first-match-wins + mandatory
   `defaults`), then derive `(cost_class, paid_step_before_spend)` per §PC.4.

**Emitted output (read-only, reminder posture):**

- `overseer status` (human): a spend-awareness section, one line per active slice, for example
  `cost_awareness: Track P / P-cost [thinking] → deep-reasoning (high) — paid step before spend`.
  When no active slice is paid: `cost_awareness: no paid step in active slice`.
- `overseer status --json`: an additive `cost_awareness` key:

```json
{
  "cost_awareness": {
    "enabled": true,
    "policy": "policy/model-routing.yaml",
    "slices": [
      {
        "phase_id": "Track P / P-cost",
        "phase_tier": "thinking",
        "gate": "freeze_review",
        "route_id": "freeze-thinking",
        "model_tier": "deep-reasoning",
        "cost_class": "high",
        "paid_step_before_spend": true
      }
    ]
  }
}
```

  When disabled the key is `{"enabled": false}` (mirrors the `model_routing` disabled shape).
- `overseer governance-sync` footer: the same one-line-per-slice spend-awareness reminder, emitted
  alongside the existing §KH1.9 gate reminders when `governance-sync` is in `surfaces`.
- All emitted lines are **reminders only**: they carry the same "acknowledge or decide; silence is
  not pass" posture as governance gates and never change a success exit code.

**Exit code (frozen addition; non-overlapping with existing `1`,`2`,`4`,`5`,`7`,`8`,`10`–`11`,
`20`–`26`,`30`–`31`):**

| Code | Meaning | Where |
| --- | --- | --- |
| `0` | Surface emitted / cost annotation succeeded | `route`, `status`, `governance-sync` |
| `32` | Malformed cost-awareness metadata — a declared `cost_class` outside the frozen vocabulary `free\|low\|moderate\|high`, or a non-string `cost_class`, in `model_tiers` | `route` (cost annotation path) |

- Exit `32` is a **data-integrity** fault (the shared `model_tiers` file is invalid), never a
  spend decision. It is confined to `overseer route` — the explicit cost/routing resolution surface,
  which already fails closed when the `model_tiers` document it must read is invalid. The Auto build
  raises it as a routing-policy-error-typed failure carrying `exit_code = 32` so the existing
  `overseer route` error handling maps it cleanly.
- On `overseer status` and the `overseer governance-sync` footer, malformed cost metadata degrades to
  a read-only `cost_awareness: invalid — <violation>` **warning** and does **not** change the success
  exit code — byte-for-byte the same posture as the existing `model_routing: invalid` warning
  (`cli/commands/status.py`). This keeps the informational surfaces graceful and honors the §PC.1
  rule that cost never changes an exit code; the only hard-fail path is the explicit `route` surface.
- A **missing/unreadable** routing policy while `cost_awareness.enabled: true` reuses exit `31`; a
  structurally **malformed routing policy** reuses exit `30`. P-cost introduces only `32`.
- `32` never overlaps the L2 honesty codes (`20`–`24`), the provenance codes (`25`/`26`), or the
  P-route codes (`30`/`31`).

---

## §PC.8 — Boundary & capability table (frozen)

The single most important frozen rule: **the kit holds and surfaces the cost-awareness view; the
runtime spends the money.** This keeps the kit on the governance/frontend side of the K7 / `AGENTS.md`
boundary.

| Concern | Overseer Kit (cost-awareness rule-holder) | Runtime — Cursor / OpenRouter / Scooling 9A (spender) |
| --- | --- | --- |
| Own the relative cost bands | Yes — `cost_class` in `model_tiers` | No (consumes them) |
| Surface "paid step before spend" in advance | Yes (read-only reminder) | May re-surface in its own UI |
| Name a dollar amount / currency | **Never** | Yes (its own price list) |
| Keep a budget / spend cap / running total | **Never** | Yes (if it chooses) |
| Convert a band → a real price | **Never** | Yes |
| Block or refuse on spend | **Never** (reminder only) | Yes (its own policy) |
| Call / dispatch a model, open a network connection | **Never** | Yes |
| Fail closed on malformed cost metadata | Yes (exit `32`) | May re-validate |

Capability tiers (baseline vs deepen):

| Capability | `git-only` (baseline) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Declare + validate cost bands | Full | Full (identical) |
| Annotate `overseer route` with cost | Full | Full (identical) |
| Active-slice spend-awareness surface | Full | Full (identical) |
| Dollar math / budgets / spend caps | **Not in the kit** (runtime) | **Not in the kit** (runtime) |

Cost-awareness adds no substrate-gated capability: everything works on plain GitHub, matching the K7
frozen guardrail.

---

## §PC.9 — Seven-tier test matrix (P-cost Auto build must satisfy)

The P-cost Auto build ships all seven tiers green locally before DONE (`policy/test-tiers.yaml`).

| Tier | Proves |
| --- | --- |
| **unit** | `cost_class` parse (optional; accepts only `free\|low\|moderate\|high`; rejects any other value and non-string → exit `32`; `cost_class` accepted as a known `model_tiers` key, not rejected as unknown); `paid_step_before_spend` derivation for every band + `human` (unpaid) + absent band (conservative `unknown` → paid); ordinal ordering `free<low<moderate<high`; `cost_awareness` config parse (default off, `surfaces` closed vocabulary, unknown value → exit `2`); phase-`Model`-label → `phase_tier` normalization; pending-gate → routing `gate` mapping; derivation purity (no I/O). |
| **integration** | `overseer route` emits additive `cost_class` + `paid_step_before_spend` for representative selectors without changing `route_id`/`model_tier`/`fallback`; malformed `cost_class` → route exit `32`; `overseer status` composes config + routing policy to emit the active-slice surface only when `cost_awareness.enabled: true`; disabled → status output byte-identical to pre-P-cost; missing policy while enabled → exit `31`. |
| **e2e** | Full active-slice cycle on a fixture repo whose handover NEXT is a `Thinking` freeze slice with a pending `freeze_review` gate → surface reports `deep-reasoning (high) — paid step before spend`; an `Auto` slice → `standard (moderate)`; a slice routing to `local-offline` → `free`, `paid_step_before_spend: false`; `governance-sync` footer carries the same lines; identical results under `git-only` and a Muse regime. |
| **stress** | Many active slices / a large routing policy resolve + annotate within a documented bound; no unbounded scan; the active-slice surface is order-stable under a fixed handover/roadmap. |
| **data-integrity** | Surface + annotation are idempotent (same inputs twice = same output); `paid_step_before_spend` derivation is deterministic; enabling cost-awareness does not mutate any file (read-only); no partial write on induced mid-resolution failure; disabled cost-awareness leaves `version.lock`/footprint digest unchanged. |
| **performance** | Route annotation and the active-slice surface complete within a bounded time on a realistic handover/roadmap + policy size; no unbounded VCS or filesystem scan on the cost path (reuses the existing bounded gate scan). |
| **security** | No dollar amount, currency symbol, price, vendor slug, endpoint, or key ever appears in `cost_class`, in `route` output, or in the spend-awareness surface; **no network connection and no model call is made on any code path** (asserted, e.g. via a runner/socket guard); malformed or injection-shaped `cost_class`/label values are treated as opaque data and fail closed (`32`), never executed; the surface never blocks a build/merge on spend (reminder-only asserted); no secret or identity leakage in logs. |

---

## §PC.10 — Shared-contract note for consumer runtimes (informative)

The frozen cost-awareness shape is a contract three runtimes consume, each staying on its own side of
the boundary:

- **Cursor** — reads `paid_step_before_spend` to warn a user before a step that would engage a
  metered model in its picker; the band → real price mapping lives in the user's own understanding of
  their plan, not the kit.
- **OpenRouter** — a consumer runtime maps each `cost_class` band to its own knowledge of OpenRouter
  model prices, computes the actual dollar cost, and enforces any budget in its runtime. The kit
  supplies only the relative band + paid flag.
- **Scooling 9A router** — the worker/checker/foreman router (reference in `docs/consumers`, not
  vendored) uses the band to decide whether a cheaper tier or the `human` terminal is warranted
  before spending, then does the metered call in its own runtime. This is the `AGENTS.md` boundary:
  the 9A router is reference-only; the kit owns the cost-awareness shape, never the spend.

In every case the runtime converts the band into money and makes the spend decision; the kit only
declares the bands, derives the paid flag, and surfaces the warning **before** the spend.

---

## §PC.11 — Close-out (execute only when P-cost freeze marked DONE)

1. Freeze-review `pass` recorded in the Review record table above (stamp written by
   `overseer review --freeze`).
2. ROADMAP Track P / P-cost row: freeze **DONE (Thinking)**; queue the **P-cost Auto build**
   (`{step}b`) against this contract.
3. Handover NEXT flips to **Track P / P-cost Auto build** with a paste-ready prompt + the mandatory
   governance-gate reminders.
4. Governance sync: `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together in the same
   commit (SD-17).
