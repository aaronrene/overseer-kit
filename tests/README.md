# Test disposition: bounded v1 and FPR-1 foundation

Default collection is the explicit `testpaths` list in `pyproject.toml`:
`tests/v1`, `tests/fpr1` plus unchanged digest/config/path/adapter unit tests and adapter-factory
integration tests. No supported requirement is waived with skips or xfails.

`tests/v1` replaces the old public status/init/sync and print-NEXT contract with
physical-root/UUID binding, canonical NEXT, runtime checks, atomic writer, and
two disposable repositories. The legacy tests assume a different config schema,
CLI context injection, handover prompt scraping and governance regeneration;
those expectations do not govern the replacement CLI.

All 393 original test/support files remain byte-identical at their original
paths, inventoried in `historical/baseline-test-inventory.json`. A supported test
checks these hashes. Original tests outside the explicit supported list are
**historical/non-gating for this milestone**, not deleted or reported as passing.
Hosted/desktop, provider/review/ledger, publication and orchestration capabilities
are outside this first CLI milestone; this does not assert they are permanently
superseded. The full baseline's unresolved failures are recorded in
`docs/validation/baseline-failures.json`.

OCI/NXH and sole-writer/GSR architecture contracts in the dirty original checkout
remain in that checkout and the verified recovery snapshot; none were imported
or restored as a release gate. Git/Muse adapter sources and selected tests remain
available, but adapter passes do not establish native Muse authority for v1 CLI.

Run the supported suite with `.venv/bin/python -m pytest -q -p no:cacheprovider`.
Run historical material explicitly by path when investigating it. See
`docs/validation/V1-RECOVERY.md` for the requirement mapping and exact results.


FPR-1 adds the schema/dispatch/migration/event acceptance cases in `tests/fpr1`.
The exact focused selection, source map, changed historical contracts and failure
record are in [FPR-1 evidence](../docs/validation/FPR-1-FOUNDATION.md).
Run `sh docs/validation/fpr1/run-focused.sh` from the source root; its fixture
parent is outside Git. This includes all supported tests and the specifically
retained migration classification, lane, footprint and bookend-option checks.

The preserved old CLI-injection, `--from-config`, force-promotion and
HANDOVER-scraping tests are not silently made green. Their maintained outcomes
now have actual `cli/ok` tests; changed unsafe contracts are mapped explicitly.
FPR-2 and FPR-3 add authority/lanes and remaining product surfaces before the single
combined FPR-4 validation and independent FPR-5 review. The completed bounded
review, installation/rollback and pilot are not rerun by this wave.
