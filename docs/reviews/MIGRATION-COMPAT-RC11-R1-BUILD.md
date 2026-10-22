# R1b — build record for F1 and F2

Checkout: `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-knowtation-compat-20261020`
Branch: `fix/knowtation-migration-compat-20261020` (local only)
Frozen spec: [MIGRATION-COMPAT-RC11-R1-SPEC.md](MIGRATION-COMPAT-RC11-R1-SPEC.md)
Spec base: `99e2e5b`. Reviewed code parent: `30f5cb4`.

All pytest runs used `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`, and a
basetemp under `/tmp` (or the CI driver's `tempfile.mkdtemp` under the system
temp directory). Runs were outside the Cursor sandbox.

## 1. Focused commands (spec §6.3)

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q tests/v1/test_supported_v1.py tests/v1/test_apply_mapping_recovery.py tests/v1/test_muse_artifact.py -p no:cacheprovider --basetemp=/tmp/r1b-basetemp-git-new` | **66 passed** in 74.74 s |
| `.venv/bin/python -m pytest -q tests/fpr1/test_migration.py tests/v1/test_muse_artifact.py -p no:cacheprovider --basetemp=/tmp/r1b-basetemp-fpr1b` | **48 passed** in 58.17 s |
| `.venv/bin/python -m pytest -q tests/fpr1/test_migration.py tests/v1/test_adoption.py -p no:cacheprovider --basetemp=/tmp/r1b-basetemp-fpr1` | **63 passed, 1 failed** in 116.36 s — failure is the documented superseded `test_fresh_standalone_git_install_without_muse` |
| `.venv/bin/python -m pytest -q tests/integration/test_legacy_migration_compat.py tests/integration/test_historical_prompt_migration.py -p no:cacheprovider --basetemp=/tmp/r1b-basetemp-compat` | **18 passed** in 26.38 s |
| `.venv/bin/python -m pytest -q tests/muse/test_runtime_rebind.py tests/muse/test_reviewed_runtime_matrix.py --muse-python ~/.local/share/muse/venv/bin/python3.14 -p no:cacheprovider --basetemp=/tmp/r1b-basetemp-muse2` | **32 passed** in 320.34 s |

rc5 was not executed on this host (no rc5 venv). The rc5 direction (stale =
rc11) is verified by source only via portable `rebind_runtimes` /
`rebind_pair`. No hosted CI run was performed.

## 2. E2 — Git-only `supported_v1.py`

```text
/usr/bin/time -p .venv/bin/python tools/ci/supported_v1.py \
  --junitxml /tmp/r1b-scratch/git.xml
```

| Metric | Value |
| --- | --- |
| Wall time (P4) | real **1185.69** s |
| Pytest summary | **2 failed, 768 passed** in 1185.38 s (770 tests in JUnit) |
| Failure set | exactly `tests/v1/test_adoption.py::test_fresh_standalone_git_install_without_muse` and `tests/v1/test_commands.py::test_unsupported_commands_cannot_run` (superseded per `FPR-5-REVIEW.md:267-268`) |
| Compatibility | 15 + 3 cases present and passed |
| New Git-job tests | `test_supported_v1` 27 passed; `test_apply_mapping_recovery` 27 passed |

## 3. E3 — Combined with host rc11

```text
/usr/bin/time -p .venv/bin/python tools/ci/supported_v1.py \
  --muse-python ~/.local/share/muse/venv/bin/python3.14 \
  --junitxml /tmp/r1b-scratch/combined.xml
```

| Metric | Value |
| --- | --- |
| Wall time (P4) | real **2971.23** s |
| Stderr probe line | `supported_v1: reviewed Muse 0.2.1rc11 c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe` |
| Pytest summary | **4 failed, 967 passed** in 2970.81 s (971 tests in JUnit) |
| Failure set | E2's two, plus `tests/muse/test_handoffs.py::test_native_linked_worktree_own_branch_and_checkout_identity` and `tests/muse/test_mirror.py::test_add_change_delete_and_no_content_source_commit` (superseded per `FPR-5-REVIEW.md:269-270`) |
| New/renamed Muse | `test_runtime_rebind` 29 present/passed; `test_reviewed_runtime_matrix` 3 present/passed; `test_real_rebind` and `test_linked_checkout` present/passed |

## 4. X5 diff checks

Against `99e2e5b` for R1b code/docs (including untracked new test files):

| Check | Result |
| --- | --- |
| `git diff 99e2e5b -- .github/` | empty (0 bytes) |
| Added URLs (`https?://`) | none |
| Added IP addresses | none |
| Added `secrets.` / `vars.` | none |
| Added token/key assignments | none |
| Absolute `/Users/…` home paths | none as path values; one security assertion string `assert '/Users/' not in message` (X1) |
| Fixture hosts | no new dotted public hosts; fixtures continue to use `example.invalid` where applicable |
| Hosted rc11 job | not added (`supported-v1.yml` byte-unchanged) |

## 5. Scope confirmation

Changed only the files listed in spec §6.1. Did not implement N1, F3–F11, A1, or
D1. Did not build a prepared runtime. Consumers remain on `309ac668…`.
No push, PR, merge, install, or dependency change.

## 6. Build verification review

## Build verification — R1b round 1

**Verdict:** pass
**Frozen spec:** docs/reviews/MIGRATION-COMPAT-RC11-R1-SPEC.md
**Diff scope:** working tree vs `99e2e5b` / R1a head for §6.1 paths only

### Findings

| ID | Sev | path:line | Claim vs reality |
| --- | --- | --- | --- |
| — | — | — | none |

### Evidence

| type | sha256 / ref | notes |
| --- | --- | --- |
| test_output | E2 `/tmp/r1b-scratch/git.xml` (770 tests, 2 superseded failures) | wall 1185.69 s |
| test_output | E3 `/tmp/r1b-scratch/combined.xml` (971 tests, 4 superseded failures) | wall 2971.23 s; rc11 probe line on stderr |
| test_output | focused muse rebind+matrix 32 passed | rc11 host venv |
| test_output | focused Git new+artifact+compat | 66 + 48 + 18 passed |

Honesty `require_independent_second_reviewer` is unset/off → V9 N/A. ISR not required for DONE.

### Honest summary

R1b shipped the portable `MUSE_RUNTIMES` CI probe and Muse fixtures (F1), the
hint-first `apply_mapping` recovery path used only by rebind (F2), the named
seven-tier tests, docs, and this build record. E2/E3 failure sets match the four
documented superseded cases only. `.github/` is unchanged; no prepared runtime
was built.
