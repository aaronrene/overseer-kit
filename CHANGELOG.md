# Changelog

## Unreleased

### Added

- **`ok pr-land`** — authorized wait-for-green PR merge (`tools/close_ritual/pr_land.py`).
  Polls `gh pr checks` locally, refuses merge on failure (exit 2 for babysit),
  merges only when green. Requires `--authorized "<reason>"` (Tier-3 delegated).
  Spec: `docs/PHASE-PR-LAND-AFTER-CHECKS.md`. Policy: `policy/tiers.yaml`
  `delegated_merge_when_green`.

## 0.1.0 — 2026-07-10

### Added

- K1 Bootstrap: repository skeleton per `docs/OVERSEER-KIT-SPEC.md` §2.
- Promoted frozen architecture spec from Scooling (`OVERSEER-KIT-ARCHITECTURE-OUTLINE.md`).
- Promoted Governance Hygiene Agent spec (`PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md`).
- Kit-owned `ROADMAP.md` and `OVERSEER-HANDOVER.md` (dogfood governance).
- Placeholder policy, template, adapter, and CLI directories for K2–K6 build.
