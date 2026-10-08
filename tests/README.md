# Test scope after the v1 reset

`python -m pytest` runs the supported v1 release matrix: `tests/v1` and
`tests/retained`. The complete requirement mapping, baseline counts, and known
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
