# Canonical NEXT

For manual current-prompt display, select the project and lane and run that
project's bound reader:

```sh
/absolute/project/.overseer/bin/ok -C /absolute/project next --lane product
```

Replace the path and lane with the selected project's actual context. The
validated output contains the current saved prompt and its recommended `Model:`;
copy the entire returned block verbatim. In an already running bound browser,
the **Next / Handover** tab's NEXT control displays the same validated result.
Confirm the project context before using it. Refusal means report the error,
not use an older display or reconstruct a prompt from summaries.

Read at entry and before each new task. At closeout, publish the actual next
unfinished authorized task through `next-write`, make the closing commit, then
read and display the fresh validated prompt and model again. If approved work
is complete, publish a `stop` stating completion with no invented next task.
The [current scope](decisions/CURRENT-PROMPT-DISPLAY-SCOPE.md) excludes automatic
Cursor events, vendor execution protection and shared-chat investigation.

## One small task, from start to handover

For example, use an already initialized Git project to improve one documentation
page. No new installation is needed.

1. **Read first.** Run the project's bound `next --lane product` reader above.
   Check the project, branch, lane and model, and display the returned prompt
   verbatim. If it refuses, report the refusal and resolve it explicitly.
2. **Confirm the task's authority.** A valid `stop` means no work is queued.
   A new owner instruction can authorize a new task; the stop itself cannot.
   When saving that task, use bound `next-write` with the current context and
   the whole-file digest from `status --json`, then read it back before work.
3. **Make the small change.** Stay within the authorized repository and scope.
   For a documentation edit, check the wording and links and run
   `git diff --check`. Update ROADMAP and HANDOVER together when the milestone
   changes; keep them as summaries rather than separate task instructions.
4. **Publish the handover.** Use bound `next-write` with the current digest and
   explicit context to save the next unfinished authorized task. If the task is
   finished and nothing else is authorized, save an `action-kind stop` saying so.
   For Git, include that NEXT publication in the single closing commit.
5. **Read after the commit.** Run the same bound reader and display its exact
   prompt and recommended model. Check that it names the intended project and
   reports the actual remaining work or completion stop. Report the checks and
   commit to the owner. Do not treat the completed task as pending again.

This demonstrates the explicit manual workflow. It does not establish automatic
editor events, qualify a new release or authorize installation into another repo.
Muse's publication order differs; see the revision rules below.

## Reader and writer reference

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
