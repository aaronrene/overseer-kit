# Phase GSB — Governance-sync dated-branch collision

Status: **Reviewed → `pass` (GSB-r3).** GSB-a is **spec-only** and now frozen; no product code
lands in this phase. GSB-b (Auto) is cleared to build mechanically against this contract.

```yaml
phase: GSB
outputs:
- id: gsb-governance-sync-branch-collision
  path: docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md
  frozen: true
frozen_inputs:
- id: phase-9a5-commit-strategy
  path: docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
- id: gsw-fix-write-path
  path: docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md
- id: governance-hygiene-engine
  path: tools/governance_hygiene/engine.py
- id: muse-git-mirror-adapter
  path: adapters/muse_git_mirror/adapter.py
- id: muse-only-adapter
  path: adapters/muse_only/adapter.py
- id: git-only-adapter
  path: adapters/git_only/adapter.py
- id: governance-sync-cli
  path: cli/commands/governance_sync.py
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
review_stamp:
  reviewed_at: '2026-07-31T20:09:56Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:30cfb99945282ffb3cd8f0624c95565fea6eac99a7659652d4bdcaaff1443a1e
```

**Downstream edge:** GSB-b treats this document as ground truth without re-deriving it
(SPEC §6 mandatory reviewed freeze). It closes the permanent gap exposed live on 2026-07-31 while
dogfooding PLS land-b: a second same-day `ok governance-sync --write` reuses the dated sync branch
`feat/governance-sync-<yyyy-mm-dd>`; under `muse+git-mirror` the Muse-first ensure checks out the
**stale** Muse tip into the shared working tree, which dirties Git relative to the intended tip, so
`git checkout feat/governance-sync-<date>` refuses with “local changes would be overwritten”
(engine exit `2`).

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge to
`main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| GSB-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R1-M1** `PatchPlan` is `frozen=True` — “update `plan.feature_branch`” underspecified; **R1-M2** `T_current` = HEAD tip fails when Muse HEAD already on stale `B` while Git is on advanced main; **R1-M3** Muse tip form cited `muse branch -f` (no such flag) / vague `-C`; prefer `muse update-ref`; **R1-M4** `git branch -f` vs forbidden checkout `--force` not distinguished; **R1-M5** `pr_url` rebuilt after uniquify. Fixed in-doc. |
| GSB-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | **R2-M1** residual `T_current` wording in §GSB.3.4 after R1 rename to `T_target`; **R2-N1** C0 “remain on original_branch_state” contradicted `O_H == B` tip-update case. Fixed in-doc. |
| GSB-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | Checklist gate clean (0 findings). Semantic re-read: R1-M1–M5 / R2-M1 / R2-N1 RESOLVED; live defect evidence + C0-before-C1 + `T_target` base-ref rules + Muse-never-dirties-Git + frozen-plan uniquify + seven-tier same-day-collision on all three regimes present; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation (Tier-1 CLI fix; merge remains Tier 3). Stamp written by `ok review --freeze`. |

---

## §GSB.0 — Simple summary

At the end of a work session the helper updates two living notes and saves them on a side branch
named with today’s date. If you run that helper twice on the same calendar day, the second run
tries to reuse yesterday’s-same-day side branch. On the Muse+Git setup, Muse switches to that old
side branch first and rewrites the shared files on disk to the old tip. Git then refuses to switch
to the same branch name because those rewritten files would be overwritten. The sync fails even
though nothing is wrong with the notes themselves.

**This phase freezes the permanent fix:** before switching either history onto the dated sync
branch, the engine must **reconcile** that name — if the existing branch tip is an ancestor of the
current tip, fast-forward the branch tip to the current tip **without** checking it out first; if
it is not an ancestor, pick a new deterministic uniquified name. Only after reconciliation may the
existing dual-HEAD ensure run. Muse must never leave the Git working tree dirtied by a stale-tip
checkout.

**Technical summary:** amend `tools/governance_hygiene/engine.py` so `_ensure_feature_branch`
(or a helper it calls) runs a **reconcile step** against `plan.feature_branch` on every history
that already has that branch, **before** any Muse/Git checkout of that name; update
`plan.feature_branch` when uniquified; compose with frozen GSW order
(`capture → realign → ensure → write → commit → marker → push`) without redesigning rollback or
`commit_feature`; `--force` stays forbidden; freeze a seven-tier matrix that requires
same-day-collision `--write` on **all three** regimes.

---

## §GSB.1 — Verified incident (do not redesign around folklore)

Live overseer-kit dogfood during PLS land-b post-merge sync (2026-07-31), regime
`muse+git-mirror`:

| Fact | Evidence |
| --- | --- |
| Second same-day closeout reuses dated sync branch | `_feature_branch_name` in `tools/governance_hygiene/engine.py` lines 579–582 builds `governance-sync-{date.today().isoformat()}` only — no collision suffix |
| Prior same-day sync branch still present on both histories | Live tree had `feat/governance-sync-2026-07-31` from earlier GSW-FIX / closeout syncs the same calendar day (handover change-log 2026-07-31; git branches include that name) |
| Muse ensure runs **before** Git ensure | `_ensure_feature_branch` lines 711–718: Muse path for `muse-only`/`muse+git-mirror`, then Git path for `git-only`/`muse+git-mirror` |
| Existing Muse branch → bare/`--autoshelf` checkout of **stale tip** | `_ensure_muse_branch` lines 739–747: `checkout -b` fails → `checkout <branch>` / `checkout --autoshelf <branch>` — no tip-reconcile before switch |
| Shared working tree: Muse checkout rewrites disk bytes to stale tip | Muse 0.2.x checkout updates the shared worktree; Git then sees those bytes as local modifications vs the intended tip |
| Git checkout of same name refuses | `_ensure_git_branch` lines 761–767: after create fails, `git checkout <branch>` returns non-ok when “local changes would be overwritten” |
| Engine exit `2` | `_apply_plan` lines 512–518: `_ensure_feature_branch` non-`None` → `_failure(2, …)` |
| Manual unblock used ancestor FF + Muse tip reset (not checkout `--force`) | Operator live remediation: git tip fast-forward when stale tip was ancestor of current tip, plus Muse tip reset via force-copy / equivalent (`muse branch -C <src> <dest>` copy-force, or `muse update-ref`) so Muse no longer pointed at pre-PLS content — then re-run succeed path. Not `muse checkout --force`. |
| GSW-FIX already fixed write-before-branch and dirty-carry | Frozen `docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` §GSW.3 / §GSW.5 / §GSW.6 — **composed**, not redesigned. GSW does not address same-day dated-name tip collision |
| Coverage gap | Existing GSW / governance-sync suites exercise dirty-tree `--write` and some “branch already exists” paths, but do **not** require a same-day second `--write` where the existing dated branch tip is **behind** the current tip on Muse under `muse+git-mirror` |

**Root cause:** dated branch name is calendar-day unique only; tip reuse without reconcile + Muse-first
checkout of a stale tip mutates the shared worktree before Git can switch — fail-closed exit `2`.

**Not the root cause (do not “fix” these instead):**

- GSW apply order (already correct: ensure before write).
- `commit_feature` dirty-carry / already-on-branch short-circuit (secondary; never reached when ensure fails).
- Rollback / marker timing (GSW).
- Using `--force` Muse/Git checkout (forbidden — data-loss risk).

---

## §GSB.2 — Scope

**In scope (GSB-a freezes; GSB-b implements):**

1. Frozen reconcile-before-ensure contract for an already-existing dated sync branch (§GSB.3).
2. Fast-forward when existing tip is an ancestor of the current tip; deterministic uniquify otherwise (§GSB.3.2–§GSB.3.3).
3. Muse-first / dual-HEAD ensure must never dirty the Git tree via stale-tip checkout (§GSB.3.4).
4. Regime matrix for `git-only`, `muse-only`, `muse+git-mirror` (§GSB.4).
5. Explicit non-goals (§GSB.5).
6. Security / privacy checklist (§GSB.6).
7. Auto deliverables (§GSB.7).
8. Seven-tier regression matrix including same-day-collision `--write` on all three regimes (§GSB.8).
9. Definition of Done + hard stops (§GSB.9–§GSB.10).

**Out of scope (explicit non-goals):**

| Non-goal | Why rejected |
| --- | --- |
| Redesign of GSW `_apply_plan` order / rollback / marker timing | Compose with GSW; only amend ensure/reconcile |
| Redesign of `commit_feature` / adapter dirty-carry | Ensure must succeed before commit; out of GSB scope |
| `--force` checkout as the fix | Data-loss risk; forbidden (GSW §GSW.4.3 / §GSW.6.2) |
| Changing calendar slug format (`governance-sync-<yyyy-mm-dd>`) as the sole fix | Suffix uniquify is additive; base slug stays 9A-5 §6 |
| New CLI flag / exit-code renumbering | Surface stays `ok governance-sync [--write]`; exit `2` on VCS failure remains |
| Silent commits / merges to `main`, staging push, live flips | Tier 3 unchanged |
| Requiring live MuseHub for baseline green | Fixtures + injectable runners |
| GSB-b Auto implementation in the Thinking phase | SD-3 split |

---

## §GSB.3 — HOW (frozen reconcile-before-ensure)

### §GSB.3.1 — Placement in the GSW sequence (frozen)

GSW §GSW.3.1 successful path remains:

`A capture → B realign → C ensure feature branch → D write → E commit → F marker → G push`

**GSB amends step C only.** Step C becomes:

| Sub-step | Action |
| --- | --- |
| C0 | **Reconcile** candidate name `plan.feature_branch` against each applicable history (§GSB.3.2–§GSB.3.3). May replace the frozen plan (or thread a reconciled name) when uniquifying. Runs before C1; must **not** use checkout-of-`B` as the tip-advance mechanism. When `O_H ≠ B`, remain on `original_branch_state` through C0 tip probes/updates. When `O_H == B`, tip update via `update-ref` / `branch -f` / Muse `-C` copy is allowed while HEAD already names `B`. |
| C1 | Dual-HEAD / regime ensure onto the **reconciled** feature-branch name (existing `_ensure_muse_branch` / `_ensure_git_branch` semantics from GSW §GSW.5 — create if missing, switch if exists). |

**Forbidden:** any Muse or Git checkout of the candidate dated name **as the C0 tip-advance mechanism** before C0 classification + tip update complete for that history.

**Forbidden:** leaving C0 incomplete (partial tip move on one history) and then proceeding to C1 without fail-closed restore of `original_branch_state` per GSW §GSW.4.

Dry-run remains inert for branch create/switch/reconcile (GSW §GSW.3.2 unchanged).

### §GSB.3.2 — Existence probe + tip classification (frozen)

Let `B` = candidate branch name (`plan.feature_branch` after `_feature_branch_name`, before uniquify).

Ancestor checks are **per-history** (Git SHAs and Muse `sha256:` ids are different object spaces — never cross-compare).

For each applicable history H ∈ regime set (§GSB.4):

1. Probe whether `B` exists on H (branch listing / `rev-parse` / equivalent fail-closed probe).
2. If `B` does **not** exist on H → no tip reconcile on H; C1 may create it.
3. If `B` exists on H:
   - Let `T_exist` = tip commit of `B` on H.
   - Let `T_target` = tip of the **reconcile base ref** on H (§GSB.3.2.1) — **not** blindly “current HEAD” when HEAD is already `B`.
   - Classify:
     - **ancestor:** `T_exist` is an ancestor of `T_target` on H (including equal tips) → contributes to **fast-forward path** (§GSB.3.3).
     - **diverged / not ancestor:** → contributes to **uniquify path** (§GSB.3.3).
   - Probe failure / unreadable tip → fail closed exit `2` with the exact failing command; zero doc writes; restore per GSW if any partial mutation occurred.

#### §GSB.3.2.1 — Reconcile base ref → `T_target` (frozen)

For history H, with captured original branch name `O_H` from `original_branch_state`:

| Condition | Base ref used for `T_target` |
| --- | --- |
| `O_H` is non-empty and `O_H ≠ B` | `O_H` (live PLS land-b case: operator on `main`, dated `B` exists behind) |
| `O_H == B` (HEAD already on the dated sync branch) | Configured main for that history: Git → `vcs.git.main_branch`; Muse → `vcs.muse.main_branch` |

Rationale: if Muse HEAD is already stranded on stale `B` while Git HEAD is on advanced `main`, defining `T_target` as Muse HEAD would classify Muse as “equal tips” and skip FF — leaving the shared worktree at the stale tip so Git checkout of a FF’d `B` still fails. Falling back to configured main when `O_H == B` forces the stale tip to be evaluated against main.

When `O_H == B` and `B` has commits **not** in main (diverged from main), classification is uniquify — do **not** rewind `B` onto main.

**Cross-history rule (`muse+git-mirror`):**

- Run classification on **both** Muse and Git when `B` exists on either side.
- If **either** side classifies as diverged/not-ancestor → take the **uniquify** path for the shared name (do not FF one side and uniquify the other under the same `B`).
- If both sides that have `B` classify as ancestor (or one side lacks `B`) → take the **fast-forward** path: FF every side that has `B` and is behind its `T_target`; create-on-ensure for a side that lacks `B`.

### §GSB.3.3 — Fast-forward vs deterministic uniquify (frozen)

#### Fast-forward path

Update the tip of `B` on each history that has it so `B` points at that history’s `T_target`, **without checking out `B` as the means of advancing the tip** (no “checkout stale `B` then merge” as the primary FF mechanism):

| History | Allowed tip-update forms (Auto picks one; tests lock the call shape) |
| --- | --- |
| Git | `git branch -f <B> <T_target>` **or** `git update-ref refs/heads/<B> <T_target>` — these are **ancestor-validated tip moves**, not `git checkout --force` |
| Muse | **Preferred:** `muse update-ref <B> <T_target>` (moves ref without merge; does not use checkout). **Allowed alternate:** `muse branch -C <base_ref> <B>` (force-**copy** base onto name `B`, per Muse 0.2.x). **Forbidden:** `muse checkout --force <B>` |

After FF, `B` remains the plan’s feature-branch name. Proceed to C1 (switch/create). Because tips match `T_target`, Muse switch onto `B` must not rewrite worktree bytes away from the Git-visible tip that C1 will require (§GSB.3.4). If a tip-only update leaves a stale worktree while HEAD already names `B`, Auto MUST refresh worktree to `T_target` without checkout `--force` (e.g. checkout/`reset` forms that do not discard unrelated operator work — fail closed if refresh would clobber unrelated dirty files outside this ensure path’s contract).

**Equal tips:** treating equal as ancestor is required (no-op tip update allowed; must not uniquify solely because tips are equal).

#### Uniquify path

When any applicable history has `B` with a non-ancestor tip relative to that history’s `T_target`:

1. Derive a **deterministic** alternate name: start from base `B`, append suffix `-2`, then `-3`, … until the candidate is free on **all** applicable histories for the regime.
2. Determinism: given the same base name and the same set of existing branch names on those histories, the chosen suffix MUST be identical across runs (lowest integer N≥2 that is free everywhere required).
3. Because `PatchPlan` is a frozen dataclass (`tools/governance_hygiene/types.py`), Auto MUST **replace** the plan (e.g. `dataclasses.replace`) with the uniquified `feature_branch` and a **rebuilt** `pr_url` from `_build_pr_url(..., uniquified)` before C1 / commit / push. Returning a reconciled branch string from the ensure helper and threading it through `_apply_plan` is an allowed equivalent — the success-path commit, push, and result `plan.feature_branch` MUST all observe the reconciled name.
4. Do **not** delete or rewind the diverged existing `B`; do **not** use checkout `--force` on it.
5. C1 then create/switch the uniquified name as a normal missing branch (or ensure if somehow present and equal — still subject to §GSB.3.2 if a race recreated it; fail closed on unexpected tip mismatch).

**Slug / pattern:** uniquify amends only the final branch string after
`feature_branch_pattern.replace("{slug}", "governance-sync-<date>")`. Do not change the date
slug format itself.

### §GSB.3.4 — Muse must never dirty the Git tree (frozen invariant)

Under `muse+git-mirror`, after C0 and during C1:

1. Muse checkout/switch of the reconciled branch MUST NOT leave the Git worktree with
   modifications relative to the Git `T_target` that would cause `git checkout <reconciled>` to
   refuse with “local changes would be overwritten”.
2. Achieving (1) via `git checkout --force` or `muse checkout --force` is **FORBIDDEN**.
   Ancestor-validated tip moves (`git branch -f` / `git update-ref` / `muse update-ref` /
   `muse branch -C <base> <B>`) are **ALLOWED** under §GSB.3.3 and are not “checkout `--force`”.
3. Achieving (1) solely by reordering to Git-first without tip reconcile is **FORBIDDEN** — a
   stale Muse tip remaining would still break the dual-HEAD invariant or later Muse commit path;
   tip reconcile is mandatory.
4. Preferred satisfaction: C0 FF (or uniquify to a fresh name at `T_target`) so Muse switch is a
   no-content-change relative to the target tip, then Git switch succeeds with a clean relative
   tree.

### §GSB.3.5 — Failure + rollback composition

- C0/C1 failures → exit `2` with exact failing command (existing ensure failure mapping).
- Doc writes have not occurred yet (GSW order) → rollback uses `restore_docs=False` path but MUST
  still restore `original_branch_state` if any HEAD moved (GSW §GSW.4.2).
- C0 tip updates that succeed on one history and fail on the other → fail closed; best-effort
  restore original HEADs; do **not** leave docs written; do **not** stamp marker.
- Success path: operator remains on reconciled `plan.feature_branch` (GSW success posture).

---

## §GSB.4 — Regime matrix (frozen)

| Regime | Histories in C0/C1 | Same-day collision `--write` required |
| --- | --- | --- |
| `git-only` | Git only | **Yes** — existing dated branch tip behind current tip → FF then ensure; diverged → uniquify |
| `muse-only` | Muse only | **Yes** — same classify/FF/uniquify; no git argv |
| `muse+git-mirror` | **Both** (shared name; §GSB.3.2 cross-history rule) | **Yes** — mandatory gap close for the live PLS land-b defect |

Protected-branch refusal (`main` / configured main) remains adapter-enforced (9A-5 §6). Reconcile
MUST NOT retarget protected main; it only updates tips of the dated **feature** branch name (or
chooses a new feature name).

---

## §GSB.5 — Non-goals (echo)

- No GSW order / rollback / marker redesign.
- No `commit_feature` redesign.
- No `--force` as default checkout or tip rewrite of unrelated branches.
- No dry-run branch mutation.
- No docs-only auto-open PR to `main` (SD-11).
- No `muse bridge git-export` on the kit dev tree (SD-14).
- No consumer re-init requirement for DONE.
- No GSB-b Auto code in GSB-a.

---

## §GSB.6 — Security / privacy checklist

- No secrets in commit messages, reconcile logs, or fixtures.
- Shell-safe quoting for all branch names via existing `quote_arg` / argv lists — branch names and
  suffixes remain data, never interpolated unsafely.
- Fail closed on unreadable tip / failed FF / failed uniquify probe / failed ensure — exit `2`.
- Least privilege: `git-only` never invokes Muse; `muse-only` never invokes git/gh.
- No checkout `--force` as default success or failure path (distinct from ancestor-validated
  `git branch -f` / `muse update-ref` / `muse branch -C` tip moves on the **feature** branch).
- No writes to protected branches; uniquify/FF target only feature-branch names.
- Deterministic uniquify must not embed secrets, absolute paths, or hostnames in the suffix.

---

## §GSB.7 — Auto deliverables (GSB-b)

| Change | Location |
| --- | --- |
| Reconcile-before-ensure (C0) for existing dated sync branch: ancestor → FF tip without checkout-as-FF of `B`; else deterministic `-N` uniquify; `dataclasses.replace` (or equivalent) so success-path commit/push/result plan observe reconciled name + rebuilt `pr_url` | `tools/governance_hygiene/engine.py` (`_ensure_feature_branch` and/or new helper); `types.PatchPlan` stays frozen |
| Preserve GSW C1 dual-HEAD ensure + rollback composition | `engine.py` |
| Do **not** change `_apply_plan` order outside C0 insertion; do **not** redesign `commit_feature` | adapters unchanged unless a tiny tip-probe helper is strictly required and covered by tests |
| Seven-tier tests per §GSB.8 | `tests/{unit,integration,e2e,stress,data_integrity,performance,security}/` |
| ROADMAP + HANDOVER close together; `/build-verification-review` → `pass` before DONE | governance docs |

**Exit codes:** unchanged (`0` success; `2` VCS/apply failure; other existing codes retain meaning).

---

## §GSB.8 — Seven-tier test matrix (GSB-b)

| Tier | Frozen case |
| --- | --- |
| **unit** | (1) Ancestor classifier: `T_exist` ancestor-of / equal-to `T_target` → FF; non-ancestor → uniquify. (2) When `O_H == B`, `T_target` resolves to configured main (not HEAD tip). (3) Uniquify picks lowest free `-N` (N≥2) given a fixture set of existing names. (4) Reconcile helper invokes tip update **without** checkout-as-FF of `B` when FF path chosen (spy/call-log; allow `update-ref` / `branch -f` / Muse `-C` copy). (5) Cross-history: one side diverged → uniquify (no partial FF of the other under same `B`). (6) Equal tips → no uniquify. (7) Uniquify replaces frozen `PatchPlan` (or threads reconciled name) so `feature_branch` + `pr_url` match. |
| **integration** | Injected-runner `--write` per regime fixture: seed existing `feat/governance-sync-<today>` behind `T_target`; assert FF then successful ensure; `plan`/push target uses original dated name. Second fixture: diverged tip → uniquified `-2` used for commit/push/`pr_url`. Third (`muse+git-mirror`): Muse HEAD already on stale `B`, Git HEAD on advanced main → C0 still FF Muse `B` to muse main / Git `B` to git main (or uniquify if diverged) so C1 does not exit `2`. |
| **e2e** | **Same-day-collision `--write` on all three regimes** (mandatory gap close): first `--write` creates dated branch + commit; second `--write` same calendar day with tip advanced on original branch (simulate post-land main tip) succeeds without exit `2`; under `muse+git-mirror`, Git worktree is never left in a state that refuses checkout after Muse ensure; `main` untouched; `muse-only` zero git argv; `git-only` zero muse argv. |
| **stress** | N≥20 alternating same-day `--write` attempts with induced ensure failure after partial C0: every failure restores `original_branch_state`; no accumulation of stranded HEADs on `feat/governance-sync-*`. |
| **data-integrity** | FF path: after success, feature-branch tip equals pre-ensure current tip + exactly one new sync commit; diverged path: original diverged `B` tip unchanged (not force-reset), uniquified branch holds the new commit; mid-C0 failure: docs bytes unchanged, marker unrestamped, HEADs restored. |
| **performance** | Reconcile probes + at most one tip update per history stay within existing governance-sync performance bound (no unbounded `git log` / Muse history scans). |
| **security** | (1) Branch / suffix with shell metacharacters cannot break quoting (fail closed or safe argv). (2) `git-only` call log contains zero `muse` argv. (3) `muse-only` call log contains zero `git`/`gh` argv. (4) No `checkout --force` in default FF / uniquify / ensure / rollback paths; ancestor-validated tip moves remain allowed. |

**Coverage gate (frozen):** GSB-b is incomplete if same-day-collision `--write` exists only for
`git-only`. All three regimes are required — this is the live `muse+git-mirror` defect class.

---

## §GSB.9 — Definition of Done (GSB-b)

- [ ] C0 reconcile runs before any checkout of the dated sync name (§GSB.3.1)
- [ ] Ancestor/equal → FF tip without checkout-as-FF of `B`; non-ancestor → deterministic `-N` uniquify + frozen-plan replace / rebuilt `pr_url` (§GSB.3.3)
- [ ] `T_target` uses §GSB.3.2.1 base-ref rules (including `O_H == B` → configured main)
- [ ] `muse+git-mirror` cross-history rule + Muse-never-dirties-Git invariant (§GSB.3.2 / §GSB.3.4)
- [ ] GSW order / rollback / `commit_feature` unchanged in contract (compose only)
- [ ] Seven-tier §GSB.8 green, including same-day-collision `--write` on all three regimes
- [ ] `/build-verification-review` → `pass` before ROADMAP **DONE**
- [ ] `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17)
- [ ] No consumer re-init; no feature→GitHub-`main` without Tier 3; no secrets; `--force` stays forbidden

---

## §GSB.10 — Hard stops

- No GSB-b Auto implementation during GSB-a
- No merge to `main` / staging push / live posture flips without Tier 3
- No live `muse bridge git-export` on the kit dev tree
- No `--force` as the collision fix
- No rollback / `commit_feature` / GSW order redesign
- No freeze/BV redesign

---

## §GSB.11 — Cross-references

- `docs/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — §6 commit strategy (dated slug)
- `docs/PHASE-GSW-FIX-GOVERNANCE-SYNC-WRITE-PATH.md` — §GSW.3 order, §GSW.5 dual-HEAD, §GSW.6 dirty-carry
- `tools/governance_hygiene/engine.py` — `_feature_branch_name`, `_ensure_feature_branch`, `_ensure_muse_branch`, `_ensure_git_branch`
- `docs/OVERSEER-KIT-SPEC.md` §6 — freeze review policy
- `policy/test-tiers.yaml` — seven-tier contract
- `docs/OVERSEER-HANDOVER.md` — PLS land-b 2026-07-31 live defect queue entry

---

## Freeze-review findings ledger

| ID | Severity | Category | Citation | Message |
| --- | --- | --- | --- | --- |
| R1-M1 | MAJOR | completeness | `tools/governance_hygiene/types.py:78-88` (`PatchPlan` `frozen=True`); first-draft §GSB.3.3 uniquify step 3 | “Update `plan.feature_branch`” is impossible in-place on a frozen dataclass; freeze must require `replace` / threaded reconciled name + rebuilt `pr_url`. |
| R1-M2 | MAJOR | ground-truth edge | first-draft §GSB.3.2 `T_current` = current HEAD tip; live asymmetric case (Muse on stale `B`, Git on main) | HEAD-as-target skips Muse FF when already on stale `B`, recreating git checkout refusal. Freeze must define `T_target` via base-ref rules (§GSB.3.2.1). |
| R1-M3 | MAJOR | completeness | first-draft §GSB.3.3 Muse row (`muse branch -f`); `muse branch --help` (flags are `-c`/`-C` copy, plus `muse update-ref`) | Cited non-existent `muse branch -f`. Freeze preferred form: `muse update-ref`; allowed alternate: `muse branch -C <base> <B>`. |
| R1-M4 | MINOR | security / consistency | first-draft §GSB.6 “No `--force`” vs FF using `git branch -f` | Must distinguish ancestor-validated tip force-update from forbidden `checkout --force`. |
| R1-M5 | MINOR | completeness | `tools/governance_hygiene/engine.py:354` builds `pr_url` before apply | Uniquify after plan construction must rebuild `pr_url` or success-path URL drifts from the branch actually pushed. |
| R2-M1 | MINOR | consistency | `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` §GSB.3.4 (pre-fix) | Residual `T_current` after R1 renamed the frozen term to `T_target`. |
| R2-N1 | MINOR | consistency | `docs/PHASE-GSB-GOVERNANCE-SYNC-BRANCH-COLLISION.md` §GSB.3.1 C0 (pre-fix) vs §GSB.3.2.1 | “Must run while still on original_branch_state (no checkout of dated name yet)” conflicted with the allowed `O_H == B` tip-update path. |
