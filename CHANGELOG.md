# Changelog

## v1.0.0-rc.1 — published 2026-10-10

The bounded local CLI prerelease is published, not stable and not Latest. Its tag
remains at `293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`; all five assets are unchanged.
The seven commands are `status`, `init`, `sync`, `adopt`, `mirror`, `next`, and
`next-write`. Git-only use remains permanent; Muse adoption and mirroring are
explicit. Mirror repair and combined validation are complete.

PR #87 later published the documentation closeout. Production deployment succeeded,
and post-merge CI passed 156 / 156 / 289 tests with zero failures, errors or skips.
No recovery task remains. See [the current summary](docs/ROADMAP.md).

## Historical records

The entries below describe earlier source milestones, including the pre-reset
historical product. Their command lists are not the bounded-v1 entrypoint contract.
The `1.0.0` source milestone was not a stable release. Use the [README](README.md)
and [docs index](docs/README.md) for current commands.

## Historical source milestone: 1.0.0 — 2026-10-08

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
