# FPR-5 owner decisions and open reliability issues — 2026-10-15

Status: acceptance closeout preparation; not independent adjudication or release
approval. This record supersedes the pending owner-decision language in the
historical [interactive checkpoint](../validation/FPR-5-INTERACTIVE.md), without
editing that checkpoint, its inventories, raw failures or the original FINDINGS
review. Production source and tests are unchanged.

## Owner correction: the duplicate conversations were not deliberate

The owner states: **“I did not open the same conversation.”** The owner opened
only one Knowtation workspace deliberately; another may have opened on its own
or already been open when the computer restarted. The owner likewise did not
deliberately open Overseer Kit or Bornfree twice. The owner reported a restart
following a full disk, but does not know how the extra views appeared.

The coordinator's earlier explanation incorrectly suggested a deliberate user
action and overstated the cause. Local extension logs establish that several
windows displayed one conversation ID; they do not establish who or what
selected/restored it. There is no demonstrated causal link to the restart, full
disk or recent Overseer repairs. Do not blame the owner or describe this as a
proven restart defect. Switching the visible conversations was mitigation only;
it did not fix or explain the restoration mechanism.

## Explicit acceptance decision

The owner approved:

> I approve postponing the two Cursor automatic checks. Record them as not
> verified. Keep all security and network restrictions. Do not repeat the tests.
> Continue the acceptance process and prepare the next handover.

| Requirement | Current disposition |
| --- | --- |
| Actual Cursor 3.24.18 sessionStart | **POSTPONED / NOT VERIFIED**, by owner decision. No successful native receipt. |
| Actual Cursor 3.24.18 stop | **POSTPONED / NOT VERIFIED**, by owner decision. No successful native receipt. |
| Automatic host guarantee / full integrated pilot | Remains unaccepted where dependent on those events. Local workflow success is preserved separately. |
| Desktop rendering, canonical NEXT and normal quit | Owner-observed pass remains preserved for the recorded candidate. |
| Python 3.11 and Python 3.14/native Muse | Existing complete selected-case passing evidence remains; raw failures and affected reruns stay distinct. |
| Six FPR-5 findings | Author repairs and evidence complete; original independent FINDINGS verdict unchanged. |
| Final independent adjudication | Pending; must be a non-author and assess the exact proposed claim and unresolved limitations. |
| Owner release decision | Pending and separate from adjudication. No publication authority. |

Postponement permits preparation to continue. It is not a test pass, permission
change, permanent removal of the automatic-host requirement or approval to call
the full product certified. Do not ask for this postponement again. A proposed
release claim must state the exclusion explicitly and receive its separate
release decision; do not infer that decision here.

## Scheduled investigation and repair work

### FPR-OPS-1 — unexpected conversation restoration across project windows

**Open; cause unknown.** Cursor 3.24.18 and Codex extension 26.908.40401 were
observed. Logs showed the Overseer conversation active in Bornfree, Knowtation
and Overseer windows. Subsequent navigation selected the respective Bornfree and
Knowtation conversations. This explains the mirrored display, not how it arose.
The owner's correction above is authoritative about their actions. Selected log
excerpts and workspace mappings are in [local observations](../validation/fpr5-owner-closeout/local-observations.json).

Schedule a bounded investigation before claiming reliable automatic handoff
across restored editor windows or rolling it out to existing consumers. Trace
window restoration, extension conversation selection, conversation ownership,
workspace association and task root selection separately. Determine whether the
cause is in the editor, extension, integration or installation. A visible project
window does not by itself prove task/conversation isolation.

The intended prevention is an explicit check of the active task's repository
against the selected workspace/repository, stopping on a mismatch before work.
First establish what trustworthy context the host exposes; a prompt instruction
alone is not a proven enforcement boundary. Use disposable project windows and
new affected checks when separately scoped; do not repeat the failed lifecycle
launch or use real profiles to force a pass. If the responsible component is
external, prepare a local minimal reproducer and limitation; external reporting
requires separate authorization. This record neither implements nor certifies
that prevention.

### FPR-OPS-2 — shared legacy CLI selects an incomplete dependency environment

**Confirmed local installation failure; not repaired.** Read-only diagnosis
reproduced `ModuleNotFoundError: No module named 'cryptography'` from
`~/.local/bin/ok -C /Users/aaronrenecarvajal/knowtation next`. The wrapper adds the
older `overseer-kit/.venv/bin` to PATH but dispatches to
`overseer-kit-main-stable/cli/ok`. That shim prefers its own `.venv`, in which
`cryptography` is absent. The shared command fails before printing NEXT.
This is distinct from mirroring; no causal connection is proven. The dated
recovery checkout's bound launcher succeeds with its pinned runtime.

Prepare a confined repair/migration plan before relying on shared consumer
handoffs: identify the intended runtime/interpreter, verify pinned dependencies,
preserve consumer configuration/history and verify read-only NEXT identity per
target. No global wrapper edit, dependency install, consumer migration or hook
activation is performed or newly authorized here. Preserve older dirty worktrees;
do not redirect all consumers to an uncertified recovery build.

### FPR-EVID-1 — externally retained temporary evidence is unavailable

**Open evidence-availability limitation.** The original disposable pilot project,
host/platform temporary root and interactive curation root are absent at recorded
paths. None of the 40 selected interactive external originals or two externally
retained screenshots is present at its recorded path. Committed curated evidence
still verifies. This does not establish when or why files disappeared, or that
no other copy exists. Do not claim restarting deleted them, recreate them as
original evidence or repeat completed tests to conceal their absence.

The closeout packet must distinguish surviving committed records from unavailable
originals, including redacted copies and the historical pilot state. Resolve
their sufficiency for the proposed claim before asserting final-adjudication
readiness. The [availability record](../validation/fpr5-owner-closeout/verification.json)
does not rewrite historical inventories' then-current preservation statements.

## Next deliverable and completion boundary

Prepare one **acceptance closeout packet**: an exact source/claim/evidence map,
these decisions, deferred/missing requirements and explicit disposition of
FPR-OPS-1, FPR-OPS-2 and FPR-EVID-1. Classify required pre-release repairs versus
claim limitations without silently moving an unresolved requirement to a later
release. Identify the smallest necessary follow-up if readiness is blocked.
Do not launch another general review or validation cycle.

After required evidence and dispositions are complete, reserve one final
independent adjudication by a non-author, then a separate owner release decision.
Neither is authorized or performed here. Implementation waves and six author
repairs are complete; acceptance closeout is in progress. A percentage or finish
date would conceal unresolved reliability/evidence work.

Continue here with GPT-6 Astra, Max reasoning, as acceptance coordinator. No new
chat or pasted prompt is needed for preparation. A separate non-author session
will be needed for final adjudication once ready and appointed. The exact
pending action lives only in canonical `docs/NEXT.md`.

## Preservation and validation

Opening HEAD `829dc3352c6510cd5623afa72a032de868a05f3f` has sole parent
`7ee9a372e478ad251c17d8e8fd1a4118811c01b2`; physical/Git root, name, UUID, branch,
clean state and bound NEXT matched. Repaired runtime remains
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.
Before edits, all 133 repair artifacts, 215 acceptance artifacts and 54 latest
interactive artifact/companion entries verified, as did eight repaired source
files and 40 native source entries. All 144 refs were captured for preservation.

This is documentation/evidence maintenance only. The owner's no-repeat instruction
supersedes the standing instruction to rerun the supported suite before each
feature commit: no completed suite, review, pilot or isolated launch is rerun.
Retain unchanged-source evidence and check document integrity, preservation and
bound publication/readback. Update ROADMAP and HANDOVER together; publish only
through bound `next-write` with the current digest, then make one local feature
closing commit with the opening HEAD as sole parent.

All security/network restrictions remain: no keychain/privacy changes, real
profile/account/provider access, real-consumer mutations/hooks, external network,
fetch/push, live export/delivery, main merge, tags, signing or deployment. No
older worktree, protected ref or Muse history changes in this closeout.
