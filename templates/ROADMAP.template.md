# {{docs.roadmap_title}}

Repository: {{repo.name}}. Companion: {{docs.handover_path}}.
Read the current action with the bound `ok next`; canonical `docs/NEXT.md`
contains repository identity, lane, model, revision and the accepted action.

## Build queue

| Phase | Model | Status | Deliverable / evidence |
| --- | --- | --- | --- |
| **First slice** | Owner-selected | **TODO** | Define acceptance before implementation |

## Validation and dependencies

Record focused checks, combined validation and independent review separately.
Build verification: when required by the accepted action or configured gates,
record `/build-verification-review` evidence and the actual verdict before marking
the phase complete. Author checks do not supply independent review.
A missing prerequisite or failed check remains open. A local source package is
not a published release. Record explicit authority for remote and release actions.

## Change log

Keep this summary and the handover consistent. Publish successor text only via
`ok next-write`; neither this table nor a handover fence regenerates NEXT.
