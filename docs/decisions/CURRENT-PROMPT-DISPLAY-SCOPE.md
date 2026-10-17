# Current-prompt display scope — 2026-10-17

The latest owner direction supersedes the FPR-6 external-dependency stop and
automatic completion plan for current work. Finish the manual current-prompt
display workflow using the existing validated reader and writer. Automatic
Cursor events, vendor execution protection and shared-chat investigation are
outside this task. Do not pursue vendor assistance. Their historical statuses
remain NOT VERIFIED, UNQUALIFIED and UNRESOLVED respectively; none is a new
prerequisite for this manual workflow.

## Required workflow

Select the physical project and intended lane. Read its canonical `docs/NEXT.md`
through that project's bound `.overseer/bin/ok -C ROOT next --lane LANE`. Check
the returned root/UUID, branch/revision, lane, model and action context. Display
the validated prompt verbatim, including its saved recommended model, for manual
use. Do this at entry, before each new task and after the closing commit. A
refusal must be reported; never reconstruct a task from summaries or chat history.

The maintained CLI already renders the prompt and model. The existing browser
NEXT control uses the same validated service. No new UI, reader, writer, native
event integration or model-selection service is needed. These are explicit reads;
they neither execute the prompt nor enforce a vendor's tool permissions.

Only bound `next-write`, with explicit context and the expected prior whole-file
digest, publishes canonical NEXT. At closeout publish the actual next unfinished
authorized task, make the local closing commit, then read back and display the
validated output. If the approved work is complete, publish a completion stop
and say no unfinished task remains. Do not invent a follow-on task or queue
another general review. ROADMAP and HANDOVER remain paired summaries.

## Verification and preservation

Reuse working code and completed evidence. Fix only demonstrated gaps; use focused
checks for affected behavior. Documentation-only changes require consistency and
validated readback, not completed suites, reviews, experiments or another blocked
launch. The existing display path satisfies the requirement; this session resolves
stale scope and session instructions and publishes the completion state.

The accepted manual source `97f052949146c3cf337478927e6d345e353d2063`, independent
acceptance and [local release](../releases/FPR-5-MANUAL-LOCAL-RELEASE.md) remain
preserved with their original limits. The FPR-6 plan, requests and evidence remain
historical records; requests stay UNSENT. No automatic acceptance is claimed.
Existing-project installation stays on hold. No external contact, network call,
profile/account/keychain access, vendor/shared-command change, release or
installation into existing projects is authorized. Preserve old worktrees,
original evidence and Muse history.

Opening HEAD: `a0a1250aa25122cbe4b051d012421a887de8378b`.
Repository UUID: `6988dc4a-5f22-454b-9d68-ac5905b383bf`.
Branch: `feat/overseer-v1-recovery-20261014`; lane: product.
Model: GPT-6 Astra; reasoning: High.
