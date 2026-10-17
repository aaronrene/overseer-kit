---
name: governance-sync
description: Inspect and explicitly synchronize paired repository governance summaries.
---

Read AGENTS.md and use the repository-bound `ok` launcher with an explicit root.
Start with `ok next` and `ok governance-sync --dry-run`; select `--lane` or
`--all-lanes` explicitly. Verify identity, history authority and the proposed paths.

`--write` applies paired summaries and commits them locally on the selected clean
feature branch. Preserve living prose and canonical NEXT. Remote PR enrichment
requires `--allow-network --gh /absolute/gh`; feature push additionally requires
`--push --write`. These flags require task authorization. Muse transport uses
controlled `mirror prepare/reconcile/verify/deliver`, never live git-export.

`--print-next` reads the canonical service and cannot combine with writes or
all-lanes. Hygiene never generates a prompt. After substantive work, explicitly
publish the accepted successor through `next-write` with current context and
expected prior digest. Read `ok next` again after the closing commit.
