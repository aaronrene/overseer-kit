# Overseer Kit v1 handover

2026-10-08 — R2 controlled mirror preparation and reliable retry are implemented
and locally tested. R3 source reconciliation and combined validation follow. The
complete intended product remains unfinished; the Git-only release candidate stays
on hold. There is no session ceiling. Git-only is a permanent supported mode with
no Muse installation, account or automatic conversion. The kit's intended eventual
publication remains Muse-first with verified GitHub distribution.

Recovery physical root: `overseer-kit-v1-recovery`; branch
`feat/overseer-v1-recovery`; repository name `overseer-kit`; UUID
`6dba88a5-029c-4136-9277-c3a0c81f31a6`. R2 started at clean Git HEAD
`99a13c0e4ff73fa42b5901d73f69705b454b7ba2`. Recovery remains Git-bound; real source
reconciliation is R3 work. No original Muse ref was changed.

Runtime remains unpublished candidate `1.0.0`; digest changed from R1
`379df92544be4722597b7ccecdf6a1efca1a181b1a852046172fd375c7fbe2cb` to
`90e179326877edc25263f0f1e1597c6b4067c09e64d03565e0b828d07640ccc6`.
The manifest adds both mirror modules and the deployed/template wrapper. An actual
runtime-change refusal, read-only sync preview, explicit sync, status and NEXT
readback passed; sync preserved Git authority, UUID and living documents.

R1's pinned optional Muse reader, source-labelled NEXT and explicit adoption remain
in place. Existing bindings never silently change authority. Adoption preserves
config history/documents/edits, supports rollback, and refuses tracked local assets.
Both local VCS modes stay offline; valid NEXT does not establish Hub acceptance or
GitHub delivery. See the [adoption guide](MIGRATE-EXISTING-REPO.md).

R2's [mirror workflow](../MUSE-BRIDGE-WORKFLOW.md) replaces implicit deploy behavior
with a reviewed plan, exact raw digest, and `mirror prepare`, `verify`, `deliver`.
Source main, immutable revision, logical source ID, Hub URL, physical target,
GitHub repository, branches and expected heads are explicit. Preparation is offline
and accepts only an absent isolated target or its own dedicated bare Git target.
Foreign content, development/linked Git worktrees, aliases/overlap, inherited hooks,
stale heads, missing blobs and unsupported modes refuse before publication.

The engine reads actual native Muse objects through the R1 environment and builds
Git trees directly. It avoids the native exporter's hook execution, source bridge
writes, missing-blob skipping, implicit staging and shebang mode guesses. Actual
projected paths/bytes/modes are compared, including R1 exclusions of historical
local bindings. Templates and living summaries survive. Git executable modes come
from an explicit reviewed list; other POSIX permissions are normalized. Symlinks,
hardlinks and special bits are unsupported; empty directories are reported/omitted.

One source-local correspondence record binds one pair. Source/plan commit trailers
and exact parent/tree checks recover interrupted recording. Identical retry keeps
the Git SHA and record bytes. A same-content new source gets a correspondence commit.
Delivery observes approved Hub identity/revision and the expected Git remote head,
uses non-force distribution-branch push, verifies readback and checks PR state with
explicit repository/head/base context. Export, authority, push and PR outcomes are
separate. Interrupted pushes and failed PR creation remain retryable without false
success or repeating a verified push.

All delivery tests used recording transports, with real local Muse and Git objects.
No real remote writes or read probes were needed. The adapter's public staging JSON
refs protocol, live authentication/rights and remote write lifecycle remain
unvalidated. Private MuseHub and unresolved production trust are unsupported;
there is no fingerprint reset, login or host fallback. Existing legacy mirrors are
refused and need explicit isolated reconciliation before use.

**Final combined suite: 201 passed, zero failures/errors/skips in 261.42s.**

The [R2 validation entry](validation/V1-RECOVERY.md#r2-controlled-mirror-preparation-and-retry--2026-10-08)
records the full supported suite, **66 new mirror cases**, earlier
failures/corrections, runtime sync and preservation evidence. Raw logs/XML and
closeout readbacks live in `../RECOVERY-RUNS/20261008-muse-restoration-r2/`.
The historical test inventory is preserved. Closed unchanged Git-core reviews were
not repeated; this is implementation validation, not independent review or finish.

The release worktree remains clean at `06f988e5a078ede81c9dc664520833980a9a19a3`,
branch `release/overseer-v1.0.0`. Original Muse HEAD/refs/config/identity/bridge
records and original Git working edits remain unchanged. No consumer, real-project
mirror, remote write, automatic hook, OCI or replacement governance system ran.

R3 starts isolated source reconciliation from verified staging
`sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6`,
using the reviewed recovery delta from `d47291d5d9030de5ebef713da95efa978c4d8c6e`.
Preserve the original and release trees; do not copy dirty original working files.
Compare every intended file/exclusion/mode, address supported Git/Muse CI, independently
review the changed integration, and test combined installation/migration and
current/previous rollback with a no-hooks fixture lifecycle. Native Muse linked
worktree mutations/stage isolation remain outside R1/R2 evidence. Production trust,
remote publication and consumer validation retain separate authorization boundaries.

Canonical NEXT advances through `next-write` to `OVERSEER-V1-MUSE-RESTORATION-R3`,
kind `implement`, GPT-6 Astra with Extra High reasoning. Read it from disk with
`./.overseer/bin/ok next`; this summary contains no alternate executable prompt.
