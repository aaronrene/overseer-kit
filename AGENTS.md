# Overseer Kit — bounded recovery instructions

Current authority: the owner request and `docs/decisions/V1-SCOPE-RESET.md`.
The former sole-writer/NXR-GSR NEXT and per-step packet chain are superseded.
Do not follow historical handoffs or expand the architecture.

At every actionable turn verify physical cwd, Git root, branch, full HEAD and
configured repository name. Current user scope overrides inherited instructions.
Use disposable fixtures; do not access real consumer repositories without explicit
current authorization. Preserve both older dirty worktrees and local Muse history.

Use this installation's conventional `.venv` and `cli/ok`. Runtime symlinks are
normal. `ok -C ROOT status` and `ok -C ROOT next` are read-only and repository-bound.
At session entry and after the closing commit, invoke the bound
`.overseer/bin/ok -C ROOT next` and display its validated action. These Codex
bookends are instruction-triggered; no native Codex lifecycle delivery is claimed.
Report any refusal without guessing a replacement task.
Only `next-write` publishes canonical `docs/NEXT.md`, with explicit context and
expected prior digest. ROADMAP and HANDOVER are paired summaries, not alternative
prompt sources. Update both when the milestone changes.

The supported release matrix is in `docs/validation/V1-RECOVERY.md`. Run it before
local feature commits. Preserve historical tests and report unresolved failures;
do not equate a green bounded suite with a green historical suite or a release.

Local feature commits are authorized after checks. No push, mirror, merge to main,
release, deployment, provider/network access, real-consumer hooks or pilot. Do not
restore OCI, native/Mach GSR, sole-writer storage or identity-bridge prerequisites.
One independent architecture/build review, installation/rollback and an explicitly
authorized pilot remain final-v1 requirements. Do not claim independent review of
work authored in this session.

At closeout read NEXT from disk and include its validated paste-ready prompt when
it describes the pending task, together with the model. Never present a completed
action as pending. Do not run obsolete governance-sync to regenerate a handoff.
