# Scooling — consumer boundary (public stub)

Scooling is an **optional** product runtime that may consume Overseer Kit for
governance. It is an **optional entry** into the ecosystem and is **never
required** for kit custody, `ok init`, or baseline GitHub regimes.

## What the kit owns vs what Scooling owns

| Layer | Kit | Scooling |
| --- | --- | --- |
| Regimes / `ok` CLI / footprint | **Owns** | Consumes |
| Living docs content | Templates only | Consumer tree |
| Multi-agent product runtime | — | Consumer-owned (not vendored by the kit) |

## Hard stop — live install is operator-gated

Live `ok init` / `ok sync` against a Scooling production tree is **operator-gated**
(Tier 3 against the consumer). This stub does **not** authorize merges, staging
pushes, or live capability flips.

Track O product contract: `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`.

Stage 3 kit ceremony (optional GitHub deepen): `ok upgrade-regime` against freeze
`PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY` (`docs/archive/phases/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`).

Migrate / fixture path: `docs/MIGRATE-EXISTING-REPO.md` and
`tests/fixtures/pilot/config-scooling.yaml`.
