# Docs archive (maintainers)

Historical freezes and architecture vision moved here so the public root stays
product-facing.

**Not** the onboarding surface. New visitors should start at:

| Doc | Role |
| --- | --- |
| [`README.md`](../../README.md) | Product overview + install |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | How to propose changes |
| [`docs/README.md`](../README.md) | Public docs index |
| [`docs/OVERSEER-KIT-SPEC.md`](../OVERSEER-KIT-SPEC.md) | Frozen architecture |
| [`docs/GIT-ONLY-QUICKSTART.md`](../GIT-ONLY-QUICKSTART.md) | Fastest GitHub-only path |
| [`docs/MIGRATE-EXISTING-REPO.md`](../MIGRATE-EXISTING-REPO.md) | `init --migrate` for existing docs |

## Layout

| Path | Contents |
| --- | --- |
| `phases/` | Shipped phase freeze contracts (`PHASE-*`, multi-repo freeze) |
| `thinking/` | Architecture vision drafts (kit history, not operator personal notes) |

Personal paste helpers, private consumer pilot packs, and machine-local operator
runbooks are **not** stored in this repository.

Freeze filenames (for example `PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY`) stay
stable as **string markers** in contracts even when the file lives under
`docs/archive/phases/`.
