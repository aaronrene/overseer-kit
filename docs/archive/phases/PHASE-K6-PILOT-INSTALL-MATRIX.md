# Phase K6 — Pilot Install Matrix (Frozen Thinking Outline, K6a)

Status: **Frozen install matrix + parity gate for K6b (Auto Build). No live `overseer init`
against production consumer repos in this step. No gate flips. No `main` merges. No staging
pushes. No retirement of hand-maintained upkeep.** This doc is the machine-checkable ground truth
K6b implements mechanically against; it refines — and stays compatible with —
`docs/OVERSEER-KIT-SPEC.md` §8, and composes with the frozen K4 vendoring CLI
(`docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md`) and 9A-5 governance-sync
(`docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md`).

## Freeze-contract declaration (§6.1 schema)

```yaml
phase: K6a
outputs:
  - id: k6-pilot-install-matrix
    path: docs/archive/phases/PHASE-K6-PILOT-INSTALL-MATRIX.md
    frozen: true                     # K6b treats this as ground truth without re-deriving
frozen_inputs:
  - id: kit-spec-migration-path
    path: docs/OVERSEER-KIT-SPEC.md#8
  - id: kit-spec-config-schema
    path: docs/OVERSEER-KIT-SPEC.md#3
  - id: kit-spec-vcs-adapters
    path: docs/OVERSEER-KIT-SPEC.md#4
  - id: kit-vendoring-cli-contract
    path: docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md
  - id: kit-governance-hygiene-outline
    path: docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md
  - id: kit-test-tiers
    path: policy/test-tiers.yaml
```

**Downstream edge:** K6b (Auto) → consumes `k6-pilot-install-matrix` as ground truth. Per §6, this
is a **mandatory reviewed freeze** before K6b builds. Human escalation is required only if a finding
hits `security | irreversible | real_money | gates_tier3`.

**Review record (§6.2):**

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 (2026-07-10) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); file+line citations | **`blocked`** (1 BLOCKER, 5 MAJOR, 2 MINOR) | Not cleared for K6b. No human escalation. Findings B1, M1–M5, N1–N2 listed below (historical). |
| 1-fix (2026-07-11) | Author fix revision (B1 + M1–M5 + N1–N2) | — | **B1:** P7 reworded — governance-sync dry-run zero *additional* writes; migrate footprint may already exist. **M1:** all four consumers now have complete loadable YAML (`thresholds` + nested `freeze_contract`). **M2:** `--force` under `--migrate` table — living docs stay preserved unless `--force --include-preserved` (pilot-forbidden). **M3:** default sync retains `origin: preserved` lock entries verbatim. **M4:** `--check-footprint` integrity over `origin: kit` only; preserved = `preserved-living`. **M5:** KN-R2 PASS → classification `updated` without `--force`. **N1:** P5 aligned/`plan=None` ⇒ PASS; pilot expects aligned hand docs or pre-seeded anchors. **N2:** docs-root sentinel is `"."` only; empty string invalid; `working_dir` escape → `2`. Awaiting round-2 confirmation. |
| 2 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from round 1; file+line citations | **`blocked`** (1 BLOCKER, 1 MAJOR, 1 MINOR) | Round-1 **B1, M1–M3, M5, N1–N2 confirmed RESOLVED**. **M4 incomplete** → elevates to **R2-B1**. New **R2-M1**, **R2-N1**. Not cleared for K6b. No human escalation (`security \| irreversible \| real_money \| gates_tier3` not hit). |
| 2-fix (2026-07-11) | Author fix revision (R2-B1 + R2-M1 + R2-N1) | — | **R2-B1:** kit-only `footprint_digest` on migrate write + default sync rewrite (preserved stay in per-file manifest, excluded from aggregate). **R2-M1:** P5 parity PASS = rule 1 only (`aligned`/`plan=None`); matches SPEC §8; in-anchor-only plans are diagnostic FAIL until aligned. **R2-N1:** first-class `--include-preserved` option row for `init` + `sync` (+ `--only` interaction). Awaiting round-3 confirmation. |
| 3 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from rounds 1–2; file+line citations | **`blocked`** (1 BLOCKER, 1 MINOR) | Round-2 **R2-B1, R2-M1, R2-N1 confirmed RESOLVED**. Round-1 spot-check still RESOLVED. New **R3-B1** + **R3-N1**. Not cleared for K6b. No human escalation (`security \| irreversible \| real_money \| gates_tier3` not hit). |
| 3-fix (2026-07-11) | Author fix revision (R3-B1 + R3-N1) | — | **R3-B1:** `origin: preserved` sync paths are non-blocking for refusal (warn only, like K4.3 `--only` out-of-scope); `kit-updated` preserved skipped for write and never blocking; `sync --force` alone never writes/promotes preserved. **R3-N1:** explicit `sync --force` middle row + unit cases for hand-edit non-block and `--force`-alone. Awaiting round-4 confirmation. |
| 4 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from rounds 1–3; file+line citations | **`blocked`** (1 BLOCKER) | Round-3 **R3-B1, R3-N1 confirmed RESOLVED** (as scoped to `origin: preserved`). Round-1/2 spot-check still RESOLVED. New **R4-B1** (seeded / `origin: kit` living docs). Not cleared for K6b. No human escalation (`security \| irreversible \| real_money \| gates_tier3` not hit). |
| 4-fix (2026-07-11) | Author fix revision (R4-B1) | — | **R4-B1:** under `--migrate`, every living-doc destination (handover / roadmap / coordination) is locked `origin: preserved` whether classified `seed`, `unchanged`, or `preserved` — so seeded Knowtation roadmap shares digest exclusion + sync write/refusal gates with hand-preserved docs; `sync --force` alone never overwrites living docs; kit-only digest / P2 = shared assets only. Unit/data-integrity cases for seeded living-doc hand-edit. Awaiting round-5 confirmation. |
| 5 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from rounds 1–4; file+line citations | **`blocked`** (1 BLOCKER) | Round-4 **R4-B1 confirmed RESOLVED** (default migrate / seed / digest / sync-`--force`-alone / P2 / tests). Round-1/2/3 spot-check still RESOLVED. New **R5-B1** (absolute `origin: preserved` vs `--force --include-preserved` promotion). Not cleared for K6b. No human escalation (`security \| irreversible \| real_money \| gates_tier3` not hit). |
| 5-fix (2026-07-11) | Author fix revision (R5-B1) | — | **R5-B1:** scoped living-doc origin rule to **pre-promotion** migrate locks; `--force --include-preserved` on `init --migrate` and `sync` promotes present living docs to `origin: kit` (overwrite when bytes differ; ownership flip when identical); classification table has explicit promote rows; sync composition drops absolute “always preserved”; unit/data-integrity cover promotion. Pilot still forbids the combo on live consumers. Awaiting round-6 confirmation. |
| 6 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from rounds 1–5; file+line citations | **`findings`** (1 MAJOR) | Round-5 **R5-B1 confirmed RESOLVED**; Round-4 **R4-B1** still RESOLVED (pre-promotion path). Round-1/2/3 spot-check still RESOLVED. New **R6-M1** (sync-table kit-only gloss). Not cleared for K6b until R6-M1 → `pass`. No human escalation (`security \| irreversible \| real_money \| gates_tier3` not hit). |
| 6-fix (2026-07-11) | Author fix revision (R6-M1) | — | **R6-M1:** default-`sync` lock-rewrite + hand-edit note now say kit-only subset per digest rule (`origin: kit`, incl. promoted living docs) — no “(shared-asset)”-only gloss. Digest membership unchanged. Awaiting round-7 confirmation. |
| 7 (2026-07-11) | Independent Freeze-Step Reviewer (Cursor Grok 4.5 Thinking); different session from rounds 1–6; file+line citations | **`pass`** | Round-6 **R6-M1 confirmed RESOLVED**. Round-5 **R5-B1** + Round-4 **R4-B1** spot-check still RESOLVED (pre-promotion + promotion carve-out). Round-1/2/3 spot-check still RESOLVED. Full regress §K6.0–§K6.10: no new contradictions; no K6b leak. **Cleared for K6b.** No human escalation. |

**Round 1 findings (cited at review time — historical; addressed in 1-fix):**

| ID | Sev | Cat | Citation (at review time) | Round-2 confirmation |
| --- | --- | --- | --- | --- |
| B1 | BLOCKER | consistency | §K6.6.1 P7 | **RESOLVED** — P7 + evidence: zero *additional* writes / tree unchanged across dry-run; migrate footprint may already exist. |
| M1 | MAJOR | completeness | §K6.3 partial configs | **RESOLVED** — all four configs ship `thresholds` + nested `freeze_contract.reviewer`. |
| M2 | MAJOR | consistency | hard stop vs `--force` | **RESOLVED** — force table preserves living docs under `--migrate` / `--migrate --force`; overwrite only with `--force --include-preserved`. |
| M3 | MAJOR | completeness | sync lock + `origin: preserved` | **RESOLVED** — default sync retains preserved lock entries verbatim; promotion only via `--force --include-preserved`. |
| M4 | MAJOR | consistency | P2 vs preserved-living | **RESOLVED via R2-B1 (2-fix)** — check **and** write paths use kit-only aggregate digest; see §K6.4 lock digest rule. |
| M5 | MAJOR | consistency | KN-R2 vs conflict table | **RESOLVED** — KN-R2 PASS → `updated` without `--force`; conflict row composes `--force` **or** KN-R2. |
| N1 | MINOR | completeness | P5 / unanchored docs | **RESOLVED via R2-M1 (2-fix)** — P5 retirement PASS = aligned/`plan=None` only (§8 match). |
| N2 | MINOR | consistency | `""` docs-root / escape exits | **RESOLVED** — `"."` only; empty → `2`; `working_dir` escape → `2`. |

**Round 2 findings (addressed in 2-fix — round-3 confirmation):**

| ID | Sev | Cat | Citation | Round-3 confirmation |
| --- | --- | --- | --- | --- |
| R2-B1 | BLOCKER | consistency | §K6.4 lock digest | **RESOLVED** — kit-only `footprint_digest` on migrate write + default sync rewrite (L451–461); same set as `--check-footprint` (L465–470); preserved stay in per-file manifest (L449–450) but excluded from aggregate. |
| R2-M1 | MAJOR | consistency | §K6.6.1 P5 vs SPEC §8 | **RESOLVED** — P5 PASS = rule 1 only (`aligned` / `plan=None`, L531–534); in-anchor-only = diagnostic FAIL (L537–540); matches SPEC §8 “match” before retirement. |
| R2-N1 | MINOR | completeness | `--include-preserved` option | **RESOLVED** — first-class option on `init` + `sync` (L391); default off; no effect without `--force`; sync + `--only` interaction frozen (L416–419). |

**Round 3 findings (addressed in 3-fix — round-4 confirmation):**

| ID | Sev | Cat | Citation | Round-4 confirmation |
| --- | --- | --- | --- | --- |
| R3-B1 | BLOCKER | completeness | §K6.4 sync × `origin: preserved` vs §K4.3 | **RESOLVED** (as scoped) — sync flag table L413–416: preserved never written (incl. `kit-updated`); non-blocking warn; `sync --force` alone never writes/promotes. Composition rule L418–430: write gate = `--force --include-preserved` only; refusal gate never blocks preserved; hand-edit → default sync exit `0` when no kit-entry conflicts. L473–477 restates retain-verbatim + kit-only digest. |
| R3-N1 | MINOR | completeness | §K6.4 sync flag table | **RESOLVED** — explicit `sync --force` middle row L414; unit matrix L640 covers hand-edit → default sync exit `0` and `sync --force` alone does not overwrite preserved; data-integrity L644 covers hand-edit + check-footprint ok + shared-asset sync. |

**Round 4 findings (addressed in 4-fix — round-5 confirmation; still holds under 5-fix pre-promotion path):**

| ID | Sev | Cat | Citation | Round-7 confirmation |
| --- | --- | --- | --- | --- |
| R4-B1 | BLOCKER | consistency | §K6.2 Knowtation seed + §K6.4 digest/sync × living docs + P2 + hard stop | **RESOLVED** (pre-promotion) — living-doc origin rule L437–440 + classification L494/L496/L499 lock every migrate living doc as `origin: preserved` when classified `seed` / `unchanged` / `preserved` (Knowtation seed L188–193); kit-only digest write L523–528 + check L540–545 exclude them; hand-edit incl. seeded → check-footprint ok + default sync exit `0` (L472–476); `sync --force` alone never writes/promotes (L453, L464–465); P2 integrity over `origin: kit` incl. promoted (L597); unit L698 + data-integrity L702 + e2e L700 cover seeded hand-edit. Promotion is a separate carve-out (R5-B1). |

**Round 5 findings (addressed in 5-fix — round-6 confirmation):**

| ID | Sev | Cat | Citation | Round-7 confirmation |
| --- | --- | --- | --- | --- |
| R5-B1 | BLOCKER | consistency | §K6.4 living-doc origin rule + sync composition + force table vs promotion | **RESOLVED** — origin rule scoped to migrate **without** `--force --include-preserved` (L437–440); promotion carve-out L441–444 + force table L430 + classification promote rows L497/L500; sync composition write/refusal gates L457–471 (no absolute “always preserved”); unit L698 + data-integrity L702 cover init/sync promotion (differing + identical). Pilot forbid unchanged (L150, L433–435). |

**Round 6 findings (addressed in 6-fix — round-7 confirmation):**

| ID | Sev | Cat | Citation | Round-7 confirmation |
| --- | --- | --- | --- | --- |
| R6-M1 | MAJOR | consistency | §K6.4 sync flag table + composition vs digest rule | **RESOLVED** — default-`sync` lock-rewrite L452 cites kit-only subset per digest rule (`origin: kit`, incl. promoted living docs); L453/L455 inherit that gloss; composition hand-edit note L473–474 excludes preserved and keeps promoted in kit-only set; matches digest write rule L523–528 + check L540–545 + P2 L597 + unit L698. No “(shared-asset)”-only kit-only shorthand that excludes promoted. |

**Freeze status:** **Round 7 → `pass`.** Cleared for K6b Auto build against this matrix.

---

## Simple summary (no jargon)

We already have a working installer (`overseer init`). Four real projects need it, each with
different version-control rules and differently named living docs. This freeze locks **which
project goes first**, **exactly what config each gets**, **how we install without wiping their
existing handovers**, and **what “good enough to stop hand-maintaining” means** — before any Auto
session touches those repos.

## Technical summary

K6a freezes the §8 migration order extended to four consumers (Scooling → Knowtation → MuseHub →
VideoFactory), an additive `overseer init --migrate` contract that preserves existing living docs,
per-repo `.overseer/config.yaml` matrices (regime + doc paths + special preconditions), universal
and per-repo **parity gate** criteria keyed to `governance-sync --dry-run` + regime checks, the
external `git-only` quickstart deliverable, and the K6b seven-tier test matrix. Live production
inits and hand-process retirement remain operator-gated after parity PASS; no Tier-3 gate flips.

---

## §K6.0 — Scope

**In scope for K6a (this doc):** freeze WHAT/HOW for pilot install + parity; emit K6b Auto prompt
shape; record verified-on-disk consumer layout facts that K6b must honor.

**In scope for K6b (Auto Build, after freeze review `pass`):**

1. Implement additive CLI/config seams frozen here (`--migrate`, path normalization, optional Muse
   working-dir) against K4/K2 without forking core logic.
2. Ship prepared consumer config fixtures under `tests/fixtures/pilot/` (not live secrets).
3. Publish `docs/GIT-ONLY-QUICKSTART.md` (external developer template per §8 item 5).
4. Run seven-tier tests green locally on **fixtures** (no production tree required for DONE of the
   kit-side build).
5. Produce a paste-ready **operator runbook** for live feature-branch installs (one repo at a time
   in frozen order). Live inits are **operator-executed** under that runbook; K6b may assist only
   when the operator explicitly authorizes a named repo.

**Out of scope (hard stops — never K6a or K6b without separate Tier-3 authorization):**

| Action | Why blocked |
| --- | --- |
| Live `overseer init` into production trees during K6a | This phase is Thinking-only |
| Merge pilot PRs to consumer `main` / Muse canonical main | Tier 3 |
| `muse push staging`, staging deploy, live env/gate flips | Tier 3 |
| Retire hand-maintained handover/roadmap upkeep | Requires **parity gate PASS** + operator sign-off |
| `--force` overwrite of living docs during pilot (incl. `--force --include-preserved`) | Violates §8 “alongside, non-destructive”; see §K6.4 force rule |
| Dogfood `muse+git-mirror` on overseer-kit itself | That is **K7** |
| Redesign K4 footprint membership or 9A-5 write anchors | Compose; do not fork |

**Greenfield `init` (no `--migrate`)** remains exactly §K4.2 — K6 does not change empty-repo
behavior.

---

## §K6.1 — Install order (frozen)

Canonical-first, **one repo at a time**, non-destructive (§8). Extended order (ROADMAP + handover):

| Step | Consumer | Regime | Why this order |
| --- | --- | --- | --- |
| 1 | **Scooling** | `muse+git-mirror` | Richest policy source; coordination log owner; proves migrate + governance-sync parity first |
| 2 | **Knowtation** | `muse+git-mirror` | Same regime as Scooling; adds `no-docs-only-pr-to-main` rule-fragment gate |
| 3 | **MuseHub** | `muse-only` | Proves git-forbidden least-privilege; non-default doc filenames |
| 4 | **VideoFactory** | `git-only` | Proves baseline-without-Muse; non-`docs/` living-doc layout; doubles as quickstart exemplar |

No step starts until the previous step’s **kit-side fixture tests** are green **and** (for live
operator runs) the previous consumer’s **parity gate** is recorded PASS or explicitly deferred by
the operator with a written reason in that consumer’s change log.

---

## §K6.2 — Verified consumer layout (ground facts for K6b)

Verified on disk 2026-07-10. K6b configs **must** use these paths; do not invent alternate names.

| Consumer | Install root (operator machine) | Living handover | Living roadmap | Coordination / SD log | VCS markers |
| --- | --- | --- | --- | --- | --- |
| Scooling | `~/scooling` | `docs/OVERSEER-HANDOVER.md` | `docs/ROADMAP.md` | `docs/CROSS-REPO-COORDINATION.md` (SD log lives here) | `.muse/` + `.muse/git-bridge.toml` + `.git/` + `MUSE-BRIDGE-WORKFLOW.md`; **no** `.cursor/` yet |
| Knowtation | `~/knowtation` | `docs/OVERSEER-HANDOVER.md` | **absent** (phase truth currently cited as Scooling’s roadmap) | none local | `.muse/` + `.muse/git-bridge.toml` + `.git/`; existing `.cursor/rules/no-docs-only-pr-to-main.mdc` |
| MuseHub | `~/MUSE_HUB` (workspace that owns the living docs) | `docs/MUSEHUB-OVERSEER-HANDOVER.md` | `docs/MUSEHUB-ROADMAP.md` | none | Living docs at workspace `docs/`; Muse store observed at `musehub/.muse` (**not** at workspace root); **no** `.git` at workspace root |
| VideoFactory | `~/VIDEO FACTORY/VideoFactory` | `OVERSEER_HANDOVER.md` (**repo root**, underscore) | `ROADMAP.md` (**repo root**) | none | `.git/` only; rich `.cursor/rules/` (product rules — kit must not delete them) |

**Frozen consequences of these facts:**

1. **Knowtation roadmap seed:** migrate **seeds** `docs/ROADMAP.md` from the kit template when
   absent (write allowed) and locks it `origin: preserved` (living-doc origin rule — §K6.4).
   Handover is **preserved**. After seed, Knowtation owns a local roadmap; hand-edits do not flip
   footprint integrity and are not overwritten by `sync --force` alone. Cross-repo orchestration
   notes may still point at Scooling, but kit config always resolves a local `docs.roadmap` path
   (schema requires it; handover==roadmap collision is forbidden).
2. **MuseHub Muse cwd seam:** install root owns docs; Muse working tree may be a subdirectory.
   K6b implements optional `vcs.muse.working_dir` (§K6.5). Live MuseHub pilot is blocked until that
   seam is implemented **and** `adapter.status()` succeeds against the configured working dir.
3. **VideoFactory path seam:** `repo.root_relative_docs: "."` with exact filenames
   `OVERSEER_HANDOVER.md` / `ROADMAP.md`. K6b normalizes the docs-root sentinel `"."` so
   destinations are bare relative paths (not `./file` and never `/file`) in footprint, tokens,
   lock, and governance-sync path joins (§K6.5). Empty string is **not** a valid config value.
4. **Cursor coexistence:** VideoFactory (and any consumer) may already have `.cursor/rules/*`.
   Kit vendoring adds/replaces **only** kit-owned rule filenames (`governance-sync.mdc`,
   `no-docs-only-pr-to-main.mdc`, `tier-authority.mdc`). Other consumer rules are never deleted.

---

## §K6.3 — Per-repo install matrix (frozen configs)

Each row below is the **complete, authoritative** config K6b materializes via `--from-config`
(prepared YAML under `tests/fixtures/pilot/` for tests; operator copies for live runs). Every
fixture must be a full loadable document — `thresholds` and nested `freeze_contract.reviewer`
are required (no “inherit from Scooling” guessing). Values are names/booleans only (§9) — no
secrets, no absolute machine paths in committed fixtures (fixtures use synthetic repo names;
operator runbook substitutes real roots via `-C`).

**Shared freeze_contract (identical across all four pilots unless a future phase freezes a
delta):** `enabled: true`; `reviewer: {mode: agent, model: thinking-high, provider: local,
fallback: human}`; `human_escalation: [security, irreversible, real_money, gates_tier3]`.

**Shared thresholds (identical across all four pilots):** `realign_max_commits: 50`,
`drift_warn_only: true`.

### K6.3.1 — Scooling (`muse+git-mirror`)

```yaml
overseer_config_version: 1
repo:
  name: scooling
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
  coordination: CROSS-REPO-COORDINATION.md
  standing_decisions: CROSS-REPO-COORDINATION.md
thresholds:
  realign_max_commits: 50
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security, irreversible, real_money, gates_tier3]
```

**Init command (live, operator-gated):**

```bash
./cli/overseer -C <scooling-root> init --migrate --from-config <prepared-scooling.yaml> --non-interactive
```

**Special checks:** after migrate, `governance-sync --dry-run` is the primary parity probe; D2
realign remains dry-run-only during pilot.

### K6.3.2 — Knowtation (`muse+git-mirror`)

```yaml
overseer_config_version: 1
repo:
  name: knowtation
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
    working_dir: null
docs:
  handover: OVERSEER-HANDOVER.md
  roadmap: ROADMAP.md                 # seeded if absent
  coordination: null
  standing_decisions: ROADMAP.md
thresholds:
  realign_max_commits: 50
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security, irreversible, real_money, gates_tier3]
```

**Rule-fragment gate (before replacing cursor rule):**

| Check ID | Criterion | Fail action |
| --- | --- | --- |
| KN-R1 | Existing `.cursor/rules/no-docs-only-pr-to-main.mdc` is present | Stop; do not invent a replacement without operator review |
| KN-R2 | After rendering kit `cursor/rules/no-docs-only-pr-to-main.mdc` with Knowtation tokens, **semantic parity** holds: forbids docs-only PR/merge to `vcs.git.main_branch`; allows feature-branch commits; `alwaysApply: true` | Refuse replace; print unified diff; operator resolves |
| KN-R3 | Byte-identity is **not** required (kit is tokenized; consumer rule is hardcoded `main`/`docs/`) | — |

**KN-R2 → migrate classification (frozen exception):** on KN-R2 PASS, the destination
`.cursor/rules/no-docs-only-pr-to-main.mdc` is classified `updated` (write allowed) **without**
`--force`, even when on-disk bytes differ from rendered kit bytes. On KN-R2 FAIL, that destination
remains a normal shared-asset `conflict` (refuse exit `4` unless `--force`). Other
`.cursor/rules/*` files are untouched.

### K6.3.3 — MuseHub (`muse-only`)

```yaml
overseer_config_version: 1
repo:
  name: musehub
  root_relative_docs: docs
vcs:
  regime: muse-only
  canonical: muse
  git:
    remote: origin                 # present in schema; unused — git methods no-op
    main_branch: main
    mirror_branch: null
    feature_branch_pattern: "feat/{slug}"
  muse:
    staging_remote: null
    main_branch: main
    working_dir: musehub           # relative to install root; see §K6.5
docs:
  handover: MUSEHUB-OVERSEER-HANDOVER.md
  roadmap: MUSEHUB-ROADMAP.md
  coordination: null
  standing_decisions: MUSEHUB-ROADMAP.md
thresholds:
  realign_max_commits: 50
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security, irreversible, real_money, gates_tier3]
```

**Regime checks (parity + security):**

| Check ID | Criterion |
| --- | --- |
| MH-G1 | `adapter.mirror(...)` reports git-forbidden / no-op; zero git process invocations |
| MH-G2 | `read_head("origin/main")` returns ReadError git-forbidden |
| MH-G3 | `realign` returns single-history no-op |
| MH-G4 | `adapter.status()` succeeds using `vcs.muse.working_dir` |

### K6.3.4 — VideoFactory (`git-only`)

```yaml
overseer_config_version: 1
repo:
  name: VideoFactory
  root_relative_docs: "."
vcs:
  regime: git-only
  canonical: git
  git:
    remote: origin
    main_branch: main
    mirror_branch: null
    feature_branch_pattern: "feat/{slug}"   # VF also uses video/BOR-* product branches; kit pattern is governance-only
  muse:
    staging_remote: null
    main_branch: null
    working_dir: null
docs:
  handover: OVERSEER_HANDOVER.md            # underscore — exact on-disk name
  roadmap: ROADMAP.md
  coordination: null
  standing_decisions: ROADMAP.md
thresholds:
  realign_max_commits: 50
  drift_warn_only: true
freeze_contract:
  enabled: true
  reviewer:
    mode: agent
    model: thinking-high
    provider: local
    fallback: human
  human_escalation: [security, irreversible, real_money, gates_tier3]
```

**Special checks:** path normalization (§K6.5); kit cursor rules add without deleting product rules;
`realign`/`mirror` no-op; governance-sync dry-run works on root-level living docs.

---

## §K6.4 — `overseer init --migrate` (frozen additive contract)

**Purpose:** first install into a repo that **already has** hand-authored living docs — add the kit
*alongside* them (§8). Does not replace §K4.2 greenfield `init`.

**New options (additive to §K4.2 / §K4.3):**

| Option | Commands | Type | Default | Meaning |
| --- | --- | --- | --- | --- |
| `--migrate` | `init` | flag | off | Enable living-doc preserve + **living-doc origin rule** (pre-promotion: every living-doc destination locked `origin: preserved`, including seeds) |
| `--include-preserved` | `init`, `sync` | flag | off | With `--force`: **promote** living-doc paths — overwrite with rendered kit bytes and lock/rewrite `origin: kit`. **No effect unless `--force` is also set.** Post-parity only; pilot-forbidden on live consumers. |

**Requires (`init --migrate`):** `--non-interactive` for CI/fixtures, and either `--from-config` or explicit
`--regime` plus values sufficient to build a valid config (fail closed `2` if guessing required).

**`--force` under `--migrate` (frozen — resolves K4.2 force vs §8 preserve):**

| Flag combo | Living docs (handover / roadmap / coordination) | Shared assets (policy / cursor / SD reference) | Config |
| --- | --- | --- | --- |
| `--migrate` (no `--force`) | always `preserved` when present+differs (skip write; never refuse); absent living docs are `seed` (write) then locked `origin: preserved` | `conflict` → refuse exit `4` | existing config still subject to §K4.2 step-1 (refuse without `--force`) |
| `--migrate --force` | **still** never overwrite living docs (skip write on present+differs; seeds still write only when absent); lock `origin: preserved` | may overwrite | may overwrite `.overseer/config.yaml` per §K4.2 step-1(a) |
| `--migrate --force --include-preserved` | **promote:** present living docs → classify `updated`, lock `origin: kit` (overwrite when bytes differ; ownership-only when already identical). Absent living docs still `seed` then lock `origin: preserved` (seed is not a promotion) | may overwrite | may overwrite config |

`--include-preserved` without `--force` is a no-op for living-doc writes (living docs stay
`origin: preserved` when classified `seed` / `unchanged` / `preserved`). Pilot runbook and K6b DoD
**forbid** `--force --include-preserved` on live consumers. Hard stop: living-doc overwrite during
pilot.

**Living-doc origin rule (frozen — resolves R4-B1; promotion carve-out resolves R5-B1):** under
`init --migrate` **without** `--force --include-preserved`, every footprint destination that is a
configured **living doc** (handover / roadmap / coordination) is recorded in `version.lock` with
`origin: preserved`, whether migrate classified the path as `seed`, `unchanged`, or `preserved`.
**Promotion carve-out:** when `--force --include-preserved` is set, every **present** living doc
is promoted: classify `updated`, lock `origin: kit` (write rendered bytes if they differ; ownership-
only lock flip if already identical). Same end-state as sync promotion. Absent living docs remain
`seed` → `origin: preserved` (seed is not promotion). Shared assets (policy / cursor / SD reference)
remain `origin: kit` (default). Greenfield `init` without `--migrate` is unchanged (§K4.2 — living
docs are kit-owned).

**`sync` × living docs / `origin: preserved` (frozen — amends K4.3 conflict composition for migrate locks):**

| Flag combo | Living-doc / `origin: preserved` paths | Conflict / refusal | Lock rewrite |
| --- | --- | --- | --- |
| default `sync` (no `--include-preserved`) | never written (incl. when classified `kit-updated`) | **non-blocking** — report warn only (same as K4.3 `--only` out-of-scope conflicts); never refuse the whole sync | retain preserved manifest entries verbatim; recompute `footprint_digest` over kit-only subset per digest rule (`origin: kit`, incl. promoted living docs) |
| `sync --force` (no `--include-preserved`) | **never written / never promoted** | same non-blocking warn for living docs; `--force` may still overwrite **shared-asset** conflicts per K4.3 | same retain-verbatim + kit-only digest as default |
| `sync --force --include-preserved` | may overwrite when bytes differ; **always promote** matching preserved paths → `origin: kit` (ownership flip even if unchanged) | promotion path | rewrite promoted entries (`origin: kit`, sha256 = on-disk/written bytes); digest includes them as kit |
| `sync --include-preserved` without `--force` | no living-doc write (same as default for preserved paths) | same non-blocking warn as default | same retain-verbatim + kit-only digest as default |

**Living-doc sync composition rule (frozen):** for every path whose lock entry **currently** has
`origin: preserved` (after a default `--migrate`, that is every living-doc destination that has not
yet been promoted — seeded, unchanged, or hand-preserved):

1. **Write / promote gate:** a preserved path is promoted only when `--force --include-preserved`
   is set (and `--only` eligibility holds). Promotion **writes** rendered bytes when they differ and
   **always** rewrites lock `origin: kit`. `kit-updated`, `consumer-modified`, and `both-changed`
   classifications on preserved paths never alone authorize a write or promotion. `sync --force`
   alone never writes or promotes living docs.
2. **Refusal gate:** living-doc / preserved-path conflicts / kit-updated states are **never** blocking
   conflicts under default sync or `sync --force` alone — warn only, proceed with in-scope
   shared-asset updates. Only **`origin: kit`** in-scope conflicts refuse exit `4` without `--force`
   (K4.3 unchanged for kit entries). Under **pre-promotion** migrate locks, living docs are
   `origin: preserved` and therefore non-blocking; after promotion they are `origin: kit` and follow
   normal shared-asset / kit refusal rules.
3. A hand-edit to a living doc after migrate (including a **seeded** roadmap) **while it remains
   `origin: preserved`** therefore leaves `--check-footprint` ok (kit-only subset per digest rule —
   preserved paths excluded; promoted living docs remain in the kit-only set)
   **and** leaves default `overseer sync` able to update shared assets (exit `0` when no shared-asset
   conflicts).

**Interaction with `sync --only`:** `--only` still restricts which paths are *eligible* to write.
`--include-preserved` does not expand `--only`; a preserved path is written only when it matches an
`--only` glob (or `--only` is absent) **and** `--force --include-preserved` is set. Out-of-scope
preserved entries always retain verbatim (K4.3 out-of-scope retain rule) and remain non-blocking.

**Behavior (frozen sequence):**

1. Resolve repo root (`-C` / cwd). Apply §K4.2 step-1 existence rule for an **already-initialized**
   kit install (force / no-op / refuse). `--migrate` does not bypass a conflicting existing
   `.overseer/config.yaml` without `--force`.
2. Load/build config; validate via `load_config` → fail closed `2`.
3. Resolve footprint per §K4.5 (after §K6.5 path normalization).
4. Classify each footprint destination:

   | On-disk state | Flags | Classification | Action |
   | --- | --- | --- | --- |
   | absent, **living doc** | any `--migrate` combo | `seed` | write rendered bytes; lock `origin: preserved` (sha256 = written bytes). Seed is not promotion. |
   | absent, **shared asset** | any | `seed` | write rendered bytes; lock `origin: kit` |
   | present + byte-identical to rendered, **living doc** | without `--force --include-preserved` | `unchanged` | skip write; lock `origin: preserved` (sha256 = on-disk bytes) |
   | present + byte-identical to rendered, **living doc** | `--force --include-preserved` | `updated` (promotion) | skip byte write (already match); lock **`origin: kit`** (sha256 = on-disk / rendered bytes — ownership promotion so future kit updates are not stuck behind preserve gates) |
   | present + byte-identical to rendered, **shared asset** | any | `unchanged` | skip write; lock `origin: kit` |
   | present + differs, **living doc** | `--migrate` or `--migrate --force` (no `--include-preserved`) | `preserved` | **skip write**; lock `origin: preserved` (sha256 = on-disk bytes); never refuse |
   | present + differs, **living doc** | `--migrate --force --include-preserved` | `updated` (promotion) | **write** rendered bytes; lock `origin: kit` (sha256 = written bytes) |
   | present + differs, **shared asset** | any | `conflict` | refuse whole op exit `4` unless `--force` **or** the KN-R2 PASS exception (§K6.3.2) |
   | present + differs, Knowtation `.cursor/rules/no-docs-only-pr-to-main.mdc` **and** KN-R2 PASS | any | `updated` | write rendered bytes **without** requiring `--force`; lock `origin: kit` |

5. Write config (if needed), all `seed`/`updated` files (including promoted living docs), forced
   shared-asset updates; write `version.lock` **last** (§K4.4 durability).
6. Report `created[]`, `preserved[]`, `unchanged[]`, `updated[]`, `conflicts[]`. Exit `0` on success.

**Lock additive field (frozen, MINOR-compatible with §K4.6):** each footprint manifest entry may
include:

```yaml
origin: kit | preserved     # default kit when omitted (greenfield / shared-asset)
```

- `origin: preserved` → sha256 is the **on-disk** (or just-written seed) living-doc bytes at migrate
  time; `source` still names the kit template for traceability. Preserved entries **remain in the
  per-file manifest**. Under `--migrate` **without promotion**, living-doc destinations use this
  origin (living-doc origin rule above) — including Knowtation’s seeded roadmap.
- **Promotion → `origin: kit`:** after `init --migrate --force --include-preserved` or
  `sync --force --include-preserved` promotes a present living doc, that entry’s lock `origin` is
  `kit` and its sha256 is the on-disk / newly written bytes. Promoted living docs join the kit-only
  digest set and follow kit refusal/write rules thereafter.
- **`footprint_digest` write rule (frozen — amends K4.7 composition for migrate locks):** on
  `init --migrate` lock write **and** every subsequent `sync` lock rewrite while any
  `origin: preserved` entries exist, compute `footprint_digest` over **`origin: kit` (and
  omitted-default kit) entries only** — i.e. shared assets **plus any promoted living docs** (the
  **same set** `--check-footprint` uses). Preserved living-doc entries are **excluded** from the
  aggregate. When no `origin: preserved` entries remain (all living docs promoted, or greenfield),
  digest is the full-manifest digest per K4.7.
- **Default `sync` / `sync --force` (no `--include-preserved`):** never writes `origin: preserved`
  paths on disk; living-doc classifications are non-blocking (warn only — see sync composition rule
  above). When rewriting `version.lock`, **retain those manifest entries verbatim** (`path`,
  `source`, `sha256`, `origin`) — same retain rule as K4.3 `--only` out-of-scope entries. Do **not**
  replace preserved sha256 with rendered kit bytes while leaving the file alone. Recompute
  `footprint_digest` from the kit-only subset after the rewrite.
- **`sync --force --include-preserved`:** promotes eligible `origin: preserved` living-doc paths —
  write rendered bytes when they differ; always rewrite lock to `origin: kit` (ownership promotion
  even when bytes already match). Promoted entries join the kit-only digest set. Post-parity only;
  forbidden in default pilot.
- **`status --check-footprint` integrity (frozen):** recompute digest over **`origin: kit` (and
  omitted-default kit) entries only** and compare to `version.lock.footprint_digest` (which was
  written over that same set). Paths with `origin: preserved` are reported separately as
  `preserved-living` (informational). A hand-edit to a living doc — **including a seeded roadmap** —
  **while `origin: preserved`** **never alone** flips footprint integrity to `mismatch` / exit `6`.
  Shared-asset / promoted (`origin: kit`) mismatch still reports `mismatch` as today.

**Idempotency:** re-running `init --migrate` when config + lock + on-disk match → no-op exit `0`.

**Dry-run:** `--dry-run` reports the classification plan and writes nothing.

---

## §K6.5 — Additive config / path seams (frozen for K6b)

### K6.5.1 — `vcs.muse.working_dir`

Optional string | null. Default `null` (= install root).

When set (MuseHub matrix): every Muse invocation the `muse-only` and `muse+git-mirror` backends
make uses `muse -C <absolute(install_root / working_dir)>` (existing cwd-safety rule), while
**file** reads/writes for living docs and footprint stay under install root.

Validation (at `load_config` / config build): path must resolve inside install root (no `..`
escape, no absolute path that leaves the root) → else config error exit `2`. Runtime write-path
escape refusals elsewhere remain exit `4` per K4.

### K6.5.2 — `root_relative_docs` normalization

When `repo.root_relative_docs` is exactly `"."` (after strip):

| API | Normalized relative path for doc `NAME` |
| --- | --- |
| footprint destination | `NAME` |
| token `docs.*_path` | `NAME` |
| governance-sync joins | `repo_root / NAME` |

When docs root is any other relative segment (e.g. `docs`), keep `{root}/{NAME}` as today.

**Not valid:** empty string `""` — `load_config` continues to require a non-empty
`root_relative_docs` (fail closed `2`). Pilots that want repo-root docs use `"."` only.

Forbidden: emitting absolute paths, leading `/`, or `..` segments in destinations (§9 / K4 path
confinement).

---

## §K6.6 — Parity gate (frozen criteria)

Parity is the §8 gate that must PASS **before** any hand process is retired and before
`--include-preserved` promotion. It is **not** a Tier-3 product gate flip.

### K6.6.1 — Universal criteria (every consumer)

| ID | Criterion | Evidence |
| --- | --- | --- |
| P1 | `.overseer/config.yaml` validates; regime matches matrix row | `load_config` + `status` |
| P2 | `.overseer/version.lock` present; **`origin: kit`** footprint integrity OK (shared assets + any promoted living docs) | `status --check-footprint` (`origin: preserved` paths excluded from integrity mismatch — §K6.4) |
| P3 | Living docs still present at configured paths; migrate preserved or seeded them; lock `origin: preserved` for every **unpromoted** living-doc destination | file exists; lock `origin: preserved` on handover / roadmap / coordination (parity runs before promotion) |
| P4 | `overseer governance-sync --dry-run` exits `0` (fail-closed reads succeed) | CLI exit + report |
| P5 | **Content parity** (see rules below) | dry-run report + optional plan diff |
| P6 | No secrets/identity/absolute machine paths in dry-run report, lock, or planned patch text | security scan |
| P7 | Feature-branch only; no write to protected main/canonical; **governance-sync dry-run wrote zero bytes** (no *additional* writes during the parity probe — migrate footprint may already exist) | report `dry_run: true`; tree unchanged across the dry-run invocation |

**P5 rules (frozen — §8 “match” = byte-aligned dry-run):**

1. If dry-run reports **aligned** / `plan=None` (D1–D3 fully aligned; engine short-circuit) → **P5
   PASS**. This is the only PASS path. It is the SPEC §8 requirement that kit-driven
   `governance-sync --dry-run` **matches** the current hand-maintained handover/roadmap before any
   hand process is retired.
2. If a plan exists with any planned edit **outside** 9A-5 named anchors (`HANDOVER_ANCHORS` /
   `ROADMAP_ANCHORS`) → **P5 FAIL** (out-of-anchor drift).
3. If a plan exists and all planned edits are **inside** those anchors only → report diagnostic
   `in_anchor_only`; **P5 still FAIL** for the parity gate (planned ≠ on-disk, so §8 match is not
   met). Operator aligns hand docs (or applies a reviewed non-dry-run sync in a later
   operator-gated session) until a subsequent dry-run returns `aligned` / `plan=None`.
4. A drifted **unanchored** tree that forces a plan with fallback anchor insertion → **P5 FAIL**
   until the operator aligns the hand docs (rule 1) or seeds anchors and then reaches rule 1.

**Pilot expectation:** first-install consumers typically lack `<!-- overseer:anchor:* -->`
markers. Retirement therefore waits for rule 1 — not for an in-anchor-only plan.

**PASS** = P1–P7 all true, recorded in the consumer change log (and optionally a
`.overseer/parity-gate.yaml` stamp with timestamp + kit_version only — no identity).

**FAIL** = any Pi false → hand process stays; kit remains installed alongside; operator fixes drift
or anchors, re-runs dry-run.

### K6.6.2 — Per-repo extra criteria

| Consumer | Extra IDs | Criterion |
| --- | --- | --- |
| Scooling | SC-P1 | `docs.coordination` resolves; standing_decisions points at coordination; coordination file preserved |
| Scooling | SC-P2 | Regime `muse+git-mirror`; bridge marker present; D2 dry-run path reachable without apply |
| Knowtation | KN-P1 | KN-R2 rule-fragment gate PASS; vendored rule on disk |
| Knowtation | KN-P2 | `docs/ROADMAP.md` exists (seeded or pre-existing); handover preserved |
| MuseHub | MH-P1 | MH-G1–G4 all PASS |
| MuseHub | MH-P2 | Living docs remain `MUSEHUB-*` names under `docs/` |
| VideoFactory | VF-P1 | Token/footprint paths are bare `OVERSEER_HANDOVER.md` / `ROADMAP.md` |
| VideoFactory | VF-P2 | Pre-existing non-kit `.cursor/rules/*` still present after migrate |

### K6.6.3 — What parity does **not** authorize

Parity PASS does **not** authorize: merge to main, staging push, gate flips, deleting backup copies
of hand docs, enabling Automation that requires Tier-3, or `--force --include-preserved`
promotion. Those remain separate operator acts.

---

## §K6.7 — Live operator runbook shape (frozen; executed only with consent)

Per consumer, in order:

1. Feature branch in that repo under its VCS rules (`feat/overseer-k6-pilot` or Muse equivalent).
2. `overseer init --migrate --from-config … --non-interactive` (optionally `--dry-run` first).
   **Never** pass `--force --include-preserved` during pilot.
3. `overseer status --check-footprint`.
4. `overseer governance-sync --dry-run` → evaluate P1–P7 + per-repo extras.
5. On PASS: record stamp + change-log line; **leave** hand process in place until operator
   explicitly retires it in a later session.
6. Open PR / Muse proposal for review; **do not** auto-merge.

K6b ships this runbook as `docs/MIGRATE-EXISTING-REPO.md`.

---

## §K6.8 — External `git-only` quickstart (frozen deliverable)

K6b adds `docs/GIT-ONLY-QUICKSTART.md`:

- Prerequisites: clone overseer-kit (or install shim path); GitHub repo; no Muse required.
- Commands: `overseer init --regime git-only --non-interactive` on an empty or new repo;
  `status`; `governance-sync --dry-run`; `review --freeze` on a sample artifact.
- States VideoFactory as the **in-house** `git-only` reference after its pilot parity PASS.
- Reaffirms K7 guardrail: no core capability is MuseHub-only.

---

## §K6.9 — Security / least-privilege (frozen)

- Migrate never logs tokens, credentials, or absolute paths (§9).
- `muse-only` never invokes git/gh (MH-G1–G2).
- `git-only` never invokes muse.
- Path confinement: `-C`, `--from-config`, `working_dir`, and all footprint destinations stay inside
  install root (`working_dir` escape at config validate → exit `2`; other path-escape refusals →
  exit `4`).
- Templates: fixed token set only; no shell interpolation of doc content.
- Pilot PRs are reviewable Tier-1 diffs; no hidden hooks installed by K6.

---

## §K6.10 — Seven-tier test matrix (K6b)

Per `policy/test-tiers.yaml` and spec §10. All under `tests/`; **no test mutates a real consumer
repo**. Use `tmp_path` trees cloned from `tests/fixtures/pilot/*` layouts.

| Tier | Module(s) (new/extended) | Cases that must pass |
| --- | --- | --- |
| **unit** | `test_init_migrate.py`, `test_path_normalize.py`, `test_muse_working_dir.py`, argparse extensions | `--migrate` classification table; `--migrate --force` preserves living docs; KN-R2 PASS → `updated` without `--force`; living-doc origin rule (seed / unchanged / differs → lock `origin: preserved`); **`--migrate --force --include-preserved` on differing living doc → write + lock `origin: kit`; on identical living doc → ownership promotion lock `origin: kit` without byte rewrite**; preserved lock + sync retain-verbatim; **kit-only `footprint_digest` on migrate write and sync rewrite** (shared assets + promoted only); `--check-footprint` ignores preserved living docs for integrity mismatch; refuse shared-asset conflict without `--force`; `--include-preserved` without `--force` is no-op; **hand-edit to preserved living doc → default sync exit `0`**; **hand-edit to seeded living doc → `--check-footprint` ok + default sync exit `0`**; **`sync --force` alone does not overwrite preserved or seeded living docs**; **`sync --force --include-preserved` promotes preserved → `origin: kit` + joins digest** (differing and identical cases); `.` docs-root normalization; empty `root_relative_docs` → `2`; `working_dir` escape → `2`; unknown flag → `1` |
| **integration** | `test_pilot_matrix_configs.py` | Each of 4 **complete** prepared configs loads; footprint destinations match matrix; MuseHub config wires working_dir; VF bare paths; coordination skip/include |
| **e2e** | `test_pilot_migrate_cycle.py` | Fixture with pre-existing handover ≠ template → migrate preserves bytes + seeds missing roadmap with lock `origin: preserved` + vendors policy/cursor; status OK (preserved-living informational; kit-only digest matches); hand-edit seeded roadmap leaves check-footprint ok; governance-sync dry-run exit `0`; second migrate no-op |
| **stress** | `test_pilot_large_preserved_docs.py` | Large preserved handover/roadmap; migrate + status + dry-run stay bounded |
| **data-integrity** | `test_migrate_idempotency.py` | Run-twice migrate identical; dry-run zero writes; mid-write failure leaves lock unadvanced; preserved sha matches on-disk; default sync retains preserved lock entries verbatim; **hand-edit to preserved doc leaves `--check-footprint` ok** (kit-only digest unchanged) **and** default sync still updates kit shared assets without refusing; **same for hand-edit to seeded living doc**; **after `sync --force --include-preserved`, promoted living-doc lock is `origin: kit` and joins digest; subsequent hand-edit flips footprint integrity** |
| **performance** | `test_pilot_status_bounded.py` | status + governance-sync dry-run on pilot-sized fixture within bounded budget; no unbounded VCS scans |
| **security** | `test_pilot_least_privilege.py`, `test_pilot_no_secret_leak.py` | muse-only fixture zero git calls; path escape refused; outputs free of secrets/absolute paths; `--include-preserved` absent from default sync / pilot runbook |

**Definition of Done for K6b (frozen):** additive seams + quickstart + operator runbook + seven
tiers green; both kit governance docs updated; feature-branch PR on overseer-kit; **no** claim of
consumer parity PASS unless an operator-recorded stamp exists for that consumer; **no** gate flips.

**Definition of Done for K6a (this phase):** this matrix doc frozen; ROADMAP + HANDOVER updated;
K6b paste-ready prompt staged; awaiting freeze-review `pass` before Auto build.

---

## §K6.11 — Recommendation (path forward)

1. **Done:** Independent freeze review **round 7** → **`pass`** (R6-M1 + R5/R4 spot-check +
   §K6.0–§K6.10 regress).
2. Execute **K6b Auto** against fixtures only until green (paste-ready prompt in handover).
3. Operator then runs live pilots **in order** (Scooling first) on feature branches using the
   runbook; record parity stamps; keep hand upkeep until explicitly retired.
4. Defer overseer-kit’s own `muse+git-mirror` flip to **K7**.

---

## Cross-references

- `docs/OVERSEER-KIT-SPEC.md` §3, §4, §5, §8, §9, §10
- `docs/archive/phases/PHASE-K4-VENDORING-CLI-CONTRACT.md` — greenfield init/sync/status; migrate is additive
- `docs/archive/phases/PHASE-9A-5-GOVERNANCE-HYGIENE-AGENT-OUTLINE.md` — dry-run parity probe + anchors
- `policy/test-tiers.yaml` — RULE #0 tier contract
- `docs/ROADMAP.md` / `docs/OVERSEER-HANDOVER.md` — phase control + relay
