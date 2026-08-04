# Phase KIT-PRESERVE-SHARED-ASSETS — `ok init --preserve-shared-assets`

Status: **Reviewed → `pass` (PSA-r1)** + **Build verified → `pass` (PSA-BV-r1).**
Implements the consumer-owned shared-asset preserve path so `init --migrate --force`
stops clobbering bridge scripts (`MUSE-BRIDGE-WORKFLOW.md`, `scripts/muse-bridge-deploy.sh`)
and other non-living footprint files the consumer already customized.

```yaml
phase: KIT-PRESERVE-SHARED-ASSETS
outputs:
- id: preserve-shared-assets
  path: docs/archive/phases/PHASE-PRESERVE-SHARED-ASSETS.md
  frozen: true
frozen_inputs:
- id: k6-migrate-preserve
  path: docs/archive/phases/PHASE-K6-PILOT-INSTALL-MATRIX.md
- id: k7-bridge-footprint
  path: docs/archive/phases/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: test-tiers
  path: policy/test-tiers.yaml
- id: decision-tiers
  path: policy/tiers.yaml
- id: scooling-product-order
  path: ~/scooling/docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-30T17:09:41Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:c8f1eacc6f0833997e79810eb37d65f65d62d9c39033c1b5f2fd97b4b467a02c
```

**Incident (ground truth):** Knowtation `init --migrate --force` (2026-07-26) overwrote
consumer bridge assets with kit templates. Living docs were preserved (§K6.4); shared assets
were not. Operator restored bytes and marked `origin: preserved` by hand; footprint mismatch
remains intentional until this flag lands.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

---

## §PSA.0 — Simple summary

When a repo already has its own bridge scripts (or other kit shared files), install must be
able to keep those files instead of replacing them with kit copies — even when `--force` is
used for the rest of the install.

**Technical summary:** add `ok init --preserve-shared-assets`. Under migrate (and greenfield
conflict handling), differing **non-living** footprint destinations are classified
`preserved`, locked `origin: preserved`, and never byte-written unless
`--force --include-preserved` promotes them. Default (flag absent) behavior stays unchanged.

---

## §PSA.1 — Scope

**In scope:**

1. Argparse flag `--preserve-shared-assets` on `ok init` only.
2. Migrate classification change for non-living footprint rows (§PSA.3).
3. Greenfield init: when the flag is set, differing existing shared assets are preserved
   instead of conflict/refuse or `--force` overwrite (§PSA.4).
4. Lock `origin: preserved` + kit-only digest exclusion (reuse §K6.4 machinery).
5. Seven-tier tests (§PSA.8).
6. Kit ROADMAP + HANDOVER update; no live consumer re-init in this phase.

**Out of scope (explicit non-goals):**

- Changing default migrate/`--force` behavior when the flag is **absent**.
- New `sync` flag (once `origin: preserved`, existing sync retain rules apply).
- `upgrade-regime` flag changes (keeps its own `--force` bridge overwrite contract).
- Live Knowtation/Scooling re-init (operator-gated; Tier 3).
- Redesign of living-doc preserve / `--include-preserved` promotion.
- Blocking KN-R2 semantic updates (KN-R2 PASS still `updated` without `--force`).

---

## §PSA.2 — Shared asset definition

A footprint destination is a **shared asset** when it is **not** in
`living_doc_destinations(config)` (handover / roadmap / coordination). Includes regime-
conditional bridge files (`MUSE-BRIDGE-WORKFLOW.md`, `scripts/muse-bridge-deploy.sh`) and
policy/cursor kit copies.

---

## §PSA.3 — Migrate classification (additive)

Extend `_classify_migrate` for the shared-asset branch:

| Existing | Identical? | `--preserve-shared-assets` | `--force --include-preserved` | Class | Lock origin |
| --- | --- | --- | --- | --- | --- |
| absent | — | any | any | `seed` | `kit` |
| present | yes | any | any | `unchanged` | `kit` |
| present | no | **set**, promote false | — | **`preserved`** | **`preserved`** |
| present | no | set | promote true | `updated` | `kit` |
| present | no | unset | force true | `updated` (today) | `kit` |
| present | no | unset | force false | `conflict` (today) | — |
| KN-R2 PASS | no | any | — | `updated` | `kit` |

`--preserve-shared-assets` alone (no `--force`) converts what would have been a shared-asset
`conflict` into `preserved`. With `--force` and the flag, differing shared assets stay
`preserved` (do **not** overwrite). Only `--force --include-preserved` promotes/overwrites
them (same escape hatch as living docs; pilot-forbidden for routine installs).

Living-doc rows are unchanged by this flag.

---

## §PSA.4 — Greenfield init

When `--preserve-shared-assets` is set:

- Differing existing **shared** destinations are **not** listed as conflicts and are **not**
  written; lock entries use on-disk bytes + `origin: preserved`.
- Without the flag: existing refuse/`--force` overwrite behavior unchanged.
- Living docs under greenfield remain as today (overwrite on `--force`; conflict without).

---

## §PSA.5 — Sync / footprint integrity

No sync code changes required when lock origin is `preserved` — §K6.4 retain-verbatim and
kit-only digest already apply. `--check-footprint` excludes `origin: preserved` from
integrity mismatch (shared or living).

---

## §PSA.6 — CLI surface

```text
ok init --preserve-shared-assets
```

Help text (exact intent): preserve existing differing shared assets (non-living footprint);
lock `origin:preserved`; with `--force` still does not overwrite them unless
`--include-preserved`.

---

## §PSA.7 — Hard stops

- No live consumer `init` / re-init without operator authorization.
- No secrets in commits, logs, or lock files.
- No feature→GitHub-`main` in consumers; kit merge to `main` remains Tier 3 (SD-21 land
  hygiene may apply after BV `pass` with no live flips).
- Do not change default overwrite behavior when the flag is absent.

---

## §PSA.8 — Seven-tier test matrix

| Tier | Cases |
| --- | --- |
| **unit** | Classification table rows; argparse accepts flag; unknown flag still exit `1`; living-doc path unchanged with flag set; KN-R2 still updates under flag |
| **integration** | `init --migrate --preserve-shared-assets` keeps hand-tuned `muse-bridge-deploy.sh` + workflow; lock `origin: preserved`; `--migrate --force --preserve-shared-assets` same; without flag `--migrate --force` still overwrites |
| **e2e** | Fixture muse+git-mirror tree: migrate+force+preserve → `status --check-footprint` exit `0`; default `sync` retains preserved bridge bytes |
| **stress** | Many differing shared assets (policy + cursor + bridge) all preserved in one migrate |
| **data-integrity** | Lock sha256 equals on-disk for preserved shared; kit-only digest excludes them; run-twice migrate identical |
| **performance** | Preserve path migrate completes under 5s on pilot footprint |
| **security** | Preserve path does not log file contents; path confinement unchanged; no secret tokens in report JSON |

---

## §PSA.9 — Definition of Done

- Flag implemented per §PSA.3–§PSA.4
- Seven-tier §PSA.8 green
- Freeze review **`pass`** + build verification **`pass`**
- Kit `docs/ROADMAP.md` + `docs/OVERSEER-HANDOVER.md` updated together
- No live consumer re-init; no secrets

---

## Review record

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| PSA-r1 | Freeze checklist + thinking (`thinking-high`) | **pass** | Stamp `sha256:c8f1eacc…` (2026-07-30). C8 file+line discipline present; §PSA.0–§PSA.9 complete; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. |
| PSA-BV-r1 | Build verification (`thinking-high`) | **pass** | Flag + classify + greenfield preserve match §PSA.3–§PSA.4; seven-tier §PSA.8 **28** green; evidence `test_output` sha256 `b4f5cde617a78e2c95c9bcb1ebd17b273bf84a6841661ad30f6976d25f2d05b7`. No live consumer re-init. |

### Evidence (PSA-BV-r1)

| type | sha256 | ref | notes |
| --- | --- | --- | --- |
| test_output | b4f5cde617a78e2c95c9bcb1ebd17b273bf84a6841661ad30f6976d25f2d05b7 | §PSA.8 seven-tier (28 passed) | unit+integration+e2e+stress+data-integrity+performance+security |
