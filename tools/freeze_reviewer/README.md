# Freeze reviewer engine

Implements the Freeze-Step Reviewer per `docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md` and SPEC §6.

## CLI

```bash
overseer review --freeze <path> [--dry-run] [--mode agent|human] [--provider local|api] [--model LABEL] [--no-stamp] [--checklist PATH]
```

- Human/report output → stdout; diagnostics → stderr.
- `--json` emits one §K5.9 report object.
- On `pass` without `--dry-run` / `--no-stamp`, writes `review_stamp` into the artifact freeze block only (never VCS).

## Providers

| Provider | Reachability | Notes |
| --- | --- | --- |
| `local` | Always reachable offline | Shared checklist engine; injectable in tests |
| `api` | Requires `OVERSEER_REVIEW_API_KEY` | Same engine surface; missing creds → `fallback: human` |

Unreachable provider with `fallback: human` → exit `8`, escalation report — never fabricates `pass`.

## Automation degrade (§K5.10)

Templates ship under `cursor/automations/` — **not auto-enabled**. When Cursor Automations are unavailable:

| Intent | Preferred | Degrade |
| --- | --- | --- |
| Session-end freeze check | Automation → `overseer review --freeze <path> --dry-run` | Operator runs CLI or `/freeze-review` skill |
| Pre-build gate | Automation/CI → `overseer review --freeze <path>` | Same CLI; **no silent skip** |

Unavailability is never treated as `pass`.

## Tests

All provider calls are faked in CI (`tests/` §K5.12 matrix). No network, no real models.
