# Instruction-triggered canonical NEXT bookends

Use this guidance in explicitly selected Claude Code skills or Codex AGENTS
instructions. Preserve existing instructions; copying this template does not
register any native host lifecycle event.

At session entry, verify the physical repository root, then run its bound
launcher using absolute paths:

```sh
"/ABSOLUTE/REPOSITORY/.overseer/bin/ok" -C "/ABSOLUTE/REPOSITORY" next
```

Replace both placeholders with the selected root, or use the exact command in
the generated `.overseer/instructions/bookends.md`. Do not discover `ok` through
PATH, environment overrides or neighboring runtimes. Read the validated action
before starting work. Label this an **instruction-triggered bookend**.

At closeout, after an authorized `next-write` publication and final local closing
commit, run that same command again. Display its validated paste-ready pending
action and model from disk. If it refuses, report the refusal and do not invent
or reuse a fallback prompt. HANDOVER, ROADMAP and prior chat text are summaries
or history, not canonical NEXT authorities.

These instructions read only. They do not publish a handoff, run governance-sync,
commit, or authorize other work. They do not prove native Claude/Codex lifecycle
delivery. Generated Cursor adapters have offline fixture coverage; delivery on
a named supported host version requires the combined FPR-4 validation.
