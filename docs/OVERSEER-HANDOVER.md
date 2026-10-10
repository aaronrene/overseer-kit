# Overseer Kit v1 handover

## Recovery and documentation publication complete — 2026-10-10

[PR #87](https://github.com/aaronrene/overseer-kit/pull/87) merged successfully as
`8b519ab9e44e7f7738ede815d21d6f319b0c9d78`. Documentation publication is complete.
Automatic Cloudflare production deployment `c3a1baaf-203c-475b-b6b9-2591a34ddc19`
succeeded for that commit and became canonical for `overseerkit.com`.
[Post-merge CI](https://github.com/aaronrene/overseer-kit/actions/runs/38060695412)
passed **156 / 156 / 289 tests** (Python 3.11 Git / Python 3.14 Git / Muse), with
zero failures, errors or skips. No recovery task remains.

[v1.0.0-rc.1](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1),
release ID `408458432`, and its five assets remain unchanged. It is a prerelease,
not stable and not Latest. Its tag remains at
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`; GitHub main is newer because it includes
the later documentation closeout. Source metadata reporting `1.0.0` does not imply
a stable release. The [installation and rollback guide](releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md)
and [release closeout](decisions/V1-RELEASE-PUBLICATION.md) identify the frozen assets.

## Public product and operating choices

Overseer Kit v1 is a small local command-line tool with one trusted NEXT per
repository. Its seven public commands are `status`, `init`, `sync`, `adopt`,
`mirror`, `next` and `next-write`. Git-only operation is permanently supported
without Muse installation or an account. Muse-only and Muse with a controlled
GitHub mirror are explicit per-repository choices.

The [README](../README.md), [documentation index](README.md),
[Git-only quickstart](GIT-ONLY-QUICKSTART.md) and
[controlled bridge workflow](../MUSE-BRIDGE-WORKFLOW.md) describe current use.
The static website is informational and does not run Overseer. Hooks are optional
and off by default. The CLI does not choose or execute tasks, merge automatically,
release automatically or deploy automatically.

## Retained evidence and limits

Earlier reviews, source installation/rollback and the authorized pilot are closed
at their recorded scope. [Public evidence](validation/V1-PUBLIC-EVIDENCE.md) links
actual release and CI identities. The [recovery record](validation/V1-RECOVERY.md)
retains dated history; its earlier pending-work statements are superseded by this
closeout. ROADMAP and HANDOVER are summaries; only checkout-local `docs/NEXT.md`,
published through `next-write`, supplies the task.

The optional Muse runtime is the pinned Overseer recovery build of `0.2.1rc5`,
not an upstream release. Its exact pins and immutable artifact URL are unchanged.
The known native clone limitation omitted 19 empty directories while preserving
all 861 rc.1 file bytes. Muse snapshots do not encode POSIX modes; controlled
mirroring enforces the reviewed executable list. Untested platforms, relocation,
and broader consumer rollout are not established by these results.
