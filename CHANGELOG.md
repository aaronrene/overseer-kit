# Changelog

## Unreleased

### Added

- Bounded v1 command surface: `status`, `init`, `sync`, `next`, and `next-write`.
- Persistent per-checkout UUID and physical-root binding.
- Canonical `docs/NEXT.md` with repository, branch, lane, model-label, action,
  prompt-digest, expected-digest, and Git-freshness validation.
- Repository-bound launchers with isolated source-installation imports.
- Confined atomic NEXT writes and stale-writer refusal.
- Optional read-only Cursor hooks; disabled by default.
- Clean source installation, current/previous rollback, and authorized DINERO
  pilot validation.

### Changed

- Reset the supported product to a small trusted-host local Git handoff utility.
- Preserve former CLI and tests as historical sources outside the public v1 surface.
- Document opt-in GitHub Release notifications and explicit Git pull/sync updates;
  no automatic update check or background network access was added.

## 0.1.0 — 2026-07-10

### Added

- K1 Bootstrap: repository skeleton per `docs/OVERSEER-KIT-SPEC.md` §2.
- Promoted frozen architecture spec from Scooling (`OVERSEER-KIT-ARCHITECTURE-OUTLINE.md`).
- Promoted Governance Hygiene Agent spec (`PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md`).
- Kit-owned `ROADMAP.md` and `OVERSEER-HANDOVER.md` (dogfood governance).
- Placeholder policy, template, adapter, and CLI directories for K2–K6 build.
