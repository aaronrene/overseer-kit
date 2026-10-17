# FPR-OPS-1 conversation restoration investigation

**The historical restoration cause remains unknown.** The saved evidence proves
shared conversation display, and the installed source explains how restored
conversation routes, task cwd and stream ownership can remain independent of the
visible project window. A small offline reproduction demonstrates that boundary
with synthetic inputs. It does not recreate the unknown selection trigger or
prove that an incident task executed against the wrong repository.

The bounded investigation is complete; FPR-OPS-1 remains an open qualification
blocker for restored-window automatic handoff and consumer rollout. Navigation
was mitigation only. The owner did not deliberately open duplicate conversations
or project windows. Neither owner error, a Cursor/Codex defect, restart/full-disk
causation nor an Overseer repair regression is established.

## Verified boundary

Opening HEAD is `4c7f225b6148f95fb575bcd604b113aed5b5999b`, the packet closing
commit whose sole parent is `d6d6b92d0f10c58a41e25678835f2436b1a5f827`.
Physical/Git root is
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, name
`overseer-kit`, UUID `6988dc4a-5f22-454b-9d68-ac5905b383bf`, branch
`feat/overseer-v1-recovery-20261014`, lane `product`. Entry was clean and bound
NEXT validated the requested action. No unexplained source difference was found.

[Opening verification](fpr5-handoff-reliability/opening-verification.json)
records 295 runtime, 440 test, 40 native, ten packaging, four validation-driver
and two requirements entries matching the recorded candidate. Runtime membership
and actual digest remain
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.
The packet and earlier immutable artifact sets, original review files and 144
refs verified. Historical mutable summary companions are not relabelled as
matching their old inventories. The acceptance packet and original findings,
failures and inventories remain unchanged.

Source was read from installed Cursor **3.24.18**, commit
`be4c9e5350d77747b42cd467cbd3370a753d4640`, and Codex extension
**26.908.40401**. Their version labels match the saved observations; the saved
incident record has no client bundle hashes establishing incident-time byte
identity. [Source map](fpr5-handoff-reliability/source-map.json) pins current
bundle hashes, exact UTF-8 byte ranges, lines and excerpts. References such as
E1 and R3 below identify entries in that map. App-server binary internals were
not available as readable source and were not executed.

## What the saved incident evidence establishes

The [sanitized observations](fpr5-owner-closeout/local-observations.json) preserve
selected view-activity lines, not complete event traces. All four logged windows
selected conversation `01a13f0e-ba38-78e1-8168-c46783739a4f`:

| Saved window | First retained active line | Later retained transition |
| --- | --- | --- |
| 1 | 06:03:47.585, line 35, needs_resume | 06:48:27.906, owner becomes inactive; Bornfree conversation becomes active |
| 6 | 06:05:58.760, line 27, needs_resume | 06:09:51.473, follower becomes inactive; Knowtation diagnostic conversation follows |
| 2 | 06:11:17.860, line 49, needs_resume | 06:52:43.510, follower becomes inactive; original Knowtation conversation follows |
| 3 | 06:11:41.144, line 44, needs_resume | No later role or navigation line retained in this selection |

These are the original log clock strings on 2026-10-15; no timezone conversion
or missing transition is inferred. Owner/follower observations occur at different
times; the selection is not a simultaneous ownership snapshot. R6 shows that
the logging method records activity, resume state and role, without task cwd,
selected repository, route origin or dispatched tool target.

The saved workspace mappings distinguish Knowtation's standalone folder from an
untitled multi-root workspace containing Knowtation and Scooling. Overseer's
window folder is the outer `OVERSEER_KIT` directory, not necessarily the dated
repository. These mappings do not supply an atomic window/client/thread/root
binding at each logged event. The original screenshots, unredacted lines and
temporary profiles remain unavailable as described in the
[acceptance packet](FPR-5-ACCEPTANCE-PACKET.md); no current real profile or account
was read to fill those gaps.

## Source trace and the limits of each link

| Boundary | Installed behavior and implication | Evidence |
| --- | --- | --- |
| Cursor window restoration | `doGetPathsFromLastSession` reads saved window and last-active descriptors; `getRestoreWindowsSetting` uses `all` when the application's `wasRestarted` flag is true. The incident's flag, descriptor contents and downstream deduplication outcome are unknown. This flag must not be equated with the owner's reported OS restart. | C1 |
| Conversation tab restoration | `ensureRestoredConversationTabsResolved` enumerates restored custom/text tabs with scheme `openai-codex` and invokes `vscode.openWith`. This method has no workspace comparison. The URI parser identifies a conversation from `/local/ID` or `/remote/ID`; it has no repository identity field. | E1, E2 |
| Route selection | `resolveCustomEditor` turns that URI into `initialRoute`; the host injects metadata, and the renderer redirects to it. Separate URI/sidebar navigation routes also exist. No retained incident line identifies which route selected the conversation, or whether each view was a sidebar or custom editor. | E3–E6, U1, U2 |
| Shared persistence | Persisted atoms are read from global state and updates broadcast to views. This is a possible area for further tracing, not evidence of a shared last-conversation key: no such causal key/value was identified in the saved record. | E11 |
| Window roots and task cwd | The host obtains workspace folders independently. Resume loads thread metadata and permissions; cwd arbitration can choose the stored thread cwd over an unrelated requested cwd. The helper constructing resume roots can combine thread cwd and window roots. A root candidate list alone does not establish effective write permission. | E7, R1–R4 |
| Stream owner and follower | Owner discovery sends host ID and conversation ID; this request has no workspace identity. Follower turn requests target the owner, whose start-turn case forwards the conversation and turn payload. This explains a mechanism for shared interaction after selection, not the initial selection or incident tool execution. | E8, E9, R5 |
| Existing context checks | IDE context lookup filters by path membership. Overseer binds its own launcher/runtime/root/UUID and validates optional hook root fields. Those checks do not bind a Codex task or follower sender to the selected repository. Empty hook payloads are accepted and generated hooks use `failClosed: false`; they cannot be represented as an enforced task execution gate. | E10, O1, O2; `cli/product_bookends.py` |

The demonstrated gap is at the inspected entry points. It is not a claim that
all downstream client/backend enforcement is absent. In particular, the full
resume policy, actual sandbox grants and app-server execution were not exercised.

## Smallest disposable reproduction delivered

[reproduce.mjs](fpr5-handoff-reliability/reproduce.mjs) evaluates only seven
saved, hash-checked source excerpts in mock host contexts. It creates two empty
temporary directories, supplies the same synthetic restored conversation URI to
each, resolves both routes, calls the real cwd/root helpers and captures owner
discovery requests against a stub. A matching-root control and a nested-cwd
control distinguish intended cwd retention from the mismatch case. The temporary
directories are removed in `finally`.

The single new execution completed with exit code 0 and empty stderr; see
[result](fpr5-handoff-reliability/reproduction-result.json). Both routes select
the synthetic thread. With project A's stored thread cwd, the second window's
requested project B cwd resolves to A; its root candidates include A and B.
Both owner queries are identical and omit workspace identity. The owner response
is explicitly mocked. The Cursor policy helper also distinguishes ordinary
startup from its synthetic application-restart flag.

```sh
node docs/validation/fpr5-handoff-reliability/reproduce.mjs
```

This is a source-function reproduction of **propagation given seeded state**.
It deliberately does not reproduce the unknown creation of that state. It uses
no Electron launch, app-server, real conversation, profile, account, hook,
provider or network. No prior test, review, pilot or failed lifecycle launch was
repeated. Its result is not added to acceptance-test counts.

## Smallest further capture needed to distinguish causes

No saved evidence distinguishes these hypotheses:

| Hypothesis | Missing discriminator |
| --- | --- |
| Existing conversation URI restored in more than one window | Per-window serialized editor URI/state immediately before shutdown and resolver inputs on restore |
| URI, queued navigation or another selection path targeted the wrong view | Selection origin and destination window/webview/client IDs, including URI handling and pending navigation |
| Shared persisted state influenced selection | Exact relevant key/value and writer/reader scope before and after hydration; global-state existence alone is insufficient |
| Stale workspace association or an ownership transition affected execution | Window membership epoch, authoritative thread cwd/permissions, owner discovery/role transitions and submitted turn/tool target in one correlated trace |

The smallest next experiment is two synthetic repositories with distinct UUIDs,
two mock threads whose stored cwd points respectively to those repositories, and
two initially distinct per-window routes. Use an offline copied-client or
host-API restoration harness with stubbed app-server/IPC and a separate empty
state directory. Seed different routes, snapshot only binding metadata, then
perform one synthetic persistence/restore cycle. Observe whether routes become
equal **before** any navigation; compare root binding again before resume and
before a no-op turn. First scope the surface identified as sidebar or editor;
expand to multi-root only if that path requires it.

Record the route's origin, window/client IDs, workspace membership/version,
thread ID/cwd, requested/resolved cwd, owner ID/role, effective permissions and
admission result. Preserve input/output snapshots and chronological events using
synthetic identifiers, without chat text or credentials. If the harness cannot
reproduce convergence, retain that result; it does not clear the historical
incident. Do not substitute a real profile, account login, keychain change,
provider call or the postponed lifecycle launch. Execution/instrumentation of
that new client harness requires a separately scoped successor; none ran here.

## Confined mismatch guard proposal

The useful enforcement boundary belongs in the host/task admission path, with a
second check at the execution owner. It cannot be supplied by changing NEXT text
or by showing a different chat.

1. The extension host obtains the selected repository from the actual window's
   workspace membership and an explicit repository selection where needed. Bind
   physical root, UUID, branch/revision, host ID and a membership generation.
   An outer workspace or multi-root window cannot silently mean its first root.
   An ancestor path or matching UUID alone is insufficient: linked worktrees and
   copied configurations require their own physical-root and revision checks.
2. After thread metadata hydration, compare the authoritative task binding with
   that selected binding before automatic resume, acquiring write ownership or
   submitting a turn. E1/E3 are suitable for early read-only display gating;
   R3/R4 and the host's outgoing request boundary are needed for admission.
   Missing, stale or ambiguous context permits labeled read-only inspection and
   refuses work. Do not silently rewrite the task cwd or broaden writable roots.
3. For a follower, carry a host-issued sender-context token to the owner. Validate
   it at E9/R5 against the actual sender and current thread, not merely the
   owner's own window. Recheck at turn/steer and tool dispatch and invalidate
   the token on root, revision, thread or owner changes. The model's cwd string,
   conversation title and a webview-supplied path are not trusted tokens.
4. Keep authorization for an existing correctly bound owner independent of an
   unrelated mismatched viewer. A stale viewer must not redirect, stop or gain
   authority over that owner's work. Any intentional cross-project task needs
   an explicit new binding; restoration must not infer one.

The host APIs expose window folders and thread metadata separately, so the
comparison can be designed there. The current examined request does not carry
an attested per-window selected-repository token; adding and validating one
would require a client/owner protocol change, not an Overseer-only prompt patch.
Future focused cases should cover matching roots, wrong/missing binding,
multi-root ambiguity, linked worktrees, symlinks, and drift between admission
and execution. No client, extension, hook, global or consumer repair was applied.

## Separate FPR-OPS-2 legacy CLI repair plan

The saved failure remains `ModuleNotFoundError: No module named 'cryptography'`.
The global wrapper prepends `overseer-kit/.venv/bin` but runs
`overseer-kit-main-stable/cli/ok`; that shim selects its own `.venv/bin/python3`.
This independent installation defect does not explain conversation mirroring.
The recovery repository's bound launcher still validates NEXT.

The proposed compatibility-repair pair is the existing stable source
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-main-stable/cli/ok` and its own
`.venv/bin/python3`, which currently resolves to Homebrew Python 3.14.4.
[Read-only inputs](fpr5-handoff-reliability/legacy-plan-inputs.json) pin its
manifest: `PyYAML>=6.0` and `cryptography>=42.0` are ranges, **not verified pins**.
An installation-ready dependency selection therefore remains outstanding.

Before a separately authorized repair, freeze the exact source/interpreter
pair and choose compatible dependency versions and artifact hashes from approved
local inputs. Preserve global wrapper bytes/mode/target, interpreter/venv state
and consumer configuration/identity/history with an exact rollback record.
Prepare and check that dependency set in a disposable environment before any
replacement. Confine any later mutation to the approved legacy environment and,
only if separately needed, its wrapper; do not redirect all consumers to the
recovery candidate. After repair authority is granted, validate read-only NEXT
with explicit root/UUID/branch/lane/current digest for each named target before
relying on shared handoffs. Hooks remain disabled. If local compatible inputs
are unavailable, stop without downloading. The broken command was not rerun.

## Completion and pending authority

The deliverables are this source trace, the executable source-function
reproduction, unresolved hypotheses, the smallest discriminating capture and
the confined guard/legacy proposals. ROADMAP and HANDOVER are updated together;
canonical NEXT is published only by bound `next-write` with explicit context
and current expected digest. The successor is a stop pending scope for the new
disposable client capture or repair, not another investigation of the same saved
evidence or another packet preparation cycle.

Cursor sessionStart and stop remain **owner-postponed NOT VERIFIED**. Full
automatic-host acceptance and final-adjudication readiness remain unestablished.
The original **FINDINGS** verdict, missing-original limitations and old worktrees,
protected refs and Muse history remain preserved. Final non-author adjudication
and the separate owner release decision remain pending and unauthorized.
No fetch/push, network/provider, live export/delivery, merge, tag, signing or
deployment occurred.
