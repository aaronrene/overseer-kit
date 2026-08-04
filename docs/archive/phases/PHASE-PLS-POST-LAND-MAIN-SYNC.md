# Phase PLS — Post-land main sync (close-ritual additive)

Status: **Reviewed → `pass` (PLS-r4).** PLS-a is **spec-only** and now frozen; no product code
lands in this phase. PLS-b (Auto) is cleared to build mechanically against this contract.

```yaml
phase: PLS
outputs:
- id: pls-post-land-main-sync
  path: docs/archive/phases/PHASE-PLS-POST-LAND-MAIN-SYNC.md
  frozen: true
frozen_inputs:
- id: pr-land-after-checks
  path: docs/archive/phases/PHASE-PR-LAND-AFTER-CHECKS.md
- id: close-ritual-pr-land
  path: tools/close_ritual/pr_land.py
- id: close-ritual-land-check
  path: tools/close_ritual/land_check.py
- id: close-ritual-config
  path: adapters/config.py
- id: pr-land-cli
  path: cli/commands/pr_land.py
- id: decision-tiers
  path: policy/tiers.yaml
- id: pmhf-post-merge
  path: docs/archive/phases/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: test-tiers
  path: policy/test-tiers.yaml
review_stamp:
  reviewed_at: '2026-07-31T17:47:30Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:7a31fb2b310f5952b243a5765c9468b510d6b4b749b3d845d40fe9feb844b628
```

**Downstream edge:** PLS-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze). It closes the permanent gap after an authorized PR land
succeeds (`ok pr-land`): GitHub `main` advances, but the operator’s local checkout often still
points at a pre-merge tip (or a feature branch), so living-doc bytes on disk lag `origin/<main>`
until a separate manual `git fetch` / `git pull --ff-only`.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| PLS-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Checklist dry-run `pass`. Semantic: **R1-M1** exit `6` collides with K4 INTEGRITY; **R1-M2** muse-only trigger vs `regime_skipped`; **R1-M3** `PrLandResult` null vs always-object ambiguity; **R1-M4** `sync_status` vs `.status` naming; **R1-M5** SPEC §5 “if lists pr-land” weasel; **R1-N1** already-merged+checks-failed non-trigger underspecified. Fixed in-doc. |
| PLS-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** residual `sync_status=` prose in §PLS.5.1/§PLS.5.3 after R1-M4; **R2-M2** hard-fail row listed under “soft outcomes (exit remains 0)” table. Fixed in-doc. |
| PLS-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R3-N1** `run_pr_land` without config must still emit always-present `post_land_sync` with `disabled` (unit-test / signature compat). Fixed in-doc §PLS.4.3. |
| PLS-r4 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read: R1-M1–M5 / R1-N1 / R2-M1–M2 / R3-N1 RESOLVED; config keys + exit `36` (not `6`) + dirty skip + verify_landed additive-only + consumer default-off + seven-tier matrix present; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (Tier-1 CLI additive; merge authority unchanged). Stamp written by `ok review --freeze`. |

---

## §PLS.0 — Simple summary

After someone authorizes a pull-request merge and it lands on GitHub, the notes on your machine
often still show the old “before merge” files until you remember to pull. This phase freezes an
**optional** helper that, right after a successful authorized land, updates the local main branch
from the configured Git remote — but only with a fast-forward, and only when the working tree is
clean. It never force-pushes, never overwrites dirty files, and never replaces the existing
“did the files match main?” check. Editors may still show old tabs after the pull — reload from
disk; never save stale tab content over the fresh files.

**Technical summary:** add nested `close_ritual.post_land_sync` config (`enabled` default `false`,
`strategy: ff_only`, `require_clean_worktree: true`). Wire an additive post-step into
`tools/close_ritual/pr_land.py` / `ok pr-land` that runs **only after** `merged: true` on a
successful land path: `git fetch <vcs.git.remote>`, dirty tree → warn/skip (never clobber), clean
tree → ensure checkout of `vcs.git.main_branch` then `git pull --ff-only`. Compose with
`mode: verify_landed` (unchanged); exit `36` only for hard sync failures after a successful merge;
consumer opt-in; seven-tier §PLS.10.

---

## §PLS.1 — Verified gap (do not redesign around folklore)

| Fact | Evidence |
| --- | --- |
| `ok pr-land` merges via `gh` after green checks; returns exit `0` when `merged: true` | `tools/close_ritual/pr_land.py` `run_pr_land` (merge / already-MERGED paths); exit table in `docs/archive/phases/PHASE-PR-LAND-AFTER-CHECKS.md` |
| `ok pr-land` does not fetch or update the local checkout after merge | `cli/commands/pr_land.py` calls `run_pr_land` only; no git pull/checkout |
| `ok land-check` `verify_landed` compares working-tree `require_paths` to `origin/<main_branch>` (or local main fallback) | `tools/close_ritual/land_check.py` `compare_paths_to_main` / `run_land_check` |
| Close-ritual config today has no post-land sync keys | `adapters/config.py` `CloseRitualConfig` + `_parse_close_ritual` allowed set `{enabled, mode, require_paths, consumer_verify_script}` |
| Blind auto-merge remains forbidden | `policy/tiers.yaml` `refuse_blind_auto_merge: true`; `PrLandResult.auto_merge` always `False` |
| PMHF land-b syncs living-doc *content* via `ok governance-sync`; it does not ff-pull local `main` | `docs/archive/phases/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md` §PMHF.3.2 |
| Live dogfood still needs a separate manual pull so disk matches GitHub after land | Overseer-kit closeout commits after SD-21 lands (handover change-log 2026-07-31) |

**Root gap:** merge success on GitHub ≠ local checkout tip/bytes match `origin/<main_branch>`.
Operators and agents re-read stale handover/roadmap until someone runs a manual pull — and stale
editor buffers can overwrite the freshly pulled disk bytes if saved carelessly.

---

## §PLS.2 — Scope

**In scope (PLS-a freezes; PLS-b implements):**

1. Nested config `close_ritual.post_land_sync` (§PLS.3).
2. Additive post-step after successful `ok pr-land` MERGED outcome (§PLS.4).
3. Dirty-tree / clean-tree / regime behavior (§PLS.5).
4. Exit codes + `PrLandResult` report fields (§PLS.6).
5. Interaction with `close_ritual.mode: verify_landed` and `close_ritual.enabled` (§PLS.7).
6. Consumer opt-in/out + migration (§PLS.8).
7. Explicit non-goals (§PLS.2.1), security checklist (§PLS.9), seven-tier matrix (§PLS.10),
   Auto deliverables (§PLS.11), DoD + hard stops (§PLS.12–§PLS.13).

### §PLS.2.1 — Out of scope (explicit non-goals)

| Non-goal | Why rejected |
| --- | --- |
| **Multi-worktree / portal merges (VideoFactory-specific)** | Consumer-owned; kit stays regime-generic single-checkout sync |
| **Editor / Cursor automation that reloads buffers or writes tabs** | Kit must not drive IDE state; operator note only (§PLS.4.4) |
| **Blind dirty-tree merges / stash / reset --hard / force checkout** | Data-loss risk; contradicted by `require_clean_worktree: true` |
| **Force push** | Tier 3 / irreversible; never part of post-land sync |
| **Changing `refuse_blind_auto_merge`** | Stays `true` in `policy/tiers.yaml`; PLS is not a merge path |
| **Replacing `verify_landed` / redesigning `ok land-check`** | Additive post-step on `pr-land` only; land-check semantics unchanged |
| **Redesigning land authorization (`--authorized`) or check polling** | `ok pr-land` merge authority stays as frozen in PHASE-PR-LAND-AFTER-CHECKS |
| **Silent commits / merges to `main`, staging push, live flips** | Tier 3 unchanged |
| **Making `close_ritual.enabled` or `post_land_sync.enabled` default `true`** | Consumer posture flip; kit Auto ships default-off |
| **PMHF land-b / GFG / GS-PASTE redesign** | Compose only: PLS updates git tip; land-b still regenerates NEXT |
| **Muse `git-export` on the kit dev tree** | SD-14 / AGENTS.md forbidden |
| **PLS-b Auto implementation in the Thinking phase** | SD-3 split |

---

## §PLS.3 — Config contract (frozen)

### §PLS.3.1 — Nested schema

Additive under existing `close_ritual:` (YAML):

```yaml
close_ritual:
  enabled: false                 # existing — unchanged default
  mode: verify_landed            # existing — unchanged vocabulary
  require_paths: []              # existing
  consumer_verify_script: null   # existing
  post_land_sync:
    enabled: false               # default OFF — consumer opt-in
    strategy: ff_only            # v1 closed vocabulary — only this value
    require_clean_worktree: true # v1 — must be true (see §PLS.3.2)
```

### §PLS.3.2 — Parse rules (fail-closed)

Extend `_parse_close_ritual` / `CloseRitualConfig` (or nested frozen dataclass
`PostLandSyncConfig`):

| Key | Type | Default | Rule |
| --- | --- | --- | --- |
| `post_land_sync` | mapping (optional) | absent → defaults below | Unknown nested keys → `ConfigError` |
| `post_land_sync.enabled` | bool | `false` | Non-bool → `ConfigError` |
| `post_land_sync.strategy` | string | `ff_only` | Must equal exactly `ff_only`; any other value → `ConfigError` |
| `post_land_sync.require_clean_worktree` | bool | `true` | Must be `true` in v1; `false` → `ConfigError` (dirty merges are non-goals) |

**Allowed `close_ritual` top-level keys after PLS-b:**  
`{enabled, mode, require_paths, consumer_verify_script, post_land_sync}`.

**Remote / branch identity (not duplicated under `post_land_sync`):**

| Value | Source (frozen) |
| --- | --- |
| Fetch/pull remote | `vcs.git.remote` (kit default `origin`) |
| Main branch name | `vcs.git.main_branch` (kit default `main`) |
| Sync ref | `<remote>/<main_branch>` after fetch |

Do **not** invent parallel `post_land_sync.remote` / `.main_branch` keys in v1.

### §PLS.3.3 — Defaults & consumer opt-in/out

| Consumer posture | Effect |
| --- | --- |
| Omit `post_land_sync` | Identical to today — no post-land sync |
| `post_land_sync.enabled: false` | Explicit opt-out (same as omit) |
| `post_land_sync.enabled: true` | Opt-in — run §PLS.4 after successful MERGED |
| Kit dogfood default in shipped templates | Remain **off** unless a consumer template explicitly opts in |

Flipping a live consumer from off → on is a **consumer config change** (not a kit Auto default flip).

---

## §PLS.4 — HOW (additive post-step on `ok pr-land`)

### §PLS.4.1 — Trigger (frozen)

Enter the post-land sync helper **if and only if** all of the following hold:

1. `close_ritual.post_land_sync.enabled` is `true`.
2. `run_pr_land` has reached a **successful merge outcome**:
   - `merged: true` (including `already_merged: true`), **and**
   - the merge-path exit code **before** sync would be `0`.
3. `dry_run` is `false` (dry-run never mutates the working tree or refs via sync).

Inside the helper, regime decides work (§PLS.5.3): `muse-only` returns `status=regime_skipped`
with **zero** git/gh argv; `git-only` / `muse+git-mirror` continue §PLS.4.2.

**Non-triggers (frozen) — do not enter the helper; `post_land_sync.status=not_applicable`
unless disabled applies first:**

- `post_land_sync.enabled: false` (or omitted) → `status=disabled` (byte-compatible with pre-PLS
  when disabled; no git pull).
- Checks failed / unauthorized / timeout / gh error / non-OPEN refused states — including the
  already-MERGED path that returns `EXIT_CHECKS_FAILED` when checks report failure
  (`tools/close_ritual/pr_land.py` already-MERGED + failing checks) — no sync.
- `dry_run: true` with green checks — no sync (`status=not_applicable`).

### §PLS.4.2 — Sequence when triggered (frozen)

Injectable git runner (tests); argv form normative:

| Step | Action | On failure |
| --- | --- | --- |
| S0 | Load remote = `vcs.git.remote`, main = `vcs.git.main_branch` | Config already validated |
| S1 | `git fetch <remote>` (cwd = repo root) | → sync hard-fail (§PLS.6) |
| S2 | Read dirty state: `git status --porcelain` (full tree) | Unreadable → hard-fail |
| S3 | If porcelain non-empty **and** `require_clean_worktree: true` | → **skip** with warn (`skipped_dirty`); **never** stash/reset/checkout/pull |
| S4 | If clean and `HEAD` ≠ `main_branch`: `git checkout <main_branch>` | Checkout fail → hard-fail |
| S5 | `git pull --ff-only <remote> <main_branch>` (or equivalent ff-only merge of `<remote>/<main_branch>` into current `main_branch`) | Non-ff / pull fail → hard-fail |
| S6 | Emit operator editor-buffer note (§PLS.4.4) | Always after successful S5 |

**Forbidden during sync:** `--force`, `reset --hard`, `clean -fd`, stash pop as default, merge strategies other than ff-only, `gh pr merge`, pushing any branch, Muse bridge export.

### §PLS.4.3 — Wiring point (frozen)

| Surface | Rule |
| --- | --- |
| `tools/close_ritual/pr_land.py` | After successful merge / already-merged OK path, call post-land sync helper when config enables it; attach report to `PrLandResult` |
| `cli/commands/pr_land.py` | Load full config (today validates install); pass `OverseerConfig` (or post_land_sync + vcs.git fields) into `run_pr_land` |
| New helper module (Auto choice of path) | Preferred: `tools/close_ritual/post_land_sync.py` exporting `run_post_land_sync(...)` + report dataclass — keeps `pr_land.py` merge logic stable |
| `ok land-check` | **Unchanged** — no post-land sync here |

`repo_root` (already reserved on `run_pr_land`) becomes required for the sync path when enabled.
When `run_pr_land` is invoked without an `OverseerConfig` / post-land-sync config (unit helpers),
treat sync as **disabled** (`post_land_sync.status=disabled`) — still emit the always-present
object (§PLS.6.3); never leave the key absent.

### §PLS.4.4 — Operator editor-buffer note (frozen)

After a **successful** ff-only sync (S5), emit exactly one normative note (human stderr / messages list; JSON field may mirror it):

```text
post_land_sync: editor buffers may be stale — reload governance docs from disk; never overwrite disk with old tab content
```

This is **advisory only**. PLS does not automate editor reload, does not touch Cursor, and does not
rewrite open buffers.

---

## §PLS.5 — Dirty tree, regimes, and never-clobber

### §PLS.5.1 — Dirty-tree policy (frozen)

When `require_clean_worktree: true` (v1 always):

| State | Sync action | Merge outcome |
| --- | --- | --- |
| Clean porcelain | Proceed S4–S6 | Unchanged |
| Dirty porcelain | **Skip** pull/checkout; emit warn with dirty summary (paths truncated safely); `post_land_sync.status=skipped_dirty` | Merge success preserved (exit `0` unless other rules) |
| Dirty + any clobber strategy | **Forbidden** | N/A |

“Dirty” = any non-empty `git status --porcelain` output (tracked or untracked), matching
fail-closed hygiene elsewhere in the kit.

### §PLS.5.2 — Clean tree not on main (frozen)

If clean and current branch ≠ `vcs.git.main_branch`, Autobuild **must** `git checkout <main_branch>`
before ff-only pull (§PLS.4.2 S4). Rationale: `git pull --ff-only` on a feature branch does **not**
sync local main to `origin/<main_branch>` — the frozen goal is local checkout alignment to
`origin/<main_branch>`.

Checkout is allowed **only** when porcelain is clean (S3 already passed).

### §PLS.5.3 — Regime matrix (frozen)

| Regime | Post-land sync |
| --- | --- |
| `git-only` | Full §PLS.4.2 when enabled |
| `muse+git-mirror` | **Git side only** — fetch/checkout/pull against `vcs.git.*`; does **not** run Muse commits, bridge export, or `muse pull`. Muse tip hygiene remains existing Tier-1 / SD-14 paths |
| `muse-only` | **Inert skip** — `post_land_sync.status=regime_skipped`; emit note that git post-land sync does not apply; exit code unchanged from merge path (no git/gh) |

---

## §PLS.6 — Exit codes and result fields

### §PLS.6.1 — Existing `ok pr-land` codes (unchanged meanings)

| Code | Constant | Meaning |
| --- | --- | --- |
| 0 | `EXIT_OK` | Authorized path succeeded (merged / already merged) |
| 1 | `EXIT_USAGE` | Bad usage / refused PR state |
| 2 | `EXIT_CHECKS_FAILED` | Checks failed |
| 3 | `EXIT_UNAUTHORIZED` | Missing `--authorized` |
| 4 | `EXIT_TIMEOUT` | Timeout waiting for checks |
| 5 | `EXIT_GH_ERROR` | `gh` / merge transport error |

### §PLS.6.2 — Additive sync exit (frozen)

| Code | Constant | Meaning |
| --- | --- | --- |
| 36 | `EXIT_POST_LAND_SYNC` | Merge outcome was successful (`merged: true`, pre-sync would be `0`), sync was **enabled**, helper was entered, and sync **hard-failed** on a git regime (fetch fail, unreadable status, checkout fail, non-ff-only pull fail). Confined to `ok pr-land`. |

**Must not reuse exit `6`.** K4 freezes `6` as INTEGRITY (`footprint_digest` / lock) on
`ok status` / `ok sync` (`docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md`). PLS must not overload that
code on `ok pr-land`.

| Outcome | Exit | `post_land_sync.status` |
| --- | --- | --- |
| Sync disabled / omitted | `0` | `disabled` |
| `muse-only` skip (helper entered) | `0` | `regime_skipped` |
| Dirty skip (§PLS.5.1) | `0` | `skipped_dirty` |
| Sync completed ff-only | `0` | `synced` |
| Not triggered (no successful merge / dry_run) | pre-sync code | `not_applicable` |
| Hard-fail after successful merge | `36` | `failed` |

**Rationale:** dirty skip is a safe no-op warn (operator cleans tree and re-runs `ok pr-land` on
the already-merged PR, or pulls manually) — it must **not** look like a CI babysit failure (`2`).
Hard sync failure after a real merge uses `36` so agents can distinguish “landed but local tip not
updated” from “checks failed” (`2`) and from footprint integrity (`6`).

Re-running `ok pr-land` on an already-MERGED PR with sync enabled is allowed when the
already-merged path still returns pre-sync exit `0` (not the already-merged + checks-failed path).

### §PLS.6.3 — `PrLandResult` additive fields (frozen)

Additive keys (JSON / dataclass); existing fields retain meaning.

**Normative (not optional):** every `PrLandResult` returned from `run_pr_land` after PLS-b **must**
include a `post_land_sync` object (never omit the key; never use bare `null` for the object when
the function returns a result). Populate `status` from the closed set below.

| Field | Type | Notes |
| --- | --- | --- |
| `post_land_sync` | object | Always present on `run_pr_land` results |
| `post_land_sync.status` | string | Closed set: `disabled` \| `regime_skipped` \| `skipped_dirty` \| `synced` \| `failed` \| `not_applicable` |
| `post_land_sync.remote` | string | Echo of `vcs.git.remote` when helper entered on a git regime; empty string otherwise |
| `post_land_sync.main_branch` | string | Echo of `vcs.git.main_branch` when helper entered on a git regime; empty string otherwise |
| `post_land_sync.messages` | list[str] | Includes dirty warn and editor-buffer note when relevant |

`auto_merge` remains always `False`.

---

## §PLS.7 — Interaction with `verify_landed` and `close_ritual.enabled`

| Concern | Frozen rule |
| --- | --- |
| `close_ritual.mode: verify_landed` | **Unchanged.** Still compares working-tree `require_paths` hashes to `<remote>/<main_branch>` (fallback local main). PLS does not alter comparison logic. |
| Purpose of PLS relative to verify_landed | After GitHub merge, `origin/<main>` advances; PLS ff-updates the **local** main checkout so disk bytes can match the landed tip before the operator runs `ok land-check`. |
| Replacing verify_landed | **Forbidden.** PLS is an additive post-step on `pr-land` only. |
| `close_ritual.enabled: false` | `ok land-check` remains today’s no-op. `post_land_sync.enabled` is **independent** for the `pr-land` path: sync may run when nested enabled even if top-level `close_ritual.enabled` is false (mirrors today’s `pr-land` not requiring `close_ritual.enabled` — `cli/commands/pr_land.py`). |
| `close_ritual.enabled: true` + sync enabled | Land-check + post-land sync both available; no ordering coupling beyond “sync runs inside `pr-land` after MERGED.” |
| PMHF land-closeout / land-b | Orthogonal. PLS does not regenerate NEXT; land-b / `ok governance-sync` still required for living-doc closeout (§PMHF.3.2). Recommended operator order after authorized land: `ok pr-land` (optional PLS) → land-b docs sync → `ok land-closeout`. |

---

## §PLS.8 — Consumer migration

| Consumer | Action |
| --- | --- |
| Default / omit block | No change — opt-out |
| Want post-land sync | Set `close_ritual.post_land_sync.enabled: true` (strategy/require_clean defaults apply) |
| VideoFactory | May keep consumer portal/multi-worktree jobs; must **not** expect kit PLS to replace them. Optional: enable kit sync for the primary checkout only |
| Scooling / Knowtation | Opt-in via config when desired; no kit Auto force-enable |
| `muse-only` | Leave disabled or accept inert `regime_skipped` |

Update `docs/consumers/videofactory/OVERSEER-SETUP.md` close-ritual table with the three
`post_land_sync` keys (additive docs in PLS-b). Amend `docs/archive/phases/PHASE-PR-LAND-AFTER-CHECKS.md` with a
short “optional post-land sync” pointer to this freeze.

---

## §PLS.9 — Security / privacy checklist

| Topic | Rule |
| --- | --- |
| **secrets** | No new credentials; uses existing local git remote + existing `gh` auth for merge only |
| **injection** | Remote/branch from validated config strings; git argv list form only (no shell interpolation) |
| **force / clobber** | Forbidden (`--force`, hard reset, clean -fd, dirty merge) — asserted in security tier |
| **refuse_blind_auto_merge** | Unchanged `true`; PLS never calls `gh pr merge --auto` |
| **Tier 3** | `ok pr-land` merge authority unchanged; PLS does not authorize merges; kit `main` merge still Tier 3 / SD-21 |
| **scope** | Single `repo_root`; no cross-repo / portal writes |
| **editor** | Advisory note only — no IDE automation surface |

---

## §PLS.10 — Seven-tier test matrix (PLS-b)

| Tier | Frozen case |
| --- | --- |
| **unit** | (1) Config parse: defaults off/`ff_only`/`true`; reject unknown keys, bad strategy, `require_clean_worktree: false`, non-bool enabled. (2) Trigger matrix: enabled+merged+not dry_run → enter helper; disabled / dry_run / non-merged → no git pull; muse-only → `regime_skipped` with zero git argv. (3) Dirty porcelain → `skipped_dirty`, zero checkout/pull argv. (4) Clean on feature branch → checkout main then pull `--ff-only`. (5) Exit `36` mapping for fetch/pull hard-fail after merged (not `6`). |
| **integration** | Injected runner: successful merge then fetch+ff-only pull updates mocked main tip; `PrLandResult.post_land_sync.status == synced`; editor note present in messages. Already-merged path also invokes sync when enabled. |
| **e2e** | Temp git repo: land path stubbed to merged; with sync enabled and clean tree on feature branch, after `ok pr-land` (or engine entry) HEAD is `main` and matches `origin/main`. With dirty tree, HEAD unchanged and status `skipped_dirty`, exit `0`. |
| **stress** | N≥20 alternating dirty-skip / clean-sync cycles: never clobber dirty files; clean cycles always ff-only argv only. |
| **data-integrity** | Dirty tree with unique file content: after skipped sync, file bytes unchanged. Clean sync: working tree bytes for a tracked file equal `origin/main` after pull. No force-push / no new commits invented by sync (ff-only only). |
| **performance** | Sync path performs bounded git calls (fetch + status + optional checkout + pull) — no unbounded log walks; completes under existing close-ritual unit budget on fixtures. |
| **security** | (1) Call log never contains `--force`, `reset --hard`, `clean -fd`, or `merge --auto`. (2) `muse-only` fixture: zero `git`/`gh` argv from sync helper. (3) Branch/remote metacharacters fail closed or safe argv. (4) `refuse_blind_auto_merge` policy text/tests still hold. |

---

## §PLS.11 — Auto deliverables (PLS-b)

1. `PostLandSyncConfig` (+ parse) under `close_ritual.post_land_sync` per §PLS.3.
2. `tools/close_ritual/post_land_sync.py` (or equivalent) implementing §PLS.4–§PLS.5.
3. Wire into `run_pr_land` / `cli/commands/pr_land.py` with config + `repo_root`.
4. `PrLandResult` additive always-present `post_land_sync` object + exit `36` per §PLS.6.
5. Seven-tier tests §PLS.10 green.
6. Doc touchpoints: `docs/archive/phases/PHASE-PR-LAND-AFTER-CHECKS.md` pointer + exit `36` row; VideoFactory OVERSEER-SETUP close-ritual table; **mandatory** additive SPEC §5 row for `ok pr-land` (authorized wait-for-green merge + optional `close_ritual.post_land_sync` ff-only post-step; exit `36` on hard sync fail) — `pr-land` is absent from §5 today and must be added (not a conditional).
7. ROADMAP + HANDOVER close together; `/build-verification-review` → `pass` before DONE.

**Exit codes:** `0`–`5` retain frozen meanings on `ok pr-land`; `36` = `EXIT_POST_LAND_SYNC` only as §PLS.6.2; do not reuse `6`.

---

## §PLS.12 — Definition of Done (PLS-b)

- [ ] Config keys frozen in §PLS.3 parsed fail-closed
- [ ] Post-step runs only on successful MERGED when enabled (§PLS.4.1)
- [ ] Dirty → warn/skip never clobber; clean → checkout main + `git pull --ff-only` (§PLS.4.2 / §PLS.5)
- [ ] `verify_landed` unchanged; sync additive only (§PLS.7)
- [ ] Consumer default-off opt-in (§PLS.3.3 / §PLS.8)
- [ ] Editor-buffer note emitted after successful sync (§PLS.4.4)
- [ ] Seven-tier §PLS.10 green
- [ ] `/build-verification-review` → `pass` before ROADMAP **DONE**
- [ ] `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17)
- [ ] No kit `main` merge without Tier 3; no secrets; no land-authorization redesign

---

## §PLS.13 — Hard stops

- No PLS-b Auto implementation during PLS-a
- No merge to `main` / staging push / live posture flips without Tier 3
- No secrets in commits, adapters, logs, or governance docs
- No force push, dirty-tree clobber, or `refuse_blind_auto_merge` change
- No replacing `verify_landed` / redesigning `--authorized` land path
- No editor/Cursor automation that writes buffers

---

## §PLS.14 — Cross-references

- `docs/archive/phases/PHASE-PR-LAND-AFTER-CHECKS.md` — authorized wait-for-green land
- `tools/close_ritual/pr_land.py` — merge engine
- `tools/close_ritual/land_check.py` — `verify_landed` (unchanged)
- `adapters/config.py` — `CloseRitualConfig` / `_parse_close_ritual`
- `policy/tiers.yaml` — `refuse_blind_auto_merge: true`
- `docs/archive/phases/PHASE-PMHF-POST-MERGE-HANDOVER-FRESHNESS.md` — land-b docs closeout (compose, not replace)
- `docs/OVERSEER-KIT-SPEC.md` §6 — freeze review policy
- `policy/test-tiers.yaml` — seven-tier contract

---

## Freeze-review findings ledger

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | consistency | `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` (~exit `6` INTEGRITY); draft §PLS.6.2 used exit `6` | Exit `6` is frozen K4 INTEGRITY on status/sync. Post-land hard-fail must use a free code (`36`) confined to `ok pr-land`. |
| R1-M2 | MAJOR | consistency | draft §PLS.4.1 item 4 vs §PLS.5.3 `regime_skipped` | Trigger excluded `muse-only` entirely while regime matrix required `regime_skipped` — freeze must enter helper and short-circuit with zero git argv. |
| R1-M3 | MAJOR | completeness | draft §PLS.6.3 | “null vs always object — Auto must pick” is not a freeze. Normative: always-present `post_land_sync` object on `run_pr_land` results. |
| R1-M4 | MAJOR | consistency | draft §PLS.6.2 soft table vs §PLS.6.3 | Soft table used `sync_status`; result field is `post_land_sync.status` — unify naming. |
| R1-M5 | MAJOR | completeness | draft §PLS.11 item 6; `docs/OVERSEER-KIT-SPEC.md` §5 | Conditional SPEC §5 row (“if §5 lists pr-land”) is weasel; `pr-land` absent today — freeze mandatory additive §5 row. |
| R1-N1 | MINOR | completeness | `tools/close_ritual/pr_land.py` already-MERGED + checks-failed path; draft §PLS.4.1 | Non-trigger must explicitly include already-merged + `EXIT_CHECKS_FAILED` so sync does not run on that path. |
| R2-M1 | MAJOR | consistency | `docs/archive/phases/PHASE-PLS-POST-LAND-MAIN-SYNC.md` §PLS.5.1 / §PLS.5.3 (pre-fix) | Residual `sync_status=` after R1-M4 rename — must say `post_land_sync.status=`. |
| R2-M2 | MAJOR | consistency | `docs/archive/phases/PHASE-PLS-POST-LAND-MAIN-SYNC.md` §PLS.6.2 soft table (pre-fix) | Hard-fail (`36`/`failed`) was listed under “exit remains 0” soft outcomes — split into outcome×exit table. |
| R3-N1 | MINOR | completeness | `tools/close_ritual/pr_land.py` `run_pr_land` signature (no config today); §PLS.6.3 always-present object | Without config, unit callers would omit `post_land_sync` unless freeze defaults missing config to `disabled` object. |
