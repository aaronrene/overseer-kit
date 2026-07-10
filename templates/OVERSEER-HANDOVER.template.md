# Overseer Handover — {{repo.name}}

**Living relay for {{repo.name}} development.** Paste the **NEXT SESSION** block into a fresh chat.

---

## NEXT SESSION — <title>

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

Model: <label>.

Read first: {{docs.roadmap_path}}; {{docs.handover_path}}.

Deliverables:
- <deliverable list>

Hard stops: <hard stops>

Governance sync: update {{docs.roadmap_path}} + {{docs.handover_path}} on completion.
```

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

## Change log

- **<YYYY-MM-DD>** — <event summary>

---

## Handover regeneration rules (SD-3, SD-17)

1. **Docs-first:** update `{{docs.roadmap_path}}` and durable specs before regenerating this file.
2. **Model label required:** every NEXT block and paste prompt includes **`Model:`**.
3. **Thinking → Auto split:** when NEXT is split, emit `{step}a` (Thinking) then `{step}b` (Auto) — never one combined prompt.
4. **Closing commit:** the session-ending commit bundles code/tests + `{{docs.roadmap_path}}` + `{{docs.handover_path}}`.

See `{{docs.standing_decisions_path}}` → Model-split handover protocol (SD-3) and governance sync (SD-17).
