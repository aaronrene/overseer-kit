# Overseer Kit — agent instructions

## Version control

- **Git-only** for this repo (see `.overseer/config.yaml`).
- Default workflow: feature branch → commit → push → PR → merge to `main`.
- Never force-push `main`.

## Read first

- `docs/OVERSEER-KIT-SPEC.md` — frozen architecture; do not redesign during Build phases.
- `docs/ROADMAP.md` — phase control + Build status table.
- `docs/OVERSEER-HANDOVER.md` — living relay; update with ROADMAP on phase completion.

## Boundaries

- This kit is **repo-agnostic governance** — not a product runtime.
- Scooling Phase 9A (`src/phase9a/`) is a **reference** for worker/checker/foreman patterns; do not copy product adapters into the kit.
- Consumer repos customize via `.overseer/config.yaml` only.

## Tests

Seven-tier tests (unit, integration, e2e, stress, data-integrity, performance, security) for every Build phase that adds code.

## Governance sync

On phase completion, update **both** `docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` in the closing commit.
