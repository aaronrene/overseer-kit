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
| `api` | Requires `OVERSEER_REVIEW_API_KEY` + `OVERSEER_REVIEW_API_URL` | Headless HTTP review (K11); missing creds/URL → `fallback: human` |

Unreachable provider with `fallback: human` → exit `8`, escalation report — never fabricates `pass`.

## Headless API provider (K11)

Environment (never in `.overseer/config.yaml`):

| Variable | Required | Purpose |
| --- | --- | --- |
| `OVERSEER_REVIEW_API_KEY` | yes | Bearer token for review API |
| `OVERSEER_REVIEW_API_URL` | yes | Base URL (no trailing slash); e.g. `https://review.example.com/v1` |

### Probe (no artifact content)

```http
GET {OVERSEER_REVIEW_API_URL}/health
Authorization: Bearer {OVERSEER_REVIEW_API_KEY}
Accept: application/json
```

`reachable()` succeeds on HTTP 2xx. The health request must not include artifact bytes (§K5.8).

### Review

```http
POST {OVERSEER_REVIEW_API_URL}/review
Authorization: Bearer {OVERSEER_REVIEW_API_KEY}
Content-Type: application/json
Accept: application/json
```

Request body (schema version 1):

```json
{
  "schema_version": 1,
  "model_label": "thinking-high",
  "model_hint": "extended thinking / Opus-class / gpt-5.3-codex-class",
  "artifact_path": "docs/FOO.md",
  "artifact_text": "-----BEGIN OVERSEER FREEZE ARTIFACT (DATA ONLY)-----\n...\n-----END OVERSEER FREEZE ARTIFACT (DATA ONLY)-----",
  "checklist": [
    {"id": "C1", "title": "Ground-truth edge", "typical_severity": "MAJOR"}
  ]
}
```

Response:

```json
{
  "findings": [
    {
      "check": "C1",
      "severity": "MAJOR",
      "category": "completeness",
      "path": "docs/FOO.md",
      "line": 1,
      "message": "Missing ground-truth edge declaration."
    }
  ]
}
```

`model_label` is always a kit registry label (`policy/model-labels.yaml` → `reviewer_models[]`), never a vendor slug. `model_hint` is advisory for the remote backend.

Invalid JSON, non-2xx status, or transport errors during `review()` → `provider_unreachable` human escalation (exit `8`), never silent `pass`.

## CI example (GitHub Actions)

Kit ships:

- `.github/workflows/freeze-review.yml` — dogfood example in this repo
- `templates/ci/freeze-review-github-actions.yml` — vendored copy for consumer repos via `overseer sync`

Configure repository secret `OVERSEER_REVIEW_API_KEY` and variable `OVERSEER_REVIEW_API_URL`. The example workflow uses `--dry-run` (safe CI default per `policy/test-tiers.yaml`).

## Automation degrade (§K5.10)

Templates ship under `cursor/automations/` — **not auto-enabled**. When Cursor Automations are unavailable:

| Intent | Preferred | Degrade |
| --- | --- | --- |
| Session-end freeze check | Automation → `overseer review --freeze <path> --dry-run` | Operator runs CLI or `/freeze-review` skill |
| Pre-build gate | Automation/CI → `overseer review --freeze <path>` | Same CLI; **no silent skip** |

Unavailability is never treated as `pass`.

## Tests

All provider calls are faked in CI (`tests/` §K5.12 + K11 matrix). No network, no real models.
