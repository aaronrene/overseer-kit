# FPR-5 acceptance scope — manual delivery, 2026-10-17

**Current scope: existing features, browser and manual repository-bound NEXT.**
The [owner-approved scope revision](../decisions/FPR-5-MANUAL-DELIVERY-SCOPE.md)
supersedes earlier automatic-host prerequisites. The maintained CLI, local app,
actual desktop, local read-only hosted surface, three authority modes, selected
Python cells and source installation/migration/update/rollback remain in scope.
The selected platform remains macOS 15.7.2 arm64 source installation. The
browser is sufficient; no feature removal or browser expansion is requested.

| Requirement | Current acceptance disposition |
| --- | --- |
| Manual repository-bound NEXT | Required. Explicit physical root/UUID, branch/revision, lane, model and action context; digest-checked publication through `next-write`. Existing recorded evidence goes to the single non-author adjudicator. |
| Actual desktop rendering/NEXT | Owner observation and exact copied NEXT comparison were subsequently recorded in [interactive acceptance](FPR-5-INTERACTIVE.md). The original blocked attempt below remains historical; missing screenshot originals remain disclosed. |
| Local integrated workflow | Completed local install/migration, governance/NEXT, ledger, app/desktop, simulated transport and rollback evidence remains in scope. No pilot rerun. The original full automatic-pilot verdict remains unaccepted. |
| Actual Cursor sessionStart/stop and dependent pilot continuity | **DEFERRED / NOT VERIFIED**; excluded from this delivery's acceptance prerequisites, not passed by manual or synthetic bookends. |
| Client-level restored/forwarded conversation protection | **DEFERRED / UNQUALIFIED**; Overseer's own repository checks do not establish client-wide task/tool enforcement. |
| Shared chat-history behavior | **UNRESOLVED**; neither its cause nor a fix is established. |
| Upstream vendor request | **OPTIONAL / UNSENT**, not a release prerequisite; no vendor contact authorized. |
| Evidence custody | Surviving curated evidence with its recorded limits is the submission basis. Unavailable originals are not reconstructed; the final non-author decides sufficiency. |
| Final acceptance / release | One independent non-author acceptance decision remains, then the owner's separate release decision. Neither is started or performed by this documentation change. |

All six repairs, original FINDINGS, raw failures and completed validation remain
preserved. The [current packet](FPR-5-ACCEPTANCE-PACKET.md) contains the exact
revised claim, retained environment/command/authority coverage and review brief.
No completed tests, experiments, pilot or general review are rerun. Existing
platform/distribution/provider exclusions and legacy rollout conditions remain.
Model for this scope reconciliation: GPT-6 Astra; reasoning: High.

## Historical author acceptance record — 2026-10-15

The original report follows unchanged. Its opening identity, then-blocked GUI
observation, automatic-host requirements and former NEXT are historical, not
current instructions. Later desktop evidence and the owner-approved revision
above determine the current scope; deferred requirements are not relabelled passed.

# FPR-5 remaining acceptance — author evidence

Status: local acceptance evidence recorded on 2026-10-15; **two interactive
requirements remain blocked**. This is author acceptance evidence,
not independent adjudication or an owner release decision. The original
[FPR-5 FINDINGS review](../reviews/FPR-5-REVIEW.md), all six
[bounded repair records](FPR-5-REPAIRS.md), raw failures and completed old pilot
remain preserved. Neither completed review nor old pilot is repeated.

## Owner decisions and exact boundary

The owner delegated the acceptance choices, then explicitly instructed:

> Approve the pinned package download and the disposable local pilot. Continue
> here with your recommended acceptance plan. Keep all other network and release
> restrictions.

The physical/Git root is
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`;
configured name `overseer-kit`, UUID `6988dc4a-5f22-454b-9d68-ac5905b383bf`,
branch `feat/overseer-v1-recovery-20261014`, lane `product`, model GPT-6 Astra
with Max reasoning. Opening HEAD is
`2e8ec694def9be4a0faa4a994bf2fff3f212ab23`, the repair closing commit whose sole
parent is `4c62c17cff6c606a5e1ddf565e12353973b3bcad`. Opening Git state was clean;
bound status/NEXT and repair config/lock hashes matched. Runtime remains
`cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.

| Decision | Selected requirement and limits |
| --- | --- |
| Python | Keep complete POSIX Python 3.11 and 3.14 Git cells; Python 3.14 with pinned Muse rc5 remains required separately. Do not waive the missing Python 3.11 cell. |
| Package exception | Official PyPI metadata for cffi 2.1.0 and only its compatible cp311 macOS arm64 wheel; verify published SHA-256. No general dependency upgrade, other download or provider access. |
| Automatic host | Installed Cursor 3.24.18 on macOS 15.7.2 arm64 (OS build 24G325). Both actual sessionStart and stop delivery require evidence. Scripted events and Codex/Claude instruction bookends cannot satisfy this claim. |
| Platform/distribution | Initial acceptance target: macOS Apple silicon source installation, complete CLI, local app, actual desktop GUI and local read-only hosted functionality, including install/migration/update/rollback. All three authority modes remain required. |
| Explicitly deferred claims | Linux/Windows platform claims, native installers, signing/notarization, new hosted CI, live providers and public deployment. Existing implementation and historical evidence remain; these claims are not inferred from local macOS results. |
| New integrated pilot | Only `/private/tmp/overseer-fpr5-integrated-pilot-20261015`, fresh Git project/UUID, branch `pilot/fpr5-integrated-20261015`, lanes `product` and `validation`, Cursor 3.24.18. Hooks may be installed only in this new project. Git-only selection for this pilot does not remove the separate Muse requirements. |

Permitted pilot operations are fresh install and explicit migration with owner
content preservation; bound status and local governance; local Check OK/review;
one confined verification and accurate ledger append/verify; actual local app and
desktop readback; simulated remote operations; explicit digest-checked NEXT,
local closing commits, automatic/manual bookends and quiescent rollback/return.
No actual external provider or delivery/export, working-repository fetch/push,
main merge, tags, signing or deployment is authorized. Loopback is limited to
local acceptance services. Existing consumer repositories and their hooks stay
untouched. Old worktrees, protected refs and Muse history remain preserved.

## Prepared source and prerequisite

A new deterministic source archive was built from the repaired closing source,
verified, unpacked and provisioned offline with exact Python 3.14 dependencies.
Its actual packaged CLI help succeeded. The archive contains 1,483 source files:

- archive SHA-256: `de8cd9222df8cf6c5fe3f4d858e561018baa0dc6d61df1f0ac423928adaed47f`;
- manifest SHA-256: `044ed9bea6a61220604252372b37186584b15e66dd4efbccde1d9901e485134d`;
- local preparation: `/private/tmp/overseer-fpr5-acceptance-preparation-w580lsq4`.

The authorized download obtained
`cffi-2.1.0-cp311-cp311-macosx_11_0_arm64.whl`, SHA-256
`f5bce581e6b8c235e566a14768a943b172ada3ed73537bb0c0be1edee312d4e7`, matching
official PyPI metadata. Redirects and ambient proxies were refused. The first
sandboxed request failed DNS resolution; the narrowly authorized retry succeeded.
Metadata, response details, wheel hash and both attempts are retained.

A new conventional Python 3.11.15 venv in a separate unpacked installation uses
that wheel, the existing local PyYAML 6.0.3 cp311 wheel, and exact locally pinned
cryptography 49.0.0, pycparser 3.0 and validation dependencies. Wheel RECORD and
copied dependency hashes were checked. `_cffi_backend` import and the actual
cryptography operation passed; Muse is absent. This resolved prerequisite
availability. The complete Python 3.11 outcome is recorded separately below.

## Execution and unresolved evidence

The complete repaired Git selection contains 1,196 cases, including all 152 new
FPR-5 repair cases. Its 165 real-native cases remain assigned to Python 3.14:
161 under `tests/muse` and four FPR-4 native cases. Mocked Muse adapter/config and
artifact checks remain in the Git cell. All seven existing changed-contract
replacements remain explicit; no dependency skip or new requirement waiver is
introduced.

Disk exhaustion interrupted the new native build and the initial Python 3.11
collection before tests executed, and truncated one pilot evidence write.
Those raw records are preserved. Only this attempt's rebuildable native target
and compiler cache were reclaimed; historical artifacts were not removed.
The Python 3.11 cell ran in serial disjoint groups with evidence outside the
installation and a free-space floor. Only newly generated fully passing fixture
trees may be reclaimed after their complete raw logs/XML/source records are saved.

### Complete Python 3.11 cell

All 1,196 required cases executed exactly once across nine disjoint groups on
immutable repaired source: **1,195 passed, one failed, zero errors or skips**.
The sole failure was `test_twin_skill_paths_exist`: the fresh source installation
had not yet received the normal generated consumer skills. Actual `init`
without hooks installed that footprint and preserved every one of the 1,483
source members, runtime/test/dependency bytes, HEAD and refs. The unchanged test
then passed. No production change or test waiver was used for this failure.

All **1,196 distinct required cases now have passing evidence** across the
original partitions and that prerequisite-corrected rerun. The original run
remains non-green. After applying only the native configuration fix below, the
two affected package cases also passed separately in clean processes. Their
source snapshots show only that one source member changed; all Python runtime,
tests and dependency bytes remained identical. See
[original partition outcomes](fpr5-acceptance/python311-serial.json) and
[exact reconciliation](fpr5-acceptance/python311-targeted-reconciliation.json).
This closes the missing Python 3.11 cell as author evidence.

### Native startup finding and bounded fix

The first actual GUI launch of a freshly compiled native binary aborted with
`a webview with label main already exists`. The Tauri configuration created a
default `main` window before the Rust setup code created its authenticated
`main` webview. The sole product change in this acceptance action is
`"create": false` on that configured window. Existing Rust setup still creates
the window and injects its authentication state. No Python runtime or test file
changed; runtime SHA-256 remains the pinned value above.

`desktop/src-tauri/tauri.conf.json` changed from
`d834a532c7e67eaf9c7a21c9e80d52a31a7160d6aaad88ee9903078132ef42be` to
`d65242ef9ca4be228e791d7596bd2a60ff90ba200445c0d5dbf58229c5eecab6`.
All other 39 native files and all 295 runtime files match the repaired source.
The candidate build passed offline using a new APFS clone of the verified local
Cargo cache; cloned application/build-script/resource outputs were removed before
compilation. Original cache membership, bytes and modes remained unchanged.
An earlier candidate rebuild stopped at the disk reserve; its record is retained.
Native build success does not by itself establish GUI acceptance.

The repaired candidate binary SHA-256 is
`a515148a94ffebb88e7520fb194bc0287967484896c44900e6d7ab4e7b364551`.
It created one real native window without the duplicate-label panic. A separate
bounded shutdown observation recorded the native process and its Python child,
accepted a normal macOS quit request, and observed exit code zero and an empty
process group before any fallback cleanup. A subsequent connection was refused
and a reuse-address bind succeeded on the local app port; the immediate plain
bind failure remains in the raw record. The startup fix and normal child shutdown
have passing evidence. Rendered desktop content and canonical NEXT readback
inside that window remain **BLOCKED**: own-window capture was refused and
accessibility observation was unavailable. Local HTTP and desktop-child checks
do not replace this required GUI observation.

### Disposable integrated pilot

The new Git-only pilot completed its local install/migration, owner-file
preservation, two-lane governance/NEXT, Check OK, mechanical review, verification
ledger, app/desktop-child, fake hosted/landing, rollback and return exercises.
The pilot ends clean at `4e394520262e1447ae8b5415ae36dc75dc05197e`, UUID
`20dd0872-c7a4-5fdf-81a5-27eefa0acc2e`, with final NEXT digest
`489ded7be7f530ea242e1ed5dbdce96037ec752cc63c9359eaa778aa483ba055`.
Its 102 recorded commands are workflow evidence, not a pytest count. The full
integrated pilot is still unaccepted because actual automatic host events are
missing; a mechanical review is not human or independent approval. See
[raw results](fpr5-acceptance/pilot/RESULTS.json) and the
[durable/external artifact inventory](fpr5-acceptance/pilot/INVENTORY.json).

### Actual automatic host evidence remains blocked

Cursor 3.24.18 recognized both project hook definitions in the disposable pilot,
but neither actual `sessionStart` nor actual `stop` delivery was observed.
The first isolated launch exited during its internal sandbox initialization.
A fresh-profile retry reached renderer readiness with the external-network and
real-account restrictions still enforced, but local debugger observation timed
out and window capture was refused. Its exact process group was terminated and
verified empty. These facts establish a limitation of this attempt, not that
the selected host can never work offline. Synthetic hook invocations, CLI
readback and instruction bookends do not supply the missing native events.

### Remaining gate

Actual Cursor automatic start/end and actual rendered desktop content/NEXT
readback remain open. These keep full selected host/platform and integrated-pilot
acceptance blocked. The complete Python 3.11 cell is now supported by the
explicit reconciliation above.
Completing the two interactive observations requires owner assistance or an
explicit owner decision about that acceptance requirement; neither is waived.
The attempt does not authorize real-profile access, external-provider calls or
changing host privacy permissions. Existing repaired Python 3.14/native Muse
evidence remains valid for its recorded unchanged Python runtime, tests and
dependencies; the native configuration delta and its affected checks are
identified separately here.
Safe, prepared owner-assisted commands and the exact observations still needed
are in [OWNER-NEXT-STEPS.txt](fpr5-acceptance/host-platform/OWNER-NEXT-STEPS.txt).
That helper was syntax checked but has not been executed as an owner observation;
it supplies no additional acceptance claim. Continue in the current session with
GPT-6 Astra, Max reasoning. No new session or model is needed for these checks.
After the complete repaired source and acceptance evidence are ready, reserve
one final independent adjudication by a reviewer who did not author the repairs,
then a separate owner release decision. Neither is performed in this action.

## Preservation and handoff

The acceptance closing commit has the repaired closing commit
`2e8ec694def9be4a0faa4a994bf2fff3f212ab23` as its sole parent. Canonical NEXT
was replaced only through bound `next-write`, using the opening expected digest
and explicit repository/branch/lane/model/action context. ROADMAP and HANDOVER
were updated together. The new action is `OVERSEER-FPR5-INTERACTIVE-ACCEPTANCE-1`,
kind `stop`; it does not appoint the final adjudicator prematurely.

Preservation checks cover all 144 refs (only the active feature ref may advance),
48 original review files, 393 historical test/support files, 603 previously
tracked evidence files including the repair records, all 295 runtime files and
440 current test files. The only native source delta is identified above.
Configuration, disabled working-repository hooks, old worktrees and Muse history
remain preserved. The preexisting unrelated installation-footprint drift is
unchanged; no clean-footprint claim or full installation refresh is made.

[ARTIFACTS.json](fpr5-acceptance/ARTIFACTS.json) inventories the durable evidence.
Nested pilot and host inventories distinguish copied records from externally
retained backups, profiles, caches and binaries. Credential-related Cursor log
lines are redacted only in the durable copies; original local logs remain
unchanged and hashed. Raw failed and incomplete attempts remain explicit.
