# K6 Pilot Operator Runbook

Live consumer installs are **operator-gated**. K6b kit work uses fixtures only.
Do not run these steps against a production tree without explicit consent for a
**named** repo.

**Hard stops (never during pilot):**

- `--force --include-preserved` on live consumers
- Merge pilot PRs to consumer `main` / Muse canonical main without review
- `muse push staging`, staging deploy, live env/gate flips
- Retire hand-maintained handover/roadmap upkeep before parity PASS + sign-off
- Dogfood `muse+git-mirror` on overseer-kit itself (that is **K7**)

## Install order (one repo at a time)

1. Scooling (`muse+git-mirror`) — setup: `docs/consumers/scooling/OVERSEER-SETUP.md`
2. Knowtation (`muse+git-mirror`) — setup: add `docs/consumers/knowtation/` when piloted
3. MuseHub (`muse-only`) — requires `vcs.muse.working_dir` seam + `adapter.status()` OK
4. VideoFactory (`git-only`) — setup: `docs/consumers/videofactory/OVERSEER-SETUP.md`

Do not start the next consumer until the previous step’s kit-side fixture tests
are green **and** (for live runs) the previous parity gate is PASS or explicitly
deferred with a written reason in that consumer’s change log.

## Prepared configs

Copy from `tests/fixtures/pilot/`:

| Consumer | Fixture |
| --- | --- |
| Scooling | `config-scooling.yaml` |
| Knowtation | `config-knowtation.yaml` |
| MuseHub | `config-musehub.yaml` |
| VideoFactory | `config-videofactory.yaml` |

Substitute the real install root via `-C` only — fixtures must not contain absolute machine paths.

## Per-consumer steps

1. Open a feature branch under that repo’s VCS rules (`feat/overseer-k6-pilot` or Muse equivalent).
2. Optionally dry-run first:

   ```bash
   ./cli/ok -C <repo-root> init --migrate --from-config <prepared.yaml> --non-interactive --dry-run
   ```

3. Apply migrate (**never** pass `--force --include-preserved`):

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

   Evaluate universal criteria P1–P7 and per-repo extras in
   `docs/PHASE-K6-PILOT-INSTALL-MATRIX.md` §K6.6.

6. On PASS: record stamp + change-log line; **leave** hand process in place until
   explicitly retired in a later session.
7. Open PR / Muse proposal for review; **do not** auto-merge.

## Knowtation extra

Before replacing `.cursor/rules/no-docs-only-pr-to-main.mdc`, confirm KN-R1–R3
(rule present; semantic parity after token render; byte-identity not required).
On KN-R2 PASS, migrate classifies that rule as `updated` without `--force`.

## MuseHub extra

Confirm MH-G1–G4 (git forbidden; `working_dir` status succeeds) before treating
parity as PASS.

## VideoFactory extra

Confirm bare paths `OVERSEER_HANDOVER.md` / `ROADMAP.md` and that non-kit
`.cursor/rules/*` remain after migrate.
