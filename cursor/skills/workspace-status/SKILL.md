> **Historical pre-reset product.** This document describes the pre-reset historical product.
> Its legacy commands are not exposed by the bounded-v1 entrypoint. Do not use it
> as current onboarding. See the [root README](../../../README.md) and [current docs index](../../../docs/README.md).

# Workspace status skill

Use when the operator asks for constellation / multi-repo NEXT authority, types
`/workspace-status`, or before pasting a NEXT prompt from a multi-root workspace.

## Purpose

Show which member owns **product_order** PRIMARY and whether relay tips are fresh.
Focused editor tabs are not authority.

## CLI

```bash
./cli/ok workspace status
./cli/ok workspace status --json
./cli/ok workspace check-next
./cli/ok workspace doctor
./cli/ok status --workspace --exit-code
```

Exit `35` (`WORKSPACE_RELAY`) means stale/ambiguous/missing relay integrity.
Single-repo `ok status` green does **not** imply `workspace.ok`.

## Board filenames

Prefer `{REPO_SLUG}-OVERSEER-HANDOVER.md` / `{REPO_SLUG}-ROADMAP.md` so multi-root tabs
are distinct. Doctor reports `board_name_violation` for bare legacy names under
`strict_board_names`.
