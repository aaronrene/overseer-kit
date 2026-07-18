# Overseer Kit — agent instructions

## Version control

- **Current regime: `muse+git-mirror`** (see `.overseer/config.yaml`). **MuseHub is canonical**;
  GitHub `main` is the mirror merge target only.
- Feature work: `muse commit` on a feature branch; **never** `git push origin main`.
- Mirror to GitHub only via the safe deploy script → permanent `muse-mirror` branch → PR to `main`.
- **Never** run `muse bridge git-export --git-dir .` on the dev tree (it deletes ignored files like
  `.env.local`); the bridge target is always an isolated `.muse/mirror/` checkout.
- Never force-push `main`.

See root `MUSE-BRIDGE-WORKFLOW.md` and `scripts/muse-bridge-deploy.sh` for SD-14 mirror rules.

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

## Check OK (any AI tool)

Ad-hoc honesty check — same freeze-review + build-verification path as roadmap loops.

| How | Command |
| --- | --- |
| Cursor / Claude Code | Type **Check OK** or `/check-ok` |
| Terminal (Copilot / any) | `ok check-ok --topic "<slug>"` |
| Paste prompt | `docs/CHECK-OK.md` |

Skills install to **both** `.cursor/skills/` and `.claude/skills/` on `ok sync`. Do not open a
new `docs.lanes` entry for one-offs.
