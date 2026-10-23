# RC13a — frozen spec: add Muse 0.2.1rc13 to the reviewed runtime list

Status: **frozen.** RC13a (Thinking) fixes WHAT and HOW. RC13b (Auto) builds
exactly this and nothing else. RC13b treats this file as ground truth and does
not re-derive the version, the digest, or the stale-partner map. Review
findings must cite file+line. The freeze-review result is in the Review record
at the end.

```yaml
phase: RC13a
outputs:
- id: muse-rc13-allowlist-spec
  path: docs/reviews/MUSE-RC13-ALLOWLIST-SPEC.md
  frozen: true
frozen_inputs:
- id: muse-allowlist
  path: cli/v1_revision.py#MUSE_RUNTIMES
- id: read-only-reader
  path: cli/v1_muse_reader.py
- id: compatibility-doc
  path: docs/MUSE-RC11-COMPATIBILITY.md
- id: rebind-pair
  path: tests/muse/conftest.py#rebind_pair
- id: runtime-matrix
  path: tests/muse/test_reviewed_runtime_matrix.py
- id: next-model-muse-fixture
  path: tests/muse/test_next_model_suggestion_muse.py#stale_binding
- id: probe-tests
  path: tests/v1/test_supported_v1.py
- id: test-tiers
  path: .overseer/policy/test-tiers.yaml
- id: kit-spec-freeze-policy
  path: docs/OVERSEER-KIT-SPEC.md#6
```

- Branch: `feat/muse-rc13-allowlist`, local only. Spec base commit:
  `3cf46e6f3dea6aa529f0143f4539a6c335ad32c2` (`main`).
- In scope: one new exact allowlist pair, the test updates that pair forces,
  and the three documents named below.
- Not in scope, and forbidden in RC13b: pushing, opening a pull request,
  merging, installing a package, downgrading Muse, changing the shared Muse
  virtualenv, rebinding Knowtation, rebinding Muse 108, rebinding Born Free,
  editing `docs/NEXT.md`, editing `.overseer/config.yaml`, a hosted rc13 job,
  a distribution artifact, and any edit under `cli/` except the
  `MUSE_RUNTIMES` dict replacement in section 2.

## 1. Verified facts this spec relies on

Checked in RC13a against the already-installed shared Muse virtualenv. The
interpreter is a virtualenv (`sys.prefix != sys.base_prefix`). The package
directory is the `muse` package inside that virtualenv and is inside the
virtualenv prefix. `importlib.metadata.version("muse")` is `0.2.1rc13`.

The digest below is the construction in `cli/v1_muse_reader.py:76-78`: sort
`package.rglob("*.py")` as paths, then for each path update SHA-256 with the
relative name encoded as UTF-8, a NUL, the file bytes, and a NUL. Measured
result:

| Fact | Value |
| --- | --- |
| Version | `0.2.1rc13` |
| Source fingerprint | `8b6667bd475355a955563ddeb1b98444c671cd13f73a1decba6ce227039709ba` |
| `*.py` files | 385 regular files, none of them symlinks |
| `str(relative)` versus `as_posix()` | equal on this host, so the existing probe in `tools/ci/supported_v1.py:35-36` hashes this tree to the same digest |
| Path sort versus sorted relative strings | equal for this tree |

RC13b must recompute that digest with the same construction and the same
interpreter the operator names in the RC13b paste block. The count must be
385 and the digest must equal the fingerprint above. If either check fails,
RC13b stops and does not edit the allowlist.

The reader imports these Muse names and no others (`cli/v1_muse_reader.py:81-83`
and `:126-129`). In the installed rc13 tree they are still the same objects:

| Import | Installed definition checked |
| --- | --- |
| `muse.core.commits.read_commit` | `muse/core/commits.py:516`. Reads typed object bytes, builds `CommitRecord`, verifies the content id, returns the record or `None`. The read path does not write. |
| `muse.core.snapshots.read_snapshot` | `muse/core/snapshots.py:231`. Same contract for `SnapshotRecord`, `manifest`, and `directories`. The read path does not write. |
| `muse.core.validation.validate_branch_name` | `muse/core/validation.py:123-168`. Returns the string or raises. No I/O. |
| `muse.core.ignore.resolve_patterns` | `muse/core/ignore.py:157-185`. Concatenates global patterns, then the selected domain. No I/O. |
| `muse.core.ignore.is_ignored` | `muse/core/ignore.py:234-256`. Last match wins, including negation. No I/O. |
| `muse.core.snapshot._BUILTIN_SECRET_PATTERNS` | `muse/core/snapshot.py:96`. A static list. It contains `.env`. |
| `muse.core.types.hash_file` | `muse/core/types.py:198-228`. Stats the file, reads bytes, returns `sha256:` plus the hex digest of `blob <size>\0<content>`. |
| `muse.plugins.code.plugin._ALWAYS_IGNORE_DIRS` | `muse/plugins/code/plugin.py:158`. A `frozenset`. It contains `.git` and `.muse`. |

`cli/v1_muse_reader.py:118` still does not call `read_stage`. RC13b does not
change the reader.

`tests/muse/conftest.py:17-20` sets the stale partner to the single other
allowlist key. A third key makes `len(others) == 1` fail for every current
version. That failure is the deliberate stop the rc11 spec required before
the allowlist grows. Section 3 is that extension. It is test-only.

`tests/muse/test_next_model_suggestion_muse.py:52-54` hardcodes a current
binding of `0.2.1rc11` and a stale binding of `0.2.1rc5`. Against the rc13
interpreter the post-apply binding is rc13, so that assertion fails until
section 3 replaces it.

`tests/v1/test_supported_v1.py:34-37` accepts every pair currently in
`MUSE_RUNTIMES`. It does not by itself pin the three digests. Section 4 adds
that pin. `:46-48` refuses only the rc5/rc11 swap. Section 4 extends the
cross pairs. `:40-43` refuses `0.2.1rc999` only. Section 4 also refuses
`0.2.1rc12` and `0.2.1rc14`.

The product CLI in this fresh checkout refuses `ok next` with the message in
`cli/ok:8`. Canonical `docs/NEXT.md` stays the existing PR #93 prompt. RC13b
does not publish it.

## 2. Allowlist

Edit only `cli/v1_revision.py`. Keep `MUSE_VERSION = "0.2.1rc5"` (`:15`).
Keep the comment on `:16`. Replace the dict at `:17-20` with exactly:

```python
MUSE_RUNTIMES = {
    MUSE_VERSION: "7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92",
    "0.2.1rc11": "c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe",
    "0.2.1rc13": "8b6667bd475355a955563ddeb1b98444c671cd13f73a1decba6ce227039709ba",
}
```

Do not add another key. Do not change a retained digest. Membership of this
dict remains the only acceptance check (`cli/v1_muse_reader.py:70-80` and
`tools/ci/supported_v1.py:74-77`). Do not edit either of those checks. Do not
edit `tools/ci/supported_v1.py`. Do not edit `cli/v1_muse_reader.py`.

Refusal stays fail-closed:

- a version that is not one of those three keys is refused;
- a matching version with any other digest is refused;
- there is no version range and no prefix match.

## 3. Stale partner used by tests

`REBIND_STALE` lives only in `tests/muse/conftest.py`. Product code must not
import it. It is not a downgrade path and it does not select a Muse install.
The stale value is metadata on a disposable fixture. The obsolete interpreter
does not need to exist. Do not install rc5 or rc11.

Replace `rebind_pair` (`tests/muse/conftest.py:17-20`) with:

```python
REBIND_STALE = {
    '0.2.1rc5': '0.2.1rc11',
    '0.2.1rc11': '0.2.1rc5',
    '0.2.1rc13': '0.2.1rc11',
}


def rebind_pair(current):
    """Return (current, stale) from the named one-to-one test map.

    The map must name every allowlist key and nothing else. An extra or
    missing reviewed version fails here instead of picking a partner by sort.
    """
    if set(MUSE_RUNTIMES) != set(REBIND_STALE) or current not in REBIND_STALE:
        raise AssertionError('reviewed Muse stale partner must be the named map')
    stale = REBIND_STALE[current]
    if stale == current or stale not in MUSE_RUNTIMES:
        raise AssertionError('reviewed Muse stale partner must be the named map')
    return current, stale
```

Preserved pairs: rc5's partner stays rc11, and rc11's partner stays rc5.
rc13's partner is rc11, the previous reviewed runtime. That is a fixture
choice, not a product migration.

In `tests/muse/test_reviewed_runtime_matrix.py`, rename
`test_rebind_runtimes_are_current_and_single_other` to
`test_rebind_runtimes_use_the_named_partner`. Keep the current/stale
assertions at `:29-32`. Replace `:33-37` with:

```python
    assert rebind_pair('0.2.1rc5') == ('0.2.1rc5', '0.2.1rc11')
    assert rebind_pair('0.2.1rc11') == ('0.2.1rc11', '0.2.1rc5')
    assert rebind_pair('0.2.1rc13') == ('0.2.1rc13', '0.2.1rc11')
    monkeypatch.setitem(MUSE_RUNTIMES, '0.2.1rc999', '0' * 64)
    with pytest.raises(AssertionError, match='reviewed Muse stale partner must be the named map'):
        rebind_pair('0.2.1rc11')
    with pytest.raises(AssertionError, match='reviewed Muse stale partner must be the named map'):
        rebind_pair('0.2.1rc13')
```

In `tests/muse/test_next_model_suggestion_muse.py`, change `stale_binding`
(`:45-67`) so it takes `rebind_runtimes`, unpacks `current, stale`, asserts
the post-apply version equals `current`, and writes `stale` plus
`MUSE_RUNTIMES[stale]`. Delete the hardcoded `0.2.1rc11` and `0.2.1rc5` in
that fixture. Change its docstring to say it is a metadata-only stale partner
from `rebind_runtimes`. Keep the file's single-quote style. Do not change
`test_muse_rebind_then_publish_codex` or
`test_muse_codex_requires_explicit_vcs_and_base_head`.

`tests/muse/test_runtime_rebind.py:29-37` already consumes `rebind_runtimes`.
Do not edit that fixture.

## 4. Probe pins and refusal tests

In `tests/v1/test_supported_v1.py`:

1. Add this test beside the existing accept test:

```python
def test_allowlist_is_the_three_reviewed_pairs():
    assert MUSE_RUNTIMES['0.2.1rc5'] == '7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92'
    assert MUSE_RUNTIMES['0.2.1rc11'] == 'c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe'
    assert MUSE_RUNTIMES['0.2.1rc13'] == '8b6667bd475355a955563ddeb1b98444c671cd13f73a1decba6ce227039709ba'
    assert set(MUSE_RUNTIMES) == {'0.2.1rc5', '0.2.1rc11', '0.2.1rc13'}
    from cli.v1_revision import MUSE_VERSION
    assert MUSE_VERSION == '0.2.1rc5'
```

2. Keep `test_probe_accepts_each_exact_reviewed_pair` parametrized over
   `list(MUSE_RUNTIMES.items())`.
3. Replace `test_probe_refuses_unreviewed_version` with a parametrized test
   over `0.2.1rc999`, `0.2.1rc12`, and `0.2.1rc14`. Each raises `ValueError`
   matching `^muse_version_unreviewed: <version>$` for that exact version.
4. Extend `test_probe_refuses_cross_paired_digest` with these rows, keeping
   the two existing rows:

```python
    ('0.2.1rc13', MUSE_RUNTIMES['0.2.1rc5']),
    ('0.2.1rc13', MUSE_RUNTIMES['0.2.1rc11']),
    ('0.2.1rc5', MUSE_RUNTIMES['0.2.1rc13']),
    ('0.2.1rc11', MUSE_RUNTIMES['0.2.1rc13']),
```

Do not edit `tests/v1/test_muse_artifact.py`. Its rc5 pin must keep passing.
Do not edit `tests/fpr4/test_composition.py`. That cell stays the rc5 pin.

## 5. Reader API test

Add `tests/muse/test_reader_api_compatibility.py`. It requires the same
`--muse-python` fixture as the rest of `tests/muse`. It does not open
Knowtation, Muse 108, or Born Free.

The test runs the rc13 interpreter with `-I` and `-B` on a list argv, never a
shell. Before the audit hook, the child writes one regular file under the
test temp directory whose bytes are `b'hello\n'`. It then inserts the kit
root on `sys.path`, installs `cli.v1_muse_reader.readonly` as an audit hook,
and imports the eight names in section 1. Creating that file after the hook
is refused: `readonly` rejects `O_CREAT` (`cli/v1_muse_reader.py:29-30`), and
unlinking it after the hook is refused (`:31-34`). The child must not create,
rename, or delete a file after the hook. The parent deletes the temp file
after the child exits. Import failure or an audit refusal fails the test.
The child then asserts, and the parent checks, all of the following:

- `read_commit`, `read_snapshot`, `validate_branch_name`, `resolve_patterns`,
  `is_ignored`, and `hash_file` are callable;
- `validate_branch_name('main') == 'main'`;
- `validate_branch_name('bad name')` raises;
- `resolve_patterns({}, 'code') == []`;
- `is_ignored('a.py', [])` is `False`;
- `_BUILTIN_SECRET_PATTERNS` is a `list` and contains `.env`;
- `_ALWAYS_IGNORE_DIRS` is a `frozenset` and contains `.git` and `.muse`;
- `hash_file` on the file written before the hook equals `sha256:` plus the
  hex SHA-256 of `b'blob 6\0'` concatenated with `b'hello\n'`. The child
  computes that expected digest itself.

The child prints one JSON object on stdout and exits 0. The parent fails if
the exit code is not 0. The parent also asserts
`muse_runtime.version == '0.2.1rc13'` and
`muse_runtime.sha256 == MUSE_RUNTIMES['0.2.1rc13']`. A different live pair
fails this test rather than widening the allowlist.

`tests/muse/test_reviewed_runtime_matrix.py:17-25` already checks that the
probe digest, the reader digest, and `MUSE_RUNTIMES[version]` agree in under
15 seconds. Keep that bound. Do not add a second timer. That test is the
stress and performance evidence for the 385-file tree.

`tests/muse/test_runtime_rebind.py:245-259` already refuses an unreviewed
version and a replaced digest inside a disposable child. The shared virtualenv
stays unmodified. Do not weaken that test.

## 6. Documents RC13b updates together

One feature-branch commit contains the code, the tests, and all three of
these documents. Do not commit them apart.

### 6.1 `docs/MUSE-RC11-COMPATIBILITY.md`

Keep the filename. Keep the rc5 and rc11 rows. Keep the 2026-10-20
installed-source section as historical rc11 evidence.

Replace the opening paragraph with:

```markdown
The read-only reader accepts exactly three reviewed Muse versions: 0.2.1rc5,
0.2.1rc11, and 0.2.1rc13. It refuses every other version and every other
source digest. It does not upgrade Muse, migrate its store, run its native
CLI during reads, or silently change an existing binding.
```

Add this table row under the rc11 row:

```markdown
| 0.2.1rc13 | `8b6667bd475355a955563ddeb1b98444c671cd13f73a1decba6ce227039709ba` |
```

Replace the paragraph that says version 0.2.1rc12 is not in the table with:

```markdown
Replacing `~/.local/share/muse/venv` while a project still names the old version
makes that project's checks refuse until step 2. Versions other than the three
rows above, including 0.2.1rc12, are not reviewed. This allowlist step does not
rebind Knowtation, Muse 108, or Born Free, and it does not install or downgrade
Muse.
```

Add a section `Installed-source review, 2026-10-22` after the 2026-10-20
section. It records the eight imports and the file:line notes from section 1,
states that the reader import list did not change, and states that this is
the RC13b confirmation of those imports, not independent acceptance and not
a general Muse audit.

Replace the sentence that says tests use the single other `MUSE_RUNTIMES`
entry with: the probed `--muse-python` venv is the current runtime, and the
stale binding is `tests/muse/conftest.py` `REBIND_STALE`. In the hosted-job
paragraph, state that there is no hosted rc13 job. Do not add a workflow, a
wheel, or a URL.

### 6.2 Roadmap and handover

`docs/ROADMAP.md` and `docs/OVERSEER-HANDOVER.md` stay paired.

RC13a does not invent a `review_stamp`. In this checkout `cli/ok review
--freeze` refuses at `cli/ok:8` because there is no `.venv`, and this step
does not create one or install a package. The tracked config root is still
the publication checkout, so a launcher that got past that line would refuse
`config_repository_mismatch`. Rebinding that config is out of scope. The
local checklist engine, which is the reviewer that command would call, reports
no findings. RC13a, in the same commit as this file, adds one current section
at the top of the roadmap and the handover. That section records this
thinking-loop pass and the CLI refusal, names RC13b as next, and leaves the
older N1 and rc11 sections in place as history. It does not publish
`docs/NEXT.md`.

RC13b updates those same two sections again. It may mark RC13b done only
after section 7 passes and `/build-verification-review` returns pass. Green
tests alone do not mark RC13b done. RC13b does not invent a following
product task. The handover after a passing build says to stop: the allowlist
now contains the three pairs, and consumer rebind is not authorized. RC13b
does not edit this freeze except to leave it unchanged.

## 7. Seven-tier test matrix

Run from this checkout. The Muse interpreter is the one named in the RC13b
paste block. Pass `--muse-python` as a list argument. Do not run the rc5
composition cell as if it were the rc13 cell.

| Tier | Test | Pass condition |
| --- | --- | --- |
| unit | `tests/v1/test_supported_v1.py` and `tests/v1/test_muse_artifact.py` | The three-pair pin holds. Each exact pair is accepted. `0.2.1rc999`, `0.2.1rc12`, and `0.2.1rc14` are refused. All six cross-paired digests are refused. Malformed output is still refused. The rc5 recovery digest stays `MUSE_RUNTIMES['0.2.1rc5']`. |
| integration | `tests/muse/test_reviewed_runtime_matrix.py` and `tests/muse/test_reader_api_compatibility.py` with the rc13 interpreter | Probe, reader, and allowlist agree on `0.2.1rc13` and the frozen fingerprint. The eight imports succeed under the reader audit hook. The named partner map matches section 3. |
| end to end | `tests/muse/test_runtime_rebind.py`, `tests/muse/test_next_model_suggestion_muse.py`, then the whole `tests/muse` directory, all with the rc13 interpreter | Disposable fixtures rebind from the named stale partner to the live rc13 interpreter. The directory sweep must pass. Real Knowtation, Muse 108, and Born Free trees are not opened. |
| stress | the existing timer in `tests/muse/test_reviewed_runtime_matrix.py:17-25` | The 385-file read finishes in under 15 seconds. No second harness. |
| data-integrity | `test_allowlist_is_the_three_reviewed_pairs` plus the probe/reader equality in the matrix test | The dict is exactly the three pairs in section 2. A second observation of the live tree equals the same fingerprint. |
| performance | the same 15-second bound | The bound is not raised. |
| security | unreviewed-version tests, cross-digest tests, and `test_native_reader_refuses_unreviewed_runtime` | Unknown versions and swapped digests refuse before use. The shared virtualenv is not patched. No shell string is executed. No network call is added. |

If the `tests/muse` sweep fails in a file outside sections 3, 4, and 5, stop.
The only allowed test edits are those three sections. Do not weaken an
assertion to make the run green.

## 8. Explicit non-goals

- No deletion, store migration, or Muse object rewrite. The reader stays read-only.
- No billing and no live spend.
- This file does not authorize merge to `main`, push, release, or deployment.
- No `auto_may_start` field is written.
- This author session does not append an `adversarial_freeze` ledger pass.

## Review record

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| 1 | Freeze-review loop (thinking) | findings | F1, scope bullet: it said the only `cli/` edit was one dict line, while section 2 replaces the whole `MUSE_RUNTIMES` dict. F2, section 5: the API child created its temp file after `readonly`, which refuses `O_CREAT` (`cli/v1_muse_reader.py:29-30`) and refuses unlink (`:31-34`). A probe confirmed import and `hash_file` succeed when the file already exists. F3, the seven-tier end-to-end row did not require the rest of `tests/muse`, so a leftover two-key assumption could ship. Fixed in this file before the stamp. |
| 2 | Freeze-review loop (thinking) | findings | F4, seven-tier close: the stop sentence treated every `tests/muse` failure as out of scope, including the tests sections 3 and 5 tell RC13b to add. A failure in those tests is fixed to this spec. A failure in any other file stops. |
| 3 | Freeze-review loop (thinking) | findings | F5, section 6.2: it told RC13a to wait for a freeze-review stamp. `cli/ok review --freeze --dry-run` exits 2 with the `cli/ok:8` refusal. Creating a `.venv` or rebinding the publication config root is outside this step. The section now records that refusal and does not invent a stamp. |
| 4 | Freeze-review loop (thinking) | pass | Re-read the artifact. F1–F5 are closed. No remaining finding. The local checklist engine reports no findings. |
