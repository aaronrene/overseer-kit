# Repository history and reconciliation status

Observed 2026-11-19, America/Los_Angeles. This is a repository inventory and
review plan, not a release, deployment, runtime rebind, or change of authority.

## Published versions

| Surface | Observed state |
| --- | --- |
| GitHub `main` | `9952ab5a8abe6f77a13e136a4dc48f02fdf16cf8`, PR #96, October 23 |
| GitHub `muse-mirror` | `ea27d722aa4b2edf3080e9ade4bb9d00971e834d`, October 11 publication |
| MuseHub staging `main` | `sha256:ff22b6a82a08c117176c3e2603264a0e49fe8204ce57c3cefe7f5b165a8634f8` |
| MuseHub production | No `aaronrene/overseer-kit` repository returned by authenticated listing or refs lookup |
| Latest published prerelease | `v1.0.0-rc.2` at `d54a228235404bdc27be87b99a79163c7f69b68e` |

The staging Muse snapshot and GitHub `muse-mirror` contain the same 865 file
contents. GitHub `main` contains later accepted work: 151 changed files and
1,100 additional files relative to that snapshot. Its history has 44 commits
not reachable from `muse-mirror`. PRs #92, #93, #94 and #96 were merged after
the last mirror publication. The rc.2 tag is two commits behind `main`.

The original local Muse `main` is older still, at
`sha256:80c922b95203a49a07d1706db41ac051a91414bff298d83739df87028610cec1`.
Do not publish that checkout as the current product or reset newer work to it.
Old dirty and recovery checkouts are preserved historical material.

## Authority and runtime boundaries

The October 8 staging decision retained a Muse-first publication intention.
The later accepted GitHub source has a `git-only` repository configuration and
publication instructions for feature PRs. A remote URL alone does not reconcile
those histories or establish a successful authority migration. Choose and record
the ongoing authority before changing configuration or repointing any main branch.

The reviewed runtime allowlist in GitHub `main` contains Muse `0.2.1rc5`,
`0.2.1rc11`, and `0.2.1rc13`. Installing Muse `0.2.3rc7` does not qualify it for
the kit's bound native reader. A compatibility review and explicit rebind are
separate from repository publication. Do not simply add a version string.

The copied repository-bound launcher refuses in a different checkout with
`launcher_repository_mismatch`. This inventory does not rebind it or invent a
replacement canonical NEXT. Existing `docs/NEXT.md` stays unchanged.

## Integrity and recovery evidence

A fresh staging clone with Muse `0.2.3rc7` returned 140 commits and 139 snapshots,
but full `muse verify --strict` found 736 missing historical blob objects.
Two sampled missing objects were available through the authenticated object GET
endpoint with matching hashes. This establishes a download-completeness issue;
it does not establish server-side deletion of the other objects.

An isolated copy was repaired using 700 hash-matching blobs from preserved local
Muse history and 36 from Git objects. Full verification then passed: 140 commits,
139 snapshots and 1,708 objects. Existing refs were unchanged. No server repair,
cache invalidation or original-checkout mutation was performed.

## Prepared Muse reconciliation candidate

The local branch `reconcile/github-main-20261119` joins preserved Muse ancestry
to a complete import of the observed GitHub `main`:

- Candidate: `sha256:e869f2b24a00e19d491f77f84e54cc1062daa5ad81180971fbffaa861b964dc2`.
- First parent: staging `main` listed above.
- Second parent: `sha256:56092091830da5793038c05d0bc37fd1899dfb3f956830331000ad6b0b5ee14d`,
  the imported GitHub tip.
- Snapshot: `sha256:914f576ef75964b9f8c93c3271ac0c99d9e59d44cffa0477d9c8a37eefc42730`.
- All 267 Git commits, 338 parent links and 188,746 snapshot file entries were
  compared independently; file bytes and ancestry matched, with zero mismatches.
- Full candidate-store verification passed: 408 commits, 339 snapshots and
  3,535 objects. All eight pre-existing staging branch refs stayed unchanged.

The import records original Git SHAs; it does not claim new signatures from
historical authors. Muse's import currently does not preserve Git executable
bits. The exact Git file-mode inventory is retained with the private audit;
14 paths at the source tip are executable. Byte equivalence is not sufficient
to declare a faithful executable-mode round trip. Preserve the Git repository
and tags, and require mode verification before replacing a distribution mirror.

This candidate is local and unpublished. It contains the accepted source before
this documentation PR; a later approved publication must incorporate any newly
accepted changes and recheck the live tips.

## Remaining publication work

1. Record the intended ongoing authority and review the candidate's two-parent
   ancestry, file-mode limitation and preserved historical branches.
2. Qualify any native runtime rebind separately. Keep existing installations intact.
3. Re-read GitHub and MuseHub tips. Stop on changes from the inventory; do not
   force-push or silently replace a newer branch.
4. Have the production owner establish the production repository and publish the
   reviewed content through the agreed review workflow. Preserve old staging refs.
5. Clone the result independently and run full integrity verification, content and
   mode comparison, and an installation check before declaring it current.

## Branch and CI hygiene

GitHub has 65 branches; 37 non-main branches are graph ancestors of `main`.
They are cleanup candidates only, not a deletion instruction. Other branches
include unmerged work, and a graph-only test does not account for squash merges,
active worktrees, release evidence or local-only changes. Preserve `muse-mirror`.

There were no open PRs at the initial observation. No branch protection or active
ruleset was returned for `main`. The supported Python workflow is manual-only;
the latest GitHub tip has a successful Cloudflare Pages check, which is not a
supported-runtime test result. Review required checks before enabling protection
so the rule names correspond to checks that actually run.
