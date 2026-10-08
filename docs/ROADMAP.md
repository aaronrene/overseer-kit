# Overseer Kit v1 roadmap

2026-10-08 — R1 local restoration is implemented. The complete intended v1 remains
incomplete and the preserved Git-only release candidate stays on hold. The owner's
[scope clarification](decisions/V1-SCOPE-RESET.md) authorizes local restoration
without a session-count ceiling and preserves two permanent operating choices:

- **Git/GitHub only:** standalone operation without Muse installed, a MuseHub
  account, network access for local handoffs, or forced migration.
- **MuseHub with a GitHub mirror:** explicitly selected Muse authority, followed
  by a controlled one-way distribution mirror. Local handoffs are implemented;
  mirror repair and publication verification remain pending.

| Milestone | State |
| --- | --- |
| Preserve original work and recovery snapshots | Complete; original Muse refs/state and Git edits preserved through R1 |
| Git status/init/sync/NEXT and confined atomic writer | Retained; existing requirements remain covered |
| Git-core architecture/build review, installation/rollback, authorized DINERO pilot | Closed; unchanged review and consumer work not repeated |
| Muse restoration audit and common-base reconciliation | Complete; 841/841 shared file bytes matched verified staging main |
| R1: Optional Muse-aware local status/NEXT and explicit adoption | Implemented and locally tested; exact results in validation |
| R2: Controlled mirror with reliable retry and source correspondence | Next; depends on R1 authority and local exclusion policy |
| R3: Isolated source reconciliation, integration review, combined installation/rollback | Planned; depends on R1/R2 |
| Authorized Muse-first publication and bounded consumer validation | Later gate; no remote writes or consumer activation authorized here |

R1 adds an explicit Git/Muse revision backend, schema-2 source-labelled NEXT,
Muse logical identity and runtime pins, physical linked-worktree selection,
expected Muse revision checks, and additive exclusions in both VCS systems.
`adopt --dry-run` previews a deliberate config change; apply preserves identity,
documents and application edits and saves the exact prior config. Tested rollback
restores that config, including when Muse is unavailable, while retaining safe
local exclusions. Authority changes require explicit `next-write`; they never
choose a new task. Existing schema-1 Git bindings remain valid and stay Git.

The [R1 validation record](validation/V1-RECOVERY.md#r1-optional-local-muse-handoffs-and-adoption--2026-10-08)
records **135 passed, zero failures, errors or skips in 132.34s**, together with
exact commands, corrections, runtime digest and limitations.
The [adoption guide](MIGRATE-EXISTING-REPO.md) documents the supported migration
inputs, reviewed exclusion policy, already-tracked-file refusal and rollback.
R1 covers local read commands on Muse code-domain repositories and registered
linked worktrees with Muse 0.2.1rc5 in a separate Python >=3.14 environment. It does
not certify native Muse mutation commands on linked worktrees, per-worktree staging,
full mode/symlink fidelity, or remote publication. Local publication state remains
`not_checked_offline`.

The completed [audit](validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08)
is the baseline for R2. Its unsafe deploy script/export behavior remains disabled
for real-project use: implicit source selection, early push, interrupted-push retry,
stale target content, mode projection, lost correspondence and hidden PR errors
still need repair. R2 must enforce exclusions on the actual export projection and
mirror, including historical tracked local files; ignore strings alone are not proof.
Prepare with native export `--no-push` only in an isolated context that cannot execute
inherited Muse/Git hooks. Validate source, target and snapshot before any separately
authorized publication.

R3 must start isolated Muse source reconciliation from verified staging main
`sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`,
then apply the reviewed recovery delta. Preserve the original checkout and release
worktree. Production Hub trust remains unresolved; do not switch hosts or reset
trust to bypass the recorded fingerprint refusal. No R1 remote or consumer access
occurred, and no automatic hooks or governance machinery were restored.

Only canonical `docs/NEXT.md`, published and validated through `next-write`, carries
the runnable next action. R1 closeout advances it to R2; this roadmap is a summary,
not an alternate prompt or a claim that the complete product is finished.
