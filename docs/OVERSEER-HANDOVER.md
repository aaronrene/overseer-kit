# Overseer Handover — Overseer Kit

**Living relay for kit development.** Paste the **NEXT SESSION** block into a fresh chat.

---

## NEXT SESSION — K4a DONE (contract frozen); start K4b build

**Date:** 2026-07-10  
**Current position:** **K4a Freeze vendoring CLI contract complete** — `init|sync|status` arg contract, exit-code taxonomy, extended `version.lock` shape, deterministic `footprint_digest` algorithm, atomicity rule, and the K4b seven-tier test matrix are frozen in `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md`. No CLI code written (Thinking phase).  
**Model:** **Auto** (spec now frozen; build mechanically)

### What just landed

| Slice | Deliverable |
| --- | --- |
| **K4a Freeze CLI contract** | `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` — frozen `init\|sync\|status` args + exit codes, `version.lock` shape (+ per-file manifest), `footprint_digest` algorithm, atomic/lock-last durability, seven-tier K4b matrix; ROADMAP + this handover synced |
| **K3 Extract shared assets** | `templates/` (4 skeletons + `tokens.yaml`); `policy/tiers.yaml`, `model-labels.yaml`, `test-tiers.yaml`; `cursor/rules/` + `cursor/skills/`; `adapters/templating.py`; 58 tests green |
| **K2 Config + adapters** | Config schema + three fail-closed VCS backends |
| **K1 Bootstrap** | Repo skeleton, promoted spec, dogfood config |

### THE ONE NEXT STEP — **Model: Auto**

**K4b Vendoring CLI build** — implement `overseer init|sync|status` + `version.lock` + drift check exactly against the K4a freeze.

| | |
| --- | --- |
| **ID** | **K4b** |
| **Branch** | `feat/k4-vendoring-cli` |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` (the freeze — build to it exactly); `docs/OVERSEER-KIT-SPEC.md` §5/§9/§10; `adapters/config.py`, `adapters/templating.py`, `adapters/runner.py` |
| **Hard stops** | No consumer repo migration (K6); no `governance-sync`/`review` (K5/9A-5); no live hooks; no `mirror`/`main` write; no main merge without review |

### Paste-ready prompt — K4b (Auto)

```
Phase K4b — Build vendoring CLI (overseer-kit).

Model: Auto. Build mechanically against the frozen contract — do not redesign.

Read first (ground truth): docs/PHASE-K4-VENDORING-CLI-CONTRACT.md.
Also: docs/OVERSEER-KIT-SPEC.md §5/§9/§10; adapters/config.py; adapters/templating.py; adapters/runner.py; cli/overseer shim.

Deliverables (exactly per the K4a freeze):
- overseer init | sync | status implemented in a cli/ Python runtime, dispatched by the existing cli/overseer POSIX shim.
- version.lock reader/writer with the frozen shape (§K4.6): lock_version, kit_version, config_version, installed_at, synced_at, footprint_digest, per-file footprint[] manifest.
- footprint_digest per §K4.7 (sorted, LF-normalized, sha256sum-style Merkle-of-manifest over the rendered footprint).
- Atomic per-file writes + version.lock written last (§K4.8); update .overseer/version.lock from sha256:pending-k4 to the real digest.
- All seven test tiers from §K4.10 green locally (unit, integration, e2e, stress, data-integrity, performance, security) under tests/.

Constraints: init/sync/status call only adapter.status() (read-only); no VCS writes, no mirror, no main. Fail-closed on every read; drift warn-only. No secrets/hardcoded SHAs.

Hard stops: no consumer migration; no governance-sync/review; no live hooks; no main merge without review.

Governance sync: update docs/ROADMAP.md (K4b DONE) + docs/OVERSEER-HANDOVER.md (snapshot, change log, next prompt) together in the closing commit; open PR under the kit's git-only rules.
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
| **Policy** | `policy/tiers.yaml`, `model-labels.yaml`, `test-tiers.yaml` — from three-repo source |
| **Cursor footprint** | `cursor/rules/` (governance-sync, tier-authority, no-docs-only-pr); `cursor/skills/` (governance-sync, freeze-review) |
| **Templating** | `adapters/templating.py` — fixed-key `{{token}}` substitution, fail-closed |
| **Tests** | 58 passing — unit, integration, security (K4b adds the §K4.10 tiers) |
| **CLI** | Contract **frozen** (`docs/PHASE-K4-VENDORING-CLI-CONTRACT.md`); shim only (`cli/overseer`) — **K4b implements** |
| **version.lock** | `sha256:pending-k4` placeholder; K4b writes the real §K4.7 digest |
| **Scooling reference** | Phase 9A runtime @ `scooling/src/phase9a/` |

## Change log

- **2026-07-10** — Governance decision captured: dogfood `muse+git-mirror` (MuseHub canonical + GitHub mirror) deferred to new **Phase K7** (operator-run). Repo stays `git-only` until then — the Muse bridge imports existing git history, so git-first now has zero rework cost. `AGENTS.md` + `ROADMAP.md` (K7 row + regime capability tiers) updated. K4b remains the next build step.
- **2026-07-10** — K4a Freeze CLI contract: `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` frozen (`init|sync|status` args + exit codes, `version.lock` shape + per-file manifest, `footprint_digest` algorithm, atomic/lock-last durability, seven-tier K4b matrix). Thinking phase — no code. ROADMAP + handover synced.
- **2026-07-10** — K3 Extract shared assets: templates, policy, cursor fragments, templating module, 58 tests green.
- **2026-07-10** — K2 Config + adapters: config validation, three backends, unit/integration/security tests.
- **2026-07-10** — K1 Bootstrap: repo created; spec promoted from Scooling; dogfood governance initialized.
