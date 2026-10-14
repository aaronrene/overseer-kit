# Canonical NEXT

Run `./cli/ok -C ROOT next` from this source installation. Each initialized checkout
has one persistent UUID and physical root in `.overseer/config.yaml` and one
`docs/NEXT.md`. The reader checks repository, branch, lane, model, action ID/kind,
head freshness and exact prompt digest before printing. It never writes, scrapes
ROADMAP/HANDOVER, regenerates a prompt, or executes the action.

`next-write` requires `--repo-id`, `--branch`, `--lane`, `--model`, `--action-id`,
`--action-kind`, `--expect-next` and a confined `--prompt-file`. Use the digest
reported by status, or `absent` to create a missing NEXT. Binding lines are generated
from metadata; do not put conflicting binding headers inside the prompt. The
writer atomically replaces a same-directory temporary file and fsyncs it and its
directory where supported. Concurrent stale writers refuse. A directory-fsync
failure after replace reports failure although a complete new file may be present.

The one closing commit containing the exact NEXT bytes is accepted; a later commit
requires explicit refresh. `sync` preserves NEXT and living documents. A missing or
invalid NEXT must be repaired explicitly; the reader never silently chooses another
repository or revives historical prompts. A copied config, NEXT, launcher or hook
must refuse if its repository/location bindings disagree.
