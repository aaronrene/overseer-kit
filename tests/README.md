# Test disposition: bounded v1, foundation and FPR-2 authority

Default collection is the explicit `testpaths` list in `pyproject.toml`:
`tests/v1`, `tests/fpr1`, `tests/fpr2` plus unchanged digest/config/path/adapter unit tests and adapter-factory
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


FPR-2 adds `tests/muse` as an explicitly selected required native suite, with
`--muse-python /absolute/pinned/venv/bin/python`. Its fixture verifies rc5 and the
committed package-source pin; a missing prerequisite fails rather than skipping.
Default Git-only collection remains runnable without Muse. The complete focused
selection is `docs/validation/fpr2/run-focused.sh`, with `FPR2_MUSE_PYTHON` set and
fixtures under a nonrepository parent. Source/test mappings and development/final
results are in [FPR-2 evidence](../docs/validation/FPR-2-AUTHORITY.md).

Imported M adoption tests now use normalized schema and retain tracked Git
bindings. Native mirror/history/credential cases retain meaningful safety checks;
new tests cover lane collection/batch CAS, native context races, controlled
upgrades and explicit preservation. Two FPR-1 unavailable-Muse assertions and its
fake native migration prerequisite expectation change to the activated native
contract; real native migration has replacement coverage. Historical D tests,
source-distribution tests pending FPR-3, and the 104 historical failures are not
silently reclassified as passing. These are focused author checks, not the
completed bounded exercises, FPR-4 combined matrix or an independent review.


One preserved footprint assertion,
`test_k7_footprint.py::test_rendered_deploy_script_safety_invariants`, specifically
requires native git-export and automatic push. Its recorded FPR-2 failure remains
visible. The focused runner explicitly deselects that superseded route and runs
`tests/muse/test_product.py::test_bound_bridge_wrapper_uses_controlled_offline_service`
in its place, alongside target/projection/retry/credential tests. The replacement
executes the actual wrapper from a foreign cwd and checks offline prepare/verify,
legacy flag refusal and delivery refusal without explicit transport authorization.
The original historical test is byte-identical; it is not silently made green.
