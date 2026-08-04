# Docs archive (maintainers)

Historical freezes, thinking sessions, pilot operator notes, and consumer-domain
prompts moved here before the public open-source cut.

**Not** the onboarding surface. New visitors should start at:

| Doc | Role |
| --- | --- |
| [`README.md`](../../README.md) | Product overview + install |
| [`docs/README.md`](../README.md) | Public docs index |
| [`docs/OVERSEER-KIT-SPEC.md`](../OVERSEER-KIT-SPEC.md) | Frozen architecture |
| [`docs/GIT-ONLY-QUICKSTART.md`](../GIT-ONLY-QUICKSTART.md) | Fastest GitHub-only path |

## Layout

| Path | Contents |
| --- | --- |
| `phases/` | Shipped phase freeze contracts (`PHASE-*`, multi-repo freeze) |
| `thinking/` | One-shot master prompts / vision drafts |
| `personal/` | Operator-local paste helpers (not product docs) |
| `operators/` | Live pilot runbooks against private consumer trees |
| `consumers/` | Detailed sister-product setup / domain prompts |

Freeze filenames (for example `PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY`) stay
stable as **string markers** in contracts even when the file lives under
`docs/archive/phases/`.
