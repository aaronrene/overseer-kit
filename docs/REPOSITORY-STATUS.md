# Repository status and preserved reconciliation history

Current guidance reconciled November 22, 2026, America/Los_Angeles. Historical
observations below retain their November 19 scope. This record supersedes
[PR #97](https://github.com/aaronrene/overseer-kit/pull/97)'s current-status guidance
while preserving its useful evidence. The original draft commit is
`6d3b9b8f1fcb87e95d6d7d968461e60b79f65ad4`; its branch and exact source are retained.
[PR #99](https://github.com/aaronrene/overseer-kit/pull/99) carries the reconciled
record and current roadmap. No MuseHub inspection or publication was performed
for this documentation update.

## Current source and authority

The source baseline used here is GitHub main
`4129ef1efd96bf67171cd039d90858dc3013b308`, the accepted merge of
[PR #98](https://github.com/aaronrene/overseer-kit/pull/98). Its runtime tree matches
the independently reviewed rc8 candidate. The exact
[Muse 0.2.3rc8 compatibility contract](MUSE-RC8-COMPATIBILITY.md) records 221 passing
tests, no failures or skips, one explicit historical-fixture deselection with a
tested successor, and a separate bound disposable fixture. Earlier rc5/rc11/rc13
reviewed paths remain; acceptance did not install into existing consumers.

The owner selected **eventual Muse-canonical development hosted on MuseHub** after
cleanup and qualification. GitHub remains authoritative until the
[explicit migration and cutover gates](decisions/MUSEHUB-CANONICAL-ROADMAP.md) pass.
This resolves the older undecided-authority note without treating a remote URL,
a local candidate or a compatibility merge as an executed migration.

The copied source launcher/config/NEXT can still name the historical publication
checkout. A different clone does not inherit that binding or its task authority.
Inspect context first and report mismatch; do not execute the old installation
or manufacture canonical NEXT. Configuration portability remains separate work.

## November 19 observations retained as history

These values describe the earlier audit, not current hosted state. Recheck exact
identity, owner/organization scope, permissions, visibility and complete ref
listings through approved access before preparing a publication manifest.

| Surface | November 19 observation |
| --- | --- |
| GitHub main | `9952ab5a8abe6f77a13e136a4dc48f02fdf16cf8`, accepted PR #96 |
| GitHub muse-mirror | `ea27d722aa4b2edf3080e9ade4bb9d00971e834d` |
| MuseHub staging main | `sha256:ff22b6a82a08c117176c3e2603264a0e49fe8204ce57c3cefe7f5b165a8634f8` |
| MuseHub production | The requested repository was not returned by the audit's listing/refs lookup; no deletion or nonexistence conclusion follows. |
| Published prerelease | `v1.0.0-rc.2` at `d54a228235404bdc27be87b99a79163c7f69b68e` |
| Original local Muse main | `sha256:80c922b95203a49a07d1706db41ac051a91414bff298d83739df87028610cec1` |

The staging snapshot and GitHub muse-mirror matched 865 file contents. At those
observed tips, GitHub main had 151 changed paths, 1,100 additional paths and 44
commits outside the mirror's ancestry; the graph also retained 12 mirror-only
commits. The observed prerelease was two accepted commits behind main. These
comparisons do not describe today's complete repository or authorize replacing
historical refs. Preserve old dirty/recovery trees and both source histories.

The earlier inventory reported 65 GitHub branches and 37 non-main branches that
were graph ancestors of main. Those counts are dated and are not a deletion list.
Ancestry alone does not establish squash equivalence, custody or absence of live
worktree/runtime/evidence dependencies. The original audit's initial no-open-PR
observation also predates the subsequent PRs and is not current status.

## Historical clone-recovery evidence

The November 19 audit used Muse `0.2.3rc7` to obtain a staging clone containing
140 commits and 139 snapshots. Strict verification reported 736 missing historical
blobs. Two sampled objects were retrievable with matching hashes through the
object endpoint. This exposed a clone-completeness gap; it did not establish
server deletion or identify the full delivery/storage root cause.

A separate local copy recovered 700 matching blobs from preserved Muse history
and 36 from Git objects. The recorded strict verification then passed with 140
commits, 139 snapshots and 1,708 objects. Existing refs were unchanged. This was
local reconstruction, not a server repair or proof that a later fresh hosted
clone would be complete. Original stores were not repaired by this operation.
These are preserved results, not tests rerun during the PR #99 documentation work.

## Historical Git-to-Muse candidate and its limits

The unpublished November 19 proposal on `reconcile/github-main-20261119` retained
both staging ancestry and a Git import:

| Identity | Recorded value |
| --- | --- |
| Candidate | `sha256:e869f2b24a00e19d491f77f84e54cc1062daa5ad81180971fbffaa861b964dc2` |
| First parent | `sha256:ff22b6a82a08c117176c3e2603264a0e49fe8204ce57c3cefe7f5b165a8634f8` |
| Imported Git source | `9952ab5a8abe6f77a13e136a4dc48f02fdf16cf8` |
| Imported Muse tip / second parent | `sha256:56092091830da5793038c05d0bc37fd1899dfb3f956830331000ad6b0b5ee14d` |
| Snapshot | `sha256:914f576ef75964b9f8c93c3271ac0c99d9e59d44cffa0477d9c8a37eefc42730` |

The recorded independent import comparison covered 267 Git commits, 338 parent
links, 188,746 snapshot file entries and 3,360 distinct Git blobs, matching bytes
and parent graph. Candidate strict verification reported 408 commits, 339
snapshots and 3,535 objects; eight pre-existing staging branch refs were retained.
Original Git SHAs provide provenance, not newly invented historical signatures.

The source tip had 14 executable paths whose executable mode was not preserved
by the tested import. Later review also identified unsupported symlink/gitlink
representation. Byte equality is insufficient for a faithful working migration;
a tip-only chmod does not preserve executable semantics throughout history.
Retain mode-faithful Git history and qualify any supported conversion or
per-commit restoration/export mechanism before cutover.

The candidate accurately represented the then-selected Git source bytes, but it
was never a complete reconciliation of all local work. It predates accepted PR
#98 and the current documentation. Keep it as a dated recovery proposal; do not
publish or promote it unchanged. Future preparation must use accepted selected
source, retain relevant histories and recheck exact live tips.

## Remaining work

1. Reconcile selected retained work and portable configuration without replacing
   originals or treating older installation records as current tasks.
2. Reproduce clone completeness and historical mode/symlink behavior in disposable
   environments. Any required client/server correction goes through tested review.
3. Prepare exact source/target/ref/privacy manifests with drift checks, faithful
   recovery and rollback. A missing listing does not authorize creating a duplicate
   production repository.
4. Gabriel executes approved shared-hub publication and any production operation.
   Preserve historical refs and avoid forced updates or inferred identity repairs.
5. Independently verify complete fresh clones, content, provenance and executable
   behavior without local object fallback. Accept the authority cutover only when
   the supported working workflow and migration gates pass.

Consumer/global installations remain separately scoped. The hosted supported-v1
workflow remains manual and rc5-specific; a Pages success is not application or
hosted rc8 acceptance. Required CI policy must name checks that actually run and
use reviewed immutable runtime inputs. This record neither changes protection
settings nor triggers a deployment, installation or migration.
