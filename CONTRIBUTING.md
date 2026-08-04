# Contributing to Overseer Kit

Thanks for helping improve 🆗 Overseer Kit — portable governance for AI-assisted
development. This guide covers how to propose changes safely.

## What belongs in this repository

Ship only product-facing material:

| In scope | Out of scope (do not commit) |
| --- | --- |
| CLI, adapters, templates, policy, tests | Personal Cursor/user-rule paste dumps |
| Public docs under `docs/` (and maintainer freezes under `docs/archive/phases/`) | Private sister-product pilot laundry / machine-specific runbooks |
| Landing static site under `docs/landing/` | Secrets, tokens, `.env*`, private signing keys |
| Contributor / security / license docs | Live posture flips, staging deploys, real payments |

Operator-local notes stay **off this tree**. If a doc is only useful on one private
machine or one private consumer deploy, it does not belong here.

## Before you start

1. Read [`README.md`](README.md) and [`docs/README.md`](docs/README.md).
2. Skim [`docs/OVERSEER-KIT-SPEC.md`](docs/OVERSEER-KIT-SPEC.md) — do not redesign frozen architecture inside a Build phase.
3. Prefer a **feature branch** for every change. Never push or merge directly to `main` without maintainer (Tier-3) authorization.
4. Security issues: follow [`SECURITY.md`](SECURITY.md) — do **not** open a public issue for undisclosed vulnerabilities.

## Development setup

Requires **Python 3.11+**.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Sanity
./cli/ok status
./cli/ok --help
```

`cli/ok` is the canonical POSIX entrypoint (`python -m cli.main`). The
`cli/overseer` shim remains for compatibility and prints a one-line deprecation.

## Making a change

1. Create a feature branch from current `main`.
2. Keep changes scoped. Match existing style; avoid drive-by refactors.
3. Update living governance docs **together** when a phase/status changes:
   - `docs/ROADMAP.md`
   - `docs/OVERSEER-HANDOVER.md`
4. Prefer `./cli/ok governance-sync --dry-run` before claiming docs match VCS reality.
5. Open a pull request against `main`. Describe intent, risk, and how you tested.

### Authority tiers (short form)

| Tier | Examples |
| --- | --- |
| **1 — do** | Feature-branch commits/pushes, tests, non-secret doc hygiene |
| **2 — recommend once** | Persistence / adapter contract shape (record the decision) |
| **3 — stop for maintainer** | Merge to `main`, live capability flips, secrets, real money, data deletion |

Full policy: `policy/tiers.yaml`.

## Tests (RULE #0)

New behavior needs coverage across the seven tiers in `policy/test-tiers.yaml`
where applicable: unit, integration, end-to-end, stress, data-integrity,
performance, security.

```bash
# Full suite
.venv/bin/pytest -q

# Focused
.venv/bin/pytest -q tests/security/
```

Do not mark a Build phase **DONE** on green tests alone when freeze/build gates
apply — maintainers run `/build-verification-review` (or `ok review` paths) per
kit policy.

## Docs map for contributors

| Doc | Role |
| --- | --- |
| [`docs/GIT-ONLY-QUICKSTART.md`](docs/GIT-ONLY-QUICKSTART.md) | Adopt with plain GitHub |
| [`docs/MIGRATE-EXISTING-REPO.md`](docs/MIGRATE-EXISTING-REPO.md) | `init --migrate` for repos that already have handover/roadmap |
| [`docs/CONSUMER-ADAPTER-PATTERN.md`](docs/CONSUMER-ADAPTER-PATTERN.md) | How a product repo plugs into the kit |
| [`docs/CHECK-OK.md`](docs/CHECK-OK.md) | Ad-hoc honesty / freeze + build verification paste |
| [`docs/archive/README.md`](docs/archive/README.md) | Maintainer archive map (phase freezes + vision) |

## Pull request checklist

- [ ] Feature branch (not direct-to-`main`)
- [ ] Tests updated or justified N/A for docs-only
- [ ] No secrets, absolute private paths, or `.env*` files
- [ ] ROADMAP + HANDOVER updated together when status changes
- [ ] SECURITY.md path used for vulnerability reports
- [ ] License remains **MIT** (`LICENSE`)

## Code of conduct expectation

Be respectful and constructive. Assume good faith. Maintainers may close PRs that
rewrite frozen contracts without a Thinking freeze, invent Tier-3 automation, or
introduce MuseHub-only baselines (every core governance feature must keep working
on `git-only`).

## Maintainers only

Repository visibility / DNS / signing-secret flips are **Tier 3**. Use
[`docs/PUBLIC-VISIBILITY-CHECKLIST.md`](docs/PUBLIC-VISIBILITY-CHECKLIST.md)
before making this repository public.
