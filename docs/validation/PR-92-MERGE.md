# PR #92 owner-authorized merge — 2026-10-17

**MERGED:** https://github.com/aaronrene/overseer-kit/pull/92

The owner approved proceeding if the final checks remained good, following the
explicit question covering the successor delta, marking ready, merge, and the
existing automatic website-deployment consequence. This supersedes the previous
merge prohibition for PR #92 only. No new release or existing-project installation
was authorized. Entry bound NEXT validated the saved owner-decision stop before
publication of `OVERSEER-PR92-MERGE-1` through the existing CAS writer.

## Exact operation and result

| Item | Verified value |
| --- | --- |
| Approved PR head | `18608de80a0f0a5119a41f2fbeba630ab196d450` |
| Main before merge | `ff9091cc2f3bdb54c679ea2cd27f4d5280d83603` |
| GitHub merge commit | `87d40740081c0f5855e75f7aa2df7f16528d4e5c` |
| Merged at | `2026-10-17T22:01:48Z` |
| Merge tree | `44aa3e3d6c63f6c7984899c25d62ca4eb654d1aa` |
| Final PR state | MERGED, no longer draft |

The [premerge receipt](pr92-merge/premerge.json) confirmed exact head/base,
MERGEABLE/CLEAN and a successful Cloudflare check. No new commits, reviewer
findings, required branch checks or rules appeared. The current bound status and
runtime pin were valid. The finite author review and existing evidence were reused;
no general review, suite or pilot repeated. Owner approval to merge is not a new
independent acceptance or a release decision.

Marked the PR ready through GitHub, then rechecked head and main immediately before
calling the merge API with `sha=18608de...` and `merge_method=merge`. GitHub
[confirmed success](pr92-merge/merge-result.json). Fetching main into this isolated
clone verified both ordered parents, preserving existing histories. The merge tree
is exactly the approved PR tree: zero content differences. No force push, squash,
branch deletion, direct main push or older-worktree change occurred.

## Deployment evidence and limits

The existing Cloudflare integration ran automatically after main changed. Its
[GitHub app check](pr92-merge/main-checks.json) reports success at the exact merge
commit, deployment `78f9799d-b958-453e-a6b7-f043aefc098e`, project `overseer-kit`.
No deployment command/retry or hosting configuration change was invoked.

[Public route receipts](pr92-merge/public-route-checks.json) show HTTP 200 at
`overseerkit.com` for `/`, `/docs.html`, `/scenarios/`, `/source.html`, the stylesheet
and theme script. Cloudflare redirects the two `.html` paths to extensionless
routes. CSS and theme bytes match the merged source exactly.

The initial raw HTML comparison correctly found differences. Inspection identified
exactly one Cloudflare analytics script and one added newline per page. Removing
only that identified host injection yields byte-equivalent source HTML for all
four pages; [comparison receipt](pr92-merge/postmerge-verification.json).
A second inspection request without the successful verification user-agent received
HTTP 403; repeating with the original request headers returned 200. The failed
raw checks are retained and not relabelled exact-byte passes.

**Documentation discrepancy:** `docs/landing/HOSTING.md` says no tracking script
is involved, but the public host injects Cloudflare analytics. This was observed
after merge; it is not a source/runtime mismatch. The hosting guide needs a narrow
clarification distinguishing repository assets from the deployed host, or a
separately approved hosting-settings decision. No settings were changed here.

**Control-plane verification remains unverified:** there is no configured
authenticated Cloudflare tool or token in this session. The GitHub-app receipt and
live domain content do not independently verify Cloudflare account/domain ownership,
canonical production selection or unchanged project controls. No profile/keychain
or credential-file search was performed. The stronger authenticated checks described
by HOSTING.md remain a separately identifiable verification gap; do not claim them
completed or repeat the merge to address them.

## Local closeout and remaining scope

The merge task is complete. Paired summaries and canonical NEXT in the selected
publication checkout record the merged state and the hosting caveats. This closing
documentation commit stays local; it is not part of the already merged PR, and no
new PR, extra main write or preview-triggering push is created for this receipt.
The source checkout and older worktrees remain unchanged. Only the selected clone's
remote-tracking main ref was fetched; its feature-branch context stays bound.

Accepted source `97f0529`, its independent acceptance and local manual release
remain immutable with their original limits. Merging the successor does not expand
that acceptance. Before a new release, separately authorize exact source/version/
distribution and establish the candidate's acceptance, verified artifact, manifest,
checksums and notes. Existing-project installation remains separately held.
Automatic-event, vendor-protection, shared-chat, platform and evidence-custody
qualifications remain as recorded. No new release/tag/installer was published.
