# Hosting clarification and read-only verification gap — 2026-10-17

The owner asked to finish the pasted post-merge handover or explain any blocker.
This follow-up corrects the demonstrated hosting documentation discrepancy and
checks the availability of authenticated read-only Cloudflare access. It does not
reopen the completed PR #92 merge or authorize a release, installation or hosting
configuration change.

## Completed

Fresh GitHub API reads confirm PR #92 remains merged at
`87d40740081c0f5855e75f7aa2df7f16528d4e5c`, and current `main` points to that commit.
The approved PR head remains `18608de80a0f0a5119a41f2fbeba630ab196d450`.

[HOSTING.md](../landing/HOSTING.md) now distinguishes the repository's static assets
from the Cloudflare analytics script observed in served HTML. It identifies four
public pages, requires authenticated verification of configuration, and requires a
recorded baseline before claiming controls are unchanged. This changes documentation
only; HTML, styles, scripts, runtime and hosting configuration are unchanged.

Reused the [merge receipt](PR-92-MERGE.md) and its exact-commit deployment/public-page
checks. Their original observations remain historical evidence, not fresh hosting
control verification. No general product review or test suite was repeated.

## Blocked verification

The plugin-management search for `Cloudflare` returned no plugins. No callable
Cloudflare Pages account/project connector is configured; Sites tools manage a
separate service and cannot verify this existing project. Presence-only checks of
`CLOUDFLARE_API_TOKEN` and `CF_API_TOKEN` were both false. No credential files,
profiles or keychains were searched; no secrets were displayed or requested in chat.

Authenticated verification remains blocked by missing read-only access. A supported
connection must expose the `overseer-kit` Pages project and `overseerkit.com` domain.
Once available, verify production branch and commit, canonical deployment, active
domain ownership/status, project controls and analytics injection settings. Record
inaccessible controls separately and compare against a known baseline where one
exists. Public HTTP responses and the GitHub app check cannot substitute for these
account-level checks. Do not change settings to make the checks pass.

## Validation and custody

The focused [check receipt](hosting-followup/checks.json) covers the documentation
links, paired-summary consistency, preserved summary hashes, runtime identity,
unchanged website executable assets, whitespace and validated bound NEXT readback.
Inherited footprint/drift diagnostics are unchanged; this does not certify those
historical diagnostics or establish successor acceptance.

The correction and the formerly local PR #92 merge receipts are published in
[draft PR #93](https://github.com/aaronrene/overseer-kit/pull/93) from the selected
publication branch. The earlier merge record describes its original local custody;
this follow-up publishes it without altering its observations. Merging the draft needs
a decision covering its exact head and the existing automatic production deployment.
The already merged PR #92 is not modified or remerged. Source and older worktrees
are unchanged.

Accepted source `97f0529` and its manual release retain their original scope. A new
release still needs exact source/version/scope approval, candidate-specific
acceptance, and verified artifact, manifest, checksums and release notes.
Existing-project installation remains on hold.
