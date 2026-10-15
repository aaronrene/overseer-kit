# FPR-OPS-1 distinct-route restoration capture

**Distinct routes did not converge in the selected custom-editor harness. An
explicitly injected workspace/task mismatch reached the client's outgoing
`thread/resume` request.** Neither result establishes the historical restoration
cause or clears the incident. FPR-OPS-1 remains a qualification blocker.

This is the single experiment authorized as
`OVERSEER-FPR5-OPS1-RESTORE-REPRO-1`, performed on 2026-10-15 by the bounded
investigation author, not an independent adjudicator. The completed
[prior investigation](FPR-5-HANDOFF-RELIABILITY.md), seeded propagation result,
original findings/failures and all their limitations remain unchanged.

## Verified boundary and execution

Entry was clean at `9653a4b43f14a7b918b8162f17e46274f46d7ba6`, physical/Git root
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, repository `overseer-kit`, UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`, lane `product`. Bound NEXT validated the
prior stop action; the current owner request supplied this experiment's authority.
[Opening verification](fpr5-restore-repro/opening-verification.json) records
unchanged membership/hashes for 295 runtime, 440 test, 40 native, ten packaging,
four validation-driver and two requirements entries. Runtime remains
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.

[reproduce.mjs](fpr5-restore-repro/reproduce.mjs) ran **once**, with **one**
persistence/restore cycle, exit code 0 and empty stderr. The
[command record](fpr5-restore-repro/reproduction-command.json) records
15:49:07.979225–15:49:09.990278 UTC. The
[complete captured result](fpr5-restore-repro/reproduction-result.json) retains
inputs, persisted state, restored selections, chronological events and outgoing
request fields. Two new Git repositories with distinct fixture UUIDs and two
mock threads were created under an empty temporary directory. Its repositories
and backing state were removed in `finally`; only sanitized evidence remains.
No prior reproduction, suite, review, pilot or failed launch was repeated.
This capture is not added to acceptance-test counts.

## Actual code and host API boundary

Read-only installed source is Cursor 3.24.18 and Codex extension 26.908.40401,
matching the prior version labels. The extension/renderer bundle hashes still
match the earlier source map. Newly pinned Cursor workbench and extension-host
bundles are recorded with exact UTF-8 ranges in the
[host source map](fpr5-restore-repro/restore-source-map.json). These are current
installed bytes, not incident-time byte attestation.

The [host adapter](fpr5-restore-repro/restore-host.mjs) executes installed
custom-editor serialization (`ntn`/`vqn`), editor-group serialization and MRU
selection (`oNe`), grid serialization/traversal, editor-part state save/load,
workspace-scoped memento caching and storage IPC, followed by native tab DTO
creation and extension-host tab hydration. Fresh code/state objects restore
the saved bytes. The native memento key is
`memento/workbench.parts.editor`, containing `editorpart.state`; the actual
storage client sends the distinct workspace IDs to the stub storage channel.
Both windows share a fixture code context within each phase to exercise the
workspace memento separation. This does not establish that real windows share
a JavaScript realm.

The [extension adapter](fpr5-restore-repro/extension-host.mjs) executes the
installed restored-tab enumerator, URI parser, custom-editor resolver,
initial-route metadata/reader, workspace-root reader and owner discovery.
Its [source map](fpr5-restore-repro/extension-source-map.json) pins those routines.
The [resume adapter](fpr5-restore-repro/renderer-admission.mjs) executes the actual
`_6t` resume path, thread read/workspace classification, `M2t.prepare`,
`w2t`/`ilt`/`T2t` request preparation, cwd/permission helpers, ownership eligibility
callback and `h6t` dispatch. Its 63 exact source excerpts are in the
[renderer source map](fpr5-restore-repro/renderer-admission-source.json).

Host UI objects, URI/event APIs, backing storage, settings APIs, app-server and
IPC are explicit fixtures. Per-window workspace identities are supplied at
the host API boundary; OS-window recreation/deduplication and workspace descriptor
assignment are not implemented by this harness. No unavailable client selection
routine was replaced with invented convergence/restoration behavior. No missing
source dependency blocked this selected boundary.

## Captured result

Here A and B mean the two distinct physical disposable repositories. Their
UUIDs are respectively `7d521a18-129b-4907-8bbc-2a8c4eac71a1` and
`58de70fd-939f-4c48-9f72-092c6d8230b2`. Window/client/workspace identifiers and
membership generations are explicit in the result. UUIDs are fixture metadata;
the captured client requests do not attest those repository identities.

| Observation | Window/client | Workspace membership | Selected route / thread cwd | Outgoing resume cwd | Stream evidence |
| --- | --- | --- | --- | --- | --- |
| Initial and restored A | `synthetic-window-a` / `synthetic-client-a` | A, generation 1 | `/local/synthetic-thread-a` / A | A | Stub discovery names client A; resume source sets owner |
| Initial and restored B | `synthetic-window-b` / `synthetic-client-b` | B, generation 1 | `/local/synthetic-thread-b` / B | B | Stub discovery names client B; resume source sets owner |
| Labelled post-restore drift probe | Window/client B | A, generation 2 | Unchanged route B / B | **B** | Resume source sets owner before outgoing request |

The route origin is fixture custom-editor URI → native workspace persistence →
custom-editor deserialization/tab API → extension `initialRoute`. Both routes
remain distinct at the pre-navigation comparison, with zero navigation calls.
Neither restored window naturally develops a workspace/task mismatch in this
one cycle. Sidebar routes, shared persisted-atom selection and other restoration
surfaces are outside this capture; the saved incident does not identify its
surface.

After that comparison, the harness deliberately changes B's workspace input to
A while retaining B's restored route and authoritative mock thread cwd. This
is one diagnostic admission probe using the same restored selection, not a
second restore, spontaneous convergence or historical reconstruction. Each
admission probe uses a fresh renderer conversation/role store and a synthetic
visible active window; no successful resume or live ownership transition is
simulated. Mock IPC discovery and actual source role assignment are separately
labelled rather than treated as real cross-window arbitration.

In the drift probe the actual resume preparation retains cwd B and constructs
root candidates `[B, A]`. Derived client permissions contain a `workspaceWrite`
policy with those roots and network disabled. **Those derived permissions are
not effective grants.** The exact outgoing request carries `threadId` B and
`cwd` B; for this fixture it omits explicit sandbox/permission/root fields.
The client sets its stream role to owner and reaches the stubbed
`thread/resume` boundary without rejecting the mismatch. The harness then
cancels through the actual cancellation callback and returns no backend result.
The resulting `not-ready/canceled` is a harness stop, not a mismatch rejection.
Turn admission, backend policy, effective sandbox grants, tool execution and
cross-repository writes were **not observed**.

`requestedCwd` in the record labels the window's selected workspace root; it
is not an explicit cwd parameter accepted by `_6t`. Stored summary cwd,
authoritative thread cwd, preparation roots and dispatched cwd are recorded
separately to avoid conflating them.

## One confined repair recommendation

Implement a client host/owner **repository-binding admission guard** immediately
after authoritative thread hydration and before stream-owner acquisition or
outgoing resume/turn submission. Compare the current host-issued selected
repository binding (physical root, UUID, revision and membership generation)
with the task binding; missing, stale, ambiguous or mismatched context must
permit only labelled read-only inspection. Carry and validate that binding at
the execution owner for forwarded requests, invalidating it on membership,
thread or owner changes. Preserve an unrelated correctly bound owner's work.
Do not silently rewrite cwd or widen roots to make the comparison pass.

This is the confined guard described by the prior report, now supported by the
captured outgoing mismatch. It requires client/owner protocol work; NEXT text
or an Overseer-only prompt change cannot enforce it. No repair was applied,
and this recommendation grants no implementation authority.

## Separate FPR-OPS-2 and remaining authority

FPR-OPS-2 remains the independent legacy CLI installation defect:
`ModuleNotFoundError: No module named 'cryptography'`. The proposed repair pair
remains `overseer-kit-main-stable/cli/ok` and that checkout's own
`.venv/bin/python3` (recorded as Homebrew Python 3.14.4). Its manifest ranges
`PyYAML>=6.0` and `cryptography>=42.0` are not verified pins. Before any separately
authorized repair, select exact compatible versions/hashes from approved local
artifacts, freeze source/interpreter, preserve wrapper bytes/mode/target and
venv/consumer identity/history with rollback, prepare the dependencies in a
disposable environment, then validate bound NEXT per explicitly named target.
If compatible local artifacts are unavailable, stop without downloading. No
legacy command rerun, wrapper redirect, global/consumer mutation or repair
occurred. The [original detailed plan](FPR-5-HANDOFF-RELIABILITY.md#separate-fpr-ops-2-legacy-cli-repair-plan)
and its pinned inputs remain authoritative evidence.

ROADMAP and HANDOVER are updated together. Canonical NEXT is published only
through bound `next-write` with explicit context and the current expected digest,
as a stop: no next experiment or review is scheduled. Cursor sessionStart/stop
remain **owner-postponed NOT VERIFIED**. Historical cause, full automatic-host
qualification and final readiness remain unresolved. Original findings/failures,
old worktrees, protected refs and Muse history are preserved. Final non-author
adjudication and separate owner release remain unauthorized.

No Cursor launch, real profile/account access, keychain/privacy change, installed
source mutation, hook, provider/network operation, live export/delivery,
fetch/push, main merge, tag, signing or deployment occurred.
