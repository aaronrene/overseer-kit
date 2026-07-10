# Cross-Repo Coordination And Overseer Playbook — {{repo.name}}

Status: **Coordination doc — process, not product.** Explains where work happens, how repos stay in
sync, which boundaries must not be crossed, and how to hand the overseer chat off without losing
cross-repo context.

Related:

- `{{docs.roadmap_path}}` — phase control + build status
- `{{docs.handover_path}}` — living, always-current filled handover block
- `{{docs.standing_decisions_path}}` — Standing Decisions (ADR) log + decision authority tiers
- `policy/tiers.yaml`, `policy/model-labels.yaml`, `policy/test-tiers.yaml` — machine-readable policy

---

## Simple summary

Governance habits (handover, roadmap, testing discipline, merge authority, model labels) must stay
consistent across connected repos. This page is the map: where each kind of change goes, what must
never break, and how one chat hands the baton to the next so the overseer view is reconstructable
from durable docs — not chat scrollback.

## Technical summary

**VCS regime for this repo:** `{{vcs.regime}}` (canonical: `{{vcs.canonical}}`). Coordination uses:
(1) a clear ownership/decision table, (2) per-repo VCS discipline, (3) explicit non-overstep
boundaries, (4) a canonical-document map, and (5) an **overseer handover protocol** with a paste-able
state snapshot.

---

## Version control (this repo)

| Setting | Value |
| --- | --- |
| Regime | {{vcs.regime}} |
| Canonical | {{vcs.canonical}} |
| Git remote | {{vcs.git.remote}} |
| Main branch | {{vcs.git.main_branch}} |
| Mirror branch | {{vcs.git.mirror_branch}} |
| Muse staging remote | {{vcs.muse.staging_remote}} |
| Muse main branch | {{vcs.muse.main_branch}} |
| Feature branch pattern | {{vcs.git.feature_branch_pattern}} |

Shared rules: never work directly on `{{vcs.git.main_branch}}`; feature branch per task; never commit
secrets or ignored paths. Say **"Muse commit"** vs **"Git commit"** explicitly when both histories apply.

### Regime-specific hard stops

| Regime | Rule |
| --- | --- |
| `muse+git-mirror` | Muse `{{vcs.git.main_branch}}` before GitHub `{{vcs.git.main_branch}}` (SD-14); mirror via `{{vcs.git.mirror_branch}}` PR only; never `git push {{vcs.git.remote}} {{vcs.git.main_branch}}` |
| `muse-only` | **Git/GitHub forbidden** in this repo; Muse-only workflow |
| `git-only` | Canonical = Git `{{vcs.git.remote}}/{{vcs.git.main_branch}}`; no Muse commands |

> **Cross-repo Muse safety:** when driving Muse from an agent, always use explicit
> `muse -C <absolute-repo-root> <command>` and confirm branch + HEAD before any cross-repo operation.

---

## Boundaries we do not overstep

- **Review-before-write** for durable knowledge changes.
- **No secrets** across repo boundaries — tokens, keys, and private content never in adapters, logs,
  or shared procedures.
- **Canonical-first ordering** — do not wire a consumer before the surface it reads exists.
- **Governance sync (SD-17)** — update `{{docs.roadmap_path}}` + `{{docs.handover_path}}` before session end.

---

## Canonical documents map (this repo)

| Question | Authoritative doc |
| --- | --- |
| What phase / what's next / which model | `{{docs.roadmap_path}}` |
| Current filled handover block | `{{docs.handover_path}}` |
| Decision authority + Standing Decisions | `{{docs.standing_decisions_path}}` |
| Cross-repo coordination (this page) | `{{docs.coordination_path}}` |

---

## The overseer role and handover protocol

**Overseer chat** tracks state, decides what goes next, and guards boundaries. State must always be
reconstructable from **durable docs**, not chat history.

**Durable state of record:**

1. `{{docs.roadmap_path}}` — phase truth + build status.
2. `{{docs.handover_path}}` — living filled handover block (single paste source).
3. `{{docs.standing_decisions_path}}` — tiers + ADR log.
4. This doc — boundaries + decision table (when `docs.coordination` is configured).

**Docs-first ordering:** (1) update durable docs to match reality, (2) regenerate
`{{docs.handover_path}}` from those docs, (3) emit/paste the NEXT block. Never hand-write the block
from memory ahead of the docs.

**Handover snapshot shape** (filled into `{{docs.handover_path}}`):

```text
OVERSEER HANDOVER — <date/time>
Initiative + current step: <step-id>
Build order / next action: <action>

Per-repo state:
- {{repo.name}}: branch <feat/...>  last <vcs> <sha>  dirty? <y/n>

Open gates / blockers: <list>
Boundaries to honor: <list>
Links: {{docs.roadmap_path}}; {{docs.handover_path}}
```

---

## Decision authority (three tiers)

Machine-readable copy: `policy/tiers.yaml`.

| Tier | What it covers | Behavior |
| --- | --- | --- |
| **1 — Standing defaults** | Feature-branch commits (docs or code); tests; formatting; non-destructive refactors | **Just do it.** Never on `{{vcs.git.main_branch}}`; never push/merge. |
| **2 — Recommend-and-confirm** | Persistence shape; adapter contracts; schema-version choices | **Propose + recommend → one yes/no → record in Standing Decisions.** |
| **3 — Hard gates** | Merge to `{{vcs.git.main_branch}}`; staging push; live capability flips; payments; secrets | **Always stop for operator authorization.** |

**Commit rule:** committing on a feature branch is Tier 1. Pushing to staging or merging to
`{{vcs.git.main_branch}}` is Tier 3. Leaving durable doc edits uncommitted is the worse state.

---

## Recommended Flow: Overseer handover

Scope: session end, chat switch, or multi-repo state in flight. **Docs-first.**

| # | Step | Verification |
| --- | --- | --- |
| 1 | **Snapshot truth** — VCS status per touched repo (explicit `-C` for Muse) | Branch + sha captured |
| 2 | **Record step + next action + blockers** | Next action unambiguous |
| 3 | **List boundaries + cross-repo wiring touched** | Boundaries explicit |
| 4 | **Update durable docs FIRST** — roadmap, standing decisions if needed | Docs match reality |
| 5 | **Regenerate `{{docs.handover_path}}`** from current docs; SD-3 split if Thinking → Auto | Living file matches docs |
| 6 | **Emit/paste** NEXT block into the next chat | New overseer needs no prior history |

---

## Model-split handover protocol (SD-3)

When the roadmap **Model** column for NEXT contains **`→`**, see `{{docs.standing_decisions_path}}`
and `policy/model-labels.yaml`. Emit `{step}a` then `{step}b` — not one combined prompt.

---

## Seven-tier test contract (RULE #0)

Every Build phase that adds code ships all seven tiers. See `policy/test-tiers.yaml` for the
machine-readable matrix and what each tier must prove.
