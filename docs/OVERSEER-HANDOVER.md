# Overseer Handover — Overseer Kit

**Living relay for kit development.** Paste the **NEXT SESSION** block into a fresh chat.

---

## NEXT SESSION — Operator live dogfood (K7.L1/L2)

**Date:** 2026-07-11  
**Current position:** **K7b DONE.** Footprint assets + regime-conditional resolver + executable
deploy script + seven-tier tests (**254** green). Kit repo remains **`git-only`** (footprint-first
per §K7.7). Operator flip (config/`AGENTS.md` + Muse bind + first bridge) is the next slice.  
**Model:** **Operator** (human-gated; not Auto)  
**Repo state:** merge `feat/k7-muse-git-mirror-dogfood` → `main`, then operator session on feature branch

### What just landed

| Slice | Deliverable |
| --- | --- |
| **K7b build** | `templates/MUSE-BRIDGE-WORKFLOW.template.md` + `templates/scripts/muse-bridge-deploy.sh.template` (S1–S13); `resolve_footprint` regime gate; `write_footprint_bytes` (`0755` on deploy script); `tokens.yaml`; `tests/fixtures/config-overseer-kit-dogfood.yaml`; `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md` |
| **Sync seed/conflict** | Default `sync` seeds absent bridge destinations; conflicts (exit `4`) when on-disk bridge files exist without lock baseline |
| **Tests** | Seven-tier K7 matrix (§K7.8): **254** passing |
| **Footprint-first held** | `.overseer/config.yaml` + `AGENTS.md` unchanged (`git-only` / planned) |

### THE ONE NEXT STEP — Operator live dogfood

| | |
| --- | --- |
| **ID** | **K7 operator** (D1–D8 + L1/L2) |
| **Runbook** | `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md` |
| **Ground truth** | `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md` §K7.2–§K7.4 |
| **Config matrix** | `tests/fixtures/config-overseer-kit-dogfood.yaml` (§K7.2.3) |
| **Hard stops** | No `muse bridge git-export --git-dir .`; no `git push origin main`; Tier-3 for `muse-mirror` → `main` merge |

### Paste-ready prompt — operator dogfood

```
Operator session: flip overseer-kit to muse+git-mirror per docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md
(D1–D8). K7b merged. Flip .overseer/config.yaml + AGENTS.md; Muse bind (D2); overseer sync (D5);
parity K7.P1–P10; first live bridge via ./scripts/muse-bridge-deploy.sh only (K7.L1). Record L1/L2
in handover. Never git-export on dev tree.
```

---

## Shared context (prepend to any phase prompt)

| | |
| --- | --- |
| **Project** | Overseer Kit — repo-agnostic governance vendoring CLI |
| **Read** | `docs/OVERSEER-KIT-SPEC.md`; target phase in `docs/ROADMAP.md`; this handover |
| **Guardrails** | No secrets; fail-closed VCS reads; no MuseHub-only baseline features; no Tier-3 automation |
| **Tests** | Seven tiers per `policy/test-tiers.yaml` before DONE |
| **Close** | Update ROADMAP + this handover together; feature branch → PR (no commit/push without consent) |

---

## Verified snapshot

| Area | State |
| --- | --- |
| **Kit version** | `0.1.0` (`VERSION`) |
| **K5a contract** | `docs/PHASE-K5-FREEZE-REVIEWER-CONTRACT.md` — reviewed → `pass` (round 3) |
| **K5b reviewer** | **Cleared** — K5b-r2 `pass` + fix on `main` (PR #6 / `b06ce17`) |
| **9A-5 governance-sync** | **DONE** — `overseer governance-sync [--dry-run]`; `tools/governance_hygiene/` |
| **K6a pilot matrix** | **DONE** — K6a-r7 `pass`; ground truth for K6b |
| **K6b pilot install** | **DONE** — migrate + seams + fixtures + quickstart + runbook; **224** tests at K6b close |
| **K7a dogfood freeze** | **DONE** — K7a-r2 `pass`; ground truth for K7b |
| **K7b dogfood build** | **DONE** — bridge footprint + resolver + tests + operator runbook; **254** tests green |
| **CLI** | `init [--migrate]` \| `sync [--include-preserved]` \| `status` \| `review --freeze` \| `governance-sync` |
| **Regime (this repo)** | Still **`git-only`** — operator flip (D3–D4) + L1/L2 pending |
| **Live pilots** | Not claimed PASS — operator runbook only; no consumer parity stamps |

## Change log

- **2026-07-11** — **K7b DONE (Auto).** Shipped regime-conditional bridge footprint
  (`MUSE-BRIDGE-WORKFLOW.md`, `scripts/muse-bridge-deploy.sh` S1–S13), `resolve_footprint` gate,
  executable write helper, `tokens.yaml`, `config-overseer-kit-dogfood.yaml` fixture,
  `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md`, seven-tier tests (254 green). Sync seed/conflict for new
  bridge destinations. Kit config/`AGENTS.md` remain `git-only`/planned (footprint-first). Next:
  **operator live dogfood** (K7.L1/L2).
- **2026-07-11** — **K7a-r2 `pass`.** Independent freeze review confirmed M1 + M2 + N1–N3 RESOLVED;
  full §K7.0–§K7.10 regress clean vs SPEC §4/§8, ROADMAP regime tiers, PHASE-K4 §K4.5, AGENTS.md.
  Cleared for **K7b**. No Build; no live muse export.
- **2026-07-11** — **K7a 1-fix.** Resolved freeze-review M1 + M2 + N1–N3 in
  `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`: S13 mirror publish; S7 `muse -C`; default-`sync`
  new-destination seed/conflict; §K7.1 footprint-first (config/`AGENTS.md` → operator); S11/S12
  quoted expansions. Handover + ROADMAP retargeted to **K7a-r2**. No Build.
- **2026-07-11** — **K7a-r1 `findings`.** Independent freeze review recorded M1 + M2 (MAJOR) and
  N1–N3 (MINOR). Not cleared for K7b.
- **2026-07-11** — **K7a DONE (Thinking).** Froze muse+git-mirror dogfood design in
  `docs/PHASE-K7-MUSE-GIT-MIRROR-DOGFOOD.md`: ordered flip steps, self-install config matrix,
  regime-conditional footprint (bridge workflow + tokenized deploy script with S1–S12 safety),
  parity gate K7.P1–P10 + operator L1/L2, no MuseHub-only core-capability guardrail, K7b
  seven-tier matrix. Auto default = footprint-first (kit stays `git-only` until operator session).
  No Build; no live muse export. Next was **K7a freeze-review**.
- **2026-07-11** — **K6b DONE (Auto).** Implemented `init --migrate` / `--include-preserved`,
  sync preserve+promote, kit-only digest + `origin` lock field, `vcs.muse.working_dir`,
  `root_relative_docs: "."` normalization, pilot fixtures, `GIT-ONLY-QUICKSTART.md`,
  `K6-PILOT-OPERATOR-RUNBOOK.md`, seven-tier tests (224 green on fixtures). No live consumer
  init; no gate flips; no K7 muse dogfood. Next: **K7a Thinking**.
- **2026-07-11** — **K6a-r7 `pass`.** Independent freeze review confirmed R6-M1 RESOLVED
  (sync-table + composition kit-only gloss = digest rule, incl. promoted living docs); R5-B1 /
  R4-B1 spot-check still RESOLVED; full §K6.0–§K6.10 regress clean. Cleared for **K6b**.
- **2026-07-11** — **K6a 6-fix.** Resolved freeze-review R6-M1 in
  `docs/PHASE-K6-PILOT-INSTALL-MATRIX.md` (sync-table + composition kit-only gloss aligned with
  digest rule: `origin: kit`, incl. promoted living docs). Handover retargeted to **K6a-r7**
  re-review → K6b.
- **2026-07-11** — **K6a-r6 `findings`.** Independent freeze review confirmed R5-B1 + R4-B1
  RESOLVED; recorded R6-M1 (stale sync-table “shared-asset” kit-only gloss vs digest rule).
- **2026-07-11** — **K6a 5-fix.** Resolved freeze-review R5-B1 (pre-promotion origin rule +
  `--force --include-preserved` promotion carve-out).
- **2026-07-11** — **K6a-r5 `blocked`.** Independent freeze review recorded R5-B1
  (absolute `origin: preserved` vs promotion path).
- **2026-07-11** — **K6a 4-fix.** Resolved freeze-review R4-B1 (living-doc origin rule:
  seed/unchanged/differs → `origin: preserved`).
- **2026-07-11** — **K6a-r4 `blocked`.** Independent freeze review recorded R4-B1.
- **2026-07-11** — **K6a 3-fix.** Resolved freeze-review R3-B1 + R3-N1.
- **2026-07-11** — **K6a-r3 `blocked`.** Independent freeze review recorded R3-B1 + R3-N1.
- **2026-07-11** — **K6a 2-fix.** Resolved freeze-review R2-B1 + R2-M1 + R2-N1.
- **2026-07-11** — **K6a-r2 `blocked`.** Independent freeze review recorded R2-B1 + R2-M1 + R2-N1.
- **2026-07-11** — **K6a 1-fix.** Resolved freeze-review B1 + M1–M5 + N1–N2.
- **2026-07-10** — **K6a-r1 `blocked`.** Independent freeze review recorded B1 + M1–M5 + N1–N2.
- **2026-07-10** — **K6a DONE (Thinking).** Frozen pilot install matrix + parity gates + migrate contract in `docs/PHASE-K6-PILOT-INSTALL-MATRIX.md`.
- **2026-07-10** — **9A-5 DONE.** Governance Hygiene Agent + seven-tier tests (181 green).
- **2026-07-10** — K5b-r2 **`pass`**. Cleared for 9A-5 Auto.
- **2026-07-10** — K5a round 3 `pass`; cleared for K5b Auto build.
