# Phase Track O / O2 — Stage 3 kit upgrade ceremony freeze (Thinking)

Status: **Reviewed → `pass` (O2-r3).** O2 Thinking is **spec-only** and now frozen; no ceremony
code, no signup UI, no live consumer `ok init`, and no Tier-3 merge land in this phase. Closes the
§O0.3.3 deferral: defines the kit ceremony for `muse-only` → `muse+git-mirror`. The Track O / O3
Auto build (`{step}b`) is cleared to implement **`ok upgrade-regime`** as scoped in §O2.7. Do
**not** re-derive this contract during the Auto build. Products unlock Stage 3 one-click only
after §O2.6.

```yaml
phase: TRACK-O-O2
outputs:
- id: track-o-o2-stage3-upgrade-ceremony
  path: docs/PHASE-TRACK-O-O2-STAGE3-UPGRADE-CEREMONY.md
  frozen: true
frozen_inputs:
- id: track-o-o0-funnel
  path: docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md
- id: track-o-o1-product-contract
  path: docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md
- id: k7-dogfood-guardrail
  path: docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
- id: k7-operator-runbook
  path: docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md
- id: k4-vendoring-cli
  path: docs/PHASE-K4-VENDORING-CLI-CONTRACT.md
- id: kit-spec-regimes
  path: docs/OVERSEER-KIT-SPEC.md#4
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: roadmap-track-o-rows
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-13T23:02:47Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:ac970077edfe6ce01f98e25d06b8d49af0d13841149079981638b11171a661c0
```

**Downstream edge:** Track O / O3 (Auto) treats this document as ground truth without re-deriving
it (SPEC §6). Product Stage 3 one-click in Scooling/Knowtation (or other entry products) may wrap
the ceremony **only** after §O2.6 unlock criteria are met. This freeze does **not** authorize
signup UI, live consumer installs, or Tier-3 merges.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes during the loop are Tier 1 (feature branch); merge
to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| O2-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist clean (0 findings). Semantic review raised non-escalating findings below. No `security`/`irreversible`/`real_money`/`gates_tier3` escalation. |
| O2-r1 fix | Author (cited items only) | — | **R1-M1** fixed: §O2.3 C1 splits idempotent success vs incomplete-upgrade repair (C3–C5). **R1-M2** fixed: §O2.5 adds G8 local git-remote URL gate. **R1-M3** fixed: §O2.7 freezes preferred orchestrator name + flags closed set. **R1-N1** fixed: §O2.3 C0 clarifies muse-only may lack a usable git remote. |
| O2-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | Residual: product-contract Stage 3 still says "deferred to O2" after ceremony defined — but retargeting in Thinking breaks O1 §O0.8 harness keywords. No escalation. |
| O2-r2 fix | Author (cited items only) | — | **R2-M1** fixed: §O2.7 requires O3 to retarget product contract + Track O harness keywords **together**; O2 Thinking does not edit the O1 contract pack (avoids greenwash / broken e2e). C6 report aligns with G8 `ready_for_live_bridge`. |
| O2-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings). Semantic re-read confirmed R1/R2 items RESOLVED: C0–C8 ceremony; §O2.4 migrate/force + docs.* preserve; G1–G8 bridge gates; §O2.6 product unlock; §O2.7 `ok upgrade-regime` closed flags; §O2.8 rejection; §O2.9 seven-tier; K7/SD-14 held; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §O2.0 — Simple summary

Someone who started with Muse-only custody can later add GitHub backup. That change is not a
one-line config tweak: the tree must gain the full mirror setup (Git fields + bridge files) and
must publish through the safe bridge (isolated mirror → `muse-mirror` PR), never by pushing
`main`. This freeze defines that upgrade ceremony so products can later offer a one-click wrapper
without inventing shortcuts.

**Technical summary:** freeze the ordered, fail-closed kit ceremony for the allowed transition
`muse-only` → `muse+git-mirror` (O0 §O0.3.1 / §O0.3.3). The ceremony composes existing K4/K6/K7
surfaces: complete config write (no silent `vcs.regime`-only edit), footprint re-seed via
`ok sync` / `ok init --migrate` with explicit `--force` rules, bridge dry-run gates (SD-14), and
Tier-3 stop before merge to `main`. O3 Auto implements against this contract; products unlock
Stage 3 UX only after O3 build-verification `pass`.

**Recommendation:** stamp this freeze → queue **Track O / O3** Auto for the kit ceremony surface
+ seven-tier harness; keep product one-click and live consumer init out of O2/O3 kit Auto green.

---

## §O2.1 — Scope

**In scope (freeze only — this phase writes no production ceremony code):**

- Ceremony identity vs O0 deferral, K7 dogfood, and operator runbooks (§O2.2).
- Ordered ceremony steps C0–C8 for `muse-only` → `muse+git-mirror` (§O2.3).
- Config write + footprint re-seed + `--migrate` / `--force` interaction (§O2.4).
- Bridge dry-run gates and live-bridge boundaries (§O2.5).
- Product UX unlock criteria (§O2.6).
- O3 Auto deliverables (§O2.7).
- Explicit non-goals / rejection table (§O2.8).
- Seven-tier matrix O3 must satisfy (§O2.9).
- Hard stops + tier linkage (§O2.10).
- Thinking DoD + close-out (§O2.11).

**Out of scope (explicit — prevent creep):**

- **Any Auto implementation** of the ceremony in this Thinking session.
- **Signup UI, OAuth, account APIs, or marketplace plugins** in overseer-kit.
- **Live consumer `ok init`** on Scooling, Knowtation, or any named production tree.
- **Adapter rewrite** or a fourth VCS regime.
- **`git-only` → `muse+git-mirror`** ceremony (allowed transition in O0, but **not** Stage 3; needs
  its own later freeze if productized).
- **Auto-merge** of `muse-mirror` → `main`, `git push` canonical `main`, or
  `muse bridge git-export --git-dir .`.
- **Making MuseHub, Scooling, Knowtation, Cursor, or Track Q mandatory** for baseline kit use.
- **Tier-3 merge, staging push, or live capability flips** authorized by this freeze.
- **Storing GitHub tokens, vault bytes, or Knowtation credentials** inside the kit.

---

## §O2.2 — Identity (frozen)

| Artifact | Role | Not this phase |
| --- | --- | --- |
| **O0 §O0.3.3** | Deferred Stage 3; forbade silent regime edit + product one-click until O2 | Does not define steps |
| **O1 product contract** | Restates deferral for implementers | Still blocks one-click until §O2.6 |
| **K7 dogfood** | Kit self-flip `git-only` → `muse+git-mirror`; footprint membership; S1–S13 deploy script | Different start regime; operator dogfood of **this** repo |
| **K7 runbook** | Operator live evidence L1/L2 for kit self-flip | Not normie Stage 3 product UX |
| **O2 (this doc)** | Normie/product Stage 3 **kit ceremony** for `muse-only` → `muse+git-mirror` | No Auto code |
| **O3 (queued Auto)** | Implement ceremony surface + tests against this freeze | No product signup UI |

**Frozen one-liner:** O2 freezes **how** a `muse-only` personal space becomes `muse+git-mirror`
without silent config drift; it does not ship the button and does not merge to `main`.

---

## §O2.3 — Ceremony steps (frozen order)

Work on a **feature branch** / personal working tree. Steps marked Tier-3 never run inside product
one-click without separate operator authorization.

| Step | Action | Writes? | Tier |
| --- | --- | --- | --- |
| **C0** | **Prerequisites.** Confirm: existing `.overseer/config.yaml` with `vcs.regime: muse-only` (or repair entry via C1); Muse substrate usable for the tree; `muse` on PATH for later live bridge; `gh` optional until PR open. A muse-only tree **may lack** a configured Git remote URL even when config names `vcs.git.remote` — creating the empty GitHub repo and `git remote add` is **product/operator** work (not kit network invent) and must be done before C7 (enforced by G8 at C5). | No | — |
| **C1** | **Start-state gate.** (a) If already `muse+git-mirror` **and** bridge footprint present **and** footprint check OK → **idempotent success** (exit 0, no rewrite). (b) If already `muse+git-mirror` but bridge footprint missing/mismatched (silent-edit or partial upgrade drift) → **repair path**: skip C2 only when the on-disk VCS block already satisfies §O2.4.2; otherwise run C2; always continue C3–C5 (and C6–C7 if live requested). (c) If `git-only` or missing config → **refuse** (wrong ceremony; point to greenfield `ok init` or later git→mirror freeze). (d) If `muse-only` → continue C2. | No | — |
| **C2** | **Complete config write.** Write a full `muse+git-mirror` VCS block: `canonical: muse`, required `vcs.git.remote` / `main_branch` / `mirror_branch` (default `muse-mirror`), `vcs.muse.main_branch`, and `vcs.muse.staging_remote` (name required by schema; push may be deferred operationally — do **not** invent a fake remote). **Preserve** existing `repo.*`, `docs.*`, `thresholds.*`, and `freeze_contract.*` from the pre-upgrade config unless the operator explicitly supplies replacements. **Refuse** a patch that changes only `vcs.regime` (or only the regime string + partial git fields). | Yes (config) | 1 |
| **C3** | **Footprint re-seed.** After C2 config is on disk and loads as `muse+git-mirror`, re-resolve footprint so K7 regime-conditional destinations appear: root `MUSE-BRIDGE-WORKFLOW.md` + `scripts/muse-bridge-deploy.sh` (executable). Preferred path: `ok sync` (new destinations absent from lock+disk → seed per K7.3.4). Alternate: `ok init --migrate --from-config <post-C2-config>` when migrate classification of living docs is required. Apply `--force` **only** per §O2.4. | Yes (footprint + lock) | 1 |
| **C4** | **Footprint gate.** `ok status --check-footprint` (or equivalent kit check) must report OK with both bridge destinations present in lock + on disk. | No | — |
| **C5** | **Bridge dry-run gates.** Run §O2.5 static/safety gates on the rendered deploy script and config. **No** live `muse bridge git-export` in C5. | No | — |
| **C6** | **Explicit consent for live bridge.** Product UX / operator must confirm before C7. Ceremony `--dry-run` / plan mode stops after C5 with a machine-readable report: `ready_for_live_bridge: true` only when G1–G8 all pass; if G8 fails, report footprint gates separately and set `ready_for_live_bridge: false`. | No | — |
| **C7** | **First live bridge (optional in same session).** Only via vendored `./scripts/muse-bridge-deploy.sh` (or kit-equivalent that preserves K7 S1–S13): isolated `.muse/mirror/` → push `muse-mirror` only → open/update PR to `main` when `gh` available. | Mirror checkout + remote `muse-mirror` | 1 for branch push |
| **C8** | **Merge `muse-mirror` → `main`.** | Remote `main` | **Tier 3 — stop** |

**Invariant:** never `muse bridge git-export --git-dir .` (or any path equal to the development
checkout). Never `git push <remote> <main_branch>`.

---

## §O2.4 — Config + migrate / force interaction (frozen)

### §O2.4.1 — Silent edit (forbidden)

| Forbidden action | Why |
| --- | --- |
| Edit only `vcs.regime: muse+git-mirror` in place | Leaves muse-only footprint (no bridge files); exact KH3/K7 drift class O0 §O0.3.3 forbids |
| Flip regime without `mirror_branch` / required muse+git fields | Invalid or half-mirror config; fail-closed load or unsafe publish |
| Product claims Stage 3 complete after config edit alone | Ceremony incomplete without C3–C5 |

### §O2.4.2 — Required post-upgrade VCS shape (minimum)

Names/booleans only (no secrets):

```yaml
vcs:
  regime: muse+git-mirror
  canonical: muse
  git:
    remote: origin          # or existing remote name preserved from pre-upgrade when present
    main_branch: main       # preserve existing main_branch name when present
    mirror_branch: muse-mirror
    feature_branch_pattern: "feat/{slug}"  # preserve when present
  muse:
    staging_remote: staging # required name; operational push may defer (K7 precedent)
    main_branch: main       # preserve existing muse main_branch when present
    working_dir: null       # preserve existing working_dir when set
```

**Living-doc paths:** preserve pre-upgrade `docs.*` values. Do **not** replace a working
muse-only doc layout with greenfield `default_config_dict("muse+git-mirror")` filenames (those
defaults point at different templates than many muse-only trees).

### §O2.4.3 — Footprint re-seed composition

| Case | Required behavior |
| --- | --- |
| Post-C2 `resolve_footprint` | Includes bridge workflow + deploy script (K7.3.1) |
| Bridge destinations absent from lock **and** disk | `ok sync` (or migrate) **seeds** both; lock `origin: kit` |
| Bridge destinations absent from lock, **present** on disk with differing bytes | Shared-asset **conflict** → refuse exit `4` without `--force` (preserve hand-tuned consumer scripts) |
| Identical bytes already on disk | `unchanged`; ensure lock entries exist |
| Living docs (handover/roadmap/coordination) | Prefer `--migrate` semantics: preserve bytes; `origin: preserved`; never promote with `--force --include-preserved` on the **product Stage 3** path (pilot-forbidden) |
| `ok init` without `--migrate` on an existing governed tree | **Refuse** for Stage 3 (would fight existing living docs / config rules) unless the tree is truly greenfield — Stage 3 assumes prior muse-only install |

### §O2.4.4 — `--force` rules (frozen)

| Context | `--force` allowed? | Rule |
| --- | --- | --- |
| Shared-asset conflict on bridge workflow/script (C3) | Yes, with **explicit** operator/product consent | Overwrite kit-owned bridge assets only after conflict report shown |
| Living-doc conflict | **No** on product Stage 3 path | Keep preserve; do not `--include-preserved` |
| Overwriting entire config via `init --force` | Allowed **only** when the written config equals the §O2.4.2 complete matrix **and** preserves `docs.*` / `repo.*` as required | Still must run C3–C5; force alone is not ceremony completion |
| Silent force in product one-click without surfacing conflicts | **Forbidden** | Fail-closed; show conflicts |

---

## §O2.5 — Bridge dry-run gates (frozen)

C5 must prove the following **without** live export. Gates compose K7 §K7.3.3 invariants.

| Gate ID | Check | Fail closed |
| --- | --- | --- |
| **G1** | Config loads; `vcs.regime == muse+git-mirror`; `canonical == muse`; `mirror_branch` set | Exit non-zero; no C7 |
| **G2** | Footprint lock lists both bridge destinations; on-disk files exist; script mode executable | Same |
| **G3** | Rendered deploy script contains S3 refusal (mirror dir ≠ repo root) and never instructs `--git-dir .` as the export target | Same |
| **G4** | Script never pushes `main_branch` on `git.remote` (S8); publish path is `mirror_branch` only (S13) | Same |
| **G5** | Script uses cwd-safe `muse -C` + absolute `--git-dir` mirror path (S7) | Same |
| **G6** | No secret-assignment patterns / absolute operator home paths in rendered script (S11) | Same |
| **G7** | Plan/dry-run ceremony report states: next live step is deploy script → `muse-mirror` PR; merge remains Tier 3 | Informational required in report |
| **G8** | Local read-only check: `git remote get-url` (or equivalent) for `vcs.git.remote` returns a non-empty URL — **no** network fetch required | Block C7; dry-run C5 may still report "ready for footprint" but must mark **not ready for live bridge** until G8 passes |

**Live C7** may proceed only after G1–G8 pass **and** C6 consent. C7 failure must not leave config
rolled back automatically in O3 unless the Auto freeze-review of implementation adds an explicit
transaction story — **default frozen rule:** config+footprint from C2–C4 may remain (tree is valid
`muse+git-mirror`); live bridge can be retried. Do not half-revert to muse-only without a separate
documented downgrade freeze (out of scope).

---

## §O2.6 — Product UX unlock criteria (frozen)

Products (Scooling, Knowtation, others) may ship Stage 3 **one-click / wizard wrap** only when
**all** of the following are true:

1. This O2 artifact is freeze-reviewed → **`pass`** with non-empty `review_stamp`.
2. **Track O / O3** Auto is build-verified → **`pass`** against this freeze (seven tiers green).
3. The product wraps **only** `ok upgrade-regime` (flags per §O2.7) — it does **not** invent a
   parallel path that edits `vcs.regime` alone or skips G1–G8.
4. Product one-click includes C6 explicit consent before any live bridge (C7).
5. Product one-click **never** auto-performs C8 (merge to `main`).
6. Product still obeys O0 rejection table (no MuseHub-only baseline; no push-to-main shortcut).

Until (1)–(2) hold, products may only **describe** Stage 3 as coming soon / operator-assisted
(O0 §O0.3.3 / O1 contract).

**Operator today (unchanged):** may follow K6/K7-style runbooks with explicit consent on a feature
branch — that is operator dogfood, not product unlock.

---

## §O2.7 — O3 Auto deliverables (frozen)

After this freeze is stamped `pass`, **Track O / O3** may ship **only**:

1. **Kit ceremony orchestrator (required):** thin CLI subcommand
   **`ok upgrade-regime`** with frozen flags:
   - `--from muse-only --to muse+git-mirror` (only supported pair in O3; other pairs refuse)
   - `--dry-run` (default for product wrappers until explicit live) runs C0–C5 + G1–G8 report; no
     live export
   - `--apply` performs C2–C4 writes (and C5 gates); still no C7 unless `--live-bridge` is also set
   - `--live-bridge` requires prior/apply success + C6 consent channel (`-y` / `--yes` only after
     gates pass; refuse `--yes` alone without gate success)
   - `--force` only for §O2.4.4 shared-asset bridge conflicts (never implies `--include-preserved`)
   Orchestrator **composes** existing `init`/`sync`/`status` + K7 script invariants — **not** an
   adapter rewrite and **not** a fourth regime. A docs-only composition checklist **without** this
   subcommand is **insufficient** for O3 (silent partial upgrade risk).
2. **Docs:** kit-side ceremony runbook at
   `docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md` + update
   `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md` Stage 3 section to replace "deferred to
   Thinking O2" / "deferred to O2" shipping language with a pointer to this freeze +
   `ok upgrade-regime`, and retarget the Track O docs harness keywords in the same Auto change
   (keep one-click blocked until §O2.6; no redesign of Stages 1/2/4). Do **not** retarget the
   product contract in O2 Thinking alone — O1 §O0.8 harness still requires deferred markers until
   O3 updates validators + contract together.
3. **Fixtures** for muse-only → post-ceremony muse+git-mirror and incomplete-upgrade repair
   (tmp trees only; no live consumer).
4. **Seven-tier tests** per §O2.9.
5. **ROADMAP + HANDOVER** sync; O3 marked DONE only after `/build-verification-review` → `pass`.

**O3 must not ship:** signup UI, account APIs, live Scooling/Knowtation `ok init`, auto-merge to
`main`, or `git-only` → `muse+git-mirror` productization.

---

## §O2.8 — Rejection table (frozen)

| Proposal | Verdict |
| --- | --- |
| Silent `vcs.regime` edit without C2–C5 | **Reject** |
| Product Stage 3 one-click before O3 BV `pass` | **Reject** (§O2.6) |
| One-click auto-merges `muse-mirror` → `main` | **Reject** (Tier 3 / SD-14) |
| `muse bridge git-export --git-dir .` | **Reject** (SD-14) |
| New fourth regime string for "backup mode" | **Reject** |
| Adapter rewrite to dual-write outside existing interface | **Reject** |
| `--force --include-preserved` on product Stage 3 path | **Reject** |
| Replace muse-only `docs.*` paths with greenfield muse+git defaults silently | **Reject** |
| O2/O3 live consumer `ok init` without operator consent | **Reject** |
| O2 Thinking session implements ceremony code | **Reject** (this phase) |
| Treat K7 kit self-dogfood as Stage 3 product unlock | **Reject** |
| Productize `git-only` → `muse+git-mirror` under Stage 3 | **Reject** (separate freeze) |
| O3 ships docs-only checklist without `ok upgrade-regime` | **Reject** (§O2.7) |
| `--live-bridge` without G1–G8 pass / without C6 consent | **Reject** |

---

## §O2.9 — Seven-tier test matrix (O3 Auto must satisfy)

Skipping a tier is **forbidden**. Tests use tmp fixtures / injected runners only — no live Muse
export against real consumer working trees in Auto-green.

| Tier | Proves |
| --- | --- |
| **unit** | Ceremony classifiers: start-state muse-only vs complete-upgrade vs incomplete-upgrade repair vs wrong-regime; silent regime-only patch detector; required VCS field set for §O2.4.2; G3–G6 + G8 helpers on fixture script/remote bytes; docs.* preservation helper; argparse for `ok upgrade-regime` frozen flags. |
| **integration** | Fixture muse-only tree → `--apply` C2–C4 → footprint includes bridge files + lock entries; regime-only config mutation refused; shared-asset conflict without `--force` → exit `4`; with consented `--force` on bridge script only → OK; living-doc preserve under migrate path; idempotent re-run on complete upgrade → exit 0; incomplete muse+git-mirror without bridge files enters repair C3–C5; G8 fail marks not-ready-for-live. |
| **e2e** | Full `--dry-run` ceremony on tmp tree through C5/G1–G8 report; `--live-bridge` **not** invoked in default e2e; product-contract Stage 3 text after O3 update points at O2 + `ok upgrade-regime` (no "deferred to O2" / "coming soon" shipping claim); `git-only` fixture refused; runbook path `docs/TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md` resolves. |
| **stress** | Ceremony dry-run repeated N≥20 on large fixture footprint without hang; bounded runtime asserted. |
| **data-integrity** | Dry-run leaves tree unchanged; failed C3 conflict leaves pre-conflict bytes; successful C2–C4 twice → stable lock digest; no partial lock advance on induced mid-write failure. |
| **performance** | Single dry-run C0–C5 on fixture completes within bounded time documented in the test; no unbounded filesystem walk outside repo root. |
| **security** | No secrets in ceremony outputs/logs; path-escape outside repo → fail-closed; G3/G4 refuse `--git-dir .` and push-main; no network calls required for C0–C5 unit/integration paths; K7 MuseHub-optional baseline unchanged for `git-only` fixtures. |

---

## §O2.10 — Hard stops + tier linkage (frozen)

| Action | Tier | O2/O3 rule |
| --- | --- | --- |
| Feature-branch commits for this freeze / O3 ceremony | Tier 1 | Allowed |
| `git push` feature branch / open PR | Tier 1 / SD-17 | Allowed |
| Merge to `main` | Tier 3 | **Stop** — never part of freeze or one-click |
| Live consumer `ok init` | Operator-gated | **Stop** in O2/O3 Auto-green |
| `muse push` staging / live gate flip | Tier 3 | **Stop** |
| C7 push `muse-mirror` | Tier 1 | Allowed after C5+C6 |
| C8 merge PR | Tier 3 | **Stop** |
| New ceremony flags / persistence beyond §O2.7 | Tier 2 | Confirm once + ADR if O3 expands past frozen orchestrator |
| Shipping `ok upgrade-regime` exactly as §O2.7 | Tier 1 | Allowed in O3 Auto against this freeze |

This freeze does **not** itself authorize Tier-3 actions. Consuming it for merge/staging/live still
requires separate operator authorization (SPEC §6.4).

---

## §O2.11 — Definition of Done (Thinking) + close-out

**O2 Thinking DoD:**

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [x] `frozen: true` + non-empty `review_stamp` filled by the CLI
- [x] ROADMAP Track O / O2 → **DONE (Thinking)**; Track O / O3 Auto row queued against this contract
- [x] Handover NEXT flips to O3 with valid `Model: Auto` + paste-ready fence (KH1 H7/H8)
- [x] No ceremony implementation code landed in the Thinking phase
- [x] No Tier-3 merge performed as part of freeze

**Close-out sequence (execute only when O2 freeze marked DONE):**

1. Freeze-review `pass` recorded; stamp written by `ok review --freeze`.
2. ROADMAP: Track O / O2 → DONE; add **Track O / O3** (Auto, TODO) ceremony build.
3. Exploration backlog Track O row: note O2 freeze DONE; O3 Auto queued.
4. Handover NEXT → Track O / O3 Auto with paste-ready prompt.
5. Governance sync: `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together (SD-17).

---

## Cross-references

- `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md` — §O0.3.3 deferral closed by this freeze
- `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md` — Stage 3 remains blocked until §O2.6
- `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` — footprint membership + S1–S13 + K7.3.4
- `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md` — operator dogfood (not product unlock)
- `docs/PHASE-K4-VENDORING-CLI-CONTRACT.md` — `init`/`sync`/`--force` refuse semantics
- `docs/OVERSEER-KIT-SPEC.md` §4–§6
- `AGENTS.md` — SD-14
- `docs/ROADMAP.md` — Track O rows
- `policy/test-tiers.yaml` / `policy/tiers.yaml`
