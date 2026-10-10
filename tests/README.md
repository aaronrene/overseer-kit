# Test scope after the v1 reset

`python -m pytest` runs the supported v1 release matrix: `tests/v1` and
`tests/retained`, including migration/protocol tests and a standalone installation
that has no Muse package. The additional supported real-Muse matrix is explicit:

```sh
.venv/bin/python -m pytest -q tests/v1 tests/retained tests/muse \
  --muse-python /absolute/path/to/muse-venv/bin/python
```

Selecting `tests/muse` without the separate Muse venv fails; no skip masks that
requirement. Git-only users can run the default suite without installing Muse.
`tools/ci/supported_v1.py` is the shared local/hosted CI entrypoint. Run it with
this source installation's `.venv/bin/python`, `--junitxml PATH`, and optionally
`--muse-python /absolute/muse-venv/bin/python`. It verifies required dotfiles and
pins the reviewed rc5 package sources before combined collection. The checked-in
workflow runs Git on 3.11/3.14 and combined on 3.14. Hosted CI is verified: the
[PR #87 post-merge run](https://github.com/aaronrene/overseer-kit/actions/runs/38060695412)
passed 156 / 156 / 289 tests, with zero failures, errors or skips. The Muse job
uses `MUSE_RC5_RECOVERY_WHEEL_URL` to download the immutable recovery wheel and
verifies its exact artifact contract before installation. No skip hides that installation prerequisite. Legacy
`templates/ci` examples are explicitly historical and must not be activated.

The exact supported procedure, from each source installation with its own `.venv`, is:

```sh
.venv/bin/python -B tools/ci/supported_v1.py --junitxml /tmp/overseer-git.xml
.venv/bin/python -B tools/ci/supported_v1.py \
  --muse-python /absolute/path/to/muse-venv/bin/python \
  --junitxml /tmp/overseer-combined.xml
```

Run the Git command on both Python 3.11 and 3.14; run combined on Python 3.14
with the separate pinned Muse environment. Follow [the recovery artifact contract](../tools/ci/MUSE-RC5-RECOVERY.md)
and the [installation guide](../docs/releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md).
Record each candidate identity and require zero failures, errors and skips.

The complete requirement mapping, baseline counts, and known
historical failures are in `docs/validation/V1-RECOVERY.md`.

The original seven tier directories (`unit`, `integration`, `e2e`, `security`,
`data_integrity`, `performance`, `stress`) and their helpers/fixtures are preserved
at their original paths as **historical pre-reset tests**, except explicitly
retained copies listed below. They are not current release requirements. This
preserves imports, failure evidence, and Git history. Their baseline run was
1,391 passed / 104 failed; no claim is made that their failures were all fixed.

The old API lives in `cli/legacy_main.py` only as historical source. Tests importing
`cli.main` describe the former command surface and require the base revision to
reproduce their baseline. Do not call legacy commands against consumers.

Retained verbatim: `tests/retained/test_footprint_digest.py`, copied from
`tests/unit/test_footprint_digest.py`; v1 uses that module's raw digest primitive.
Other retained requirements have direct v1 replacements: init/sync preservation,
status and NEXT CLI behavior, path confinement, atomic writes, launcher isolation,
staleness and identity. Legacy hosted/desktop, multi-lane orchestration,
freeze/ledger/approval, publish/upgrade/recovery architecture contracts are
superseded or deferred as stated in the scope decision.

The dirty checkout's additional OCI/NXH/NXR tests and modules remain intact there
and in the verified recovery archive. They are not imported into this worktree.
`historical/baseline-test-inventory.json` records every original test's SHA-256.
No original test was deleted to obtain green.
