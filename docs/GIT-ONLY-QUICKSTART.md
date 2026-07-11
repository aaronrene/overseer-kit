# Git-only quickstart (Overseer Kit)

Use this when you have a plain GitHub repo and **no MuseHub**. The kit’s governance
features work on Git alone; Muse is optional.

VideoFactory is the in-house `git-only` reference after its K6 pilot parity PASS.

## Prerequisites

- A clone of [overseer-kit](https://github.com/aaronrene/overseer-kit) (or a path to its `cli/overseer` shim)
- A GitHub repository (empty or existing)
- Python 3.11+ available to the shim (kit `.venv` is fine)

No Muse install is required for `git-only`.

## Commands

From your consumer repo (or with `-C <repo>`):

```bash
# Greenfield (empty / new repo)
<path-to-overseer-kit>/cli/overseer -C . init --regime git-only --non-interactive

# Status + footprint check
<path-to-overseer-kit>/cli/overseer -C . status --check-footprint

# Governance hygiene probe (default dry-run — writes nothing)
<path-to-overseer-kit>/cli/overseer -C . governance-sync --dry-run

# Freeze review on a sample artifact
<path-to-overseer-kit>/cli/overseer -C . review --freeze docs/<artifact> --dry-run
```

For repos that **already** have hand-authored handover/roadmap files, use migrate
(see `docs/K6-PILOT-OPERATOR-RUNBOOK.md`) instead of greenfield `init`.

## Guardrails

- **K7:** no core governance capability is MuseHub-only. `git-only` is a first-class baseline.
- Never commit secrets into `.overseer/config.yaml` (names and booleans only).
- Feature-branch commits only; do not auto-merge to `main`.
