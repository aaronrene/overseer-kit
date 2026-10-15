# Test disposition: restored full-product requirements

The FPR-4 combined selection, recorded source/dependencies, bounded repairs and
unresolved acceptance cells are in [combined evidence](../docs/validation/FPR-4-COMBINED.md).
Use `scripts/fpr4_matrix.py` with the explicit
`docs/validation/fpr4/disposition-closeout-selection.json` and separate pinned Muse
interpreter. The runner verifies exact-once execution across disjoint groups on
unchanged source/dependencies; latency and archive checks run separately. The
serial `scripts/fpr4_run.py` accepts the same selection. Its disposition audit accounts for all original files and 104
historical failures. The frozen combined run recorded 1,207 passes and one
changed-contract import assertion failure; its explicit clean-process successor
passed two later cases on unchanged production/dependencies. The 1,209-case
closeout selection is exactly covered by those passing outcomes, not presented
as a second all-green combined run. Raw selection, hashes and failure remain
preserved. Changed bounded command/dependency assertions remain
preserved with concrete successors. Default pytest paths and the earlier
`tools/ci/supported_v1.py` convenience driver are smaller selections; neither
substitutes for this combined matrix. Missing Python/platform/host prerequisites
and the unselected integrated pilot remain unresolved requirements.

FPR-3 restores maintained commands and app/desktop/hosted surfaces through the
single bound CLI. The complete [test disposition](../docs/validation/fpr3/test-disposition.json)
records every original family and all 104 historical failures, with retained
requirements and explicit replacement cases. All 393 original test/support files
remain byte-identical. Historical failures are not relabelled as passes.

The focused FPR-3 selection and logs are in [surface evidence](../docs/validation/FPR-3-SURFACES.md).
The earlier reusable driver is `tools/ci/supported_v1.py`; the FPR-4 record above
defines the expanded combined selection. Use this installation's `.venv`
and a disposable basetemp under a nonrepository parent. The default testpaths
are a convenience subset, never the full release/combined matrix.

Old public tests that inject a CliContext or scrape HANDOVER have maintained
outcomes covered through actual `cli/ok` and bound app-service replacements.
Useful engine/security tests remain required. Source packaging does not claim a
new signed installer. Native Muse requires the separate exact pinned runtime;
real local sockets and toolchains must be available when their tests are selected.
No missing prerequisite may become a skip or a success.

Only superseded mechanisms are excluded: OCI, native/Mach GSR, sole-writer storage,
identity bridges, infrastructure packet prerequisites, live worktree export,
ambient runtime discovery and prompt regeneration. The user-facing evidence
ledger remains maintained. Completed bounded certification, rollback and pilot
records are preserved rather than repeated during this wave.


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
