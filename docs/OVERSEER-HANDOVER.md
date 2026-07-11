# Overseer Handover — Overseer Kit

**Living relay for kit development.** Paste the **NEXT SESSION** block into a fresh chat.

---

## NEXT SESSION — K7 Dogfood muse+git-mirror (Thinking first)

**Date:** 2026-07-11  
**Current position:** **K6b → DONE.** Pilot install seams, fixtures, quickstart, operator runbook,
and seven-tier tests are green on fixtures only. Live consumer inits remain operator-gated via
`docs/K6-PILOT-OPERATOR-RUNBOOK.md`. No gate flips. No K7 muse dogfood yet.  
**Model:** **Thinking (K7a outline)** then Auto (K7b)  
**Repo state:** `feat/k6-pilot-install` (merge to `main` before K7)

### What just landed

| Slice | Deliverable |
| --- | --- |
| **K6b CLI** | `init --migrate` / `--include-preserved`; sync preserve + promote; kit-only `footprint_digest`; `origin: preserved\|kit` |
| **K6b seams** | `vcs.muse.working_dir`; `root_relative_docs: "."` bare paths |
| **K6b fixtures** | `tests/fixtures/pilot/config-{scooling,knowtation,musehub,videofactory}.yaml` |
| **K6b docs** | `docs/GIT-ONLY-QUICKSTART.md`; `docs/K6-PILOT-OPERATOR-RUNBOOK.md` |
| **K6b tests** | Seven tiers green (**224** total) — fixtures only; no live consumer mutation |
| **Hard stops held** | No live init; no `--force --include-preserved` on live pilots; no gate flips; no kit muse dogfood |

### THE ONE NEXT STEP — K7 Thinking outline

| | |
| --- | --- |
| **ID** | **K7a** (Thinking) → **K7b** (Auto) |
| **Branch** | `feat/k7-muse-git-mirror-dogfood` (from updated `main` after K6b merge) |
| **Repo** | **overseer-kit** |
| **Ground truth** | `docs/OVERSEER-KIT-SPEC.md` §4/§8; ROADMAP K7 row; regime capability tiers |
| **Also read** | `docs/OVERSEER-HANDOVER.md`; `AGENTS.md` (K7 regime flip notes); `docs/PHASE-K6-PILOT-INSTALL-MATRIX.md` (out of scope: live pilots still operator-run) |
| **Hard stops** | No `git push origin main`; no staging push without Tier-3; MuseHub must only *deepen* capabilities — never make a core feature MuseHub-only |

### Paste-ready prompt — K7a (Thinking)

```
Phase K7a — Dogfood muse+git-mirror outline (overseer-kit).

Model: Thinking. Freeze WHAT/HOW for flipping this repo to MuseHub canonical + GitHub mirror.
Do not Build. Do not run live muse bridge export on the dev tree.

Read first:
- docs/OVERSEER-HANDOVER.md (shared context + this prompt)
- docs/ROADMAP.md (K7 row + regime capability tiers)
- docs/OVERSEER-KIT-SPEC.md §4 / §8
- AGENTS.md (planned muse+git-mirror regime)
- docs/PHASE-K6-PILOT-INSTALL-MATRIX.md (K6 live pilots are separate operator work)

Freeze: dogfood steps; footprint additions (MUSE-BRIDGE-WORKFLOW.template.md + tokenized
muse-bridge-deploy.sh); parity gate for kit self-install; seven-tier matrix for K7b;
guardrail that no core capability becomes MuseHub-only.
Update ROADMAP + OVERSEER-HANDOVER; await freeze-review pass before K7b Auto.
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
| **K6b pilot install** | **DONE** — migrate + seams + fixtures + quickstart + runbook; **224** tests green |
| **CLI** | `init [--migrate]` \| `sync [--include-preserved]` \| `status` \| `review --freeze` \| `governance-sync` |
| **Tests** | **224 passing** |
| **Branch** | `feat/k6-pilot-install` |
| **Live pilots** | Not claimed PASS — operator runbook only; no consumer parity stamps |

## Change log

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
