# Public evidence for v1.0.0-rc.1

This index describes the published prerelease and the evidence retained at its
closeout. It was published in the later documentation closeout (PR #87). It is not an
extra file in the rc.1 archive or a claim of new implementation tests.

## Release and immutable source

- [Published prerelease](https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1): ID `408458432`, published
  `2026-10-10T00:36:33Z`, not Latest at publication verification.
- [Accepted commit](https://github.com/aaronrene/overseer-kit/commit/293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30)
  and [PR #86](https://github.com/aaronrene/overseer-kit/pull/86): accepted squash
  content, with original mirror history retained separately.
- [Published manifest](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/release-manifest.json) and
  [SHA256SUMS](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/SHA256SUMS): source/companion identities and checksums.
- [Exact source archive](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/overseer-kit-1.0.0-rc.1-source.tar.gz),
  [release notes](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/RELEASE-NOTES.md), and
  [installation/rollback guide](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md).

All five asset sizes, SHA-256 values and asset IDs appear in the
[release closeout](../decisions/V1-RELEASE-PUBLICATION.md). The manifest and notes
bind reported Muse provenance to the Git tree. Checksums detect changed bytes;
they are not independent signatures or proof of upstream authorship.

## Retained hosted runs

| Context | Exact candidate context | Public run | Git 3.11 / Git 3.14 / combined Muse |
| --- | --- | --- | --- |
| Recovery feature | `32254cd939885d9d6f40634997ea5b9c37ea776c` | [37983390020](https://github.com/aaronrene/overseer-kit/actions/runs/37983390020) | 156 / 156 / 289 |
| PR #86 | Mirror head `9c9db93b47ceabd9a021a1d0679cb696d65cc6c2`; pull-request workflow context | [37985479580](https://github.com/aaronrene/overseer-kit/actions/runs/37985479580) | 156 / 156 / 289 |
| Accepted main | `293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30` | [37996198972](https://github.com/aaronrene/overseer-kit/actions/runs/37996198972) | 156 / 156 / 289 |

Each reported zero failures/errors/skips. Counts come from retained job summaries,
not merely a green workflow icon. CI proves those tested contexts; it does not
prove all native Muse operations, independent review or complete-product readiness.
GitHub log retention may limit future access; no indefinite retention promise is made.

## Local evidence deliberately separated

| Former reference type | Portable treatment |
| --- | --- |
| Sibling release result, draft/published API responses and download directories | Link the public release, manifest and five attachments; retain hash/size results in the release closeout. Raw execution logs stay operator-held. |
| Hosted job logs stored on the operator's machine | Link the exact public run and state the retained per-job counts. No local path is advertised as a download. |
| Owner acceptance/authorization JSON | State the completed owner decisions and link the actual PR/release outcome. Raw owner messages remain operator-held; a public outcome is not itself proof of private authorization. |
| Native Muse push/readback, directory repair and preservation inventories | Label them operator-recorded observations and retain exact Muse IDs and limits. Public release notes/manifest report those IDs; GitHub CI is not substituted as proof of native writes. |
| Long historical validation/decision logs | Link their immutable accepted-commit versions as historical narrative. Full later local originals are preserved; their machine paths are not public assets. |
| Local planning files, NEXT, UUID/config, review overlay and patch | Excluded from the proposed distribution. The public docs describe the later source/PR boundary without copying a machine-bound prompt. |

The approved local release proposal is intentionally not added to the public tree:
its pending-authorization wording and machine paths are historical, and its exact
approved bytes remain preserved. Published companion notes/guide are included
unchanged under `docs/releases/v1.0.0-rc.1/`; conditional publication wording refers
to their original preparation. Read the release closeout for completed status.

Historical documents outside this follow-up's explicit file inventory remain
historical; this is not a repository-wide rewrite. Their old commands and local
evidence paths are not current operating guidance.

## Completed documentation closeout

[PR #87](https://github.com/aaronrene/overseer-kit/pull/87) merged as
`8b519ab9e44e7f7738ede815d21d6f319b0c9d78`. Automatic production deployment
`c3a1baaf-203c-475b-b6b9-2591a34ddc19` succeeded and became canonical.
[Post-merge CI](https://github.com/aaronrene/overseer-kit/actions/runs/38060695412)
passed 156 / 156 / 289 tests with zero failures, errors or skips.
The rc.1 tag and five assets are unchanged. No recovery task remains.
