# Current full-product restoration

For current source authority and the dated recovery evidence retained from PR #97,
see [repository status and preserved reconciliation history](REPOSITORY-STATUS.md)
and the [eventual MuseHub migration decision](decisions/MUSEHUB-CANONICAL-ROADMAP.md).
A copied source binding/NEXT must identify the selected physical checkout before
its historical task can be used.

Start with [source quickstart](V1-QUICKSTART.md), [maintained surfaces](FPR-3-PRODUCT-SURFACES.md), [source distribution](SOURCE-DISTRIBUTION.md), and [FPR-3 evidence](validation/FPR-3-SURFACES.md). Canonical `docs/NEXT.md` is the sole action source. Older phase pages below describe their historical scope, not current release readiness.

# Overseer Kit — public docs

Portable governance for AI-assisted development. Start here; deeper history lives
under [`archive/`](archive/README.md).

## Start

| Doc | When to read |
| --- | --- |
| [Git-only quickstart](GIT-ONLY-QUICKSTART.md) | Adopt with plain GitHub (`ok init`) |
| [Migrate existing repo](MIGRATE-EXISTING-REPO.md) | `ok init --migrate` when living docs already exist |
| [Check OK](CHECK-OK.md) | Ad-hoc honesty / freeze + build verification |
| [Consumer adapter pattern](CONSUMER-ADAPTER-PATTERN.md) | How a product repo plugs into the kit |
| [Overseer Kit spec](OVERSEER-KIT-SPEC.md) | Frozen architecture (maintainers + serious adopters) |

## Day-to-day product surfaces

| Doc | Role |
| --- | --- |
| [Desktop operator runbook](TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md) | Mac console / `ok app` |
| [Stage 3 upgrade runbook](TRACK-O-STAGE3-UPGRADE-OPERATOR-RUNBOOK.md) | `muse-only` → `muse+git-mirror` |
| [Normie custody contract](TRACK-O-NORMIE-CUSTODY-PRODUCT-CONTRACT.md) | Stages Start → Work → backup → optional bind |
| [Hosted dashboard runbook](HOSTED-GOVERNANCE-DASHBOARD-OPERATOR-RUNBOOK.md) | Read-only remote glance |
| [K7 Muse dogfood runbook](K7-DOGFOOD-OPERATOR-RUNBOOK.md) | Kit’s own `muse+git-mirror` substrate |
| [Landing hosting](landing/HOSTING.md) | Static site (`overseerkit.com`) |

## Living governance (this repo dogfoods the kit)

| Doc | Role |
| --- | --- |
| [ROADMAP.md](ROADMAP.md) | Phase board |
| [OVERSEER-HANDOVER.md](OVERSEER-HANDOVER.md) | Current summary; canonical NEXT requires a valid repository binding |

## Sister / consumer products

Optional example consumers keep **thin public stubs** under [`consumers/`](consumers/).
Use [`MIGRATE-EXISTING-REPO.md`](MIGRATE-EXISTING-REPO.md) and
`tests/fixtures/pilot/` for install-shaped examples. Domain packs and verify
scripts **never** live in this kit.
