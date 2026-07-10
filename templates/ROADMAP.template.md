# {{repo.name}} — Roadmap

## Phase Model Key

| Label | Meaning |
| --- | --- |
| **Thinking** | Design + freeze spec before any build |
| **Auto** | Mechanical implementation against frozen spec |
| **Thinking → Auto** | Thinking design + test matrix, then Auto build |
| **Operator + Auto** | Tier 3 operator authorization for live/staging gates; Auto for implementation |

**Handover rule (SD-3):** any step marked **Thinking → Auto** is split into **`{step}a` (Thinking)** then
**`{step}b` (Auto)** in `{{docs.handover_path}}`. Every next-step table and paste block **must**
include **`Model:`**.

## Build queue

| Phase | Model | Status | Deliverable |
| --- | --- | --- | --- |
| <phase-id> | <model label> | **TODO** | <deliverable> |

## Definition of Done (every phase)

- Deliverables match frozen spec for the phase
- Required seven-tier tests green locally (`policy/test-tiers.yaml`)
- No secrets committed
- Both `{{docs.roadmap_path}}` and `{{docs.handover_path}}` updated together (SD-17)
- Feature branch → commit → (push/PR per `{{vcs.regime}}` rules); no `{{vcs.git.main_branch}}` merge without Tier 3

## VCS context (this repo)

| Setting | Value |
| --- | --- |
| Regime | {{vcs.regime}} |
| Canonical | {{vcs.canonical}} |
| Git remote | {{vcs.git.remote}} |
| Main branch | {{vcs.git.main_branch}} |
| Mirror branch | {{vcs.git.mirror_branch}} |
| Muse staging | {{vcs.muse.staging_remote}} |
| Muse main | {{vcs.muse.main_branch}} |
| Feature branch pattern | {{vcs.git.feature_branch_pattern}} |

## Cross-references

- `{{docs.handover_path}}` — living relay; paste NEXT SESSION into fresh chats
- `{{docs.standing_decisions_path}}` — Standing Decisions (ADR) log and decision authority tiers
- `policy/tiers.yaml` — machine-readable Tier 1/2/3 authority table
- `policy/model-labels.yaml` — allowed Model labels for roadmap + handover
- `policy/test-tiers.yaml` — RULE #0 seven-tier test contract
