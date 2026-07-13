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
| **KH2a Muse-sync hard gate** | Thinking | **DONE** | **Fail-closed Muse-sync gate** freeze — `docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md` **reviewed → `pass` (KH2-r2)**. Closes the gap this exact repo hit live: Git committing ahead of Muse with nothing catching it (KH1b's substrate health only checks `.muse/` file **presence**, never content freshness). Freezes `StatusResult.muse_dirty`/`git_dirty` field additions, the `tools/muse_sync/` probe (`MuseSyncReport` / `check_muse_sync`), the precise frozen trigger (`muse_dirty and not git_dirty` — Git clean, Muse stale; mid-edit "both dirty" is a frozen non-trigger, never blocked), the three wiring points (`status --exit-code`, `review --freeze`, `governance-sync`, all reusing exit code `2` — no renumbering of the frozen `2 > 6 > 3 > 0` precedence), and the seven-tier matrix. Documented boundary: does not catch drift re-masked by a later uncommitted edit (deferred, separate scope). Cleared for KH2b. |
| **KH2b Muse-sync hard gate build** | Auto | **DONE** | Built mechanically against the frozen `docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md`: `StatusResult.muse_dirty`/`git_dirty` (all three adapters); `tools/muse_sync/` (`MuseSyncReport`, `check_muse_sync`); wired into `cli/commands/status.py` (`_exit_code_from_conditions` extended, additive `muse_sync` JSON key), `cli/commands/review.py` (refuses before any review provider runs), `tools/governance_hygiene/reads.py` (`perform_verified_reads` returns `ReadFailure("muse-sync", ...)`, mapped to exit `2` by the existing `run_governance_sync`); seven-tier tests (**456** total green, +27 §KH2.8). Repo's own live drift (Git ahead of Muse by 2 commits) caught up via `muse commit` as Tier-1 hygiene in the same session. |
| **KH3a Footprint self-integrity hard gate** | Thinking | **DONE** | **Fail-closed footprint self-integrity gate** freeze — `docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md` **reviewed → `pass` (KH3-r2)**. Direct response to this exact repo's own live incident: 13 kit-owned files (`.cursor/rules/*`, `.cursor/skills/*/SKILL.md`, `.overseer/policy/*.yaml`, `.overseer/STANDING-DECISIONS.reference.md`) were declared in `version.lock` since K4b but never actually rendered, and nothing automated ever objected because the existing footprint check is an opt-in `--check-footprint` flag not wired into `review --freeze`/`governance-sync`. Freezes `tools/footprint_integrity/` (`FootprintIntegrityReport` / `check_footprint_integrity`), the narrow frozen trigger (declared in `version.lock` with non-`preserved` origin, absent from disk — deliberately **existence-only**, never content-hash, to avoid false-closing on the same benign drift class §KH2/this session already hit for `scripts/muse-bridge-deploy.sh`), the three wiring points (`status --exit-code`, `review --freeze`, `governance-sync`, all reusing exit code `2`), and the seven-tier matrix. R1-M1 (fixed in KH3-r2): narrowed scope from "any digest mismatch" to "declared-but-absent only," specifically to avoid consumer-repo blast radius. Cleared for KH3b. |
| **KH3b Footprint self-integrity hard gate build** | Auto | **DONE** | Built mechanically against the frozen `docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md`: new `tools/footprint_integrity/` (`FootprintIntegrityReport`, `check_footprint_integrity`); wired into `cli/commands/status.py` (`_exit_code_from_conditions` extended with `footprint_self_integrity_ok`, additive `footprint_self_integrity` JSON key, always-on — no flag needed), `cli/commands/review.py` (refuses before any review provider runs), `tools/governance_hygiene/reads.py` (`perform_verified_reads` returns `ReadFailure("footprint-self-integrity", ...)`, mapped to exit `2`); seven-tier tests (**486** total green, +30 §KH3.8). **Build-time refinement from the frozen spec** (documented transparently, not a redesign): the gate checks existence against what `version.lock` **already declares** rather than re-resolving the current kit templates via `resolve_footprint` — strictly narrower and more precise to the actual incident (a live template not yet synced is *drift*, already covered elsewhere, not "declared but missing"), and avoids false-closing on lightweight test fixtures with synthetic/empty locks. This session's own remaining `footprint_self_integrity: ok` confirmed on the live repo. |
| **Track P / P0** | Thinking | **DONE** | **Agent identity & signed provenance** freeze — `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md` **reviewed → `pass` (P0-r2)**, stamp digest `sha256:7db8681…`. Optional `provenance` envelope (`agent_id`/`model_id`/Ed25519 `sig`) on ledger entries; canonical hash excludes `provenance.sig` (v1 chain unbroken); soft under git-only, hard under Muse. Shared schema with Muse social domain. Social stays consumer-only. |
| **Track P / P1** | Auto | **DONE** | **Build verified → `pass` (P1-BV-r2).** Optional `provenance` envelope + Ed25519 verify + `require_agent_signature` + exit codes `25`/`26`; canonical hash excludes `provenance.sig` (v1 chain unbroken). Build-verification round 1 raised **BV1** (§P0.6 parity: `verify` did not emit `2` on hash-consistent malformed provenance) → fixed in `tools/honesty/ledger.py` `verify_chain` + CLI message + regression test; round 2 **`pass`**. **429** tests green (+30 §P0.8). Muse adapter plain-text SHA fix: `_muse_rev_parse_sha` reads bare stdout (0.2.x returns plain SHA on success); `governance-sync --dry-run` exits 0. First muse canonical commit `sha256:4671b7f…`; GitHub bridge PR #15 (`muse-mirror → main`). |
| **Track P / P-route** | Thinking | **DONE** | **Declarative model-routing policy** freeze — `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` **reviewed → `pass` (P-route-r2)**, stamp digest `sha256:ab6b6a9…`. Freezes the `policy/model-routing.yaml` schema (`{position, phase_tier, gate} → model_tier + fallback`; first-match-wins + mandatory `defaults` terminal; `fallback[0] == model_tier`, terminating in `human`), the additive `model_tiers` extension to `policy/model-labels.yaml` (abstract capability tiers, no vendor slugs), an optional default-inert `model_routing:` config block, a read-only `overseer route` surface + exit codes `30`/`31`, the rule-holder-not-executor boundary table, and the seven-tier matrix. Runtime (Cursor / OpenRouter / Scooling 9A) is the executor; **no model calls in the kit.** Cleared for the P-route Auto build. |
| **Track P / P-route build** | Auto | **DONE** | **Build verified → `pass` (P-route-BV-r1).** Vendored `policy/model-routing.yaml` (v1, first-match-wins + mandatory `defaults`; `fallback[0] == model_tier` terminating in `human`); extended `policy/model-labels.yaml` with `model_tiers`; optional default-inert `model_routing:` config; read-only `overseer route` (resolve / `--validate` / explain — no dispatch, no network, no key); exit codes `30`/`31`; `overseer status` routing-validity line when `enabled: true`. **529** tests green (+43 §PR.8). Kit = rule-holder, runtime = executor. |
| **Track P / P-cost** | Thinking | **DONE** | **Cost-awareness surface** (not a dollar pricer) freeze — `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` **reviewed → `pass` (P-cost-r2)**, stamp digest `sha256:9f26678…`. Freezes an optional, ordinal, currency-free `cost_class` (`free < low < moderate < high`) on each `model_tiers[]` entry; a deterministic `paid_step_before_spend` derivation (`free` + reserved `human` unpaid; absent band conservatively paid); additive `cost_class` + `paid_step_before_spend` annotation on the read-only `overseer route` output; an optional default-inert `cost_awareness:` config block; a read-only active-slice spend-awareness surface on `overseer status` + the `governance-sync` footer (reusing the §KH1.9 active-slice scan; reminder-only, never blocks); exit code `32` (malformed cost metadata, confined to `overseer route`); the boundary table (kit declares bands, runtime converts to dollars/budgets/spend); the seven-tier matrix. **No dollar amount, currency, budget, spend cap, network call, or model call in the kit** — price-agnostic by design. Cleared for the P-cost Auto build. |
| **Track P / P-cost build** | Auto | **DONE** | **Build verified → `pass` (P-cost-BV-r1).** Built mechanically against frozen `docs/PHASE-TRACK-P-P-COST-AWARENESS.md`: optional `cost_class` on `model_tiers` (closed vocabulary `free\|low\|moderate\|high`; recognized key); `paid_step_before_spend` derivation; additive `cost_class` + `paid_step_before_spend` on `overseer route`; optional `cost_awareness:` config (`enabled` default `false`, `surfaces` default `[status, governance-sync]`); active-slice spend-awareness surface on `overseer status` (+ `--json`) and `governance-sync` footer + handover template reminder; exit `32` (malformed cost metadata, confined to `overseer route`); **569** tests green (+40 §PC.9). Kit = cost-awareness rule-holder, runtime = spender. |
| **Track P / P-evidence** | Thinking | **DONE** | **Verification evidence capture** freeze — `docs/PHASE-TRACK-P-P-EVIDENCE.md` **reviewed → `pass` (P-evidence-r3)**, stamp digest `sha256:c1b9fb3…`. Freezes ledger kind `verification_evidence` (additive to K9a enum); closed artifact types `test_output`\|`deploy_health`\|`screenshot` (hashes + opaque refs; no blobs in ledger); `honesty.require_verification_evidence: off\|warn\|require` (default `off`; `HONESTY_KEYS` membership); honesty-status Mode A/B mutual exclusion (`--verification-evidence` / `--frozen-spec`); exit `33` + error token `missing_verification_evidence`; normative build-verification V8 + Evidence table delta; boundary table (kit records/gates claims, never deploys). Closes build-verification V8 durability gap. Cleared for the P-evidence Auto build. **Spec-only — no code landed.** |
| **Track P / P-evidence build** | Auto | **DONE** | Built against frozen `docs/PHASE-TRACK-P-P-EVIDENCE.md` → `/build-verification-review` **`pass` (P-evidence-BV-r1)**. Shipped: ledger kind `verification_evidence` + `validate_verification_artifacts`; `honesty.require_verification_evidence`; honesty-status Mode B (`--verification-evidence` / `--frozen-spec`); exit `33` + `missing_verification_evidence`; twin build-verification V8 + Evidence table skill delta. **612** tests green (+43 §PE.10). Kit records/gates claims; never deploys. |
| **Track Q / Q0 Freeze Overseer App** | Thinking | **DONE** | **Overseer App freeze** — `docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` **reviewed → `pass` (Q0-r2)**, stamp digest `sha256:3c3f6229…`. Freezes `overseer app`: local-only web UI over the existing Python engine (zero rewrite); closed `api/*` read/act surface (status, ROADMAP/HANDOVER, review --freeze, governance-sync, ledger, honesty-status); bind default `127.0.0.1` (+ `localhost`/`::1`); Bearer + CSRF-header auth; stdlib HTTP server (FastAPI not required); fail-closed CLI parity; seven-tier §Q0.12 matrix. **Boundary:** frontend/distribution of governance, never runtime. **Spec-only — no code landed.** Cleared for Q1 Auto build. |
| **Track Q / Q1 Local web UI build** | Auto | **DONE** | **Build verified → `pass` (Q1-BV-r1).** Built against frozen `docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md`: `overseer app` stdlib loopback server (`tools/app/`) + static UI; `cli/commands/app.py`; closed `api/*` handlers calling existing engine; Bearer + CSRF auth; inert-first writes; seven-tier §Q0.12. **654** tests green (+42 §Q0.12). |
| **Track Q / Q2a Freeze OK CLI entrypoint** | Thinking | **DONE** | **Canonical CLI rename freeze** — `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md` **reviewed → `pass` (Q2a-r2)**. Freezes `ok` as the standard POSIX entrypoint (`cli/ok` → `python -m cli.main`); `argparse` prog `ok`; operator-facing docs/templates prefer `ok status`, `ok app`, etc. **`cli/overseer` remains a compatibility shim** (same runtime; one-line stderr deprecation per process). Amends K4/SPEC §5 entrypoint naming without changing subcommands, exit codes, or `.overseer/` config paths. Engine shims are **not** footprint members (corrects earlier Q2b “footprint + version.lock entry” wording). Seven-tier §Q2A.10 matrix. **Spec-only — no code landed.** Cleared for Q2b. |
| **Track Q / Q2b OK CLI entrypoint build** | Auto | **TODO** | Implement frozen Q2a: ship `cli/ok` + `cli/overseer` compat deprecation; `prog="ok"`; operator docs/templates/CI/`AGENTS.md` pass; SPEC §5 + K4.1 naming amendment; seven-tier §Q2A.10 tests. **No** footprint/`version.lock` manifest row for shims. **Gated on Q2a freeze review → `pass` + `/build-verification-review`.** |
| **Track Q / Q3 Tauri desktop packaging** | Auto | **TODO** | Package Q1's local web UI into an installable cross-platform desktop app using **Tauri** (bundles the Python engine + serves the same localhost UI in a native window; macOS/Windows/Linux from one codebase). Launcher invokes **`ok app`** (post Q2b). No new engine logic — packaging only. Native macOS/SwiftUI explicitly deferred. **Gated on Q2b DONE + `/build-verification-review`.** |
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
- `docs/PHASE-TRACK-P-P0-AGENT-PROVENANCE.md` — Track P / P0 agent-provenance freeze (reviewed → `pass`); P1 built against it
- `docs/PHASE-TRACK-P-P-ROUTE-MODEL-ROUTING.md` — Track P / P-route model-routing policy freeze (**reviewed → `pass`, P-route-r2**); the P-route Auto build builds against it
- `docs/PHASE-TRACK-P-P-COST-AWARENESS.md` — Track P / P-cost cost-awareness surface freeze (**reviewed → `pass`, P-cost-r2**, stamp `sha256:9f26678…`); the P-cost Auto build builds against it
- `docs/PHASE-TRACK-P-P-EVIDENCE.md` — Track P / P-evidence verification-evidence capture freeze (**reviewed → `pass`, P-evidence-r3**, stamp `sha256:c1b9fb3…`); the P-evidence Auto build builds against it
- `docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md` — Track Q / Q0 Overseer App freeze (**reviewed → `pass`, Q0-r2**, stamp `sha256:3c3f6229…`); Q1 built against it
- `docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md` — Track Q / Q2a OK CLI entrypoint freeze (**reviewed → `pass`, Q2a-r2**); Q2b builds against it
- `docs/PHASE-KH2-MUSE-SYNC-HARD-GATE.md` — KH2 Muse-sync hard gate freeze (**reviewed → `pass`, KH2-r2**) + Auto build, both **DONE**
- `docs/PHASE-KH3-FOOTPRINT-INTEGRITY-HARD-GATE.md` — KH3 footprint self-integrity hard gate freeze (**reviewed → `pass`, KH3-r2**) + Auto build, both **DONE**
- `docs/CONSUMER-ADAPTER-PATTERN.md` — consumer plug-in pattern
- `docs/consumers/` — per-consumer reference adapters (not kit architecture)
- `templates/` + `policy/` + `cursor/` — vendored footprint (K3)
- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — first agent tool
- Scooling `docs/PHASE-9A-MULTI-AGENT-OVERSEER-ROUTER-OUTLINE.md` — runtime org-chart reference
