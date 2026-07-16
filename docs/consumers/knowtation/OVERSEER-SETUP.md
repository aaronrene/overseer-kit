# Knowtation — overseer kit setup (stub)

Kit-side stub for Track O Stage 4 (optional Knowtation bind). Full Knowtation pilot parity
(K6-style live install matrix) is a **later** operator phase — not Track O / O1.

## Regime note

Knowtation as a governed consumer may use any frozen regime from SPEC §4:

| Regime | Fit |
| --- | --- |
| `muse-only` | Preferred personal-space start (Track O Stage 1) |
| `git-only` | Full baseline without Muse (K7) |
| `muse+git-mirror` | When both substrates are ready at init |

The kit does **not** store vault bytes. Knowtation owns vault markdown/media under its own
data roots. Product bind UX associates a vault root with the same custody identity as the
governed working tree (see Track O product contract).

## Track O Stage 4 pointer

Normie custody stages (Start → Work → optional GitHub backup → optional Knowtation bind):

`docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`

Stage 3 kit upgrade ceremony (`muse-only` → `muse+git-mirror`) remains deferred to Thinking
O2 — products must not ship one-click backup yet.

## Hard stop — no live Knowtation `ok init` in O1

Live install against a Knowtation production tree is **operator-gated** (Tier 3 against the
consumer). This stub does **not** authorize:

- Live `ok init` / `ok sync` on a Knowtation checkout
- Vault credentials or absolute machine vault paths in kit docs
- Kit-hosted vault storage

When an operator later pilots Knowtation, follow the K6 operator runbook pattern
(`docs/K6-PILOT-OPERATOR-RUNBOOK.md`) with a named-repo consent gate — same discipline as
Scooling.

## What the kit owns vs what Knowtation owns

| Layer | Kit | Knowtation |
| --- | --- | --- |
| Regimes / `ok` CLI / footprint | **Owns** | Consumes |
| Vault bytes / bind UX | **Never** | **Owns** |
| Normie Stage 4 wizard | Contract only | May host bind UX (optional) |
| Account / SSO for vault | **Never** | Product-owned |

## Cross-references

- Product contract: `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md`
- Freeze: `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md`
- Scooling (first live-pilot consumer runbook): `docs/consumers/scooling/OVERSEER-SETUP.md`
- Adapter pattern: `docs/CONSUMER-ADAPTER-PATTERN.md`
