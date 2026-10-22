# R2 — independent re-review of the R1b delta (F1 and F2)

**Verdict: PASS.** No blocking findings. F1 and F2 match the frozen spec.
The saved E2 and E3 runs contain only the four superseded failures. The R1b
commit stays inside the R1 file list.

- Reviewer: Grok 4.7, Thinking, this session. This session did not write or
  change commit `68952c7`. This is an AI review, not a human audit.
- Date: 2026-10-21.
- Checkout: `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-knowtation-compat-20261020`
- Branch: `fix/knowtation-migration-compat-20261020` (no upstream; not pushed).
- Head: `68952c7be497a8a9466da267a8359755827fc795`
- Range reviewed: `d54a228..68952c7`. The F1/F2 build is `68952c7` (parent
  `8f23721`). The earlier code commit in the range is `30f5cb4`, already
  covered by `MIGRATION-COMPAT-RC11-INDEPENDENT-REVIEW.md`.
- Frozen spec: `docs/reviews/MIGRATION-COMPAT-RC11-R1-SPEC.md` (frozen at `8f23721`).
- Build record: `docs/reviews/MIGRATION-COMPAT-RC11-R1-BUILD.md`.
- Method: read the spec, build record, roadmap, handover, and the `68952c7`
  diff. Parsed the retained JUnit and time logs under `/tmp/r1b-scratch`
  (written before the 07:25 commit: E2 at 06:32, E3 at 07:22). Did not re-run
  E2 or E3. No code edits, pushes, PRs, merges, installs, dependency changes,
  or ledger writes. Did not open knowtation, bornfree-hub, or the N1 worktree.

Instruction-triggered bookend: `.overseer/bin/ok -C` this checkout
`next --lane thinking` refused with `launcher_repository_mismatch` (exit 2).
That matches spec fact 12. No replacement task was taken from HANDOVER.

The build record's own "build verification pass" is the builder's same-commit
check. This file is the separate re-review.

## 1. F1 — reviewed Muse pair, not an rc5-only probe

`tools/ci/supported_v1.py` matches spec §2.1:

- `MUSE_SOURCE_SHA256` is gone. `KIT` is inserted on `sys.path` only when
  missing (`supported_v1.py:16-18`). `Refusal`, `MUSE_RUNTIMES`, and
  `bounded_run` come from the shared CLI modules (`:19-20`).
- `COMPATIBILITY_TESTS`, `PROBE_TIMEOUT = 60`, `PROBE_LIMIT = 4096`, and
  `PROBE` match the spec text (`:22-38`), including the isolated-venv and
  in-prefix assertions.
- `muse_runtime` (`:43-78`) refuses in the specified order: probe failure
  (`Refusal`, `OSError`, `subprocess.SubprocessError`, or non-zero exit) →
  `muse_probe_failed`; malformed ASCII/JSON/shape/version/digest →
  `muse_probe_output_invalid`; unknown version →
  `muse_version_unreviewed: <version>`; wrong digest →
  `muse_source_digest_unreviewed: <version>`. The version is echoed only after
  it matches `[0-9A-Za-z.+-]{1,64}`. The child is started with a list argv,
  `-I -B -c`, `cwd='/'`, and an environment with no `PYTHON*` or `MUSE_*` keys.
- `main` (`:81-112`) keeps the separate-venv checks, adds both compatibility
  files to the required-file loop, appends them after the retained selection,
  and calls `parser.error` before `subprocess.call` when the pair is refused.
  `docs/validation/fpr3/retained-selection.json` is not in the diff.
- `.github/workflows/supported-v1.yml` is byte-unchanged from `d54a228` through
  `68952c7`. No hosted rc11 job was added (spec §2.6; A1 stays queued).

`tests/muse/conftest.py:11-49` adds `MuseRuntime`, `rebind_pair`,
`muse_runtime`, and `rebind_runtimes`. `muse_python` returns
`muse_runtime.python`. The missing-option `pytest.fail` text and the
`is_absolute()` / `exists()` checks are unchanged. `rebind_pair` asserts
exactly one other allowlist entry. `pytest_addoption` and `muse_root` are
unchanged. The `muse` fixture's only edit is moving `import subprocess` into
the fixture after the module-level import was removed; the command and
environment are the same.

`tests/muse/test_runtime_rebind.py` renames the two rc11-specific tests, takes
`current, stale` from `rebind_runtimes` (`:29-37`, `:104-118`), and passes
`muse_runtime.version` into the unreviewed-runtime script (`:247-270`). Drift
tests still assert exit code 2 only (`:197`). That is F7, left for H1, as
§2.3 requires.

`tests/muse/test_reviewed_runtime_matrix.py` is I1, I2, and I5: probe/reader
agreement under 15 seconds, both `rebind_pair` directions plus the third-entry
`AssertionError`, and the FPR-4 successor called as `_mirror_successor`.
`tests/fpr4/` and `tests/muse/test_mirror.py` have an empty diff from
`99e2e5b` to `68952c7`.

`tests/v1/test_muse_artifact.py:131-133` pins the rc5 artifact digest to
`MUSE_RUNTIMES['0.2.1rc5']`.

`docs/MUSE-RC11-COMPATIBILITY.md:103-115` is the spec §2.7 section.
`tools/ci/MUSE-RC5-RECOVERY.md:45-48` is the specified sentence.

Git-job tests `tests/v1/test_supported_v1.py` cover U1–U9, S2, S3, X3, and X4.
E2's JUnit records 27 passed cases for that module, including both allowlist
pairs, both cross-digest directions, 12 malformed outputs, exit 1 and mode
`0o644`, the selection order, the missing compatibility file, the shared
allowlist object, the 8 MiB bound, the killed `sleep` pid, the `Popen` spy,
and the stripped environment.

## 2. F2 — hint-first recovery, rebind only

`cli/product_migration.py:315-349` matches spec §3.1:

- `DEFAULT_RECOVERY` is the old sync sentence. `RECOVERY` is
  `[ -:<-~]{1,256}` with `fullmatch` (printable ASCII except `;`).
- An invalid `recovery` raises `Refusal("recovery_hint_invalid")` before
  `_updates`, the lock, or any write, including `dry_run=True` (`:325-326`).
- `recovery is None` keeps the old bytes, using `DEFAULT_RECOVERY` (`:345-347`).
- A supplied hint is placed first (`:348-349`). Both raises use `from exc`.
  An empty `completed` list re-raises the original exception (`:350`).
- The rest of the module is unchanged. `import re` was already present.

`cli/product_authority.py:10-12` is `REBIND_RECOVERY`. The only call-site edit
is `rebind_muse_runtime` passing `recovery=REBIND_RECOVERY.format(backup=backup)`
(`:169-170`). `backup` remains `.overseer/local/rebind-` plus the config digest
(`:121`). Adopt (`product_authority.py:259`), init (`cli/v1.py:496`), sync
(`product_migration.py:742`), and upgrade-regime (`cli/product_upgrade.py:44`)
pass no hint. An `ast` scan is I3 and passed.

`docs/MUSE-RC11-COMPATIBILITY.md:82-98` replaces the old "On interruption
inspect" wording with the spec §3.4 text, including the concurrent-edit save
step. The "shared directory lock" sentence at `:82-83` is still there (F4,
left for H1).

`tests/v1/test_apply_mapping_recovery.py` covers U10–U16, S1, I3, and DI2.
E2 records 27 passed cases: the byte-identical default message, the hint-first
message, all nine invalid hints on both dry-run values, the 256-character
accept, the first-row re-raise, `stale_write` preservation, the 211-character
template (`test_rebind_recovery_template`), the 500-row bound, the five-call
scan, and the sync message derived from the dry-run `changed` list.

Muse tests in `test_runtime_rebind.py:274-528` cover DI1 (six points), DI1a,
DI3, DI4, X1, S4, and E1. E3 records 29 passed cases in that module and 3 in
the matrix module. `follow_hint` (`:77-84`) copies launcher, lock, then config
with `shutil.copyfile` and sets each restored mode from
`assets[].before.mode`, which is the §3.4 operator step the mode assertions
require.

## 3. E2 and E3 failure sets

Parsed from the retained JUnit, not from the build record's summary alone.

| Run | JUnit | tests | failures | errors | skipped | sha256 |
| --- | --- | --- | --- | --- | --- | --- |
| E2 | `/tmp/r1b-scratch/git.xml` | 770 | 2 | 0 | 0 | `7ca8e89c2d890a40d13ec22eddc169f98022c09f268254f0115693bf38d42a9c` |
| E3 | `/tmp/r1b-scratch/combined.xml` | 971 | 4 | 0 | 0 | `7554b83887db92c2ab1a2671c04d87c4caa1be0d80015d277629e4950500f8c7` |

E2 failures, and only these:

- `tests.v1.test_adoption::test_fresh_standalone_git_install_without_muse`
- `tests.v1.test_commands::test_unsupported_commands_cannot_run`

E3 adds only:

- `tests.muse.test_handoffs::test_native_linked_worktree_own_branch_and_checkout_identity`
- `tests.muse.test_mirror::test_add_change_delete_and_no_content_source_commit`

Those four names are the superseded rows at `docs/reviews/FPR-5-REVIEW.md:267-270`.
Stdout tails match the build record: E2 `2 failed, 768 passed in 1185.38s`;
E3 `4 failed, 967 passed in 2970.81s`. Wall times in the `time -p` logs are
real `1185.69` s and real `2971.23` s. E3 stderr is:

`supported_v1: reviewed Muse 0.2.1rc11 c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe`

Inside both JUnit files, with zero failures: legacy migration 15, historical
prompts 3, `test_supported_v1` 27, `test_apply_mapping_recovery` 27. E3 also
has `test_runtime_rebind` 29 and `test_reviewed_runtime_matrix` 3, all passed,
including `test_real_rebind_preserves_settings_source_history_and_publishes_separately`,
`test_linked_checkout_uses_restored_footprint_contract`, all six DI1 points,
E1, and S4.

Focused logs match the build record: 66 passed, 48 passed, 63 passed with the
one superseded adoption failure, 18 passed in 26.38 s, and 32 passed in 320.34 s.
An earlier muse log (`muse-rebind.txt`, 06:06) failed E1 and S4 on a status
exit-code assert. The committed E1 test (`test_runtime_rebind.py:525-527`)
asserts `footprint_integrity.ok` and `footprint_coverage.ok`, which is what
spec E1 requires, and that test passed in the later 32-case run and in E3.

rc5 was not executed. The build record says the rc5 direction is source-only.
`rebind_pair('0.2.1rc5')` is asserted in `test_reviewed_runtime_matrix.py:33`.
No hosted run is claimed.

## 4. Scope

`git diff --name-status 8f23721 68952c7` is exactly the spec §6.1 list:
the two CLI modules, `supported_v1.py`, muse conftest and rebind tests, the
artifact test, both docs, the three new test modules, the build record,
`docs/ROADMAP.md`, and `docs/OVERSEER-HANDOVER.md`.

Commits `a7ae00c`, `d96c3e1`, `3254b41`, `99e2e5b`, and `8f23721` touch only
roadmap, handover, the prior review, and the frozen spec. They do not
implement N1, F3–F11, A1, or D1.

- No push: this branch has no upstream, and
  `origin/fix/knowtation-migration-compat-20261020` does not exist.
- `.github/` diff from `99e2e5b` to `68952c7` is empty.
- No requirements or dependency file changes from `d54a228` to `68952c7`.
- The R1b diff adds no URL, IP address, token assignment, or `secrets.` /
  `vars.` use. The only new `/Users/` occurrences are handover checkout paths,
  which this repo already uses, and the X1 assertion
  `assert '/Users/' not in message` (`test_runtime_rebind.py:452`).
- No prepared-runtime artifact is in the diff. Roadmap and handover still
  leave consumers on `309ac668…` under D1. A1, H1, D1, and N1b stay queued
  or held. `cli/main.py`'s 300-character cap is not in the R1b diff.

Roadmap `docs/ROADMAP.md:28-29` marks R1b done on the builder's verification
and leaves R2 as NEXT. That matches spec §6.6 and §6.8. Handover counts for
E2/E3 match the JUnit.

## 5. Build-verification checks

| Check | Result |
| --- | --- |
| V1 Deliverables exist | Pass. Every §6.1 path is in `68952c7`. |
| V2 Behavior matches the spec | Pass. §§1–2 above. |
| V3 Matrix rows are real assertions | Pass. Parametrized probe, hint, and interruption cases assert the specified messages and refusals. E2/E3 contain them as passed. |
| V4 No scope creep | Pass. §4. Drift reasons were not tightened (F7 remains). |
| V5 No dropped requirement | Pass. Default sync message kept. Workflow, retained selection, and F4 wording kept. |
| V6 Governance claims | Pass. Roadmap/handover/build-record counts match the JUnit. The builder's pass is not described here as independent. |
| V7 Secrets and injection | Pass. Hint charset rejects newline, CR, `;`, ESC, and non-ASCII (U12/X2). Probe argv is a list with no `shell` keyword (X3). No new secret material. |
| V8 Claims vs artifacts | Pass. Evidence table below. E2/E3 were not re-executed in this session; the retained JUnit was parsed. |
| V9 Independent-second-review ledger | N/A. No `require_independent_second_reviewer` setting is present under `.overseer/`. This document is the requested R2 record. No ledger append. |

### Evidence

| type | sha256 | ref | notes |
| --- | --- | --- | --- |
| test_output | `7ca8e89c2d890a40d13ec22eddc169f98022c09f268254f0115693bf38d42a9c` | `/tmp/r1b-scratch/git.xml` | E2: 770 tests, 2 superseded failures, wall 1185.69 s |
| test_output | `7554b83887db92c2ab1a2671c04d87c4caa1be0d80015d277629e4950500f8c7` | `/tmp/r1b-scratch/combined.xml` | E3: 971 tests, 4 superseded failures, wall 2971.23 s, rc11 probe line |
| test_output | focused logs under `/tmp/r1b-scratch` | `git-new.txt`, `fpr1-artifact.txt`, `fpr1-adoption.txt`, `compat.txt`, `muse-rebind2.txt` | 66; 48; 63+1 superseded; 18; 32 passed |

### Findings

| ID | Sev | path:line | Claim vs reality |
| --- | --- | --- | --- |
| — | — | — | none |

## 6. Summary

The two pre-merge fixes are in the code and the tests exercise them. The
automated run accepts either reviewed Muse release instead of only the older
one, and a crashed switch-over now prints the backup restore step first. The
full runs fail only on the four cases that were already accepted as replaced.
Nothing else in that build was started: no upload, no new hosted job, and no
new packaged runtime.

R1b at `68952c7` implements frozen spec §§2–5 for F1 and F2. The CI probe and
Muse fixtures share `MUSE_RUNTIMES`. `apply_mapping` takes an optional
validated recovery hint and only `rebind_muse_runtime` supplies one. E2/E3
JUnit failure sets are exactly the four `FPR-5-REVIEW.md:267-270` nodes.
Scope is the §6.1 file list. A1, H1 (F3–F7, F11), D1, and N1 were not built.

Recommendation: treat R2 as pass. R3 is still the owner's decision to push
and open a PR. Merge to main stays a separate approval. Do not start N1b in
this checkout.
