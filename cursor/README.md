# Cursor fragments — vendored into consumer `.cursor/` on init/sync

Portable rules and skills for the overseer governance method. Token placeholders
(`{{repo.name}}`, etc.) are substituted from `.overseer/config.yaml` at vendoring time.

Source under `cursor/` is **tool-neutral markdown**. On `ok sync` / `ok init`:

- `rules/*` → `.cursor/rules/`
- `skills/**` → **`.cursor/skills/**` (Cursor) and `.claude/skills/**` (Claude Code)** — same bytes

Policy still lives in `policy/*.yaml` for every assistant — see root `README.md` § AI tool
compatibility. Copilot and paste-only tools use `ok` CLI + `docs/CHECK-OK.md`.

| Path | Purpose |
| --- | --- |
| `rules/governance-sync.mdc` | SD-17 mandatory roadmap + handover sync |
| `rules/tier-authority.mdc` | Tier 1/2/3 when to act vs ask |
| `rules/no-docs-only-pr-to-main.mdc` | Docs-only PR guard (configurable per consumer) |
| `skills/governance-sync/SKILL.md` | Session-end hygiene agent workflow |
| `skills/freeze-review/SKILL.md` | Single-pass frozen spec review before Auto build (§6) |
| `skills/freeze-review-loop/SKILL.md` | **Optional** bounded loop until freeze `pass` |
| `skills/build-verification-review/SKILL.md` | **Mandatory** post-build honesty review |
| `skills/check-ok/SKILL.md` | **Check OK** — ad-hoc honesty (`/check-ok`, `ok check-ok`) |
| `rules/build-verification-required.mdc` | Always-on: no DONE without build-verification `pass` |
| `rules/check-ok-thinking.mdc` | Always-on: Thinking sessions get freeze + BV gates |
| `automations/*.json` | Optional Automation templates (not auto-enabled; **Tier 2** confirm-once to enable) |
| `automations/governance-sync-session-end.json` | Session-end `ok governance-sync --dry-run` (GFG; degrade to CLI/skill) |
| `automations/freeze-review-session-end.json` | Session-end freeze-review dry-run template |

**Degrade path:** when IDE skills are unavailable, use `./cli/ok check-ok`,
`./cli/ok governance-sync`, and `./cli/ok review --freeze` from the terminal instead.
