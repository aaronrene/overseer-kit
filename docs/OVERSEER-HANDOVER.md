# Overseer Handover — Overseer Kit

**Living relay for kit development.** Paste the **NEXT SESSION** block into a fresh chat.

---

## NEXT SESSION — K4b DONE; start K5a freeze reviewer

**Date:** 2026-07-10  
**Current position:** **K4b Vendoring CLI build complete** — `overseer init|sync|status` implemented in `cli/` Python runtime, dispatched by `cli/overseer` shim; `version.lock` reader/writer + §K4.7 `footprint_digest`; atomic per-file writes with lock-last durability; all §K4.10 seven-tier tests green (108 total). K4a freeze independently reviewed (`pass`, 4 rounds, PR #3 merged).  
**Model:** **Thinking** (K5a must freeze reviewer-model config schema before K5b builds)  
**Repo state:** PR [#4](https://github.com/aaronrene/overseer-kit/pull/4) (`feat/k4-vendoring-cli`) open for review; **no `main` merge without review**.

### What just landed

| Slice | Deliverable |
| --- | --- |
| **K4b Vendoring CLI** | `cli/` package: `init`, `sync`, `status`; `footprint.py`, `digest.py`, `version_lock.py`, `sync_classify.py`; shim execs `python3 -m cli.main`; `.overseer/version.lock` updated to real `sha256:54ffb06e…` digest |
| **K4a Freeze CLI contract** | `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` — reviewed `pass` (4 rounds) |
| **K3 Extract shared assets** | `templates/`, `policy/`, `cursor/`; `adapters/templating.py` |
| **K2 Config + adapters** | Config schema + three fail-closed VCS backends |
| **K1 Bootstrap** | Repo skeleton, promoted spec, dogfood config |

### THE ONE NEXT STEP — **Model: Thinking (K5a)**

**K5a Freeze reviewer** — freeze `overseer review --freeze` arg contract + extend `freeze_contract.reviewer.{mode, model, provider, fallback}` schema per `docs/OVERSEER-KIT-SPEC.md` §6.2.

| | |
| --- | --- |
| **ID** | **K5a** |
| **Branch** | `feat/k5-freeze-reviewer-contract` |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/OVERSEER-KIT-SPEC.md` §6.2; `docs/ROADMAP.md` K5 row; `policy/model-labels.yaml`; `tools/freeze_reviewer/README.md` |
| **Hard stops** | No `review --freeze` implementation (K5b); no governance-sync (9A-5); no consumer migration (K6); no `main` merge without review |

**Queued after K5a (do not start early):**
- **K5b Freeze reviewer build** (Auto) — implement `overseer review --freeze`; **K5a must freeze the reviewer-model config schema** (`local|api` provider + `fallback: human` fail-closed; spec §6.2). No core review capability may be API-only.
- **9A-5 Governance Hygiene Agent** (Auto) — `overseer governance-sync [--dry-run]`
- **K6 Pilot install** (Thinking → Auto) — `overseer init` into Scooling → Knowtation → MuseHub → VideoFactory
- **K7 Dogfood muse+git-mirror** (Thinking → Auto, operator-run) — flip this repo to MuseHub canonical + GitHub mirror. Guardrail: no core governance feature may ever be MuseHub-only (`docs/ROADMAP.md` § Regime capability tiers).

### Paste-ready prompt — K5a (Thinking)

```
Phase K5a — Freeze reviewer contract (overseer-kit).

Model: Thinking. Freeze the `overseer review --freeze` contract and the extended freeze_contract.reviewer schema — do not implement the reviewer CLI.

Read first: docs/OVERSEER-KIT-SPEC.md §6.2; docs/ROADMAP.md K5; policy/model-labels.yaml; tools/freeze_reviewer/README.md; docs/PHASE-K4-VENDORING-CLI-CONTRACT.md (pattern for freeze doc).

Deliverables: frozen contract doc for review --freeze (args, exit codes, reviewer-model config schema with local|api provider + fallback: human); seven-tier test matrix for K5b; governance sync on completion.

Hard stops: no K5b build; no governance-sync; no main merge without review.
```

---

## Verified snapshot

| Area | State |
| --- | --- |
| **Kit version** | `0.1.0` (`VERSION`) |
| **Spec** | Frozen in `docs/OVERSEER-KIT-SPEC.md` |
| **Config schema** | `adapters/config.py` — version 1, regimes `muse+git-mirror` \| `muse-only` \| `git-only` |
| **VCS adapters** | `adapters/git_only/`, `muse_only/`, `muse_git_mirror/` — §4 interface, fail-closed reads |
| **Templates** | `templates/*.template.md` — handover, roadmap, standing decisions, coordination |
| **Policy** | `policy/tiers.yaml`, `model-labels.yaml`, `test-tiers.yaml` |
| **Cursor footprint** | `cursor/rules/` + `cursor/skills/` (source); vendored to `.cursor/` on `init` |
| **Templating** | `adapters/templating.py` — fixed-key substitution, fail-closed |
| **CLI** | `cli/overseer` shim → `cli/main.py`; `init` \| `sync` \| `status` per `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` |
| **version.lock** | Full §K4.6 shape; `footprint_digest: sha256:54ffb06e01c8026c9c1cca3ad2c5086d4386d1cb2668fc5c67576bd6d13beb12` |
| **Tests** | **108 passing** — unit, integration, e2e, stress, data-integrity, performance, security (§K4.10) |
| **Scooling reference** | Phase 9A runtime @ `scooling/src/phase9a/` |

## Change log

- **2026-07-10** — K4b Vendoring CLI build: `cli/` package with `init|sync|status`, `version.lock` reader/writer, §K4.7 `footprint_digest`, atomic lock-last writes; shim dispatches to Python; 108 tests green across seven tiers; `.overseer/version.lock` updated from `sha256:pending-k4` to computed digest. ROADMAP + handover synced. PR #4.
- **2026-07-10** — K5 reviewer-model config requirement frozen: `freeze_contract.reviewer.{mode, model, provider, fallback}` schema captured in `docs/OVERSEER-KIT-SPEC.md` §6.2 and `docs/ROADMAP.md` K5 row. `provider: local` is first-class; fail-closed to `human` if unreachable; model is a label, never a vendor slug. K5a Thinking must freeze this schema before K5b builds the reviewer.
- **2026-07-10** — K4a freeze **independently reviewed over 4 rounds** (dogfood of §6 Freeze-Step Reviewer, `gpt-5.3-codex`, all findings cited file+line): `blocked → blocked → blocked → pass`. Round 1 (1 BLOCKER + 6 MAJOR + 2 MINOR): init rule, `--only` semantics, exit precedence, `last_governance_sync`, exit `5` wording, absolute-path ban, skills glob, standing-decisions, digest newline. Round 2 (destination collision, `--verbose` carve-out, carried digest). Round 3 (**ADR skeleton silently dropped** → fixed: SD skeleton always vendored to `.overseer/STANDING-DECISIONS.reference.md`, `docs.standing_decisions` is a pointer only). Round 4: `pass` + pinned `--only` to destination-path matching. Full 4-round review record in the contract's freeze block. Fixed on PR #3.
- **2026-07-10** — Governance decision captured: dogfood `muse+git-mirror` (MuseHub canonical + GitHub mirror) deferred to new **Phase K7** (operator-run). Repo stays `git-only` until then. `AGENTS.md` + `ROADMAP.md` (K7 row + regime capability tiers) updated.
- **2026-07-10** — K4a Freeze CLI contract: `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` frozen. Thinking phase — no code. ROADMAP + handover synced.
- **2026-07-10** — K3 Extract shared assets: templates, policy, cursor fragments, templating module, 58 tests green.
- **2026-07-10** — K2 Config + adapters: config validation, three backends, unit/integration/security tests.
- **2026-07-10** — K1 Bootstrap: repo created; spec promoted from Scooling; dogfood governance initialized.
