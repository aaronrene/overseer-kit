# V1 recovery milestone — verification, 2026-10-08

**Result: milestone passed; final v1 is not complete.** Session 1 reached the
session-2 status/NEXT checkpoint across two disposable repositories. Independent
architecture and completed-build reviews are still pending. This record is the
implementation owner's evidence, not either independent review.

## Preservation and base

Original physical checkout and Git root:
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit`; repository name `overseer-kit`;
branch `feat/overseer-context-isolation`; HEAD
`e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`.

Verified local snapshot:
`/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-SNAPSHOTS/20261008T122430Z-v1-recovery`.
The archive contains 21,213 entries: complete checkout including .git/.muse/venv,
all untracked/ignored payload, operator-owned workspace file, recovery handover,
prior OCI snapshot, and NXR/GSR evidence. Separate all-ref Git bundle (153 refs),
full-index binary staged/unstaged patches, untracked archive, inventory with type,
mode, size, SHA-256, uid/gid/mtime and symlink targets, plus artifact SHA256SUMS.
Archive and untracked archive were reopened and compared; bundle verification,
reopened bare clone and `git fsck --full` passed (two dangling historical commits,
no corruption). All artifact hashes were rechecked after implementation.

All 19,418 original archived regular files rechecked byte-identical with matching
modes; symlink targets matched. An IDE `vscode-merge-base` entry appeared for the
new feature branch in shared Git config; it was removed and exact original bytes
restored. New Git worktree administration and feature refs are intentional
additions. No original payload or historical evidence was deleted. This snapshot
is local and is not an off-device backup.

Implementation worktree:
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery`; branch
`feat/overseer-v1-recovery`; base `d47291d5d9030de5ebef713da95efa978c4d8c6e`.
The [scope decision](../decisions/V1-SCOPE-RESET.md) records the exact local Muse
reconciliation: 835 identical files, six explained repair differences and five
omitted generated/local files. No remote reconciliation or Muse ref mutation.

## Clean-base results before implementation

Python 3.14.4, pytest 9.1.1; base tests used the preexisting development venv, with
bytecode and pytest cache writes disabled. Tests ran in the new untouched feature
worktree before source changes.

| Run | Result | Time |
| --- | --- | --- |
| Full original suite | 1,391 passed, 104 failed | 27.40s |
| Excluding hosted_dashboard, q1_app, q4b_ui, q3_desktop groups | 1,313 passed, 44 failed, 138 deselected | 24.77s |

Full-suite failures: 68 socket bind/listen denials imposed by the sandbox; 16
launcher missing-PyYAML failures; 9 missing paths/fixtures; 11 other product/test
failures. The filtered run still included eight socket denials in LAC tests.
These are classifications of actual tracebacks, not blanket attribution to the
sandbox. [All 104 failing node IDs](baseline-failures.json) retain their categories
and error messages. The former product has unresolved failures; it is not claimed
green. The v1 launcher/environment and canonical documents replace the retained
behavior; deferred desktop/hosted/orchestration/review/publishing defects remain
historical and unresolved.

Exact baseline commands (PY is the original checkout's `.venv/bin/python`):

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -q -p no:cacheprovider --junitxml=/private/tmp/overseer-v1-baseline.xml
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -q -p no:cacheprovider -k 'not hosted_dashboard and not q1_app and not q4b_ui and not q3_desktop' --junitxml=/private/tmp/overseer-v1-baseline-filtered.xml
```

## Supported v1 release matrix

Default pytest collection is `tests/v1` plus `tests/retained`. This follows the
retained requirements, not the result of individual old tests. Every original
test source remains byte-identical at its old path, labeled historical in
`tests/README.md` and inventoried in `tests/historical/baseline-test-inventory.json`.
A supported integrity test verifies that preservation. Dirty OCI/NXH tests remain
in the original checkout and snapshot; none were ported. `cli/legacy_main.py`
preserves the former CLI. It is outside the public v1 command surface.

| Retained requirement | Supported coverage |
| --- | --- |
| Status, init, sync; persistent UUID; living-document preservation | `tests/v1/test_commands.py` (real disposable Git repositories and worktrees) |
| Canonical read-only NEXT; strict metadata; expected repository/branch/lane/model/action ID/kind; stale state | `test_commands.py` (including malformed, copied, duplicate, missing, tampered, unborn, detached, and post-commit cases) |
| Two similar repositories with identical action IDs | `test_isolation.py` (14 matrix tests) |
| Cwd, explicit -C, copied config/NEXT, bound launchers and hooks | `test_isolation.py`, both fixture directions |
| PATH/PYTHONPATH/PYTHONHOME/Git environment poisoning; no neighboring runtime fallback; normal venv symlinks | `test_isolation.py`, `test_commands.py` |
| Confined no-follow reads/writes, hardlink refusal, raw digest, atomic replacement and fsync failures | `test_integrity.py` |
| Concurrent stale writers and readers; bounded reads | `test_integrity.py` (stress and performance coverage) |
| Retained digest module | Six unchanged tests in `tests/retained/test_footprint_digest.py`, plus v1 raw-byte digest regression |

No test skip or expected-failure marker masks a supported requirement. The retained
atomic-write and repository-scope behavior has direct executable regression
coverage rather than the old stale fixture assumptions. No socket service,
consumer repository, push, mirror, merge, release, deployment, or pilot is needed.

## Implementation results

The worktree uses its own conventional Python 3.14.4 venv with standard Python
symlinks. Dependencies were seeded offline from already installed package bytes,
excluding the original editable-package finder and `.pth`; imports resolve to
this checkout and this venv. Runtime requirements are pinned in
`requirements-v1.txt`, development requirements in `requirements-v1-dev.txt`.
Fresh network installation and current/previous rollback are future milestones.

| Run | Result | Time |
| --- | --- | --- |
| Initial v1 regression run | 56 passed, 2 failed | 41.57s |
| Focused command/write tests after correction | 45 passed | 25.72s |
| Two-repository isolation matrix | 14 passed | 22.72s |
| Complete supported suite, including later added boundary tests | **77 passed, 0 failed** | **45.27s** |

The two initial failures exposed sync accepting symlinked docs/NEXT paths. Sync
now refuses those paths before refreshing assets. Additional full-suite coverage
checks relative launchers, malformed hook events/config, dry-run recovery of a
missing launcher, linked Git worktrees, first commits, post-publication fsync
errors, and preservation of old tests.

Commands in the recovery worktree:

```sh
.venv/bin/python -m pytest -q tests/v1/test_commands.py tests/v1/test_integrity.py -p no:cacheprovider
.venv/bin/python -m pytest -q tests/v1/test_isolation.py -p no:cacheprovider
.venv/bin/python -m pytest -q -p no:cacheprovider
./cli/ok -C . status --json
./cli/ok -C . next
```

Own-checkout status and NEXT passed. The original config is preserved verbatim at
`docs/archive/v1/config-before-reset.yaml`; this worktree was explicitly bound once
to UUID `6dba88a5-029c-4136-9277-c3a0c81f31a6`. Its read-only hooks were refreshed;
no real consumer hook was activated. `git diff --check` passed.

Machine counts: [test-results.json](test-results.json). Full logs, JUnit files,
Muse comparison, preservation recheck, and SHA256SUMS are stored at
`/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-1`.

## Limits and next action

Supported: POSIX Git checkouts/worktrees, one lane and configured model per
checkout, source installation with its own venv. Muse-only command integration,
automatic config migration/rebinding, packaged installation and rollback remain
out of this milestone. Scope is a trusted local host, not malicious same-UID/root.
Sync is per-file atomic and rerunnable; it has no transaction/recovery subsystem.
Directory fsync failure after replacement reports failure even though a complete
new NEXT may already be present; readers never see a partially written file.

There are no unresolved supported-suite failures. Final v1 remains incomplete:
independent architecture and completed-build reviews, clean install/rollback,
and a separately authorized noncritical pilot are outstanding. One current action
is in `docs/NEXT.md`: **OVERSEER-V1-REVIEW-1**. Keep the five-to-eight-session cap.
