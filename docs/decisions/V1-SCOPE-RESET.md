# Bounded v1 scope reset — 2026-10-08

## Owner correction and current authority — 2026-10-08

The owner explicitly clarified that the reset was meant to remove OCI complexity,
not MuseHub authority or Muse-to-GitHub mirroring. The earlier interpretation
excluded more than the owner intended. That exclusion and the resulting Git-only
completion/publication recommendation are superseded. The original record below
is retained to explain what was implemented and tested; it is not evidence that
the owner consented to excluding Muse.

Intended v1 retains the repository/UUID/lane/NEXT protections and offers a
per-repository choice: Git/GitHub only, or MuseHub as the shared source of truth
with controlled GitHub mirroring. Git-only is an ongoing supported mode, not a
temporary migration stage. Native Muse authority drives freshness for Muse-managed work;
adding a mirror script alone is insufficient. OCI, discarded storage/security
machinery, and packet chains remain excluded. Other old features are dispositioned
individually in the [restoration audit](../validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08),
not automatically reinstated.

The completed audit authorized fixtures, documentation, read-only remote
inspection, and next-write. It did not authorize production implementation,
publication, original Muse ref mutation, consumer access, or hook activation.
The preserved release branch is on hold. The audit supplies the restoration
milestones; the subsequent clarification below supersedes its budget stop.

## Subsequent owner clarification: mode choice and no session ceiling

The owner explicitly removed any session limit and directed the planned local
restoration to proceed while preserving both operating choices. Earlier five-to-
eight-session language and the audit's budget-approval NEXT are historical and no
longer constrain work. Do not invent a replacement cap or request another extension.
Milestones remain useful for testing and truthful progress, not as a work allowance.

Git/GitHub-only users must be able to stay in that mode indefinitely without Muse,
a MuseHub account, background network checks, or automatic conversion. MuseHub+
GitHub users explicitly select Muse authority and receive a controlled one-way
distribution mirror. The kit project's own Muse-first source-of-truth decision
does not force that choice on consumers. Any transition is explicit, preserves
identity/documents and existing edits, and must have tested rollback behavior.

Local R1–R3 restoration is authorized. R1 is the next implementation milestone;
R2 repairs mirroring and R3 validates source reconciliation and installation/
rollback. Completion is determined by evidence and acceptance criteria. Removing
the session cap does not claim technical limits are solved or authorize remote
writes, consumer access, original Muse ref changes, or automatic hook activation.

## Original implementation decision — historical record

The owner's October 6 recovery handover and October 8 implementation request
supersede the old NEXT, freeze chains, and security prerequisites. This is session
1 of a five-to-eight-session attempt. By session 2, status and NEXT must work
across two disposable repositories or the attempt stops or becomes a smaller tool.

V1 is a local repository and handoff utility. Trust the OS and administrator.
Retain explicit physical-root binding, one persistent UUID in config, canonical
`docs/NEXT.md`, read-only status/NEXT, a confined atomic NEXT writer, strict
repository/branch/lane/model/action ID/action-kind checks, deterministic imports,
a conventional venv, and protection from stale state and ordinary mistakes.
The first implementation supports local Git checkouts and worktrees. Muse history
is preserved; Muse-only command integration is deferred, not silently treated as Git.

The public command set is `status`, `init`, `sync`, `next`, and `next-write`.
Initialization preserves existing living documents. Sync refreshes the small
repository-bound launcher and optional fixture hooks; it never invents a NEXT.
The writer requires explicit context and the prior NEXT digest. No command pushes,
merges, deploys, or runs the prompt. One architecture review and one completed-build
review remain for final v1; this implementation does not claim independent review.

OCI registries, receipts, generations, transactions, automatic recovery, native or
Mach GSR, sole-writer storage, identity bridges, and packet chains are superseded.
The old hosted/desktop product, multi-repo orchestration, automatic governance
rewrites, freeze/ledger gates, and publishing commands are deferred from this small
CLI. Their sources, tests, and evidence remain historical, not release gates.
Tests for retained behavior must be replaced or retained explicitly, not erased
because they failed. The supported matrix and raw baseline results live in
`docs/validation/V1-RECOVERY.md`.

Base: Git `d47291d5d9030de5ebef713da95efa978c4d8c6e`. Local Muse main
`sha256:80c922b95203a49a07d1706db41ac051a91414bff298d83739df87028610cec1`
is an ancestor (21 commits including endpoints) of AFF
`sha256:8461d44b77376fbf06fa7c3e085d309e3010fd8d5886d63c63e69ce118811ad4`.
Candidate comparison against that 846-entry snapshot found 835 byte-identical
files, six deliberate Muse CLI compatibility changes (adapter and five tests),
and five omitted generated/local files (four Tauri schemas and bridge sentinel).
No unexplained implementation divergence remains. This is local reconciliation,
not a claim about current remote Muse state. No Muse refs were changed.

The dirty original checkout, all local committed refs, Muse history, untracked
files, binary patches, permissions, prior snapshot, and NXR/GSR evidence were
archived and verified at
`../RECOVERY-SNAPSHOTS/20261008T122430Z-v1-recovery` (21,213 entries; 153 bundle
refs; reopened hashes/modes and bare-clone fsck passed). Originals remain.
This local recovery copy does not authorize deletion or claim off-device backup.

Work occurs only in `overseer-kit-v1-recovery`, branch
`feat/overseer-v1-recovery`. Local commits are authorized; no push, mirror, main
merge, release, deployment, consumer activation, or pilot is authorized.
Remaining final-v1 work: independent reviews, clean install/current-previous
rollback exercise, and a separately authorized noncritical consumer pilot.
