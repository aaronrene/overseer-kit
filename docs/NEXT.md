---
schema: 1
repo_id: 6dba88a5-029c-4136-9277-c3a0c81f31a6
repo_root: /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery
branch: feat/overseer-v1-recovery
base_head: 2bfa69864ec2f8bb3d89cc66d6353dd111421875
lane: product
model: GPT-6 Astra
action_id: OVERSEER-V1-INSTALL-ROLLBACK-1
action_kind: implement
prompt_sha256: 9cc4a30c04f5f5c24ba2b5e4993894b0535310978e261601137ed600d01989bc
---
Validate clean source installation and current/previous rollback for bounded v1.
Read AGENTS.md, docs/decisions/V1-SCOPE-RESET.md, and docs/validation/V1-RECOVERY.md.
The architecture review and its two corrected build findings are closed; do not
repeat OVERSEER-V1-REVIEW-1 against unchanged code.
Use disposable installation directories and Git fixtures, each runtime with its
own conventional venv. Verify clean dependency installation, status/NEXT, upgrade
to current and rollback to previous, preserving fixture identity and documents.
Keep changes bounded; record exact commands, results, and limitations in the
existing validation document and update both living summaries. Run the supported
suite for any code change. Keep the five-to-eight-session cap.
No new packets or discarded security machinery. No real consumers, push, mirror,
merge, release, deployment, consumer hook activation, or pilot. On completion,
publish the actual next action through next-write; do not leave this completed
action as NEXT. A consumer pilot requires separate explicit authorization.
