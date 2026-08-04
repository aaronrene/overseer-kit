# Phase K7 — Dogfood muse+git-mirror (Frozen Thinking Outline, K7a)

Status: **Frozen dogfood design + footprint contract + parity gate + K7b seven-tier matrix.
No Build in this step. No live `muse bridge git-export` on the overseer-kit development tree.
No `git push origin main`. No staging push without Tier-3 authorization. No retirement of
`git-only` as a first-class baseline.** This document is the machine-checkable ground truth
K7b implements mechanically against; it refines — and stays compatible with —
`docs/OVERSEER-KIT-SPEC.md` §4 / §8, the regime capability tiers in `docs/ROADMAP.md`,
`AGENTS.md` (planned → active flip notes), and the K4 footprint membership contract
(`docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` §K4.5). Live K6 consumer pilots remain separate
operator work (`docs/archive/phases/PHASE-K6-PILOT-INSTALL-MATRIX.md`, `docs/MIGRATE-EXISTING-REPO.md`).

## Freeze-contract declaration (§6.1 schema)

```yaml
phase: K7a
outputs:
  - id: k7-muse-git-mirror-dogfood
    path: docs/archive/phases/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
    frozen: true                     # K7b treats this as ground truth without re-deriving
frozen_inputs:
  - id: kit-spec-vcs-adapters
    path: docs/OVERSEER-KIT-SPEC.md#4
  - id: kit-spec-migration-path
    path: docs/OVERSEER-KIT-SPEC.md#8
  - id: kit-regime-capability-tiers
    path: docs/ROADMAP.md#regime-capability-tiers
  - id: kit-vendoring-cli-contract
    path: docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md
  - id: kit-agents-regime-notes
    path: AGENTS.md
  - id: kit-test-tiers
    path: policy/test-tiers.yaml
```

**Downstream edge:** K7b (Auto) → consumes `k7-muse-git-mirror-dogfood` as ground truth. Per §6,
this is a **mandatory reviewed freeze** before K7b builds. Human escalation is required only if a
finding hits `security | irreversible | real_money | gates_tier3`.

**Review record (§6.2):**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking) | `findings` (2 MAJOR + 3 MINOR) | **M1** S7↔S9 mirror publish underspecified; **M2** default-`sync` new-destination cases underspecified; **N1** §K7.1 Auto scope vs footprint-first; **N2** deploy-script `muse -C`; **N3** bash token quoting. Not cleared for K7b. |
| 1-fix (2026-07-11) | Author fix revision (M1 + M2 + N1–N3) | — | **M1:** S7 cwd-safe `muse -C` + S13 publish `mirror_branch` only (no `--no-push` without that push; never `main`). **M2:** §K7.3.4 default-`sync` new-destination seed/conflict rows + integration cases. **N1:** §K7.1 config/`AGENTS.md` flip → operator slice. **N2:** folded into S7. **N3:** S11/S12 require double-quoted token expansions. Awaiting **K7a-r2**. |
| 2 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from round 1; file+line citations | **`pass`** | Round-1 **M1 + M2 + N1–N3 confirmed RESOLVED**. Full regress §K7.0–§K7.10 vs SPEC §4/§8, ROADMAP regime tiers, PHASE-K4 §K4.5, AGENTS.md: no new contradictions; no K7b leak. **Cleared for K7b.** No human escalation. |

### Freeze-review findings ledger (K7a-r1)

| ID | Severity | Status | Where resolved |
| --- | --- | --- | --- |
| M1 | MAJOR | **RESOLVED** (r2 confirmed) | §K7.3.3 S7 + **S13**; P10; unit/security matrix |
| M2 | MAJOR | **RESOLVED** (r2 confirmed) | §K7.3.4 default-`sync` new-destination rows; §K7.8 integration |
| N1 | MINOR | **RESOLVED** (r2 confirmed) | §K7.1 scope table (config/`AGENTS.md` → operator) |
| N2 | MINOR | **RESOLVED** (r2 confirmed) | §K7.3.3 S7 `muse -C` |
| N3 | MINOR | **RESOLVED** (r2 confirmed) | §K7.3.3 S11/S12 quoted expansions; §K7.9 |

---

## Simple summary (no jargon)

The kit already *supports* Muse-as-canonical with a GitHub mirror, but this repo still runs on
plain GitHub. K7 freezes **how we flip this kit repo itself** to that Muse+mirror setup, **what
extra files the installer ships** for that setup (a bridge workflow doc + a safe deploy script),
**what “good enough” looks like before we claim the flip worked**, and **how we prove GitHub-only
users still get every core feature**. No live Muse export on the working tree in this outline.

## Technical summary

K7a freezes: (1) ordered dogfood steps for flipping overseer-kit from `git-only` to
`muse+git-mirror`; (2) additive, **regime-conditional** footprint membership —
`templates/MUSE-BRIDGE-WORKFLOW.template.md` → root `MUSE-BRIDGE-WORKFLOW.md` and a tokenized
`muse-bridge-deploy.sh` → `scripts/muse-bridge-deploy.sh`, vendored **only** when
`vcs.regime == muse+git-mirror`; (3) a kit self-install **parity gate** (K7.P1–K7.P10) plus
operator-gated live bridge evidence; (4) the explicit **no MuseHub-only core capability**
guardrail with concrete K7b checks; (5) the K7b seven-tier test matrix. Deploy-script contract
is **S1–S13** (cwd-safe `muse -C`, quoted tokens, publish `mirror_branch` only). Live Muse init,
first bridge export, and staging push remain **operator-gated** after green fixture tests — never
part of Auto Build’s definition of green. Auto is **footprint-first**: kit stays `git-only` until
operator L1.

**Recommendation:** after K7a-r2 → `pass`, run K7b Auto for footprint + resolver +
tests + runbook on a feature branch (config stays `git-only`); keep the first live Muse bind /
bridge of overseer-kit as a separate operator session against the parity checklist.

---

## §K7.0 — Hard stops (frozen)

| Hard stop | Rationale |
| --- | --- |
| No Build / no code changes in K7a | Thinking freeze only |
| **Never** `muse bridge git-export --git-dir .` on the overseer-kit (or any) **dev tree** | Destructive delete-and-replace; deletes ignored files (`.env.local`, etc.) — SD-14 / AGENTS.md |
| Bridge target is always isolated `.muse/mirror/` (or config-equivalent under that rule) | Same failure mode as Knowtation/Scooling |
| No `git push origin main` | SD-14; mirror via `muse-mirror` PR only |
| No staging push / main merge / live gate flip without Tier-3 operator authorization | Spec §9; kit never automates Tier 3 |
| No claim that K6 live consumer pilots are PASS | Separate operator runbook |
| No core governance capability becomes MuseHub-only | Regime capability tiers (ROADMAP); §K7.5 |
| K7b fixture tests must not invoke live Muse against the real overseer-kit working tree | Injected runners / tmp fixtures only |

---

## §K7.1 — Scope split (K7a vs K7b vs operator)

| Slice | Owner | In scope | Out of scope |
| --- | --- | --- | --- |
| **K7a** (this doc) | Thinking | Freeze WHAT/HOW; update ROADMAP + handover | Any Build; any live Muse command on this tree |
| **K7b** (Auto) | Auto against this freeze | Footprint templates + regime-conditional resolver; token registry if needed; seven-tier tests on fixtures; operator runbook for kit self-flip (`docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md`). **Footprint-first:** do **not** flip overseer-kit `.overseer/config.yaml` or `AGENTS.md` off `git-only` / “planned” in this Auto slice (§K7.7) | Live Muse bind; live bridge export; staging push; merging `muse-mirror` → `main`; kit config/`AGENTS.md` regime flip |
| **Operator live dogfood** | Human after K7b green + freeze-review `pass` | Muse init/bind (D2); config flip to §K7.2.3 + `AGENTS.md` active-regime language (D3–D4); first safe bridge via vendored script (L1); PR merge Tier-3 (L2) | Redesign of adapter interface |

K6 live pilots (Scooling → Knowtation → MuseHub → VideoFactory) stay on
`docs/MIGRATE-EXISTING-REPO.md`. K7 does **not** re-run those inits. When K7b lands bridge
assets, later consumer `sync` may pick them up under K4/K6 sync rules (§K7.3.4).

---

## §K7.2 — Dogfood steps (frozen order)

Operator sequence for flipping **this** repo (`overseer-kit`) after K7b ships the footprint assets.
Each step is Tier-1 feature-branch work unless marked Tier-3.

### K7.2.1 — Prerequisites (operator)

| # | Prerequisite | Evidence |
| --- | --- | --- |
| 1 | `muse` CLI on `PATH` | `muse --version` |
| 2 | `gh` authenticated | `gh auth status` |
| 3 | Git remote `origin` → GitHub overseer-kit | `git remote -v` |
| 4 | Muse staging remote provisioned for this repo (or explicit operator decision to defer staging push while local Muse works) | `.muse/config.toml` / Muse hub repo exists |
| 5 | Permanent GitHub branch `muse-mirror` exists **or** may be created by the first safe bridge | `gh api` / remote branch list — **not** by exporting onto `.` |
| 6 | K7b merged (or available on the feature branch under test): bridge template + deploy script in kit sources; resolver regime gate live | `status --check-footprint` after config flip |

### K7.2.2 — Ordered flip steps

| Step | Action | Writes? | Tier |
| --- | --- | --- | --- |
| D1 | Confirm clean git working tree; **do not** run any `muse bridge git-export` yet | No | — |
| D2 | Initialize / bind Muse for overseer-kit (operator Muse setup; cwd-safe `muse -C <abs-root>`) | Muse metadata under `.muse/` (local) | 1 / local |
| D3 | Flip `.overseer/config.yaml` to the frozen self-install matrix (§K7.2.3) | Yes (config) | 1 |
| D4 | Update `AGENTS.md`: regime **active** `muse+git-mirror`; keep SD-14 rules; remove “planned / not yet active” language | Yes | 1 |
| D5 | `overseer sync` (or `init --migrate` if treating as migrate) so regime-conditional footprint adds `MUSE-BRIDGE-WORKFLOW.md` + `scripts/muse-bridge-deploy.sh` | Yes (footprint) | 1 |
| D6 | Run parity gate K7.P1–K7.P10 (§K7.4) on fixtures + read-only adapter probes | Read / dry-run | — |
| D7 | **First live bridge** only via `./scripts/muse-bridge-deploy.sh "mirror: …"` → isolated `.muse/mirror/` → push `muse-mirror` → open/update PR to `main` | Mirror checkout + remote `muse-mirror` | 1 for branch push; **Tier-3** for merge to `main` |
| D8 | After merge: day-to-day = `muse commit` on feature branches; never `git push origin main`; mirror only via deploy script | Muse + mirror PR | 1 / 3 |

### K7.2.3 — Overseer-kit self-install config matrix (frozen)

Target `.overseer/config.yaml` after the flip (names/booleans only; no secrets):

```yaml
overseer_config_version: 1

repo:
  name: overseer-kit
  root_relative_docs: docs

vcs:
  regime: muse+git-mirror
  canonical: muse
  git:
    remote: origin
    main_branch: main
    mirror_branch: muse-mirror
    feature_branch_pattern: "feat/{slug}"
  muse:
    staging_remote: staging
    main_branch: main
    working_dir: null          # install root == Muse root

docs:
  handover: OVERSEER-HANDOVER.md
  roadmap: ROADMAP.md
  coordination: null           # kit keeps SD/ADR pointers in ROADMAP today; no CROSS-REPO doc
  standing_decisions: ROADMAP.md

thresholds:
  realign_max_commits: 50
  drift_warn_only: true

freeze_contract:
  enabled: true
  reviewer: agent
  human_escalation:
    - security
    - irreversible
    - real_money
    - gates_tier3
```

**Frozen notes:**

- `docs.coordination: null` is intentional for overseer-kit (matches current dogfood; coordination
  template stays skipped per §K4.5).
- `working_dir: null` — Muse root is the install root (unlike MuseHub’s nested `working_dir`).
- `staging_remote: staging` satisfies regime validation; if staging is not yet operational, the
  operator may skip `muse push staging` (Scooling precedent) but **must not** invent a fake remote
  in config — config names the intended remote; push deferral is operational, not a schema lie.

### K7.2.4 — Day-to-day rules after flip (frozen; mirrors AGENTS.md / SD-14)

1. Canonical history = MuseHub; GitHub `main` is the mirror merge target only.
2. Feature work: `muse commit` on a feature branch; never commit governance via unprotected
   `git push origin main`.
3. Publish to GitHub: `./scripts/muse-bridge-deploy.sh "mirror: <summary>"` only.
4. Permanent branch `muse-mirror`; do not delete; do not hand-edit as a substitute for Muse.
5. **Never** `muse bridge git-export --git-dir .` (or any path equal to the development checkout).

---

## §K7.3 — Footprint additions (frozen)

### K7.3.1 — Additive membership (regime-conditional)

Extends §K4.5. New rows apply **if and only if** `config.vcs.regime == "muse+git-mirror"`.
For `git-only` and `muse-only`, these sources are **not** resolved, **not** written, and **not**
entered in `version.lock`.

| Kit source | Consumer destination | Rendering | Regime |
| --- | --- | --- | --- |
| `templates/MUSE-BRIDGE-WORKFLOW.template.md` | `MUSE-BRIDGE-WORKFLOW.md` (repo **root**, not under `docs/`) | token-substituted | `muse+git-mirror` only |
| `templates/scripts/muse-bridge-deploy.sh.template` | `scripts/muse-bridge-deploy.sh` | token-substituted; file mode **executable** (`0755`) on write | `muse+git-mirror` only |

**Destination uniqueness:** both paths are fixed and must not collide with any other footprint
destination. Root `MUSE-BRIDGE-WORKFLOW.md` matches Scooling/Knowtation convention.

**Not living docs:** these paths are **not** members of `living_doc_destinations` (handover /
roadmap / coordination). They follow ordinary shared-asset sync classification (K4/K6), not
`origin: preserved` living-doc rules.

### K7.3.2 — Template content contract (WHAT must appear)

`MUSE-BRIDGE-WORKFLOW.template.md` MUST encode, after token substitution:

| Clause | Required content |
| --- | --- |
| Plain + technical summary | Muse canonical; GitHub via isolated mirror checkout |
| Flow diagram | Muse `{{vcs.muse.main_branch}}` → deploy script → `.muse/mirror/` → `{{vcs.git.remote}}/{{vcs.git.mirror_branch}}` → PR → `{{vcs.git.main_branch}}` |
| Hard rule | Never `muse bridge git-export --git-dir .` |
| Hard rule | Never `git push {{vcs.git.remote}} {{vcs.git.main_branch}}` |
| Hard rule | `{{vcs.git.mirror_branch}}` is permanent |
| Day-to-day | Feature work in Muse; bridge from Muse main after merge |
| Pointer | Run `./scripts/muse-bridge-deploy.sh` |

Tokens used MUST be members of `ALLOWED_TOKENS` / `templates/tokens.yaml`. Prefer existing keys:
`repo.name`, `vcs.regime`, `vcs.git.remote`, `vcs.git.main_branch`, `vcs.git.mirror_branch`,
`vcs.muse.main_branch`, `vcs.muse.staging_remote`. **No new token keys** unless a freeze-review
finding proves an existing key cannot express a required clause — then add to `ALLOWED_TOKENS` +
`tokens.yaml` + `build_token_map` together (single additive change).

### K7.3.3 — Deploy script contract (tokenized safety invariants)

`templates/scripts/muse-bridge-deploy.sh.template` MUST implement, after substitution:

| Invariant | Behavior |
| --- | --- |
| S1 | `set -euo pipefail` |
| S2 | Resolve `REPO_ROOT`; default `MIRROR_DIR=.muse/mirror` (overridable via env, e.g. `MUSE_BRIDGE_MIRROR_DIR`) |
| S3 | **Refuse** if resolved mirror dir equals `REPO_ROOT` (blocks `--git-dir .`) |
| S4 | Provision / update isolated git checkout at mirror dir on `{{vcs.git.mirror_branch}}` from `{{vcs.git.remote}}` |
| S5 | Before export: create non-secret sentinel(s) under `REPO_ROOT`; after export: fail if sentinel missing |
| S6 | If `.env` / `.env.local` existed pre-export, fail if either disappeared |
| S7 | Invoke Muse **cwd-safe**: `muse -C <absolute Muse root>` (install root when `vcs.muse.working_dir` is null; else install root / working_dir) then `bridge git-export` with `--git-dir` = **absolute mirror path only**; `--git-branch {{vcs.git.mirror_branch}}`; `--git-remote {{vcs.git.remote}}` (or equivalent); `--exclude` at least `.muse/*`, `.env`, `.env.local`. Must **not** pass `--no-push` unless S13 is satisfied by a later explicit push of **only** `{{vcs.git.mirror_branch}}`. |
| S8 | Never push `{{vcs.git.main_branch}}` on `{{vcs.git.remote}}` |
| S9 | After S13 succeeds: open or update GitHub PR `{{vcs.git.mirror_branch}}` → `{{vcs.git.main_branch}}` via `gh` when available; warn + exit 0 if `gh` missing |
| S10 | Stack audit is **optional**: if no `package.json`, skip pnpm audit (overseer-kit is Python). Do not hard-require Node. |
| S11 | No secrets, tokens, absolute operator home paths, or hardcoded SHAs in the template. Every substituted `{{…}}` token that expands into a shell word **MUST** appear inside double quotes (or an equivalent safe expansion) so config values cannot break out of the script. |
| S12 | Shebang `#!/usr/bin/env bash`; substituted output remains valid bash; S11 quoting preserved after substitution |
| S13 | **Publish mirror branch:** after a successful export, `{{vcs.git.mirror_branch}}` **must** exist on `{{vcs.git.remote}}` — either because `muse bridge git-export` pushed it (default Muse behavior when `--git-remote` is set and `--no-push` is absent) **or** via an explicit `git -C <mirror> push {{vcs.git.remote}} {{vcs.git.mirror_branch}}` (or equivalent). Never push `{{vcs.git.main_branch}}`. Local-only export without this publish step is a contract failure. |

**Product-specific Scooling/Knowtation extras** (Netlify, Knowtation `config/local.yaml` /
`data/` sentinels, forced `pnpm audit` fail) are **not** required in the kit baseline. Consumers
may hand-extend after vendoring; kit `sync` treats divergent scripts as shared-asset conflicts
unless `--force`.

### K7.3.4 — Resolver + migrate/sync composition

| Case | Behavior |
| --- | --- |
| `resolve_footprint` + `muse+git-mirror` | Include both new files (sorted with existing destinations) |
| `resolve_footprint` + `git-only` \| `muse-only` | Omit both; digest/lock unchanged vs pre-K7 for those regimes aside from unrelated kit changes |
| Greenfield `init` muse+git-mirror | Write both; lock `origin: kit` |
| `init --migrate` where root workflow / script already exist and bytes differ | Standard shared-asset **conflict** → refuse without `--force` (preserves Scooling/Knowtation hand-tuned scripts) |
| `init --migrate` identical bytes | `unchanged`; lock `origin: kit` |
| Default `sync` (paths already in lock) | Update when kit template changed and on-disk matches last lock baseline; refuse consumer edits without `--force` (shared-asset / K4.3 / K6 rules) |
| Default `sync` — **new** destination not in lock, **absent** on disk | Classify `missing` → **restore/seed** write; lock `origin: kit` (overseer-kit dogfood D5 path) |
| Default `sync` — **new** destination not in lock, **present** on disk | Classify `both-changed` (no baseline) → shared-asset **conflict** refuse exit `4` without `--force` (preserves existing Scooling/Knowtation bridge files) |
| Overseer-kit dogfood (files absent today) | First sync/init after regime flip **seeds** both files via the new-destination-absent rule above |

### K7.3.5 — `templates/tokens.yaml` registry

Add the new template paths under `templates:`:

- `MUSE-BRIDGE-WORKFLOW.template.md`
- `scripts/muse-bridge-deploy.sh.template` (path relative to `templates/`)

No change to the living-doc token set unless §K7.3.2 forces an additive token (reviewer-gated).

---

## §K7.4 — Parity gate (kit self-install)

Parity is **proven before** claiming overseer-kit dogfood DONE. Fixture-automated checks (K7b
tests) cover P1–P3 (static/config/footprint) and P9–P10 always; P4–P8 use injected runners on
tmp fixtures. Live P4–P8 against the real tree are **operator evidence** recorded in the handover
change log — not required for K7b Auto to merge footprint code.

### K7.4.1 — Universal kit parity (K7.P1–K7.P10)

| ID | Criterion | Evidence |
| --- | --- | --- |
| **K7.P1** | Config matches §K7.2.3 regime matrix (`muse+git-mirror`, `canonical: muse`, required muse/git fields, `mirror_branch: muse-mirror`) | Load `.overseer/config.yaml`; `SUPPORTED_REGIMES` validate |
| **K7.P2** | Footprint includes root `MUSE-BRIDGE-WORKFLOW.md` + `scripts/muse-bridge-deploy.sh`; `status --check-footprint` OK for kit-only digest | Lock manifest + check |
| **K7.P3** | `AGENTS.md` states **active** `muse+git-mirror` + SD-14 (no “planned / not yet active”) | File content |
| **K7.P4** | `adapter.status()` succeeds; notes include canonical=muse and SD-14 reminder | Injected or live status |
| **K7.P5** | `read_canonical_anchor()` succeeds (`.muse/git-bridge.toml` and/or `origin/muse-mirror`) | Adapter result |
| **K7.P6** | `realign(dry_run=true)` reachable; does not apply; respects `realign_max_commits` | Adapter result `applied: false` |
| **K7.P7** | `mirror(dry_run=true)` returns diff summary; `mirror(dry_run=false)` does **not** push (`operator-authorization-required` or equivalent) | Adapter result `pushed: false` |
| **K7.P8** | `governance-sync --dry-run` exit `0`; zero additional writes | Tree unchanged across invocation |
| **K7.P9** | **Guardrail:** `git-only` fixture still gets full `init` / `sync` / `status` / `review --freeze` / `governance-sync --dry-run` with **no** Muse invocation and **without** bridge footprint files | Seven-tier + least-privilege tests |
| **K7.P10** | Deploy script (rendered) contains S3 refuse-root, S5 sentinel, S7 isolated `--git-dir` + `muse -C`, S8 no push main, S11/S12 quoted token expansions, S13 publish-`mirror_branch` (no local-only `--no-push` without later mirror push) | Static unit assertions on rendered bytes — **no live export** |

### K7.4.2 — Operator live evidence (not Auto-green)

| ID | Criterion | Notes |
| --- | --- | --- |
| **K7.L1** | First successful `./scripts/muse-bridge-deploy.sh` against overseer-kit using `.muse/mirror/` only | After K7b; Tier-1 remote `muse-mirror` |
| **K7.L2** | PR `muse-mirror` → `main` opened; merge only under Tier-3 | Never force-push `main` |

K7b marks **code DONE** when seven-tier tests green and governance docs updated. Kit dogfood
**operational DONE** additionally requires K7.L1 (and K7.L2 when publishing). Handover must not
conflate the two.

---

## §K7.5 — Guardrail: no MuseHub-only core capability (frozen)

Restates and operationalizes the ROADMAP regime capability tiers for K7b:

| Capability | Must work on `git-only` after K7b | Muse deepening only |
| --- | --- | --- |
| `init` / `sync` / `status` / drift / footprint digest | Yes | — |
| Governance docs + freeze review + governance-sync | Yes | — |
| `realign` | No-op (`single-history`) | Active import path |
| `mirror` | No-op | Active SD-14 path + vendored script |
| Bridge workflow + deploy script in footprint | **Absent** (not required) | Present for `muse+git-mirror` only |
| Provenance / Muse version enrichment | N/A | Optional future; not a baseline gate |

**K7b concrete checks (frozen):**

1. No new CLI flag or subcommand that errors on `git-only` solely because Muse is missing, unless
   the command is explicitly Muse-deepening (`realign` apply / `mirror` apply) and already
   documented as no-op/report on `git-only`.
2. Bridge files MUST NOT appear in `git-only` or `muse-only` footprints (P9).
3. `docs/GIT-ONLY-QUICKSTART.md` remains valid; update only to point at K7 dogfood as optional
   Muse depth — never as a requirement for kit use.
4. `muse-only` continues to report git/mirror forbidden; K7 does not weaken that least-privilege.

---

## §K7.6 — Adapter / CLI surface (compose, do not fork)

K7b **does not** redesign §4. It consumes existing `MuseGitMirrorAdapter` behavior:

| Method | K7 expectation |
| --- | --- |
| `status` | Already returns canonical=muse + SD-14 note |
| `read_canonical_anchor` | Bridge toml / mirror ref |
| `realign` | Dry-run first; `git-import --incremental`; max_commits guard |
| `mirror` | Dry-run reports; non-dry-run stops for operator authorization (script is the operator path) |
| `commit_feature` | Muse feature branches only |

CLI footprint resolver (`cli/footprint.py`) gains the regime-conditional rows in §K7.3.1.
Init/sync write path must set executable bit on `scripts/muse-bridge-deploy.sh`.

---

## §K7.7 — K7b deliverables checklist

| # | Deliverable |
| --- | --- |
| 1 | `templates/MUSE-BRIDGE-WORKFLOW.template.md` per §K7.3.2 |
| 2 | `templates/scripts/muse-bridge-deploy.sh.template` per §K7.3.3 |
| 3 | `resolve_footprint` regime gate + executable mode on script write |
| 4 | `templates/tokens.yaml` lists new templates; token fail-closed preserved |
| 5 | Fixture config(s) for muse+git-mirror assert new destinations; git-only/muse-only assert absence |
| 6 | Committed dogfood doc updates **deferred to operator**: `AGENTS.md` active-regime section + `.overseer/config.yaml` flip land only in the operator dogfood PR (D3–D4), not in K7b Auto. Auto must **not** claim Muse canonical while config remains `git-only` |
| 7 | `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md` — operator steps D1–D8 + L1–L2 (no live execution in Auto) |
| 8 | Seven-tier tests green (§K7.8) |
| 9 | ROADMAP + OVERSEER-HANDOVER updated together |

**Sequencing note (frozen):** K7b may land footprint + tests **before** the operator flips live
config. If the PR includes the config/`AGENTS.md` flip, that flip must be accompanied by operator
acknowledgment that Muse bind (D2) is done or immediately follows — otherwise land footprint first,
flip config in a follow-up operator PR. Prefer **footprint-first** in Auto so CI/fixtures stay
honest: kit repo can remain `git-only` until L1 path is ready, while still *shipping* the assets
consumers need.

**Frozen Auto default:** K7b Auto **ships assets + tests + runbook**; leaves overseer-kit
`.overseer/config.yaml` as `git-only` until operator dogfood session. `AGENTS.md` keeps “planned”
until the operator flip PR. Handover records which sub-slice landed.

---

## §K7.8 — Seven-tier test matrix (K7b)

| Tier | Focus | Required cases |
| --- | --- | --- |
| **unit** | Footprint resolver; templating; script safety strings; argparse unchanged | `muse+git-mirror` footprint includes both new destinations; `git-only` and `muse-only` omit them; token render of workflow + script uses only `ALLOWED_TOKENS`; rendered script matches S3/S5/S7 (`muse -C` + isolated `--git-dir`)/S8/S11–S13 assertions; unknown token → `ConfigError`; executable bit set on script write helper; config matrix §K7.2.3 loads |
| **integration** | init/sync/status compose | muse+git-mirror fixture `init` writes workflow + script + lock entries; git-only fixture init has neither path; `status --check-footprint` OK; sync no-op at same version; migrate conflict when pre-existing differing script without `--force`; **default `sync` seeds new bridge destinations when absent from lock+disk**; **default `sync` conflicts (exit `4`) when new bridge destinations exist on disk but not in lock, without `--force`** |
| **e2e** | Fixture dogfood cycle | tmp muse+git-mirror tree: init → status → governance-sync `--dry-run` (injected runner) → footprint check; no live Muse; second sync no-op |
| **stress** | Large rendered workflow + many policy/cursor files | Footprint resolve + digest remain bounded with bridge files present |
| **data-integrity** | Idempotency + digest | Run-twice init identical lock digest; mid-write failure does not advance lock; kit-only digest includes bridge files when regime muse+git-mirror; omitting regime excludes them |
| **performance** | `status --check-footprint` | Completes within existing pilot bound with bridge files in footprint |
| **security** | Least privilege + no leak + no live export | git-only path invokes no `muse`; muse-only still forbids git mirror push; rendered script/templates contain no secrets/absolute homes/hardcoded SHAs; every shell-expanded token in the deploy script is double-quoted (S11); tests never call live `git-export` on workspace root; path confinement for script destination under install root |

**Explicit non-tests for K7b Auto:** live Muse bind of overseer-kit; live bridge export; staging
push; GitHub `main` merge.

---

## §K7.9 — Security checklist (phase-specific)

- Fail-closed reads unchanged (§4 / §9).
- Deploy script refuses repo-root export (S3) — primary injection/destruction defense.
- Sentinels prove export did not touch the dev tree (S5/S6).
- Templates: fixed token set only; no shell interpolation of doc bodies.
- Deploy script: every substituted token in a shell word is double-quoted (S11/S12); Muse invoked via `muse -C` (S7).
- Mirror publish targets only `{{vcs.git.mirror_branch}}` (S13); never `main` (S8).
- No credentials in config, templates, lock, or test fixtures.
- Tier-3 surfaces (main merge, staging push) remain human-gated; adapter `mirror(dry_run=false)`
  does not push.

---

## §K7.10 — Out of scope (explicit)

- Redesigning VCS adapter method signatures
- Making `realign` / `mirror` available as baseline requirements on `git-only`
- Live K6 consumer inits or gate flips
- Publishing the kit as a MuseHub-only product
- Automating Tier-3 merges
- Copying Scooling product runtime or Knowtation vault paths into the kit
- Running `muse bridge git-export --git-dir .` “just to see”

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §4 (adapters), §8 (migration), §9 (security)
- `docs/ROADMAP.md` — regime capability tiers; K7a/K7b rows
- `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` §K4.5 — footprint membership composition
- `docs/archive/phases/PHASE-K6-PILOT-INSTALL-MATRIX.md` — consumer pilots (separate)
- `docs/GIT-ONLY-QUICKSTART.md` — baseline promise K7 must not break
- `AGENTS.md` — SD-14 / planned regime notes
- Scooling / Knowtation root `MUSE-BRIDGE-WORKFLOW.md` + `scripts/muse-bridge-deploy.sh` — reference
  implementations (not vendored verbatim; kit ships tokenized baseline)
