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
| **K5 Freeze reviewer** | Thinking → Auto | **TODO** | `overseer review --freeze` + automation routing |
| **9A-5 Governance Hygiene Agent** | Auto | **TODO** | `overseer governance-sync [--dry-run]` against kit VCS adapter |
| **K6 Pilot install** | Thinking → Auto | **TODO** | `overseer init` into Scooling → Knowtation → MuseHub → VideoFactory |

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
