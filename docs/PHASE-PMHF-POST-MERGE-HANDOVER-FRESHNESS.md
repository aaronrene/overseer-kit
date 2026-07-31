# Phase PMHF — Post-merge handover freshness (platform-neutral closeout)

Status: **Reviewed → `pass` (PMHF-r4).** PMHF-a is **spec-only** and now frozen; no code lands
in this phase. PMHF-b (Auto) is cleared to build mechanically against this frozen contract.

```yaml
phase: PMHF
outputs:
- id: pmhf-post-merge-handover-freshness
  path: docs/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md
  frozen: true
frozen_inputs:
- id: gfg-freshness-gate
  path: docs/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md
- id: phase-9a5-triggers
  path: docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: gs-paste-ready-regen
  path: docs/PHASE-GS-PASTE-READY-REGEN.md
- id: kh1-relay-standard
  path: docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md
- id: close-ritual-land-check
  path: tools/close_ritual/land_check.py
- id: governance-freshness-probe
  path: tools/governance_freshness/check.py
- id: governance-hygiene-drift
  path: tools/governance_hygiene/drift.py
- id: next-regen
  path: tools/governance_hygiene/next_regen.py
- id: status-exit-code
  path: cli/commands/status.py
- id: decision-tiers
  path: policy/tiers.yaml
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: test-tiers
  path: policy/test-tiers.yaml
review_stamp:
  reviewed_at: '2026-07-31T12:28:43Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:7d02bb23779a67015f423e95aa4adca2803d3aeeba1a201fb291f514b2bf6986
```

**Downstream edge:** PMHF-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze). It closes the permanent gap left when GFG detect-only
(`ok status --exit-code` → exit `2` on D1) and optional Cursor session-end Automation do **not**
force a post-merge living-doc closeout — the exact consumer incident after bornfree-hub SF-4 /
PR #206: merge lands on GitHub, handover paste stays “open PR / wait for merge,” agents re-paste
the stale prompt.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| PMHF-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist dry-run pending stamp. Semantic: **R1-M1** §PMHF.4.2 bare `open PR` false-positives normal feature pastes (`templates/OVERSEER-HANDOVER.template.md` / SD-17 language); **R1-M2** bare `Operator` Model label not in `policy/model-labels.yaml` labels (only `Operator + Auto`); **R1-M3** §PMHF.3.3 “land complete” used `report.ok` which includes `land_a_in_progress` — contradicts §PMHF.5 stricter complete rule; **R1-M4** must explicitly amend GFG §GFG.3#4 “no on-merge Automation” for optional GitHub Actions (not git hook / not Cursor); **R1-M5** §PMHF.3.3 roadmap-DONE-while-land-a needs a concrete closeout check not soft prose; **R1-N1** name exact template/skill touchpoint paths in §PMHF.11. Fixed in-doc. |
| PMHF-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** matching land queue row for `land_phase_conflicts_queue_done` underspecified; **R2-M2** freshness `unreadable` must not be masked as `post_merge_incomplete`. Fixed in-doc. |
| PMHF-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R3-M1** §PMHF.3.3 criterion 2 (any row containing `→ main`) false-matches historical DONE land rows (`docs/ROADMAP.md` GS-PASTE → main, GFG → main, …) while a new land-a is in progress — narrow to **phase_tokens intersection only**. Fixed in-doc. |
| PMHF-r4 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read: R1-M1–M5 / R1-N1 / R2-M1–M2 / R3-M1 RESOLVED; land-a/land-b protocol + `land_complete` vs `ok` distinction precise; vocabulary excludes bare `open PR`; queue-DONE conflict uses phase_tokens only; GFG amendment note holds (optional Actions ≠ Cursor/git on-merge primary); no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (Tier-1 CLI + Tier-2 optional CI enable). Stamp written by `ok review --freeze`. |

---

## §PMHF.0 — Simple summary

When a branch is ready to land, someone opens a pull request and waits for a human (or an
authorized land) to merge it. After the merge, the living notes — roadmap and handover — must be
updated so the “what’s next” box no longer says “wait for merge.” Today the kit can *notice* that
those notes are stale (`ok status` already fails), but nothing in the land protocol *requires* a
second paste step to fix them, and Cursor session-end Automation is not an acceptable primary fix
because the kit must work on any platform.

**PMHF freezes a platform-neutral closeout:** land is two paste steps (land-a then land-b);
CLI surfaces refuse “land complete / all clear” until the handover NEXT matches post-merge reality;
optional GitHub Actions may comment or open a docs PR with a governance-sync plan — never silent
writes to `main`, never Cursor-only.

**Technical summary:** compose with GFG (D1/D2 + marker) and GS-PASTE (`next_regen`). Add
machine-readable `land-phase` on the existing `overseer:next` marker; freeze land-a / land-b paste
shapes; add `tools/land_closeout/` (`LandCloseoutReport` / `check_land_closeout`); wire fail-closed
into `ok status --exit-code`, enabled `ok land-check`, and thin `ok land-closeout`; extend
`governance-sync` / `next_regen` so a post-merge plan prefers land-b NEXT; ship opt-in
`templates/ci/governance-closeout-github-actions.yml`. No redesign of freeze review or
build-verification. No Cursor Automation as primary trigger.

---

## §PMHF.1 — Scope

**In scope (PMHF-a freezes; PMHF-b implements):**

1. Two-step land protocol (land-a / land-b) in templates, skills/rules touchpoints, and
   `next_regen` emission rules (§PMHF.3).
2. Machine-readable `land-phase` attribute on the existing NEXT HTML marker (§PMHF.4).
3. `LandCloseoutReport` + `check_land_closeout` resolution rules (§PMHF.5).
4. Fail-closed wiring: `ok status --exit-code`, `ok land-check` (when enabled), new
   `ok land-closeout` (§PMHF.6).
5. Optional CI template: push/merge to `main` → comment or open docs PR with dry-run plan
   (§PMHF.7).
6. Explicit non-goals (§PMHF.2), boundary table (§PMHF.8), consumer migration (§PMHF.9),
   seven-tier matrix (§PMHF.10), Auto deliverables (§PMHF.11).

**Out of scope (explicit non-goals — prevent creep):**

| Non-goal | Why rejected |
| --- | --- |
| **Cursor session-end Automation as primary closeout** | Kit must work on Copilot, Claude Code, CI, and any chat. Cursor Automation may remain a *secondary* degrade (GFG already ships the template); it is **not** the primary loop closer. |
| **Silent writes / commits to `main` after merge** | SD-14 / Tier 3. CI and CLI never patch living docs on `main` in place. Apply stays feature-branch (or docs PR from a branch). Merging a docs-only PR to `main` remains operator policy (existing no-docs-only-PR-to-main rule when deploys are paid) — PMHF CI may *open* a branch PR; it must not auto-merge. |
| **Git `post-merge` hook as primary trigger** | Already REJECTED in 9A-5 §1 / GFG §GFG.2 — does not fire for GitHub-side merges; invisible per-clone; fails `muse-only`. |
| **Reopening GFG’s Cursor/git on-merge Automation as primary** | GFG §GFG.3 rule 4 forbids on-merge Automation *as GFG’s primary*. PMHF **does not** add Cursor/git on-merge Automation. It adds an **optional GitHub Actions** template (§PMHF.7) as a platform-neutral *nudge* — comment or feature-branch docs PR only. |
| **Redesign of freeze review or build-verification** | Out of incident scope. `/freeze-review-loop` and `/build-verification-review` stay as frozen. |
| **Redefining D1/D2/D3 semantics** | Reuse GFG + `tools/governance_hygiene/drift.py`. PMHF adds land-phase posture + closeout state on top. |
| **Making `close_ritual.enabled: true` the default** | Consumer posture flip is Tier 3 / out of kit Auto. Status + `ok land-closeout` are the always-on floor. |
| **Requiring `gh` for the always-on status floor** | Status must remain usable offline relative to GitHub PR listing (same posture as GFG §GFG.4.1). Optional PR-merged enrichment is best-effort when `gh` is available (§PMHF.5.3). |
| **Auto-merge or `ok pr-land` redesign** | Land merge authority stays SD-21 / Tier 3 / existing `ok pr-land`. |
| **Hosted dashboard / Track Q / product runtime changes** | Kit governance only. |
| **One-off hand-edit of a single consumer handover as the “fix”** | Symptom patch; next land recreates the gap. |

---

## §PMHF.2 — Incident → permanent gap (verified, do not redesign)

| Fact | Evidence |
| --- | --- |
| GFG fail-closes `ok status --exit-code` on D1/D2 / stale marker | `docs/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md` §GFG.4–§GFG.6; live `governance_freshness: drifted` |
| GFG primary secondary trigger is Cursor session-end Automation template | §GFG.3; user rejects Cursor-only as primary for this incident class |
| GFG explicitly rejected git post-merge hook and silent main writes | §GFG.2 / §GFG.11 |
| GS-PASTE regenerates NEXT + paste via `governance-sync` only | `docs/PHASE-GS-PASTE-READY-REGEN.md`; `tools/governance_hygiene/next_regen.py` |
| `ok land-check` can report `landed: true` while ignoring land-phase posture | `tools/close_ritual/land_check.py` — path hash match + GFG freshness when enabled; no NEXT posture |
| Land sessions stop for Tier 3 human merge; merge happens on GitHub | SD-21 / Tier 3; bornfree-hub SF-4 / PR #206 class of failure |
| After merge, paste stays “open PR / wait for merge”; agents re-paste | Handover NEXT not split into land-a / land-b; detect ≠ closeout |

PMHF **must not** reopen GFG’s D1/D2 rules, marker format, or exit-code precedence renumbering. It
adds the missing **land protocol**, **NEXT posture**, **land-complete refusal**, and **optional
CI nudge**.

**Frozen amendment note vs GFG §GFG.3 rule 4:** GFG forbids shipping an on-merge Automation that
*pretends to replace* session-end + CLI for freshness. PMHF’s §PMHF.7 GitHub Actions template is
**not** that Automation: it is optional, never Cursor-only, never a git hook, never writes `main`,
and never clears local freshness by itself — agents still run land-b / `ok governance-sync` /
`ok land-closeout`. GFG detect floor stays authoritative for D1/D2/marker.

---

## §PMHF.3 — Land = two paste steps (frozen protocol)

Land is **incomplete** until **both** steps are done.

### §PMHF.3.1 — land-a (PR + stop for merge)

**Purpose:** Open or update the land PR (or run SD-21 finish-mode land hygiene through the
authorized merge path), then **stop** for Tier 3 human merge when SD-21 criteria are not met.

**Frozen paste shape (required fields inside the paste-ready fence):**

```text
Model: Operator + Auto
ID: <slice> → main (land-a)
land-phase: land-a

Deliver:
1. Open/update PR (or SD-21 Muse→mirror→GitHub main path when criteria hold)
2. Stop for Tier 3 merge authorization when required
3. Do NOT claim land complete
4. Do NOT regenerate post-merge NEXT in this paste

After merge is confirmed on main: paste land-b (same slice). Land is incomplete until land-b.
```

**Model label:** exactly `Operator + Auto` from `policy/model-labels.yaml` (no bare `Operator`
— that display value is not a valid label). Never emit a combined “merge + sync docs” single
paste that agents treat as done after opening the PR.

### §PMHF.3.2 — land-b (post-merge roadmap + handover sync)

**Purpose:** After `main` has advanced (merge confirmed), sync living docs so NEXT matches reality.

**Frozen paste shape:**

```text
Model: Auto
ID: <slice> land-b (post-merge sync)
land-phase: land-b

Deliver:
1. Fetch/pull latest main (regime-appropriate)
2. ok governance-sync --dry-run then apply when the plan is correct
3. Regenerate NEXT + paste so they no longer say wait-for-merge / land-a
4. Feature-branch commit bundling ROADMAP + HANDOVER (SD-17); open docs PR if needed
5. ok status --exit-code → 0 and ok land-closeout → 0 before claiming land complete

Hard stops: no silent commits to main; no Cursor-only dependency; no freeze/BV redesign.
```

### §PMHF.3.3 — Completeness rule (frozen)

Define `land_complete(report, freshness)` (stricter than `report.ok` — see §PMHF.5):

```text
land_complete = freshness.ok AND (
  report.state == "complete"
  OR (report.state == "not_applicable" AND freshness.ok)
)
```

`land_a_in_progress` has `report.ok == True` (status must not false-fail while waiting for
merge) but **`land_complete` is False**.

| Claim | Allowed only when |
| --- | --- |
| “PR opened / waiting for merge” | `land-phase=land-a` and state is `land_a_in_progress` |
| “Land complete” / “all clear after land” | `land_complete(...)` is true |
| Queue row `{slice} → main` → **DONE** | `land_complete(...)` is true **and** handover `land-phase` is not `land-a` |

Roadmap may keep a single `{slice} → main` row; the **handover** MUST expose land-a then land-b as
sequential THE ONE NEXT STEPs.

**Frozen check (PMHF-b must implement):** `check_land_closeout` (and therefore
`ok land-closeout` / enabled `ok land-check`) returns `unreadable` with message token
`land_phase_conflicts_queue_done` when the default-lane roadmap has a **matching land
queue row** with status `DONE`/`MERGED` **while** handover `land-phase=land-a`.

**Matching land queue row (frozen):** a build-queue row where
`normalize_status(row.status) in {DONE, MERGED}` **and**
`phase_tokens(row.phase)` intersects `phase_tokens` derived from the land-a NEXT **ID**
cell / paste `ID:` line (reuse `tools/governance_hygiene/parse.py` `phase_tokens`).

Before tokenizing the land-a ID, strip a trailing `(land-a)` / `(land-b)` parenthetical
(case-insensitive) so `PMHF → main (land-a)` tokens align with queue row `PMHF → main`.

**Rejected match rule:** do **not** treat “any DONE row whose phase contains `→ main`” as a
match — that false-fires against historical land rows (e.g. `GS-PASTE → main` DONE while a
new slice’s land-a is current).

Agents must not mark the land queue row DONE until land-b clears `land-phase`.

### §PMHF.3.4 — `next_regen` / governance-sync emission (frozen)

When `ok governance-sync` plans NEXT regeneration (GS-PASTE):

1. If current handover NEXT marker has `land-phase=land-a` **and** closeout state would be
   `post_merge_incomplete` (main advanced / D1 drifted / optional merged-PR signal) → emit
   **land-b** paste for the same slice (do not re-emit land-a).
2. If current NEXT is land-b and D1/D2 become aligned after apply → emit the next unambiguous
   open queue row (or idle / human_authorship_required per GS-PASTE ambiguity rules).
3. Ambiguity remains fail-closed (`next_regen: human_authorship_required`) — never invent a
   product NEXT.
4. Dry-run shows the planned land-b body; apply writes only on non-dry-run (marker stamp carve-out
   from GFG unchanged).

---

## §PMHF.4 — Machine-readable `land-phase` (frozen)

### §PMHF.4.1 — Marker attribute

Extend the existing NEXT marker (KH1 / GS-PASTE), do **not** invent a second marker family:

```html
<!-- overseer:next role=primary lane=product status=live land-phase=land-a -->
```

| Attribute | Values | Required? |
| --- | --- | --- |
| `land-phase` | `land-a` \| `land-b` | Optional on non-land NEXT; **required** on land-a and land-b pastes |

Absent `land-phase` → non-land NEXT (normal queue work). Unknown values → fail closed as
`unreadable` for land_closeout (do not treat as ok).

### §PMHF.4.2 — Closed vocabulary fallback (legacy handovers)

When the marker lacks `land-phase`, scan **only** the paste-ready fence body (not the whole
handover), case-insensitive.

Treat posture as **land-a** when **any** of these frozen substrings match:

- `land-phase: land-a`
- `wait for merge`
- `awaiting merge`
- `stop for Tier 3 merge`
- `→ main (land-a)`
- `(land-a)` as an ID/title token (e.g. `ID: … (land-a)`)

**Explicitly excluded** (do **not** treat as land-a alone — false-positive on ordinary feature
work / SD-17 language):

- bare `open PR` / `open/update PR` / `feature branch → PR`
- `Tier 3` without the full `stop for Tier 3 merge` phrase

Treat as **land-b** when fence contains `land-phase: land-b` or `land-b (post-merge sync)`.

If both land-a and land-b vocabularies match → `unreadable` (fail closed; force human fix).

PMHF-b must prefer the HTML attribute when present; vocabulary fallback is for pre-PMHF
consumer handovers (bornfree-class). Bornfree “wait for merge” pastes match without needing
the HTML attribute.

---

## §PMHF.5 — `LandCloseoutReport` + `check_land_closeout` (frozen)

New module `tools/land_closeout/` (sibling to `tools/governance_freshness/`):

```python
@dataclass(frozen=True)
class LandCloseoutReport:
    state: str
    # not_applicable | land_a_in_progress | post_merge_incomplete |
    # land_b_in_progress | complete | unreadable
    message: str
    remediation: str | None
    land_phase: str | None  # land-a | land-b | None
    freshness_ok: bool
    d1: str | None
    optional_pr_merged: bool | None  # None = not probed

    @property
    def ok(self) -> bool:
        return self.state in {"not_applicable", "land_a_in_progress", "complete"}


def check_land_closeout(
    config: OverseerConfig,
    repo_root: Path,
    *,
    adapter: VcsAdapter | None = None,
    runner: CommandRunner | None = None,
    probe_merged_pr: bool = False,
) -> LandCloseoutReport:
    ...
```

**`ok` semantics (frozen):**

- `not_applicable` — no land posture; closeout N/A → ok for this probe.
- `land_a_in_progress` — waiting for merge; D1 still aligned with current main tip → **ok for
  status floor** (must not fail the whole tree while human merge is pending).
- `post_merge_incomplete` / `land_b_in_progress` / `unreadable` → **not ok**.
- `complete` → ok.

**“Land complete / all clear”** (stricter than `report.ok`): allowed only when
`state == "complete"` **or** (`state == "not_applicable"` **and** freshness ok).  
`land_a_in_progress` is **not** land complete.

### §PMHF.5.1 — Reads (frozen)

1. Reuse `check_governance_freshness` for D1/D2/marker (no re-derivation of GFG rules).
2. Read default-lane handover text; parse `land-phase` from NEXT marker; apply §PMHF.4.2 fallback.
3. Do **not** call `gh` unless `probe_merged_pr=True` (§PMHF.5.3).
4. Unreadable handover / marker parse failure → `state="unreadable"`.

### §PMHF.5.2 — Resolution order (frozen)

1. If config/repo cannot load → `unreadable`.
2. If not initialized (no `version.lock`) → `not_applicable`.
3. Compute freshness via GFG probe; record `freshness_ok`, `d1`.
   If freshness `state == "unreadable"` → `unreadable` (do not mask as
   `post_merge_incomplete`).
4. Resolve `land_phase` (§PMHF.4).
5. If `land_phase == "land-a"` and a **matching land queue row** exists per §PMHF.3.3 →
   `unreadable` with message token `land_phase_conflicts_queue_done`. Do not treat as complete.
6. If `land_phase` is None → `not_applicable` (this probe does not override GFG; status still
   applies GFG independently).
7. If `land_phase == "land-a"`:
   - If `d1 == "drifted"` OR freshness state in `{drifted, stale_marker}` OR
     optional_pr_merged is True → `post_merge_incomplete`.
     Remediation (frozen string prefix):  
     `land-b required: ok governance-sync --dry-run then apply; paste land-b; do not re-paste land-a`.
   - Else → `land_a_in_progress`.
8. If `land_phase == "land-b"`:
   - If freshness not ok OR `d1 == "drifted"` → `land_b_in_progress` with remediation to finish
     governance-sync apply + clear land-phase.
   - Else → `complete`.
9. Else → `unreadable`.

### §PMHF.5.3 — Optional merged-PR enrichment (frozen)

When `probe_merged_pr=True` **and** `gh` is available **and** the paste fence names
`PR #<digits>`:

- If that PR is merged on the configured remote → treat as merge reflected
  (`optional_pr_merged=True`), even if D1 was hand-edited back to aligned.
- If `gh` missing/fails → leave `optional_pr_merged=None`; do **not** fail open to `complete`.

**Default for `ok status --exit-code`:** `probe_merged_pr=False` (offline floor).  
**Default for `ok land-closeout`:** `probe_merged_pr=True` when regime is not `muse-only`; False
for `muse-only` (no git/gh).  
**CI template:** may pass `--probe-merged-pr`.

### §PMHF.5.4 — Composition with GFG (frozen)

| Surface | GFG | PMHF land_closeout |
| --- | --- | --- |
| D1/D2/marker | Authority | Consumer of GFG report |
| Mid-land wait (land-a, D1 aligned) | ok | `land_a_in_progress` (ok for status) |
| Post-merge stale NEXT (land-a, D1 drifted) | exit 2 | `post_merge_incomplete` + land-b remediation |
| Hand-edited VCS SHA, land-a remains, PR merged | may look ok | Caught when `probe_merged_pr` true; else CI nudge + land-check refusal |
| Circular wiring into `governance-sync` | Forbidden (GFG) | Still forbidden — sync must run to repair |

---

## §PMHF.6 — Fail-closed CLI wiring (frozen)

Reuse exit code **`2`**. Do **not** renumber `2 > 6 > 35 > 3 > 0`.

### §PMHF.6.1 — `ok status` / `ok status --exit-code`

- Always compute `check_land_closeout(..., probe_merged_pr=False)` when initialized (additive).
- JSON key:  
  `land_closeout: {state, ok, message, remediation, land_phase, freshness_ok, d1, optional_pr_merged}`.
- Human mode: print a line when `not report.ok` (mirror GFG / muse_sync).
- `--exit-code`: fold `land_closeout_ok` into the top tier with existing conditions:  
  `… or not governance_freshness_ok or not land_closeout_ok → 2`.  
  Because `land_a_in_progress` has `ok=True`, waiting for merge does **not** false-fail status.
- Plain `ok status` without `--exit-code` still exits `0`.

### §PMHF.6.2 — `ok land-check`

When `close_ritual.enabled: false`, keep today’s no-op exit `0` (**unchanged**).

When enabled, after path checks + GFG freshness (§GFG.6):

1. Run `check_land_closeout` with `probe_merged_pr=True` (git regimes).
2. Set `landed=True` only when path checks pass **and** freshness ok **and**
   land_closeout state is `complete` or `not_applicable`.
3. If state is `land_a_in_progress`, `post_merge_incomplete`, or `land_b_in_progress` →
   `landed=False`, exit `2`, emit remediation (never merge).

### §PMHF.6.3 — `ok land-closeout` (new thin command)

| Item | Rule |
| --- | --- |
| Command | `ok land-closeout [--json] [--probe-merged-pr]` |
| Behavior | Print `LandCloseoutReport`; exit `0` if `report.ok` else `2` |
| Merge | Never |
| Doc writes | Never |
| Purpose | Agent/CI choke point with explicit land-b remediation; platform-neutral |

`--probe-merged-pr` forces enrichment on; `--no-probe-merged-pr` disables. Default per §PMHF.5.3.

### §PMHF.6.4 — Surfaces that must NOT gain circular fail-closed

| Surface | Rule |
| --- | --- |
| `ok governance-sync` | Must still run when land_closeout incomplete (it is the repair tool). |
| `ok review --freeze` | Not wired (same as GFG). |

### §PMHF.6.5 — Refusal strings (frozen tokens)

Emit these human-visible tokens (exact) when refusing land complete:

- `land_closeout: post_merge_incomplete`
- `land_closeout: land_b_in_progress`
- `land_closeout-remediation: land-b required: ok governance-sync --dry-run then apply; paste land-b; do not re-paste land-a`

Never emit “all clear” / `landed: true` / `land complete` while those states hold.

---

## §PMHF.7 — Optional CI on push/merge to main (frozen)

Ship a **template only** (opt-in; not auto-enabled for all consumers):

**Path:** `templates/ci/governance-closeout-github-actions.yml`

**Frozen behavior:**

```yaml
on:
  push:
    branches: [main]   # or repo main_branch name documented in header comments
  workflow_dispatch:
```

Job steps (normative intent — PMHF-b may use current `actions/checkout` / `setup-python` majors):

1. Checkout `main` at the push SHA.
2. Install CLI deps (PyYAML) — same pattern as freeze-review CI template.
3. Run `ok governance-sync --dry-run` (and optionally `ok land-closeout --probe-merged-pr`).
4. If dry-run reports D1/D2 drift or land_closeout not ok:
   - **Comment** on the push commit (or associated merged PR when detectable) with the dry-run
     plan summary + frozen remediation pointing to land-b paste; **or**
   - **Open a docs PR** from an auto branch (e.g. `chore/governance-closeout-<shortsha>`) that
     contains **only** the planned living-doc patch **after** an explicit apply in CI is
     **forbidden on `main`**. Preferred v1: **comment-only** with the plan; opening a docs PR is
     allowed only if the workflow commits to a **feature branch** and opens PR → `main` (never
     direct push to `main`).
5. Workflow exit non-zero when closeout incomplete so the check is visible — but **never**
   treat CI unavailability as pass for local agents (degrade: run `ok land-closeout` locally).

**Frozen bans:**

- No `git push` to `main` from this workflow.
- No applying governance-sync patches directly onto `main` in CI.
- No Cursor-only steps.
- No secrets beyond standard `GITHUB_TOKEN` for comment/PR.

Kit dogfood may vendor a disabled example under `.github/workflows/` only if clearly marked
optional; default remains template-under-`templates/ci/` like freeze-review.

---

## §PMHF.8 — Boundary table (frozen)

| Scenario | Caught / closed by PMHF? |
| --- | --- |
| Merge on GitHub; NEXT still land-a; D1 drifted; `ok status --exit-code` | **Yes** — GFG + `post_merge_incomplete` remediation → land-b |
| Agent re-pastes land-a after merge | **Yes** — protocol forbids; CLI remediation says do not re-paste land-a; land-check refuses landed |
| Cursor Automations unavailable | **Non-blocking** — CLI + optional CI remain primary |
| Mid-land wait; land-a; D1 aligned | **No false fail** on status — `land_a_in_progress` ok |
| Hand-edit VCS SHA; land-a remains; PR merged; `gh` available | **Yes** via `ok land-closeout --probe-merged-pr` |
| Same hand-edit; offline; no gh | **Partial** — status may be green; land-check (enabled) still refuses landed while land-a; CI comment nudges |
| Silent main doc rewrite from CI | **Forbidden** |
| Freeze / BV redesign | **Out of scope** |
| `muse-only` (no git/gh) | land-phase + freshness via Muse tip; no gh probe; CI template N/A |

---

## §PMHF.9 — Consumer migration notes (frozen honesty)

After PMHF-b merges and consumers `ok sync`:

1. **No required config block** for the status / `land-closeout` floor (always-on when initialized).
2. Existing land NEXT pastes without `land-phase=` keep working via §PMHF.4.2 vocabulary fallback.
3. Operators should split any living “→ main / wait for merge” NEXT into land-a then land-b on the
   next land (template + regen will emit the attribute going forward).
4. Optional: copy `templates/ci/governance-closeout-github-actions.yml` into
   `.github/workflows/` (Tier 2 confirm-once to enable). Not required for CLI floor.
5. `close_ritual.enabled: false` consumers still get status + `ok land-closeout`; land-check
   posture refusal applies only when enabled (unchanged GFG split).
6. One-time: if currently D1-drifted with stale wait-for-merge NEXT, run land-b
   (`ok governance-sync --dry-run` → apply) — do not re-paste land-a.
7. Blast radius: workflows that claimed “landed” solely from path hashes while NEXT said wait-for
   merge will start seeing `land-check` / `land-closeout` exit `2`. That is intended.

---

## §PMHF.10 — Seven-tier test matrix (PMHF-b Auto must satisfy)

| Tier | Proves |
| --- | --- |
| **unit** | `check_land_closeout` resolution table: not_applicable / land_a_in_progress / post_merge_incomplete (D1 drifted) / post_merge_incomplete (stale_marker) / land_b_in_progress / complete / unreadable (bad land-phase) / vocabulary fallback land-a (`wait for merge`) / bare `open PR` alone does **not** trigger land-a / conflict vocab → unreadable / `land_phase_conflicts_queue_done` (token intersection) / historical other-slice `→ main` DONE does **not** conflict; `ok` vs `land_complete` distinction; marker attribute beats vocabulary. |
| **integration** | `ok status --json --exit-code` → `2` with `land_closeout.state=post_merge_incomplete` when land-a + D1 drifted; → `0` when land-a + D1 aligned (`land_a_in_progress`); `ok land-closeout` exit codes; `ok land-check` with ritual enabled refuses `landed` for land-a and post_merge_incomplete; governance-sync dry-run plans land-b NEXT when land-a + D1 drifted. |
| **e2e** | Fixture cycle: land-a NEXT + aligned main → status 0 → advance main tip → status 2 + land-b remediation → governance-sync apply → land-phase cleared/complete → status 0 + land-closeout 0. |
| **stress** | Large handover (200+ queue rows) — land_closeout parse + freshness compose finishes bounded; no gh when probe false. |
| **data-integrity** | land-closeout and status never write docs; CI template contains no apply-to-main step; dry-run governance-sync still only stamps local marker per GFG carve-out. |
| **performance** | Default status path adds no `gh` invocation for land_closeout (`probe_merged_pr=False`). |
| **security** | No secrets in report; remediation strings non-executed; muse-only never calls git/gh; CI template uses `GITHUB_TOKEN` only; fail-closed unreadable; no silent main write path. |

---

## §PMHF.11 — PMHF-b Auto deliverables (exact)

1. `tools/land_closeout/` (`__init__.py`, report + `check_land_closeout`) per §PMHF.5.
2. `cli/commands/land_closeout.py` + `cli/main.py` registration for `ok land-closeout`.
3. `cli/commands/status.py` additive JSON/human + `--exit-code` fold per §PMHF.6.1.
4. `tools/close_ritual/land_check.py` landed refusal per §PMHF.6.2.
5. `tools/governance_hygiene/next_regen.py` (+ patch/engine wiring as needed) land-b emission per
   §PMHF.3.4; marker `land-phase=` support per §PMHF.4.
6. Minimal template/skill/rule touchpoints (exact paths):
   - `templates/OVERSEER-HANDOVER.template.md` — land-a / land-b paste shape note (or short
     subsection under regeneration rules)
   - `cursor/skills/governance-sync/SKILL.md` (+ twin `.claude/skills/governance-sync/SKILL.md`
     if footprint copies it) — land-b remediation one-liner when land-a + drift
   - `.cursor/rules/tier-authority.mdc` (and twin if present) — one line: land incomplete until
     land-b; no claim of land complete while `ok land-closeout` fails
7. `templates/ci/governance-closeout-github-actions.yml` per §PMHF.7.
8. SPEC §5 additive rows for `ok land-closeout` + status `land_closeout` key (additive only).
9. Seven-tier tests under `tests/` covering §PMHF.10 (include
   `land_phase_conflicts_queue_done` + vocabulary false-positive exclusions).
10. Kit ROADMAP + HANDOVER updated together; `/build-verification-review` → `pass` before
    ROADMAP PMHF-b → DONE.
11. No Cursor-only primary path; no silent main writes; no freeze/BV redesign.

---

## §PMHF.12 — Hard stops (unchanged)

- No kit `main` merge without Tier 3 / SD-21 criteria.
- No consumer posture/env flips; no secrets; no real money.
- No Cursor Automation as the primary closeout.
- No silent writes on `main`.
- No redesign of `/freeze-review-loop` or `/build-verification-review`.

---

## Cross-references

- `docs/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md` — detect floor this phase closes into a loop.
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` §1 — trigger rejections this phase respects.
- `docs/PHASE-GS-PASTE-READY-REGEN.md` — NEXT/paste regen surface land-b reuses.
- `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` — NEXT / paste shape.
- `docs/OVERSEER-KIT-SPEC.md` §6 — Freeze-Contract review policy.
- `policy/tiers.yaml` — SD-21 finish-mode land hygiene vs Tier 3 merge.
- `templates/ci/freeze-review-github-actions.yml` — CI template precedent.
