# Print NEXT — portable closeout paste (any AI tool)

**Not Cursor-only.** Use this in Claude Code, GitHub Copilot, ChatGPT, or any assistant.

Host niceties improve odds of tab refresh; they do **not** guarantee an accurate open
tab. CLI/Muse/shell rewrites and dirty buffers can still stale a tab.

Open the repository root (the folder that contains `.overseer/`) as the IDE workspace.
If you open a parent folder, project rules and skills under `.cursor/` often do not load.
The CLI still works. The open editor tab is not the source of truth — run `ok next`.

## Fast path

After updating the living handover and/or roadmap:

```bash
ok next
# synonym (print-only; does not run hygiene R1–R5 / patches):
ok governance-sync --print-next
```

Paste the printed block into chat under the heading it already includes:

```
## CURRENT NEXT — paste this
```

## Source of truth order

When the printed fence, the disk file, and an open tab disagree:

1. **`ok next` / the printed CURRENT NEXT fence** (this session, after the write)
2. **The handover file on disk** at the config-driven path
3. **Never** “whatever the open tab happens to show”

An old chat paste is not a source of truth. Merge to `main` is not required to refresh NEXT.

## Runtime map

| Tool | Skill auto-load | Fallback |
| --- | --- | --- |
| Cursor | `.cursor/skills/print-next/` after `ok sync` | CLI + this paste |
| Claude Code | `.claude/skills/print-next/` after `ok sync` | CLI + this paste |
| Copilot / others | — | CLI + this paste (skills not native) |

## Paste-ready prompt (when skills are unavailable)

```
Print NEXT — closeout surfacing.

After any update to the living handover and/or roadmap, include in your FINAL reply
the paste-ready fence under heading ## CURRENT NEXT — paste this.

Bytes must come from disk after write:
  ok next
  # or: ok governance-sync --print-next

Do not paste from memory, an earlier chat, or an unsaved editor buffer.
Session incomplete without it. Do not claim the open IDE tab is accurate.
Not ok workspace check-next.

Read: docs/PRINT-NEXT.md.
```
