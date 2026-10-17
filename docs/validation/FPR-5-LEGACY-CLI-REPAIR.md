# FPR-OPS-2 confined legacy CLI repair

**The legacy CLI missing-dependency failure is repaired.** Its existing source
and Python 3.14.4 interpreter now load the required libraries and start
successfully. The only existing installation changed is
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-main-stable/.venv`.
The global wrapper, stable source and external Python installation are unchanged.
This does not resolve FPR-OPS-1 or qualify restored-window automatic handoff.

The owner authorized `OVERSEER-FPR5-OPS2-LEGACY-REPAIR-1`. This is implementation
and focused author validation, not a new review or independent adjudication.
The [original investigation/legacy plan](FPR-5-HANDOFF-RELIABILITY.md) and
[restoration capture](FPR-5-RESTORE-REPRO.md) remain byte-identical, including
their unresolved-cause and backend-execution limitations.

## Verified inputs and exact change

Recovery entry was clean at `c247186f139c7916a38030ff25fba30f5aa94576`, on
`feat/overseer-v1-recovery-20261014`, repository `overseer-kit`, UUID
`6988dc4a-5f22-454b-9d68-ac5905b383bf`, lane `product`, at the requested physical
root. Bound NEXT validated the prior stop; the current owner instruction
authorized this repair. Runtime and 791 source/test/native/package/driver/
requirements entries match the recorded candidate. Runtime remains
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.

[Opening verification](fpr5-legacy-repair/opening-verification.json) freezes the
legacy source at `d47291d5d9030de5ebef713da95efa978c4d8c6e`, all 841 tracked
source-file hashes/modes, the wrapper and interpreter. The existing interpreter
still resolves to
`/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/bin/python3.14`.
Its binary SHA256 is
`9d8a576754c7fa953404cfe209f94b649aa0f723421fa196e42e081939eae7bb`.

The venv had no cryptography distribution. Its PyYAML package and metadata
were symlinks to `/opt/homebrew/lib/python3.10/site-packages`, not local Python
3.14 dependencies. The repair unlinked only those two aliases inside the target
venv, left their external targets untouched, and added 190 verified library and
distribution-metadata files:

| Distribution | Version | Files | Installed artifact tag |
| --- | --- | --- | --- |
| PyYAML | 6.0.3 | 25 | `cp314-cp314-macosx_11_0_arm64` |
| cryptography | 49.0.0 | 119 | `cp311-abi3-macosx_11_0_arm64` |
| cffi | 2.1.0 | 32 | `cp314-cp314-macosx_11_0_arm64` |
| pycparser | 3.0 | 14 | `py3-none-any` |

These satisfy the stable manifest's PyYAML/cryptography requirements and the
required dependency closure for CPython 3.14. They were selected from the
previously approved installed-file artifact set in
[FPR-4 distribution evidence](fpr4/distribution-repaired-results.json),
`dependencies["3.14"]`. That manifest's SHA256 is
`ca4351d12e79fb47e0c2d0ab0e88a83513d475978e2f4d7cf8542d77df3490c3`.
All 190 files matched before staging; 186 nonempty package RECORD hashes also
verified. [Dependency selection](fpr5-legacy-repair/dependency-selection.json)
retains the exact per-file hashes. This is an exact runtime-library artifact
copy, not a newly fetched or complete wheel installation. No package manager,
download, version substitution, source redirect or bytecode compilation occurred.

The original CFFI RECORD refers to an optional `bin/cffi-gen-src` console
launcher absent from the historical artifact set and source venv. It is unused
by this CLI and was not invented or installed. That original RECORD reference
and the excluded bytecode references remain unchanged. This repair does not
qualify optional generator tooling or a general development environment.

## Validation and preparation failures

Before target mutation, a complete venv backup was copied and compared. The
same dependency repair was then applied to a disposable clone. Five focused
commands checked dependency versions/native operations, actual unchanged CLI
startup, selection of fixture A from B's working directory, selection of B from
A's working directory, and refusal of B's configuration under root A. The first
four exited 0; the refusal exited 4 with `config path outside repo root`.
Rollback restored the clone's original inventory exactly. Only then was the
target repaired and the same five checks performed through its own interpreter
and actual `cli/ok` shim. Those checks passed with the same outcomes.

See [disposable validation](fpr5-legacy-repair/disposable-validation.json),
[target validation](fpr5-legacy-repair/target-validation.json) and
[post-application preservation](fpr5-legacy-repair/preservation-after-apply.json).
Compatibility checks exercise YAML parsing/native binding, CFFI's backend,
pycparser and cryptography SHA256 hashing; no signing, provider or network is
involved. Fixture documents are disposable; no real consumer is initialized,
migrated or altered. Validation caused no target bytecode writes.

Five preparation failures are retained in
[preparation history](fpr5-legacy-repair/preparation-history.json): unavailable
Python xattr API; copy-tool timestamp differences; an external RECORD entry;
the absent optional launcher; and an incorrect initial assumption that the old
PyYAML aliases were empty directories. Each occurred before target mutation
and before dependency/CLI behavioral validation. Native macOS metadata reads,
timestamp restoration, explicit artifact exclusions and symlink-aware repair
resolved them. Failed preparation directories are preserved. No completed
acceptance suite, review, pilot, restoration experiment or failed Cursor launch
was repeated.

## Legacy binding limitation

The actual legacy source supports `-C`, config-path confinement and lane
selection. It does **not** implement `--repo-id`, branch assertions,
`--expect-next` or canonical `next-write`. It extracts a handover fence without
comparing the fence's repository identity to the selected context.

Consequently, the original plan's modern UUID/branch/digest validation cannot be
performed through this fixed legacy source. The new fixture checks prove root
selection and path confinement only. The authorized venv repair cannot add the
missing source features. Startup repair is complete; modern bound handoff or
real-consumer acceptance is not claimed. Recovery coordination continues to
use its existing bound launcher; the global wrapper was not changed or tested
against any real consumer.

## Verified rollback

The retained backup is:

```text
/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261015-fpr-ops2-s8rcdg_c/venv-before
```

Its sibling `selected-artifacts` preserves the exact applied inputs, and
`global-wrapper-before` preserves wrapper bytes. The
[before](fpr5-legacy-repair/venv-before.json) and
[after](fpr5-legacy-repair/venv-after.json) inventories capture bytes, paths,
symlink targets, modes, ownership, mtimes, filesystem flags and extended
attributes. Native copy preserves ACLs. Inode identity and ctime are not
restorable. The [preparation record](fpr5-legacy-repair/preparation.json)
identifies the verified backup and inventory digests.

If rollback is later requested, run from the recovery root:

```sh
.venv/bin/python3 -B docs/validation/fpr5-legacy-repair/repair.py rollback
```

The [guarded rollback implementation](fpr5-legacy-repair/repair.py) refuses if
the repaired environment or backup differs from the recorded inventory. It
removes only added paths, restores the two original symlinks and original
directory metadata, then requires an exact before-inventory match. It never
modifies the external Python 3.10 directories. Rollback returns the original
missing-dependency defect; it was rehearsed in the disposable clone, not applied
to the now-repaired target. Do not bypass a drift refusal by deleting the venv.

## Closeout and limits

ROADMAP and HANDOVER are updated together. Canonical NEXT is published only by
the recovery bound `next-write`, using explicit context and the current expected
digest. The successor is a stop; no further experiment or review is scheduled.
Original findings/failures, old worktrees, protected refs and Muse history remain
preserved. The original `ModuleNotFoundError` record remains historical evidence.

FPR-OPS-1 remains unresolved. Cursor sessionStart/stop remain **owner-postponed
NOT VERIFIED**. Final non-author adjudication and separate owner release remain
unauthorized. No installed client, real profile/account, keychain/privacy,
hook, other global/consumer, network/provider, live export/delivery, fetch/push,
main merge, tag, signing or deployment operation occurred.
