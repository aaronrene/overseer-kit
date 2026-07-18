# Phase — Check if OK (ad-hoc honesty)

Status: **DONE** — build-verified → `pass` (CIO-BV-r1) on `feat/check-if-ok`.

## Freeze-contract declaration

```yaml
phase: check-if-ok
outputs:
  - id: check-if-ok-surface
    path: docs/PHASE-CHECK-IF-OK.md
    frozen: true
frozen_inputs:
  - id: k5-freeze-reviewer
    path: docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
```

## Intent

Anyone in any Overseer-installed repo can type **Check if OK** (or run `ok check-if-ok`) and get
the **same** freeze-review + build-verification honesty path used on ROADMAP Thinking→Auto loops —
including side research that is **not** a roadmap row. Does **not** create a `docs.lanes` entry.

## Deliverables

| Item | Path |
| --- | --- |
| Cursor skill | `cursor/skills/check-if-ok/SKILL.md` (+ template) |
| Always-on Thinking rule | `cursor/rules/check-if-ok-thinking.mdc` |
| Scaffold module | `tools/check_if_ok/` |
| CLI | `ok check-if-ok` → scaffolds then `run_review` (identical engine) |
| SPEC §5 row | additive |
| Consumer note | `docs/consumers/scooling/OVERSEER-SETUP.md` |
| Seven-tier tests | `tests/*/test_check_if_ok*` |

## Non-goals

- New freeze-reviewer algorithm
- Automatic new governance lanes
- Replacing `/freeze-review-loop` or `/build-verification-review`

## Review record

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| CIO-BV-r1 | Build-verification (Auto session; structural + seven-tier) | **pass** | All deliverables present; `ok check-if-ok` delegates to `run_review`; footprint includes skill+rule+template; §CIO tests **17** green; no new lanes; SPEC §5 row additive |
