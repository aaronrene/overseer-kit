# Overseer Kit v1.0.0-rc.1 — bounded CLI release candidate

This **prerelease** offers the bounded local CLI and optional
Muse integration for explicit evaluation; it does not declare complete-product
readiness or authorize deployment into another repository.

The release tag is `v1.0.0-rc.1`, targeting exactly
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`. This is the owner-accepted squash
merge of [PR #86](https://github.com/aaronrene/overseer-kit/pull/86). Its tree
`735b2eb9248148e5c11d377fa79fb1f4dc11b75f` matches the approved 861-file mirror
`9c9db93b47ceabd9a021a1d0679cb696d65cc6c2`, including ten executable paths.
The original two-parent history remains preserved on `muse-mirror`.

Source provenance: frozen recovery Git
`32254cd939885d9d6f40634997ea5b9c37ea776c`; accepted staging Muse revision
`sha256:106ef9e12cca7f3be3ffb2a6bd3abfa76f032dce453c9e5010d732a8d86f2e14`;
Muse snapshot
`sha256:36037a7bad29f82f50c7ea6442672dc5df306278859119da5c1e393fead3c0aa`.

## Included behavior

- Repository UUID and physical-root binding; explicit branch, revision, lane,
  model-label and action checks before displaying canonical NEXT.
- Read-only `status` and `next`, explicit initialization and runtime `sync`, and
  a confined `next-write` requiring the previous NEXT digest.
- Permanent Git/GitHub-only operation without Muse installation or login.
- Explicit per-repository Muse adoption and config rollback, plus verified,
  controlled Muse-to-GitHub mirroring. Remote delivery is separately invoked;
  it does not merge a PR or publish a release.

The kit uses a conventional source installation and its own `.venv`. Git-only
operation is supported on the tested Python 3.11/3.14 combinations. Optional Muse
requires a separate Python 3.14 venv and the exact reviewed rc5 recovery wheel.
No packaged Overseer wheel, desktop installer, Windows support or automatic
updater is offered by this release candidate.

## Validation already completed

Each of the three hosted runs passed **156 Git-only tests on Python 3.11,
156 Git-only tests on Python 3.14, and 289 combined Muse tests on Python 3.14**,
with zero reported failures/errors/skips:

- [Feature: 37983390020](https://github.com/aaronrene/overseer-kit/actions/runs/37983390020)
  at frozen recovery Git.
- [PR: 37985479580](https://github.com/aaronrene/overseer-kit/actions/runs/37985479580)
  at the actual mirror head.
- [Accepted main: 37996198972](https://github.com/aaronrene/overseer-kit/actions/runs/37996198972)
  at the tag target.

Earlier scoped architecture/build reviews, source installation/rollback exercises
and the separately authorized DINERO manual pilot remain retained evidence with
their original scope. They were not repeated or relabelled as new reviews of this
release package. No unresolved supported-test failure is recorded.

## Read the companion guide first

Use the attached `INSTALL-AND-ROLLBACK.md` for this candidate. The immutable source
still includes historical guidance: `docs/GIT-ONLY-QUICKSTART.md` mentions
unsupported `governance-sync`, `review` and `status --check-footprint` commands;
README CI/provenance passages predate the recovery-wheel contract and hosted runs.
Those instructions are superseded for this release by the companion guide and
these notes. The runtime, `VERSION` and package metadata still report `1.0.0`;
the rc.1 identity is the release tag, exact commit and manifest. No version bytes
were changed to manufacture a different candidate.

## Known limits and disposition

Native Muse rc5 clone omitted 19 empty snapshot directories while restoring all
861 file bytes. Verified readbacks materialized only the immutable snapshot's
approved directory metadata. This remains an upstream runtime limitation, accepted
as a disclosed prerelease limitation rather than described as repaired. It does
not affect the Git source archive, which has no empty-directory representation.
Muse snapshots also lack POSIX executable modes; mirror export requires the
explicit reviewed ten-path executable policy.

The optional dependency is an **Overseer recovery build of Muse 0.2.1rc5**, not
an upstream release or recovered original source distribution. Its wheel,
recovery source ZIP and package-source hash stay exactly pinned. The existing
immutable artifact URL and artifact branch remain in use; this release does not
replace them or select a moving installer. See the companion guide for exact pins.
Third-party dependency wheels and Python/toolchain binaries are not a completely
hash-locked offline distribution.

Public staging Muse publication is evidenced. Production trust, private Hub
workflows, native linked-worktree mutation/stage isolation, general symlink/mode
fidelity, relocating bound installations and untested platforms are not certified.
Automatic hooks, consumer rollout and OCI are outside this release proposal.

## Assets and documentation

The attachments are the exact source tarball, these release notes,
`INSTALL-AND-ROLLBACK.md`, `release-manifest.json`, and `SHA256SUMS`. Verify checksums
before installation. The manifest binds source and companion documents separately.
Companion documents are release guidance, not additional files in the tagged tree.

Pending local ROADMAP, HANDOVER, publication-decision and validation closeouts are
preserved for a separate documentation-only Muse/source and GitHub PR follow-up.
They are not silently incorporated into this source archive or tag. The older
held release at `06f988e5a078ede81c9dc664520833980a9a19a3` remains untouched.
