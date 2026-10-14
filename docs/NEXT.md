---
schema: 1
repo_id: 6988dc4a-5f22-454b-9d68-ac5905b383bf
repo_root: /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014
branch: feat/overseer-v1-recovery-20261014
base_head: 333f81e9bf847dcd418b305b931b1279da3c7ade
lane: product
model: GPT-6 Astra
action_id: OVERSEER-V1-RECOVERY-INSTALL-ROLLBACK-1
action_kind: maintain
prompt_sha256: feeb78dd78abbd360fd665f447676bcb07df9c7ae510b14e8538a3feb6ca05f3
---
Reasoning: Extra High
Role: Senior maintainer validating clean installation and current/previous rollback

Open only the bound recovery worktree above and disposable fixtures created for
this task. Before acting, print and verify physical cwd, Git top-level, branch,
full HEAD, configured repository name and UUID. Stop on mismatch. Do not access
older dirty worktrees or real consumer repositories.

Read AGENTS.md, docs/decisions/V1-SCOPE-RESET.md, docs/validation/V1-RECOVERY.md,
docs/reviews/V1-RECOVERY-REVIEW.md, docs/V1-QUICKSTART.md and canonical docs/NEXT.md.
The independent architecture/completed-build review is complete. R1/R2 repair
evidence is recorded separately; do not queue or repeat that completed review.

Validate a clean source installation and current-to-previous-to-current rollback
using disposable Git repositories and installation directories. Obtain current
and previous committed source only from this worktree's Git objects; record exact
commit IDs and runtime digests. Use offline dependencies from this worktree's
local .venv and preserve ordinary interpreter symlinks. Do not download packages.

Exercise init, repository-bound read-only status/NEXT, explicit sync and bound
next-write. Verify physical-root/UUID/runtime binding, refusal before explicit
runtime refresh, preservation of living documents and NEXT, and recovery to the
current installation. Keep the previous build's known R1/R2 limitations explicit;
rollback operability does not certify that build free of those findings. Stay
within the existing source-installation and trusted-host contract. Record bounded
blockers instead of inventing packaging, automatic rebinding or storage machinery.

Run the complete supported suite with this worktree's local .venv. Separate
product failures from environment restrictions, retain historical test disposition,
and record reproducible installation/rollback evidence. Update ROADMAP and HANDOVER
together. Publish exactly one evidence-based successor through bound next-write;
if validation passes, stop pending separate authorization for a noncritical pilot.
Read back NEXT and commit evidence and handoff locally after checks. Report the
validated successor prompt and model. Test passes do not establish final v1.

No OCI, native/Mach GSR, sole-writer storage, identity bridges, packet chains,
network/provider access, push, mirror, main merge, release, deployment,
real-consumer hooks or pilot. A handoff does not authorize those actions.
