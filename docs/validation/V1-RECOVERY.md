# V1 recovery milestone — verification, 2026-10-08

**Result: clean source installation and current/previous rollback passed in
session 3; architecture review and corrected build findings remain closed.
Final v1 awaits a separately authorized consumer pilot.** Session 1 reached the session-2 status/NEXT checkpoint
across two disposable repositories. Session 2 independently reviewed the bounded
architecture and completed recovery build; see the review below. The original
implementation evidence is retained in the preceding milestone sections.

## Preservation and base

Original physical checkout and Git root:
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit`; repository name `overseer-kit`;
branch `feat/overseer-context-isolation`; HEAD
`e9be0c4b3cafb149b9f3b7af2ab060f01bbfa504`.

Verified local snapshot:
`/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-SNAPSHOTS/20261008T122430Z-v1-recovery`.
The archive contains 21,213 entries: complete checkout including .git/.muse/venv,
all untracked/ignored payload, operator-owned workspace file, recovery handover,
prior OCI snapshot, and NXR/GSR evidence. Separate all-ref Git bundle (153 refs),
full-index binary staged/unstaged patches, untracked archive, inventory with type,
mode, size, SHA-256, uid/gid/mtime and symlink targets, plus artifact SHA256SUMS.
Archive and untracked archive were reopened and compared; bundle verification,
reopened bare clone and `git fsck --full` passed (two dangling historical commits,
no corruption). All artifact hashes were rechecked after implementation.

All 19,418 original archived regular files rechecked byte-identical with matching
modes; symlink targets matched. An IDE `vscode-merge-base` entry appeared for the
new feature branch in shared Git config; it was removed and exact original bytes
restored. New Git worktree administration and feature refs are intentional
additions. No original payload or historical evidence was deleted. This snapshot
is local and is not an off-device backup.

Implementation worktree:
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery`; branch
`feat/overseer-v1-recovery`; base `d47291d5d9030de5ebef713da95efa978c4d8c6e`.
The [scope decision](../decisions/V1-SCOPE-RESET.md) records the exact local Muse
reconciliation: 835 identical files, six explained repair differences and five
omitted generated/local files. No remote reconciliation or Muse ref mutation.

## Clean-base results before implementation

Python 3.14.4, pytest 9.1.1; base tests used the preexisting development venv, with
bytecode and pytest cache writes disabled. Tests ran in the new untouched feature
worktree before source changes.

| Run | Result | Time |
| --- | --- | --- |
| Full original suite | 1,391 passed, 104 failed | 27.40s |
| Excluding hosted_dashboard, q1_app, q4b_ui, q3_desktop groups | 1,313 passed, 44 failed, 138 deselected | 24.77s |

Full-suite failures: 68 socket bind/listen denials imposed by the sandbox; 16
launcher missing-PyYAML failures; 9 missing paths/fixtures; 11 other product/test
failures. The filtered run still included eight socket denials in LAC tests.
These are classifications of actual tracebacks, not blanket attribution to the
sandbox. [All 104 failing node IDs](baseline-failures.json) retain their categories
and error messages. The former product has unresolved failures; it is not claimed
green. The v1 launcher/environment and canonical documents replace the retained
behavior; deferred desktop/hosted/orchestration/review/publishing defects remain
historical and unresolved.

Exact baseline commands (PY is the original checkout's `.venv/bin/python`):

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -q -p no:cacheprovider --junitxml=/private/tmp/overseer-v1-baseline.xml
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -q -p no:cacheprovider -k 'not hosted_dashboard and not q1_app and not q4b_ui and not q3_desktop' --junitxml=/private/tmp/overseer-v1-baseline-filtered.xml
```

## Supported v1 release matrix

Default pytest collection is `tests/v1` plus `tests/retained`. This follows the
retained requirements, not the result of individual old tests. Every original
test source remains byte-identical at its old path, labeled historical in
`tests/README.md` and inventoried in `tests/historical/baseline-test-inventory.json`.
A supported integrity test verifies that preservation. Dirty OCI/NXH tests remain
in the original checkout and snapshot; none were ported. `cli/legacy_main.py`
preserves the former CLI. It is outside the public v1 command surface.

| Retained requirement | Supported coverage |
| --- | --- |
| Status, init, sync; persistent UUID; living-document preservation | `tests/v1/test_commands.py` (real disposable Git repositories and worktrees) |
| Canonical read-only NEXT; strict metadata; expected repository/branch/lane/model/action ID/kind; stale state | `test_commands.py` (including malformed, copied, duplicate, missing, tampered, unborn, detached, and post-commit cases) |
| Two similar repositories with identical action IDs | `test_isolation.py` (14 matrix tests) |
| Cwd, explicit -C, copied config/NEXT, bound launchers and hooks | `test_isolation.py`, both fixture directions |
| PATH/PYTHONPATH/PYTHONHOME/Git environment poisoning; no neighboring runtime fallback; normal venv symlinks | `test_isolation.py`, `test_commands.py` |
| Confined no-follow reads/writes, hardlink refusal, raw digest, atomic replacement and fsync failures | `test_integrity.py` |
| Concurrent stale writers and readers; bounded reads | `test_integrity.py` (stress and performance coverage) |
| Retained digest module | Six unchanged tests in `tests/retained/test_footprint_digest.py`, plus v1 raw-byte digest regression |

No test skip or expected-failure marker masks a supported requirement. The retained
atomic-write and repository-scope behavior has direct executable regression
coverage rather than the old stale fixture assumptions. No socket service,
consumer repository, push, mirror, merge, release, deployment, or pilot is needed.

## Implementation results

The worktree uses its own conventional Python 3.14.4 venv with standard Python
symlinks. Dependencies were seeded offline from already installed package bytes,
excluding the original editable-package finder and `.pth`; imports resolve to
this checkout and this venv. Runtime requirements are pinned in
`requirements-v1.txt`, development requirements in `requirements-v1-dev.txt`.
Fresh network installation and current/previous rollback are future milestones.

| Run | Result | Time |
| --- | --- | --- |
| Initial v1 regression run | 56 passed, 2 failed | 41.57s |
| Focused command/write tests after correction | 45 passed | 25.72s |
| Two-repository isolation matrix | 14 passed | 22.72s |
| Complete supported suite, including later added boundary tests | **77 passed, 0 failed** | **45.27s** |

The two initial failures exposed sync accepting symlinked docs/NEXT paths. Sync
now refuses those paths before refreshing assets. Additional full-suite coverage
checks relative launchers, malformed hook events/config, dry-run recovery of a
missing launcher, linked Git worktrees, first commits, post-publication fsync
errors, and preservation of old tests.

Commands in the recovery worktree:

```sh
.venv/bin/python -m pytest -q tests/v1/test_commands.py tests/v1/test_integrity.py -p no:cacheprovider
.venv/bin/python -m pytest -q tests/v1/test_isolation.py -p no:cacheprovider
.venv/bin/python -m pytest -q -p no:cacheprovider
./cli/ok -C . status --json
./cli/ok -C . next
```

Own-checkout status and NEXT passed. The original config is preserved verbatim at
`docs/archive/v1/config-before-reset.yaml`; this worktree was explicitly bound once
to UUID `6dba88a5-029c-4136-9277-c3a0c81f31a6`. Its read-only hooks were refreshed;
no real consumer hook was activated. `git diff --check` passed.

Machine counts: [test-results.json](test-results.json). Full logs, JUnit files,
Muse comparison, preservation recheck, and SHA256SUMS are stored at
`/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-1`.

## Limits and next action

Supported: POSIX Git checkouts/worktrees, one lane and configured model per
checkout, source installation with its own venv. Muse-only command integration,
automatic config migration/rebinding, packaged installation and rollback remain
out of this milestone. Scope is a trusted local host, not malicious same-UID/root.
Sync is per-file atomic and rerunnable; it has no transaction/recovery subsystem.
Directory fsync failure after replacement reports failure even though a complete
new NEXT may already be present; readers never see a partially written file.

The implementation run had no unresolved supported-suite failures. The independent
review below identified two additional defects outside that coverage; both are
closed by the correction/recheck recorded at the end of this document. Final v1
remains incomplete. Installation/rollback is now closed by session 3 below.
The current action in `docs/NEXT.md` is **OVERSEER-V1-PILOT-AUTHORIZATION-1**,
kind `stop`. Keep the five-to-eight-session cap.

## Independent architecture and completed-build review — session 2, 2026-10-08

Reviewer: fresh GPT-6 Astra review session, action `OVERSEER-V1-REVIEW-1`, lane
`product`. Physical cwd and Git root both resolved to
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery`; branch
`feat/overseer-v1-recovery`; full HEAD
`2bfa69864ec2f8bb3d89cc66d6353dd111421875`. Config name `overseer-kit`, UUID
`6dba88a5-029c-4136-9277-c3a0c81f31a6`. The checkout was clean before review.
Reviewed the 48-file change from `d47291d5d9030de5ebef713da95efa978c4d8c6e`.

**Architecture verdict: pass for the bounded trusted-host design.** Explicit
physical-root/UUID binding, canonical NEXT, isolated source/venv launchers,
expected-context checks, raw-byte compare-before-write, and directory-locked
atomic NEXT replacement fit the scope. Per-file sync and the documented
post-replacement fsync limitation do not require a transaction or security
subsystem. Historical commands are excluded from the v1 entrypoint. No discarded
OCI/GSR/sole-writer prerequisites are needed to address the findings.

**Completed-build verdict: findings; pass withheld.** Both findings below were
reproduced against the reviewed HEAD using two fresh disposable Git repositories
under `/private/tmp`, removed by `TemporaryDirectory` after the probes. No
production code or permanent tests were changed for this review.

1. **P2 — Reject abbreviated duplicate repository selectors.**
   `cli/v1.py:332`, `345`, and `373–376`: argparse accepts unique long-option
   abbreviations, but the duplicate-binding scan recognizes only full spellings.
   With initialized fixtures A and B, `cli/ok -C A --repo B next` exits 2 with
   `duplicate_binding_option`; `cli/ok -C A --rep B next` instead exits 0 and prints
   B's repository and prompt. A conflicting explicit selection therefore silently
   wins, contrary to the duplicate-selector guard and strict repository contract.
   Disable abbreviation on both the root parser and subparsers, or normalize all
   accepted aliases before duplicate detection. Validate refusal with no prompt
   for abbreviated duplicates as well as the existing full-spelling cases.

2. **P2 — Include executable permissions in sync's asset comparison.**
   `cli/v1.py:278–289`: `apply_assets` schedules replacement only when bytes differ.
   After fixture initialization with hooks, changing `.overseer/bin/ok` and
   `.cursor/hooks/session-start-next.sh` to mode 0644 without changing their bytes
   leaves both unusable. Both `sync --hooks --dry-run --json` and
   `sync --hooks --json` exit 0 with `changed: []`; both files remain 0644 and
   non-executable. Compare required modes as well as content, report mode repairs
   in dry-run, and restore the executable mode during sync. Validate invocation
   of the repaired launcher and hook, plus dry-run non-mutation.

Verification: the exact requested `.venv/bin/python -m pytest -q` completed with
**77 passed, 0 failed, 0 skipped in 51.99s**. These two additional defect probes
are not included in that count; both findings remain unresolved. Own-checkout
`cli/ok -C . status --json` and `cli/ok -C . next` passed. The historical inventory
was compared to the base revision, and the legacy CLI and retained digest tests
were confirmed byte-identical to their base sources. Prior archive/Muse evidence
was read as recorded evidence, not independently re-created or remotely verified.

Disposition: correct the two cited defects within this bounded implementation and
recheck them before granting the completed-build pass. After that pass, the next
engineering milestone is clean installation/current-previous rollback, within the
five-to-eight-session cap. The independently accepted architecture needs no new
packet chain. The existing review NEXT remains unchanged and validates from disk;
this review did not publish a new action or make a local commit. ROADMAP and
HANDOVER were updated together. No real consumer, push, mirror, merge, release,
deployment, consumer hook activation, or pilot was used.

### Same-action recheck — 2026-10-08

The owner repeated `OVERSEER-V1-REVIEW-1` in the same review conversation.
Reconfirmed the physical root, branch, full HEAD, config name and UUID recorded
above, and reread the scope and review evidence. The diff from the recovery base
still contains the same implementation; compared with the reviewed HEAD, only
the three review documents are modified. This is a continuation of session 2,
not another independent reviewer or completed milestone.

Reran the exact `.venv/bin/python -m pytest -q`: **77 passed, 0 failed, 0 skipped
in 54.26s**. Both P2 findings reproduced again in fresh disposable fixtures:
`-C A --rep B next` printed B while the full-spelling duplicate was refused;
dry-run and actual sync reported `changed: []` with the launcher and start hook
still non-executable at 0644. The probe fixtures were removed. Status and NEXT
validated, and `git diff --check` passed. Architecture verdict remains pass;
completed-build verdict remains findings with both defects unresolved. The
conditional installation/rollback milestone has not been started. No production
code, permanent tests, NEXT, or Git refs changed during this recheck.

### Additional independent verification of the same action — 2026-10-08

Reconfirmed physical cwd/Git root, branch, full HEAD, config name and UUID against
the identity recorded above. This invocation began with existing uncommitted
changes in this validation document, ROADMAP, and HANDOVER; those changes were
preserved. Implementation HEAD remains `2bfa69864ec2f8bb3d89cc66d6353dd111421875`.
Reviewed the 48-file diff from `d47291d5d9030de5ebef713da95efa978c4d8c6e`, including
the command/parser and confined I/O implementation, launchers/hooks, supported
tests, scope changes, and historical preservation. This continues the existing
review action; it does not advance the milestone/session budget.

The exact `.venv/bin/python -m pytest -q` passed: **77 passed, 0 failed,
0 skipped in 55.97s**. Independently repeated both finding probes in two fresh
Git fixtures under `/private/tmp`, removed on completion:

- Full-spelling `-C A --repo B next` exited 2 with `duplicate_binding_option` and
  no foreign prompt; `-C A --rep B next` exited 0 and printed B's repository and
  prompt. Finding 1 remains unresolved (`cli/v1.py:332–345`, `373–376`).
- After changing the initialized launcher and start hook to 0644, both
  `sync --hooks --dry-run --json` and `sync --hooks --json` exited 0 with
  `changed: []`. Both assets remained 0644 and failed the executable-access check.
  Finding 2 remains unresolved (`cli/v1.py:278–289`).

Compared all 324 inventoried historical test files with the base revision and
confirmed the inventory hashes. The preserved legacy CLI, retained digest tests,
and archived pre-reset config also match their base sources byte-for-byte.
Archive/Muse preservation claims remain previously recorded evidence, not a new
archive or remote verification. Own-checkout status and canonical NEXT validated;
`git diff --check` passed.

**Disposition unchanged: architecture pass; completed-build pass withheld for
the two P2 findings.** Correct and recheck them before clean installation/current-
previous rollback, keeping the five-to-eight-session cap. Updated both living
summaries; no production code, permanent tests, canonical NEXT, or Git refs were
changed. No new packets, discarded security machinery, real consumers, push,
mirror, merge, release, deployment, consumer hook activation, or pilot was used.


### Findings corrected; repeated review action closed — 2026-10-08

The owner explicitly asked to get out of the repeated-prompt loop. The cause was
handoff handling: the review had completed with actionable findings, but canonical
NEXT still requested the same review. Repeating the suite against unchanged code
could not resolve either finding. The reviewer corrected the two cited defects
and rechecked the original acceptance criteria here. This is same-session finding
closure within session 2, not a claim of another independent review or final-v1
completion. Earlier review observations above are retained as historical evidence.

Starting identity: physical cwd/Git root
`/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery`, branch
`feat/overseer-v1-recovery`, HEAD `2bfa69864ec2f8bb3d89cc66d6353dd111421875`,
config name `overseer-kit`, UUID `6dba88a5-029c-4136-9277-c3a0c81f31a6`.

- Finding 1 closed: `cli/v1.py` disables argparse abbreviation on the root parser
  and every subparser. Abbreviated conflicting selectors before/after the command,
  including equals forms, now exit 2 without a prompt in both fixture directions.
  Full-spelling duplicates still refuse; valid full-spelling selection still works.
- Finding 2 closed: asset planning compares required file modes as well as bytes
  and carries the planned mode into the existing atomic replacement. Dry-run lists
  all three damaged executable assets without changing bytes or modes. Actual sync
  restores the launcher and both hooks to 0755, preserves their bytes and living
  documents, and each repaired executable successfully reads NEXT. Repeated sync
  reports no changes.

Verification: **22 disposable verification cases passed**, using two fresh Git
repositories in a `TemporaryDirectory` under `/private/tmp`; fixtures were removed.
No permanent tests were added. The exact `.venv/bin/python -m pytest -q` then
reported **77 passed, 0 failed, 0 skipped in 54.44s**. The counts are separate;
the 22 cases are targeted script checks, not additional collected pytest tests.
Own-checkout explicit sync refreshed only the runtime digest in config after the
source edit; repository identity stayed unchanged. Status, NEXT and whitespace
checks passed. Existing review evidence was preserved in the validation record.

**Disposition: bounded architecture pass retained; completed-build review closed
with its two findings corrected and rechecked.** No unresolved supported-suite
failure or open finding remains from this review. Clean installation/current-
previous rollback is the next engineering milestone, not another identical review.
Canonical NEXT is published through `next-write` with explicit context and the
prior raw digest as **OVERSEER-V1-INSTALL-ROLLBACK-1**, kind `implement`. ROADMAP
and HANDOVER now summarize this disposition. The five-to-eight-session cap remains;
installation/rollback and the separately authorized consumer pilot are outstanding.
No new packet, security subsystem, real consumer, push, mirror, merge, release,
deployment, consumer hook activation, or pilot was introduced.

## Clean source installation and rollback — session 3, 2026-10-08

Action `OVERSEER-V1-INSTALL-ROLLBACK-1`, lane `product`, model `GPT-6 Astra`.
Physical cwd/Git root: `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery`;
branch `feat/overseer-v1-recovery`; starting clean HEAD
`b2a09775d1daabd0b49003b36b18cfce31434fb5`; config name `overseer-kit`, UUID
`6dba88a5-029c-4136-9277-c3a0c81f31a6`. Initial own-checkout `./cli/ok -C .
status --json` and `./cli/ok -C . next` passed. No production code or permanent
test changed; the closed architecture/build review was not repeated.

**Passed: two clean dependency installations, six fixture lifecycle stages, and
77 supported tests (0 failed, 0 skipped) in 54.46s.** The lifecycle stages are
script assertions, not six additional pytest tests. Each independent runtime
followed previous → current → previous at its original physical path:

| Source | Git revision | Runtime SHA-256 |
| --- | --- | --- |
| Previous / rollback | `2bfa69864ec2f8bb3d89cc66d6353dd111421875` | `f85810afb27de05cff194a01f8b229ea23d9a9b82b5d7613d1d4bd7647133066` |
| Current | `b2a09775d1daabd0b49003b36b18cfce31434fb5` | `045412b50c755e188a37aff017924a1eaf6b21fe57f1b14407e74eb026630bc8` |

Both report version `1.0.0.dev1`; the source digest distinguishes them. Sources
were exported using `git archive`, without copying the recovery venv. Installations
`runtime a` and `runtime b` and Git repositories `fixture a` and `fixture b` lived
under `/private/tmp/overseer-v1-install-2jo3ue_u` (paths intentionally contain
spaces). Each runtime had its own new conventional `.venv`; neither PyYAML nor
pytest was importable before installation. Python was 3.14.4 on Darwin arm64.

The first pip attempt exited 1 because sandbox DNS could not resolve PyPI. The
same installation command passed with approved network access for both venvs,
using `--isolated --no-cache-dir --index-url https://pypi.org/simple`. No installed
package bytes or pip cache were used to seed them. Both `pip check` runs reported
no broken requirements, and isolated imports resolved within the respective
venv. Both freezes: PyYAML 6.0.3, pytest 9.1.1, iniconfig 2.3.1, packaging 26.3,
pluggy 1.6.0, Pygments 2.21.0. The two revisions have identical runtime and dev
requirements; the clean environments remained in place throughout the exercise.

Every lifecycle stage validated direct and bound-launcher status/NEXT, with
explicit expected UUID, branch, lane, model, action ID/kind and NEXT digest.
Both fixtures used `FIXTURE-INSTALL-1` with distinct prompts and identities:
`875f5b76-5978-4ba1-a8be-11235fb07cf0` (A) and
`f315a1dd-454b-46d0-af75-ad745b2054a7` (B). Before each sync, both entrypoints
refused status/NEXT with exit 2 and `runtime_changed`. Dry-run listed only
`.overseer/config.yaml` and changed no fixture bytes/modes. Explicit sync updated
that pin; repeated sync reported `changed: []`. Cross-installation sync refused
with `runtime_installation_mismatch` and made no changes in all six stages.

Assertions preserved the UUID/name/root, Git branch and HEAD, NEXT bytes/digest,
preexisting ROADMAP/HANDOVER, prompt and binary payload bytes/modes, bound launcher
bytes/mode, and original venv configuration. After rollback, every fixture file
outside `.git`, including config, matched its original post-init/publication hash
and mode. No fixture hooks were installed by the lifecycle script; the supported
suite exercises its own disposable hooks. Both installation directories and both
Git fixtures were removed after success.

### Exact commands and retained evidence

All orchestration commands below were invoked from the recovery worktree. The
preserved script contains the assertions, and `commands.jsonl` records every
expanded argv, cwd, expected/actual exit, stdout and stderr, including the initial
DNS failure. `results.json` contains all six status records; `supported.xml` is
the JUnit report; `cleanup.txt` records removal. Evidence directory:
`/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-3`.

```sh
.venv/bin/python /Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-3/validate.py prepare
.venv/bin/python /Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-3/validate.py install
# Same install command retried with network access after sandbox DNS failure.
.venv/bin/python /Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-3/validate.py probe
```

The script exports each revision with `git archive --format=tar -o ARCHIVE REV`
and uses Python `tarfile.extractall(runtime, filter='data')` to replace the local
trusted source at the fixed installation path, leaving its venv in place. Both
revisions have the same tracked file set. For each runtime it invokes (variables
below stand for the corresponding exact paths/UUID/digest in `commands.jsonl`):

```sh
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m venv "$runtime/.venv"
# cwd is the respective runtime:
"$runtime/.venv/bin/python" -m pip --isolated install --no-cache-dir --index-url https://pypi.org/simple -r requirements-v1-dev.txt
"$runtime/.venv/bin/python" -m pip check
"$runtime/.venv/bin/python" -m pip freeze
"$runtime/cli/ok" -C "$fixture" status --json
"$runtime/cli/ok" -C "$fixture" next --repo-id "$uuid" --branch main --lane product --model 'GPT-6 Astra' --action-id FIXTURE-INSTALL-1 --action-kind maintain --expect-next "$digest"
# After each source replacement, status/NEXT must first refuse; then:
"$runtime/cli/ok" -C "$fixture" sync --dry-run --json
"$runtime/cli/ok" -C "$fixture" sync --json
```

The full supported suite ran from the **current disposable source** with its
freshly installed dependencies (cwd `/private/tmp/overseer-v1-install-2jo3ue_u/runtime a`):

```sh
'/private/tmp/overseer-v1-install-2jo3ue_u/runtime a/.venv/bin/python' -m pytest -q -p no:cacheprovider --junitxml=/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261008-v1-session-3/supported.xml
```

### Disposition and limits

No unresolved failure remains in this milestone. The initial network failure was
environmental and resolved by the successful clean downloads. Historical baseline
failures remain as recorded above. This proves a manual fixed-path source upgrade
and rollback for these two revisions on Python 3.14.4/Darwin arm64. It does not
validate package installation, other Python/platform combinations, changing
dependency/schema versions, concurrent commands during source replacement,
automatic recovery, or moving/rebinding an installation. Source replacement is
not atomic; operators must stop commands during it, then explicitly sync. No
current/previous symlink-switching mechanism is introduced. Rolling back to the
previous revision also restores its known historical P2 defects; rollback success
does not endorse that revision for consumer use or reopen the closed review.

Session budget is now **3 of 5–8**. Both living summaries were updated together.
The remaining final-v1 milestone is a separately authorized noncritical consumer
pilot. `next-write` replaces the completed installation action with
**OVERSEER-V1-PILOT-AUTHORIZATION-1**, kind `stop`, using the explicit repository
context and prior raw digest
`1b10ff44b1b702578bf4f616b478474aa263568602e6278625c1e7443fc242aa`.
Publication exited 0; the new raw NEXT digest is
`35afaafe249e089ac3171baba58538f365abf8b23108f5dd8307f31be8158de4`.
The temporary confined prompt was removed after copying it to evidence as
`next-prompt.txt`; `published-NEXT.md` preserves the published document.

```sh
./cli/ok -C . next-write --repo-id 6dba88a5-029c-4136-9277-c3a0c81f31a6 --branch feat/overseer-v1-recovery --lane product --model 'GPT-6 Astra' --action-id OVERSEER-V1-PILOT-AUTHORIZATION-1 --action-kind stop --expect-next 1b10ff44b1b702578bf4f616b478474aa263568602e6278625c1e7443fc242aa --prompt-file .overseer/session-3-prompt.txt --json
./cli/ok -C . status --json
./cli/ok -C . next --repo-id 6dba88a5-029c-4136-9277-c3a0c81f31a6 --branch feat/overseer-v1-recovery --lane product --model 'GPT-6 Astra' --action-id OVERSEER-V1-PILOT-AUTHORIZATION-1 --action-kind stop --expect-next 35afaafe249e089ac3171baba58538f365abf8b23108f5dd8307f31be8158de4
git diff --check
```

Own-checkout status, explicitly validated NEXT, and whitespace checks passed.
No new packet, discarded security subsystem, real consumer, push, mirror, merge,
release, deployment, consumer hook activation, or pilot was used. Final v1 is
not complete; neither the green suite nor this closeout authorizes a pilot.
