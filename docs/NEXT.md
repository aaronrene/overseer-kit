---
schema: 1
repo_id: 6988dc4a-5f22-454b-9d68-ac5905b383bf
repo_root: /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014
branch: feat/overseer-v1-recovery-20261014
base_head: a1751f84604f634521020c93c67050d9127bd6b1
lane: product
model: GPT-6 Astra
action_id: OVERSEER-FPR5-FRESH-NEXT-ACCEPTANCE-1
action_kind: review
prompt_sha256: 4d50434a9949aade986c6c9c887b1a979b0c6f923addc70d5074537ef3c19ab7
---
Reasoning: High
Role: Independent non-author acceptance reviewer

The owner supplies this prompt to appoint one fresh non-author session.
If you authored the implementation, repairs or scope closeout, stop; this review
must run in a fresh non-author session. No review is performed by the author.

Read AGENTS.md, docs/decisions/FPR-5-MANUAL-DELIVERY-SCOPE.md and
 docs/validation/FPR-5-ACCEPTANCE-PACKET.md. Retrieve validated NEXT through
 .overseer/bin/ok -C /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014 next
with the supplied repository UUID, branch and product lane. Stop on refusal or
wrong context. Review the exact closing commit validated by that read; its sole
parent is a1751f84604f634521020c93c67050d9127bd6b1. Record the full closing SHA
and the packet's retained runtime/native identities before adjudicating.

Owner decision: keep automatic prompt display for convenience; explicitly fetch
and check fresh repository-bound NEXT before each new task, not every message.
An agent may perform this read; no extra button click is required after it.
Use the fresh validated result, not a cached prompt. Preserve current hook
settings, including disabled hooks. No automatic-freshness fix is claimed.

Execute the packet's revised acceptance brief once using read-only source and
surviving evidence. Decide R1-R6, every retained requirement and evidence custody
sufficiency. Write one reviewer-attributed ACCEPTED or precise BLOCKED record.
Every blocker must name the retained requirement, exact evidence gap, responsible
component and completion criterion. Preserve original FINDINGS and raw failures.

Actual Cursor sessionStart/stop and automatic-pilot continuity remain DEFERRED /
NOT VERIFIED. Client restored/forwarded conversation protection remains DEFERRED /
UNQUALIFIED. Shared chat-history behavior remains UNRESOLVED. Vendor request is
OPTIONAL / UNSENT. Deferral is not a pass.

Follow all packet restrictions: no repeated tests, experiments, pilots, launches
or general review; no original reconstruction, speculative adapters, vendor
contact, profiles/accounts, permission changes, installed/global/consumer changes,
hooks, network/providers, live export/delivery, fetch/push, main merge, tags,
signing, deployment or release. Preserve rollback, old worktrees, protected refs
and Muse history. Write only the review record and necessary bound handoff
maintenance. After ACCEPTED, stop for the owner's separate release decision
naming exact candidate, artifact/version, destination and permitted effects.
After BLOCKED, stop with the precise gap; do not begin repairs or reruns.
