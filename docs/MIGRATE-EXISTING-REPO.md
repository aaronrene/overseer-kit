# Migrate an existing repo (`ok init --migrate`)

Use this when a consumer already has hand-authored handover/roadmap (or other
living docs) and you want Overseer Kit without clobbering them.

Live installs against production trees are **operator-gated**. Kit CI and
day-to-day development use fixtures under `tests/fixtures/pilot/` only.

## Hard stops

Never during a migrate session:

- `--force --include-preserved` on a live consumer without explicit written consent
- Merge migrate PRs to consumer `main` / Muse canonical main without review
- `muse push staging`, staging deploy, or live env/gate flips
- Retire the consumer’s previous hand process before parity PASS + sign-off
- Dogfood `muse+git-mirror` on this kit itself via consumer migrate steps (that is
  kit-operator work — see `docs/K7-DOGFOOD-OPERATOR-RUNBOOK.md`)

## Prepared example configs

Copy from `tests/fixtures/pilot/` and pass the real install root with `-C` only —
fixtures must not gain absolute machine paths.

| Example | Fixture |
| --- | --- |
| Scooling-shaped | `config-scooling.yaml` |
| Knowtation-shaped | `config-knowtation.yaml` |
| MuseHub-shaped | `config-musehub.yaml` |
| VideoFactory-shaped | `config-videofactory.yaml` |

Thin public boundary stubs: `docs/consumers/*/OVERSEER-SETUP.md`.
Adapter pattern: `docs/CONSUMER-ADAPTER-PATTERN.md`.

## Steps

1. Open a feature branch under that repo’s VCS rules.
2. Optionally dry-run:

   ```bash
   ./cli/ok -C <repo-root> init --migrate --from-config <prepared.yaml> --non-interactive --dry-run
   ```

3. Apply migrate (**never** pass `--force --include-preserved` by default):

   ```bash
   ./cli/ok -C <repo-root> init --migrate --from-config <prepared.yaml> --non-interactive
   ```

4. Check footprint:

   ```bash
   ./cli/ok -C <repo-root> status --check-footprint
   ```

5. Parity probe:

   ```bash
   ./cli/ok -C <repo-root> governance-sync --dry-run
   ```

   Universal criteria and historical matrix live in
   `docs/archive/phases/PHASE-K6-PILOT-INSTALL-MATRIX.md` §K6.6.

6. On PASS: record a change-log line; leave the previous hand process in place
   until an explicit later retirement.
7. Open a PR / Muse proposal for review; **do not** auto-merge.

## Regime extras (when applicable)

| Regime shape | Confirm before PASS |
| --- | --- |
| Knowtation-shaped `no-docs-only-pr` rule | Semantic parity after token render (byte-identity not required) |
| MuseHub `muse-only` | Git forbidden; `vcs.muse.working_dir` status succeeds |
| VideoFactory docs-at-root | Bare `OVERSEER_HANDOVER.md` / `ROADMAP.md`; non-kit `.cursor/rules/*` retained |
