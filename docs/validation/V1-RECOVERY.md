# Bounded v1 recovery — public validation closeout

[v1.0.0-rc.1](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1) is published as a prerelease, not Latest.
Main acceptance and prerelease authorization are complete. The documentation on
this branch is a separate later proposal; it is absent from the rc.1 source tree.
The source still reports `1.0.0`; use the tag/commit/manifest to identify rc.1.

## Supported v1 release matrix

The three retained hosted runs each passed **156 Git-only tests on Python 3.11,
156 Git-only tests on Python 3.14, and 289 combined Muse tests on Python 3.14**.
Each has zero reported failures/errors/skips. The [public evidence index](V1-PUBLIC-EVIDENCE.md)
binds every run to its candidate context. No unresolved supported-test failure
remains, and this documentation action did not repeat a closed review or unchanged suite.

Default collection is `tests/v1` plus `tests/retained`; adding `tests/muse` selects
the combined matrix. The exact supported driver is `tools/ci/supported_v1.py`,
run with the kit's conventional `.venv/bin/python` and required `--junitxml PATH`.
Optional `--muse-python` must select the separately installed pinned Muse runtime.
Git-only operation requires no Muse. See [test scope](../../tests/README.md).

| Retained behavior | Supported coverage |
| --- | --- |
| Identity, physical root, init/sync, preservation and NEXT context | `tests/v1/test_commands.py`, `tests/v1/test_isolation.py` |
| Confined I/O, digest, atomic replacement and writer concurrency | `tests/v1/test_integrity.py` |
| Historical source integrity and retained digest behavior | `tests/v1`, `tests/retained` |
| Muse authority, explicit adoption/rollback and controlled mirror | `tests/muse` and the supported driver |

Hosted evidence is Linux with Python 3.11/3.14. Retained local evidence is macOS
arm64 and fixed-path source installations. It does not certify Windows, arbitrary
interpreters, packaged/desktop installs, relocation or arbitrary old-version rollback.

## Earlier reviews, installation and pilot

The bounded architecture review and completed-build review closed after correcting
the duplicate-selector abbreviation and executable-mode sync findings. The earlier
77-test Git core, two clean dependency installations with six fixture lifecycle
stages, and 32 checks in the separately authorized DINERO manual pilot are retained
at their original scope. They are not additional tests in the hosted totals and
are not new reviews of this documentation proposal. The pilot preserved consumer
files and kept automatic hooks off. No consumer was accessed by this follow-up.

The [frozen detailed validation ledger](https://github.com/aaronrene/overseer-kit/blob/293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30/docs/validation/V1-RECOVERY.md)
preserves earlier findings, commands, corrections and milestone results. Its local
paths identify historical operator evidence; they are not downloadable links or
installation instructions. The full later local ledger is also preserved by the
operator. This portable closeout replaces repeated historical NEXT directions
with current conclusions; it does not erase the retained records or their failures.

## Historical baseline failures

Before the scope reset, the full old suite reported **1,391 passed / 104 failed**;
the filtered run reported **1,313 passed / 44 failed / 138 deselected**. The full
failures comprised 68 sandbox socket denials, 16 launcher/PyYAML failures, nine
missing paths/fixtures and 11 other product/test failures. Those former-product
results are not called green. [All 104 failing node IDs](baseline-failures.json)
and the historical test sources/inventory remain preserved. Deferred desktop,
hosted, orchestration and old publishing behavior is outside the bounded CLI.

## MuseHub restoration audit — 2026-10-08

The owner corrected the mistaken removal of Muse authority alongside OCI and
removed the session-count ceiling. Git-only is a permanent choice; Muse adoption
is explicit, and the kit itself publishes Muse-first. The
[original 18-finding audit](https://github.com/aaronrene/overseer-kit/blob/293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30/docs/validation/V1-RECOVERY.md#musehub-restoration-audit--2026-10-08)
records reproduced bridge defects, evidence classes and feature-by-feature scope.
R1 supplied local Muse authority/adoption; R2 supplied controlled mirror preparation
and retry; R3 reconciled source and validated combined installation/rollback.
Later credential compatibility repair and actual delivery evidence are recorded
below. The obsolete budget gate and pending restoration language are historical.
OCI, native GSR, sole-writer machinery, automatic governance rewrites and packet
chains remain excluded; the old deploy path must not be reactivated.

## R2 controlled mirror preparation and retry — 2026-10-08

The [controlled mirror workflow](../../MUSE-BRIDGE-WORKFLOW.md) separates local
prepare/verify from explicitly authorized delivery. It pins source, destination,
expected heads, exact files/modes and plan bytes, refuses dirty/foreign targets,
and never exports onto a development tree. Fixture results remain local evidence;
the later live sequence is reported separately below.

## Muse artifact and CI readiness — 2026-10-08

The optional runtime is an **Overseer recovery build of Muse 0.2.1rc5**, recovered
from verified installed files. It is not an upstream release or reconstruction
of the unavailable original sdist. The [artifact contract](../../tools/ci/muse-rc5-artifact.json),
[recovery recipe](../../tools/ci/MUSE-RC5-RECOVERY.md) and unchanged
[companion guide](../releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md) retain all four
digests and the immutable wheel/source ZIP URL. CI uses
`MUSE_RC5_RECOVERY_WHEEL_URL`; no moving installer or alternate package is accepted.

## Hosted CI execution — 2026-10-09

The relevant retained release runs are feature `37983390020`, PR `37985479580`
and accepted-main `37996198972`, each **156 / 156 / 289** passed.
Earlier candidate runs are historical; their results are not transferred to a
different candidate. No new hosted run was dispatched for this local docs plan.

## Local credential compatibility repair — 2026-10-09

The repaired helper accepts repeatable Git challenge metadata while retaining
strict scalar destination fields, exact HTTPS repository scoping, bounded UTF-8
input and in-memory credentials. The old helper reproduced six fixture failures;
all **39 credential tests** passed after repair. Subsequent non-force Git delivery
authenticated successfully. No credential reset or persistent helper change was
needed. See the immutable released helper/tests and the publication record.

## Repaired candidate live publication — 2026-10-09

The [Muse publication record](../decisions/V1-MUSE-PUBLICATION.md) binds the frozen
recovery Git, accepted Muse revision/snapshot, real two-parent mirror and exact
GitHub acceptance. Native source readbacks verified 861 file bytes. A first mirror
authority read failed before push; a matching read and same-plan retry succeeded.
The original refs/edits, isolated Muse feature/main and held Git-only release
`06f988e5a078ede81c9dc664520833980a9a19a3` remain preserved.

## GitHub acceptance — owner confirmed

The owner accepted PR #86's squash merge to
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`. Its tree
`735b2eb9248148e5c11d377fa79fb1f4dc11b75f` matches mirror
`9c9db93b47ceabd9a021a1d0679cb696d65cc6c2`. The original two-parent mirror
history remains intact; no corrective merge or history rewrite is requested.

## Prerelease published — 2026-10-09

The [release closeout](../decisions/V1-RELEASE-PUBLICATION.md) records release ID
`408458432`, the exact tag, five checksum-bound assets, and independent draft and
published download verification. Publication is complete. These later docs do
not retag rc.1, replace its assets, or change source version metadata.

## Declared limits

Native rc5 clone omitted **19 empty directories** while all **861 file bytes**
matched. Only immutable-snapshot-approved metadata was restored in isolated
readbacks. This limitation remains; dirty-state guards must not be bypassed.
Muse snapshots lack POSIX modes; the ten executable paths require explicit policy.

Private/production Hub state and trust, native linked-worktree mutation/stage
isolation, general file/mode fidelity, semantic-analysis breadth, relocation,
untested platforms and broader consumer rollout remain outside the evidence.
Recovered runtime provenance and rc.1/source-version distinction stay explicit.
No stable or complete-product readiness follows from green bounded tests.
