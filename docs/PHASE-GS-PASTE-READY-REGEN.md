# Phase GS-PASTE — Paste-ready / NEXT regeneration for governance-sync

Status: **Reviewed → `pass` (GSP-r3).** GS-PASTE-a is **spec-only** and now frozen; no code
lands in this phase. GS-PASTE-b (Auto) is cleared to build mechanically against this contract.

```yaml
phase: GS-PASTE
outputs:
- id: gs-paste-ready-regen
  path: docs/PHASE-GS-PASTE-READY-REGEN.md
  frozen: true
frozen_inputs:
- id: phase-9a5-writes
  path: docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: kh1-relay-standard
  path: docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: model-labels
  path: policy/model-labels.yaml
- id: governance-hygiene-patch
  path: tools/governance_hygiene/patch.py
- id: governance-hygiene-anchors
  path: tools/governance_hygiene/anchors.py
- id: governance-hygiene-engine
  path: tools/governance_hygiene/engine.py
- id: governance-hygiene-parse
  path: tools/governance_hygiene/parse.py
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: test-tiers
  path: policy/test-tiers.yaml
review_stamp:
  reviewed_at: '2026-07-30T19:13:40Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:123c2e687fd62eac76af880d61b4bf495f1c185b9b2566b892c293373eacb648
```

**Downstream edge:** GS-PASTE-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze). It closes the permanent gap left when 9A-5 §4 promised
templated regeneration of the handover **NEXT SESSION** heading + **paste-ready prompt** block,
anchors `next-session` / `paste-ready-prompt` were declared in `tools/governance_hygiene/anchors.py`,
and KH1 deferred auto-regeneration — while `build_handover_patches` still never patches those
anchors (`tools/governance_hygiene/patch.py`).

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| GSP-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist dry-run clean. Semantic: **R1-M1–M3** below — fixed in-tree same session. |
| GSP-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** missing-anchor region bounds underspecified for nested paste-inside-NEXT dogfood — fixed in §GSP.5.3. |
| GSP-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist dry-run clean (0 findings). Semantic re-read: R1-M1–M3 + R2-M1 RESOLVED; sole surface = `governance-sync`; fail-closed ambiguity; git-only/no-Muse; §GSP.10 matrix + DoD present; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §GSP.0 — Simple summary

After a roadmap queue moves forward, the handover’s “what’s next” box and the copy-paste prompt
are supposed to match that queue. Today the sync tool updates other handover sections (VCS table,
done-recently, snapshot, change log) but **leaves the next-step box and paste prompt alone**, so
humans or agents rewrite them by hand — or leave them stale.

This phase freezes how the existing sync command regenerates those two sections from the roadmap
queue: only through `ok governance-sync` (dry-run plans; apply writes), never by inventing a next
step, and **stop without guessing** when the next step is ambiguous. The feature must work on plain
GitHub-only fixtures with **no Muse**.

**Technical summary:** extend `tools/governance_hygiene/` so `build_handover_patches` (invoked only
from `run_governance_sync`) regenerates the `next-session` and `paste-ready-prompt` anchor bodies
from an **unambiguous** open build-queue row (after D3 reconciliation). Ambiguity →
`next_regen: human_authorship_required`; other §4 patches may still proceed. Dry-run emits the
planned regen and writes nothing to docs. `git-only` fixtures prove zero Muse invocation. Compose
with 9A-5 §4/§7, KH1 H1–H12 / H16 fields, and `policy/model-labels.yaml` `handover_regeneration`.

---

## §GSP.1 — Scope

**In scope (GS-PASTE-a freezes; GS-PASTE-b implements):**

1. Regeneration of handover anchors `next-session` and `paste-ready-prompt` via
   `ok governance-sync` / `ok governance-sync --dry-run` only (§GSP.3–§GSP.5).
2. Unambiguous-NEXT selector + fail-closed ambiguity rule (§GSP.4).
3. SD-3 / `policy/model-labels.yaml` paste emission rules (§GSP.5).
4. Anchor presence / insertion using existing `replace_anchor_block` (§GSP.6).
5. Dry-run plan surface + apply path parity with existing PatchPlan (§GSP.7).
6. `git-only` baseline: feature green without Muse (§GSP.8).
7. Seven-tier matrix for GS-PASTE-b (§GSP.10) and Definition of Done (§GSP.11).

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected |
| --- | --- |
| **Separate CLI / slash command for NEXT regen** | Single behavior surface is `governance-sync` (9A-5 §1). |
| **Inventing phases, Model labels, or deliverables not in the queue** | Docs-first; queue is durable truth (SD-3 / SD-17). |
| **Free-form rewrite of prose outside the two anchors** | 9A-5 §4 templated section replacement only. |
| **Auto-resolving multi-track / idle / Operator-choice boards** | Ambiguous → human authorship (fail-closed). |
| **Requiring Muse for the feature** | Regime guardrail: no MuseHub-only baseline (`docs/ROADMAP.md` regime table). |
| **Weakening D4 H1–H12 or skipping D1–D3** | Compose; regenerated bytes must still satisfy KH1 shape. |
| **Opening docs-only PRs to `main` / staging / live flips** | SD-11 / Tier 3 unchanged. |
| **GS-PASTE-b Auto implementation in the Thinking phase** | SD-3 split. |
| **Live consumer `ok sync` / re-init** | Operator-gated; out of kit Auto. |
| **Amending KH1 H-checklist IDs** | Additive regen only; H rules stay frozen. |

**KH1 supersession (narrow):** `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` §KH1.0 listed
“Auto-regeneration of NEXT SESSION body from roadmap” as out of scope. **This phase supersedes
that non-goal for the two named anchors only.** All other KH1 rules remain in force.

---

## §GSP.2 — Verified gap (do not redesign)

| Fact | Evidence |
| --- | --- |
| 9A-5 §4 lists **NEXT SESSION heading + paste-ready prompt block** among handover writes | `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` lines 160–171 |
| Ambiguous NEXT → patch everything else + flag for human authorship | same §4 lines 168–171; §7 lines 233–234 |
| Anchors `next-session` + `paste-ready-prompt` declared | `tools/governance_hygiene/anchors.py` lines 19–27, 62–63 |
| `build_handover_patches` patches vcs / done-recently / snapshot / change-log only — **never** next-session or paste-ready | `tools/governance_hygiene/patch.py` lines 16–47 |
| `extract_paste_ready_block` exists but is unused by the patch path | `tools/governance_hygiene/patch.py` lines 230–233 |
| Glance uses first open row when multiple exist (not fail-closed) | `tools/governance_hygiene/patch.py` lines 206–217 |
| KH1 deferred NEXT auto-regen | `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` §KH1.0 line 104 |
| Model / split rules for paste emission | `policy/model-labels.yaml` `handover_regeneration` + `rule` |

---

## §GSP.3 — HOW (sole surface)

**Decision: regenerate only inside `ok governance-sync` (default dry-run + explicit apply/write).**

| Surface | Behavior |
| --- | --- |
| `ok governance-sync` (default dry-run) | Run R1–R5 + D1–D3 (+ D4 as today). Plan includes whether `next-session` / `paste-ready-prompt` **would** regenerate or `human_authorship_required`. **Docs bytes unchanged** (GFG marker carve-out unchanged). |
| `ok governance-sync --write` / apply path | Same plan; on apply, `replace_anchor_block` for those two anchors when regen is unambiguous; feature-branch commit bundle rule unchanged (9A-5 §6). |
| Any other command | **Must not** regenerate NEXT / paste. |

No new subcommand. No Automation change required for GS-PASTE (GFG session-end already runs dry-run).

---

## §GSP.4 — Unambiguous NEXT selector (fail-closed)

### §GSP.4.1 — Open-row set

After D3 reconciliation of roadmap text (same patched roadmap used for glance), parse queue rows
via existing `parse_queue_rows`.

**Open row** = `normalize_status(row.status)` ∈ `{TODO, NEXT, WIP}`.

### §GSP.4.2 — Unambiguous rule (frozen)

| Condition | Result |
| --- | --- |
| Exactly **one** open row | **Unambiguous** — regenerate from that row |
| Zero open rows | **Ambiguous** — `human_authorship_required` |
| Two or more open rows | **Ambiguous** — `human_authorship_required` |
| Open row’s Model cell is empty or not exactly one `policy/model-labels.yaml` `display` value | **Ambiguous** — `human_authorship_required` |
| `Thinking → Auto` split state undeterminable (§GSP.5.2) | **Ambiguous** — `human_authorship_required` |

**Frozen amendment to glance consistency:** when open-row count ≠ 1, `_render_next_step_glance`
MUST emit the existing “No unambiguous NEXT row — operator authorship required.” message (today
it only does so for zero rows and otherwise picks `next_rows[0]` — `patch.py` lines 206–217).
GS-PASTE-b updates that function to match this fail-closed rule.

### §GSP.4.3 — On ambiguity

1. Do **not** replace `next-session` or `paste-ready-prompt` bodies.
2. Other §4 patches (vcs-table, done-recently, verified-snapshot, change-log, queue, glance) proceed
   per existing rules.
3. Emit a plan/result message including exact token:
   `next_regen: human_authorship_required` plus reason
   (`zero_open_rows` | `multiple_open_rows` | `invalid_model_label` | `split_undetermined`).
4. Do **not** invent a NEXT from Verified snapshot prose, change-log, or chat memory.

---

## §GSP.5 — Regenerated content contract

### §GSP.5.1 — Inputs (docs-first)

| Field | Source |
| --- | --- |
| Phase id / title | Unambiguous open queue row `phase_label` (strip markdown bold for ID token via `phase_tokens`) |
| Model label | Queue row `model` cell (must match `policy/model-labels.yaml` `display`) |
| Deliverable summary | Queue row `deliverable` cell |
| Date | Sync date (`date.today()` / injected `sync_date` — same as VCS table) |
| Current position | One line: last DONE/MERGED queue row phase token (if any) + `→` + open row phase token |
| Branch | From config `vcs.git.feature_branch_pattern` with slug derived from phase id (lowercase, non-alnum → `-`); if regime has no git feature pattern, omit Branch row value as `` `unknown` `` |
| Repo | `config.repo.name` |
| Read first | Config-resolved `docs.roadmap` + `docs.handover` paths |
| Hard stops | Frozen boilerplate: no merge to main without Tier 3; no secrets; no live posture flips; no inventing NEXT |

**What just landed table:** regenerate **exactly one** data row from the most recent DONE/MERGED
queue row (by table order, last matching). If none, keep a single placeholder row
`| _(none)_ | Queue has no DONE/MERGED row yet |` — never fabricate PR titles from R4 inside the
NEXT block (R4 remains the done-recently anchor path).

### §GSP.5.2 — SD-3 / Thinking → Auto split

**Authority conflict (frozen resolution):** 9A-5 §4 lines 167–169 say the agent emits
`{step}a` and `{step}b` as **two** blocks. `policy/model-labels.yaml` `handover_regeneration`
requires `emit step_a_only` / `emit step_b_only` / `emit one prompt`, and KH1 / SD-3 forbid a
combined Thinking+Auto paste. **CHOSEN for GS-PASTE:** `policy/model-labels.yaml` wins — one
regen emits **at most one** paste fence (`{step}a` **or** `{step}b` **or** single-model). The
9A-5 “two blocks” phrase means **sequential sessions across runs** as the queue advances, not
two fences in one regeneration.

| Queue Model | Emission |
| --- | --- |
| `Thinking` / `Auto` / `Operator + Auto` | **One** paste-ready fence (`single_model`) |
| `Thinking → Auto` | Emit **`{step}a` only** or **`{step}b` only** — never combined |

**Split detector (frozen, deterministic):**

1. Let `step_id` = first `phase_tokens` entry with spaces/`/` normalized to a compact id
   (e.g. `GS-PASTE` from `**GS-PASTE**` / `**GS-PASTE-a …**` — use the row’s primary token).
2. Locate freeze artifact path candidates under repo-root `docs/` matching
   `PHASE-*{token}*.md` case-insensitive (basename glob only; no recursive escape), **or** a
   repo-relative path already cited in the deliverable cell that resolves under `docs/` and
   exists on disk.
3. **Emit `{step}a` (Thinking)** when no candidate exists **or** no candidate has
   `review_stamp.verdict: pass` (YAML freeze block) / Review record verdict `pass`.
4. **Emit `{step}b` (Auto)** when at least one candidate has reviewed → `pass`, no candidate
   contradicts with a non-pass stamp, and the open row status is still open
   (`TODO`/`NEXT`/`WIP`).
5. If multiple freeze artifacts disagree on pass/fail → **`split_undetermined`** (ambiguous).

Paste fence **must** include substrings: `Model:`, `Repo:`, `Step:`, `Authority:` (KH1 H16 when
workspace configured; always emit for kit baseline so H16 stays green where applicable).

Auto / `{step}b` fences **must** include the build-verification reminder lines from
`templates/OVERSEER-HANDOVER.template.md` (Governance gates checklist).

### §GSP.5.3 — Anchor body shapes (frozen)

**`next-session` body** (inside markers) MUST contain, in order:

1. `## NEXT SESSION — <title>`
2. `**Date:**`, `**Current position:**`, `**Model:**` lines (§KH1.2)
3. `### What just landed` + 2-column table
4. `### THE ONE NEXT STEP — **Model: <label>**`
5. ONE NEXT STEP table with rows **ID**, **Branch**, **Repo**, **Read first**, **Hard stops** (H6)

It MUST **not** embed the fenced paste body (paste lives in the sibling anchor).

**`paste-ready-prompt` body** MUST contain:

1. `### Paste-ready prompt — <phase-id>`
2. One fenced code block whose body includes `Model:` matching the emitted step

Byte-stable for identical inputs (9A-5 §7 idempotency).

**Missing-anchor migration (frozen):** when markers are absent, `replace_anchor_block` fallback
must not swallow the sibling section. Bound the would-be `next-session` region from
`## NEXT SESSION` through the line **before** the first `### Paste-ready prompt` (or before the
`---` that precedes `## Verified snapshot` if no paste heading exists). Bound
`paste-ready-prompt` from the first `### Paste-ready prompt` through the closing fence of that
block’s first fenced code region. After the first successful regen, both named markers MUST be
present so subsequent runs are pure in-marker replacement.

### §GSP.5.4 — Multi-repo / PRIMARY markers

When regenerating, preserve an existing `<!-- overseer:next role=… -->` marker line immediately
above `## NEXT SESSION` if present; do not invent `role=relay` / `tip_hash` / workspace ownership.
If the marker is absent, insert `<!-- overseer:next role=primary lane=product status=live -->`
only when `workspace:` is **not** configured; when `workspace:` is configured and marker absent →
treat as ambiguous (`human_authorship_required`) rather than guessing PRIMARY vs RELAY.

---

## §GSP.6 — Patch wiring

### §GSP.6.1 — Signature / call-order (frozen)

Today `build_handover_patches` takes only handover text + reads/drift
(`tools/governance_hygiene/patch.py` lines 16–23) and `engine.py` calls it **before**
`build_roadmap_patches` (lines 330–340). NEXT regen needs **(a)** `OverseerConfig` for repo /
doc paths / feature-branch pattern and **(b)** the **D3-reconciled** roadmap text.

**Frozen call order in `run_governance_sync` plan builder:**

1. `build_roadmap_patches(...)` first (so queue rows reflect D3 merges).
2. `build_handover_patches(handover_text, reads, drift, *, config, roadmap_text=patched_roadmap, …)`
   — additive kwargs; existing positional args preserved for test churn control where possible.
3. NEXT/paste selection **must** use `roadmap_text` from step 1, never the pre-patch roadmap.

**Frozen signature additions** on `build_handover_patches`:

| Param | Required | Role |
| --- | --- | --- |
| `config: OverseerConfig` | yes | repo name, docs paths, `feature_branch_pattern`, `workspace` presence |
| `roadmap_text: str` | yes | D3-reconciled roadmap for §GSP.4 selector |
| `repo_root: Path` | yes | Confine freeze-artifact discovery under `docs/` |

### §GSP.6.2 — Modules

| Change | Location |
| --- | --- |
| Add `select_unambiguous_next_row(roadmap_text) -> tuple[QueueRow \| None, str \| None]` | `tools/governance_hygiene/parse.py` or new `tools/governance_hygiene/next_regen.py` |
| Add `render_next_session(...)` + `render_paste_ready(...)` | `next_regen.py` (preferred) or `patch.py` |
| Wire regen inside `build_handover_patches` — order frozen: after done-recently/snapshot, **before** change-log append so the change-log line can mention `next_regen=…` | `tools/governance_hygiene/patch.py` |
| Align glance fail-closed with §GSP.4.2 | `tools/governance_hygiene/patch.py` `_render_next_step_glance` |
| Reorder engine plan builder per §GSP.6.1; surface `next_regen` in dry-run / JSON messages | `tools/governance_hygiene/engine.py` (additive message; no new exit code) |
| Use `replace_anchor_block` for both anchors (insert fallback already exists) | `tools/governance_hygiene/anchors.py` (no API change required) |

**Change-log line (additive fragment):** include `next_regen=regenerated` or
`next_regen=human_authorship_required:<reason>` in the governance-sync change-log summary.

**Exit codes:** unchanged. Ambiguity is not a hard failure of the sync run (other patches may
succeed); it is a fail-closed **refusal to invent NEXT**.

### Freeze-review findings ledger (GSP-r1)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | consistency | `docs/PHASE-GS-PASTE-READY-REGEN.md` §GSP.5.2 (pre-fix) vs `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md:167-169` vs `policy/model-labels.yaml` `handover_regeneration` | 9A-5 “two blocks” vs model-labels a_only/b_only unresolved — Auto could emit combined fences. |
| R1-M2 | MAJOR | completeness | `tools/governance_hygiene/patch.py:16-23`, `tools/governance_hygiene/engine.py:330-340`, freeze §GSP.5.1 / §GSP.6 (pre-fix) | Regen needs `config` + D3-reconciled `roadmap_text`, but freeze did not specify signature/call-order changes; engine currently patches handover before roadmap. |
| R1-M3 | MINOR | completeness | freeze §GSP.5.2 step 2 (pre-fix) | Freeze-artifact glob must state repo-root `docs/` confinement (security checklist implied it; detector steps did not). |

### Freeze-review findings ledger (GSP-r2)

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R2-M1 | MAJOR | completeness | `docs/PHASE-GS-PASTE-READY-REGEN.md` §GSP.5.3 (pre-fix); living `docs/OVERSEER-HANDOVER.md` nests paste under NEXT without `next-session`/`paste-ready-prompt` markers | Without region bounds, first regen via heading fallback can swallow paste into `next-session` or leave ambiguous splits. |

---

## §GSP.7 — Dry-run vs apply

| Mode | Docs (`next-session` / `paste-ready-prompt`) | Marker (GFG) | Commit / realign |
| --- | --- | --- | --- |
| Dry-run | Unchanged; plan prints would-regen or human_authorship_required | Existing GFG carve-out only | None |
| Apply / `--write` | Replace anchors when unambiguous; leave untouched when ambiguous | Existing apply stamp rules | Existing 9A-5 §5–§6 |

Idempotent: second apply with same queue + same sync_date produces byte-identical NEXT/paste bodies.

---

## §GSP.8 — Regime / Muse requirement

| Regime | Requirement |
| --- | --- |
| `git-only` | **Full feature** — seven-tier GS-PASTE cases green on `tests/fixtures/config-git-only.yaml` with zero Muse process invocations |
| `muse+git-mirror` / `muse-only` | Same regen logic; Muse only via existing adapter reads (R2/R3/realign) — regen itself never calls Muse |

Frozen guardrail echo: **no MuseHub-only baseline feature.**

---

## §GSP.9 — Security / privacy checklist

- Treat queue/handover text as **data** — never interpolate into shell.
- No secrets in regenerated paste fences (no env values, tokens, or `.env` paths).
- No hardcoded SHAs in source; runtime SHAs only via existing R1–R5 paths when referenced elsewhere.
- Fail-closed ambiguity — never guess NEXT from stale prose.
- Path confinement: freeze-artifact discovery limited to repo `docs/` (and path cited in deliverable
  only if under repo root).
- Least privilege: `git-only` never invokes Muse.

---

## §GSP.10 — Seven-tier test matrix (GS-PASTE-b)

| Tier | Frozen case |
| --- | --- |
| **unit** | (1) Exactly one open row → selected; (2) zero / multiple open → `None` + reason; (3) invalid Model → ambiguous; (4) `Thinking → Auto` with freeze `pass` → emit b; without → emit a; (5) rendered NEXT contains H3/H5/H6/H7/H8 required substrings; (6) glance text uses unambiguous message when open count ≠ 1 |
| **integration** | `governance-sync --dry-run` on `config-git-only` fixture with one open Auto row: plan lists `next-session` + `paste-ready-prompt` would-patch; tree docs unchanged; runner call log contains **no** `muse` |
| **e2e** | Apply/`--write` on git-only fixture: anchors inserted/replaced; ONE NEXT STEP ID matches queue; paste `Model:` matches; feature-branch commit bundles handover+roadmap; `main` untouched; second run idempotent on NEXT/paste bytes |
| **stress** | Roadmap with 200 DONE rows + 1 open row regenerates within performance bound; roadmap with 40 open rows → human_authorship_required and **zero** NEXT/paste mutation |
| **data-integrity** | Ambiguity path: other sections may patch; NEXT/paste bytes identical to pre-run; induced mid-apply failure leaves no commit (existing integrity contract) |
| **performance** | Regen path on kit-sized handover+roadmap completes under same governance-sync budget as existing suite (no unbounded `docs/` walk — freeze discovery capped to `docs/*.md` names matching token) |
| **security** | Queue cell containing shell metacharacters appears only as escaped/markdown text in fence; path escape outside repo root rejected; git-only fixture asserts no Muse argv |

---

## §GSP.11 — Definition of Done (GS-PASTE-b)

- [ ] `build_handover_patches` regenerates `next-session` + `paste-ready-prompt` per §GSP.4–§GSP.5
- [ ] Ambiguous NEXT fail-closed with `next_regen: human_authorship_required` (§GSP.4.3)
- [ ] Glance fail-closed aligned (§GSP.4.2)
- [ ] Dry-run plans regen without writing docs; apply writes via anchors only
- [ ] Seven-tier §GSP.10 green locally; **git-only fixture proves no Muse**
- [ ] `/build-verification-review` → `pass` before ROADMAP **DONE**
- [ ] `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17)
- [ ] No consumer re-init; no feature→GitHub-`main`; no secrets

---

## §GSP.12 — Hard stops

- No GS-PASTE-b Auto implementation during GS-PASTE-a
- No merge to `main` / staging push / live posture flips without Tier 3
- No live consumer re-init
- No inventing NEXT when ambiguous
- No Muse required for baseline green

---

## §GSP.13 — Cross-references

- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — §4 writes, §7 ambiguity / dry-run
- `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` — NEXT + paste shape; anchors; H1–H12 / H16
- `policy/model-labels.yaml` — labels + `handover_regeneration`
- `tools/governance_hygiene/{anchors,patch,engine,parse}.py` — implementation surface
- `templates/OVERSEER-HANDOVER.template.md` — paste / gate checklist skeleton
- `docs/OVERSEER-KIT-SPEC.md` §6 — freeze review policy
