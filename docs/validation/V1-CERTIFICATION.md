# Bounded v1 final certification — 2026-10-14

Action: `OVERSEER-V1-RECOVERY-FINAL-CERTIFICATION-1` (review).
Decision: **CERTIFIED**, for the exact claim below. No unresolved certification
blockers remain within that claim. This is the final evidence adjudication for
the bounded recovery milestone, not a new independent architecture/build review.

## Certified claim

**Repository-bound source v1 for local POSIX Git repositories/checkouts and
worktrees under the documented trusted-host model, with Python 3.14.4 as the
validated environment and the public `status`, `init`, `sync`, `next`, and
`next-write` surface.** The claim covers physical-root/UUID and runtime binding,
isolated launchers using the installation's conventional venv, preservation of
living documents, validated read-only status/NEXT, and explicit-context,
expected-digest publication of canonical `docs/NEXT.md` by its confined writer.
It includes the documented unborn and single-closing-commit freshness behavior.

This claim was fixed before adjudicating the verdict. It is bounded by the
[scope reset](../decisions/V1-SCOPE-RESET.md) and the exclusions below. Certification
applies to the repaired source present at the verified starting HEAD, not to all
historical Overseer features or the previous rollback build.

| Binding | Certified source / adjudication context |
| --- | --- |
| Physical cwd and Git top-level | `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014` |
| Configured name / UUID | `overseer-kit` / `6988dc4a-5f22-454b-9d68-ac5905b383bf` |
| Branch | `feat/overseer-v1-recovery-20261014` |
| Starting full HEAD | `f5870f585e625628725e33e0520d50b5b6cd2eab` |
| Repaired implementation commit | `348e0f323a3b17cd5022a1bfd56fa09a6831c51f` |
| Runtime version | `1.0.0.dev1` (unchanged; no release version assigned) |
| Runtime SHA-256 | `b7fa1921fcb586ac6fcf8422f094fe20f9f9a438f64eecdaddd97d347115db95` |
| Lane / model / reasoning | `product` / `GPT-6 Astra` / Extra High |

The starting identity matched in full and the worktree was clean. Git comparison
from the repaired implementation to the starting HEAD showed only documentation
and validation-artifact changes; product source and test selection were unchanged.
Bound status confirmed the repaired runtime digest. This closing action changes
only documentation and canonical NEXT.

## Evidence and adjudication

| Requirement | Preserved evidence | Disposition for this claim |
| --- | --- | --- |
| Independent architecture/completed-build review | [Original review](../reviews/V1-RECOVERY-REVIEW.md) of `d8f10d8` against `d47291d`; 153 supported passes and reproduced R1/R2 | Completed; original **FINDINGS** verdict remains unchanged. Findings assessed separately below. |
| Repair of actionable findings | [Author repair record](V1-RECOVERY.md#r1r2-findings-repair--2026-10-14), [test results](test-results.json), retained before/after logs and XML | 19 failed / 1 passed before repair; 20 passed after repair; complete supported suite 173 passed. Sufficient deterministic evidence to resolve R1/R2 for the bounded claim. |
| Clean source installation and current/previous rollback | [Exercise record](V1-RECOVERY.md#clean-source-installation-and-rollback--2026-10-14), [machine-readable results](install-rollback-results.json), retained commands/log | All 43 exercise checks passed for `348e0f3` → `333f81e` → `348e0f3`, with fixed installation root, explicit refresh and preserved identity/NEXT/documents. Source operability only; previous build retains R1/R2. |
| Separately authorized noncritical pilot | [Pilot record](V1-RECOVERY.md#newly-created-test-repository-pilot--2026-10-14), [machine-readable results](pilot-results.json), retained commands and preservation manifest | Completed in the newly created local test repository with one documentation task and two local closing commits. Adequate for this local source claim; no established-consumer or sustained-use inference. |
| Supported matrix and historical preservation | [Requirement matrix](V1-RECOVERY.md#supported-release-matrix-for-this-milestone), [test disposition](../../tests/README.md), [inventory](../../tests/historical/baseline-test-inventory.json) | Latest preserved complete supported run: **173 passed in 107.49 seconds**, zero failures/errors/skips. All 393 original test/support hashes still match. Historical failures remain. |

The scope reset required the independent review, installation/rollback exercise
and separately authorized noncritical pilot. Each is now recorded as completed.
The original review's blocking findings were specific reproducible defects;
the separately recorded repairs and deterministic failing-before/passing-after
evidence address those defects. Neither the scope reset nor this certification
claims a second independent review of the repairs. The limited pilot satisfies
the bounded local handoff requirement without establishing broader operations.
Taken together, this evidence supports certification of the defined claim.

### R1 and R2 disposition

- **R1 — resolved for this certification by author repair evidence.** The writer
  revalidates captured repository/config/runtime, branch and full HEAD after
  acquiring the directory lock and after candidate fsync, before replacement.
  Deterministic real-Git/real-lock cases change branch, HEAD, config and runtime
  while publication waits; changed observed context refuses without replacing
  old NEXT. Existing stale-digest CAS and concurrent-writer coverage remains.
- **R2 — resolved for this certification by author repair evidence.** Both
  closing-commit parent and committed-NEXT lookups use one captured full commit
  ID, and readers recheck context before emitting output. The deterministic
  H1/H2 mixed-revision case and post-read changes are covered, alongside valid
  unborn and single-closing-commit cases and read-only snapshots.

The independent review remains **FINDINGS at its reviewed revision**; it is not
rewritten as PASS. Its bytes retain SHA-256
`d6bd4958fcade51005bede1b01efbd29b6c64c3b7c5fdf14c147e133d0fc90e0`.
The author repair record is preserved separately and is not labeled independent
validation. This decision closes the two findings for the repaired source only.

## Supported environment, exclusions and limitations

The validated host is this local POSIX/macOS environment with Python **3.14.4**,
ordinary symlinked `.venv` interpreters, Git revision authority, PyYAML **6.0.3**
and pytest **9.1.1** for the recorded suite. Use this installation's `cli/ok` or
its repository-bound launcher. Python 3.11+ is a source prerequisite stated in
the quickstart, not a validated version matrix. Other Python versions and other
platforms are outside this certification.

- No packaged installation/distribution, automatic migration or rebinding,
  existing-consumer migration/workflow, sustained or multi-user operation,
  independent-operator trial, consumer hooks, providers/network, remote
  publication or production deployment is certified. Isolated fixture hook
  coverage does not authorize or certify consumer hook operation.
- The pilot used one maintainer, one session and a newly created test repository.
  Its final local HEAD is `50b5a19b7d6f1c964368140ed0dc3dc91504de16`.
  No broader consumer access follows from that result.
- Trust the local OS and administrator. Malicious same-UID/root actors are
  outside the contract. Git operations and NEXT do not share a global
  transaction; rechecks detect observed context changes, not every possible
  interleaving or change-and-reversion.
- Writes are confined and per-file atomic; sync and source replacement are
  nontransactional. A directory-fsync failure after replacement can report
  failure with complete new NEXT bytes already present. Source rollback needs
  quiescent commands, the same physical installation root and explicit refresh.
  Rollback operability does not certify the previous build free of R1/R2.
- Native Muse revision authority, legacy hosted/app/orchestration features,
  OCI, native/Mach GSR, sole-writer storage, identity bridges and packet-chain
  machinery are outside the public v1 claim; preserved legacy source/tests
  do not imply certification of those features.

The preserved historical baseline is **1,391 passed / 104 failed**: 68 socket
denials, 16 missing-cryptography, nine path/fixture and 11 other failures. The
historical suite remains failing and non-gating for this explicit supported
matrix; it was not rerun, waived or declared green. The installation validation's
initial **171 passed / 2 failed** fixture-placement run and the pilot's incorrect
expected-digest readback remain recorded. The unchanged suite passed after moving
fixtures outside Git; corrected digest readback passed without changing NEXT.
Neither operator error is erased or relabeled a product repair.

## Checks performed for this decision

Only offline, read-only evidence/repository checks and documentation closeout
were needed. No unresolved fact required running a targeted product test. No
supported or historical suite, independent review, installation/rollback exercise
or pilot was repeated.

SHA-256 checks matched all retained repair before/after/supported logs and XML,
both installation supported-run logs/XML, the installation commands/exercise log
and reproduction script, and all six pilot artifacts listed in its JSON.
Parsing the six retained JUnit reports confirmed their recorded test/failure/
error/skip counts. All 393 historical test/support hashes matched. The independent
review and committed machine-readable evidence remain unchanged:

| Evidence file | SHA-256 |
| --- | --- |
| `test-results.json` | `52d625598e9de2f051e387373f6f4664f43330a4ce1abddc5a4e86babef6fc12` |
| `install-rollback-results.json` | `29a34ed755bd1e9d880b83271c7c0c042443ec830c08899de1ab0040fec89dbf` |
| `pilot-results.json` | `16c460c68a251f37be92c33a614e96094b6e1ad5eab200df519fd762a787b407` |

The pilot repository, both older dirty worktrees, local Muse history and rollback
fixture are preserved; no commands were executed in them during this action.
Product source, runtime/config binding, test selection and historical tests are
unchanged. ROADMAP and HANDOVER are updated together; quickstart and the recovery
record point here while retaining the earlier evidence and its historical status.

## Authority and closing boundary

**Certification grants no release, merge, push, publication or deployment
authority. Release or distribution requires a separate owner decision.** No
network/provider access, hooks, other consumer access or superseded machinery is
authorized. No additional implementation task is selected.

The sole canonical successor is `OVERSEER-V1-RECOVERY-CERTIFIED-STOP-1`, kind
`stop`, model **GPT-6 Astra**, reasoning **Extra High**, published only through
bound `next-write`. Its expected prior NEXT digest is
`56e52bc98dad1577a1e86b240c3c442770e38e15ec64cbe7d2a395fc030f78c6` and its base
HEAD is the verified starting HEAD above. Canonical prompt bytes live only in
`docs/NEXT.md`. Exactly one publication succeeded, producing NEXT SHA-256
`118dc6a16c25ccd3516b96a7fc214d6468143803ac2cb93639b83afc8ce8f185`.
Document-link and disposition consistency checks passed; the preexisting recovery
evidence below its new disposition pointer remains verbatim. The closing boundary
is one local documentation commit with
document-consistency/whitespace checks and fully bound status/NEXT readback.
