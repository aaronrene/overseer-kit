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
| **K4b Vendoring CLI build** | Auto | **DONE** | `overseer init\|sync\|status` + `version.lock` + `footprint_digest` + drift check; POSIX shim → `cli/` Python runtime; 108 tests green (§K4.10 seven tiers) |
| **K5a Freeze reviewer contract** | Thinking | **DONE** | Frozen `overseer review --freeze` arg contract + exit codes `7`/`8` + extended `freeze_contract.reviewer.{mode,model,provider,fallback}` schema (legacy string normalization; `local\|api`; `fallback: human` fail-closed; `reviewer_models` labels) + findings/verdicts/stamp/escalation + Automation degrade path + K5b seven-tier matrix (`docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md`). Independent freeze review **round 3 → `pass`** (F1–F9 + N1–N3 resolved). Cleared for K5b. |
| **K5b Freeze reviewer build** | Auto | **DONE** | `overseer review --freeze` + nested `freeze_contract.reviewer` parse (legacy string normalization) + `reviewer_models` in `policy/model-labels.yaml` + `tools/freeze_reviewer/` engine (injectable local\|api; `fallback: human` fail-closed) + §K5.9 report + stamp write + Automation templates + seven-tier tests. Cleared by K5b-r2 `pass` + PR #6 on `main` (not by premature PR #5 merge alone). |
| **K5b-r Merge gate review** | Thinking | **DONE** | Round 1 `blocked` (F1–F6 on PR #5). F1–F5 fixed (PR #6). **K5b-r2 → `pass`** ([review](https://github.com/aaronrene/overseer-kit/pull/6#pullrequestreview-4676205810)). K5b cleared. |
| **9A-5 Governance Hygiene Agent** | Auto | **DONE** | `overseer governance-sync [--dry-run]` against kit VCS adapter — `tools/governance_hygiene/` + seven-tier tests (**181** green) |
| **K6a Freeze pilot install matrix** | Thinking | **DONE** | Frozen install order + per-repo config matrix + `init --migrate` preserve contract + parity gate (P1–P7 + per-repo extras) + Muse `working_dir` / VF `.` docs-root seams + K6b seven-tier matrix (`docs/PHASE-K6-PILOT-INSTALL-MATRIX.md`). Rounds 1–5 **`blocked`** → fixes through **5-fix**; Round 6 **`findings`** (R6-M1) → **6-fix**; **K6a-r7 → `pass`** (R6-M1 + R5/R4 spot-check + full §K6.0–§K6.10 regress). Cleared for K6b. |
| **K6b Pilot install build** | Auto | **DONE** | Additive `init --migrate` + `--include-preserved`; `vcs.muse.working_dir` + `root_relative_docs: "."` seams; `origin: preserved\|kit` lock + kit-only digest; `tests/fixtures/pilot/*`; `docs/GIT-ONLY-QUICKSTART.md` + `docs/K6-PILOT-OPERATOR-RUNBOOK.md`; seven-tier tests (**224** green). Live consumer inits remain operator-gated; no gate flips; no K7 muse dogfood. |
| **K7a Freeze muse+git-mirror dogfood** | Thinking | **DONE** | Frozen dogfood steps + regime-conditional footprint + parity K7.P1–P10 + §K7.5 guardrail + §K7.8 matrix (`docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`). **K7a-r1 → `findings`** → **1-fix** → **K7a-r2 → `pass`** (M1/M2/N1–N3 confirmed RESOLVED; full §K7.0–§K7.10 regress clean). Cleared for K7b. No Build; no live muse bridge export on the dev tree. |
| **K7b Dogfood muse+git-mirror build** | Auto | **DONE** | Footprint assets (`MUSE-BRIDGE-WORKFLOW.template.md`, `muse-bridge-deploy.sh` S1–S13), regime-conditional `resolve_footprint`, executable script write, `config-overseer-kit-dogfood.yaml` fixture, `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md`, seven-tier tests (**254** green). No live `git-export` on dev tree. |
| **K7 operator live dogfood** | Operator | **DONE** | D2–D5 flip to `muse+git-mirror`; first safe bridge via `.muse/mirror/` (`209cd3f`); PR [#10](https://github.com/aaronrene/overseer-kit/pull/10) merged (Tier-3); adapter `rev-parse --abbrev-ref HEAD` fix; deploy template re-synced; **255** tests green. |
| **K8a Freeze multi-lane docs** | Thinking | **DONE** | Frozen `docs.lanes` + `docs.default_lane` schema + `governance-sync --lane` / `--all-lanes` contract (`docs/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md`). |
| **K8b Multi-lane docs build** | Auto | **DONE** | `docs.lanes` + `default_lane` in config; `governance-sync --lane` / `--all-lanes`; all-lane footprint; fixture `config-two-lane.yaml`; **266** tests green. |
| **K9a Freeze L1+L2 modules** | Thinking | **▶ NEXT** | Freeze checkpoint plugin + honesty module contracts from `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md` (L0–L3; two legs; Muse on-ramp; Track N landing seed) |
| **K9b Checkpoint plugin build** | Auto | TODO | Generic L1 orchestrator + schema; VF remains reference pack |
| **K10 Honesty module** | Thinking → Auto | TODO | Productize Track H as opt-in L2 (ledger, roles, co-requirement) |
| **K11 API/CI freeze provider** | Auto | TODO | Real headless `provider: api` + Actions example |
| **K12 / Track N** | Thinking → Auto | TODO | Public landing, scenario gallery, GitHub→MuseHub funnel |

**Vision baton (expand next):** `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md`

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
- `docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md` — frozen K5 reviewer contract (K5a); K5b builds against it
- `docs/PHASE-K6-PILOT-INSTALL-MATRIX.md` — frozen K6 pilot install matrix (K6a); K6b builds against it
- `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` — frozen K7 dogfood design (K7a); K7b builds against it
- `templates/` + `policy/` + `cursor/` — vendored footprint (K3)
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — first agent tool
- Scooling `docs/PHASE-9A-MULTI-AGENT-OVERSEER-ROUTER-OUTLINE.md` — runtime org-chart reference
