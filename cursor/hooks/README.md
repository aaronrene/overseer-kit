# Optional Cursor `stop` hook — print NEXT (ONS)

**Template only.** Not copied by `ok sync` / `ok init` footprint (same posture as
`cursor/automations/`). Enabling is **Tier 2 confirm-once**.

Host niceties improve odds of tab refresh; they do **not** guarantee an accurate open
tab. CLI/Muse/shell rewrites and dirty buffers can still stale a tab.

## Enable (operator)

1. Confirm once that you want a fail-open `stop` follow-up (Tier 2).
2. Merge the snippet from `print-next-stop.json` into the project `.cursor/hooks.json`
   (do **not** overwrite unrelated hooks).
3. Restart Cursor if the host requires it for hooks to load.

## Behavior (frozen)

- Event: `stop`
- `failClosed`: **false** (fail open)
- `loop_limit`: `1` (at most one follow-up)
- If the agent’s last reply lacks `## CURRENT NEXT — paste this` and this session wrote
  the living handover or roadmap, follow up once: run or request `ok next` and include
  the heading+fence
- MUST NOT block DONE, MUST NOT merge, MUST NOT write docs, MUST NOT claim tab reload

If the host payload cannot see “wrote handover,” a follow-up when the heading is absent
is acceptable because `loop_limit` is 1 and fail-open.
