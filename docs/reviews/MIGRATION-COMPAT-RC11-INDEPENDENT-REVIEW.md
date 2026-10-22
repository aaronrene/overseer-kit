# Independent review — commit 30f5cb4 (migration compatibility + Muse rc11)

**Verdict: PASS.** No blockers found. Seven non-blocking findings are listed below,
two of them recommended before merge. Nothing here is marked fixed.

- Reviewer: Claude Opus 5.5 (Anthropic), running as an AI agent in Cursor. This is
  an AI review, not a human audit.
- Authorship: this session did not write or change any part of the commit.
- Date: 2026-10-20.
- Commit: `30f5cb48cfe6aafc542d6818e9128caa03e978a1` on
  `fix/knowtation-migration-compat-20261020`, parent `d54a228`; 17 files, +1210/−38.
  The worktree was clean before and after the review.
- Method: read-only source review of every changed file and its callers, plus
  adversarial scratch tests and full test runs. All scratch work stayed in `/tmp`.
  No code edits, commits, pushes, PRs, merges, installs, dependency changes or
  ledger writes. Knowtation and BornFree were only read.

## 1. Legacy `kit` becomes inert `legacy_kit` — verified

- `cli/product_config.py:338-345`: `kit` is accepted only in a legacy-full config
  (`overseer_config_version: 1`). It is moved to `legacy_kit` after
  `_legacy_kit()` validation (`:125-146`): flat scalars only, at most 64 keys,
  keys must match TOKEN, strings up to 16 KiB with no control characters, and
  NaN/infinity are refused.
- `:365-369`: schema 3 accepts only `legacy_kit`. A schema-3 `kit` refuses, and so
  does a legacy-full `legacy_kit` (both tested at
  `tests/integration/test_legacy_migration_compat.py:213-224`).
- Nothing consumes it. A repo-wide search finds `legacy_kit` only in
  `product_config.py` (validation and diagnostics) and in
  `product_migration.py:443`, which is an unrelated diagnostic label. The adapter
  view keeps only CORE|OPTIONAL keys (`product_config.py:218`), so `legacy_kit`
  never reaches adapters. Runtime selection uses `config["runtime"]`
  (`cli/v1.py:180-183`), validated by `_runtime` (`product_config.py:149-156`).
  Launcher and binding generation never read `kit` or `legacy_kit`.
- It does appear in status JSON (`configuration.legacy_kit`), which is
  display-only.

## 2. Size limits — verified, with a small scope note

- The commit's only limit change is in `cli/product_footprint.py:11`. `with_lock`
  now uses `product_migration.read` (16 MiB `ASSET_LIMIT`) instead of the 128 KiB
  `v1_io.read`. That reader was already present at d54a228
  (`product_migration.py:24-28`). Config and NEXT keep `LIMIT` (128 KiB) inside it.
  `with_lock` skips NEXT entirely (`product_footprint.py:18, 24`).
- Unchanged limits: prompt files are read with `v1_io.read` (128 KiB,
  `cli/main.py:16, 307`). Plans were already 16 MiB at d54a228 (baseline
  `product_migration.py:580`). The diff contains no `LIMIT` edits.
- Scope note: the 16 MiB limit in `with_lock` covers more than living documents.
  It also applies to `version.lock` and to any owner-preserved asset, including
  the new `_legacy_consumer_owned` rows (`product_migration.py:166-181`). Each read
  is still bounded per file, refuses symlinks and hard links (`v1_io.confined`),
  and keeps only a digest. No unbounded read was introduced.
- Tests cover both edges. A document above the 16 MiB limit refuses (`:272-280`);
  config and NEXT above 128 KiB refuse (`:245-258`).

## 3. Historical prompts stay inert — verified

- The `conflicting_legacy_prompts` refusal is removed (`product_migration.py`
  around line 276). `_legacy_drafts` only collects text into the plan.
- `_apply_plan` never reads `legacy_prompt_drafts` beyond the shape check
  (`:49, 55`).
- Writable assets come from `v1.assets()`, which drops every living-document path,
  NEXT included (`cli/v1.py:377-380`). The plan cannot add NEXT because each asset
  row must exist in `approved` (`:542-548`). NEXT stays in the protected inventory
  (`_document_paths` → `inventory`), rechecked before every replace (`:560-564`).
- Tests: `tests/integration/test_historical_prompt_migration.py` covers 138 blocks
  / 71 distinct at 768,855 and 831,973 bytes, an existing NEXT left untouched, and
  a document changed after preview refusing. `tests/fpr1/test_migration.py:207-217`
  covers the rest.
- Real receipt: BornFree's `verification.json` records 138/71 with
  `historical_prompts_selected: 0`. Its NEXT is now `d659c71f…` rather than the
  receipt's `77f02052…`. The file header shows a later bound `next-write` at
  12:50 (action `CREDITS-WORDING-CONSOLE-CLEANUP-CLOSED-1`, kind `stop`), backed by
  `docs/reviews/2026-10-20-credits-wording-console-cleanup-operator-closeout/`.
  That is an operator publication after the migration, not a migration effect.

## 4. Muse rc11 exact allowlist — verified (rc5 by source inspection only)

- `cli/v1_revision.py:17-20`: `MUSE_RUNTIMES` contains exactly two pairs. rc5 is
  `7b181b6e…` (same as `tools/ci/supported_v1.py:14`) and rc11 is `c68f34f8…`
  (same as `muse-reader-api-review.json` and the inventory).
- The child reader checks version then digest (`cli/v1_muse_reader.py:69-80`). The
  parent checks the exact pair (`v1_revision.py:123-128`). `revision()` also
  requires the bound runtime to equal the observed one
  (`v1_revision.py:184-185`), so an rc5 binding against an rc11 venv still refuses
  until an explicit rebind.
- The reader imports exactly the eight reviewed names (`v1_muse_reader.py:81-83,
  126-129`), matching `muse-reader-api-review.json`.
- Unknown version and digest refusals are tested
  (`tests/muse/test_runtime_rebind.py:198-224`).
- rc5 was not executed: no rc5 venv exists on this host. Its retention is verified
  by source only.

## 5. `adopt --rebind-muse-runtime` — verified, including adversarial probes

| Requirement | Evidence |
| --- | --- |
| Same source only | `product_authority.py:73-74` (bound schema-3 Muse only), `:86-89` (repo_id/store), `:90-91` (branch/head vs args), `:81-83` (repo_id/lane/model vs args). Only `binding.runtime` and `runtime` change (`:92-94`). |
| Preview digest equals apply | Apply recomputes the full plan (protected snapshots, asset bytes, normalized config) and requires `--expect-config` (`:79-80`) and `--expect-rebind` (`:163-164`). `--expect-rebind` without the flag refuses (`cli/main.py:284-285`). |
| Lock held | `apply_mapping` takes `flock` on `.overseer/` (`product_migration.py:320-322`), then rechecks context and every `before` snapshot. Each replace runs `recheck` (`:328-329`) and compares content (`v1_io.atomic`). |
| Backups first, config last | Mapping order is three backups, launcher, lock, config (`product_authority.py:118-121`). `_updates` keeps that order. |
| Recoverable failure | Probe (below): interrupting just before the config write leaves the old config. The bound launcher refuses with `runtime_installation_mismatch`, and a fresh preview refuses with `rebind_custom_launcher_requires_resolution`. The documented restore (launcher, lock, then config from the backup) returns every non-backup byte and mode to the original. A fresh preview then applies with exit 0. |
| No path escape | All writes go through `confined()` (rejects `..`, absolute paths, symlink components, non-regular files and hard links). The backup name is fixed text plus a hex digest. Probe: a symlinked `.overseer/local` refuses with `path_parent_invalid` and nothing is written outside. A planted backup with different bytes refuses with `rebind_backup_mismatch` and nothing is written. |

Probe file: `/tmp/rv30f5c/test_break_rebind.py`, 5 of 5 passed with real rc11,
using the commit's own fixtures.

## 6. Security

- **Launcher shell injection: not present.** The premise that the runtime root is
  embedded unquoted is incorrect. `cli/v1.py:354-358` passes every interpolated
  value through `shlex.quote`, and so did d54a228 (`cli/v1.py:353`).
  - The real Knowtation and BornFree launchers look unquoted only because
    `shlex.quote` leaves strings of safe characters bare.
  - Probe: a runtime root of `kit $(touch PWNED4);rm -rf x 'y'` and a repo root with
    `;`, `$()`, backticks, quotes and a newline reached the program as six literal
    arguments, and no marker file was created.
  - A rebind whose old runtime root contained `; $(touch …)` matched its launcher,
    applied, and never executed the payload.
  - Runtime-root validation itself is minimal: absolute, physical, at most 200
    characters, no control characters (`product_config.py:149-156`). Quoting is
    what prevents injection. Hook scripts are also quoted
    (`product_bookends.py:28-30`).
- **Preview-to-apply race.** Apply recomputes and checks the digest, rechecks under
  the lock, and rechecks again before each replace. The remaining gap between the
  final check and `os.replace` concerns same-user writers, which `v1_io.atomic`
  documents as out of scope.
- **File modes.** Launcher is 0755, lock 0644, config keeps its mode
  (`product_migration.py:306-308`). Backups are always 0644; see finding F3.
- **Secrets and hosts.** No secrets, tokens, hosts or IP addresses were added. One
  private home path was added (`docs/MUSE-RC11-COMPATIBILITY.md:22`), consistent
  with 363 tracked files that already contain the same path at d54a228. Test
  fixtures use `example.invalid`.

## 7. Tests

Commands ran in `/tmp`, with `-p no:cacheprovider` and
`PYTHONDONTWRITEBYTECODE=1`. Muse runs used
`--muse-python ~/.local/share/muse/venv/bin/python3.14` (rc11).

| Run | Result |
| --- | --- |
| Focused: 4 compatibility files plus `tests/fpr1/test_migration.py` | **77 passed**: the 41 required cases plus 36 existing migration tests. |
| Whole `tests/` tree without `tests/muse`, candidate in place | 2091 cases: 1595 passed, 493 failed, 3 errors. |
| Same tree on an exported d54a228 baseline | 2073 cases: 1573 passed, 497 failed, 3 errors. |
| Comparison | **No test fails on 30f5cb4 that passes on d54a228.** All 19 new tests pass. The 4 baseline-only failures are artifacts of the export having no `.git`. The roughly 490 shared failures are retired legacy-CLI tests (for example, `main() got an unexpected keyword argument 'ctx'`). |
| CI-selected 698 tests (`tests/v1`, `fpr1`–`fpr3` and the retained selection) | Candidate fails 2, both also failing at baseline: `tests/v1/test_adoption.py::test_fresh_standalone_git_install_without_muse` and `tests/v1/test_commands.py::test_unsupported_commands_cannot_run`. Both are recorded as superseded in `docs/reviews/FPR-5-REVIEW.md:267-268`. |
| `tests/muse` (rc11), candidate | 186 cases: **184 passed, 2 failed.** The failures are `test_handoffs.py::test_native_linked_worktree_own_branch_and_checkout_identity` and `test_mirror.py::test_add_change_delete_and_no_content_source_commit`. |

On the two recorded broad failures:

- **Standalone install.** It fails at both commits, is superseded per
  `FPR-5-REVIEW.md:268`, and the failure (missing `cryptography` in the test's
  own fresh venv) does not involve the changed files.
- **Linked worktree.** It is superseded per `FPR-5-REVIEW.md:269`, and
  `docs/validation/fpr4/native-init-followup.md:13` records the same
  `dirty is False` failure under rc5.
- **Third failure.** The full `tests/muse` run surfaced
  `test_mirror::test_add_change_delete_and_no_content_source_commit`. The recorded
  191-test run did not include `test_mirror`. It is also documented as superseded
  (`FPR-5-REVIEW.md:270`). Its replacement,
  `tests/fpr4/test_mirror_full_footprint.py`, cannot run under rc11 because its
  fixture requires rc5. When called directly against rc11 (scratch probe
  `/tmp/rv30f5c/test_rc11_mirror_successor.py`), it **passed**.
- **Baseline `tests/muse` cannot run on this host**: its fixture requires rc5
  (`assert ['0.2.1rc11', …] == ['0.2.1rc5', …]`), so the Muse comparison is
  candidate-only.
- **Baseline setup note.** The provided baseline worktree's `.venv` is a symlink
  to the candidate's `.venv`, so its bootstrap refuses with
  `runtime_environment_mismatch`. I used a `git archive` export of d54a228 with a
  copy of the same environment instead.

New behaviors without a direct test:

- Partial-failure recovery for rebind: shown working by probe only.
- Seven rebind refusal reasons are never asserted by name:
  `rebind_requires_bound_schema3_muse`, `rebind_requires_existing_muse_binding`,
  `rebind_launcher_footprint_mismatch`, `rebind_backup_mismatch`,
  `context_changed_before_rebind`,
  `rebind_requires_explicit_muse_python_and_existing_authority` and
  `expect_rebind_requires_rebind_muse_runtime`. The drift tests assert only exit
  code 2 (`test_runtime_rebind.py:151`), so a refusal for the wrong reason would
  still pass.
- Symlinked or planted backup directories, and backup file modes.
- `_legacy_consumer_owned` with a missing file.
- An rc11 run of the mirror replacement contract.
- rc5 native reads (no rc5 venv).
- Stress and performance coverage of 16 MiB documents.

## Findings

### Blockers

None.

### Recommended before merge (non-blocking for this commit's correctness)

**F1 — Medium — CI cannot exercise the new rc11 behavior, and the new tests assume rc11.**

- `tools/ci/supported_v1.py:42, 48` hard-codes an rc5-only probe.
- `tests/muse/test_runtime_rebind.py:24, 70-71, 211` hard-codes rc11.
- The two new integration files are absent from the CI command and from
  `docs/validation/fpr3/retained-selection.json`.
- Failure example: the prepared Muse CI job (rc5 wheel) runs `tests/muse`. The
  `stale_binding` fixture's `assert … == "0.2.1rc11"` errors in every test built on
  it, and the digest-refusal case hits "unexpected success". With an rc11 venv,
  CI refuses at its own probe.
- Context: that job already failed at d54a228 on the documented superseded tests,
  so this deepens an existing gap rather than introducing a new one.
- Smallest correction:
  - Have the probe accept any `MUSE_RUNTIMES` pair (or add an rc11 job).
  - Derive the fixture's "current" and "stale" versions from the probed venv and
    the other allowlisted entry.
  - Add both integration files to the CI selection.

**F2 — Low — the interrupted-rebind message gives the wrong recovery step.**

- `product_migration.py:336` always says "rerun explicit sync after resolving
  drift".
- Failure example: after an interruption before the config write, sync refuses.
  The bound launcher reports `runtime_installation_mismatch` and the Muse binding
  is still rc5. The working path is the backup restore in
  `docs/MUSE-RC11-COMPATIBILITY.md`.
- Smallest correction: let `apply_mapping` take a recovery hint. The rebind would
  pass "restore launcher, lock, then config from `<backup>`; then preview again".

### Optional improvements

**F3 — Low — backups do not keep the original mode.**

- `_updates` gives backup paths 0644 or 0755 by suffix (`product_migration.py:306-308`).
- Probe: a 0600 config produced a 0644 backup, so restoring with `cp` widens
  permissions. The original modes are recorded only in the plan's `before` rows.
- Fix: write backups with the source mode, `before["mode"]` of the target.

**F4 — Low — the documentation overstates the lock coverage.**

- `docs/MUSE-RC11-COMPATIBILITY.md:83` says "shared directory lock".
- `next-write` locks `docs/` (`cli/v1.py:341-343`), not `.overseer/`. This
  predates the commit and is mitigated by rechecks and by the "quiesce writers"
  step in `ADOPTION.md`.
- Fix: correct the wording, or have `next-write` also take the `.overseer/` lock.

**F5 — Medium, pre-existing (present at d54a228:252) — exponential backtracking in
draft extraction.**

- The `(?:\s*\n)*` group in the `_legacy_drafts` pattern
  (`product_migration.py:271`) backtracks exponentially.
- Measured: `### Paste-ready prompt` followed by 22 blank lines and no fence took
  0.17 s, and the time quadruples with every 2 extra lines. About 30 lines would
  take minutes, and 40 would hang migration.
- Fix: use `(?:[ \t]*\n)*`.

**F6 — Low, pre-existing — the source digest covers only `*.py`.**

- `muse/__init__` runs before the digest check (`v1_muse_reader.py:72-80`), under
  the audit hook.
- Compiled `.pyc` and `.pth` files are not covered, so an edited bytecode cache
  could run unreviewed code.
- Fix: hash before importing (via `find_spec`) and run the child with
  `--check-hash-based-pycs always`, or include `__pycache__` contents in the
  digest.

**F7 — Low — tests assert exit code only.**

- The drift tests check `returncode == 2` without the refusal reason.
- Fix: assert the specific reason per case, and add the untested refusals listed
  in section 7.

## Real adoption receipts

- **Knowtation**: rebind plan `82482e1a…` was applied, six paths changed, and the
  C2 prompt was published. Current `.overseer/config.yaml` (`72c2f1fc…`) and
  `docs/NEXT.md` (`1279cdee…`) match the receipt.
- **BornFree**: present and reporting success. Plan `a8e1d0d7…`, 138/71 historical
  blocks with none selected. Its NEXT was later superseded by an operator
  publication (section 3).
- **Runtime**: both projects' launchers point to the prepared runtime. Its computed
  runtime digest (`309ac668…`) equals that of this clean checkout at 30f5cb4.

## Summary in plain language

The change does what it claims. Old "which kit installed me" notes are kept but
never used to pick software. Large history documents now pass through migration
while small-file limits stay in place. Old prompts are saved as evidence and never
switched on; only the normal publish command can set the next task. The Muse
upgrade support accepts exactly two reviewed releases by fingerprint, and the
switch-over command refuses if anything important changed since the preview.

I tried to break it with hostile file paths, a symlinked folder, a fake backup and
a simulated crash. Every attempt was refused or recovered. The concern about
command injection through the launcher does not hold: every path is safely quoted.
The full test suite shows no new failures compared with before the change.

Two things should be fixed before merging. The automated test pipeline is still
wired only for the old Muse release, so it cannot check the new behavior. And a
crash message gives the wrong recovery advice.

## Technical summary

PASS for 30f5cb4.

- `legacy_kit` is validated and excluded from the adapter view and the runtime
  path.
- The 16 MiB limit is per file and also covers the lock and owner-preserved
  assets. The 128 KiB limits for config, NEXT and prompts are unchanged.
- Drafts never enter `approved`, and NEXT stays protected.
- The child and parent check the exact version/digest pair, and `revision()`
  requires binding equality.
- The rebind holds the source fixed through repo_id, store, branch/head and
  context. It uses compare-and-swap on both the config digest and the
  recomputed-plan digest, takes the `.overseer` lock, writes backups first and
  config last, and confines every write.
- The launcher is `shlex.quote`d at both d54a228 and 30f5cb4.
- Tests: 77/77 focused. No regressions across the whole tree compared with
  d54a228. CI-selected: 2 failures, both at baseline and documented. `tests/muse`
  on rc11: 184/186; the 2 failures are documented as superseded, and the mirror
  replacement passes on rc11 by probe.
- Fix F1 (CI and test rc pinning) and F2 (recovery message) before merge.
- Optional: F3–F7, with F5 and F6 pre-existing.
