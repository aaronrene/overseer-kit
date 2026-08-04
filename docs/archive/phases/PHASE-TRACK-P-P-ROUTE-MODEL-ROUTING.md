# Phase Track P / P-route — Declarative model-routing policy (Thinking freeze)

Status: **Reviewed → `pass` (P-route-r2).** P-route Thinking is **spec-only** and now frozen; no
code, no policy file, and no `policy/model-labels.yaml` edit land in this phase. The P-route Auto
build (`{step}b`) is cleared to start mechanically against this frozen contract; it is the only phase
that writes files. Do **not** re-derive this contract during the Auto build.

```yaml
phase: TRACK-P-P-ROUTE
outputs:
- id: track-p-p-route-model-routing
  path: docs/archive/phases/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md
  frozen: true
frozen_inputs:
- id: model-labels
  path: policy/model-labels.yaml
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: layered-honesty-vision-spend
  path: docs/archive/thinking/OVERSEER-KIT-LAYERED-HONESTY-VISION.md#12-insight-videofactory-2026-07
- id: roadmap-p-route-row
  path: docs/ROADMAP.md
- id: scooling-router-reference
  path: docs/consumers
review_stamp:
  reviewed_at: '2026-07-12T23:07:19Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:ab6b6a9a333523769834a8f1b6623169e38d0e1bbe80db0225fde092328724b4
```

**Downstream edge:** the P-route Auto build (`{step}b`) treats this document as ground truth without
re-deriving it (SPEC §6 mandatory reviewed freeze). Consumer runtimes (Cursor, OpenRouter, Scooling
9A) also read the frozen `policy/model-routing.yaml` schema as ground truth for what a routing
decision *looks like* — but the runtime, never the kit, performs the model selection and dispatch.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| P-route-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist gate clean (0 findings). Semantic review raised two non-escalating MINOR consistency findings: **R1-N1** (§PR.6 exit `31` wording ambiguous vs. the `enabled: false` explicit-`route` path) and **R1-N2** (§PR.4 left the `model_tier` ↔ `fallback[0]` relationship unspecified). Both fixed minimally: `31` now fires on any routing op needing the policy independent of `enabled`; `fallback[0]` MUST equal `model_tier` and terminate in `human` (else exit `30`). |
| P-route-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read confirmed R1-N1 + R1-N2 RESOLVED; frozen example routes satisfy `fallback[0] == model_tier`; exit codes `30`/`31` non-overlapping with `20`–`26`; boundary table holds (kit = rule-holder, runtime = executor); seven-tier matrix complete; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `overseer review --freeze`. |

---

## §PR.0 — Simple summary

Different governance work needs different-strength AI models. A quick mechanical build step can use a
cheap fast model; freezing a contract or ruling on a dispute needs a strong reasoning model; an
offline machine needs a local model. Today that choice lives in an operator's head and in scattered
runtime settings, so it is neither written down nor auditable.

**Track P / P-route freezes a single declarative rulebook** — `policy/model-routing.yaml` — that
writes the choice down as data: for a given **seat** (who is doing the work), **phase tier** (what
kind of work), and **gate** (which checkpoint), the rulebook names a **model tier** (an
abstract strength level, never a brand) plus an ordered **fallback** chain that always ends in a
human. The Overseer Kit *holds and checks* this rulebook. The **runtime** — Cursor's model picker,
OpenRouter, or Scooling's worker/checker/foreman router — *reads* it and does the actual model call.
The kit itself never calls a model, never holds a key, and never dispatches work.

**Technical summary:** add a repo-agnostic, declarative routing policy `policy/model-routing.yaml`
(`version: 1`) that maps a selector triple `{position, phase_tier, gate}` to a `model_tier` id plus
an ordered `fallback` chain, resolved by ordered first-match-wins with a mandatory `defaults`
terminal (total resolution). Extend — do not fork — `policy/model-labels.yaml` with a new
`model_tiers:` section defining the abstract capability tiers the routing policy references (each an
`id` + `display` + `meaning` + non-binding `cursor_model_hint`; never a vendor slug or endpoint). Add
an optional, default-inert `model_routing:` config block and a read-only `overseer route` resolution
surface that returns the routing decision as data. The kit performs no model calls, holds no API
key, opens no network connection, and embeds no vendor slug — it is the rule-holder, never the
executor.

---

## §PR.1 — Scope

**In scope (freeze only — this phase writes no code):**

- The `model_tiers:` extension schema for `policy/model-labels.yaml` (§PR.3).
- The `policy/model-routing.yaml` schema + the deterministic resolution algorithm (§PR.4).
- The optional `model_routing:` config block and regime interaction (§PR.5).
- The read-only `overseer route` CLI surface + new exit codes (§PR.6).
- The boundary + capability table that keeps the kit a rule-holder, not an executor (§PR.7).
- The seven-tier test matrix the P-route Auto build must satisfy (§PR.8).
- The informative shared-contract note for consumer runtimes (§PR.9).

**Out of scope (explicit non-goals — prevent creep):**

- **Any model call, dispatch, or runtime model selection inside the kit** — no HTTP client to a model
  provider, no OpenRouter integration, no live picking of a concrete model. The kit resolves a
  *tier + fallback*, as data; the runtime maps that tier to a concrete model and executes.
- **Vendor slugs, model names, provider endpoints, prices, or keys in kit policy** — the policy is a
  brand-agnostic rulebook. Mapping a tier to a concrete model (for example `gpt`-class or
  `claude`-class) is the runtime's job, kept out of the kit for portability.
- **Cost / dollar math (P-cost)** — a separate slice; P-route names a *tier*, not a price.
- **Verification-evidence capture (P-evidence)** — separate slice; not touched here.
- **An org-chart taxonomy** — the kit does not enumerate every consumer's seats. `position` values
  are consumer-owned free-form strings; the kit fixes only the *shape* of the rule and the
  kit-owned `phase_tier` / `gate` vocabularies.
- **Making routing mandatory** — `model_routing.enabled` defaults `false`; a repo that never opts in
  is unaffected. Routing is a `git-only` baseline capability (no Muse dependency), per the K7
  guardrail that no baseline feature may be substrate-gated.

---

## §PR.2 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Phase labels | `labels[]` = `thinking`, `auto`, `thinking_to_auto`, `operator_plus_auto` (workflow labels for roadmap rows) | `policy/model-labels.yaml` |
| Reviewer models | `reviewer_models[]` = `thinking-high`, `auto-default` (freeze-review model labels) | `policy/model-labels.yaml` |
| Label rule | Every roadmap/handover step names exactly one label; a reviewer model is a **label, never a vendor slug** | `policy/model-labels.yaml` |
| Fail-closed reviewer pattern | `freeze_contract.reviewer.fallback: human` — unreachable provider falls back to human, never skips | `docs/OVERSEER-KIT-SPEC.md#6` |
| Seven-tier contract | Every code-adding build phase ships all seven tiers before DONE | `policy/test-tiers.yaml` |
| Decision tiers | Tier 1 feature-branch / Tier 2 confirm / Tier 3 hard gate | `policy/tiers.yaml` |
| Boundary | The kit is repo-agnostic governance/frontend, **never** a runtime, dispatcher, or model-host; Scooling's 9A router is reference-only | `AGENTS.md` |

P-route **must not** change existing `labels`, `reviewer_models`, the label-not-slug rule, existing
config blocks, or any existing exit code. It only **adds** a `model_tiers:` section, a
`model-routing.yaml` file, an optional `model_routing:` config block, an `overseer route` command,
and new non-overlapping exit codes.

---

## §PR.3 — `model_tiers` extension for `policy/model-labels.yaml` (frozen schema)

The Auto build adds a new top-level `model_tiers:` section to the existing `policy/model-labels.yaml`
(**extend, do not fork** — one canonical label file). Existing `labels` and `reviewer_models` are
untouched. Each tier is an **abstract capability level**, never a brand.

```yaml
model_tiers:
  - id: deep-reasoning       # strongest reasoning; freeze/ruling/dispute work
    display: Deep reasoning
    meaning: >
      Extended-thinking / frontier-class reasoning for contract freezes, disputes,
      overseer rulings, and security-sensitive review.
    cursor_model_hint: extended thinking / Opus-class   # HINT ONLY, non-binding
  - id: standard             # balanced default for most build work
    display: Standard
    meaning: >
      Balanced capability for mechanical builds against a frozen spec and routine
      verification steps.
    cursor_model_hint: default / Composer / Sonnet-class
  - id: fast                 # cheap/quick low-stakes steps
    display: Fast
    meaning: >
      Low-latency, low-cost tier for trivial or high-volume low-stakes steps.
    cursor_model_hint: fast / mini-class
  - id: local-offline        # no network; offline-capable runtime
    display: Local (offline)
    meaning: >
      Locally hosted model for offline or privacy-first runtimes; preserves the
      kit's offline promise. The kit still performs no call — the runtime does.
    cursor_model_hint: local / on-device
```

Rules (frozen):

1. `model_tiers[]` entries require a non-empty string `id`, `display`, and `meaning`. `id` values are
   lowercase kebab, unique within the file.
2. `cursor_model_hint` is an **advisory hint only** — informative text a human or runtime may read.
   It is **never** authoritative and **never** a hard vendor pin; a runtime is free to map a tier to
   any concrete model it offers.
3. A `model_tiers` entry **must not** contain a resolvable vendor slug, provider endpoint, price, or
   key. Detection uses the same label-not-slug discipline already enforced for reviewer models
   (`gpt-` / `claude-` / `composer-` style tokens are rejected).
4. `human` is a reserved terminal tier id used only inside `fallback` chains (§PR.4); it denotes
   "stop and ask a person" and is not declared in `model_tiers`.

---

## §PR.4 — `policy/model-routing.yaml` schema + resolution (frozen)

The Auto build vendors a default `policy/model-routing.yaml`. Consumers override it in their own repo
(same override pattern as other vendored policy files). Schema (`version: 1`):

```yaml
version: 1
# Declarative model-routing POLICY. The Overseer Kit is the rule-holder; the
# runtime (Cursor / OpenRouter / Scooling 9A) is the executor. The kit performs
# no model call, holds no key, and dispatches nothing.

defaults:                      # MANDATORY terminal — guarantees total resolution
  model_tier: standard
  fallback: [standard, human]

routes:                        # ordered; first match wins
  - id: freeze-thinking
    when: { gate: freeze_review, phase_tier: thinking }
    model_tier: deep-reasoning
    fallback: [deep-reasoning, human]
  - id: overseer-ruling
    when: { position: overseer }
    model_tier: deep-reasoning
    fallback: [deep-reasoning, human]
  - id: build-verification
    when: { gate: build_verification }
    model_tier: standard
    fallback: [standard, deep-reasoning, human]
  - id: auto-build
    when: { phase_tier: auto }
    model_tier: standard
    fallback: [standard, human]
  - id: offline-worker
    when: { position: worker, gate: default }
    model_tier: local-offline
    fallback: [local-offline, standard, human]
```

**Selectors (`when`) — frozen semantics:**

| Key | Owner | Allowed values | Unknown value behavior |
| --- | --- | --- | --- |
| `position` | Consumer org-chart | Free-form string (for example `foreman`, `worker`, `checker`, `overseer`, `reviewer`) | Rule simply does not match; fall through |
| `phase_tier` | Kit | An `id` from `labels[]` in `policy/model-labels.yaml` | Rule does not match; fall through (forward-compatible) |
| `gate` | Kit | `freeze_review`, `build_verification`, or `default` | Rule does not match; fall through |

- Any selector key may be omitted; an omitted key is a wildcard (matches anything).
- Only the three keys `position`, `phase_tier`, `gate` are permitted inside `when`. Any **other**
  key fails closed (invalid policy, exit `30`) — strict-key discipline mirrors config parsing.

**Resolution algorithm (frozen, deterministic):**

1. Evaluate `routes` top-to-bottom. The **first** rule whose every present `when` key matches the
   query wins; return its `model_tier` + `fallback`.
2. If no rule matches, return `defaults.model_tier` + `defaults.fallback`. Because `defaults` is
   mandatory, resolution is **total** — it always yields a tier + chain, never null.
3. Resolution is **pure and deterministic**: identical query + identical policy always yields the
   identical decision, with no I/O, no network, and no randomness.

**Value rules (frozen):**

1. `model_tier` (in every route and in `defaults`) MUST be an `id` present in `model_tiers` of
   `policy/model-labels.yaml`, or the reserved `human`. Otherwise the policy is invalid (exit `30`).
2. `fallback` is the complete, ordered list of tiers the runtime attempts. `fallback[0]` **MUST
   equal** that route's `model_tier` (the primary is attempt #1), and the list **MUST terminate in
   `human`**. This is the same fail-closed rule as the freeze reviewer (`fallback: human`): when no
   non-`human` tier in the chain is reachable, the runtime stops and asks a person rather than
   silently skipping. A policy whose `fallback[0] != model_tier`, or that omits the `human`
   terminal, is invalid (exit `30`).
3. No `model_tier`, route `id`, or comment may embed a vendor slug, endpoint, price, or key.
4. `route.id` values are unique, non-empty strings (used for diagnostics and stable output order).
5. Unknown top-level keys, or unknown keys inside a route/`defaults`, fail closed (exit `30`).

---

## §PR.5 — Config block & regime interaction (frozen)

Add an optional, additive `model_routing:` block to `.overseer/config.yaml` (default preserves
current behavior — routing is off and inert):

```yaml
model_routing:
  enabled: false                        # default false — inert; runtime opt-in
  policy: policy/model-routing.yaml      # repo-relative path to the routing policy
```

| Field | Default | Meaning |
| --- | --- | --- |
| `enabled` | `false` | When `false`, no routing gate is surfaced and `overseer status` is unchanged. `overseer route` still resolves/validates on explicit request (informational). When `true`, `overseer status` adds a read-only routing-policy-validity line. |
| `policy` | `policy/model-routing.yaml` | Confined repo-relative path (path-escape rejected, exit `4`, consistent with other path handling). |

Regime interaction: routing is **regime-agnostic** and a `git-only` baseline capability. Behavior is
byte-identical across `git-only`, `muse+git-mirror`, and `muse-only` — there is no Muse dependency
and no substrate gate. This upholds the K7 guardrail (no baseline feature may be MuseHub-only).
Enabling routing **never** causes a model call under any regime.

---

## §PR.6 — CLI surface & exit codes (frozen)

The Auto build adds one **read-only** command. It resolves and explains routing decisions as data; it
performs no model call, opens no network connection, and dispatches nothing.

```
overseer route --position <str> --phase-tier <id> --gate <id>   # resolve one decision
overseer route --validate                                        # validate the policy only
```

- All selector flags are optional; an omitted flag is a wildcard for that dimension.
- Output (human + `--json`) reports: the matched `route.id` (or `defaults`), the resolved
  `model_tier`, and the ordered `fallback` chain. `--json` emits a stable, machine-readable object so
  a runtime can consume the decision directly.
- `--validate` loads the policy, applies every §PR.4 value rule, and reports valid / the first
  violation with a citation, then exits.

**Exit codes (frozen additions; non-overlapping with existing `1`,`2`,`4`,`5`,`7`,`8`,`10`–`11`,
`20`–`26`):**

| Code | Meaning | Where |
| --- | --- | --- |
| `0` | Resolution succeeded / policy valid | `route`, `route --validate` |
| `30` | Malformed routing policy (unknown key, `model_tier` absent from `model_tiers`, `fallback` missing `human` terminal, vendor slug present, duplicate `route.id`, missing mandatory `defaults`) | `route`, `route --validate`, policy load |
| `31` | A routing operation needs the policy but `policy` file is missing or unreadable — fires on any `route` / `route --validate` invocation and whenever `enabled: true`, independent of `enabled` (fail-closed; never silently defaults) | `route`, `route --validate`, policy load |

`30`/`31` never overlap the L2 honesty codes (`20`–`24`) or the provenance codes (`25`/`26`). Usage
errors keep exit `1`; config parse errors keep exit `2`; path-escape keeps exit `4`.

---

## §PR.7 — Boundary & capability table (frozen)

The single most important frozen rule: **the kit holds and validates the rulebook; the runtime
executes it.** This keeps the kit on the governance/frontend side of the K7 / `AGENTS.md` boundary.

| Concern | Overseer Kit (rule-holder) | Runtime — Cursor / OpenRouter / Scooling 9A (executor) |
| --- | --- | --- |
| Own the routing rules | Yes — `policy/model-routing.yaml` | No (consumes them) |
| Validate the rules fail-closed | Yes (exit `30`/`31`) | May re-validate |
| Resolve tier + fallback as data | Yes (`overseer route`, pure function) | Reads the decision |
| Map a tier → a concrete model | **Never** | Yes (its own model list) |
| Hold an API key / provider endpoint | **Never** | Yes |
| Open a network connection to a model | **Never** | Yes |
| Call / dispatch a model | **Never** | Yes |
| Apply the `human` fallback terminal | Declares it | Executes the stop-and-ask |

Capability tiers (baseline vs deepen):

| Capability | `git-only` (baseline) | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Hold + validate routing policy | Full | Full (identical) |
| Resolve tier + fallback | Full | Full (identical) |
| `overseer route` read-only surface | Full | Full (identical) |
| Model dispatch | **Not in the kit** (runtime) | **Not in the kit** (runtime) |

Routing adds no substrate-gated capability: everything works on plain GitHub, matching the K7
frozen guardrail.

---

## §PR.8 — Seven-tier test matrix (P-route Auto build must satisfy)

The P-route Auto build ships all seven tiers green locally before DONE (`policy/test-tiers.yaml`).

| Tier | Proves |
| --- | --- |
| **unit** | `model_tiers` parse (required fields, unique kebab ids, vendor-slug rejection); `model-routing.yaml` schema parse (strict keys, `defaults` mandatory, `model_tier` ∈ `model_tiers`∪`human`, `fallback` non-empty and terminating in `human`, unique `route.id`); selector wildcard + first-match-wins + `defaults` fall-through; resolution purity (no I/O). |
| **integration** | `overseer route` composes config + policy: resolves a decision for representative selector triples; `--validate` reports valid / first violation; `enabled: false` vs `true` behavior; missing policy → `31`; malformed policy → `30`; path-escape on `policy` → `4`. |
| **e2e** | Full resolve cycle over a fixture policy across seats/phase-tiers/gates (for example `overseer` → `deep-reasoning`; `phase_tier: auto` → `standard`; unmatched → `defaults`); identical results under `git-only` and a Muse regime; `overseer status` shows the routing-validity line only when `enabled: true`. |
| **stress** | A large policy (many routes, deep fallback chains) resolves and validates within a documented bound; no unbounded scan; order-independence of match result under a fixed policy. |
| **data-integrity** | Resolution is idempotent (same query twice = same decision); `--validate` is deterministic; the routing policy file is included in the footprint/`version.lock` digest; no partial write on induced mid-validation failure. |
| **performance** | Resolve and `--validate` complete within a bounded time on a realistic policy size; no unbounded VCS or filesystem scan on the routing path. |
| **security** | No vendor slug, endpoint, price, or key ever appears in the policy or in any `route` output; **no network connection and no model call is made on any code path** (asserted, for example via a runner/socket guard); malformed or injection-shaped selector strings are treated as opaque data, never executed; fail-closed on malformed (`30`) and missing (`31`) policy; no secret or identity leakage in logs. |

---

## §PR.9 — Shared-contract note for consumer runtimes (informative)

The frozen `policy/model-routing.yaml` shape is the contract three runtimes consume, each staying on
its own side of the boundary:

- **Cursor** — reads the resolved `model_tier` to pre-select a model in its own picker; the mapping
  tier → concrete Cursor model lives in the user's Cursor settings, not the kit.
- **OpenRouter** — a consumer runtime maps each tier to an OpenRouter model of matching strength and
  makes the call with its own key. The kit supplies only the tier + fallback ordering.
- **Scooling 9A router** — the worker/checker/foreman router (reference in `docs/consumers`, not
  vendored) uses `position` + `gate` to pick a tier, then resolves the tier to a concrete model in
  its own runtime. This is the `AGENTS.md` boundary: the 9A router is reference-only; the kit owns
  the rulebook shape, never the dispatch.

In every case the runtime performs the model call and applies the `human` terminal when the fallback
chain is exhausted; the kit only holds, validates, and explains the rules.

---

## §PR.10 — Close-out (execute only when P-route freeze marked DONE)

1. Freeze-review `pass` recorded in the Review record table above (stamp written by
   `overseer review --freeze`).
2. ROADMAP Track P / P-route row: freeze **DONE**; queue the **P-route Auto build** (`{step}b`)
   against this contract.
3. Handover NEXT flips to **Track P / P-route Auto build** with a paste-ready prompt + the mandatory
   governance-gate reminders.
4. Governance sync: `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together in the same
   commit (SD-17).
