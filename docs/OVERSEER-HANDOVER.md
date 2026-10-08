# Overseer Kit v1 handover

2026-10-08 — R1 implements optional local Muse status/NEXT and explicit configuration
adoption. R2 mirror repair is next. The intended product remains incomplete; the
Git-only release candidate stays on hold. There is no session-count ceiling.
Git/GitHub-only operation remains a permanent supported mode without Muse installed,
a MuseHub account or automatic migration. The kit's eventual publication flow
remains Muse-first, with GitHub as its verified distribution mirror.

Recovery physical root: `overseer-kit-v1-recovery`;
branch `feat/overseer-v1-recovery`; repository name `overseer-kit`; UUID
`6dba88a5-029c-4136-9277-c3a0c81f31a6`. R1 started from clean Git HEAD
`64a1585c25bc40e62c9d0950b3b51604d49111b5`. The recovery checkout deliberately
remains Git-bound until isolated source reconciliation in R3. Its existing config
was explicitly synced after the runtime manifest changed; no authority conversion
or original Muse ref change occurred.

Runtime remains the unpublished candidate version `1.0.0`; the new runtime digest is
`379df92544be4722597b7ccecdf6a1efca1a181b1a852046172fd375c7fbe2cb`.
The manifest includes `v1_revision.py`, `v1_muse_reader.py`, and `v1_policy.py`.
Muse is optional and runs in its own venv, pinned to 0.2.1rc5 and a package-source
digest. Git-only Python support remains >=3.11; Muse's environment requires >=3.14.

R1 preserves physical root/UUID/lane/model checks, deterministic imports, canonical
NEXT, stale-digest refusal and the confined atomic writer. Muse freshness uses
that checkout's Muse branch/revision and logical repository ID. Mixed uninitialized
roots require explicit authority selection; existing Git bindings never convert.
Missing/malformed Muse state refuses without Git fallback. A small reader avoids
native CLI startup GC and legacy-stage deletion; it performs bounded local reads,
checks package/runtime pins and resolves linked-worktree HEAD from its registration.

`adopt --dry-run` previews schema/backend changes and tracked local files. Apply
preserves UUID, name, context, documents and application edits, saves exact previous
config bytes, and publishes config last. Existing NEXT stays unchanged and must be
republished for the new authority through `next-write`. Muse writes require explicit
`--vcs muse --base-head REVISION`. Rollback restores the preserved config while
retaining additive exclusions and later edits; restoring Git does not need Muse.
The [adoption guide](MIGRATE-EXISTING-REPO.md) describes supported schemas, explicit
isolated baseline import, ignore rules, partial-write behavior and rollback limits.

Local config, launcher, backup/input directory, NEXT and checkout-local editor
assets are excluded in both VCS systems. Tracked local bindings are reported and
block adoption; no automatic untracking occurs. Portable templates and living
summaries remain versionable. R2 still must enforce exclusions on real projected
snapshots and existing mirrors. A valid local NEXT never proves publication:
status reports `not_checked_offline`.

The [R1 validation entry](validation/V1-RECOVERY.md#r1-optional-local-muse-handoffs-and-adoption--2026-10-08)
records **135 passed, zero failures, errors or skips in 132.34s**: 105 Git/core
tests and 30 real Muse tests. It includes corrections, commands and limitations. Logs and JUnit results
are in `../RECOVERY-RUNS/20261008-muse-restoration-r1/`. Fixtures cover standalone Git
without Muse, Muse-only/mixed roots, linked worktrees, copied bindings, wrong context,
Muse freshness, malformed/missing state, bounded responses, concurrent CAS writes,
read-only behavior, exclusion enforcement, isolated native Git import and config
adoption/rollback. The historical test inventory remains intact. No unchanged
closed Git-core review was repeated; this is implementation verification, not an
independent integration review or final-v1 approval.

The clean release worktree remains at `06f988e5a078ede81c9dc664520833980a9a19a3`
on `release/overseer-v1.0.0`. Original Muse HEAD/refs/config/identity/bridge records
and original Git edits remain unchanged. Recovery snapshots remain intact. No
consumer, including DINERO, was accessed. No real-project mirror, remote write,
automatic hook activation, OCI or replacement governance machinery was introduced.

R2 uses the completed audit and R1 as its baseline. Repair source/destination
pinning, physical target confinement, clean-target/exact-content checks, modes,
exclusions and hook isolation before export publication. Native `--no-push` alone
does not disable hooks. Separate prepare/verify/publish, preserve source-to-Git
correspondence on no-change runs, retry incomplete delivery, and expose push/PR
failures truthfully with explicit GitHub context. Use disposable local fixtures;
real remote writes still require separate authority.

R3 follows with an isolated Muse branch from verified staging revision
`sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`,
reviewed recovery delta, independent integration review and combined installation/
rollback. The staging/Git main 841-file parity audit remains the common-base evidence.
Production Hub trust/state and publication permissions remain unverified. Do not
reset trust, copy the dirty original tree, or publish the held release candidate.

Native Muse linked-worktree mutations and separate staging isolation are not
validated by R1's correct local reader. Dirty status covers regular file content
and shared stage state, not complete mode/symlink fidelity. Historical governance
configs and relocated bindings need separate reviewed conversion. These limits
remain explicit rather than silently falling back to Git.

Canonical NEXT advances through `next-write` to `OVERSEER-V1-MUSE-RESTORATION-R2`,
kind `implement`, GPT-6 Astra with Extra High reasoning. Read it from disk with
`./.overseer/bin/ok next`; this summary supplies context, not another runnable task.
