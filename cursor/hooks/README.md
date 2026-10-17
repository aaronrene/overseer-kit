# Canonical NEXT bookends

`cli/ok -C ROOT init --hooks` or `sync --hooks` generates repository-bound Cursor
`sessionStart` and `stop` adapters. In FPR-1 these commands are exercised only in
new disposable repositories. This development installation's active hooks remain
disabled. The distributed static shell scripts remain disabled placeholders;
copying them does not install a hook. Generation is required to bind the physical
root and the launcher's UUID/runtime.

Both adapters invoke the same validated canonical `docs/NEXT.md` service as
manual `ROOT/.overseer/bin/ok -C ROOT next`. A successful payload contains the
same paste-ready text in `additional_context` and `followup_message`, retaining
the observed P/B Cursor transport contract. The end adapter reads after the
operator's accepted handoff and final local closing commit. It does not create
that handoff. No adapter scrapes HANDOVER/ROADMAP, invokes governance-sync,
publishes NEXT, or chooses an executable from PATH or another repository.

The event's optional `workspace_roots` must be an empty list or exactly one
absolute path resolving to the bound physical root. Optional `workspace_root`
and `repo_root` assertions must name the same root. Optional `lane` and `repo_id`
must match the validated configuration. Optional `hook_event_name`, `event_name`
and `event` assertions must match the invoked `sessionStart` or `stop` adapter.
Empty stdin and `{}` retain the certified B compatibility contract; the bound
script/cwd/config still establish the repository. Duplicate JSON keys, malformed
or oversized input, conflicting roots/lanes, changed script bindings, stale NEXT
and context changes refuse before any action text is emitted. Unknown host
metadata does not select a root, lane, runtime or task.

Hook failures emit a bounded stderr refusal with no actionable stdout. The host
may continue its session; a continued host session does not make the bookend
successful. The stop adapter requests one iteration (`loop_limit: 1`). FPR-1
demonstrates fixture events only. Automatic delivery on a named Cursor version
must be demonstrated in FPR-4 before claiming that version's host support.

Claude Code and Codex use **instruction-triggered bookends**. The standalone
`.overseer/instructions/bookends.md` generated with explicit `--hooks` contains
the exact root-bound entry/close command. An owner may reference it from Claude
skills or Codex AGENTS instructions; installation does not overwrite existing
skills or AGENTS files. See [the instruction template](../../templates/BOOKENDS.instructions.md)
and [the distributed print-next skill](../skills/print-next/SKILL.md). No native
Claude/Codex lifecycle API or automatic host delivery is asserted.

FPR-2 adds multi-lane presentation. FPR-1 preserves configured extra lanes and
refuses an event selecting a lane other than the current canonical context.
Real-consumer activation still needs separate authorization.
