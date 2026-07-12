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
| **K9a Freeze L1+L2 modules** | Thinking | **DONE** | Contract in `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md`. Rounds 1–8 → `findings` + fixes; **K9a-r9 → `pass`** (all prior findings confirmed RESOLVED; full §K9.0–§K9.19 regress clean). Cleared for K9b (L1) and K10 (L2). |
| **K9b Checkpoint plugin build** | Auto | **DONE** | L1 `verify-step` orchestrator + config parse + fixture pack + seven-tier tests (**302** green) |
| **KH1 Handover relay standard** | Thinking | **DONE** | **KH1-r2 → `pass`.** Contract + dogfood handover aligned; §KH1.6 close-out complete (🆗 branding lock + Track P seed). |
| **KH1b Substrate + gate reminders** | Auto | **DONE** | **§1 substrate health:** `tools/substrate_health/` fail-closed on hollow `.muse/`. **§2 gate reminders:** `tools/governance_gates/` + `governance_gates` config + `overseer status` pending-gates + `governance-sync` footer + handover template checklist (§KH1.9). **399** tests green. |
| **Track P / P0** | Thinking | **DONE** | **Agent identity & signed provenance** freeze — `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md` **reviewed → `pass` (P0-r2)**, stamp digest `sha256:7db8681…`. Optional `provenance` envelope (`agent_id`/`model_id`/Ed25519 `sig`) on ledger entries; canonical hash excludes `provenance.sig` (v1 chain unbroken); soft under git-only, hard under Muse. Shared schema with Muse social domain. Social stays consumer-only. |
| **Track P / P1** | Auto | **DONE** | **Build verified → `pass` (P1-BV-r2).** Optional `provenance` envelope + Ed25519 verify + `require_agent_signature` + exit codes `25`/`26`; canonical hash excludes `provenance.sig` (v1 chain unbroken). Build-verification round 1 raised **BV1** (§P0.6 parity: `verify` did not emit `2` on hash-consistent malformed provenance) → fixed in `tools/honesty/ledger.py` `verify_chain` + CLI message + regression test; round 2 **`pass`**. **429** tests green (+30 §P0.8). Muse adapter plain-text SHA fix: `_muse_rev_parse_sha` reads bare stdout (0.2.x returns plain SHA on success); `governance-sync --dry-run` exits 0. First muse canonical commit `sha256:4671b7f…`; GitHub bridge PR #15 (`muse-mirror → main`). |
| **Track P / P-route** | Thinking → Auto | **TODO** | **Declarative model-routing policy** (not a runtime dispatcher). `policy/model-routing.yaml`: map `position/phase-tier/gate → model tier + fallback`; the *runtime* (Cursor, OpenRouter, Scooling) consumes it. Kit stays the rule-holder, never the executor. Extends `policy/model-labels.yaml`. **Needs Thinking freeze (P0-style) before build.** No model calls added to the kit. |
| **Track P / P-cost** | Thinking → Auto | **TODO** | **Cost-awareness surface** (not a dollar pricer). Surface each phase's tier/position + a "paid step before spend" flag on `overseer status` / handover (aligns with vision §1.2 fail-closed-before-spend). Actual dollar math stays in the runtime that knows its provider/OpenRouter prices — kit is price-agnostic by design. **Needs Thinking freeze before build.** |
| **Track P / P-evidence** | Thinking → Auto | **TODO** | **Verification evidence capture.** Extend build-verification + honesty ledger to record verification artifacts (test-output hash, deploy/health check ref, screenshot ref) as ledger evidence — closes the "claims vs verifiable state" gap (build-verification V8). Reuses the L2 ledger. **Needs Thinking freeze before build.** |
| **Track Q / Q0 Freeze Overseer App** | Thinking | **TODO** | Freeze contract for `overseer app`: local-only web UI **over the existing Python engine** (zero engine rewrite — reuses `cli/`/`tools/`/`adapters/` as-is); scope = read/act on `status`, `ROADMAP`/`HANDOVER`, `review --freeze`, `governance-sync`, `ledger`/`honesty-status`; bind `127.0.0.1`-only (no LAN/remote exposure by default); auth story for a local server; fail-closed parity with the CLI (no new capabilities, no bypass of gates); seven-tier matrix. **Boundary:** a frontend/distribution of governance, never a runtime/dispatcher/model-host. Contract doc: `docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` (to be drafted). |
| **Track Q / Q1 Local web UI build** | Auto | **TODO** | Build `overseer app` against the frozen Q0 contract: FastAPI/stdlib localhost server + minimal web frontend calling the existing engine functions directly (no HTTP re-implementation of CLI logic); read-only views first (status/roadmap/handover/gates), then gated write actions (`review --freeze`, `governance-sync`) behind the same fail-closed checks as the CLI. **Gated on `/build-verification-review`.** |
| **Track Q / Q2 Tauri desktop packaging** | Auto | **TODO** | Package Q1's local web UI into an installable cross-platform desktop app using **Tauri** (bundles the Python engine + serves the same localhost UI in a native window; macOS/Windows/Linux from one codebase). No new engine logic — packaging only. Native macOS/SwiftUI explicitly deferred (would either shell out to the same CLI or require a full parallel rewrite — not worth it before Q1 proves demand). **Gated on `/build-verification-review`.** |
| **K10 Honesty module** | Auto | **DONE** | L2 `honesty-status` + `ledger {append,verify,show}` + role gates + fixture pack + seven-tier tests (**340** green); SPEC §5 updated |
| **K11 API/CI freeze provider** | Auto | **DONE** | Headless `provider: api` HTTP client (`/health`, `/review`) + `OVERSEER_REVIEW_API_KEY`/`OVERSEER_REVIEW_API_URL` + GitHub Actions example + `templates/ci/` vendored workflow; seven-tier K11 tests (**361** green) |
| **K12 / Track N** | Thinking → Auto | **DONE** | Public landing, scenario gallery, GitHub→MuseHub funnel, Apache-2.0 LICENSE, SECURITY.md; `tools/landing/` validator; seven-tier K12 tests (**380** total green) |

**Vision baton:** `docs/OVERSEER-KIT-LAYERED-HONESTY-VISION.md` (expanded)  
**K9a contract:** `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md`  
**Consumer pattern:** `docs/CONSUMER-ADAPTER-PATTERN.md`  
**Handover UX debt:** none (KH1 + KH1b **DONE**)

## Exploration backlog (ideas — NOT queued; each needs its own Thinking freeze before it becomes a phase)

These are captured so they are not lost. None are committed scope. Each must pass a P0-style Thinking
freeze (and clear the "governance, not runtime" boundary) before entering the build queue.

| Idea | Sketch | Boundary check |
| --- | --- | --- |
| **P-deploy — deployment gate** | Live-deploy sibling of build-verification: a gate that records a verifiable deploy/health check before a "shipped" claim can be marked DONE. Fits the transcript's "always-on agent with root access deploying to public URLs" risk. | Kit records/gates the *claim*; it never performs the deploy. |
| **Hosted governance dashboard** | Read-only web view of a repo's governance state (roadmap/handover/gates) sourced from GitHub/MuseHub APIs — for "see my org's governance at a glance" without a local install. Distinct from Track Q (queued below): this variant is hosted/remote and read-only; it cannot touch local repos, git, or muse. | Read-only; the authoritative workflow stays local (repo + git/muse). |
| **P-route runtime reference** | An *example* runtime adapter (in a consumer repo, e.g. Scooling) that consumes `P-route` policy + OpenRouter — to prove the policy end-to-end. | Lives in a consumer, not the kit (per `AGENTS.md` — Scooling 9A router is reference-only). |

## Dogfood integrity gate (mandatory — not optional)

When `vcs.regime` is `muse+git-mirror` or `muse-only`, **`overseer status --exit-code` must report `substrate.ok: true`** before any phase on this repo is marked DONE. Hollow `.muse/` (config flip without K7 D2 `muse init`) is the exact Muse↔Git inversion failure mode this kit exists to catch. Remediation: `muse init --force .` (Tier 1).

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
- `docs/PHASE-K8-MULTI-LANE-DOCS-CONTRACT.md` — frozen K8 multi-lane docs (K8a); K8b builds against it
- `docs/PHASE-K9A-L1-L2-MODULE-FREEZE.md` — K9a L1+L2 module freeze (**K9a-r9 → `pass`**); K9b/K10 build against it
- `docs/PHASE-K12-TRACK-N-LANDING-CONTRACT.md` — K12 Track N landing freeze (K12 build against it)
- `docs/PHASE-KH1-HANDOVER-RELAY-STANDARD.md` — KH1 handover relay standard (Thinking freeze; D4 shape checklist)
- `docs/CONSUMER-ADAPTER-PATTERN.md` — consumer plug-in pattern
- `docs/consumers/` — per-consumer reference adapters (not kit architecture)
- `templates/` + `policy/` + `cursor/` — vendored footprint (K3)
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — first agent tool
- Scooling `docs/PHASE-9A-MULTI-AGENT-OVERSEER-ROUTER-OUTLINE.md` — runtime org-chart reference
