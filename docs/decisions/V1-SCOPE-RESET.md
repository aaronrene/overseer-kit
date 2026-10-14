# Bounded v1 recovery decision — 2026-10-14

The current owner request and October 6 recovery handover replace the old
sole-writer/NXR-GSR NEXT and per-step packet chain. This is a local implementation
milestone, not a release, remote publication, or consumer pilot.

Trust the local OS and administrator. Retain physical repository-root and UUID
binding, deterministic isolated launchers, ordinary Python venv symlinks, canonical
`docs/NEXT.md`, validated read-only status/NEXT, and one confined atomic NEXT
writer. Bind repository, branch, lane, model, action ID and action kind; refuse
stale or contradictory state. Init preserves living documents; sync refreshes
owned launcher assets without inventing NEXT. Per-file replacement uses a sibling
temporary file, fsync and no-follow checks. Malicious same-UID/root actors are
outside this contract.

OCI registries/receipts/generations/transactions/upgrades/recovery, APFS/UID-599
sole writers, native/Mach GSR, historical volume identity bridges and new evidence
packet chains are superseded for v1. None will be ported. Existing source/tests
remain preserved. Other legacy features are outside this first supported CLI
milestone, not silently erased or declared architecture failures. The supported
matrix identifies retained tests and replacements before claiming green.

The first public surface is `status`, `init`, `sync`, `next`, and `next-write` on
POSIX Git checkouts/worktrees. Legacy Muse adapters remain preserved and tested;
native Muse revision authority is not claimed by this milestone. The original
Muse history stays untouched. No CLI path may fall back to a neighboring runtime.

Base `d47291d5d9030de5ebef713da95efa978c4d8c6e` was compared directly with local
Muse AFF `sha256:8461d44b77376fbf06fa7c3e085d309e3010fd8d5886d63c63e69ce118811ad4`.
Local Muse main `sha256:80c922b95203a49a07d1706db41ac051a91414bff298d83739df87028610cec1`
is its ancestor (21 commits including endpoints). Of 846 snapshot paths, 835
match byte for byte, six contain the Muse branch-command compatibility repair
and corresponding tests, and five omitted paths are generated Tauri schemas or
the local bridge sentinel. No unexplained implementation divergence was found.
This is local evidence, not a statement about remote freshness.

The original dirty checkout is preserved in
`../RECOVERY-SNAPSHOTS/20261014T121404Z-v1-recovery`: complete checkout including
Git/Muse, binary patches, all 58 untracked paths, 143 committed refs in a bundle,
the prior OCI snapshot and NXR/GSR history. Archives and hashes were reopened;
bundle clone/fsck and ref equality passed. This is local, not off-device storage.

The requested branch already held later work. Under the owner's instruction to
proceed at maintainer discretion, use the separate clean worktree
`overseer-kit-v1-recovery-20261014`, branch `feat/overseer-v1-recovery-20261014`.
Preserve the existing recovery branch/worktree. Selective code reuse is limited
to the bounded implementation at `2bfa698` and CLI fixes at `b2a0977`; their old
completion claims and NEXT are not current authority.

Local commits are authorized after verification. No network/provider access,
push, mirror, main merge, release, deployment, real-consumer hook activation or
pilot. Final v1 still needs independent architecture/build review, a clean
installation/current-previous rollback exercise, and a separately authorized
noncritical pilot. Keep the recovery attempt bounded; if repository-bound status
and NEXT require superseded machinery, stop rather than expanding architecture.
