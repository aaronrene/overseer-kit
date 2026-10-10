> **Dated recovery history; closeout complete.** PR #87 documentation publication,
> production deployment and post-merge CI (156 / 156 / 289, zero failures/errors/skips)
> are complete. No recovery task remains. Earlier pending states below are historical.
> Pre-reset commands mentioned in this record are not exposed by the bounded-v1
> entrypoint. Use the [root README](../../README.md), [docs index](../README.md)
> and [current closeout](../ROADMAP.md). The rc.1 tag and five assets are unchanged.

# rc5 recovery artifact hosting and hosted CI — owner decision

2026-10-09. **Owner-authorized artifact hosting and hosted Linux validation passed.**
The owner submitted `OVERSEER-V1-HOSTED-CI-EXECUTION`, naming the exact public
artifact commit/branch, download URL and repository variable. Authorization includes
non-force recovery feature pushes and supported-v1 hosted runs, scoped CI fixes,
dispatches and retries. It excludes main, force-push, PR, tag/release, MuseHub
publication, real mirror delivery, consumer access, production trust reset,
automatic hooks and OCI. The recovered dependency is not an upstream release.

The artifact branch has been published by normal push at exactly
`bff17390675358b764d43f31f71233ed11a673b0`. Execution evidence is retained under
`../RECOVERY-RUNS/20261009-hosted-ci/`. All three jobs in
[run 37946983229](https://github.com/aaronrene/overseer-kit/actions/runs/37946983229)
passed on recovery candidate `25f319fb5505f86a36933bb7d7ebbb94b626899f`.
Git-only Python 3.11.17 and 3.14.8 each passed 117 tests; combined Muse Python
3.14.8 passed 225, all on Ubuntu 24.04.5 with zero failures/errors/skips.
Final documentation closeout is checked separately; the product release is held.

## Concrete selected hosting location

Read-only GitHub inspection confirmed repository visibility `PUBLIC` and the
current account's `ADMIN` permission. Neither the proposed artifact branch nor
`feat/overseer-v1-recovery` existed in the observed remote matching-ref results.
These observations must be checked again before a write; access credentials alone
are not an owner decision.

An isolated local bare repository was prepared at
`.overseer/local/rc5-github-hosting/artifacts.git`. Its parentless artifact commit is
`bff17390675358b764d43f31f71233ed11a673b0` (tree `bc34c32f108833f0ad28820c812c837411e9a0b7`). It contains exactly the reviewed wheel,
source ZIP and a recovery-provenance `README.md`; no workflow, application source,
local config, NEXT, credentials or history is included. The branch will be retained
while CI depends on it. Its public files are downloadable without credentials.
No release, new repository, storage account, subscription or visibility change is
needed. The two approximately 7 MB files are below GitHub's ordinary Git file
limits. This is a small, fixed CI dependency archive, not a general package registry.

The exact authorized repository variable `MUSE_RC5_RECOVERY_WHEEL_URL` value is:

```text
https://raw.githubusercontent.com/aaronrene/overseer-kit/bff17390675358b764d43f31f71233ed11a673b0/muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl
```

The paired source ZIP URL is:

```text
https://raw.githubusercontent.com/aaronrene/overseer-kit/bff17390675358b764d43f31f71233ed11a673b0/muse-0.2.1rc5-overseer-recovery1-source.zip
```

These URLs identify the exact published artifact commit. Both remote downloads returned HTTP 200 with exact pinned bytes before the
variable was configured and read back. Detailed download and configuration
readback is retained in the execution evidence directory. Both payload hashes were verified
before creating the local commit. `git fsck --full` passed. The upload plan is in
`.overseer/local/rc5-github-hosting/upload-plan.json`. The recovery checkout's HEAD
and refs were not changed by this separate local artifact repository.

GitHub documents [commit-specific permanent links](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files)
and [ordinary Git file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
Using an exact commit plus the existing SHA-256 verifier avoids a moving download
reference. Branch retention is required; this does not promise perpetual hosting.

## Candidate and retained evidence

Repository `overseer-kit`, UUID `6dba88a5-029c-4136-9277-c3a0c81f31a6`, physical
root `/Users/aaronrenecarvajal/OVERSEER_KIT/overseer-kit-v1-recovery`; Git branch
`feat/overseer-v1-recovery`, candidate HEAD
`86d7a78f2b29440eebcbf97dc1afda9fdaa1f4e7`. Recorded origin:
`https://github.com/aaronrene/overseer-kit.git`. This was the starting candidate. The authorization documents and execution
results are reviewed and committed on the same recovery feature branch; updated
source identities and projections are recorded separately for each candidate.

The [artifact-readiness entry](../validation/V1-RECOVERY.md#muse-artifact-and-ci-readiness--2026-10-08)
records local macOS results: **225 combined tests**, **117 Git-only tests on
Python 3.14.4**, **117 Git-only tests on Python 3.11.15**, and **12 artifact
regressions** (included in the supported suites), all with zero failures, errors
or skips. During planning, existing JUnit counts were reread without repeating suites or
closed reviews. Execution runs the required supported suite before its feature
commit; unchanged closed reviews remain closed. The subsequent execution results above close the hosted Linux Git 3.11/3.14
and combined Muse 3.14 validation gap for the recorded candidate.

The original upstream rc5 archive remains unavailable; the last recorded fetch
was HTTP 404. This action did not repeat that network request. The wheel is an
Overseer recovery of installed package bytes, **not an upstream release**.

## Exact payload for owner review

Local directory:
`../RECOVERY-RUNS/20261008-muse-artifact-readiness/build-a/`.

| Item | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl` | 6,969,954 | `6b596288fd61f1d0373ead76eff90f82b14291984bff2dbecf9e51cf0694eb4d` |
| `muse-0.2.1rc5-overseer-recovery1-source.zip` | 6,935,646 | `28f5fefacf5860b600edbb83e3cdd35485b983a900ab229a2a1ea673776ae3f0` |

Both local artifact hashes and sizes were rechecked during this action. The
committed 388-file payload manifest hash is
`3a30de887720d3019ad8a40b300960f97693fc13b91da8814784dabe897115ff`
(also rechecked); the installed Python-source contract is
`7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92`.
The [recipe](../../tools/ci/MUSE-RC5-RECOVERY.md) and
[JSON contract](../../tools/ci/muse-rc5-artifact.json) remain authoritative.
The historical original-sdist and R3 reconstructed-wheel hashes are provenance,
not substitute accepted download digests. Retain the source ZIP alongside the
wheel for independent rebuilding, with the recovery provenance and license intact.

## Explicitly authorized execution scope

| Scope | Bounded permission | Owner decision |
| --- | --- | --- |
| Artifact hosting | Non-force create `ci/muse-rc5-recovery1-artifacts` at the exact prepared commit in `aaronrene/overseer-kit`, publicly retaining the two artifacts and provenance README | Authorized |
| CI configuration | Set repository Actions variable `MUSE_RC5_RECOVERY_WHEEL_URL` on `aaronrene/overseer-kit` to the exact approved wheel HTTPS URL; inspect and record any prior value first | Authorized exact URL |
| Feature-branch publication | Normal, non-force push of the reviewed candidate to `refs/heads/feat/overseer-v1-recovery` at the recorded origin, after checking remote state; no other branch | Authorized |
| Hosted CI | Permit the push-triggered `.github/workflows/supported-v1.yml` run for that exact candidate: Ubuntu Git Python 3.11 and 3.14, plus combined Muse Python 3.14; inspect run IDs, job results and logs | Authorized |
| Manual dispatch or rerun | Same supported-v1 workflow and recovery feature branch; include bounded CI fixes and retries preserving all artifact/source pins, with local validation and source reconciliation for changed candidates | Authorized |
| Pull request | None proposed or needed for this CI decision; no PR creation or update | Not authorized |

The owner explicitly submitted the prepared execution prompt. These named
permissions persist through bounded CI fixes and retries; a repeated approval
request is unnecessary within that scope. Newly proposed publication destinations,
main changes and product delivery remain outside it.

The checked-in workflow downloads the wheel with unauthenticated HTTPS `curl`
without redirect following. The selected URL must serve the exact bytes directly
to hosted runners under that contract. A private endpoint requiring credentials,
an expiring signed URL, or a redirect-only link needs an explicitly reviewed
configuration change; do not place credentials in a repository variable.
No bucket, repository, release or visibility change is implicitly authorized by
the proposed destination field. Any required resource creation must be named.

## Order and acceptance after authorization

1. Record the owner's exact decision and scope. Check the approved host and Git
   destination read-only, including existing objects, remote feature head and
   variable value. Refuse conflicting artifacts or branch history; do not replace
   bytes, force-push, delete resources or broaden scope to make the plan work.
2. Push the exact artifact commit to its named branch without force, then read
   the approved artifacts back over the approved URLs;
   verify their exact filename/size/digests and recovery identity before setting
   `MUSE_RC5_RECOVERY_WHEEL_URL`. Do not reuse `MUSE_RC5_URL` or substitute rc11,
   the moving installer, PyPI Muse, or the historical R3 wheel.
3. Before publishing a changed candidate, review its diff, run the full supported
   suite before any local feature commit as AGENTS requires, and reconcile the
   approved delta into the existing isolated Muse feature branch with exact
   snapshot/projection evidence. Do not claim the prior 854-path projection covers
   these new planning edits. Record the actual candidate SHA to be published.
   Candidate implementation/workflow changes need renewed scoped review.
4. Configure/read back the approved variable before the feature push, because
   `supported-v1.yml` runs automatically on `feat/**` pushes. Permission to push
   must therefore include its hosted CI effects. A manual dispatch is not a
   prerequisite or assumed available; use it only if separately included.
5. Bind each run to the actual pushed SHA and record run URL/ID, event, runner,
   Python versions, individual job conclusions and actual test counts. Expected
   unchanged-suite counts are 117 for each Git job and 225 for combined Muse.
   Preserve logs and visible failures; no skipped, missing, queued or cancelled
   job counts as a pass. Record infrastructure or dependency failures without
   weakening pins. Changed-code retries must be covered by the approval.
6. Record authorized results and unresolved gates, update both summaries together,
   and publish only the actual remaining action through `next-write` with explicit
   context and the expected prior raw NEXT digest; validate disk readback.

## Preserved boundaries and execution results

Git-only remains permanently usable without Muse installation, login or migration.
Muse adoption is explicit. The isolated `feat/overseer-v1-restoration-r3` branch,
original refs/edits and held release are preserved; only the existing isolated Muse feature branch receives reviewed recovery
commits; the originals and its staging main are not mutated. Existing projection evidence binds Git candidate
`86d7a78f2b29440eebcbf97dc1afda9fdaa1f4e7` to Muse source
`sha256:b6c1ce03f8e7c0bbb23c4f4ee1d53b45019a91dc51359661528b0659b88b2344`.
The held release remains the prior recorded
`06f988e5a078ede81c9dc664520833980a9a19a3`; it was not reopened.

Muse-first product publication, live Hub protocol/rights, legacy mirror
reconciliation, real delivery and consumer access remain separate gates under
the [mirror runbook](../../MUSE-BRIDGE-WORKFLOW.md). This authorization grants no main
merge/push, tag/release, deployment, MuseHub write, mirror delivery, consumer access,
production trust reset, automatic hook activation or OCI operation. There is no
complete-product claim or new independent review.

**Execution results:** artifact branch pushed at its authorized exact commit;
both downloads verified; URL variable configured/read back; recovery feature
published; all three hosted jobs passed. No scoped CI fix, rerun or manual
dispatch was needed for the first validation run.
The HTTPS readback, variable value, recovery feature candidates and hosted results
are recorded in the [execution validation](../validation/V1-RECOVERY.md#hosted-ci-execution--2026-10-09)
and sibling evidence directory. No PR, main/release, MuseHub or consumer operation
is authorized or claimed. Both summaries and canonical NEXT track actual results.
