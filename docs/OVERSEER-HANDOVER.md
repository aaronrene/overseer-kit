# Overseer Handover — Overseer Kit

**Living relay for kit development.** Paste the **NEXT SESSION** block into a fresh chat.

---

## NEXT SESSION — K2 DONE; start K3 extract shared assets

**Date:** 2026-07-10  
**Current position:** **K2 Config + VCS adapters complete** — config schema validation + three fail-closed backends + tests.  
**Model:** **Auto**

### What just landed

| Slice | Deliverable |
| --- | --- |
| **K2 Config + adapters** | `adapters/config.py` fail-closed schema; `git_only/`, `muse_only/`, `muse_git_mirror/` backends; 48 unit/integration/security tests green |
| **K1 Bootstrap** | Repo skeleton, promoted spec, dogfood config |

### THE ONE NEXT STEP — **Model: Auto**

**K3 Extract shared assets** — move handover/roadmap/SD-format/tier/model-label/test-tier policy into `templates/` + `policy/` + `cursor/`, token-parameterized.

| | |
| --- | --- |
| **ID** | **K3** |
| **Branch** | `feat/k3-extract-assets` |
| **Repo** | **overseer-kit** |
| **Read first** | `docs/OVERSEER-KIT-SPEC.md` §2; Scooling/Knowtation/MuseHub governance docs |
| **Hard stops** | No consumer repo migration (K6); no live hooks |

### Paste-ready prompt — K3

```
Phase K3 — Extract shared governance assets into templates + policy + cursor (overseer-kit).

Model: Auto.

Read first: docs/OVERSEER-KIT-SPEC.md §2; docs/ROADMAP.md; Scooling/Knowtation/MuseHub handover + roadmap + coordination docs.

Deliverables:
- templates/ (OVERSEER-HANDOVER, ROADMAP, STANDING-DECISIONS, CROSS-REPO-COORDINATION) with token substitution
- policy/ tiers, model-labels, test-tiers finalized from three-repo source
- cursor/ rules + skills fragments vendored from existing repos

Hard stops: no consumer repo migration (K6); no live hooks; no main merge without review.

Governance sync: update docs/ROADMAP.md + this file on completion.
```

---

## Verified snapshot

| Area | State |
| --- | --- |
| **Kit version** | `0.1.0` (`VERSION`) |
| **Spec** | Frozen in `docs/OVERSEER-KIT-SPEC.md` |
| **Config schema** | `adapters/config.py` — version 1, regimes `muse+git-mirror` \| `muse-only` \| `git-only` |
| **VCS adapters** | `adapters/git_only/`, `muse_only/`, `muse_git_mirror/` — §4 interface, fail-closed reads |
| **Tests** | 48 passing — `tests/unit/`, `tests/integration/`, `tests/security/` |
| **CLI** | Stub only (`cli/overseer` prints not-implemented) — K4 |
| **Templates / policy** | Placeholder dirs — K3 |
| **Scooling reference** | Phase 9A runtime @ `scooling/src/phase9a/` |

## Change log

- **2026-07-10** — K2 Config + adapters: config validation, three backends, unit/integration/security tests.
- **2026-07-10** — K1 Bootstrap: repo created; spec promoted from Scooling; dogfood governance initialized.
