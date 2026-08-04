# Phase: Authorized wait-for-green PR land (`ok pr-land`)

**Status:** Implemented on kit feature branch (promote with consumer sync)  
**Date:** 2026-07-17  
**Consumer dogfood:** VideoFactory `jobs/pr_land_after_checks.py`

## Problem

Operators should not babysit GitHub waiting for CI, then click Merge.  
`gh pr merge --auto` only waits for **required** status checks. Repos without
branch protection (including VideoFactory `main` as of 2026-07-17) merge
**immediately**, which defeats "wait for green."

## Contract

| Item | Rule |
|------|------|
| Command | `ok pr-land --pr <N> --authorized "<reason>"` |
| Tier | Tier 3 — operator-delegated via non-empty `--authorized` |
| Poll | Local `gh pr checks` until every check settles |
| Fail | Exit `2` with failing check names → agent babysit/fix → re-run |
| Pass | Merge via `--squash` (default) / `--merge` / `--rebase` |
| Blind auto | **Forbidden** — do not rely on `gh pr merge --auto` alone |
| `ok land-check` | Unchanged — verify paths vs main; never merges |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Merged (or already merged + not failed) |
| 2 | Checks failed — fix in-scope, push, retry |
| 3 | Missing `--authorized` |
| 4 | Timeout waiting for checks |
| 5 | `gh` error |
| 36 | Merge succeeded but the optional post-land sync hard-failed (fetch / checkout / non-ff pull) — see `docs/archive/phases/PHASE-PLS-POST-LAND-MAIN-SYNC.md` §PLS.6. Never reuses exit `6` (K4 INTEGRITY). |

## Optional post-land sync (PLS)

When `close_ritual.post_land_sync.enabled: true` (default **off**), a successful
merged outcome runs an additive ff-only local sync: `git fetch` → dirty tree
warn/skip (never clobber) → clean tree checkout `main` + `git pull --ff-only`.
Every `PrLandResult` carries an always-present `post_land_sync` object
(`disabled | regime_skipped | skipped_dirty | synced | failed | not_applicable`).
Frozen contract: `docs/archive/phases/PHASE-PLS-POST-LAND-MAIN-SYNC.md`.

## Agent loop (babysit)

1. Open/update PR; push feature branch.  
2. Run `ok pr-land --pr N --authorized "…"`.  
3. If exit 2: fix failing checks in PR scope (never waive CI workflows to go green).  
4. Push; re-run `ok pr-land`.  
5. After merge: consumer `land-check` / `board_land_check --verify-landed --clear-pending`.

## Tests

```bash
python3 -m unittest tests.unit.test_close_ritual_pr_land
```

## VideoFactory mirror

```bash
python3 jobs/pr_land_after_checks.py --pr N --authorized "Aaron: …"
```
