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

## Current verification

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
