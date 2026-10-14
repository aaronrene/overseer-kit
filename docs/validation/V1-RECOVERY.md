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

## Clean source installation and rollback — 2026-10-14

Action `OVERSEER-V1-RECOVERY-INSTALL-ROLLBACK-1` began with clean HEAD
`348e0f323a3b17cd5022a1bfd56fa09a6831c51f`. Physical cwd and Git top-level matched
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`, branch
`feat/overseer-v1-recovery-20261014`, configured name `overseer-kit`, UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`. All were printed and checked before work.
The independent architecture/completed-build review is complete and was not
repeated. Its original findings verdict remains unchanged; R1/R2 author repair
evidence remains separately recorded above.

**Clean source installation and current-to-previous-to-current rollback passed
all 43 exercise checks.** Both builds came exclusively from this worktree's
committed Git objects using `git archive`, with all extracted source files and
modes compared after each installation. The previous commit is the current
commit's direct parent; it has the same runtime as the independently reviewed
implementation and retains that implementation's known R1/R2 findings.

| Build | Exact source commit | Runtime SHA-256 |
| --- | --- | --- |
| Current and recovered current | `348e0f323a3b17cd5022a1bfd56fa09a6831c51f` | `b7fa1921fcb586ac6fcf8422f094fe20f9f9a438f64eecdaddd97d347115db95` |
| Previous | `333f81e9bf847dcd418b305b931b1279da3c7ade` | `6fbdec4ece741f2407eb20b72f781228a6cb453ec67597cad44f22a5e8feb923` |

Both report version `1.0.0.dev1`; the runtime digest distinguishes their code.
The [machine-readable evidence](install-rollback-results.json) includes archive
and source-manifest hashes, offline dependency file hashes, fixture identity,
transition NEXT digests, and recovered-current status. The
[reproduction script](v1-install-rollback.py) creates only new disposable
installation and Git repository directories. It is validation machinery, not a
product installer or a new storage protocol.

The installations used fresh Python 3.14.4 venvs with ordinary interpreter
symlinks and no pip bootstrap. Only runtime dependency PyYAML 6.0.3 was copied,
byte-verified, from this worktree's local `.venv`; no `.pth`, editable finders or
bytecode were copied. Import origins and each venv prefix were checked. The active
venv's bytes, modes, symlinks and mtimes stayed unchanged across both source
transitions. Removing its interpreter link produced the expected no-fallback
refusal; the probe restored that link before rollback.

The exercise demonstrated:

- Init preserved existing ROADMAP and HANDOVER, created a persistent fixture UUID,
  and bound the physical repository and installation roots. Repeated init was a
  no-op. A symlink selector resolved to the same physical repository.
- Cwd and explicit `-C` status/NEXT reads through source and bound launchers
  preserved bytes, modes and mtimes, including Git files and directories. Reads
  supplied explicit UUID, branch, lane, model, action ID/kind and NEXT digest.
- Copied config, a changed UUID, a bound launcher targeting another repository,
  and an identical runtime at another installation path refused. Even explicit
  sync from that other installation refused; no automatic rebind was introduced.
- Source was replaced at one fixed physical installation root, preserving its
  venv. In both directions, status, NEXT, init and bound next-write refused
  `runtime_changed` before refresh. Dry-run changed nothing and proposed only
  `.overseer/config.yaml`; explicit bound sync changed only that file. Both
  living documents and NEXT retained their bytes, modes and mtimes. UUID and
  repository/runtime roots stayed fixed. Repeated sync was a no-op.
- Bound next-write succeeded on current, previous and recovered-current source;
  stale expected digests refused without mutation. Each fixture closing commit
  was followed by validated readback. Explicit launcher-mode repair also passed
  without changing NEXT or living documents. Final fixture status is clean and
  uses the current runtime digest above.

Rollback operability **does not certify the previous build free of R1/R2**.
No concurrent Git mutation was injected into that build during this exercise;
its known writer-context and mixed-revision reader limitations remain. This is
source maintenance during quiescence at a fixed installation root, under the
existing trusted-host contract. Source replacement is not transactional and sync
remains per-file atomic and rerunnable. No packaged installation, automatic
rebinding, concurrent installation replacement or new recovery service is claimed.

Reproduce offline from this bound worktree, using a new output path each time:

```sh
.venv/bin/python -I -B docs/validation/v1-install-rollback.py \
  --source /Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014 \
  --output .overseer/scratch/validation/install-rollback/reproduction
```

The recorded run used `exercise` in place of `reproduction`. Full subprocess
arguments, outputs and exit codes are retained in ignored
`.overseer/scratch/validation/install-rollback/exercise/commands.json`; its hash
is in the committed evidence. The exercise log and result JSON are retained too.

### Supported suite and disposition

The complete supported suite used this worktree's local Python 3.14.4 `.venv`
with pytest 9.1.1. **173 passed in 130.93 seconds; zero failures, errors or skips.**
No product failure or sandbox restriction remained in this run. Test selection
and product code were unchanged. Raw logs/XML are retained under
`.overseer/scratch/validation/install-rollback/`; both runs' counts, timings,
commands and artifact hashes are appended to [test-results.json](test-results.json).

The first complete attempt was **171 passed / 2 failed in 125.36 seconds**. This
was a maintainer fixture-placement error: `--basetemp` was inside the recovery Git
checkout. Both directions of
`test_cwd_and_explicit_C_select_only_intended_repository` expect the fixture parent
to be outside a repository, so their final bare `next` call correctly discovered
the recovery repository and succeeded instead of refusing. This is neither a
product fix nor a sandbox waiver. The initial log/XML remain as
`supported-nested-basetemp.{log,xml}`. The unchanged complete suite passed with a
new `/private/tmp` fixture root:

```sh
SUITE_FIXTURE_ROOT=$(mktemp -d /private/tmp/overseer-v1-install-rollback-suite.XXXXXX)
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  --basetemp="$SUITE_FIXTURE_ROOT/fixtures" \
  --junitxml=.overseer/scratch/validation/install-rollback/supported.xml
```

All **393** historical test/support files retain their inventory hashes. The
historical baseline remains **1,391 passed / 104 failed** with its original
disposition: 68 socket denials, 16 missing-cryptography, nine path/fixture and 11
other failures. It was not rerun or declared green. The independent review file
still hashes to `d6bd4958fcade51005bede1b01efbd29b6c64c3b7c5fdf14c147e133d0fc90e0`.
Shell syntax and `git diff --check` passed. No older worktree, real consumer,
network/provider, push, mirror, main merge, release, deployment or pilot was used.
No superseded architecture was restored. There is no bounded installation blocker;
a noncritical pilot still requires separate owner authorization. Final v1 is not
established by these passes.

### Successor and local closeout

Published exactly one successor in this recovery repository through its bound
`.overseer/bin/ok next-write`: `OVERSEER-V1-RECOVERY-PILOT-AUTHORIZATION-1`, kind
`stop`, model **GPT-6 Astra**, reasoning **Extra High**. The expected old NEXT
digest was `a85a75b6be582edb9c15b2990423559454ae323eab919ec643b7714cf0a11ce1`;
the new digest is `8c28a7f77072a620f9f40204bfbd0edf2184bfa56f405aa4823a893e1b80e44d`.
Readback with explicit UUID, branch, lane, model, action ID/kind and new digest
passed at base HEAD `348e0f323a3b17cd5022a1bfd56fa09a6831c51f`. ROADMAP and HANDOVER
were updated together. The canonical prompt is only in `docs/NEXT.md`; it stops
pending separate owner authorization naming a noncritical pilot target and
permitted operations. This handoff authorizes no consumer access or pilot.

Evidence and handoff form one local closing commit. Product source, runtime
binding, supported test selection and historical tests were not changed by this
maintenance action. The independent review remains complete, and no new review,
release or final-v1 certification is claimed.
