# Overseer Kit v1 roadmap

## Published bounded prerelease

[v1.0.0-rc.1](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1) was published at `2026-10-10T00:36:33Z`,
release ID `408458432`, as a prerelease and not Latest. PR #86 main acceptance
and prerelease authorization are complete. The exact tag target is
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`; source metadata still reports `1.0.0`.
The five attachments were independently downloaded and hash/size-verified before
and after publication. The archive holds 861 accepted files and ten executables.

Three retained hosted runs each passed **156 / 156 / 289 tests**, with zero
reported failures/errors/skips and no unresolved supported-test failure.
See the [public evidence index](validation/V1-PUBLIC-EVIDENCE.md),
[Muse publication record](decisions/V1-MUSE-PUBLICATION.md) and
[release closeout](decisions/V1-RELEASE-PUBLICATION.md).
Earlier scoped reviews, installation/rollback and the authorized pilot remain
closed at their original scope; no unchanged milestone was repeated.

## Operating choices and limits

Git-only operation is permanently supported without Muse installation or login.
Muse adoption is explicit; the kit project's own source publication is Muse-first.
The optional Muse package is a labelled recovery build with unchanged exact pins
and immutable artifact URL, not an upstream release. Native clone omitted 19
empty directories while preserving all 861 file bytes; only verified isolated
readbacks restored the approved metadata. Source version `1.0.0` alone cannot
identify rc.1. No stable or complete-product readiness is claimed.

## Separate documentation follow-up

This documentation belongs to a later `docs/v1-publication-closeout` proposal,
not the published rc.1 tree. It corrects stale commands and reconciles completed
publication records. The published tag and five asset bytes remain fixed;
the two companion documents are unchanged copies of the release attachments.
Local planning has not created a source revision, branch, commit or PR for this
follow-up. Future delivery needs its own reviewed Muse source, exact mirror
commit and GitHub PR. Canonical checkout-local NEXT is the only task prompt.

Frozen recovery Git `32254cd939885d9d6f40634997ea5b9c37ea776c`, original refs/edits,
isolated Muse feature/main and held release
`06f988e5a078ede81c9dc664520833980a9a19a3` remain preserved. The held release is
not a distribution target. Consumer access, deployment, production trust reset,
automatic hooks, OCI and any stable release are outside this docs proposal.
