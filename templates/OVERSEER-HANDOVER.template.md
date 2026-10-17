# {{docs.handover_title}}

Repository: {{repo.name}}. This summary lives at {{docs.handover_path}}.
Keep it paired with {{docs.roadmap_path}}.
The sole action authority is canonical `docs/NEXT.md`; read it through the
repository-bound `.overseer/bin/ok -C /absolute/repository next`.

## Current state

Record the implemented behavior, validation evidence, failures and prerequisites.
Link evidence rather than copying an active prompt into this file.
When the accepted action calls for build verification, use
`/build-verification-review` and record its evidence and verdict separately from
author tests. Follow configured review requirements; do not infer an independent
review from author validation.

## Completed work

- Add dated outcomes and their commit/evidence references.

## Open decisions

- Record decisions the owner still needs to make; do not invent approval.

## Session close

Update both summaries. Publish one accepted successor with bound `next-write`,
current authority/revision and the expected whole-file NEXT digest. After the
closing commit, read `ok next` from disk and include its validated output.
Local commits, remote transport and release/deployment are separate actions.

<!-- overseer:change-log:start -->
<!-- overseer:change-log:end -->
