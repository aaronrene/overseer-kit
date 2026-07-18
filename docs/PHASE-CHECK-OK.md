# Phase — Check OK (ad-hoc honesty)

Status: **DONE** — build-verified → `pass` (CIO-BV-r1); rename + multi-runtime skill twin
(CIO-r2) on `feat/check-if-ok`.

## Freeze-contract declaration

```yaml
phase: check-ok
outputs:
  - id: check-ok-surface
    path: docs/PHASE-CHECK-OK.md
    frozen: true
frozen_inputs:
  - id: k5-freeze-reviewer
    path: docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md
```

## Intent

Anyone in any Overseer-installed repo can type **Check OK** (or run `ok check-ok`) and get
the **same** freeze-review + build-verification honesty path used on ROADMAP Thinking→Auto loops —
including side research that is **not** a roadmap row. Does **not** create a `docs.lanes` entry.

**Not Cursor-only:** skills vendor to `.cursor/skills/` **and** `.claude/skills/`; Copilot and
other tools use `ok check-ok` + `docs/CHECK-OK.md`.

## Deliverables

| Item | Path |
| --- | --- |
| Portable skill | `cursor/skills/check-ok/SKILL.md` (+ template) → `.cursor` + `.claude` |
| Always-on Thinking rule | `cursor/rules/check-ok-thinking.mdc` |
| Scaffold module | `tools/check_ok/` |
| CLI | `ok check-ok` (+ synonym `ok check-if-ok`) → `run_review` |
| Paste prompt | `docs/CHECK-OK.md` |
| SPEC §5 + footprint dual skills | additive |
| Consumer note | `docs/consumers/scooling/OVERSEER-SETUP.md` |
| Seven-tier tests | `tests/*/test_check_ok*` |

## Non-goals

- New freeze-reviewer algorithm
- Automatic new governance lanes
- Native Copilot Agent Skills (GitHub does not support SKILL.md; CLI + paste is the contract)

## Review record

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| CIO-BV-r1 | Build-verification | **pass** | Initial Check if OK surface |
| CIO-r2 | Auto rename + multi-runtime | **pass** | Renamed **Check OK**; footprint twins `.claude/skills/**`; `docs/CHECK-OK.md`; synonym CLI kept |
