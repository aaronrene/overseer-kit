# Phase K13a — Multi-repo workspace / constellation lanes (Thinking freeze)

Status: **Reviewed → `pass` (K13a-r2).** K13a is **spec-only** and frozen; no CLI/consumer code
lands in this phase. K13b (Auto) builds mechanically against this contract. Do **not** claim the
feature exists until K13b + `/build-verification-review` → **`pass`**.

```yaml
phase: K13a
outputs:
- id: multi-repo-workspace-lanes
  path: docs/MULTI-REPO-WORKSPACE-LANES-FREEZE.md
  frozen: true
frozen_inputs:
- id: kit-spec-config-cli
  path: docs/OVERSEER-KIT-SPEC.md
- id: governance-hygiene-9a5
  path: docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: kh1-handover-relay
  path: docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: k8-multi-lane-docs
  path: docs/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md
- id: kh2-muse-sync
  path: docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md
- id: model-labels
  path: policy/model-labels.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: test-tiers
  path: policy/test-tiers.yaml
- id: dogfood-config
  path: .overseer/config.yaml
- id: handover-template
  path: templates/OVERSEER-HANDOVER.template.md
- id: cross-repo-template
  path: templates/CROSS-REPO-COORDINATION.template.md
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: agents-boundary
  path: AGENTS.md
review_stamp:
  reviewed_at: '2026-07-27T15:46:06Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:086d79ef2c4b7b956b302e9ec9671a816232f46538e628b60eacd1410587af16
```

**Downstream edge:** K13b Auto treats this document as ground truth without re-deriving it
(SPEC §6). Consumer constellation adoption (Scooling ↔ Knowtation → MuseHub → Brain) is
**operator-gated migration** after K13b ships; this freeze does not authorize edits in those repos.

**Incident that must not recur (verified 2026-07-27):** multi-root Cursor had Scooling / Knowtation /
MuseHub / overseer-kit open; operator read Knowtation’s TOP `NEXT SESSION` (still Thinking /
L-SEAM) while Scooling’s board had already advanced to L-SEAMb Auto. Knowtation also retained
multiple `## NEXT SESSION — archived …` headings. Operator concluded “kit failed”; `ok status` was
healthy. Gap: kit has no first-class multi-repo / multi-lane / relay freshness model.

**Hard facts verified against kit source (do not invent “it already does X”):**

| ID | Fact | Evidence |
| --- | --- | --- |
| A | Unit of governance = one repo, one `.overseer/config.yaml`, one default handover/roadmap pair | SPEC §3; `.overseer/config.yaml`; K8 adds *intra-repo* lanes only |
| B | `ok governance-sync` / 9A-5 = single-repo docs↔VCS drift; does not read peer roots or relay tips | `docs/PHASE-9A-5-…`; `tools/governance_hygiene/` (no peer/workspace symbols) |
| C | `ok status` = per-repo health; green ≠ constellation consistent | `cli/commands/status.py`; SPEC §5 |
| D | Handover templates / consumer practice allow multiple `## NEXT SESSION —` headings | KH1 H2 requires exactly one; Knowtation live file still has archived `## NEXT SESSION —` headings |
| E | Multi-root Cursor makes the focused tab look authoritative | Incident 2026-07-27 |
| F | Muse≠Git dual history can diverge; `muse_sync` pending is per-repo | KH2; regime backends |
| G | SD-3 `{step}a`/`{step}b` split does not answer which repo’s `{step}b` is product PRIMARY | `policy/model-labels.yaml`; KH1 |
| H | Regimes differ across members (`muse+git-mirror`, `muse-only`, `git-only`) | SPEC §4; consumer AGENTS |
| I | Tier 3 forbids auto-merge / live flips / staging push across repos | `policy/tiers.yaml` |

**Review record (§6.2):** every freeze-review finding MUST cite **file+line**; uncited findings are
invalid. Fixes during the loop are Tier 1 (feature branch); merge to `main` is Tier 3 and is never
part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| K13a-r1 | Freeze-review loop (thinking-high); file+line citations | findings | **R1-M1–M4** fixed in-tree (see ledger). CLI checklist `--dry-run` clean. Not cleared until r2. |
| K13a-r2 | Freeze-review loop (thinking-high); independent re-read | **pass** | R1-M1–M4 confirmed RESOLVED; full §MR.0–§MR.16 regress clean; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp via `ok review --freeze`. Cleared for K13b. |

### Freeze-review findings ledger (K13a-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | consistency | `docs/MULTI-REPO-WORKSPACE-LANES-FREEZE.md` §MR.6.1 (pre-fix) | Lane tips reused `## NEXT SESSION —`, contradicting KH1 H2 (“exactly one NEXT SESSION”) and enabling PRIMARY confusion. |
| R1-M2 | MAJOR | completeness | §MR.6 / Knowtation ownership+relay pattern | Ownership boards that also `relay: true` had no durable product tip when LIVE NEXT is ownership PRIMARY — 2026-07-27 class of bug would recur when Knowtation works SEC-* while Scooling advances. |
| R1-M3 | MAJOR | completeness | §MR.8 footer states | `incomplete_after_primary_advance` required a session oracle Auto cannot implement; collapsed to freshness predicate states. |
| R1-M4 | MINOR | consistency | §MR.12.2 grace vs `strict_markers` | Grace heuristic conflicted with default-strict honesty; replaced with explicit `strict_markers` bool (default true). |

---

## §MR.0 — Simple summary

When several related projects share one editor window, people paste the wrong “what’s next” note —
often the tab they happen to be looking at, or an old archived prompt that still looks like a live
one. The kit today keeps each project honest **by itself**, but it never checks whether a project
that is only a *pointer* to the product board still matches that board.

This phase freezes a **workspace (constellation)** model: a small list of related repos, who owns
product sequencing, who is only a relay, and how to fail closed when a relay tip is stale. Operators
and other developers get the same mechanical check — no folklore required.

## Technical summary

K13 freezes an **optional, additive** constellation layer on top of unchanged single-repo
governance (SPEC §3, 9A-5, KH1, K8, SD-17):

1. **Manifest** — checked into the **product_order** member as `.overseer/workspace.yaml`
   (Option B primary), with env / home override for path remapping (Option A override).
2. **Member config pointer** — additive `workspace:` block in each member’s
   `.overseer/config.yaml` for discovery.
3. **Handover UX markers** — machine-distinct LIVE PRIMARY / RELAY / ARCHIVED / LANE TIP blocks
   (amends KH1 heading discipline without replacing single-repo H1–H12).
4. **CLI** — `ok workspace status`, `ok workspace check-next` (fail on stale relay), optional
   `ok workspace doctor`; single-repo `ok status` green **must not** imply workspace OK (S9).
5. **Session-end** — advancing product_order PRIMARY without refreshing declared relays =
   incomplete multi-repo SD-17 (sibling gate to single-repo `governance-sync`).
6. **Lanes** — compose with K8 intra-repo `docs.lanes`; add cross-member lane ids so parallel
   workstreams cannot steal product PRIMARY.
7. **Regime-aware** — per-member `vcs.regime`; never issue git/gh for `muse-only` members.
8. **Seven-tier** test matrix for K13b, including honesty fail if tools claim workspace OK while
   a relay disagrees with product_order PRIMARY.

---

## §MR.1 — Scope

**In scope (freeze only — this phase writes no product/CLI code beyond this artifact + kit
governance doc updates):**

- Workspace / constellation model (§MR.2)
- Manifest location decision + schema (§MR.3)
- Member `.overseer/config.yaml` additive `workspace:` pointer (§MR.4)
- Authority + conflict rules (§MR.5)
- Handover UX contract + KH1 amendments (§MR.6)
- CLI / skill / rule surface (§MR.7)
- Relationship to 9A-5 / SD-17 (§MR.8)
- Acceptance stories S1–S11 (§MR.9)
- Seven-tier test matrix (§MR.10)
- Tier-3 hard stops (§MR.11)
- Migration / rollout (§MR.12)
- Explicit non-goals (§MR.13)
- Roadmap phase proposal + Auto deliverables list (§MR.14)

**Out of scope (this Thinking session):**

- Implementing `ok workspace *` or parsing logic
- Migrating Scooling / Knowtation / MuseHub / Brain handovers
- Merging to `main`, staging push, live posture flips
- Replacing product content inside consumer `CROSS-REPO-COORDINATION.md`
- Building Brain firmware or any consumer product feature

---

## §MR.2 — Workspace / constellation model (frozen)

### §MR.2.1 — Definitions

| Term | Meaning |
| --- | --- |
| **Constellation** (workspace) | Named set of related consumer (and optionally kit) repos that share product sequencing |
| **Member** | One git/muse repo root with its own `.overseer/config.yaml` |
| **product_order** | Exactly **one** member whose handover/roadmap wins on **product sequencing** (“what is NEXT” for the product) |
| **ownership** | Member whose board wins on that member’s own authorization / store / domain behavior |
| **enrichment** | Member that owns enrichment-only concerns (e.g. MuseHub provenance/social) — not product sequencing |
| **edge** | Member for edge/device runtime (future Brain) — first-class role even if path unknown |
| **kit** | Overseer Kit source — not a product lane; may be listed for doctor/status only |
| **RELAY tip** | A board that publishes a tip pointing at another member’s PRIMARY (usually product_order) |
| **LIVE PRIMARY** | The single paste-ready product NEXT on the product_order board (or a lane’s designated PRIMARY) |
| **Lane** | Named parallel workstream (`product`, `security`, `ux`, …) with at most one PRIMARY tip per lane |
| **required / optional member** | Required members missing locally → fail closed; optional missing → reported `member_absent` without failing the whole check unless `--strict-all` |

### §MR.2.2 — Roles (closed vocabulary)

```text
product_order | ownership | enrichment | edge | kit | other
```

Rules:

- Exactly **one** member with `role: product_order` per constellation.
- Zero or more `ownership` / `enrichment` / `edge` / `kit` / `other`.
- `relay: true` may be set on any non-`product_order` member (and never on product_order).
- `kit` members are never product_order and never declare product RELAY tips that claim product
  PRIMARY authority.

### §MR.2.3 — Today’s + tomorrow’s constellation (informative example)

Not normative paths — Auto fixtures use synthetic roots. Operator dogfood targets:

| Member id | Role | Regime (typical) | Notes |
| --- | --- | --- | --- |
| `scooling` | `product_order` | `muse+git-mirror` | Product sequencing board |
| `knowtation` | `ownership` + often `relay: true` | `muse+git-mirror` | Store/authz board; may relay product NEXT |
| `musehub` | `enrichment` | `muse-only` | No git/gh commands from kit workspace tools |
| `overseer-kit` | `kit` | `muse+git-mirror` (dogfood) | Not a product lane |
| `brain` | `edge` | TBD | `required: false` until path known |

External developers with only **store + app** use the same model with two members
(`product_order` + `ownership` relay).

### §MR.2.4 — Lanes vs K8

| Layer | Owns | Frozen interaction |
| --- | --- | --- |
| **K8 `docs.lanes`** | Multiple handover/roadmap *pairs inside one repo* | Unchanged; workspace tools read the member’s **default lane** unless a constellation lane overrides `handover`/`roadmap` paths |
| **Constellation lanes** | Parallel workstreams *across* members | Each constellation lane has `id`, `primary` (bool), optional `owner_member` |

Frozen rules:

- Exactly one constellation lane may have `primary: true` (the **product** lane).
- Non-primary lanes may publish **LANE TIP** blocks; they MUST NOT use LIVE PRIMARY markers.
- A member’s K8 non-default lane docs are ignored by workspace PRIMARY extraction unless the
  constellation lane explicitly points at those paths.

---

## §MR.3 — Where the workspace definition lives (decision)

### Options considered

| Option | Verdict | Rationale |
| --- | --- | --- |
| **A** Operator home / `OVERSEER_WORKSPACES.yaml` only | **OVERRIDE only** | Good for path remapping across machines; bad as sole source of truth (not reviewed with product, easy to drift, invisible to other developers cloning product_order) |
| **B** Declared in **product_order** repo and discovered by peers | **CHOSEN (primary)** | Matches existing human policy (Scooling product-order board wins); travels with the product; reviewable in VCS; peers already know to look at product_order for sequencing |
| **C** Cursor multi-root workspace metadata + kit overlay | **REJECTED** | Ephemeral, IDE-coupled, not regime-aware, not portable to Claude Code / Copilot / CI |
| **D** Kit-central registry of all consumer constellations | **REJECTED** | Kit must stay repo-agnostic; no Aaron-folklore registry inside overseer-kit |

### Frozen decision

1. **Canonical manifest path (primary):**  
   `<product_order_root>/.overseer/workspace.yaml`
2. **Discovery:** each member’s `.overseer/config.yaml` carries an additive `workspace:` pointer
   (§MR.4).
3. **Path remap override (Option A):** if env `OVERSEER_WORKSPACE_MANIFEST` is set, that file is
   loaded **instead** of the product_order path (operator machines / CI fixtures). The override file
   MUST declare the same `id` as `workspace.constellation_id` or the tool fails closed (`CONFIG`).
4. **Home index (optional convenience, never sole authority):**  
   `~/.overseer/workspaces/<id>.yaml` MAY be a symlink or copy used only when
   `workspace.manifest` is unset **and** `product_order_root` is unset **and**
   `OVERSEER_WORKSPACE_MANIFEST` is unset — Auto must document this as **last resort** and warn
   `manifest_source: home_index` so operators do not confuse it with the reviewed product_order
   file.

**Rejected:** inventing a second parallel protocol outside kit docs / `.overseer/`.

---

## §MR.4 — Schemas (frozen)

### §MR.4.1 — `.overseer/workspace.yaml` (canonical)

```yaml
overseer_workspace_version: 1
id: scoaling-stack                    # constellation id (stable string)
product_order_member: scoaling        # must match exactly one member.id with role product_order
strict_markers: true                  # default true when omitted (§MR.12.2)

members:
  - id: scoaling
    role: product_order               # closed vocabulary §MR.2.2
    root: "${SCOOLING_ROOT}"          # see §MR.4.3 root resolution
    regime: muse+git-mirror           # advisory; must match member config when readable
    required: true                    # missing root → fail closed
    relay: false                      # product_order MUST be false
    # optional path overrides (else read member .overseer/config.yaml docs.*)
    handover: null
    roadmap: null

  - id: knowtation
    role: ownership
    root: "${KNOWTATION_ROOT}"
    regime: muse+git-mirror
    required: true
    relay: true                       # may publish RELAY tip for product lane

  - id: musehub
    role: enrichment
    root: "${MUSEHUB_ROOT}"
    regime: muse-only
    required: false                   # optional until checkout present
    relay: false

  - id: overseer-kit
    role: kit
    root: "${OVERSEER_KIT_ROOT}"
    regime: muse+git-mirror
    required: false
    relay: false

  - id: brain
    role: edge
    root: "${BRAIN_ROOT}"             # may be empty / unset
    regime: null                      # unknown until joins; null allowed only if required: false
    required: false
    relay: false

lanes:
  - id: product
    primary: true
    owner_member: scoaling            # defaults to product_order_member when omitted
  - id: security
    primary: false
    owner_member: knowtation
  - id: truth-harden
    primary: false
    owner_member: scoaling
```

**Validation (fail closed → exit `2` CONFIG):**

- `overseer_workspace_version` must be `1` (unknown → refuse).
- `id` non-empty; `product_order_member` must reference exactly one member with `role: product_order`.
- Exactly one `role: product_order`; that member has `relay: false`.
- Exactly one lane with `primary: true`.
- Member `id` unique; `role` ∈ closed vocabulary; `regime` ∈
  `{muse+git-mirror, muse-only, git-only, null}` with `null` only when `required: false`.
- No secrets, tokens, URLs with credentials, or identity claims (`X-User-Id`, wallet, email) in the
  manifest (§MR.11).

### §MR.4.2 — Member `.overseer/config.yaml` additive block

```yaml
# Additive; omitted = single-repo only (today). When present, workspace gates apply.
workspace:
  constellation_id: scoaling-stack
  # Discovery (first match wins):
  # 1) manifest: <path>                         # explicit
  # 2) product_order_root: <path>               # load <root>/.overseer/workspace.yaml
  # 3) if this repo's workspace.yaml exists and this member is product_order → local file
  # 4) OVERSEER_WORKSPACE_MANIFEST env
  # 5) ~/.overseer/workspaces/<constellation_id>.yaml (warn)
  product_order_root: null
  manifest: null
```

Rules:

- If `workspace:` is present, `constellation_id` is required.
- Manifest `id` MUST equal `constellation_id`.
- Single-repo `governance-sync` / `status` behavior unchanged when `workspace:` is absent.
- K8 `docs.lanes` unchanged.

### §MR.4.3 — Root resolution (frozen)

For each `members[].root`:

1. Expand `${ENV_VAR}` and `${ENV_VAR:-default}` (default may use `~`).
2. Expand leading `~` to the process home directory.
3. Resolve to an absolute filesystem path.
4. If `required: true` and path missing / not a directory / no `.overseer/config.yaml` →
   **fail closed** (`stale`/`missing_member`, exit `35` on `check-next`; `status` reports
   `workspace.ok: false`).
5. If `required: false` and missing → `member_status: absent` (non-fatal unless `--strict-all`).

**No network** to peer remotes for basic freshness. Local checkouts only.

---

## §MR.5 — Authority + conflict rules (machine-checkable)

| Conflict | Winner | Machine result if violated |
| --- | --- | --- |
| Product sequencing (step id, Model, which repo’s Auto is next) | **product_order** LIVE PRIMARY | Relay tip disagree → `stale_relay` |
| Authorization / store / domain behavior of an ownership member | That member’s **ownership** LIVE PRIMARY (its own board) | Not compared to product_order for domain content |
| Enrichment-only concerns | enrichment member board | Not product PRIMARY |
| Relay tip vs product_order PRIMARY | Must match on `(step_id, Model label, repo path/id, authority=relay)` | `stale_relay` |
| Parallel lane tip vs product PRIMARY | Lane tip allowed if marked non-PRIMARY; must not use PRIMARY marker | `ambiguous_primary` if markers collide |
| Two LIVE PRIMARY markers on one board | Forbidden | `ambiguous_primary` |
| Archived block selected as PRIMARY | Forbidden | Parser ignores archived; if only archived exists → `missing_primary` |

### §MR.5.1 — Relay freshness predicate (frozen)

Extract from product_order LIVE PRIMARY (product lane):

- `step_id` (from ONE NEXT STEP **ID** / heading)
- `model` (normalized `policy/model-labels.yaml` display label)
- `repo_id` / resolved root
- `tip_hash` = SHA-256 of the canonical paste-ready fence bytes (UTF-8, LF-normalized)

Extract from each `relay: true` member’s product tip (product lane) — the sole block with
`role=relay` **or** `role=product_relay` (§MR.6.1):

- Declared target `(step_id, model, product_order member id)`
- `tip_hash` from the marker (required)

**Pass** iff for every required relay member present locally:

1. Exactly one product tip block exists (`relay` XOR `product_relay`) for the product lane, and
2. `step_id` + `model` match product_order PRIMARY, and
3. `tip_hash` matches product_order PRIMARY paste-fence hash (LF-normalized UTF-8 SHA-256).

**Fail** → exit code **`35`** (`WORKSPACE_RELAY`) on `ok workspace check-next`, with cited paths:

```text
stale_relay: <relay_handover_path> tip=(…) != product_order <po_handover_path> primary=(…)
```

This predicate is exactly what would have caught the 2026-07-27 incident.

### §MR.5.2 — Parallel lanes

- Non-primary constellation lanes MAY have their own LIVE LANE TIP on `owner_member`.
- Workspace `check-next` default scope = **product lane only**.
- `ok workspace check-next --lane <id>` checks that lane’s owner PRIMARY vs any declared lane
  relays (if a future member sets `relay_lanes: […]`; v1 may omit cross-member lane relays —
  freeze allows the flag as optional additive schema, default empty).

---

## §MR.6 — Handover UX contract (frozen)

### §MR.6.1 — Machine markers (required)

Every selectable session block MUST begin with an HTML comment marker **immediately above** its
heading:

| Role | Marker | Heading pattern (frozen) |
| --- | --- | --- |
| LIVE PRIMARY | `<!-- overseer:next role=primary lane=<id> status=live -->` | `## NEXT SESSION — <title> (PRIMARY)` |
| LIVE RELAY (board parked on product tip) | `<!-- overseer:next role=relay lane=<id> status=live product_order=<member_id> tip_hash=sha256:<hex> -->` | `## NEXT SESSION — <title> (RELAY → <member_id> <step_id> <Model>)` |
| PRODUCT RELAY (durable tip; ownership board busy) | `<!-- overseer:next role=product_relay lane=product status=live product_order=<member_id> tip_hash=sha256:<hex> -->` | `## PRODUCT RELAY — <member_id> <step_id> <Model>` |
| LIVE LANE TIP | `<!-- overseer:next role=lane_tip lane=<id> status=live -->` | `## LANE TIP — <title> (LANE: <id>)` |
| ARCHIVED | `<!-- overseer:next role=archived status=archived -->` | `## ARCHIVED SESSION — <title>` |

**Hard rules:**

1. **Exactly one** `## NEXT SESSION —` heading per board (preserves KH1 H2). That block is the
   paste target for *this board’s* next work: `role=primary` (product_order, or ownership/enrichment
   when that member’s own work is next) **or** `role=relay` (board intentionally parked as a
   product tip). Never both NEXT roles on one board.
2. Members with `relay: true` MUST always expose a **fresh product tip** for the product lane via
   **exactly one** of:
   - the LIVE `## NEXT SESSION — … (RELAY → …)` block (`role=relay`), **or**
   - a durable `## PRODUCT RELAY — …` block (`role=product_relay`) when LIVE NEXT is an ownership
     / enrichment PRIMARY.
   Workspace `check-next` reads `role=relay` **or** `role=product_relay` (prefer NEXT relay if
   both somehow present → `ambiguous_primary` fail closed).
3. Parallel lane tips use **`## LANE TIP —`** (not `## NEXT SESSION —`).
4. Archived prompts **MUST NOT** use the heading prefix `## NEXT SESSION —`.  
   `## NEXT SESSION — archived …` is **forbidden** (Knowtation failure mode).
5. Forbidden ambiguous phrases: `PRIMARY relay`, `primary (relay)`, or any `## NEXT SESSION —`
   title containing case-insensitive `archived`.
6. Parsers **only** honor blocks with valid markers; unmarked `## NEXT SESSION —` is legacy:
   warn `unmarked_next`; with `strict_markers: true` (default) → `check-next` fails
   (`ambiguous_primary`).

### §MR.6.2 — Paste-ready fence required fields

Every LIVE PRIMARY / RELAY / PRODUCT RELAY / LANE TIP paste fence MUST include these lines
(substring match). PRODUCT RELAY redirect mode still includes them in a minimal fence (body may
be a one-line “open product_order handover” instruction); `tip_hash` always hashes the
**product_order PRIMARY** paste-fence bytes, not the redirect prose.

```text
Model: <label>
Repo: <absolute or workspace-relative path>
Branch: <branch or "unknown">
Step: <step_id>          # e.g. L-SEAMb, K13b, FINISH-COMPLETE-APPLY-a
Authority: authoritative | relay | product_relay | lane_tip
```

RELAY / PRODUCT RELAY fences either:

- **(a) Redirect** — instruct to open the product_order handover path (no embedded build body), and
  still declare matching `Step` / `Model` / `tip_hash` of the authoritative fence, or
- **(b) Embed** — full paste body whose bytes hash to `tip_hash` matching product_order.

### §MR.6.3 — Template + KH1 deltas (Auto must vendor)

K13b updates:

- `templates/OVERSEER-HANDOVER.template.md` — PRIMARY marker + fence fields; archived example uses
  `## ARCHIVED SESSION —`.
- KH1 checklist gains **H13–H16** (additive; do not weaken H1–H12):

| ID | Check |
| --- | --- |
| **H13** | Exactly one `## NEXT SESSION —`; paired marker is `role=primary` or `role=relay` (not both); PRIMARY headings end with `(PRIMARY)`; RELAY headings match `(RELAY → …)`. |
| **H14** | No heading matching `^## NEXT SESSION —` with case-insensitive `archived` in the title; archived uses `## ARCHIVED SESSION —` only. |
| **H15** | If member `relay: true`: exactly one of `role=relay` (NEXT) or `role=product_relay` (`## PRODUCT RELAY —`) with `tip_hash=sha256:`; `role=lane_tip` uses `## LANE TIP —` only. |
| **H16** | Paste fence of the live NEXT block contains `Model:`, `Repo:`, `Step:`, `Authority:` substrings. |

H2 remains normative: **exactly one** `## NEXT SESSION —` heading. Lane tips and archived
sessions use distinct heading prefixes and do not count against H2.

### §MR.6.4 — Cursor / operator UX rule (vendored)

New always-on rule fragment (Auto vendors via `ok sync`):

> In a multi-root workspace, never treat a non-`product_order` handover as product PRIMARY without
> running `ok workspace status` (or `ok workspace check-next`). The focused editor tab is not
> authority.

Skill text for `/governance-sync` and orchestrator rule: when `workspace:` is configured and the
session advanced product_order PRIMARY, SD-17 multi-repo close-out requires relay refresh or an
explicit incomplete warning (§MR.8).

---

## §MR.7 — CLI / skill surface (frozen)

### §MR.7.1 — Commands

| Command | Writes? | Behavior |
| --- | --- | --- |
| `ok workspace status [--json] [--strict-all]` | No | Constellation map: members, roles, regimes, LIVE PRIMARY per member/lane, relay freshness, lane matrix, `manifest_source`. |
| `ok workspace check-next [--lane ID] [--json]` | No | Exit `0` if product-lane (or `--lane`) relay freshness passes; exit `35` on `stale_relay` / `ambiguous_primary` / `missing_primary`; exit `2` on config/manifest errors; exit `1` on usage. Cite paths. |
| `ok workspace doctor [--json]` | No | Optional diagnostics: per-member Muse≠Git (`muse_sync`) summary, missing optional members, unmarked NEXT warnings, regime mismatch (manifest vs member config). Never merges; never pushes. |
| `ok status --workspace` | No | Alias: run single-repo status **and** attach `workspace` report when configured; **must not** set overall success to imply `workspace.ok` (S9). If `--exit-code`, workspace failure contributes exit `35` without collapsing into “repo healthy”. |

Default for mutating workspace helpers: none in v1 (relays are refreshed by humans/agents editing
docs). Auto MAY add `ok workspace refresh-relays --dry-run` later **only** if a follow-on freeze
adds it; **not** in K13b scope (§MR.13).

### §MR.7.2 — Exit code

| Code | Name | Meaning |
| --- | --- | --- |
| `35` | `WORKSPACE_RELAY` | Stale/missing/ambiguous workspace NEXT / relay integrity failure |

Non-overlap: does not reuse `2`, `3`, `6`, `30`–`34`. Precedence when composed with
`status --exit-code --workspace` (extends `cli/commands/status.py` docstring
`2 > 6 > 3 > 0`):

```text
2 > 6 > 35 > 3 > 0
```

Workspace failure (`35`) never overrides config/substrate/muse_sync/footprint-self-integrity
(`2`) or lock/footprint-digest integrity (`6`). It does override mere footprint drift (`3`) and
clean (`0`), so a green single-repo status cannot hide a stale relay (S9).

### §MR.7.3 — Engine layout (Auto)

```text
tools/workspace/
  __init__.py
  manifest.py          # load/validate workspace.yaml
  next_extract.py      # PRIMARY / RELAY / ARCHIVED / LANE TIP parse
  check_next.py        # freshness predicate
  doctor.py
  types.py
cli/commands/workspace.py
```

Regime rule: for `muse-only` members, doctor/status **must not** invoke `git`/`gh`; Muse adapter
only (S5).

### §MR.7.4 — Skills / rules (Auto vendors on `ok sync`)

| Artifact | Purpose |
| --- | --- |
| `.cursor/rules/workspace-authority.mdc` (+ claude twin if applicable) | Focused-tab is not authority; run workspace status |
| `.cursor/skills/workspace-status/SKILL.md` (+ `.claude/skills/…`) | `/workspace-status` → `ok workspace status` |
| Extend governance-sync skill | Multi-repo SD-17 incomplete until relays refreshed |
| Extend `templates/OVERSEER-HANDOVER.template.md` | Markers + fence fields |

---

## §MR.8 — Relationship to 9A-5 / SD-17 (frozen)

| Concern | Owner | Replaced? |
| --- | --- | --- |
| Single-repo docs ↔ VCS drift | `ok governance-sync` (9A-5) | **No — still required** |
| Handover shape H1–H12 (+ H13–H16) | KH1 / governance-sync D4 path | Additive checks |
| Cross-repo relay freshness | `ok workspace check-next` | **Additional gate** |
| Session-end hygiene | SD-17 | Extended for constellations |

**Composition (frozen):**

1. `ok governance-sync` remains single-repo; default `--dry-run` unchanged; never opens docs-only
   PRs to main; never merges; never pushes staging.
2. When `workspace:` is configured, `governance-sync` **footer** (and `--json` additive key
   `workspace_relay`) MUST report one of:
   - `not_configured` | `ok` | `stale_relay` | `ambiguous_primary` | `missing_member` | `error`
   by invoking the same freshness predicate as `ok workspace check-next` (read-only; no peer
   writes). There is **no** separate “advanced this session” oracle — staleness is sufficient and
   machine-checkable.
3. Preferred close-out workflow when product_order PRIMARY advances:
   - Update product_order handover/roadmap (existing SD-17)
   - Refresh each `relay: true` member’s product tip (`role=relay` or `role=product_relay`)
   - Run `ok workspace check-next` → `0`
4. If relays are not refreshed: local `governance-sync` may still repair *this* repo’s docs↔VCS
   drift, but must surface `workspace_relay: stale_relay` (or worse) and treat multi-repo SD-17
   as **incomplete** until `check-next` exits `0`.
5. Workspace check is a **sibling command**; governance-sync does **not** silently rewrite peer
   repos (no cross-repo writes from one cwd without explicit `-C <peer>` agent action).

Idempotency: `workspace status` / `check-next` / `doctor` are read-only and idempotent.

---

## §MR.9 — Acceptance stories (Auto must prove)

| ID | Story | Expected |
| --- | --- | --- |
| **S1** | product_order advances Thinking→Auto (`{step}a` done → `{step}b` PRIMARY); relay still on Thinking | `ok workspace check-next` **FAIL** exit `35`, cites both handover paths |
| **S2** | Relays refreshed to match step/Model/`tip_hash` | `check-next` **PASS** exit `0` |
| **S3** | Archived headings (`## ARCHIVED SESSION —` or forbidden legacy `## NEXT SESSION — archived`) cannot be selected as PRIMARY | status/check ignore archived; legacy archived form → fail/ambiguous per §MR.6 |
| **S4** | Multi-root: `workspace status` names product_order handover path as authoritative product NEXT | Operator-visible `authoritative_handover` field |
| **S5** | MuseHub `muse-only` member: workspace tools issue no git/gh | Asserted in tests (adapter/regime guard) |
| **S6** | Parallel `## LANE TIP — … (LANE: security)` exists; product PRIMARY unchanged | `check-next` (product) PASS; lane tip listed as non-PRIMARY |
| **S7** | Add `brain` member (`required: false`) without schema redesign | Manifest validates; absent brain → `member_absent`, not error |
| **S8** | External two-repo constellation (app product_order + store ownership relay) | Same commands pass S1/S2 |
| **S9** | Single-repo `ok status` green while relay stale | Must **not** imply workspace OK; `--workspace` / `check-next` still fail |
| **S10** | Ownership board LIVE NEXT is PRIMARY (its own work) + fresh `## PRODUCT RELAY —` matching product_order | `check-next` PASS; status shows ownership PRIMARY ≠ product authoritative path |
| **S11** | Ownership PRIMARY + stale/missing `PRODUCT RELAY` after product_order advanced | `check-next` FAIL exit `35` (same class as S1) |

---

## §MR.10 — Seven-tier test matrix (K13b)

| Tier | Proves |
| --- | --- |
| **unit** | Manifest schema validate/reject; root `${ENV}`/`~` expansion; marker parse (PRIMARY/RELAY/ARCHIVED/LANE TIP); forbidden legacy archived heading detection; `tip_hash` (LF-normalize); freshness predicate true/false; role/lane cardinality rules; regime null only when optional |
| **integration** | Fixture constellation (2–3 temp repos + manifests + handovers): `ok workspace status --json` shape; `check-next` exit `0`/`35`/`2`; `status --workspace` does not claim workspace OK on single-repo green (S9); muse-only member path skips git |
| **e2e** | S1→S2 full cycle on fixtures; S3 archived; S6 lane tip; S7 optional brain absent; S8 two-repo external shape; governance-sync footer key `workspace_relay` when configured |
| **stress** | ≥20 members / ≥10 lanes manifest + large handovers: bounded runtime; stable JSON key order for status; no unbounded recursive workspace walk |
| **data-integrity** | Read-only commands never mutate repos; twice-run identical outputs; tip_hash stable; missing required member fails closed (no guessed paths); override manifest id mismatch → CONFIG `2` |
| **performance** | `check-next` on 5-member fixture completes within documented bound (Auto sets numeric budget, e.g. &lt; 2s wall on fixture SSD); no network calls |
| **security / honesty** | **Fail if any surface claims `workspace.ok: true` (or exit 0 on `check-next`) while a required relay tip disagrees with product_order PRIMARY** (pre-fix replica / differential: mutate relay tip, re-run, assert fail); no secrets in manifest fixtures; no `X-User-Id` / identity fields accepted; injection-shaped headings treated as opaque text; muse-only never shells `git`/`gh`; Tier-3 actions absent from command surface |

---

## §MR.11 — Tier 3 / hard stops (frozen)

K13 **never**:

- Auto-merges `main` (Muse or GitHub) in any member
- Auto-pushes Muse staging
- Flips live capability / posture / env gates
- Commits secrets into workspace manifests or handovers
- Invents cross-repo identity headers or authn (`X-User-Id`, bearer mint, wallet bind) for governance
- Treats GitHub as canonical under `muse+git-mirror` (SD-14)
- Requires network to remotes for basic stale-relay checks
- Writes peer-repo files from `ok workspace *` v1 (read-only)

---

## §MR.12 — Migration / rollout (frozen)

### §MR.12.1 — Activation

| State | Behavior |
| --- | --- |
| No `workspace:` in config and no discoverable manifest | Single-repo only (today); workspace commands exit `2` with “not configured” **or** exit `0` with `workspace: not_configured` — **freeze choice:** exit `0` + `not_configured` for `status`; exit `2` for `check-next` when explicitly asked and not configured |
| `workspace:` present | Gates apply; missing required members fail closed |
| Multi-root Cursor without manifest | Rule text warns; **no** silent mandate (avoid false fails for unrelated multi-root folders) |

### §MR.12.2 — Marker strictness

- Schema field `strict_markers` (bool) on `workspace.yaml`; **default `true`** when key omitted
  (new manifests and dogfood).
- When `strict_markers: true`: unmarked `## NEXT SESSION —` → `check-next` fails
  (`ambiguous_primary` / `unmarked_next`); no heuristic pass.
- When `strict_markers: false` (explicit opt-out for messy migrations only): warn `unmarked_next`
  and allow step/Model heuristic match for relay freshness; still fail on explicit step/Model
  disagreement (S1). Dogfood Scooling+Knowtation MUST use `strict_markers: true`.

### §MR.12.3 — Dogfood order

1. **overseer-kit** — ship K13b + templates/rules/skills; kit’s own `workspace:` remains
   **absent** (kit is not a product constellation member by default).
2. **Scooling + Knowtation** — first live constellation (product_order + ownership relay).
3. **MuseHub** — optional enrichment member (`muse-only`).
4. **Brain** — add as `edge`, `required: false`, when path known.

`ok sync` in consumers pulls template/rule/skill updates; creating `workspace.yaml` is
**operator-gated** (not auto-written by sync).

### §MR.12.4 — Docs-only PR policy

Unchanged: no docs-only PRs to `main` without operator request. Constellation adoption commits stay
on feature branches per member regime.

---

## §MR.13 — Explicit non-goals

- Distributed locking of chats / preventing two Autos from running
- Auto-running Auto builds in peer repos
- Replacing consumer `CROSS-REPO-COORDINATION.md` product ownership tables
- Building Brain firmware or edge runtime
- Hosted multi-repo dashboard (Hosted governance dashboard stays read-only remote glance)
- Cross-repo identity / auth product features
- Making single-repo `ok status` green mean constellation OK
- Silent redesign of 9A-5 single-repo governance-sync
- `ok workspace refresh-relays` write path in K13b (follow-on freeze if needed)
- Cursor-only features unavailable via CLI

---

## §MR.14 — Roadmap proposal + Auto deliverables

### Phase rows (insert into `docs/ROADMAP.md`)

| Phase | Model | Status after this Thinking | Deliverable |
| --- | --- | --- | --- |
| **K13a Freeze multi-repo workspace lanes** | Thinking | **DONE** after freeze-review `pass` | This contract |
| **K13b Multi-repo workspace lanes build** | Auto | **TODO** until K13a `pass` | Implement §MR.4–§MR.8 + §MR.10 |

SD-3 split: never one combined Thinking→Auto prompt.

### K13b Auto deliverable checklist (mechanical)

1. `tools/workspace/` + `cli/commands/workspace.py` + argparse wiring on `ok workspace …`
2. Exit `35` + SPEC §5 row + help text
3. Additive config parse for `workspace:` + manifest loader
4. Template handover markers + KH1 H13–H16 doc amendment note in this freeze (Auto updates KH1
   dogfood checklist implementation if D4 wired; else status/check-next enforce H13–H16)
5. Vendored rule + skills (cursor + claude)
6. `governance-sync` footer additive `workspace_relay` (no peer writes)
7. Fixture pack under `tests/fixtures/workspace/*` covering S1–S9
8. Seven-tier tests §MR.10 all green
9. `/build-verification-review` → `pass` before ROADMAP DONE
10. ROADMAP + HANDOVER updated together; no main merge

---

## §MR.15 — Security / privacy checklist

- [x] No secrets in manifest schema
- [x] No cross-repo identity invention
- [x] Fail closed on missing required roots (no path guessing beyond declared expansion)
- [x] Read-only workspace commands in v1
- [x] Regime-aware (no git in muse-only)
- [x] Honesty tier forbids false `workspace.ok`
- [x] Tier-3 actions absent

---

## §MR.16 — Close-out (this Thinking session)

1. Freeze-review loop → **`pass`**; stamp `review_stamp` via `ok review --freeze`.
2. ROADMAP: K13a → DONE (Thinking); K13b → TODO (Auto).
3. Handover NEXT → K13b Auto paste-ready prompt (only after pass).
4. Feature-branch commit bundling this freeze + ROADMAP + HANDOVER (SD-17).
5. No consumer migrations; no main merge.
