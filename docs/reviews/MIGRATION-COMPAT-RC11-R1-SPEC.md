# R1 — frozen fix spec for review findings F1 and F2

Status: **frozen.** R1a (Thinking) fixes WHAT and HOW. R1b (Auto) builds exactly
this and nothing else. The freeze-review result is in the Review record at the end.

```yaml
phase: R1
outputs:
- id: migration-compat-rc11-r1-spec
  path: docs/reviews/MIGRATION-COMPAT-RC11-R1-SPEC.md
  frozen: true
frozen_inputs:
- id: independent-review
  path: docs/reviews/MIGRATION-COMPAT-RC11-INDEPENDENT-REVIEW.md
- id: muse-rc11-compatibility
  path: docs/MUSE-RC11-COMPATIBILITY.md
- id: ci-driver
  path: tools/ci/supported_v1.py
- id: apply-mapping
  path: cli/product_migration.py#apply_mapping
- id: rebind
  path: cli/product_authority.py#rebind_muse_runtime
- id: muse-allowlist
  path: cli/v1_revision.py#MUSE_RUNTIMES
- id: cli-refusal-output
  path: cli/main.py#main
- id: test-tiers
  path: .overseer/policy/test-tiers.yaml
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
```

- Branch: `fix/knowtation-migration-compat-20261020`, local only. Spec base commit:
  `99e2e5b`. Its code is byte-identical to the reviewed commit `30f5cb4`
  (`git diff --stat 30f5cb4 99e2e5b` lists only `docs/ROADMAP.md`,
  `docs/OVERSEER-HANDOVER.md` and the review). Line numbers below refer to that code.
- In scope: findings **F1** and **F2** only. F3–F10 stay queued (H1, D1, N1, M1).
- Not allowed in R1b: pushes, PRs, merges, installs, dependency changes, hosted CI
  runs, and any change under `/Users/aaronrenecarvajal/knowtation` or
  `/Users/aaronrenecarvajal/bornfree-hub`.

## 1. Verified facts this spec relies on

Each was checked in R1a by source reading or by a scratch probe outside the
repository (`/tmp/r1a-scratch`, real Muse 0.2.1rc11 venv at
`~/.local/share/muse/venv/bin/python3.14`).

1. **The CLI truncates every refusal to 300 characters.** `cli/main.py:324-327`
   prints `'refused: ' + message[:300]`. In a real interrupted rebind (the probe made
   `.overseer/` read-only), the CLI printed only the first two backup paths and part of
   the third, 310 characters in all. Neither the reason nor the current
   "rerun explicit sync" advice reached the operator. The current 41-character advice is
   visible only when nothing but the config backup completed. The 211-character
   rebind hint (section 3.2), placed at the end as the current format would place it,
   is always cut off: even the shortest case is `22 + 109 + 27 + 211 = 369` characters.
2. **The in-process message for that interruption** was
   `partial_asset_update: <backup>/.overseer/config.yaml,<backup>/.overseer/bin/ok,<backup>/.overseer/version.lock,.overseer/bin/ok; PermissionError; config is last; rerun explicit sync after resolving drift`,
   with `__cause__` of type `PermissionError`. Completed paths appear in mapping order.
3. **Write order.** The rebind mapping is the three backups (config, launcher, lock),
   then launcher, lock and config (`cli/product_authority.py:118-121`). `_updates` keeps
   dict order (`cli/product_migration.py:303-312`), and `apply_mapping` writes rows in
   that order (`:327-329`). So whenever a live path has been replaced, all three backup
   copies already exist with the exact original bytes. The preview also refuses an
   existing backup whose bytes differ (`product_authority.py:122-125`,
   `rebind_backup_mismatch`).
4. **After that interruption,** the bound launcher refused with
   `runtime_installation_mismatch`, and a fresh preview refused with
   `rebind_custom_launcher_requires_resolution`. Copying each backup copy that exists
   over its live path (launcher, lock, then config) left only the backup files
   different from the original snapshot (bytes and modes). A new preview listed
   exactly the three live paths as changed, with a different `rebind_sha256`, and the
   apply with that new digest exited 0.
5. **Callers of `apply_mapping`.** There are exactly five, all in `cli/`:
   `product_authority.py:165` (rebind), `product_authority.py:254` (adopt),
   `v1.py:496` (init), `product_migration.py:729` (sync) and `product_upgrade.py:44`
   (upgrade-regime).
6. **The CI probe is rc5-only.** `tools/ci/supported_v1.py:42` asserts version
   `0.2.1rc5`, and `:48` asserts the digest `MUSE_SOURCE_SHA256` (`:14`).
   `tests/v1/test_muse_artifact.py:133-134` imports that constant.
7. **The tests pin rc11.** `tests/muse/test_runtime_rebind.py:24` asserts the binding
   is rc11, `:25-26` fakes rc5, `:70-71` assert rc5 to rc11, and `:211` patches the
   rc11 entry. `tests/muse/conftest.py:20-29` already accepts any allowlisted pair.
8. **The FPR-4 mirror successor is pinned to rc5 through its fixture.**
   `tests/fpr4/test_mirror_full_footprint.py:14` takes `composition_muse_python`, which
   asserts rc5 (`tests/fpr4/test_composition.py:41`). Called directly with an rc11
   interpreter, it passed (reviewer probe, kept at
   `OVERSEER_KIT/RECOVERY-RUNS/migration-compat-rc11-20261020/probes/test_rc11_mirror_successor.py`).
9. **The two new integration files need no Muse.** Run alone, Git-only and outside the
   sandbox: **18 passed in 27.17 s**. In the Cursor sandbox they fail with
   `PermissionError` on fixture `.cursor` directories; that is the sandbox, not the
   code.
10. **The stricter probe accepts the host's rc11 venv.** The probe in section 2.1
    (isolated venv, package inside the venv, JSON output) printed
    `{"version": "0.2.1rc11", "sha256": "c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe"}`.
11. **No reviewed rc11 distribution artifact exists.** The host's rc11 was installed
    from a temporary local tarball (`direct_url.json`: `file:///var/folders/…/muse.tar.gz`,
    archive SHA-256 `21caf5e8…`). The repository has a reviewed artifact contract only
    for rc5: `tools/ci/muse_artifact.py`, `muse-rc5-artifact.json`,
    `muse-rc5-source-files.json` and `requirements-muse-rc5.txt`.
12. **`ok review --freeze` cannot run in this checkout.** `./cli/ok review --freeze …
    --dry-run` refuses with `config_repository_mismatch`, and `.overseer/bin/ok` refuses
    with `launcher_repository_mismatch`. The tracked config binds the publication
    checkout (`repo.root`, `runtime.root`). Changing that binding is out of scope.

## 2. F1 — run the tests and CI under any reviewed Muse runtime

### 2.1 `tools/ci/supported_v1.py`

1. Delete `MUSE_SOURCE_SHA256` (line 14).
2. After `KIT = …`, add `KIT` to `sys.path` only if it is not already there. Then
   import `Refusal` from `cli.v1_io` and `MUSE_RUNTIMES` and `bounded_run` from
   `cli.v1_revision`. The CI driver and the Muse reader then share one allowlist
   object, with no copy of it anywhere else.
3. Add these module constants:
   - `COMPATIBILITY_TESTS = ('tests/integration/test_legacy_migration_compat.py', 'tests/integration/test_historical_prompt_migration.py')`
   - `PROBE_TIMEOUT = 60` (seconds)
   - `PROBE_LIMIT = 4096` (bytes of combined output)
   - `PROBE`, the child program below. It only measures and reports; the parent
     decides.

   ```python
   PROBE = '''import hashlib, importlib.metadata, json, sys
   from pathlib import Path
   assert sys.prefix != sys.base_prefix
   import muse
   root = Path(muse.__file__).resolve().parent
   assert root.is_relative_to(Path(sys.prefix).resolve())
   h = hashlib.sha256()
   for p in sorted(root.rglob('*.py')):
       h.update(p.relative_to(root).as_posix().encode() + b'\\0' + p.read_bytes() + b'\\0')
   print(json.dumps({'version': importlib.metadata.version('muse'), 'sha256': h.hexdigest()}))
   '''
   ```

4. Add `muse_runtime(python)` with a docstring. It returns `(version, sha256)` only
   for an exact reviewed pair, and otherwise raises `ValueError` with one of these
   reasons, checked in this order:
   1. Run `bounded_run([str(python), '-I', '-B', '-c', PROBE], cwd='/', env=env,
      timeout=PROBE_TIMEOUT, limit=PROBE_LIMIT)`.       `env` is `os.environ` without any
      key that starts with `PYTHON` or `MUSE_`. A list argv is used, never a shell.
      If `bounded_run` raises `Refusal`, `OSError` or `subprocess.SubprocessError`,
      or the exit code is not 0, raise `muse_probe_failed`. An existing but
      non-executable interpreter therefore refuses cleanly, with no traceback.
   2. stdout must be ASCII, exactly one line ending in `\n`, and decode with
      `json.loads` to a `dict` whose keys are exactly `{'version', 'sha256'}`.
      `version` must be a `str` that fully matches `[0-9A-Za-z.+-]{1,64}`. `sha256`
      must be a `str` that fully matches `[0-9a-f]{64}`. Anything else raises
      `muse_probe_output_invalid`.
   3. If `version` is not in `MUSE_RUNTIMES`, raise
      `muse_version_unreviewed: <version>`.
   4. If `MUSE_RUNTIMES[version] != sha256`, raise
      `muse_source_digest_unreviewed: <version>`.

   `<version>` is echoed only after step 2 has validated it, so the message cannot
   carry control characters.
5. In `main()`:
   - Keep the existing `--muse-python` venv checks (`:34-37`) unchanged.
   - Replace the old probe (`:38-50`) with:
     `try: version, source = muse_runtime(python)` and
     `except ValueError as exc: parser.error(str(exc))`.
   - Then print `supported_v1: reviewed Muse <version> <sha256>` to stderr and append
     `tests/muse --muse-python <python>` as today.
   - Add `COMPATIBILITY_TESTS` to the required-file loop (`:24-27`), so an
     incomplete export fails with `source file missing: <path>`.
   - Append `list(COMPATIBILITY_TESTS)` to the command immediately after the
     retained selection (`:31`).
   - pytest must never start when any check fails.
6. Update the module docstring to say that combined CI accepts only an exact
   (version, digest) pair from `cli/v1_revision.py:MUSE_RUNTIMES`.
7. Do not edit `docs/validation/fpr3/retained-selection.json`. It is FPR-3 evidence
   that many validation records cite, so the new files are added in the driver.

### 2.2 `tests/muse/conftest.py`

Replace the inline probe (`:20-29`) with the one shared implementation:

- Add `class MuseRuntime(NamedTuple)` with fields `python: Path`, `version: str` and
  `sha256: str`.
- Add a session fixture `muse_runtime(request)`. It keeps the existing missing-option
  `pytest.fail` and the `is_absolute()`/`exists()` assertions, then calls
  `tools.ci.supported_v1.muse_runtime(path)`. On `ValueError` it calls
  `pytest.fail('Muse runtime is not an exact reviewed pair: ' + reason)`. It returns
  `MuseRuntime(path, version, sha256)`.
- `muse_python` becomes a session fixture that depends on `muse_runtime` and returns
  `muse_runtime.python`. Its behaviour for every existing caller is unchanged, except
  that it is now stricter: the venv must be isolated and Muse must be inside it.
  Fact 10 shows the host venv satisfies this.
- Add a plain module-level helper `rebind_pair(current)` that returns
  `(current, stale)`:
  - `others = sorted(v for v in MUSE_RUNTIMES if v != current)`, with `MUSE_RUNTIMES`
    imported from `cli.v1_revision`;
  - `assert len(others) == 1, 'exactly one other reviewed Muse runtime is required'`;
  - `stale = others[0]`.
- Add a session fixture `rebind_runtimes(muse_runtime)` that returns
  `rebind_pair(muse_runtime.version)`. If the allowlist ever grows, this fails loudly
  and must be extended deliberately; it never picks an entry silently.
- Both live in `conftest.py`, not in `test_runtime_rebind.py`, so every module under
  `tests/muse` resolves `rebind_runtimes` without importing it. Other modules import
  `stale_binding` from `test_runtime_rebind.py`; one of them is the N1 freeze's planned
  `tests/muse/test_next_model_suggestion_muse.py`. A fixture defined only in
  `test_runtime_rebind.py` would fail for them with "fixture 'rebind_runtimes' not
  found".
- Leave `pytest_addoption`, `muse` and `muse_root` unchanged.

### 2.3 `tests/muse/test_runtime_rebind.py`

- Line 1 docstring: `"""Real reviewed Muse reads; the stale binding is a metadata-only
  fixture naming the other reviewed runtime."""`
- Do not define `rebind_pair` or `rebind_runtimes` here; they come from
  `conftest.py` (section 2.2).
- `stale_binding(native, muse_python, rebind_runtimes)`. Its first statement is
  `current, stale = rebind_runtimes`. The renamed `test_real_rebind_…` below starts
  with the same statement.
  - line 24 asserts `== current`;
  - lines 25-26 use `version=stale, sha256=MUSE_RUNTIMES[stale]`.
- Rename `test_real_rc11_rebind_preserves_settings_source_history_and_publishes_separately`
  to `test_real_rebind_preserves_settings_source_history_and_publishes_separately`. It
  takes `rebind_runtimes`, and lines 70-71 assert `stale` before and `current` after.
- Rename `test_rc11_linked_checkout_uses_restored_footprint_contract` to
  `test_linked_checkout_uses_restored_footprint_contract`. Its body is unchanged.
- `test_native_reader_refuses_unreviewed_runtime` takes `muse_runtime` as well:
  - it passes `muse_runtime.version` as `argv[4]`;
  - the script's digest branch becomes `reader.MUSE_RUNTIMES[sys.argv[4]] = '0' * 64`;
  - the test asserts `'0.2.1rc999' not in MUSE_RUNTIMES` before running.
- Add the tests that section 5's file placement assigns to this file.
- Everything else in the file stays unchanged. The drift tests' exit-code-only
  assertions are F7 (H1), not R1.

### 2.4 New `tests/muse/test_reviewed_runtime_matrix.py`

```python
"""Reviewed-runtime matrix: CI probe agreement and the FPR-4 mirror successor."""
```

- Import the successor under a name that pytest does not collect:
  `from tests.fpr4.test_mirror_full_footprint import test_full_footprint_mirror_delta_and_identical_native_snapshot as _mirror_successor`.
- `test_fpr4_mirror_successor_under_probed_runtime(tmp_path, muse_python)` calls
  `_mirror_successor(tmp_path, muse_python)`. This is the committed wrapper that runs
  under rc5 or rc11.
- `test_ci_probe_matches_reader_runtime(muse_runtime, muse_root)` asserts four things:
  - `supported_v1.muse_runtime(muse_runtime.python) == (muse_runtime.version, muse_runtime.sha256)`;
  - `muse_read(muse_root, str(muse_runtime.python))["runtime"]` has the same version and
    `sha256`;
  - `MUSE_RUNTIMES[muse_runtime.version] == muse_runtime.sha256`;
  - the probe call takes less than 15 s.
- `test_rebind_runtimes_are_current_and_single_other(muse_runtime, rebind_runtimes)`
  unpacks `current, stale = rebind_runtimes`. It asserts that
  `current == muse_runtime.version`, that `stale` is in `MUSE_RUNTIMES`, and that
  `stale != current`.
- `tests/fpr4/*`, `tests/fpr4/test_composition.py` and `tests/muse/test_mirror.py`
  stay byte-unchanged.

### 2.5 `tests/v1/test_muse_artifact.py`

At lines 131-134, replace the import of `MUSE_SOURCE_SHA256` with
`from cli.v1_revision import MUSE_RUNTIMES` and
`assert lock['package_source_sha256'] == MUSE_RUNTIMES['0.2.1rc5']`. Change the
comment to: the rc5 artifact pin must equal the reviewed rc5 allowlist entry. Nothing
else in the file changes.

### 2.6 Decision: no rc11 job in `.github/workflows/supported-v1.yml`

The workflow stays **byte-unchanged**, for three reasons:

1. A hosted rc11 job needs a reviewed rc11 distribution artifact contract like rc5's,
   and none exists (fact 11).
2. It would also need a new hosted wheel location, and this step forbids adding URLs,
   variables or secrets.
3. No hosted run is authorized.

What changes in practice:

- After R1b, the existing manual `muse` job (rc5 wheel) passes `supported_v1.py`'s
  probe and runs the rebind tests in the rc5 direction (stale = rc11).
- rc11 coverage is the local command in section 5.
- A hosted rc11 job is a separate roadmap row, **A1**, which the R1a closing commit
  adds to `docs/ROADMAP.md`. Its Model is `Operator + Auto` and its Status is
  `Queued after merge`. Its deliverable is a reviewed rc11 distribution artifact
  contract, plus owner authorization for hosting it and for any hosted rc11
  `supported-v1.yml` job. R1b does not touch A1.

### 2.7 Documentation

- `docs/MUSE-RC11-COMPATIBILITY.md`: append this section after the last line.

  ```markdown
  ## Validation across reviewed runtimes

  The Muse tests take the current runtime from the probed `--muse-python` venv and
  use the single other `MUSE_RUNTIMES` entry as the stale binding.
  `tools/ci/supported_v1.py` accepts only an exact (version, digest) pair from
  `cli/v1_revision.py:MUSE_RUNTIMES` and refuses before running pytest otherwise.
  The prepared hosted `muse` job installs only the reviewed rc5 recovery wheel. There
  is no hosted rc11 job: no reviewed rc11 distribution artifact exists, and hosted
  execution is not authorized. Run the rc11 matrix locally:

      .venv/bin/python tools/ci/supported_v1.py \
        --muse-python /absolute/rc11-venv/bin/python3.14 \
        --junitxml /absolute/scratch/combined.xml
  ```

- `tools/ci/MUSE-RC5-RECOVERY.md:45-46`: replace "It verifies rc5's version and
  exact source digest before running the full suite." with "It verifies that the
  venv's Muse version and exact source digest are a reviewed pair in
  `cli/v1_revision.py:MUSE_RUNTIMES` before running the full suite; this recovery
  wheel provides the rc5 pair." Keep the surrounding line wrapping style.

## 3. F2 — the interrupted-rebind message gives the working recovery step

### 3.1 `cli/product_migration.py`

1. Add two module constants next to `apply_mapping`:
   - `DEFAULT_RECOVERY = "rerun explicit sync after resolving drift"`;
   - `RECOVERY = re.compile(r"[ -:<-~]{1,256}")`. This allows printable ASCII 0x20–0x7E
     except `;` (0x3B), 1 to 256 characters, and is matched with `fullmatch`.
2. Change the signature to
   `def apply_mapping(root, mapping, *, check_context, dry_run=False, recovery=None):`.
   Extend the docstring: `recovery` is a caller-supplied, single-line recovery step
   for a partial failure. Omitting it keeps the sync wording.
3. The first statement, before `_updates`, the lock or any read or write, is:
   if `recovery is not None` and it is not a `str` that `RECOVERY.fullmatch`es, raise
   `Refusal("recovery_hint_invalid")`. This applies to `dry_run` too.
4. The partial-failure branch (`:330-337`) computes `completed` and `reason` exactly
   as today. Then:
   - **`recovery is None`:** raise
     `Refusal("partial_asset_update: " + ",".join(completed) + "; " + reason + "; config is last; " + DEFAULT_RECOVERY)`.
     These bytes are identical to today's message.
   - **Otherwise:** raise
     `Refusal("partial_asset_update: " + recovery + "; reason: " + reason + "; completed: " + ",".join(completed))`.
     The hint comes first so it survives the CLI's 300-character cap (fact 1).
     `22 + 256 = 278` characters, so the hint is always shown in full.
   - Both keep `from exc`.
   - When `completed` is empty, the original exception is re-raised unchanged, as
     today.
5. Nothing else in the module changes.

### 3.2 `cli/product_authority.py`

1. Add this module constant:

   ```python
   REBIND_RECOVERY = ("restore .overseer/bin/ok, .overseer/version.lock, then "
                      ".overseer/config.yaml from each copy present in {backup}/, "
                      "then preview again")
   ```

2. Line 165 becomes
   `changed = apply_mapping(root, mapping, check_context=recheck, dry_run=args.dry_run, recovery=REBIND_RECOVERY.format(backup=backup))`.
3. `backup` is `'.overseer/local/rebind-' + digest(original)` (`:117`), which is fixed
   text plus 64 lowercase hex characters. The formatted hint is 211 characters and
   always matches `RECOVERY`.
4. The plan, `rebind_sha256`, the result keys, the mapping and every check stay
   unchanged. `adopt` (`:254`) passes no hint.

Why the wording says "each copy present": live files are replaced only after all
three backup copies exist (fact 3). If a copy is missing, its live file was never
replaced, and copying a copy that is present over an unchanged live file writes the
same bytes. Following the hint is therefore correct whenever the reason is an
exception class name (a failed write). Explicit sync cannot repair the state
(fact 4).

The reason can instead be a refusal from the compare or before-replace recheck:
`stale_write: <path>` (`cli/v1_io.py:85-91, 99`, or `recheck` at
`product_authority.py:154-157`), or `context_changed_before_rebind`
(`product_authority.py:148-150`). That means another writer changed a file during
the apply, and copying a backup over that live file would discard the change. The
hint text stays fixed, because it must fit in the CLI cap. The section 3.4
documentation tells the operator to save such a file first.

### 3.3 Callers that stay unchanged

Init (`v1.py:496`), sync (`product_migration.py:729`), adopt
(`product_authority.py:254`) and upgrade-regime (`product_upgrade.py:44`) pass no
hint. Their messages stay byte-identical.

### 3.4 `docs/MUSE-RC11-COMPATIBILITY.md:85-89`

Replace the text from "On interruption inspect" to the end of that paragraph
("restoration does not downgrade Muse.") with:

```markdown
If an apply is interrupted after its first write, it refuses with
`partial_asset_update: restore .overseer/bin/ok, .overseer/version.lock, then
.overseer/config.yaml from each copy present in <backup>/, then preview again;
reason: <reason>; completed: <paths>`. Explicit `sync` cannot repair this state.
If `reason` is `stale_write: <path>` or `context_changed_before_rebind`, another
writer changed a file during the apply. Before copying, save each of the three live
files whose SHA-256 matches neither the preview's `assets[].before.sha256` nor
`assets[].after`, because the restore overwrites it.
Copy each of those three backup files that exists over its live path, in that
order, and set each restored live path's mode to its preview `assets[].before.mode`.
Then run the same `--dry-run` again and apply its new `--expect-rebind` digest. Live files are replaced only after all three copies exist, so a missing
copy means its live file was not changed. A restored config whose Muse runtime
differs from the installed venv still refuses ordinary reads until the rebind
completes; restoration does not downgrade Muse.
```

The "shared directory lock" wording at `:82-83` is F4 (H1) and stays.

## 4. Fail-closed rules

1. The CI driver never runs pytest unless the Muse venv reports an exact reviewed
   pair, its output is well-formed and bounded, and the probe finishes within
   `PROBE_TIMEOUT`.
2. The parent always re-validates the pair. The child's assertions are never trusted
   on their own.
3. The probe is an integrity check against drift. It is not a defense against a
   malicious interpreter, because the operator supplies the venv. The spec makes no
   stronger claim.
4. A missing compatibility test file fails the driver. It never shrinks the
   selection.
5. The Muse fixtures fail, and never skip, when the runtime is not reviewed, or when
   the allowlist does not have exactly one other entry for the rebind fixture.
6. An invalid recovery hint refuses before any read, lock or write, including on dry
   runs.
7. The kit never restores files automatically. Recovery stays an explicit, inspected
   operator step. Automatic rollback inside an exception path could itself fail
   partway and would touch files the operator has not inspected.
8. Messages contain only repository-relative paths, fixed text, validated tokens and
   exception class names. They never contain absolute paths, file contents, control
   characters or newlines.
9. No missing prerequisite may turn into a skip or a success. Root execution, which
   would defeat the read-only directory in E1, is a test failure, not a skip.

## 5. Seven-tier test matrix

File placement. Every test ID below lives in exactly one file:

| File | Job | Test IDs |
| --- | --- | --- |
| `tests/v1/test_supported_v1.py` (new) | Git | U1–U9, S2, S3, X3, X4 |
| `tests/v1/test_apply_mapping_recovery.py` (new) | Git | U10–U16, S1, I3, DI2 |
| `tests/muse/test_runtime_rebind.py` | Muse | I4, DI1, DI1a, DI3, DI4, S4, E1, X1 |
| `tests/muse/test_reviewed_runtime_matrix.py` (new) | Muse | I1, I2, I5 |

E2, E3, P4 and X5 are R1b runs or checks, recorded in the build record.

- **Fake interpreter:** an executable `#!/bin/sh` script at `<tmp>/venv/bin/python`,
  with an empty `<tmp>/venv/pyvenv.cfg`. It prints fixed output and ignores its
  arguments.
- **Interruption injection:** monkeypatch `cli.product_migration.atomic` so that the
  named path raises `OSError("injected")`, either before calling the real function or,
  for `after_config`, after it.

### Unit

| ID | Test | Asserts |
| --- | --- | --- |
| U1 | `test_probe_accepts_each_exact_reviewed_pair` (parametrized over `MUSE_RUNTIMES`) | `muse_runtime(fake)` returns that pair. |
| U2 | `test_probe_refuses_unreviewed_version` | `ValueError` matching `muse_version_unreviewed: 0.2.1rc999`. |
| U3 | `test_probe_refuses_cross_paired_digest` (both directions) | rc11 with rc5's digest, and rc5 with rc11's, raise `muse_source_digest_unreviewed`. |
| U4 | `test_probe_refuses_malformed_output` | Each case raises `muse_probe_output_invalid`: empty output; two lines; no trailing newline; non-JSON; a JSON list; an extra key; a missing key; an uppercase digest; a 63-character digest; a non-string version; a version with a space; non-ASCII bytes. |
| U5 | `test_probe_refuses_failed_interpreter` (parametrized) | Exit code 1, and a fake interpreter with mode 0o644 (not executable), each raise `muse_probe_failed`. |
| U6 | `test_main_selection_includes_compatibility_tests` | `subprocess.call` and `tempfile.mkdtemp` are patched. The captured command is the base suites, then the retained selection unchanged and in order, then `COMPATIBILITY_TESTS`. There is no `tests/muse` without `--muse-python`. |
| U7 | `test_main_refuses_unreviewed_runtime_before_pytest` | A fake venv with an unreviewed version gives `SystemExit(2)`, and `subprocess.call` is never invoked. |
| U8 | `test_main_refuses_missing_compatibility_test` | Point `supported_v1.KIT` at a tree with every required file except `tests/integration/test_historical_prompt_migration.py`. Result: `SystemExit(2)` with `source file missing: tests/integration/test_historical_prompt_migration.py`. |
| U9 | `test_ci_probe_and_reader_share_one_allowlist` | `supported_v1.MUSE_RUNTIMES is cli.v1_revision.MUSE_RUNTIMES`, and `supported_v1` has no `MUSE_SOURCE_SHA256`. |
| U10 | `test_default_partial_message_is_byte_identical` | A two-row mapping under `.overseer/local/r1/` in the `repo` fixture, failing on row 2 with no hint. Exact message: `partial_asset_update: .overseer/local/r1/a; OSError; config is last; rerun explicit sync after resolving drift`. |
| U11 | `test_supplied_hint_leads_the_partial_message` | The same mapping with hint `restore x from y, then preview again`. Exact message: `partial_asset_update: restore x from y, then preview again; reason: OSError; completed: .overseer/local/r1/a`. |
| U12 | `test_invalid_hint_refuses_before_any_work` (parametrized over `dry_run` False and True) | Hints `""`, `"a"*257`, `"x;y"`, `"x\ny"`, `"x\r"`, `"\x1b[31m"`, `"é"`, `b"x"` and `7` each raise `Refusal("recovery_hint_invalid")`. `_updates` and `fcntl.flock` are patched to fail if called, and the file snapshot is unchanged. |
| U13 | `test_hint_at_limit_is_accepted` | A 256-character valid hint applies a clean mapping with no error. |
| U14 | `test_no_completed_rows_reraises_original_error` | A failure on row 1 raises the original `OSError`, not a `Refusal`. |
| U15 | `test_refusal_reason_is_preserved_with_hint` | `check_context` raises `Refusal("stale_write: x")` before row 2 is replaced. The message has `; reason: stale_write: x; completed: .overseer/local/r1/a`. |
| U16 | `test_rebind_recovery_template` | `REBIND_RECOVERY.format(backup='.overseer/local/rebind-' + '0'*64)` equals the exact expected 211-character string and fully matches `RECOVERY`. |

### Integration

| ID | Test | Asserts |
| --- | --- | --- |
| I1 | `test_ci_probe_matches_reader_runtime` (section 2.4) | The CI probe, the conftest probe and the native reader report the same pair. |
| I2 | `test_rebind_runtimes_are_current_and_single_other` | The derivation in section 2.2 (fixture assertions in section 2.4). In addition, with `from tests.muse.conftest import rebind_pair`: `rebind_pair('0.2.1rc5') == ('0.2.1rc5', '0.2.1rc11')` and `rebind_pair('0.2.1rc11') == ('0.2.1rc11', '0.2.1rc5')`. After `monkeypatch.setitem(MUSE_RUNTIMES, '0.2.1rc999', '0' * 64)`, `rebind_pair('0.2.1rc11')` raises `AssertionError` matching `exactly one other reviewed Muse runtime is required`. |
| I3 | `test_only_rebind_supplies_a_recovery_hint` (Git job) | An `ast` scan of `cli/*.py` finds exactly five `apply_mapping` call sites (fact 5). Only the one inside `rebind_muse_runtime` has a `recovery` keyword. |
| I4 | Existing rebind tests, now portable: `test_real_rebind_…`, the drift parametrization, `test_rebind_existing_next_stays_byte_exact`, `test_rebind_rechecks_owner_edits_under_lock`, `test_native_reader_refuses_unreviewed_runtime` | All pass under rc11 on this host. |
| I5 | `test_fpr4_mirror_successor_under_probed_runtime` | The FPR-4 successor contract passes under the probed runtime. |

### End-to-end

| ID | Test or run | Asserts |
| --- | --- | --- |
| E1 | `test_cli_interrupted_rebind_shows_restore_hint_and_recovers` (in `tests/muse/test_runtime_rebind.py`) | Precondition: `os.geteuid() != 0`, asserted, never skipped. Preview, then chmod `.overseer` to 0o555 around a real `cli/ok` apply; mode 0o755 is restored in `finally`. The apply exits 2. stderr equals exactly `"refused: " + ("partial_asset_update: " + hint + "; reason: PermissionError; completed: " + ",".join([b/config, b/launcher, b/lock, ".overseer/bin/ok"]))[:300] + "\n"`, with no `rerun explicit sync`. The bound launcher `status --json` refuses with `runtime_installation_mismatch`. A fresh preview refuses with `rebind_custom_launcher_requires_resolution`. Then follow the hint exactly: `shutil.copyfile` each present copy over the launcher, the lock, then config. Every non-backup path's (digest, mode) equals the pre-apply snapshot, and `controls()` is unchanged. A new preview exits 0 and changes exactly the three live paths. Applying its new digest exits 0, the config equals the expected normalized config, and `status --check-footprint --json` reports integrity and coverage ok. |
| E2 | R1b local run: `.venv/bin/python tools/ci/supported_v1.py --junitxml <scratch>/git.xml` | The JUnit failure set is exactly `tests/v1/test_adoption.py::test_fresh_standalone_git_install_without_muse` and `tests/v1/test_commands.py::test_unsupported_commands_cannot_run`, both superseded per `docs/reviews/FPR-5-REVIEW.md:267-268`. All 18 compatibility cases and every new Git-job test are present and passed. |
| E3 | R1b local run: the same with `--muse-python ~/.local/share/muse/venv/bin/python3.14` | The failure set is exactly E2's two, plus `tests/muse/test_handoffs.py::test_native_linked_worktree_own_branch_and_checkout_identity` and `tests/muse/test_mirror.py::test_add_change_delete_and_no_content_source_commit`, superseded per `FPR-5-REVIEW.md:269-270`. Every new or renamed Muse test is present and passed. stderr contains `supported_v1: reviewed Muse 0.2.1rc11 c68f34f8…`. |

### Stress

| ID | Test | Asserts |
| --- | --- | --- |
| S1 | `test_hint_survives_many_completed_paths` | A 500-row mapping under `.overseer/local/stress/` fails at row 500. The message starts with `partial_asset_update: <hint>; reason: OSError; completed: `, `message[:300]` contains the whole hint, and it finishes in under 10 s. |
| S2 | `test_probe_output_is_bounded` | A fake interpreter writes 8 MiB. Result: `muse_probe_failed` in under 5 s. |
| S3 | `test_probe_timeout_is_bounded` | The fake interpreter is `#!/bin/sh` with `echo $$ > <tmp>/pid; exec sleep 30`, and `PROBE_TIMEOUT` is patched to 1. Result: `muse_probe_failed` in under 5 s. Then read the pid and assert `os.kill(pid, 0)` raises `ProcessLookupError`. `exec` makes the shell and `sleep` one process, so the kill in `bounded_run` (`cli/v1_revision.py:52-55`) reaches it. |
| S4 | `test_repeated_interruption_converges` | Interrupt at `before_config`, follow the hint, preview again, interrupt again at `before_config`, follow the hint, preview again, then apply. It exits 0. Then the config equals the expected normalized config, and each backup copy equals the original bytes. Every path except the plan's six mapping paths has the same (digest, mode) as the pre-apply `snapshot()`. `controls()` is unchanged, and `docs/NEXT.md` is still absent. |

### Data integrity

| ID | Test | Asserts |
| --- | --- | --- |
| DI1 | `test_interrupted_rebind_reports_backup_restore_and_recovers`, parametrized over the points listed below | For each point: <br>• the exact message `"partial_asset_update: " + REBIND_RECOVERY.format(backup=backup) + "; reason: OSError; completed: " + ",".join(expected)`, with no `rerun explicit sync`; <br>• live paths changed exactly as listed; <br>• for `before_lock` and `before_config`, the bound launcher refuses `runtime_installation_mismatch` and a fresh preview refuses `rebind_custom_launcher_requires_resolution`; <br>• the hint followed exactly; <br>• every non-backup (digest, mode) equals the original snapshot, and `controls()` is unchanged; <br>• a new preview changes exactly the three live paths plus any backup copy that was absent; <br>• the apply with its digest exits 0; <br>• the config equals the expected normalized config, each backup copy equals the original bytes, and `docs/NEXT.md` is still absent. |
| DI1a | `test_interruption_before_first_write_changes_nothing` | A failure on the config backup raises `OSError`, and the snapshot is unchanged. |
| DI2 | `test_sync_partial_message_unchanged` | Real `migration.sync` with the injection used in `tests/fpr1/test_migration.py:320-341`. The exact message is `partial_asset_update: <completed>; OSError; config is last; rerun explicit sync after resolving drift`. `<completed>` is the comma-joined list, in mapping order, of the paths whose post-failure snapshot equals their planned after-state. Derive it this way. Before the failing call, run `migration.sync` with the same args and `dry_run=True` to get `changed` (in mapping order), and take `before = snapshot(root)`. After the failure, take `after = snapshot(root)`. Then `<completed>` is `",".join(p for p in changed if after.get(p) != before.get(p))`. This equals the rule at `cli/product_migration.py:331-332`, because `_updates` (`:309`) includes only rows whose before-state differs from their planned after-state. |
| DI3 | `test_rebind_plan_shape_unchanged` | The plan keys are exactly `{operation, repository, source_config_sha256, context, branch, head, before_binding, after_binding, before_runtime, after_runtime, normalized_config, assets, protected, tracked_local, tracked_binding_choice, next, backup}`. Two previews are equal. |
| DI4 | `test_concurrent_live_edit_is_reported_before_restore` | The `atomic` wrapper calls the real function for `.overseer/bin/ok`, then appends `b"# concurrent\n"` to `.overseer/version.lock`. Assert the exact message `"partial_asset_update: " + REBIND_RECOVERY.format(backup=backup) + "; reason: stale_write: .overseer/version.lock; completed: " + ",".join([b/config, b/launcher, b/lock, ".overseer/bin/ok"])`. Then, using the preview's `assets` rows, the live files whose SHA-256 matches neither `before.sha256` nor `after` are exactly `[".overseer/version.lock"]`. That is the file section 3.4 tells the operator to save, and its bytes end with `b"# concurrent\n"`. |

Interruption points for DI1. "Completed" lists paths in mapping order.

| Point | Fails on | Completed paths | Live paths changed |
| --- | --- | --- | --- |
| `before_backup_launcher` | launcher backup | config backup | none |
| `before_backup_lock` | lock backup | config and launcher backups | none |
| `before_launcher` | `.overseer/bin/ok` | all three backups | none |
| `before_lock` | `.overseer/version.lock` | all three backups, then the launcher | launcher |
| `before_config` | `.overseer/config.yaml` | all three backups, then the launcher and the lock | launcher, lock |
| `after_config` | after the real config write | all three backups, then the launcher, lock and config | all three |

### Performance

| ID | Bound |
| --- | --- |
| P1 | I1: the real probe takes less than 15 s. |
| P2 | S1: under 10 s. S2 and S3: under 5 s. |
| P3 | E1: the whole cycle takes less than 180 s. |
| P4 | R1b records the wall time of E2 and E3. The two compatibility files took 27.17 s in R1a (fact 9). |

### Security

| ID | Test or check | Asserts |
| --- | --- | --- |
| X1 | `test_partial_rebind_message_has_no_absolute_paths_or_controls` | Using the DI1 `before_config` message: <br>• it does not contain `str(root)`, `str(tmp_path)` or `/Users/`; <br>• every character is printable ASCII, with no `\n`, `\r` or `\x1b`; <br>• `backup` fully matches `\.overseer/local/rebind-[0-9a-f]{64}`. |
| X2 | U12 | Newline, carriage return, `;`, an ESC sequence and non-ASCII hints are refused, so neither log lines nor terminal output can be injected. |
| X3 | `test_probe_runs_interpreter_without_shell` | The fake venv is under a directory named `a b $(touch PWNED)`, and the pair is accepted. A spy wraps `cli.v1_revision.subprocess.Popen` and records each call. Assert there was exactly one call, its argv is a `list` whose first element is exactly `str(python)` and whose remaining elements are `['-I', '-B', '-c', PROBE]`, and it has no `shell` keyword or `shell=False`. A marker-file check is not used: the child runs with `cwd='/'`, so a shell regression could not create the marker anyway, and the check could never fail. |
| X4 | `test_probe_environment_excludes_python_and_muse_variables` | With `PYTHONPATH=/nonexistent` and `MUSE_FIXTURE=1` set, the fake interpreter prints the valid pair only if both are absent from its environment, and the probe accepts it. |
| X5 | R1b diff checks | `git diff 99e2e5b -- .github/` is empty. The diff adds no URL, host, IP address, token, key, `secrets.` or `vars.` reference, and no absolute home path outside the existing doc convention. Fixtures use only `example.invalid`. |

## 6. Build rules for R1b

1. Change only these files:
   - `cli/product_migration.py`, `cli/product_authority.py`;
   - `tools/ci/supported_v1.py`;
   - `tests/muse/conftest.py`, `tests/muse/test_runtime_rebind.py`;
   - `tests/v1/test_muse_artifact.py`;
   - `docs/MUSE-RC11-COMPATIBILITY.md`, `tools/ci/MUSE-RC5-RECOVERY.md`;
   - the new `tests/v1/test_supported_v1.py`, `tests/v1/test_apply_mapping_recovery.py`
     and `tests/muse/test_reviewed_runtime_matrix.py`;
   - the new build record `docs/reviews/MIGRATION-COMPAT-RC11-R1-BUILD.md`;
   - `docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` for closing.

   Anything else, including `cli/main.py`'s 300-character cap, needs a re-freeze.
2. Run tests outside the Cursor sandbox (fact 9), with `-p no:cacheprovider`,
   `PYTHONDONTWRITEBYTECODE=1` and a basetemp under `/tmp`.
3. Run these:
   - the new tests;
   - `tests/fpr1/test_migration.py`;
   - `tests/v1/test_adoption.py` and `tests/v1/test_muse_artifact.py`;
   - the two compatibility files;
   - `tests/muse/test_runtime_rebind.py` and `tests/muse/test_reviewed_runtime_matrix.py`
     with rc11;
   - then E2 and E3.

   Record each command and its counts in the build record.
4. Only the four documented superseded failures are accepted. Any other failure
   blocks DONE.
5. rc5 cannot run on this host. The rc5 direction (stale = rc11) is verified by source
   only and must be stated that way. Do not claim a hosted run.
6. Run `/build-verification-review` against this spec, and mark DONE only on **pass**.
7. The runtime digest will change, because `cli/**` and `tools/**/*.py` are runtime
   files (`cli/v1.py:28-43`). Consumers stay on the prepared runtime `309ac668…`; moving
   them is D1. Build no prepared runtime in R1b.
8. Close with one feature-branch commit: code, tests, docs, the build record, the
   roadmap (R1b DONE, R2 NEXT) and the handover. No push.

## 7. Alternatives considered

- **Raise or remove the CLI's 300-character cap.** Rejected. It is a global output
  bound for every refusal, and the hint-first format solves the problem locally.
- **Keep the old order and append the hint.** Rejected. The hint would never be
  visible (fact 1).
- **A callable hint that inspects `completed`.** Rejected. "Each copy present" is
  correct at every point (fact 3), so a fixed string is simpler and easy to review.
- **Automatic restore inside `apply_mapping`.** Rejected (fail-closed rule 7).
- **Add the files to `retained-selection.json`.** Rejected. It is cited FPR-3
  evidence.
- **Add an rc11 hosted job now.** Rejected for the reasons in section 2.6. Queued as
  A1.
- **Pick "stale" as any non-current entry.** Rejected in favour of asserting exactly
  one, so a growing allowlist forces a deliberate test update.

## 8. Review record

The kit CLI cannot stamp this artifact from this checkout (fact 12):
`./cli/ok review --freeze` refuses with `config_repository_mismatch`, and
`.overseer/bin/ok` refuses with `launcher_repository_mismatch`. As the R1a prompt
directs, the review uses the `/freeze-review-loop` skill instead. There is no CLI
mechanical stamp and no `freeze_review` ledger entry. `auto_may_start` is not written.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 | Freeze-review loop, independent thinking subagent (did not write the spec), 2026-10-20 | findings: six minor, no blocker or major | (1) Added the plain helper `rebind_pair`, used by both the fixture and I2. (2) Fixed the section reference, added the file-placement table, renamed the data-integrity IDs to DI1–DI3, and defined DI2's completed list. (3) `OSError` and `SubprocessError` now map to `muse_probe_failed`, with a non-executable case in U5. (4) **Security category, escalated to the owner as `human_escalation: [security]` requires.** The owner approved the reviewer's fix: X3 now checks the process launcher with a spy instead of a marker file that could not fail. (5) S3 uses `exec sleep` and checks that the pid is gone. (6) The A1 roadmap row is added by the R1a closing commit. |
| 2 | Freeze-review loop, fresh independent thinking subagent, 2026-10-20 | findings: one major, two minor | (1) **Major, recovery and irreversibility (a hard-stop category in the skill), escalated to the owner.** The owner approved the reviewer's fix. Section 3.2 now limits "correct" to failed writes. Section 3.4 tells the operator to save a concurrently changed live file first, and DI4 proves both the message and that the edit is detectable. (2) S4 now states its own final-state assertions. (3) DI2 derives its completed list from a dry-run `changed` and before/after snapshots. Also corrected fact 1's wording about when the old advice is visible (reviewer observation). **Owner-approved change outside the findings:** `rebind_pair` and   `rebind_runtimes` moved to `tests/muse/conftest.py`, so the N1 freeze's planned Muse module, which imports `stale_binding`, still resolves its fixtures once the branches are combined (N1 freeze `cc79cfff…`, section 7, tier 3). |
| 3 | Freeze-review loop, fresh independent thinking subagent, 2026-10-20 | **pass** | Re-read the spec against source. No correctness or buildability findings. Rounds 1 and 2 resolutions are present. `ok review --freeze` still cannot stamp this checkout (fact 12). |
