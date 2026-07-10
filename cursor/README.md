# Cursor fragments — vendored into consumer `.cursor/` on init/sync

Portable rules and skills extracted from Scooling, Knowtation, and MuseHub governance docs.
Token placeholders (`{{repo.name}}`, etc.) are substituted from `.overseer/config.yaml` at vendoring time.

| Path | Purpose |
| --- | --- |
| `rules/governance-sync.mdc` | SD-17 mandatory roadmap + handover sync |
| `rules/no-docs-only-pr-to-main.mdc` | Knowtation-origin billing/deploy guard |
| `rules/tier-authority.mdc` | Tier 1/2/3 when to act vs ask |
| `skills/governance-sync/SKILL.md` | Session-end hygiene agent workflow |
| `skills/freeze-review/SKILL.md` | Frozen spec review before Auto build (§6) |

Automations templates ship in K5 (`cursor/automations/`).
