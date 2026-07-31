# {{docs.handover_title}} — {{repo.name}}

**Public product name:** 🆗 Overseer Kit — `{{repo.name}}` is the repo slug only, not the public brand.

**Living relay for 🆗 Overseer Kit in {{repo.name}}.** Paste the **NEXT SESSION** block into a fresh chat.

In a multi-root editor, the focused tab is **not** product authority — run `ok workspace status` /
`ok workspace check-next` when `workspace:` is configured.

---

<!-- overseer:next role=primary lane=product status=live -->
## NEXT SESSION — <title> (PRIMARY)

**Date:** <YYYY-MM-DD>  
**Current position:** <one-line status>  
**Model:** <Thinking | Auto | Thinking → Auto | Operator + Auto>

### What just landed

| Slice | Deliverable |
| --- | --- |
| <slice-id> | <deliverable summary> |

### THE ONE NEXT STEP — **Model: <label>**

<one-sentence next action>

| | |
| --- | --- |
| **ID** | **<phase-id>** |
| **Branch** | `{{vcs.git.feature_branch_pattern}}` (slug = `<slug>`) |
| **Repo** | **{{repo.name}}** |
| **Read first** | `{{docs.roadmap_path}}`; `{{docs.handover_path}}` |
| **Hard stops** | No merge to `{{vcs.git.main_branch}}` without Tier 3 · no live posture flips without authorization |

### Paste-ready prompt — <phase-id>

```
Phase <phase-id> — <title> ({{repo.name}}).

Model: <label>
Repo: <absolute-or-workspace-relative-path>
Branch: <branch-or-unknown>
Step: <phase-id>
Authority: authoritative

Read first: {{docs.roadmap_path}}; {{docs.handover_path}}.

Deliverables:
- <deliverable list>

Hard stops: <hard stops>

Governance sync: update {{docs.roadmap_path}} + {{docs.handover_path}} on completion.

Governance gates (mandatory — remind only; silence is not pass):
- Freeze review: /freeze-review-loop before Thinking freeze → DONE; ok review --freeze when CLI green
- Build verification: /build-verification-review after every Auto {step}b before ROADMAP DONE
- Workspace (when configured): ok workspace check-next before claiming multi-repo SD-17 complete
```

---

<!-- Example RELAY tip (ownership/enrichment boards parked on product tip):
<!-- overseer:next role=relay lane=product status=live product_order=<member_id> tip_hash=sha256:<hex> -->
## NEXT SESSION — Product tip (RELAY → <member_id> <step_id> <Model>)
-->

<!-- Example PRODUCT RELAY (durable tip while LIVE NEXT is ownership PRIMARY):
<!-- overseer:next role=product_relay lane=product status=live product_order=<member_id> tip_hash=sha256:<hex> -->
## PRODUCT RELAY — <member_id> <step_id> <Model>
-->

<!-- Example LANE TIP (non-primary constellation lane — never uses ## NEXT SESSION —):
<!-- overseer:next role=lane_tip lane=security status=live -->
## LANE TIP — <title> (LANE: security)
-->

<!-- overseer:next role=archived status=archived -->
## ARCHIVED SESSION — <prior title>

Archived prompts MUST NOT use `## NEXT SESSION —` (including “archived” in the title).

---

## Verified snapshot

| Area | State |
| --- | --- |
| **Repo** | {{repo.name}} |
| **VCS regime** | {{vcs.regime}} (canonical: {{vcs.canonical}}) |
| **Governance docs** | `{{docs.handover_path}}`, `{{docs.roadmap_path}}` |
| **Standing decisions** | `{{docs.standing_decisions_path}}` |

## VCS (verified <YYYY-MM-DD>)

| Item | Value |
| --- | --- |
| Branch | `<branch>` |
| HEAD | `<sha>` |
| Dirty | `<y/n>` |

## Hard stops (unchanged)

- No merge to `{{vcs.git.main_branch}}` without Tier 3 authorization
- No live capability / posture gate flips without Tier 3 authorization
- No secrets in commits, adapters, logs, or governance docs
- Governance sync is mandatory before session end (SD-17)
- Multi-repo: refresh `relay: true` product tips (or PRODUCT RELAY) when product_order PRIMARY advances

## Change log

- **<YYYY-MM-DD>** — <event summary>

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `{{docs.roadmap_path}}` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Build verification (mandatory):** after `{step}b`, run `/build-verification-review` before ROADMAP status → **DONE**.
5. **Closing commit:** the session-ending commit bundles code/tests + `{{docs.roadmap_path}}` + `{{docs.handover_path}}`.
6. **Spend awareness:** when `cost_awareness.enabled: true`, `ok status` and `governance-sync` surface the active slice's cost band and paid-step flag (reminder-only; silence is not pass).
7. **Workspace markers (KH1 H13–H17):** exactly one `## NEXT SESSION —` with PRIMARY or RELAY marker; archived uses `## ARCHIVED SESSION —` only; lane tips use `## LANE TIP —`; when `workspace:` + `strict_board_names`, prefer `{REPO_SLUG}-OVERSEER-HANDOVER.md` filenames.
8. **Land = two pastes (PMHF):** landing a slice is `land-a` (open/update PR; stop for Tier 3 merge; marker `land-phase=land-a`; ID `<slice> → {{vcs.git.main_branch}} (land-a)`) then, after merge is confirmed, `land-b` (post-merge sync; marker `land-phase=land-b`; ID `<slice> land-b (post-merge sync)`). Land is incomplete until land-b clears: `ok status --exit-code` → 0 **and** `ok land-closeout` → 0. Never re-paste land-a after merge; never mark the `<slice> → {{vcs.git.main_branch}}` queue row DONE while the handover `land-phase` is still `land-a`.

See `{{docs.standing_decisions_path}}` → Model-split handover protocol (SD-3) and governance sync (SD-17).
