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
| `rules/governance-sync.mdc` | Paired local summaries; explicit remote effects |
| `rules/tier-authority.mdc` | Tier 1/2/3 when to act vs ask |
| `rules/no-docs-only-pr-to-main.mdc` | Docs-only PR guard (configurable per consumer) |
| `skills/governance-sync/SKILL.md` | Session-end hygiene agent workflow |
| `skills/freeze-review/SKILL.md` | Single-pass frozen spec review before Auto build (§6) |
| `skills/freeze-review-loop/SKILL.md` | **Optional** bounded loop until freeze `pass` |
| `skills/build-verification-review/SKILL.md` | Configured post-build evidence review |
| `skills/check-ok/SKILL.md` | **Check OK** — ad-hoc honesty (`/check-ok`, `ok check-ok`) |
| `skills/print-next/SKILL.md` | **Print NEXT** — closeout CURRENT NEXT from disk (`ok next`) |
| `rules/build-verification-required.mdc` | Apply the repository’s configured evidence gates |
| `rules/check-ok-thinking.mdc` | Configured review hints; owner-selected model |
| `rules/print-next-closeout.mdc` | Always-on: final reply includes CURRENT NEXT after living-doc writes |
| `automations/*.json` | Optional Automation templates (not auto-enabled; **Tier 2** confirm-once to enable) |
| `automations/governance-sync-session-end.json` | Session-end `ok governance-sync --dry-run` (GFG; degrade to CLI/skill) |
| `automations/freeze-review-session-end.json` | Session-end freeze-review dry-run template |
| `hooks/` | Opt-in bound Cursor start/stop adapters; canonical read and refusal |

**Degrade path:** when IDE skills are unavailable, use `./cli/ok check-ok`,
`./cli/ok governance-sync`, `./cli/ok next`, and `./cli/ok review --freeze` from the
terminal with the bound launcher and explicit repository root instead. Copilot fallback for NEXT: `ok next` + `docs/PRINT-NEXT.md`.

Host niceties improve odds of tab refresh; they do **not** guarantee an accurate open
tab. CLI/Muse/shell rewrites and dirty buffers can still stale a tab.

Open the repository root (the folder that contains `.overseer/`) as the IDE workspace.
If you open a parent folder, project rules and skills under `.cursor/` often do not load.
The CLI still works. The open editor tab is not the source of truth — run `ok next`.
