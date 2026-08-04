# Phase KH1 — Handover relay standard (Frozen Thinking Contract)

Status: **Frozen — KH1-r2 → `pass`. Cleared for KH1 close-out and optional D4 Auto.** No Auto build
phase; D4 mechanical wiring ships as an additive patch to `tools/governance_hygiene/` when
prioritized.

```yaml
phase: KH1
outputs:
- id: kh1-handover-relay-standard
  path: docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
  frozen: true
frozen_inputs:
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: handover-template
  path: templates/OVERSEER-HANDOVER.template.md
- id: governance-hygiene-outline
  path: docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: model-labels
  path: policy/model-labels.yaml
- id: k5-freeze-reviewer-contract
  path: docs/archive/phases/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
review_stamp:
  reviewed_at: '2026-07-12T15:16:43Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:a861d192396c13e6cf9f3c7f13e8ea66957ff34fff1f77b96a15da80a02be97b
```

**Downstream edge:** Optional KH1-D4 Auto (governance-sync shape check) and KH1 close-out consume
this contract as ground truth. Per §6, this is a **mandatory reviewed freeze** before those steps
treat the handover shape as normative. KH1 has no `{step}b` Auto build.

**Review record (§6.2):**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor); file+line citations | `findings` (4 MAJOR + 1 MINOR) | **R1-M1–M4 + R1-N1** recorded below; fixed in-tree same session. Kit `muse+git-mirror` config: CLI `review --freeze` blocked by muse `ReadError` (missing `.muse/HEAD`) — checklist run via `overseer --config tests/fixtures/config-git-only.yaml review --freeze … --dry-run` (exit `7`). Semantic review per `/freeze-review-loop`. **Not cleared until KH1-r2.** |
| 2 (2026-07-12) | Independent Freeze-Step Reviewer (Cursor); different posture from r1; file+line citations | **`pass`** | **R1-M1–M4 + R1-N1 confirmed RESOLVED** (citations in r1 ledger). Full regress §KH1.0–§KH1.9: no new contradictions; H6/Branch aligned; §KH1.7 D4 spec vs build split explicit; §KH1.9 gate reminders frozen. CLI checklist `pass` via git-only config workaround; `review_stamp` written. **Cleared for KH1 close-out.** No human escalation. |

### Freeze-review findings ledger (KH1-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | consistency | `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md:100-104`, `:160` | §KH1.2 lists **Branch** as a required ONE NEXT STEP row; §KH1.4 H6 marks Branch optional — Auto/D4 cannot agree on pass/fail. |
| R1-M2 | MAJOR | completeness | `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md:1-30` | Missing §6.1 `frozen: true` declaration block and `frozen_inputs` — ground-truth edge not machine-declared. |
| R1-M3 | MAJOR | completeness | `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md:1-4` | Status claimed **Frozen** without Review record or `reviewed → pass` — contradicts K4/K9a ceremony. |
| R1-M4 | MAJOR | completeness | `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md:227-237`, `:179-186` | §KH1.7 titles matrix "when D4 is implemented" while §KH1.4 already freezes D4 behavior — downstream may defer tests incorrectly. |
| R1-N1 | MINOR | consistency | `docs/archive/phases/PHASE-KH1-HANDOVER-RELAY-STANDARD.md:1` | C8 citation readiness: artifact does not state file+line discipline for review rounds (required by §6.2 / K5). |

**Freeze status:** **reviewed → `pass` (round 2).** Cleared for KH1 close-out (§KH1.6).

**Citation discipline:** every review finding in this artifact **must** include `path:line` citations
so the operator can verify — never trust uncited review output (§6.2 / K5).

---

## Simple summary

Every repo gets **one** handover shape: a living relay file with a **NEXT SESSION** block at the
top, a paste-ready prompt fence, a verified snapshot, a VCS table, hard stops, and a change log.
The kit already vendors that skeleton in `templates/OVERSEER-HANDOVER.template.md`; KH1 freezes the
**required sections and headings** so agents and `governance-sync` can detect when a handover drifts
from the standard.

This repo **dogfoods** the template: `docs/OVERSEER-HANDOVER.md` is the reference instance.
`governance-sync` keeps D1–D3 (VCS truth vs docs); KH1 adds **D4 handover-shape** — a fail-closed
checklist that refuses to treat a malformed handover as aligned.

## Technical summary

KH1 freezes the canonical NEXT SESSION projection rules (docs-first, SD-3 split, mandatory
`Model:` labels per `policy/model-labels.yaml`) and maps them 1:1 to
`templates/OVERSEER-HANDOVER.template.md`. Consumer repos receive the template via `overseer init`;
the kit's own handover is the dogfood ground truth.

**D4 (new):** parse the handover as a **structural claim** (like D1/D3 parse doc claims) and
verify against the frozen H-checklist below. D4 does **not** infer VCS state; it only checks that
the relay file matches the vendored shape. On D4 `drifted`, `governance-sync` reports shape
violations and **refuses** `fully_aligned` even when D1–D3 are aligned (fail-closed on relay UX).

---

## §KH1.0 — Scope

**In scope (frozen):**

- Canonical section order and required headings (§KH1.1).
- NEXT SESSION block fields and paste-ready prompt fence rules (§KH1.2).
- Anchor names for governance-sync section replacement (§KH1.3).
- D4 handover-shape checklist H1–H12 (§KH1.4).
- Dogfood rules for this repo (§KH1.5).
- KH1 close-out obligations (§KH1.6) — executed only when marking KH1 **DONE**.

**Out of scope:**

- Rewriting `CROSS-REPO-COORDINATION.template.md` snapshot prose (legacy shape stays as historical
  reference; living handover uses `OVERSEER-HANDOVER.template.md`).
- Track P product work (seeded only at KH1 close-out per ROADMAP).
- Auto-regeneration of NEXT SESSION body from roadmap (human/docs-first authorship unchanged).

---

## §KH1.1 — Canonical document shape (frozen)

The living handover file **must** contain these sections in this order (content between sections may
include `---` horizontal rules and repo-specific tables):

| # | Section | Required heading pattern | Agent-owned? |
| --- | --- | --- | --- |
| 1 | Title | `# <handover_title> — <repo.name>` | Human |
| 2 | Intro | One paragraph: living relay + paste instruction | Human |
| 3 | **NEXT SESSION** | `## NEXT SESSION — <title>` | Human (docs-first) |
| 4 | What landed | `### What just landed` + 2-col table | Human |
| 5 | One next step | `### THE ONE NEXT STEP — **Model: <label>**` | Human |
| 6 | Paste prompt | `### Paste-ready prompt — <phase-id>` + fenced block | Human |
| 7 | **Verified snapshot** | `## Verified snapshot` | Human (+ sync may patch drift row) |
| 8 | **VCS table** | `## VCS (verified <YYYY-MM-DD>)` | Agent (governance-sync) |
| 9 | **Hard stops** | `## Hard stops (unchanged)` | Human (template boilerplate) |
| 10 | **Change log** | `## Change log` | Human (+ sync appends) |
| 11 | Regeneration rules | `## Handover regeneration rules (SD-3, SD-17)` | Template boilerplate |

**Not a required top-level section:** a separate `## Shared context` block. Shared context belongs
**inside** the paste-ready prompt fence (or is omitted when the fence is self-contained). Kit
dogfood may retain a supplementary shared-context table **below** the NEXT SESSION `---` divider
for operator convenience; D4 does not require it.

**Verified snapshot content** is repo-specific (kit dogfood carries phase rows; consumers may be
minimal). D4 requires the heading and a markdown table — not a fixed row list.

---

## §KH1.2 — NEXT SESSION block (frozen)

### Header lines (required immediately under `## NEXT SESSION`)

```markdown
**Date:** <YYYY-MM-DD>
**Current position:** <one-line status>
**Model:** <Thinking | Auto | Thinking → Auto | Operator + Auto>
```

Rules:

- `**Model:**` must use exactly one label from `policy/model-labels.yaml` `display` values.
- `Current position` names the last **DONE** slice and the next queue row when applicable.

### THE ONE NEXT STEP table (required rows)

| Row key | Required |
| --- | --- |
| **ID** | Phase id (e.g. `KH1`, `K9b`, `P0`) |
| **Branch** | `` `feat/{slug}` `` pattern or explicit branch name |
| **Repo** | `` **<repo.name>** `` |
| **Read first** | At minimum `` `{{docs.roadmap_path}}`; `{{docs.handover_path}}` `` (resolved paths in filled doc) |
| **Hard stops** | Session guardrails (no secrets; Tier-3 gates; etc.) |

Legacy single-cell `**Model**` row **without** the `### THE ONE NEXT STEP — **Model: …**` heading
is **shape drift** (H6).

### Paste-ready prompt fence (required)

- Heading: `### Paste-ready prompt — <phase-id>` where `<phase-id>` matches THE ONE NEXT STEP **ID**.
- Fence: triple backticks; language tag optional (`text` or none).
- Fence body **must** include a `Model:` line (SD-3 / `policy/model-labels.yaml` rule).
- For `Thinking → Auto` queue rows with incomplete split: emit `{step}a` **or** `{step}b` only —
  never a combined prompt (SD-3).
- Auto steps (`{step}b` or `Model: Auto`) must include the build-verification reminder from the
  template when the phase adds code.

---

## §KH1.3 — Governance-sync anchors (frozen)

These anchor names match `tools/governance_hygiene/anchors.py` `HANDOVER_ANCHORS`:

| Anchor | Section |
| --- | --- |
| `next-session` | Full `## NEXT SESSION` through its closing `---` |
| `done-recently` | `### What just landed` table body |
| `paste-ready-prompt` | `### Paste-ready prompt` fenced block |
| `verified-snapshot` | `## Verified snapshot` table |
| `vcs-table` | `## VCS (verified …)` table |
| `change-log` | `## Change log` entries |

KH1 dogfood handover **must** include `vcs-table` and `change-log` anchors so D1 patching and sync
append paths work. `next-session` and `paste-ready-prompt` anchors are **recommended**; D4 H12
checks for their presence in kit dogfood only.

Marker format (unchanged from 9A-5):

```html
<!-- overseer:anchor:<name> -->
…body…
<!-- /overseer:anchor:<name> -->
```

---

## §KH1.4 — D4 handover-shape checklist (frozen)

D4 compares the handover file against these rules. Each rule yields `pass | fail`; any `fail` →
D4 state `drifted`. Parse errors → `unreadable` (fail-closed).

| ID | Check |
| --- | --- |
| **H1** | Title matches `# .+ — .+` (handover title + repo name). |
| **H2** | Exactly one `## NEXT SESSION —` heading. |
| **H3** | NEXT block contains `**Date:**`, `**Current position:**`, `**Model:**` lines. |
| **H4** | `### What just landed` exists with a 2-column markdown table (`Slice`, `Deliverable`). |
| **H5** | `### THE ONE NEXT STEP — **Model:` heading exists (model in heading, not only in table). |
| **H6** | ONE NEXT STEP table contains rows **ID**, **Branch**, **Repo**, **Read first**, **Hard stops**. |
| **H7** | `### Paste-ready prompt —` heading exists with a fenced code block after it. |
| **H8** | Paste fence content includes `Model:` substring. |
| **H9** | `## Verified snapshot` with markdown table present. |
| **H10** | `## VCS (verified` table present (agent-maintained). |
| **H11** | `## Hard stops` and `## Change log` headings present. |
| **H12** | `## Handover regeneration rules` present (template tail). |

### Additive multi-repo checks (K13 — H13–H17)

These do **not** weaken H1–H12. Workspace tools / doctor enforce them when
`workspace:` is configured (see `docs/archive/phases/MULTI-REPO-WORKSPACE-LANES-FREEZE.md` §MR.6).

| ID | Check |
| --- | --- |
| **H13** | Exactly one `## NEXT SESSION —`; paired marker is `role=primary` or `role=relay` (not both); PRIMARY headings end with `(PRIMARY)`; RELAY headings match `(RELAY → …)`. |
| **H14** | No heading matching `^## NEXT SESSION —` with case-insensitive `archived` in the title; archived uses `## ARCHIVED SESSION —` only. |
| **H15** | If member `relay: true`: exactly one of `role=relay` (NEXT) or `role=product_relay` (`## PRODUCT RELAY —`) with `tip_hash=sha256:`; `role=lane_tip` uses `## LANE TIP —` only. |
| **H16** | Paste fence of the live NEXT block contains `Model:`, `Repo:`, `Step:`, `Authority:` substrings. |
| **H17** | When `workspace:` is configured and `strict_board_names` is true (default): handover basename matches `{REPO_SLUG}-OVERSEER-HANDOVER.md` or `{REPO_SLUG}-{LANE}-…` pattern; roadmap basename matches `{REPO_SLUG}-ROADMAP.md` (or lane variant); `handover_title` contains a non-empty repo/lane label distinct from the generic string `Overseer Handover` alone. |

### D4 integration (governance-sync)

| Field | Value |
| --- | --- |
| Drift id | `d4_handover_shape` |
| Compares | Handover text vs H1–H12 |
| Drift condition | any H rule `fail` |
| On drift | Emit `D4=drifted` + list failed H ids; **block** `DriftReport.fully_aligned` |
| Patch behavior | **No auto-patch** — shape drift requires human regeneration (docs-first) |
| Regimes | All (`git-only`, `muse+git-mirror`, `muse-only`) |

**CLI surface (additive, when implemented):**

```bash
overseer governance-sync [--dry-run]   # reports D4 alongside D1–D3
```

Optional future flag `--check-handover-shape` (default on) may be added; default behavior is D4
always evaluated when handover file is readable.

### Standalone validator (optional)

```bash
overseer handover-validate [--json]    # read-only H1–H12; exit 0 pass, 2 fail
```

Not required for KH1 DONE; spec-only is sufficient for the Thinking freeze.

---

## §KH1.5 — Kit dogfood (this repo)

| Item | Ground truth |
| --- | --- |
| Template | `templates/OVERSEER-HANDOVER.template.md` |
| Living instance | `docs/OVERSEER-HANDOVER.md` |
| Config | `.overseer/config.yaml` → `docs.handover: OVERSEER-HANDOVER.md` |
| Title token | `Overseer Handover — overseer-kit` until branding close-out |
| Expanded snapshot | Kit phase rows allowed; template minimal table is the consumer default |
| **Freeze review CLI** | When `.muse/HEAD` is absent on the dev tree, `overseer review --freeze` under
  `muse+git-mirror` config fails closed (`ReadError`). Dogfood workaround until operator `muse init`:
  `overseer --config tests/fixtures/config-git-only.yaml review --freeze <artifact> [--dry-run]`.
  Semantic `/freeze-review-loop` remains authoritative when CLI is blocked. |

Dogfood handover after KH1 Thinking alignment **must** pass H1–H12.

---

## §KH1.6 — KH1 close-out (execute only when marking DONE)

Do **not** execute until the operator marks KH1 **DONE**:

1. **Branding lock** — set public name **🆗 Overseer Kit** in `templates/OVERSEER-HANDOVER.template.md`
   and any template tokens that surface repo display name on landing/docs (`repo.name` token guidance
   in `templates/README.md` if needed).
2. **Track P seed** — add one-line **Track P** row to `docs/ROADMAP.md` (`P0` = spec freeze only; no
   code). Do **not** add Track P before KH1 merges.
3. **Flip NEXT SESSION** — handover NEXT becomes **Track P / P0 (freeze)** with paste-ready prompt.
4. **Governance sync** — ROADMAP KH1 row → **DONE**; handover change log entry; both docs in same
   commit (SD-17).

---

## §KH1.7 — Seven-tier test matrix (D4 implementation build)

Applies when an Auto build wires §KH1.4 D4 into `tools/governance_hygiene/`. The **D4 spec** in
§KH1.4 is frozen in this Thinking contract; only the code + tests are deferred.

| Tier | Proves |
| --- | --- |
| **unit** | Each H rule true/false on fixture strings; D4 `drifted`/`aligned` aggregation |
| **integration** | `governance-sync --dry-run` emits D4 on malformed fixture handover |
| **e2e** | Dogfood handover passes D4 on clean tree |
| **stress** | Large snapshot tables still parse; H checks bounded time |
| **data-integrity** | D4 idempotent; no handover mutation on D4-only drift |
| **performance** | H1–H12 scan completes &lt; 100ms on kit handover size |
| **security** | Validator rejects path escape; no shell execution on handover content |

---

## §KH1.9 — Governance gate reminders (frozen; implementation deferred)

Freeze review and build verification are **mandatory** but today **opt-in to invoke** (skills +
discipline). KH1 freezes **reminder surfaces** so gates cannot silently fall through the cracks.
Operators may **acknowledge and ignore** a reminder; the kit must **never** treat silence as `pass`.

### Gates

| Gate | When | Tool | Blocks without `pass` |
| --- | --- | --- | --- |
| **Freeze review** | After Thinking freeze (`{step}a`); before Auto build | `/freeze-review-loop`, `overseer review --freeze` | Auto build on `frozen: true` consumer |
| **Build verification** | After Auto build (`{step}b`); before ROADMAP **DONE** | `/build-verification-review` | Phase **DONE** row (SD-3 honesty) |

### Settings (`.overseer/config.yaml` — additive, KH1+)

```yaml
governance_gates:
  remind: true                    # default true; false = suppress reminders (logged ignore)
  freeze_review:
    required_before_auto: true
  build_verification:
    required_before_done: true
  surfaces:
    - status                       # overseer status — pending gates section
    - governance-sync              # dry-run + write plan footer
    - handover-paste               # NEXT paste-ready prompt checklist
```

**`remind: false`** is Tier 2 (recommend-and-confirm once; record in Standing Decisions). It does
**not** disable the gate — only the nudges.

### Reminder surfaces (frozen)

| Surface | Behavior |
| --- | --- |
| **`overseer status`** | Emit **Pending governance gates** when: (a) a `frozen: true` artifact in the
  active roadmap slice lacks `reviewed → pass` in its Review record; (b) a queue row is **Auto** /
  `{step}b` **WIP** or claiming **DONE** without a recorded build-verification `pass`. Exit `0`
  still; reminders are stderr/human section, not fail-closed exit (unless future `--strict-gates`). |
| **`governance-sync --dry-run`** | Append gate reminders to the plan footer (alongside D1–D4). |
| **Handover paste prompt** | Every Thinking-freeze and Auto-close paste block includes a **Governance
  gates** checklist (freeze review / build verification) with explicit invoke commands. |
| **ROADMAP Definition of Done** | Already states both gates; reminders echo this. |

### Better than full automation (operator recommendation)

| Approach | Verdict | Rationale |
| --- | --- | --- |
| **Remind + acknowledge** (this spec) | **CHOSEN** | Works offline; no false `pass`; respects Tier 2 ignore; matches K5 Automation degrade path. |
| **Hard CI block only** | Secondary | Add later: PR check on `docs/archive/phases/PHASE-*.md` without review stamp — needs API or self-hosted runner. |
| **Silent auto-review** | **REJECTED** | Violates thinking-model independence; risks shallow checklist-only pass. |

Implementation ships as a small additive CLI extension (read-only gate scan); not required for KH1
Thinking **DONE**, but spec is frozen here for the next Auto slice.

---

## §KH1.8 — Cross-references

- `templates/OVERSEER-HANDOVER.template.md` — vendored skeleton
- `docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — D1–D3 (compose, do not fork)
- `policy/model-labels.yaml` — allowed `Model:` labels + SD-3 split rules
- `tools/governance_hygiene/anchors.py` — anchor names
- `docs/ROADMAP.md` — KH1 queue row + close-out Track P gate
