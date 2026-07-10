# Overseer Kit — agent instructions

## Version control

- **Current regime: `git-only`** (see `.overseer/config.yaml`). GitHub is canonical **today**.
- Default workflow: feature branch → commit → push → PR → merge to `main`.
- Never force-push `main`.

### Planned: dogfood `muse+git-mirror` (Phase K7 — tracked, not yet active)

The kit sells `muse+git-mirror` as a first-class regime (`docs/OVERSEER-KIT-SPEC.md` §4/§8) but does
not yet dogfood it. Phase **K7** will flip this repo to **MuseHub canonical + GitHub mirror**, matching
how Scooling/Knowtation operate. Until K7 lands, this repo stays `git-only` — **do not** claim Muse is
canonical here or run `muse` commands against it.

When K7 is active, the SD-14 mirror rule applies (as in `scooling/AGENTS.md`,
`knowtation/AGENTS.md`, and their root `MUSE-BRIDGE-WORKFLOW.md`):
- Work is `muse commit` on a feature branch; **never** `git push origin main`.
- Mirror to GitHub only via the safe deploy script → permanent `muse-mirror` branch → PR to `main`.
- **Never** run `muse bridge git-export --git-dir .` on the dev tree (it deletes ignored files like
  `.env.local`); the bridge target is always an isolated `.muse/mirror/` checkout.

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
