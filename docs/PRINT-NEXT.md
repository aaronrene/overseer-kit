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

Git accepts the exact single closing commit containing these NEXT bytes; a later
commit requires explicit refresh. In a schema-3 collection, that exception also
requires the selected entry to have changed in the closing commit. Muse requires
the exact native revision and has no closing-commit exception; publish after the
work commit using explicit `--vcs muse --base-head sha256:...`. Mirror Git state
never determines Muse freshness. `sync` preserves NEXT and living documents. A missing or
invalid NEXT must be repaired explicitly; the reader never silently chooses another
repository or revives historical prompts. A copied config, NEXT, launcher or hook
must refuse if its repository/location bindings disagree.


For multiple declared repository-owned lanes, use `next --lane NAME` or
`next --all-lanes`. An unselected session shows labelled valid/missing/stale
entries and requires a lane choice before action. Bookends use the same service.
`next-write --lane NAME` updates only that entry with whole-file digest CAS;
unselected entries keep their revisions. `--batch-file` explicitly publishes
several accepted entries in one write. Schema-1/2 documents remain readable.
See [authority and lane operations](FPR-2-AUTHORITY-AND-LANES.md) for the strict
batch format, authority-change reset and native prerequisite contract.
