# PR #93 authenticated hosting verification — 2026-10-18

The owner explicitly authorized Wrangler authentication, read-only Cloudflare
verification, focused documentation fixes, and marking ready/merging PR #93 once
production identity/domain and final checks pass. This includes the existing
automatic production deployment. The owner permits carrying a precise unavailable
analytics-setting or historical-baseline limitation through this documentation-only
merge. No release or existing-project installation is authorized.

## Authenticated evidence

[Sanitized Cloudflare receipt](pr93-merge/premerge-cloudflare.json) records successful
GET requests using existing Wrangler-managed authentication (official Wrangler
4.151.1 through npx). No new login was needed. Credentials were captured internally
in memory, never printed or committed. No project dependencies were modified.

- Account `9db4904dce0e99f9234ac003e66ff3ee` matches the existing Pages integration.
- Project `overseer-kit` serves `docs/landing` from GitHub `aaronrene/overseer-kit`.
- Production branch is `main`; automatic production deployments are enabled.
- Canonical production deployment `78f9799d-b958-453e-a6b7-f043aefc098e` succeeded
  for exact main commit `87d40740081c0f5855e75f7aa2df7f16528d4e5c`, with no dirty flag.
- `overseerkit.com` is active on this Pages project. Its zone is active and associated
  with the same account. Domain verification and validation statuses are active.
- Selected build, source, preview and production controls are recorded as a baseline
  for a post-merge comparison. This is not proof that controls were unchanged before
  this session; no historical authenticated baseline has been established.

The [Web Analytics settings endpoint](https://developers.cloudflare.com/api/resources/rum/subresources/site_info/methods/list/)
returned HTTP 403. The Pages response contains no populated analytics tag/token in
its inspected fields; absence of those fields does not disprove the host-injected
script observed in public HTML. Full analytics collection/injection settings remain
unverified. This specific limitation is accepted by the owner's current instruction;
no broader login privileges or settings changes are needed for this merge.

## Focused review and validation

The author reviewed the HOSTING.md correction, the chronological merge/follow-up
records and paired summaries. No runtime or website executable changes are present.
The earlier blocked-verification statements remain historical; the current status
now points to authenticated evidence instead of presenting that blocker as current.

Reuse the existing public-route and source preservation evidence. The
[focused checks](pr93-merge/focused-checks.json) cover changed local links,
paired-summary equality, preserved summary hashes,
whitespace, unchanged runtime/site files, and bound NEXT validation. No general
product review or test suite is repeated. No new independent acceptance is claimed.

Before merge, recheck exact main/head and final-head GitHub checks, review findings
and applicable branch rules. Mark ready and merge with an exact-head guard only
if those checks remain good. Verify merge parents/tree, authenticated production
identity, deployment and public pages/assets afterward. Do not force push, directly
push main, bypass required checks or manually deploy/retry.

PR #92 is already complete and is not remerged. Preserve accepted source `97f0529`,
its manual release, source and older worktrees. A successor release still requires
exact source/version/scope approval, candidate-specific acceptance and verified
artifact, manifest, checksums and release notes.
