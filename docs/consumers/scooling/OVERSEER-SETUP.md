# Scooling — overseer kit setup

Use the same overseer discipline as other repos. Scooling is the **first** K6 pilot consumer
(`muse+git-mirror`): richest policy source, coordination-log owner, and reference home for the
9A multi-agent runtime (`src/phase9a/` — product code, **not** vendored by the kit).

## Doc mapping (same system, standard names)

| Kit concept | Scooling file | Notes |
| --- | --- | --- |
| Roadmap / phase queue | `docs/ROADMAP.md` | Kit default |
| Handover / session relay | `docs/OVERSEER-HANDOVER.md` | Kit default |
| Standing decisions / coordination | `docs/CROSS-REPO-COORDINATION.md` | SD log lives here; preserved on migrate |

**Renaming is supported** via `.overseer/config.yaml` (`docs.handover`, `docs.roadmap`, titles).
Scooling pilots should keep kit default names unless a later freeze changes that.

## What the kit owns vs what Scooling owns

| Layer | Kit (after `ok init` / `ok sync`) | Scooling (stays in this repo) |
| --- | --- | --- |
| **L0** | Templates, policy, Cursor rules/skills, CLI invoke via kit path | Living docs content, Muse+Git remotes |
| **L1** | `verify-step` orchestrator | `policy/checkpoints.yaml`, `scripts/verify/*` (when adopted) |
| **L2** | Ledger + honesty-status engines | Hook call sites / domain DoD (when enabled) |
| **Runtime** | — | `src/phase9a/` overseer router (reference only in kit `AGENTS.md`) |
| **Desktop / `ok app`** | Lives in overseer-kit only | Point `OVERSEER_REPO_ROOT` at Scooling if using Tauri/`ok app` |

## Prepared config

Fixture (no absolute machine paths):

`tests/fixtures/pilot/config-scooling.yaml`

Regime: `muse+git-mirror`, canonical Muse, git `origin` / `muse-mirror` bridge.

## Install (kit-side dry-run vs live)

Live install is **operator-gated** (Tier 3 against the consumer tree). From the **overseer-kit**
checkout:

```bash
KIT=/path/to/overseer-kit
REPO=/path/to/scooling

# Dry-run first (migrate preserves existing living docs)
$KIT/cli/ok -C $REPO init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-scooling.yaml \
  --non-interactive --dry-run

# Apply on a feature branch — only with explicit operator consent
$KIT/cli/ok -C $REPO init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-scooling.yaml \
  --non-interactive

$KIT/cli/ok -C $REPO status --check-footprint
$KIT/cli/ok -C $REPO governance-sync --dry-run
```

**Never** on live Scooling:

- `--force --include-preserved`
- Merge to Muse/`main` without Tier-3 review
- `muse push staging` / live gate flips

Full order and parity criteria: `docs/K6-PILOT-OPERATOR-RUNBOOK.md` and
`docs/PHASE-K6-PILOT-INSTALL-MATRIX.md` (SC-P1, SC-P2, universal P1–P7).

## Scooling parity extras (SC)

| ID | Expectation |
| --- | --- |
| SC-P1 | `docs.coordination` resolves; standing_decisions points at coordination; coordination file preserved |
| SC-P2 | Regime `muse+git-mirror`; bridge marker present; D2 dry-run path reachable without apply |

## Mandatory review gates (kit-wide)

Shipped via templates + `.cursor/rules/build-verification-required.mdc`:

| Gate | When | Skill / command |
| --- | --- | --- |
| Freeze review | Before Auto build | `/freeze-review-loop` · `ok review --freeze` |
| Build verification | After Auto, before DONE | `/build-verification-review` |
| Tests | During/after build | `policy/test-tiers.yaml` |
| Governance sync | Session end | `/governance-sync` · `ok governance-sync` |

## Day-to-day (Scooling)

1. Open `docs/OVERSEER-HANDOVER.md` → paste NEXT prompt into any AI session.
2. Work on `feat/<slug>` (or Muse feature branch per regime).
3. Thinking → freeze → review; Auto → build → seven-tier tests → build verification.
4. Update ROADMAP + HANDOVER together → `ok governance-sync --dry-run` → commit.
5. PR / Muse proposal → merge only with Tier-3 authorization.
6. Prefer Muse commit before Git when both histories are in play (KH2 muse-sync gate).

## Day-to-day without Cursor

Scooling does **not** require Cursor. Docs + `ok` CLI are the portable path (any chatbot paste).
Cursor rules/skills are an optional boost when the footprint is installed.

## Relation to Knowtation / MuseHub / normies

| Question | Answer |
| --- | --- |
| Does kit install create a Scooling user account? | **No** |
| Does Scooling install create a Knowtation vault? | **No** — separate product |
| Muse without Git? | Possible via `muse-only` regime in **other** products; Scooling dogfood is `muse+git-mirror` |
| Normie custody path (Start → Work → optional GitHub backup → optional Knowtation bind) | **Track O** — normative product contract: `docs/TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md` (freeze: `docs/PHASE-TRACK-O-O0-NORMIE-CUSTODY-FUNNEL.md`). Scooling is an **optional** entry product, never required for kit custody. Stage 3 kit upgrade ceremony remains deferred to O2. |
| Knowtation Stage 4 stub | `docs/consumers/knowtation/OVERSEER-SETUP.md` (no live Knowtation `ok init` in O1) |

## Hard stops

- No live `init` without named-repo operator consent
- No `--force --include-preserved` on live migrate
- No merge to canonical `main` without Tier 3
- No inventing Scooling product/runtime APIs inside overseer-kit
