# Example consumer — custom living-doc names (public stub)

This stub shows how a consumer repo can rename roadmap/handover files via
`.overseer/config.yaml` without forking the kit. VideoFactory was an early
`git-only` pilot; domain packs and verify scripts stay in the consumer repo.

## Doc mapping pattern

| Kit concept | Example consumer filenames |
| --- | --- |
| Roadmap / phase queue | `VIDEO_PRODUCTION_STATUS_BOARD.md` (or any path in config) |
| Handover / session relay | `VIDEO_OVERSEER_HANDOVER.md` |

Set `docs.handover`, `docs.roadmap`, and optional titles in `.overseer/config.yaml`.

## Install (pattern only)

```bash
KIT=/path/to/overseer-kit
REPO=/path/to/your-repo

$KIT/cli/ok -C $REPO init --migrate \
  --from-config $KIT/tests/fixtures/pilot/config-videofactory.yaml \
  --non-interactive --dry-run
```

Live apply remains **operator-gated**. Never `--force --include-preserved` on a
production consumer without Tier-3 review.

## Adapter pattern

`docs/CONSUMER-ADAPTER-PATTERN.md`

Migrate / fixture path: `docs/MIGRATE-EXISTING-REPO.md` and
`tests/fixtures/pilot/config-videofactory.yaml`.

## Print NEXT on closeout

After any update to the living handover and/or roadmap, print the paste-ready fence via
`ok next` (or `ok governance-sync --print-next`) so the operator’s next chat paste matches
disk — not an open tab. See `docs/PRINT-NEXT.md`.
