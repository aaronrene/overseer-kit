# Phase GSW-FIX — Governance-sync write-path order-of-operations

Status: **Reviewed → `pass` (GSW-r3).** GSW-FIX-a is **spec-only** and now frozen; no product
code lands in this phase. GSW-FIX-b (Auto) is cleared to build mechanically against this contract.

```yaml
phase: GSW-FIX
outputs:
- id: gsw-fix-governance-sync-write-path
  path: docs/archive/phases/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md
  frozen: true
frozen_inputs:
- id: phase-9a5-commit-strategy
  path: docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: governance-hygiene-engine
  path: tools/governance_hygiene/engine.py
- id: muse-git-mirror-adapter
  path: adapters/muse_git_mirror/adapter.py
- id: muse-only-adapter
  path: adapters/muse_only/adapter.py
- id: git-only-adapter
  path: adapters/git_only/adapter.py
- id: adapter-base
  path: adapters/base.py
- id: governance-sync-cli
  path: cli/commands/governance_sync.py
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: gfg-freshness-gate
  path: docs/archive/phases/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md
review_stamp:
  reviewed_at: '2026-07-31T14:13:22Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:63cfd1767a566418bec6a98abbe04690be5e3049aa0dc9a75ced8838dba0a532
```

**Downstream edge:** GSW-FIX-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze). It closes the permanent gap exposed live on 2026-07-31 while
dogfooding PMHF land-b: `ok governance-sync --write` on `muse+git-mirror` always fails because
`_apply_plan` writes doc patches **before** branch setup, then `commit_feature` runs a Muse
checkout that refuses dirty tracked files, and fail-closed rollback restores docs but **strands
git** on the sync branch.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| GSW-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R1-M1** realign-after-branch-switch underspecified vs today’s original-branch realign (`realign.py` / `adapter.realign` `--branch` muse main); **R1-M2** marker-before-commit contradicts GFG §GFG.5.3 “Must not stamp on mid-apply failure”. Fixed in-doc. |
| GSW-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** non-goal “Changing … GFG marker semantics” contradicted §GSW.3.4 mid-apply stamp amendment; GFG missing from `frozen_inputs`. Fixed in-doc. |
| GSW-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read: R1-M1/R1-M2/R2-M1 RESOLVED; order `capture → realign → ensure branch → write → commit → marker → push`; dual-HEAD + rollback + three-regime dirty-tree `--write` matrix present; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (Tier-1 CLI fix; merge remains Tier 3). Stamp written by `ok review --freeze`. |

---

## §GSW.0 — Simple summary

At the end of a work session, a helper is supposed to update two living notes and save them on a
side branch. Today, on the Muse+Git setup, that helper first edits the notes (making the tree
dirty), then asks Muse to switch to the side branch. Muse refuses to switch while those edits are
uncommitted. The helper then undoes the note edits but leaves Git sitting on the side branch it
just created — so the operator’s tree is stranded in the wrong place, and the sync always fails.

**This phase freezes the permanent fix:** keep any history realign on the original branch, then set
up the side branch (both histories under `muse+git-mirror`), **then** write the notes, **then**
commit, **then** stamp the sync marker. If anything fails after a branch switch, rollback must
restore the original branch (and marker) on every failure path — not only the note bytes.

**Technical summary:** amend `tools/governance_hygiene/engine.py` `_apply_plan` to
`capture → realign → ensure feature branch → write docs → commit → marker → push`; amend
Muse-regime `commit_feature` with already-on-branch short-circuit and dirty-carry checkout
(`--autoshelf` / `--merge`) only as a secondary adapter guard; restore original branch + marker on
mid-apply failure. Freeze a three-regime matrix and a seven-tier regression suite that includes
dirty-tree `--write` on **all** regimes — the exact coverage gap that let this ship.

---

## §GSW.1 — Verified incident (do not redesign around folklore)

Live overseer-kit dogfood during PMHF land-b (2026-07-31), regime `muse+git-mirror`:

| Fact | Evidence |
| --- | --- |
| `ok governance-sync --write` exits `2` | Operator live run; docs restored; no feature commit |
| Doc patches written before branch setup | `tools/governance_hygiene/engine.py` `_apply_plan` lines 450–451 write handover/roadmap, then lines 498–513 call `_ensure_feature_branch`, then lines 515–519 call `adapter.commit_feature` |
| Muse refuses dirty tracked checkout | `adapters/muse_git_mirror/adapter.py` `commit_feature` line 185: `self._muse("checkout", branch)` with no `--merge` / `--autoshelf`; Muse 0.2.x exit `1` on dirty tree without those flags |
| Git switch happens first and is not rolled back | `_ensure_feature_branch` lines 656–668 run `git checkout -b` / `git checkout` under non-`muse-only`; on later `commit_feature` failure, lines 521–535 restore doc bytes only — no git/muse branch restore |
| Observed stranded git branch | `feat/governance-sync-2026-07-31` after failed write |
| Existing write e2e is git-only + mocked clean tree | `tests/e2e/test_governance_sync_cycle.py` seeds `config-git-only.yaml` and mocks porcelain clean; no muse+git-mirror dirty-tree `--write` case |

**Root cause (two coupled defects):**

1. **Order-of-operations:** write-then-checkout is incompatible with Muse’s default dirty-tree
   refusal (unlike git, which carries uncommitted changes across checkout).
2. **Incomplete rollback:** branch identity changed by `_ensure_feature_branch` is not restored on
   failure, violating 9A-5 §7 “working tree left clean / failure reported with tree untouched”
   intent for operator branch posture.

---

## §GSW.2 — Scope

**In scope (GSW-FIX-a freezes; GSW-FIX-b implements):**

1. Frozen apply-path order-of-operations (§GSW.3), including `_apply_plan` marker-after-commit
   (§GSW.3.4).
2. Frozen branch-identity capture + restore-on-failure contract (§GSW.4).
3. Regime matrix for `muse+git-mirror`, `muse-only`, `git-only` (§GSW.5).
4. Adapter / `commit_feature` dirty-tree contract (§GSW.6).
5. Explicit non-goals (§GSW.7).
6. Security / privacy checklist (§GSW.8).
7. Auto deliverables (§GSW.9).
8. Seven-tier regression matrix including dirty-tree `--write` on all regimes (§GSW.10).
9. Definition of Done + hard stops (§GSW.11–§GSW.12).

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected |
| --- | --- |
| Redesign of freeze review or build-verification | Incident is write-path order + rollback only |
| Changing D1/D2/D3, realign guard, NEXT regen, or GFG stamp sites beyond §GSW.3.4 | Compose with 9A-5 / GS-PASTE / GFG / PMHF; only `_apply_plan` mid-apply marker timing is amended |
| New CLI subcommand or exit-code renumbering | Surface stays `ok governance-sync [--write]`; exit `2` on VCS failure remains |
| Silent commits / merges to `main`, staging push, live flips | Tier 3 unchanged |
| Requiring live MuseHub for baseline green | Fixtures + injectable runners; no live bridge export on the kit dev tree |
| Making `--force` Muse checkout the primary fix | Discards / overwrites risk; rejected |
| Reopening GFG dry-run / fully_aligned stamp sites | Only `_apply_plan` mid-apply stamp timing is amended (§GSW.3.4); other GFG stamp sites stay |
| Moving realign to after feature-branch switch | Unproven; freeze keeps realign on the original branch (§GSW.3.1 step B) |
| GSW-FIX-b Auto implementation in the Thinking phase | SD-3 split |

---

## §GSW.3 — HOW (frozen order-of-operations)

**Decision: branch setup BEFORE doc writes (primary).** Dirty-carry Muse checkout
(`muse checkout --autoshelf` or `muse checkout --merge`) is an **allowed secondary adapter guard**
only when a checkout is still required while the tree is dirty — it must **not** preserve today’s
engine order of “write docs, then ensure branch.”

### §GSW.3.1 — Apply / `--write` sequence (frozen)

Inside `_apply_plan` (or equivalent helper extracted by Auto), the successful path MUST be:

| Step | Action | Notes |
| --- | --- | --- |
| A | Capture `original_branch_state` | Regime-specific — see §GSW.4.1 |
| B | Realign guard (unchanged semantics) | Existing `execute_realign_guard` runs **on the original branch** (today’s timing). Must **not** move to after feature-branch switch — `muse bridge git-import` targets muse main via `--branch`, but running it after a sync-branch switch + dirty docs is an unproven reorder; freeze preserves original-branch realign. On failure → zero doc writes, zero feature-branch switch (nothing to roll back beyond reporting). |
| C | Ensure feature branch exists and **current HEAD(s) are on it** | `_ensure_feature_branch` amended per §GSW.5; must complete **before** any handover/roadmap patch write |
| D | Write handover + roadmap patch bytes | Existing `atomic_write_text` pair |
| E | `adapter.commit_feature(...)` | Must succeed with dirty docs already on the feature branch (§GSW.6) |
| F | Sync marker write when D1+D2 aligned | **Only after successful commit** — see §GSW.3.4 (GFG §GFG.5.3 mid-apply rule) |
| G | Feature-branch push (regime-appropriate; unchanged Tier-1 rule) | Existing `_push_feature_branch` |

**Forbidden order (today’s bug):** any path that writes handover/roadmap patches **before** step C
completes successfully.

**Also forbidden:** writing the GFG sync marker before step E succeeds (see §GSW.3.4).

### §GSW.3.2 — Dry-run (unchanged)

`--dry-run` (default) still plans patches and reports would-commit branch; it writes no doc patches,
creates no branch, performs no realign apply, creates no commit. GFG dry-run marker carve-out
(§GFG.5.3 fully_aligned / D1+D2-aligned dry-run paths) is unchanged. GSW-FIX does not alter
dry-run inertness for handover/roadmap bytes.

### §GSW.3.3 — Narrow 9A-5 §7 amendment

9A-5 §7 (“Never write partial state… working tree is left clean, or the failure is reported with
the tree untouched”) is **amended** for branch posture:

- On mid-apply failure after step C (feature-branch switch), restored state MUST include:
  1. original handover bytes,
  2. original roadmap bytes,
  3. prior marker bytes / absent per §GSW.3.4,
  4. **original branch identity** per §GSW.4.
- “Tree untouched” means **operator-visible branch + doc bytes + marker posture**, not “leave the
  operator on a newly created sync branch after a failed apply.”

No other 9A-5 §4 / §5 / §6 redesign.

### §GSW.3.4 — Narrow GFG marker amendment (mid-apply)

GFG §GFG.5.3 already freezes: **Must not stamp on mid-apply failure.** Today’s
`_apply_plan` writes the marker **before** `_ensure_feature_branch` / `commit_feature`
(`tools/governance_hygiene/engine.py` lines 490–519), which can leave
`.overseer/last_governance_sync` stamped after a failed commit while docs were rolled back.

**Frozen amendment for the `_apply_plan` success path only:**

1. Capture prior marker bytes (or “absent”) at the start of `_apply_plan` when a stamp might occur.
2. Write/refresh the enriched marker **only after** `commit_feature` returns success (step E).
3. On any mid-apply failure before that success: do **not** leave a newly written stamp — restore
   prior marker bytes if this run overwrote them, or leave absent if it was absent.
4. Fully_aligned early-return and dry-run D1+D2 stamp sites from GFG remain as frozen in GFG
   (out of GSW-FIX reorder scope except that `_apply_plan` must obey the mid-apply rule).

---

## §GSW.4 — Branch capture + rollback (frozen)

### §GSW.4.1 — `original_branch_state` (capture at step A, before any mutation)

| Regime | Captured fields (minimum) |
| --- | --- |
| `git-only` | `git_branch` = `git rev-parse --abbrev-ref HEAD` |
| `muse-only` | `muse_branch` = `muse rev-parse --abbrev-ref HEAD` |
| `muse+git-mirror` | **both** `git_branch` and `muse_branch` |

Capture failures (unreadable HEAD) → fail closed exit `2` with the exact failing command; **zero**
doc writes; **zero** branch switches.

### §GSW.4.2 — Restore on every failure path after step C

Any failure after step C begins (feature-branch ensure / write / commit) that returns a
non-success `GovernanceSyncResult` MUST, in this order:

1. Restore handover + roadmap original bytes (existing behavior).
2. Restore marker per §GSW.3.4 (no new stamp left behind).
3. Restore branch identity:
   - `git-only`: `git checkout <git_branch>` (or equivalent) when current git HEAD ≠ captured.
   - `muse-only`: `muse checkout <muse_branch>` when current muse HEAD ≠ captured.
   - `muse+git-mirror`: restore **both**; if one restore fails, report the exact failing command and
     still attempt the other (best-effort dual restore), exit non-zero.
4. Not leave the operator on `plan.feature_branch` after a failed apply.

**Step C itself fails** (cannot create/switch to feature branch): no doc writes have occurred yet
(per §GSW.3.1); if a partial switch occurred, still restore `original_branch_state`.

**Step B (realign) fails:** no feature-branch switch and no doc writes — report and exit; no
branch restore required.

**Success path:** operator remains on `plan.feature_branch` (intentional); no restore.

### §GSW.4.3 — Rollback must not use `--force` as the default restore

Preferred rollback checkout order: restore doc bytes first (§GSW.4.2 step 1) so the tree is often
clean, then restore branch with a normal checkout. If the tree is still dirty, Muse restore may use
the same dirty-carry flags as §GSW.6 (`--autoshelf` or `--merge`). `--force` is forbidden as the
default rollback mechanism (data-loss risk).

---

## §GSW.5 — Regime matrix (frozen)

| Regime | Step C must place on feature branch | Step E commit substrate | Rollback restores |
| --- | --- | --- | --- |
| `git-only` | Git HEAD | Git (`adapters/git_only`) | `git_branch` |
| `muse-only` | Muse HEAD | Muse (`adapters/muse_only`) | `muse_branch` |
| `muse+git-mirror` | **Git HEAD and Muse HEAD** | Muse commit via `adapters/muse_git_mirror` (canonical); Git feature branch already matches for push | **both** `git_branch` and `muse_branch` |

### §GSW.5.1 — `muse+git-mirror` dual-HEAD rule (frozen)

Today `_ensure_feature_branch` switches **git only** (`engine.py` lines 656–668) while Muse moves
later inside `commit_feature` (`adapter.py` line 185). That split is the live failure window.

**Frozen rule:** under `muse+git-mirror`, step C is incomplete until **both** of the following are
true before step D (doc writes):

1. `git rev-parse --abbrev-ref HEAD` == `plan.feature_branch`
2. `muse rev-parse --abbrev-ref HEAD` == `plan.feature_branch`

Auto may implement dual ensure inside `_ensure_feature_branch`, or split helpers, as long as the
pre-write invariant holds.

### §GSW.5.2 — Feature-branch create semantics

| Regime | Create if missing | Switch if exists |
| --- | --- | --- |
| `git-only` | `git checkout -b <branch>` | `git checkout <branch>` |
| `muse-only` | `muse checkout -b <branch>` | `muse checkout <branch>` (dirty-carry if needed — §GSW.6) |
| `muse+git-mirror` | create/switch on **both** sides | both sides; names MUST match `plan.feature_branch` |

Protected-branch refusal (`main` / configured main) remains adapter-enforced (9A-5 §6).

---

## §GSW.6 — `commit_feature` dirty-tree contract (frozen)

### §GSW.6.1 — Already-on-branch short-circuit (required)

For all three adapters, `commit_feature` MUST NOT fail solely because handover/roadmap paths are
dirty when HEAD is **already** `branch`:

1. Probe current branch (`rev-parse --abbrev-ref HEAD` or existing equivalent).
2. If current == `branch`, **skip** checkout; proceed to add/commit.
3. If current ≠ `branch`, perform checkout per §GSW.6.2.

This matches the post-§GSW.3 world (engine already switched) and hardens against double-checkout.

### §GSW.6.2 — Checkout when not on branch (Muse regimes)

If a Muse checkout is still required and the working tree has uncommitted tracked changes:

| Option | Verdict |
| --- | --- |
| Bare `muse checkout <branch>` (today) | **FORBIDDEN** as the sole behavior — live defect |
| `muse checkout --autoshelf <branch>` | **ALLOWED** secondary guard |
| `muse checkout --merge <branch>` | **ALLOWED** secondary guard |
| `muse checkout --force <branch>` | **FORBIDDEN** as default |

Auto picks one allowed secondary guard and covers it in tests; documenting the choice in the
implementation commit message / change-log is enough (no Tier-2 schema change).

### §GSW.6.3 — Git adapter

Git already carries dirty changes across checkout. Keep refuse-protected-branch + path validation.
Still implement §GSW.6.1 short-circuit for symmetry and fewer spurious checkouts.

---

## §GSW.7 — Non-goals (echo)

- No freeze/BV redesign.
- No change to dry-run default inertness.
- No docs-only auto-open PR to `main` (SD-11).
- No `muse bridge git-export` on the kit dev tree (SD-14).
- No consumer re-init requirement for DONE.

---

## §GSW.8 — Security / privacy checklist

- No secrets in commit messages, rollback logs, or fixtures.
- Shell-safe quoting for branch names via existing `quote_arg` / adapter argv lists — branch names
  from config patterns remain data, never interpolated unsafely.
- Fail closed on unreadable HEAD / failed checkout / failed commit — exit `2` with exact command.
- Least privilege: `git-only` never invokes Muse; `muse-only` never invokes git/gh.
- No `--force` checkout as default (data loss).
- No writes to protected branches.

---

## §GSW.9 — Auto deliverables (GSW-FIX-b)

| Change | Location |
| --- | --- |
| Reorder `_apply_plan`: capture → realign (original branch) → ensure feature branch (regime matrix) → write docs → commit → marker (D1+D2) → push | `tools/governance_hygiene/engine.py` |
| Dual-HEAD ensure for `muse+git-mirror` before writes | `engine.py` `_ensure_feature_branch` (or helper) |
| Rollback restores docs + marker + `original_branch_state` on every post-switch failure path | `engine.py` |
| `commit_feature` already-on-branch short-circuit | `adapters/{git_only,muse_only,muse_git_mirror}/adapter.py` |
| Muse dirty-carry checkout when switch still required | `adapters/muse_only/adapter.py`, `adapters/muse_git_mirror/adapter.py` |
| Seven-tier tests per §GSW.10 | `tests/{unit,integration,e2e,stress,data_integrity,performance,security}/` |
| ROADMAP + HANDOVER close together; `/build-verification-review` → `pass` before DONE | governance docs |

**Exit codes:** unchanged (`0` success; `2` VCS/apply failure; other existing codes retain meaning).

---

## §GSW.10 — Seven-tier test matrix (GSW-FIX-b)

| Tier | Frozen case |
| --- | --- |
| **unit** | (1) `_ensure_feature_branch` / apply-plan ordering helper: given a spy, assert no doc write precedes successful branch ensure; assert realign is invoked before branch ensure. (2) `commit_feature` already-on-branch skips checkout (all three adapters). (3) Muse adapter off-branch + dirty → uses `--autoshelf` or `--merge`, never bare checkout-only. (4) Rollback helper restores captured branch field(s). (5) Marker write is not invoked when commit fails. |
| **integration** | Injected-runner `--write` on each regime config fixture (`git-only`, `muse-only`, `muse+git-mirror`): simulate dirty handover/roadmap **after** branch ensure; commit succeeds; call log shows realign (or skip) → branch ensure → writes → commit → marker. |
| **e2e** | **Dirty-tree `--write` on all three regimes** (mandatory gap close): fixture starts on `main` (or regime main), apply path creates/switches to sync feature branch, patches docs, commits; `main` untouched; PR URL print rules unchanged for git regimes; `muse-only` never invokes git. |
| **stress** | Repeated apply with induced commit failure after branch switch (N≥20): every failure restores original branch; no strand accumulation of `feat/governance-sync-*` as current HEAD. |
| **data-integrity** | Induced failure after branch switch + after doc write: docs bytes == originals; current branch == captured original; no feature commit; marker absent or restored to prior bytes (GFG mid-apply rule); second successful `--write` then produces exactly one feature-branch commit bundling handover+roadmap and may stamp marker only after that success when D1+D2 aligned. |
| **performance** | Reordered apply path on kit-sized docs stays within existing governance-sync performance bound (no extra unbounded VCS log scans). |
| **security** | (1) Branch name with shell metacharacters cannot break quoting (fail closed or safe argv). (2) `git-only` write path call log contains zero `muse` argv. (3) `muse-only` write path call log contains zero `git`/`gh` argv. (4) No `--force` checkout in default success/rollback paths. |

**Coverage gate (frozen):** GSW-FIX-b is incomplete if dirty-tree `--write` exists only for
`git-only`. All three regimes are required.

---

## §GSW.11 — Definition of Done (GSW-FIX-b)

- [ ] `_apply_plan` order: realign on original branch → ensure feature branch → write docs → commit → marker (§GSW.3.1)
- [ ] Feature branch ensure (regime matrix) **before** handover/roadmap writes
- [ ] `muse+git-mirror` dual-HEAD on feature branch before writes (§GSW.5.1)
- [ ] Rollback restores docs + marker + original branch on every failure path after switch (§GSW.4)
- [ ] `commit_feature` already-on-branch short-circuit + Muse dirty-carry when needed (§GSW.6)
- [ ] Seven-tier §GSW.10 green, including dirty-tree `--write` on all three regimes
- [ ] `/build-verification-review` → `pass` before ROADMAP **DONE**
- [ ] `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17)
- [ ] No consumer re-init; no feature→GitHub-`main` without Tier 3; no secrets

---

## §GSW.12 — Hard stops

- No GSW-FIX-b Auto implementation during GSW-FIX-a
- No merge to `main` / staging push / live posture flips without Tier 3
- No live `muse bridge git-export` on the kit dev tree
- No `--force` as default checkout/rollback
- No freeze/BV redesign

---

## §GSW.13 — Cross-references

- `docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — §6 commit strategy, §7 error handling
- `tools/governance_hygiene/engine.py` — `_apply_plan`, `_ensure_feature_branch`
- `adapters/muse_git_mirror/adapter.py` — `commit_feature` Muse checkout
- `adapters/muse_only/adapter.py` / `adapters/git_only/adapter.py` — peer `commit_feature`
- `tests/e2e/test_governance_sync_cycle.py` — current git-only write coverage gap
- `docs/OVERSEER-KIT-SPEC.md` §6 — freeze review policy
- `policy/test-tiers.yaml` — seven-tier contract

---

## Freeze-review findings ledger

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | consistency | `docs/archive/phases/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` §GSW.3.1 (pre-fix); `tools/governance_hygiene/realign.py:40-98`; `adapters/muse_git_mirror/adapter.py:147-158` | First draft placed realign after feature-branch switch. That reorders realign relative to today’s original-branch timing without proving dirty feature-branch + `git-import --branch <muse_main>` safety. Freeze must keep realign before feature-branch ensure. |
| R1-M2 | MAJOR | consistency | `docs/archive/phases/PHASE-GFG-GOVERNANCE-FRESHNESS-GATE.md` §GFG.5.3 (“Must not stamp on mid-apply failure”); `tools/governance_hygiene/engine.py:490-535` | First draft kept marker write before commit. On commit failure, docs roll back but marker can remain — contradicts GFG mid-apply rule. Freeze must stamp marker only after successful `commit_feature` in `_apply_plan`. |
| R2-M1 | MAJOR | consistency | `docs/archive/phases/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` §GSW.2 non-goals (pre-fix) vs §GSW.3.4; freeze YAML `frozen_inputs` | Non-goal claimed no GFG marker semantic change while §GSW.3.4 amends `_apply_plan` stamp timing; GFG was not listed as a frozen input despite the amendment edge. |
