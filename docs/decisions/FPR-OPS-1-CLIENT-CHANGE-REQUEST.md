# Prevent work from a conversation bound to another project

**Current disposition — 2026-10-17: OPTIONAL / UNSENT.** Under the
[manual delivery scope](FPR-5-MANUAL-DELIVERY-SCOPE.md), this vendor request and
client-level restored/forwarded conversation protection are deferred from this
delivery's acceptance prerequisites. No contact is authorized or performed.
Shared chat-history behavior remains unresolved. The prepared body and historical
observations below are preserved; their completion criteria concern optional
future qualification, not the current release path.

Prepared 2026-10-17 for the Codex IDE extension maintainers, with the Codex
execution-service maintainers. Coordinate with the Cursor workspace API owner
only where the required host membership contract is unavailable. This is a
ready-to-send request, **not sent**. No external issue or implementation owner
has been assigned. The body below uses synthetic A/B identifiers; it contains
no real conversation IDs, project names, local user paths, credentials or chat
content. The local provenance notes after the body are not attachments.

---

**Subject: Bind restored/forwarded Codex work to the selected project before resume and execution**

Please provide an enforced project-binding check for restored conversations and
requests forwarded between Codex views. A local integration can validate its
own project files, but cannot bind an editor window to a Codex task or prevent
tools from running through the client/execution service.

**Observed boundary.** A source-based offline capture on 2026-10-15 used code
from Cursor 3.24.18, commit `be4c9e5350d77747b42cd467cbd3370a753d4640`, and Codex
IDE extension 26.908.40401 on macOS 15.7.2 arm64. These identify the recorded
source; they are not a claim about current versions or incident-time bytes.

Two disposable projects A/B had distinct mock threads with working directories
A/B and distinct custom-editor routes. One save/restore cycle preserved the
distinct routes with zero navigation calls. No natural mismatch occurred.
After that comparison, a deliberately injected probe changed window B's
workspace membership to A while retaining restored thread B and its authoritative
mock working directory B. The actual client resume code:

- retained working directory B and prepared root candidates `[B, A]`;
- assigned its local stream role to owner;
- reached the stubbed `thread/resume` boundary with thread B and working
  directory B, without rejecting that workspace/task mismatch.

The outgoing request in this fixture omitted explicit sandbox/permission/root
fields. Derived permissions are not effective grants. The harness canceled at
the request boundary; it did not launch the full client or app-server, admit a
turn, execute tools, or demonstrate cross-project writes. Mock discovery and
local role assignment do not prove successful real ownership arbitration.
This is an admission-gap observation, **not a demonstrated sandbox escape**.
It does not establish the cause of a separate historical shared-chat display
incident. No cause is attributed to the owner, restart or disk exhaustion.

**Requested changes and owners**

1. **Codex extension host / workspace integration:** obtain the explicitly
   selected physical repository root, repository identity, branch/revision,
   window/host identity and current workspace membership generation. Outer
   folders and multi-root windows require an explicit project selection. Obtain
   authoritative task metadata separately. Define a versioned host-issued
   binding/token contract; a webview path, conversation title, model-supplied
   working directory or optional hook field cannot substitute for it. If the
   host lacks the necessary membership/lifecycle API, identify that exact
   dependency for the Cursor API owner; this request does not allege a proven
   Cursor persistence defect.
2. **Codex renderer / resume and turn admission:** compare those bindings after
   authoritative thread hydration and before work-capable resume, stream-owner
   acquisition or turn submission. Missing, stale, ambiguous or mismatched
   context must allow only labelled read-only inspection. Do not silently change
   the task's working directory or expand writable roots. In the captured build,
   the relevant landmarks are the `_6t` resume path, `M2t.prepare`,
   `w2t`/`ilt`/`T2t` preparation and `h6t` dispatch. These are version-specific
   bundle symbols, not stable API names.
3. **Codex owner-forwarding protocol / execution service:** carry the host-issued
   sender binding to the actual execution owner. Validate sender and task there,
   recheck at turn/steer and tool dispatch, and invalidate on repository,
   revision, membership, thread or owner changes. A mismatched viewer must not
   redirect, cancel or acquire authority over a correctly bound owner's work.
   Intentional cross-project work requires an explicit new binding. Backend
   enforcement was not inspected or exercised: document any existing effective
   enforcement and implement the missing checks rather than assuming it absent.

**Completion criteria.** Identify the responsible implementation owner, protocol
and exact fixed builds. Supply focused evidence that matching contexts work;
wrong/missing/stale bindings, ambiguous multi-root selection and drift before
execution refuse work; linked worktrees and symlinks resolve to the correct
physical repository; and forwarded requests cannot affect an unrelated valid
owner. Demonstrate refusal at the actual client/owner/tool boundary, not just a
warning or canceled mock request. Explain which supported fields an external
integration may consume and which enforcement the host owns. Historical
route-selection causation may remain unresolved; do not claim this check proves
it or prevents every duplicate display. If no implementation path is available,
state that explicitly.

The local integration's two real Cursor start/end checks remain postponed and
unverified. They are separate from this request. No new permission, account,
network access or customer-project testing is requested here. No rerun was
performed to prepare this report.

---

Local provenance for the repository owner (do not attach the repository or raw
logs wholesale):

- [Completed source investigation](../validation/FPR-5-HANDOFF-RELIABILITY.md):
  E7 workspace roots; E8/E9 discovery/forwarding; R1–R5 preparation/ownership;
  O1/O2 existing repository checks. [Source map](../validation/fpr5-handoff-reliability/source-map.json).
- [Completed restoration capture](../validation/FPR-5-RESTORE-REPRO.md) and
  [recorded result](../validation/fpr5-restore-repro/reproduction-result.json):
  one save/restore cycle and the separately labelled injected mismatch.
- [Renderer excerpt map](../validation/fpr5-restore-repro/renderer-admission-source.json),
  [extension map](../validation/fpr5-restore-repro/extension-source-map.json) and
  [host map](../validation/fpr5-restore-repro/restore-source-map.json) retain source
  identities/ranges. Recorded extension bundle SHA-256:
  `820691c93be40e73f0929b633cddc694b41775050cd72283faba283e53941f4f`;
  renderer bundle SHA-256:
  `9c43854dc714687bbbdab5895bc084a09681b97c998b3f612e30a7aeac97bfec`.

Only the request body is prepared for owner routing. Additional files, vendor
source excerpts or logs require separate selection and disclosure authority.
The completed harness is not rerun or represented as self-contained without its
recorded source dependencies. No screenshot or missing original is recreated.
