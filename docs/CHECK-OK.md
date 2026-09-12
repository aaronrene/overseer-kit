# Check OK — portable honesty check (any AI tool)

**Not Cursor-only.** Use this in Claude Code, GitHub Copilot, ChatGPT, or any assistant.

## Fast path

1. In the repo terminal:

   ```bash
   ok check-ok --topic "<short-slug>" --scaffold-only
   ```

2. Fill the scope in the created `docs/reviews/<date>-<slug>.md` file.

3. Paste the block below into your AI chat (or type **Check OK** / `/check-ok` in
   Cursor / Claude Code if skills are installed).

4. Mechanical gate:

   ```bash
   ok check-ok --path docs/reviews/<your-file>.md
   ```

   The CLI line is **mechanical only** — it writes `gate: mechanical` and
   **cannot authorize Auto**. Auto authorization requires a digest-bound
   `freeze_review` ledger entry (`ok ledger append --kind freeze_review`).
   An explicit `auto_may_start: false` at the freeze-block top level blocks
   Auto regardless of ledger or stamp; the CLI never writes or clears that key.

## Paste-ready prompt

```
Check OK — run the Overseer honesty gates on my current work.

Model: thinking-high for review rounds

1) If no freeze artifact exists, scaffold with:
   ok check-ok --topic "<slug>" --scaffold-only
   then fill Scope + seven-tier matrix in that doc.
2) Freeze review (beginning gate): follow .cursor/skills/freeze-review/SKILL.md
   or .claude/skills/freeze-review/SKILL.md — cite every finding as path:line.
   Mechanical: ok check-ok --path <artifact>
3) If code already landed: build-verification-review against the freeze + git diff.
4) Verdict: pass | findings | blocked. Do not invent a new docs.lanes entry.
5) Escalate to human on security / irreversible / real_money / gates_tier3.

Read: docs/CHECK-OK.md; docs/OVERSEER-KIT-SPEC.md §6.
```

## Runtime map

| Tool | Skill auto-load | Fallback |
| --- | --- | --- |
| Cursor | `.cursor/skills/check-ok/` after `ok sync` | CLI + this paste |
| Claude Code | `.claude/skills/check-ok/` after `ok sync` | CLI + this paste |
| Copilot / others | — | CLI + this paste (skills not native) |
