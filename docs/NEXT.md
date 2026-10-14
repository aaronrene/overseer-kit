---
schema: 1
repo_id: 6988dc4a-5f22-454b-9d68-ac5905b383bf
repo_root: /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014
branch: feat/overseer-v1-recovery-20261014
base_head: 0b763df6d7c9066582d27b349a731a4ff70a43e2
lane: product
model: GPT-6 Astra
action_id: OVERSEER-FULL-PRODUCT-RESTORATION-FOUNDATION-1
action_kind: implement
prompt_sha256: 37110c8963c2bb624d8f094b52e91c1e0686ac4a88bfc4cd7f55afa87303d1ea
---
Reasoning: Max
Role: Principal product integration engineer

Perform FPR-1 only after the owner accepts this prompt: unify the product CLI,
configuration/migration and automatic canonical NEXT foundation under
docs/decisions/FULL-PRODUCT-RESTORATION-PLAN.md. This acceptance authorizes local
FPR-1 implementation and focused checks, not FPR-2/3, release or remote actions.

First verify physical cwd, Git top-level, branch, full HEAD, configured name
overseer-kit, UUID, lane, runtime binding and clean state. Validate this NEXT as
the single documentation-only closing commit whose sole predecessor is
0b763df6d7c9066582d27b349a731a4ff70a43e2. Stop on mismatch, unexpected dirt or moved
source refs. Read AGENTS.md, docs/ROADMAP.md, docs/OVERSEER-HANDOVER.md,
docs/NEXT.md, the full restoration plan, docs/decisions/V1-SCOPE-RESET.md,
docs/validation/V1-CERTIFICATION.md and tests/README.md before implementation.

Keep the current branch as integration base. Verify these committed sources:
- feat/overseer-context-isolation at e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504.
- feat/overseer-v1-recovery at 32254cd939885d9d6f40634997ea5b9c37ea776c.
- main at d47291d5d9030de5ebef713da95efa978c4d8c6e.
- Repaired safety implementation at 348e0f323a3b17cd5022a1bfd56fa09a6831c51f.
Read their committed objects from this worktree. Do not enter or alter the older
worktrees. Preserve all existing refs except authorized commits on this branch,
Muse history, recovery snapshots, rollback fixtures, completed pilot and bounded
source-release directory. Do not merge, cherry-pick or wholesale revert.

Implement the exact FPR-1 inputs, outputs and acceptance criteria in section 8
of the plan, using preserved working code by default:
1. Make cli/ok and its compatibility alias reach one dispatcher through the
   isolated bootstrap. Keep repository/runtime validation before handler entry;
   do not expose a second public CLI through legacy_main.py. Preserve useful
   engine/test injection without allowing production validation bypass.
2. Add the single schema-3 normalized config model and compatible legacy-full,
   bounded-schema-1 and October-schema-2 readers. Preserve UUID, physical root,
   runtime, authority selection, every lane, optional setting, policy, custom
   asset and living document. Implement explicit init --migrate dry-run/apply
   with expected digests, byte-exact backups, preflight, config-last replacement
   and honest partial-failure/resume behavior. Refuse contradictions and unknown
   unmapped settings. Never silently rebind, untrack, reset settings or select Git
   for an unsupported Muse operation. Authority activation belongs to FPR-2.
3. Unify init/sync/status and owned-asset classification around that context.
   Retain B's confined atomic I/O, captured writer context after locking and
   before replacement, pinned closing-commit reads and final reader rechecks.
   Preserve existing canonical NEXT on migration/sync; publish accepted legacy
   prompt text only through next-write. Extend the runtime digest to all newly
   reachable owned executable code/resources. Refresh this installation's
   runtime binding explicitly when required, preserving identity and NEXT.
4. Restore bound automatic Cursor session-start and session-end NEXT display.
   Both must read the same canonical service as manual ok next, without PATH or
   neighboring-runtime fallback, governance regeneration or HANDOVER scraping.
   Preserve Claude/Codex integrations with truthful instruction-triggered
   bookends; do not invent native lifecycle APIs or claim unverified host support.
   Install/test hooks only in newly created disposable repositories in this wave.

Run the relevant existing supported and migration/bookend checks against the
integrated entrypoint, including deterministic R1/R2, stale-digest/concurrent CAS,
unborn/exact closing commit, copied launcher/hook and two-repository isolation
cases. Add meaningful missing migration/dispatch/event cases. Use a nonrepository
fixture parent and this installation's conventional venv. Preserve historical
tests and failure evidence; map changed contracts explicitly. Do not rerun the
completed bounded independent review, installation/rollback exercise or pilot.

Do not implement the Muse/mirror/multi-lane activation wave or remaining product
surface wave here. No consumers, providers/network, real-consumer hooks, live
mirror/export, push, main merge, tag, publication, release or deployment. Do not
restore OCI, native/Mach GSR, sole-writer storage, identity bridges or packet-chain
prerequisites. Keep the plan's three implementation waves, one combined FPR-4
validation and one independent FPR-5 review; add no review-only handoff.

Close with focused evidence, a source-selection/test-disposition map, paired
ROADMAP/HANDOVER updates and one canonical FPR-2 successor through the bound
next-write using then-current context and expected prior digest. Make the coherent
local FPR-1 feature commit after checks; record any necessary mechanical repair
within this wave. Validate NEXT from disk after the closing commit. Report exact
changes, checks/failures, remaining owner choices, commit ID and validated next
prompt. Do not call the complete product restored or release-ready after FPR-1.
