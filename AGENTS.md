# Overseer Kit — bounded recovery instructions

Current authority: the owner request and
`docs/decisions/CURRENT-PROMPT-DISPLAY-SCOPE.md`. The bounded foundation in
`docs/decisions/V1-SCOPE-RESET.md` remains historical context.
The former sole-writer/NXR-GSR NEXT and per-step packet chain are superseded.
Do not follow historical handoffs or expand the architecture.

At every actionable turn verify physical cwd, Git root, branch, full HEAD and
configured repository name. Current user scope overrides inherited instructions.
Use disposable fixtures; do not access real consumer repositories without explicit
current authorization. Preserve both older dirty worktrees and local Muse history.

Use this installation's conventional `.venv` and `cli/ok`. Runtime symlinks are
normal. `ok -C ROOT status` and `ok -C ROOT next` are read-only and repository-bound.
At session entry, before each new task, and after the closing commit, invoke the
selected project's bound `.overseer/bin/ok -C ROOT next --lane LANE` and display
its validated prompt verbatim with its saved recommended model. Check physical
root/UUID, branch/revision, lane, model and action context. These Codex
bookends are instruction-triggered; no native Codex lifecycle delivery is claimed.
Report any refusal without guessing a replacement task.
Only `next-write` publishes canonical `docs/NEXT.md`, with explicit context and
expected prior digest. ROADMAP and HANDOVER are paired summaries, not alternative
prompt sources. Update both when the milestone changes.

Reuse completed evidence and working code. Fix only demonstrated gaps and run
focused checks for affected behavior. For documentation-only changes, check
consistency and validated prompt readback. Do not repeat completed general reviews,
test suites, experiments, pilots or the blocked launch. Historical tests and
failures remain preserved; no new release or independent acceptance is implied.

Local feature commits are authorized after checks. No push, mirror, merge to main,
release, deployment, provider/network access, real-consumer hooks or pilot. Do not
restore OCI, native/Mach GSR, sole-writer storage or identity-bridge prerequisites.
The bounded review, installation/rollback, pilot, manual acceptance and local
manual release are complete in their recorded scopes. Preserve them; do not queue
another general review. Automatic Cursor events, vendor execution protection and
shared-chat investigation are outside the current task. Do not pursue vendor
assistance or access profiles/accounts/keychains. No installation into existing
projects is authorized.

At closeout publish the actual next unfinished authorized task through bound
next-write, complete the local closing commit, then read NEXT again and display
the validated paste-ready prompt verbatim with its model. If approved work is
complete, publish a stop stating that no unfinished task remains; do not invent
more work or restore the superseded FPR-6 external-dependency stop. Never present
a completed action as pending. Do not run obsolete governance-sync to regenerate
a handoff.
