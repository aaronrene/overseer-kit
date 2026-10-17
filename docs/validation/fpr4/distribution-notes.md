# FPR-4 source installation and environment evidence

The latest validated package is the **repaired-tag artifact** at
`/private/tmp/overseer-fpr4-distribution-repaired-20261014/source.tar.gz`.
Its SHA256 is `fd6b5ebe0fcd87156f15d610a6b8e76beec1ac469ce07b2958a8e5fa961010cd`;
the 1220-file manifest SHA256 is
`f1297351f0d0e1bd6e4dd6481193d36a6708bb2ddf488e62643864216a70a1b8`.
It contains the final product runtime
`bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec` plus the repaired desktop bundler.
Fresh Python 3.14 entrypoints, complete footprint, authenticated desktop app child,
resource manifest/runtime and offline incremental native build pass on this artifact.
The repaired Python 3.11 configured-handover template check passes; its full
cryptography/dependency matrix remains unresolved. See `distribution-summary.json`
and the `distribution-repaired-*` records for the latest bounded outcomes.

The earlier **final-tag artifact** is retained as failing-before/workaround evidence.
It exposed a real BSD `mktemp` defect: Xs followed by `.tar.gz` were left literal,
so a repeated bundle invocation collided with the existing archive. The repaired
script atomically reserves a private `mktemp -d` directory with terminal Xs and
creates its archive inside. Both prior archives remain intact. A frozen-fixture
regression executes the actual script twice under the same TMPDIR and proves
unique mode-0700 directories, identical archive/manifest/runtime identities and
preserved archives. Its durable test passes (one case); the separate direct driver
records five passing checks. Repaired resource preparation/native build also
passes under the ordinary ambient TMPDIR without the workaround. The repair changes the bundler and its focused regression; the root validation
runner separately includes scripts in its packaging-source hash map. The product
runtime digest remains unchanged.

These are author checks of disposable local fixtures. They do not establish
FPR-5 review, a pilot, named-host lifecycle delivery, a native GUI session,
platform acceptance, signing, installation bundles, publication, or release readiness.

The first integrated snapshot uses opening HEAD
`6289d2823184a63e2968d2c5f6a76abab5818368` and runtime digest
`7d38764f026848d7d89d81abedfc62f1de5eefde6443d0032d770c2ff09a20d1`.
All eligible files were copied into a new frozen source tree before packing;
concurrent evidence writes therefore cannot change the artifact. The archive at
`/private/tmp/overseer-fpr4-distribution-20261014-2/source.tar.gz` contains 1,036
manifested files; its SHA256 is
`5f4af72607bae69fa5b73e2bde0ec5f158a057cd5f0db2f083ca69c50d06150e`, and its manifest
SHA256 is `d3e8a61cf5db1dd02633ffe0c03752ade33b52034b33ce095ae7c02a644ab69d`.
Unpacking and repacking produced the exact same archive bytes. Source and dependency
file hashes, every command, exit status and output are in
`distribution-results.json` and the phase-specific `distribution-*-results.json`.
The driver is `scripts/fpr4_distribution_matrix.py`.

Fresh Python 3.14.4 and Python 3.11.15 installations have conventional `.venv`
directories under that new nonrepository parent. Dependencies came from exact
files in the integration installation's pinned local environment; Python 3.11
PyYAML 6.0.3 came from an existing cp311 wheel in the pip cache, with wheel metadata
and archive SHA256 recorded. No package was downloaded, no version was silently
substituted, and Muse is absent from both source environments. Invoking the new
source before provisioning its venv refused with no runtime fallback. Required
CLI/desktop/app/policy/template/skill/CI assets and executable modes are manifested;
local repository bindings, VCS stores and virtual environments are absent.

On Python 3.14, the actual `cli/ok`, `cli/overseer` and newly bound consumer launcher
passed help/NEXT readback from an unrelated cwd. Explicit Git initialization,
status with complete footprint, governance dry-run and Check OK dry-run passed.
The source installation's desktop launcher started its actual local app child,
verified authenticated health against root/UUID/runtime, and shut down the child.
Loopback sockets were explicitly allowed for this bounded check. Exact child argv
and health are in `distribution-exercise-3.14-results.json`; session credentials
are not recorded.

Python 3.11 remains unresolved: the pinned cffi 2.1.0 native cp311 backend is not
available in the inspected pip/uv caches, temporary artifacts or Homebrew library
paths. Cached archive inspection found no corresponding wheel or source archive.
The existing cp314 binary was deliberately not installed into cp311. The exact
native cryptography probe fails with `ModuleNotFoundError: _cffi_backend`.
Initialization succeeds, but actual status fails on the same missing dependency.
The attempted complete Git selection from `disposition-selection.json` exits 4
with 10 collection errors and explicit uncollectable selected nodes. No tests
were relabelled skipped or passed to hide the prerequisite. The separate 63-case
unaffected adapter/template subset had 62 passes and one configured-handover-path
template failure; this subset is not a replacement for the required full matrix.
Initial prerequisite and entrypoint failures are preserved in the adjacent JSON,
log and XML files. Later affected results must be read alongside these initial
failures.

The local native build used macOS 15.7.2 arm64, explicit Rust/Cargo 1.88.0,
`cargo build --locked --offline`, the pinned Cargo lock, and a new target directory.
The initial build compiled dependencies but refused absent `resources/kit`.
After the documented `scripts/bundle-desktop-kit.sh` resource preparation and
manifest verification, the affected native build passed. Both logs remain:
`environment-native-build-initial.log` and `environment-native-build.log`.
The final binary hash, tool binary hashes, dependency lock hash and platform
inventory are retained. No preexisting FPR-3 or earlier build target, rollback fixture, pilot, source
release directory or worktree was used or modified. Later affected builds reuse
only the target directory newly created by this FPR-4 task.

A redundant fresh-source Python 3.14 full Git run was gracefully interrupted
so the root combined runner could complete the same runtime without duplicate
CPU and disk work. Its partial JUnit records 106 passes and two failures in 425
seconds, with zero skips; it is not a completed matrix. The failures are the old
PyYAML-only standalone fixture and the old assertion that restored public commands
must refuse. Exact PID/parent/command verification and SIGINT are recorded in
`distribution-python3.14-interrupt.json`. Pytest exited 1 after its interrupted
fixture teardown raised a stash `KeyError`; this interruption artifact is retained
separately from product failures. The root combined runner was not interrupted.

The initial runtime is recorded separately from any repaired final runtime.
The combined runner and final affected package checks provide the final-source
verdict; this initial snapshot alone does not validate subsequent repairs.

The closeout comparison in `distribution-closeout-equivalence.json` verifies that
all **357 production/package files**, including **295 runtime files** and **40
native inputs**, still match the exercised repaired archive exactly by path,
SHA256, size and executable mode. The production-record digest is
`0fb680ed67e5a9b10f9e1ebe23a4e5227f0c83dcfa071ce6165c74f9b4e42d2d`;
the runtime remains `bdbfdae4599ca0bd1b096d5ed2c84019df3b83ed24972c202319ea5507cf09ec`.
The record separately enumerates later test/documentation changes, including the
new `tests/fpr4/test_import_boundary.py` successor. Those changes are excluded from
the production-equivalence claim and are not retroactively claimed present in the
exercised archive. No further archive or native rebuild was needed or performed.
