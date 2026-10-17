# Independent bounded v1 recovery review — 2026-10-14

**Verdict: FINDINGS — milestone acceptance blocked by R1 and R2.** The independent
architecture/completed-build review is complete; findings repair is the successor.
No product fixes were made in this review. Test passes do not establish final v1.

Reviewed `d8f10d8ebaca3c015997f5eee205cca1cf8043fd` against
`d47291d5d9030de5ebef713da95efa978c4d8c6e`. Physical cwd and Git top-level matched
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, configured name `overseer-kit`, UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`. The initial worktree was clean. Bound status
validated runtime `1.0.0.dev1`, digest
`6fbdec4ece741f2407eb20b72f781228a6cb453ec67597cad44f22a5e8feb923`.

## Actionable findings

### R1 — P2: revalidate writer context after waiting for the NEXT lock

[cli/v1.py](../../cli/v1.py), lines 235–249: branch/HEAD and candidate validation
precede the blocking directory lock. After acquiring it, publication checks only
the old NEXT digest. An ordinary concurrent Git operation can therefore invalidate
the captured context without preventing replacement.

Reproduced with the real CLI in two disposable repositories: initialize, capture
status/digest, hold an exclusive flock on `docs`, start a fully bound `next-write`,
then switch branch or make an empty commit while the writer waits. Release the
lock. Both writers exited **0**, reported `ok: true`, and replaced the old NEXT.
Immediate readers exited **2**, respectively `next_branch_mismatch` and
`next_stale_head`. No implementation mocking was used for these two cases.

Repair: compare the captured repository/config/runtime and branch/HEAD context
again after lock acquisition and before replacement; refuse changed context while
preserving the old NEXT. Do not silently rebase an already prepared prompt onto
a new HEAD. Add deterministic branch/HEAD-change regression coverage alongside
the existing competing-NEXT-writer test. Keep the trusted-host scope and ordinary
file primitives; no new storage/security subsystem is needed.

### R2 — P2: use one immutable revision for closing-commit validation

[cli/v1.py](../../cli/v1.py), lines 214–222: freshness captures `current`, but the
parent and committed-byte checks independently resolve mutable `HEAD`. They can
combine evidence from two commits and accept a NEXT valid in neither.

Deterministic disposable-fixture reproduction: prepare candidates A and B through
the writer at H0. Commit A as H1; put B back in the working tree. Reading B refuses
because H1 contains A. During a read, commit B as H2 immediately after the real
H1 `rev-list` call, using a test-only wrapper around `git`. The reader combines
H1's parent H0 with H2's B bytes, exits **0**, and prints B. Stable reads before
and after both exit **2** with `next_stale_head`; H2's parent is H1, not H0.

Repair: use the captured full commit ID for both parent lookup and blob lookup,
and consistently check repository/branch/HEAD context before emitting a prompt.
Add a deterministic regression for this mixed-revision case while retaining the
valid first-commit and single-closing-commit cases. Validation must remain read-only.

## Verification and scope

- Complete supported suite, local Python 3.14.4 `.venv`:
  `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider --junitxml=/private/tmp/overseer-v1-independent-review-20261014.xml`
  — **153 passed in 104.94 seconds; zero failures, errors or skips**. This includes
  34 isolation tests in both directions and 55 retained original tests.
- Physical-root/UUID and runtime binding, copied config/NEXT/launchers/hooks,
  environment poisoning, conventional venv symlinks, missing/malformed NEXT,
  stale expected digests and stable branch/HEAD refusal passed. An extra fixture
  snapshot confirmed repeated status/NEXT reads preserve bytes, modes and mtimes,
  including `.git` files.
- Atomic-write coverage passed for sibling replacement, no-follow confinement,
  hardlinks, prepublication failures, concurrent CAS writers and post-replacement
  directory-fsync failure. Per-file sync is explicitly nontransactional; a failure
  after replacement may leave complete new bytes. R1 concerns context freshness,
  not partial-file publication.
- Independently compared the inventory against Git base objects: exactly all
  **393** original test/support paths and their current bytes match. The preserved
  `cli/legacy_main.py` also matches the base entrypoint exactly. Historical suites
  remain non-gating, not green. The recorded base result remains 1,391 passed /
  104 failed (68 socket denials, 16 missing-cryptography, nine path/fixture and
  11 other failures); that historical run was not repeated or waived here.
- R1/R2 are product findings, not sandbox restrictions. A later probe initially
  hit host `ENOSPC` before execution. Removing only this review's disposable pytest
  fixtures restored enough space to finish it; the JUnit XML was retained. No
  supported failure was excused as an environment restriction.

The bounded architecture otherwise stays within the scope reset. No older dirty
worktree, real consumer, provider/network, push, mirror, main merge, release,
deployment or pilot was accessed. No OCI/native-GSR/sole-writer/identity bridge
or packet-chain machinery was restored. Clean installation/current-previous
rollback remains pending after findings repair; a pilot still needs separate
authorization. This completed review must not be queued again.
