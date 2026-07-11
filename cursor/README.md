# Cursor fragments — vendored into consumer `.cursor/` on init/sync

Portable rules and skills for the overseer governance method. Token placeholders
(`{{repo.name}}`, etc.) are substituted from `.overseer/config.yaml` at vendoring time.

These files are **Cursor-first conveniences**. The same policy lives in `policy/*.yaml` and works
with any AI assistant — see root `README.md` § AI tool compatibility.

| Path | Purpose |
| --- | --- |
| `rules/governance-sync.mdc` | SD-17 mandatory roadmap + handover sync |
| `rules/tier-authority.mdc` | Tier 1/2/3 when to act vs ask |
| `rules/no-docs-only-pr-to-main.mdc` | Docs-only PR guard (configurable per consumer) |
| `skills/governance-sync/SKILL.md` | Session-end hygiene agent workflow |
| `skills/freeze-review/SKILL.md` | Single-pass frozen spec review before Auto build (§6) |
| `skills/freeze-review-loop/SKILL.md` | **Optional** bounded loop until freeze `pass` (`/freeze-review-loop`) |
| `skills/build-verification-review/SKILL.md` | **Mandatory** post-build honesty review (`.cursor/rules/build-verification-required.mdc`) |
| `rules/build-verification-required.mdc` | Always-on: no DONE without `/build-verification-review` pass |
| `automations/*.json` | Optional Automation templates (not auto-enabled; Tier-3 to enable) |

**Degrade path:** when Automations are unavailable, use `./cli/overseer governance-sync` and
`./cli/overseer review --freeze` from the terminal instead.
