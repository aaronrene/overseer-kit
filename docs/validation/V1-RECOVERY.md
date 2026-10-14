# Bounded v1 recovery verification — 2026-10-14

The [scope decision](../decisions/V1-SCOPE-RESET.md) records preservation, local
Muse reconciliation, the clean base and the isolated feature branch. Original
dirty payloads and both preexisting worktrees are preserved. This record concerns
only the current recovery milestone, not earlier release or pilot claims.

## Clean-base result before implementation

Base `d47291d5d9030de5ebef713da95efa978c4d8c6e`, clean `overseer-kit-main-stable`.
Python 3.14.4 / pytest 9.1.1 from the original local venv; the base worktree's venv
lacked pytest (initial attempt exited before collection). No dependency download.
Executed with bytecode/cache writes disabled and Git global/system config disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit/.venv/bin/python -m pytest -q -p no:cacheprovider --junitxml=/private/tmp/overseer-v1-20261014-baseline.xml
```

**1,391 passed, 104 failed in 28.97 seconds.** Actual tracebacks identify 68 sandbox
socket bind/listen denials, 16 explicit launcher missing-cryptography failures,
nine missing-path/fixture failures and 11 other product/test failures. The last
category includes truncated/downstream failures; it is not attributed to sandbox
restrictions. See [all failing IDs](baseline-failures.json). The base remains a
failing historical suite. Test execution left its tracked worktree clean.

## Supported release matrix for this milestone

Selection is requirement-based and explicit in `pyproject.toml`. Original tests
are byte-preserved and inventoried; [test disposition](../../tests/README.md)
distinguishes superseded contracts from deferred product features. No skip or
xfail may hide a supported requirement.

| Retained requirement | Supported coverage |
| --- | --- |
| Status/init/sync, persistent identity, preservation of living docs | `tests/v1/test_commands.py` with real disposable Git fixtures |
| Canonical read-only NEXT; schema, digest, stale head/branch and expected context | Command tests, malformed/copy/missing/tamper and first/closing-commit cases |
| Two similar repositories with identical action IDs and different prompts | `test_isolation.py`, fixture parametrized in both directions |
| Cwd and explicit -C, foreign/copied config and NEXT, bound launchers and hooks | Isolation matrix, including duplicate/abbreviated selectors and copied runtime |
| PATH/PYTHONPATH/PYTHONHOME/Git environment poisoning and wrong runtime | Isolation tests and conventional symlinked-venv command test |
| Confined reads, no-follow checks, partial-write failure and stale writers | `test_integrity.py`, hardlinks, symlinks, fsync/replace failures, concurrent writers |
| Ordinary sync repair | Dry-run, missing launcher and executable-mode repair tests |
| Digest/config/path and preserved VCS adapter behavior | Original unit tests for footprint digest, config, path normalization, Git-only, Muse-only, Muse working-dir and Muse/Git adapters |
| Retained adapter integration | Original `tests/integration/test_adapter_factory.py`; mocked VCS runners, no network |
| Historical test preservation | SHA-256 comparison of all 393 original test/support files |

The new public CLI currently uses Git revision authority. Passing legacy Muse
adapter tests does not claim Muse-only CLI integration. Socket-backed hosted/app
features, legacy orchestration/review/publication commands and old handover-scrape
NEXT tests are historical/non-gating here. Their source and known failures remain.
OCI/NXH dirty tests and sole-writer/GSR evidence remain in the original snapshot;
no superseded runtime machinery was ported.

## Runtime and implementation provenance

This worktree has its own Python 3.14.4 venv with standard interpreter symlinks.
Local packages were copied offline without editable-package finders or `.pth`
files. Runtime requirements are pinned; no network/provider/consumer was accessed.
The small v1 implementation/tests were selectively recovered from `2bfa698`, with
abbreviation and executable-mode fixes from `b2a0977`. Fresh regression coverage
exercises both repository directions, those fixes and copied-runtime refusal.
Closing-commit freshness compares exact bytes. No later publication/Muse runtime
or release work was imported. `cli/legacy_main.py` preserves the original entrypoint.

## Implementation verification (before independent review)

This section preserves the implementation session's result and then-pending
review. The completed review and subsequent R1/R2 repair are recorded below.

**Milestone passed; independent review remains pending.**

| Run | Passed | Failed/errors | Skipped |
| --- | ---: | ---: | ---: |
| Focused command/integrity | 64 | 0 | 0 |
| Two-repository isolation matrix | 34 | 0 | 0 |
| Retained original unit/integration | 55 | 0 | 0 |
| Complete supported suite | 153 | 0 | 0 |

The complete supported run took 107.80 seconds (console elapsed time). JUnit
measurements and counts are in [test-results.json](test-results.json). No supported
failure was attributed to the sandbox or waived. Every original test/support
hash passed. Local raw logs/XML are under `.overseer/scratch/validation/` (ignored).

Commands use `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider`:
focused adds `tests/v1/test_commands.py tests/v1/test_integrity.py`; isolation adds
`tests/v1/test_isolation.py`; retained names the eight original modules listed in
`pyproject.toml`; complete supplies no test-path override. Each records JUnit XML.

The recovery checkout itself passed `init`, `status --json`, `next`, and both
`sync --dry-run` and `sync` (no changes). Its UUID is
`6988dc4a-5f22-454b-9d68-ac5905b383bf`. Config was explicitly rebound only here,
with the original schema preserved in `docs/archive/v1/config-before-reset.yaml`.
Automatic hooks are disabled here; only disposable fixtures received bound hooks.
Shell syntax checks and `git diff --check` passed. The pending action is one
independent architecture/completed-build review, published through `next-write`.

The [changed-file inventory](changed-files.txt) covers implementation, operating
instructions, paired living docs, test selection/coverage and preservation records.
No OCI/native/GSR/sole-writer code was ported. Remaining final-v1 work is independent
review, clean installation/current-previous rollback and an explicitly authorized
noncritical pilot. None is claimed complete by this implementation session.

Sync is per-file atomic and rerunnable, not transactional. After replacement, a
directory-fsync error reports failure even though the complete new NEXT may exist.
The trusted-host contract does not claim resistance to malicious same-UID/root.

## R1/R2 findings repair — 2026-10-14

Repair base: `333f81e9bf847dcd418b305b931b1279da3c7ade`, branch
`feat/overseer-v1-recovery-20261014`, physical root
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, configured
name `overseer-kit`, UUID `6988dc4a-5f22-454b-9d68-ac5905b383bf`. These bindings
were printed and verified before repair; the starting worktree was clean.

The [independent review](../reviews/V1-RECOVERY-REVIEW.md) is complete. Its original
**FINDINGS** verdict and evidence remain byte-identical (SHA-256
`d6bd4958fcade51005bede1b01efbd29b6c64c3b7c5fdf14c147e133d0fc90e0`). This section
records author repair evidence, not a repeated or new independent review.

- **R1:** NEXT publication captures config bytes, branch and full HEAD once. It
  revalidates physical/Git root, config/UUID/runtime and branch/HEAD after taking
  the directory lock and again after candidate fsync, immediately before atomic
  replacement. A changed observation refuses without rebasing the prompt,
  replacing old NEXT or leaving a temporary candidate behind. The existing
  expected-digest CAS and directory lock remain in place.
- **R2:** closing-commit parent and NEXT-blob lookups both use the captured full
  commit ID. NEXT, status and hook output recheck the same captured context before
  rendering/emission; status metadata uses that snapshot too. The valid unborn
  and one-closing-commit cases retain their original contract.
- **Regression evidence:** `tests/v1/test_context.py` uses real disposable Git
  repositories. A child running the isolated bootstrap signals a real busy flock
  before the parent changes branch, HEAD, config or runtime binding. A test-only
  wrapper commits H2 after the real H1 parent lookup for the mixed-revision case.
  Additional cases change context after the blob read or candidate fsync.
  Successful read snapshots include Git metadata, bytes, modes and mtimes.

Before the repair, the new cases produced **19 failed / 1 passed in 10.56 seconds**:
the old writer published and old readers emitted output despite the injected
context changes. After repair, **20 passed in 13.04 seconds**. These were product
regressions, not environment restrictions. Raw logs/XML are retained in ignored
`.overseer/scratch/validation/r1-r2-{before,after,supported}.{log,xml}`. Both focused
runs used the local `.venv` with the complete command below plus
`tests/v1/test_context.py` and the corresponding JUnit filename.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider --junitxml=.overseer/scratch/validation/r1-r2-supported.xml
```

**Complete supported result: 173 passed in 132.21 seconds; zero failures, errors
or skips.** This includes all 153 previously supported tests plus 20 new cases,
the 34-case isolation matrix in both directions, concurrent CAS, valid unborn
and single-closing-commit behavior, and 55 retained original tests. No supported
failure was waived; this run encountered no environment restriction. Counts,
JUnit timings and raw artifact hashes are appended to [test-results.json](test-results.json).
Shell syntax checks and `git diff --check` also passed.

The configured runtime was refreshed through this installation's explicit
`sync --dry-run` then `sync`, changing only its digest to
`b7fa1921fcb586ac6fcf8422f094fe20f9f9a438f64eecdaddd97d347115db95`. Ordinary venv
symlinks, repository/runtime binding, no-follow confinement and per-file atomic
writes remain. Git operations are not transactionally locked with NEXT: checks
detect observed context changes, without claiming a global Git/filesystem
transaction or resistance to malicious same-UID/root actors.

All **393** historical test/support files remain byte-identical. The original
historical disposition and baseline **1,391 passed / 104 failed** remain unchanged;
that full historical suite was not rerun or declared green. No older worktree,
real consumer, network/provider, remote operation or superseded architecture was
used. Clean installation/current-previous rollback is the successor after repair;
the noncritical pilot still requires separate authorization. Final v1 is not
claimed complete.

Exactly one successor was published through this checkout's bound `next-write`:
`OVERSEER-V1-RECOVERY-INSTALL-ROLLBACK-1`, kind `maintain`, model `GPT-6 Astra`,
reasoning Extra High. Explicit repository/branch/lane/model/action and digest
expectations passed on readback. NEXT SHA-256 is
`a85a75b6be582edb9c15b2990423559454ae323eab919ec643b7714cf0a11ce1`, based on the
repair base above for the single local closing commit. ROADMAP and HANDOVER were
updated together; the prompt remains canonical only in `docs/NEXT.md`.
