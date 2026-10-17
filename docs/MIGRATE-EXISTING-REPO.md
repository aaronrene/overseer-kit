# Migrate an existing repository

Use the installation's bound CLI with the explicit physical repository root.
Preserve full configuration, repository/lane ownership, authored documents,
custom policies/skills/rules and existing NEXT. A real consumer migration needs
its own authorized task; restoration checks use disposable repositories.

1. Read `ok init --help`, capture identity/authority/runtime and quiesce writers.
2. Run `ok -C ROOT init --migrate --dry-run --json`. This reads the existing
   `.overseer/config.yaml`; it does not replace it from an arbitrary fixture.
3. Save and inspect the complete JSON plan, classifications, protected-file hashes,
   normalized settings and legacy prompt drafts. Use explicit `--refresh-runtime`
   in the preview only when adopting this installation's changed runtime.
4. Apply the exact saved plan with `init --migrate --apply-plan RELATIVE_PLAN_FILE
   --expect-plan PLAN_SHA256 --expect-config SOURCE_CONFIG_SHA256`. All values are
   emitted by the preview. The plan file must be inside the selected repository.
5. Inspect reported changes/backups and run `status --check-footprint`; explicit
   `sync --dry-run` then approved `sync --preserve-modified` records the full owned
   footprint while preserving custom files. Missing assets and integrity drift
   stay visible. Existing NEXT is never regenerated.
6. After a partial failure, inspect its report and backup before using the same
   plan/digests with `--resume`. Changed context or protected bytes still refuse.

A legacy HANDOVER prompt is a draft only. Accept a successor explicitly and publish
through bound `next-write` with the current authority/revision and expected whole-file
NEXT digest (`absent` only when absent). Do not promote preserved files with generic
force. See [source upgrade/rollback guidance](SOURCE-DISTRIBUTION.md) and
[authority and lanes](FPR-2-AUTHORITY-AND-LANES.md). Remote transport, publication and
release are separate actions.
