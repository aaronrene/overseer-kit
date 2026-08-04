# Knowtation — consumer boundary (public stub)

Knowtation is a sister product (personal knowledge / vault). It may optionally
bind as Track O **Stage 4**. The kit does **not** store vault bytes.

## Regime note

Any frozen regime from SPEC §4 may apply (`muse-only`, `git-only`,
`muse+git-mirror`). Muse is never required for kit baseline.

## Track O pointer

Normie custody stages (Start → Work → optional GitHub backup → optional Knowtation
bind): `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`.

Stage 3 ceremony: `ok upgrade-regime` /
`PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY`
(`docs/archive/phases/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md`).

## Hard stop — no live Knowtation `ok init` from this stub

Live install against a Knowtation production tree is **operator-gated** (Tier 3).
This stub does **not** authorize:

- Live `ok init` / `ok sync` on a Knowtation checkout
- Vault credentials or absolute machine vault paths in kit docs
- Kit-hosted vault storage

## What the kit owns vs what Knowtation owns

| Layer | Kit | Knowtation |
| --- | --- | --- |
| Regimes / `ok` CLI / footprint | **Owns** | Consumes |
| Vault bytes / bind UX | **Never** | **Owns** |
| Account / SSO for vault | **Never** | Product-owned |

## Detailed pilot notes (maintainers)

`docs/archive/consumers/knowtation/OVERSEER-SETUP.md`
