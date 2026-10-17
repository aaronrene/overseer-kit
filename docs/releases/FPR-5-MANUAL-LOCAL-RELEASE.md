# FPR-5 manual-delivery local source release — 2026-10-17

**COMPLETE locally: version 1.0.0.dev1; new archive verification PASS.**
The owner's current release instruction explicitly authorizes proceeding past
the release-decision stop for this exact local source delivery. It authorizes
the archive, manifest, checksums, separate acceptance provenance, this release
record, bound handoff maintenance and one local documentation closing commit.
It does not authorize installation or rollout.

## Identity and artifact boundary

- Repository: `overseer-kit`, UUID `6988dc4a-5f22-454b-9d68-ac5905b383bf`.
- Physical/Git root: `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery-20261014`.
- Branch: `feat/overseer-v1-recovery-20261014`; lane: `product`.
- Model: GPT-6 Astra; reasoning: High.
- Exact accepted source: `97f052949146c3cf337478927e6d345e353d2063`.
- Accepted Git tree: `3713493a8cc191b2658ed31a6d25cde142be4e7b`.
- Acceptance documentation: `a6d2576dfeb00f8209e56908bef8d192431312cf`,
  whose sole parent is the accepted source above. This was the clean opening HEAD.
- Destination: `/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RELEASES/fpr5-manual-97f0529/`.
- Archive: `overseer-kit-1.0.0.dev1-manual-97f0529.tar.gz`.

The existing accepted `tools/ci/source_package.py` built the archive from a fresh
temporary tree materialized directly from the accepted Git blobs and their modes.
Its supported no-Git input used a seed source inventory. Working-tree files,
later acceptance documentation and this closing commit did not enter the archive.
The temporary source tree was removed after packaging and verification. No
existing artifact was overwritten. Version, source, tests and dependencies are
unchanged. No new ref, worktree, tag or release branch was created.

The package contains exactly 1824 eligible committed source files
plus the generated `SOURCE-MANIFEST.json`. The existing packaging policy excludes
local bindings, canonical NEXT, environments, caches, secret-like filenames and
native build outputs; `VERIFICATION.json` enumerates excluded tracked paths.
This is the existing portable source format, not a full Git repository backup or
portable interpreter bundle. Historical evidence inside it retains its historical
scope. The exact accepted snapshot predates the final acceptance decision, which
is therefore supplied separately.

The unchanged manifest reports `kind: local-source-preparation` and
`release_ready: false`. These fixed packaging fields were not rewritten to imply
broader certification. The owner's limited local release authorization and the
independent manual-delivery acceptance are documented here and in provenance.

## Checksums and acceptance provenance

SHA-256:

| Artifact | Digest |
| --- | --- |
| Source archive | `e33d9d49dc3506733fe62c977b1319b304fc977aaaf0868a3c52f7a1fe54e376` |
| SOURCE-MANIFEST.json | `2e665aae2575701735e4bfc5d3a47e5789dfbe67df6fc884d634e1b5549e6905` |
| FPR-5-MANUAL-ACCEPTANCE.md | `e2b5905acaff2bf5834c8d3f06441a542a95efc859f9b4eb0921afedc4f9d8d8` |

`FPR-5-MANUAL-ACCEPTANCE.md` is a byte-exact copy of
`docs/reviews/FPR-5-MANUAL-ACCEPTANCE.md` at the acceptance documentation commit.
Its Git blob is `a678473c67f337c31131711d2916b70897a64053`.
`PROVENANCE.json` binds the source commit/tree, acceptance commit/blob/hash,
packaging tool and archive/manifest hashes. Relative evidence links in the copied
review resolve from its original repository path; the record is a separately
identified companion, not a replacement source member.

The destination also contains `VERIFICATION.json`, a byte-identical copy of this
record as `RELEASE-RECORD.md`, and a final `CLOSING-RECEIPT.json` identifying the
documentation commit and postcommit bound NEXT readback. `SHA256SUMS` covers every
delivered regular file except itself; its own digest is reported at closeout.
The release record is committed at `docs/releases/FPR-5-MANUAL-LOCAL-RELEASE.md`.
The closing commit documents delivery; it never substitutes for the source
candidate or acceptance documentation commit.

## New artifact verification

The existing packager's archive verification passed. Independent comparisons
against the accepted Git tree checked the entire eligible path set, every file's
bytes, SHA-256, size and executable mode, and normalized tar metadata. The external
manifest is byte-identical to the manifest embedded in the archive. The generated
manifest is the only member that is not an accepted Git blob.

All 791 retained component entries match the recorded final candidate boundary:
295 runtime, 440 test, 40 native, ten packaging, four validation-driver and two
requirements entries, with zero mismatches. Runtime membership was independently
enumerated from archive paths and exactly matches the recorded 295 paths.

- Runtime path/NUL/bytes/NUL SHA-256:
  `cb08617a09222622e5a3e18c9d48ab5c7f5ff216b1191a2fe390b1765b422774`.
- Native configuration SHA-256:
  `d65242ef9ca4be228e791d7596bd2a60ff90ba200445c0d5dbf58229c5eecab6`.
- Observed native binary historical SHA-256 remains
  `a515148a94ffebb88e7520fb194bc0287967484896c44900e6d7ab4e7b364551`.
  No present binary availability, new binary hash inspection or build is claimed.

These are integrity checks of the new deliverables, not reruns of completed
tests, experiments, pilots or reviews. No product launch, dependency acquisition,
installation, rollback exercise, provider request or native build occurred.

## Retained acceptance and custody limits

The independent ACCEPTED verdict applies exclusively to the revised manual-delivery
claim at the pinned source. All acceptance exclusions and qualifications in the
companion review remain controlling; this release adds no product acceptance claim.
The retained selected environment is macOS 15.7.2 arm64, Python 3.11.15/3.14.4 Git
cells and Python 3.14 with pinned Muse 0.2.1rc5. Python 3.11 native Muse is not claimed.
The complete maintained CLI, local browser app, owner-observed desktop and local
read-only hosted surface retain their recorded boundaries.

Cursor sessionStart/stop and automatic continuity remain **DEFERRED / NOT VERIFIED**;
restored/forwarded conversation protection remains **DEFERRED / UNQUALIFIED**;
shared chat-history behavior remains **UNRESOLVED**; the vendor request remains
**OPTIONAL / UNSENT**. The original automatic full-pilot acceptance remains false.

Acceptance uses surviving curated records and historical owner observations.
Missing screenshot originals, unredacted logs, binary/profile/cache and historical
pilot/backup trees were not recovered or reconstructed. Hashes do not restore
custody or support a new visual pass. The purported invalid ENOSPC fragment is
actually a valid 399-byte prior-attempt note with no successful execution evidence,
as the acceptance reviewer records. Raw failures and the original FINDINGS remain
preserved. This archive does not improve or broaden historical evidence custody.

Excluded claims include Windows/Linux qualification, signed/notarized native
installers, new hosted CI, live providers/private-production Muse transport,
real delivery/export, real-consumer migration, sustained multi-user operation and
malicious same-UID/root protection. No automatic host or client enforcement claim
follows from explicit manual NEXT reads.

## Remaining installation and rollout conditions; rollback

Stop after this local release. Installation or consumer rollout needs a separate
owner instruction identifying targets and permitted effects. Before such work:

1. Select the modern bound runtime, or separately scope necessary legacy source
   changes. OPS2 repaired startup/root selection/config confinement only; the old
   source still lacks UUID/branch/digest assertions, canonical writer and fence
   identity comparison. Do not redirect the existing wrapper by implication.
2. Classify each named target's owned assets and lock/footprint drift. Preserve
   owner content, configuration, UUID, lanes, NEXT and history; preserve explicit
   backups and a compatible, drift-guarded rollback. Summary lock maintenance is
   not full sync, and clean Git is not proof of a current installation footprint.
3. Establish the target's physical root/UUID/branch/lane/revision/digest readback
   and mismatch refusal under that separately authorized scope. Use fresh bound
   NEXT before each new task and stop on refusal. No extra manual click is needed
   after a validated agent read; lifecycle delivery remains unqualified.
4. Supply compatible local interpreter and exact prerequisites for the selected
   source installation. Preserve the recorded environment/platform limits; the
   archive is not a self-contained interpreter or signed native installer.

All existing rollback/backup trees, older dirty worktrees, protected refs and Muse
history remain preserved. OPS2's guarded rollback preserves the original source,
interpreter and wrapper and refuses drift; restoring it would also restore the
old dependency defect. Prior runtime defects are not newly certified as safe.
No installation was performed, so there is no installed-state rollback to execute
for this release. Hold these artifacts without altering an installed client.

## Closing maintenance

Entry bound NEXT validated `OVERSEER-FPR5-OWNER-RELEASE-DECISION-1`, kind `stop`,
GPT-6 Astra / High, against the requested repository context. The current owner
instruction supplies the release decision and supersedes that stop for this task.
Initial read-only inspection attempted non-existent config/summary basenames and
JSON parsing of the YAML lock; the actual configured paths and YAML format were
then read. These inspection errors changed no state and were not product reruns.

Only this repository release record, paired ROADMAP/HANDOVER summaries, their two
preserved lock hashes and canonical NEXT are closing documentation changes.
The kit-only aggregate lock digest remains
`sha256:882c3d251152d292378baf00d4b848a8013a321ef1808119d270a81dde0eec18`.
No full sync or hook refresh is performed. Canonical NEXT is published only by the
bound CAS writer with prior digest
`da7976eb461041d6dd73856048d0c781cb34ca2ffc6b72dec96c9b3903ebfaf0`,
Git base `a6d2576dfeb00f8209e56908bef8d192431312cf`, and successor stop action
`OVERSEER-FPR5-LOCAL-RELEASE-COMPLETE-1`. Closing receipt records the actual local
commit and final readback. No completed task is presented as pending.

No installation into existing projects, wrapper or hook change, network,
publication, push, merge, tag, signing, deployment or native build is authorized
or performed. The only repository commit is the authorized local documentation
closeout, with hooks and signing disabled for that invocation.
