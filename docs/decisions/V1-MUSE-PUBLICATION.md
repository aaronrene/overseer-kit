# Muse-first publication and legacy mirror decision — 2026-10-09

**Status: bounded local reconciliation implemented; remote publication is not
authorized.** The owner authorized this implementation, disposable fixtures, local
feature commit and reconciliation into the existing isolated Muse feature. The
new `mirror reconcile` operation preserves both approved GitHub histories as ordered
parents of a source-exact snapshot. Scoped GitHub credentials are exercised with
fixture tokens only. Actual remote acceptance remains unvalidated.

## Frozen implementation candidate

The exact post-commit Git SHA, Muse revision/snapshot, local projection SHA and
parents, executable list, full path/hash/mode manifest and updated delta are
recorded together in
[`candidate.json`](../../../RECOVERY-RUNS/20261009-mirror-reconciliation/candidate.json),
[`source-latest.json`](../../../RECOVERY-RUNS/20261009-mirror-reconciliation/source-latest.json)
and [`projection-latest.json`](../../../RECOVERY-RUNS/20261009-mirror-reconciliation/projection-latest.json).
These local closeout records are written after the commit and source reconciliation;
they avoid embedding a candidate's own Git or Muse digest in its hashed files.
The portable JSON below is retained as the **reviewed starting delta**. The new
complete delta is in the frozen source record; it includes this implementation
and all planning/closeout documents. No permission for the starting candidate
extends to the new candidate or to later edits.

## Reviewed starting candidate and destinations

These are the planning baseline identities, retained for comparison, not the new
implementation candidate or an approval:

| Item | Exact identity |
| --- | --- |
| Recovery Git candidate | `2d689a8398002ce667743ac7fefd12291b8973bf` |
| Git feature | `aaronrene/overseer-kit:feat/overseer-v1-recovery` |
| Isolated Muse feature | `feat/overseer-v1-restoration-r3` |
| Muse candidate | `sha256:987d0cde6e15bf17e0a9db96f94a6d03fdcefa6e52f7543c141b2998c38bddfa` |
| Muse snapshot | `sha256:dbda007c1c2b058039369d9dc7a3a8c3dd851a585c05dd2790965c0a14d6bc0d` |
| Muse logical repository | `sha256:f5863e477e2f2caf510df731720976d3d91fdd821fd5657ec8da6b57c89a3bea` |
| Public staging source | `https://staging.musehub.ai/aaronrene/overseer-kit` |
| Observed staging main | `sha256:208d9dc47f0c6d8553ee80aafc8f0993a6ebf0a88410746f47f58b4e7c6fd6a6` |
| Git destination | `https://github.com/aaronrene/overseer-kit.git` |
| Existing distribution branch | `muse-mirror` at `3e21496f7c4eab64b6d9ab3f868c5cdcaf8cfcde` |
| GitHub PR base | `main` at `d47291d5d9030de5ebef713da95efa978c4d8c6e` |
| Disposable projection, not a delivery candidate | `b462344c0bd99994a1d07759f5c5d6c7b64efa47` |

The isolated source is
`../RECOVERY-RUNS/20261008-muse-restoration-r3/isolated-muse-source`.
Its starting candidate was five commits after the observed staging main; all **855** paths,
bytes and ten executable modes match the Git candidate and retained projection.
The proposed future publication checkout and new bare target are, respectively,
`/Users/aaronrenecarvajal/OVERSEER_KIT/RECOVERY-RUNS/20261009-muse-publication-delivery/source`
and the sibling `mirror.git`. Their parent directory is currently absent. These
are dedicated kit publication paths, never original or consumer working trees.

The original planning documents were outside that 855-file baseline. The new
implementation commit includes them and the bounded migration. The frozen records
above identify the resulting candidate; the old hosted pass remains bound solely
to its original SHA.

## Retained read-only findings from publication planning

Staging `/refs` returned HTTP 200 with the exact logical ID above, `domain: code`,
default branch `main` and the recorded main revision. Its only other advertised
branch, `feat/adversarial-freeze-honesty-gate`, has that same revision. The recovery
feature is not published. The actual `NetworkDelivery.authority` reader accepted
this response and returned the expected ID/main pair. This closes the earlier
unknown about the **public read protocol**, not the write protocol.

TLS validation succeeded and the certificate matched the existing native Muse
pin, `sha256:f32899524a3c1210b9e6ba60ce80cc3b203d3344ddac7c00d7c6abd9b52d271e`.
Muse fingerprints use `blob_id(DER)`, not plain SHA-256 of DER. No pin, identity or
configuration was changed. Production was not contacted and its earlier trust
issue remains outside this staging plan.

The stored staging signing identity has handle `aaronrene`. Signed GETs for
repository metadata, collaborators, settings and open proposals returned 200.
The repository reports owner/ownerUserId `aaronrene`, public visibility,
`domainId: code`, no collaborators and no open proposals. The generic metadata
field `domain: generic` is inconsistent with `/refs` and `domainId`; delivery uses
the checked `/refs` code-domain contract. Settings allow merge commits and squash,
disable rebase, and set `deleteBranchOnMerge: true`. These reads establish the
available identity and reported ownership, **not proven push or merge rights**.
No write probe was attempted. `/openapi.json` returned an HTML application page,
not an API schema; it provides no additional write-contract evidence.

GitHub reports public visibility and current viewer permission ADMIN. Read-only
remote refs and fetched objects establish the heads above. No open GitHub PR was
returned. No current `release/overseer-v1.0.0` branch or `v1.0.0` tag was returned
by the targeted ref check. The separately hosted artifact branch remains at
`bff17390675358b764d43f31f71233ed11a673b0`.

## Reviewed starting reconciliation delta

[The exact delta](V1-MUSE-PUBLICATION-DELTA.json) records every changed path,
before/after SHA-256, modes, five staging-only removals and the executable list.
The current GitHub main and legacy mirror have **identical 841-file trees**.
Their histories differ: merge base `ebaf51831770c59d3705da85e9d72108908a8bf2`,
one main-only commit and six mirror-only commits. There is no mirror-only file
content to import into the candidate; both histories still must be preserved.

The reviewed GitHub tree delta is **46 additions, 32 modifications, 32 removals**:

| Group | Disposition |
| --- | --- |
| Bounded-v1 CLI, tests, CI and recovery contract | Add the recorded recovery implementation and validation files. |
| Launchers, documentation, ignore rules, bridge wrappers and templates | Use the reviewed recovery versions; hooks remain opt-in. |
| 24 checkout-local `.cursor/` files | Omit the installed rules/skills/hooks from distribution; retain source assets under `cursor/` and historical Git objects. |
| Eight legacy `.overseer/` files | Omit live local/governance bindings; all eight old blobs are byte-identical to their recorded archives under `docs/archive/v1/`. |
| Staging-only bridge sentinel and four generated Tauri schemas | Omit the five already dispositioned local/generated files, retaining immutable Muse history. |

Thus the native staging comparison is **846 → 855 files**, with 46 additions,
32 modifications and 37 removals. The GitHub comparison is **841 → 855 files**.
Removals apply to the proposed published snapshot, not original working edits or
historical objects. This comparison does not reopen unchanged closed reviews.

## Implemented bounded local reconciliation

`mirror reconcile` is explicit and offline. Ordinary `prepare` retains the
`mirror_legacy_destination_requires_reconciliation` refusal and its original
fresh-target behavior. Reconciliation requires an absent physical target, a
SHA-256-bound complete Git v2 bundle with exactly the approved destination mirror
and base refs, both exact commit IDs, and an exhaustive before/after hash/mode delta.
The histories must be related and their approved trees identical. Different trees,
prerequisites, extra refs or unrelated objects require another reviewed decision.

The engine unpacks into a temporary bare repository, runs strict object checks,
verifies reachability and the exact delta, and installs only its owned target.
No configuration, hooks, alternates or working files are imported. The initial
projection has **first parent** the approved legacy mirror and **second parent**
the approved GitHub base. Its tree comes entirely from the checked Muse source.
Both histories survive, main is an ancestor, and a later normal mirror push can
fast-forward. No automatic merge of legacy content is performed.

The complete reconciliation binding stays in the ownership marker and normal
correspondence record. Exact trailers, ordered parents, tree, source identity,
revision, executable policy and plan digest are checked on retries. Later source
exports retain this binding and use the verified prior mirror as their sole parent.
Later plans can explicitly pin a newly reviewed live base with
`destination.expected_base` while preserving the original parent binding.
Import/ref/record interruptions remain retryable without adopting foreign targets
or forging ownership. The [runbook](../../MUSE-BRIDGE-WORKFLOW.md) gives the schema,
limits and record refresh procedure for older ordinary projections.

Delivery rechecks both live GitHub heads, source authority and local bytes/modes
before writing and before PR work. A moved base or mirror stops delivery, including
on retry. This cannot make the services atomic; partial outcomes stay visible.
Git reads/pushes use a per-command credential helper restricted to the exact
GitHub HTTPS path and named physical `gh`, with redirects disabled. Tokens remain
in the helper/Git pipes, never URLs, argv, persistent config or reports; store and
erase do nothing. Fake-credential protocol tests do not prove live push rights.

Disposable fixtures cover the one-main/six-mirror divergent history shape, both
ancestor relationships, the 110-path starting delta, modes/exclusions, wrong
heads/bundles/dispositions, base drift, foreign/executable target metadata,
interrupted preparation/delivery and no-change retry. The retained real histories
and original candidate also receive a disposable exact projection. Required local
Git-only and combined Muse results are recorded in the validation section below.
Unchanged closed architecture/build reviews were not repeated.

## Proposed remote operations for a later owner decision

These are concrete proposed operations, **not authorization or commands to run
in this local implementation action**. Use only the exact resulting identities
in the frozen candidate records, after
new explicit owner approval; substitute no moving branch or later edit.

| Stage | Exact destination and proposed effect | Required evidence/limit |
| --- | --- | --- |
| Publish source feature | Non-force native Muse push to public staging `aaronrene/overseer-kit`, branch `feat/overseer-v1-restoration-r3`, at the approved Muse revision. | Recheck absent/approved prior branch head and staging pin; preserve the local isolated feature. |
| Accept source main | After review, non-force fast-forward staging `main` from the approved `208d9d...` base to that same exact candidate, using the dedicated publication checkout. | Requires explicit approval to advance **shared staging main**. Candidate must descend from the checked base; no force, tag push, branch deletion, proposal merge or production fallback. |
| Verify authority | Read staging `/refs` and fetch/read the accepted immutable snapshot into the dedicated checkout; bind it explicitly for Muse authority. | Exact logical ID, accepted main revision, all paths/bytes/modes and exclusions must match; no original ref may move. |
| Reconcile and deliver | Use `mirror reconcile` to prepare the reviewed two-parent mirror commit in the new bare target; normal non-force push only to GitHub `aaronrene/overseer-kit:muse-mirror`. | Recheck both approved GitHub heads, plan digest, accepted Muse main and exact tree. Record the computed Git commit before delivery, then verify the remote head. |
| Open distribution PR | Create or reuse the exact open GitHub PR `muse-mirror` → `main`, in `aaronrene/overseer-kit`. | Separate permission for PR creation and any resulting hosted CI; record actual URL/head and results. Leave PR unmerged. |

Native rc5 source inspection identifies the Muse push transport as signed staging
requests for `/push/mpack-presign` and `/push/unpack-mpack`, with an object upload
to the returned storage URL. A future owner approval must include those required
uploads, restricted to the staging-provided destination and approved objects.
Use only the pinned recovery runtime, `force: false`, a named branch, no tag/all
branches options, no trust reset and no automatic hooks. Verify native command
scope in the dedicated checkout before any write. Rights/server acceptance remain
unvalidated until those specifically authorized operations return and read back
successfully. Refusals remain visible; do not broaden permissions to get past one.

Fast-forwarding the reviewed Muse candidate is the proposed acceptance method;
this avoids relying on an unverified proposal-merge strategy or the server's
branch-deletion default. It still requires explicit owner approval for main.
GitHub main merge, release/tag publication, consumers and production are separate
decisions after source acceptance and actual mirror delivery evidence.

## Validation and retained boundaries

Local results and final identities are recorded in
[the validation closeout](../validation/V1-RECOVERY.md#local-legacy-mirror-reconciliation--2026-10-09)
and `../RECOVERY-RUNS/20261009-mirror-reconciliation/`. The required matrix uses
Git-only Python 3.11.15 and 3.14.4 and combined Muse Python 3.14.4, with the exact
recovery package source digest checked by the supported driver. No new hosted
job, remote query or remote write is part of this implementation.
Final local results are **131 passed** on Git-only 3.11.15 (52.59s), **131 passed**
on Git-only 3.14.4 (61.28s), and **264 passed** on combined Muse 3.14.4 (360.10s),
all with zero failures/errors/skips. No supported failure remains unresolved.

[Hosted run 37948400522](https://github.com/aaronrene/overseer-kit/actions/runs/37948400522)
remains evidence only for `2d689a8398002ce667743ac7fefd12291b8973bf`: Git Python
3.11.17 **117 passed**, Git Python 3.14.8 **117 passed**, combined Muse Python
3.14.8 **225 passed**. It does not validate the new candidate. New feature pushes
and any resulting hosted jobs require explicit authorization for the resulting SHA.

The recovery wheel/source pins and repository Actions URL are unchanged. The
original rc5 archive remains unavailable; this wheel is not an upstream release.
Permanent Git-only operation and explicit Muse adoption remain intact. Original
refs/edits, isolated Muse main and trust/configuration, and held release
`06f988e5a078ede81c9dc664520833980a9a19a3` are preserved. Only the existing isolated
feature advances by a source-exact local commit. Its projection lives in a separate
disposable fixture; the proposed real delivery paths remain absent.

No MuseHub or GitHub write, main change, PR, tag/release, real mirror delivery,
consumer access, production trust reset, automatic hook or OCI operation occurred.
No complete-product claim is made. Read-only planning evidence remains in
`../RECOVERY-RUNS/20261009-muse-publication-plan/`; it is a retained observation,
not a fresh remote-state assertion. Canonical NEXT alone carries the remaining
owner decision; this document grants no remote permissions.
