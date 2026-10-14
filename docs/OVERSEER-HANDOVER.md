# Overseer Kit handover

Current authority: owner direction on 2026-10-14 to restore the complete product
without discarding the certified safety work. The [scope reset](decisions/V1-SCOPE-RESET.md)
and [bounded certification](validation/V1-CERTIFICATION.md) remain preserved as the
record of the smaller source snapshot, not the desired full-product endpoint.
Active implementation: `overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, reconciled base `d47291d`.
Both older dirty worktrees remain untouched.

**Current successor: FPR-0 full-product reconciliation analysis.** Use GPT-6
Astra with Max reasoning. Compare, through this clean worktree's Git objects, the
complete product/lane line `feat/overseer-context-isolation` (`e9be0c4`), the
newer Muse authority/mirror line `feat/overseer-v1-recovery` (`32254cd`), and the
certified repository-bound NEXT safety line at this branch (`3ed3b7d`). Produce
one authoritative integration plan before changing product code. The plan must
restore automatic validated NEXT bookends, all maintained product commands,
per-repository lanes and optional Muse-as-authority with isolated Git mirroring,
while retaining the safer repository binding and concurrency fixes.

The owner wants a short, deliberate validation path: one architecture analysis,
focused checks during three implementation waves, one combined validation, and
one independent final review. Do not create a review cycle for every wave. Do not
touch the preserved worktrees, access consumers or perform network/remote actions
during FPR-0. The exact analysis instructions live only in `docs/NEXT.md`.

Preservation and local Muse/base reconciliation are complete. The independent
architecture/completed-build review of `d8f10d8` against `d47291d` is complete with
an original **FINDINGS** verdict, preserved unchanged. The subsequent repair of
R1/R2 at base `333f81e9bf847dcd418b305b931b1279da3c7ade` is complete: writer context
is rechecked after locking and before replacement; closing-commit checks use one
captured commit ID, and readers recheck context before output.

The latest local `.venv` complete supported suite passed **173 tests in 107.49 seconds**,
with zero failures, errors or skips. This includes 20 new deterministic regression
cases (19 failed before repair), existing concurrent CAS and unborn/closing-commit
behavior, both isolation directions and 55 retained original tests. All 393
original test/support files retain their hashes. An initial installation/rollback
validation run had 171 passes and two failures because the maintainer placed
pytest's fixtures inside this Git
checkout; those tests require a nonrepository parent. The unchanged complete suite
passed after moving fixtures to a new `/private/tmp` directory. Both runs are
recorded. Historical failures remain unresolved; no failure was waived as an
environment restriction.

Clean source installation and current-to-previous-to-current rollback are complete:
**43 disposable exercise checks passed**. Committed source `348e0f3` → `333f81e` →
`348e0f3` came only from this worktree's Git objects. Fresh symlinked venvs used
offline PyYAML from the local `.venv`. Source changed at a fixed installation root;
commands refused until explicit sync, which preserved UUID, living documents and
NEXT. Recovery restored the current runtime digest. The previous build still has
known R1/R2 limitations; rollback operability does not clear them. See
[reproducible evidence](validation/V1-RECOVERY.md#clean-source-installation-and-rollback--2026-10-14).

The owner separately authorized the **newly created test-repository pilot** at
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-v1-pilot-20261014`. It is complete:
branch `pilot/overseer-v1-20261014`, UUID `8520ff03-a248-4dbd-8f21-ec53de6c967b`,
final local HEAD `50b5a19b7d6f1c964368140ed0dc3dc91504de16`. It uses this recovery
installation's conventional `.venv` and unchanged repaired runtime. Init without
hooks, status, NEXT, sync dry-run/sync, explicit-context digest-checked publication,
stale-writer refusal and readback after two closing commits passed. The one
documentation task produced `docs/PILOT-OPERATIONS.md` in the pilot. Both pilot
summaries and its canonical completion stop are committed; final status is clean.

[Pilot evidence](validation/V1-RECOVERY.md#newly-created-test-repository-pilot--2026-10-14)
records the exact commits, digests, supported run and preservation checks. This
was one maintainer in one session in a new repository; no existing consumer
migration, sustained use, independent operator, consumer hooks or provider access
was exercised. The pilot has no remotes and Git hooks are disabled. An incorrect
digest supplied during recovery readback correctly refused; corrected readback
passed. This operator input error is recorded, not a waived product failure.

The [final certification adjudication](validation/V1-CERTIFICATION.md) is
**CERTIFIED** for repository-bound source v1 for local POSIX Git repositories
under the trusted-host model, validated on Python 3.14.4, with the public
`status`, `init`, `sync`, `next` and `next-write` surface. R1/R2 are resolved for
this claim on [author repair evidence](validation/V1-RECOVERY.md#r1r2-findings-repair--2026-10-14);
the original independent **FINDINGS** verdict remains unchanged. Historical
baseline **1,391 passed / 104 failed** remains unresolved and was not rerun.

The bounded certification is complete and must not be repeated. Its original
independent review, repair evidence, installation/rollback exercise and pilot
remain historical evidence for the smaller claim. Do not repeat the completed
[review](reviews/V1-RECOVERY-REVIEW.md), installation/rollback or pilot.
Packaged installation, other platforms, existing-consumer migration, sustained
or multi-user operation, consumer hooks and providers remain outside that claim.
The old sole-writer/NXR-GSR NEXT is superseded.

The newly authorized successor is FPR-0, kind `plan`. It may inspect repository
history and committed branch contents and may create the restoration decision
document plus paired ROADMAP/HANDOVER/NEXT closeout in this clean worktree. It may
not implement the restoration, activate hooks, access consumers, use providers or
network, push, mirror, merge, publish or deploy. The analysis must define all
later work and the single final review boundary before FPR-1 begins.

Read the exact current action with `./cli/ok -C . next`. Only `next-write` publishes
canonical `docs/NEXT.md`; do not regenerate a prompt from this summary or ROADMAP.
At turn start verify physical cwd, Git root, branch, HEAD and configured name.
Use disposable repositories for all isolation tests. Current user repository
scope overrides inherited handoffs. Validation belongs in
`docs/validation/V1-RECOVERY.md`; update this handover and ROADMAP together.
