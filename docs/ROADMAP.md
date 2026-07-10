# Overseer Kit — Roadmap

## Phase Model Key

| Label | Meaning |
| --- | --- |
| **Thinking** | Design + freeze spec before any build |
| **Auto** | Mechanical implementation against frozen spec |
| **Thinking → Auto** | Thinking design + tests, then Auto build |

## Build queue

| Phase | Model | Status | Deliverable |
| --- | --- | --- | --- |
| **K1 Bootstrap** | Thinking → Auto | **DONE** | Repo skeleton, promoted spec, dogfood governance docs |
| **K2 Config + adapters** | Thinking → Auto | **DONE** | `.overseer/config.yaml` schema + VCS adapter interface + three fail-closed backends |
| **K3 Extract shared assets** | Auto | **DONE** | Templates + policy + cursor fragments; `adapters/templating.py` |
| **K4a Freeze CLI contract** | Thinking | **DONE** | Frozen `init\|sync\|status` arg contract + `version.lock` shape + `footprint_digest` algorithm + K4b seven-tier matrix (`docs/PHASE-K4-VENDORING-CLI-CONTRACT.md`) |
| **K4b Vendoring CLI build** | Auto | **TODO** | Implement `overseer init\|sync\|status` + `version.lock` + drift check against the K4a freeze; seven-tier tests green |
| **K5 Freeze reviewer** | Thinking → Auto | **TODO** | `overseer review --freeze` + automation routing. **Required K5a design decision (frozen requirement):** the `freeze_contract` config block must be extended to let each repo choose its reviewer model and provider (local vs API). Proposed schema: `reviewer.mode: agent\|human`, `reviewer.model: <label from policy/model-labels.yaml>`, `reviewer.provider: local\|api`, `reviewer.fallback: human` (fail-closed if provider unreachable). No core review capability may be API-only. See K5 design note in `docs/OVERSEER-KIT-SPEC.md` §6. |
| **9A-5 Governance Hygiene Agent** | Auto | **TODO** | `overseer governance-sync [--dry-run]` against kit VCS adapter |
| **K6 Pilot install** | Thinking → Auto | **TODO** | `overseer init` into Scooling → Knowtation → MuseHub → VideoFactory |
| **K7 Dogfood muse+git-mirror** | Thinking → Auto | **TODO** | Flip this repo to MuseHub canonical + GitHub mirror; vendor `MUSE-BRIDGE-WORKFLOW.template.md` + tokenized `muse-bridge-deploy.sh` into the footprint for `muse+git-mirror` consumers; parity gate + seven-tier tests. Operator-run (needs `muse`/`gh`/staging repo). **Frozen design guardrail:** MuseHub may only *deepen* a capability — no core governance feature may ever become MuseHub-only (see principle below). |

## Regime capability tiers (git-only baseline → MuseHub-enhanced)

The kit is **fully usable on GitHub alone**; MuseHub is an **optional substrate** that unlocks deeper
capability. Same commands, same governance — more power when the canonical history is Muse.

| Capability | `git-only` (baseline, no Muse) | `muse+git-mirror` (MuseHub substrate) |
| --- | --- | --- |
| `init` / `sync` / `status` / drift | Full | Full |
| Governance docs + freeze review | Full | Full |
| Canonical history | GitHub `main` | MuseHub (content-addressed, `sha256:` commit ids) |
| `realign` (drift-repair vs canonical anchor) | No-op (single history) | Active — detects/repairs Muse↔Git inversion (the `GITHUB-MIRROR-RECONCILIATION-FOLLOWUP.md` failure) |
| `mirror` (SD-14 safe export) | No-op | Active — isolated `.muse/mirror/` export → `muse-mirror` PR |
| Provenance / version enrichment | Git commit metadata only | MuseHub version + provenance + social layer |
| Route to MuseHub onboarding | — | The vendored bridge workflow *is* the introduction path |

**Frozen guardrail (K7 design principle):** **No core governance feature may ever be MuseHub-only.**
Every baseline capability (`init`/`sync`/`status`, drift, footprint digest, templates, policy, freeze
review, governance-sync) must remain fully functional on `git-only`. MuseHub may *deepen* a capability
(`realign`, `mirror`, provenance/version enrichment) but never *gate* the baseline. This keeps the
GitHub-only promise credible and makes the MuseHub value proposition about **superior depth, not
withheld function**. The VCS adapter interface (spec §4) enforces this seam: `git-only` implements
`realign`/`mirror` as reporting no-ops; `muse+git-mirror` implements them for real; the CLI calls the
same method names in both regimes.

## Reference repos (consumers, not owners)

| Repo | Regime | Customization point |
| --- | --- | --- |
| Scooling | `muse+git-mirror` | Product runtime in `src/phase9a/` (reference, not vendored) |
| Knowtation | `muse+git-mirror` | Canonical Flow/store; kit owns governance only |
| MuseHub | `muse-only` | Plugin governance; git forbidden |
| VideoFactory | `git-only` | Track H honest-factory domain freeze specs |
| Any external project | `git-only` | `.overseer/config.yaml` only |

## Definition of Done (every phase)

- Deliverables match `docs/OVERSEER-KIT-SPEC.md`
- Required seven-tier tests green locally
- No secrets committed
- Both `docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` updated together

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` — frozen architecture
- `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` — frozen K4 CLI contract (K4a); K4b builds against it
- `templates/` + `policy/` + `cursor/` — vendored footprint (K3)
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — first agent tool
- Scooling `docs/PHASE-9A-MULTI-AGENT-OVERSEER-ROUTER-OUTLINE.md` — runtime org-chart reference
