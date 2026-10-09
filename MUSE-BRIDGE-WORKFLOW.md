# Controlled Muse → GitHub mirror

R2 implements local preparation and delivery retry; R3 validates isolated source
reconciliation and combined local operation. The complete product and held release
candidate remain unfinished. A reproducible, explicitly local rc5 recovery
distribution is hosted with an [exact contract](tools/ci/MUSE-RC5-RECOVERY.md);
the owner separately authorized dependency hosting and recovery-feature CI. Actual
hosted results are in the [execution record](docs/validation/V1-RECOVERY.md#hosted-ci-execution--2026-10-09).
The original upstream archive remains unavailable. No real-project mirror or remote
write is authorized by this runbook. Git-only operation remains a permanent
choice; mirroring requires explicit R1 Muse adoption.

The [publication decision](docs/decisions/V1-MUSE-PUBLICATION.md) records the
2026-10-09 read checks, exact legacy delta and local reconciliation results.
`mirror reconcile` now prepares an explicitly reviewed two-parent initial commit.
Ordinary `prepare` still refuses an existing remote branch on first preparation.
Disposable projections are fixture evidence; real delivery needs new owner approval.

The current workflow replaces the old deploy script's implicit export/push. The
script and its template now delegate to the repository-bound `ok mirror` command.
There is no default source, target, remote, watch mode, automatic hook or push.

## Reviewed input

Use an initialized Muse-authoritative source checkout, with main materialized at
the approved revision and a separate, **absent physical target path** outside the
source, its shared Muse store, and the kit installation. Its parent must exist.
R2 creates a dedicated bare Git repository. It never exports onto a development
worktree, clones a remote, adopts an existing Git directory, or removes foreign
content. Even an existing empty directory is refused. Subsequent operations may
reuse only that exact owned target and source/destination pair.

Save reviewed JSON under `.overseer/local/approved-mirror.json`. Required schema:

```json
{
  "schema": 1,
  "source": {
    "repo_id": "sha256:<64 lowercase hex digits>",
    "branch": "main",
    "revision": "sha256:<approved immutable revision>",
    "hub_url": "https://staging.musehub.ai/OWNER/REPOSITORY"
  },
  "destination": {
    "url": "https://github.com/OWNER/REPOSITORY.git",
    "repository": "OWNER/REPOSITORY",
    "branch": "muse-mirror",
    "base": "main",
    "expected_head": "absent"
  },
  "target": "/physical/isolated/mirror.git",
  "expected_target": "absent",
  "executables": ["path/to/approved-executable"]
}
```

For this kit's rc5 source preparation, explicitly stage new dot-directory files
such as `.github/workflows/supported-v1.yml`: recursive `muse code add .` can omit
them. Compare the actual native snapshot and mirror against the reviewed source
manifest. A successful command alone does not prove dotfile inclusion.

The executable list must be sorted, unique, and contain exactly the projected
executable paths. The source logical ID must match the existing R1 binding. The
checkout UUID/root, kit runtime and separate Muse runtime are also checked. The
plan's raw SHA-256 is a required command argument; an edited plan needs fresh
review and a new digest. Source main and the full immutable revision must agree.
A supplied approved revision is **not** a live observation of Hub acceptance.

Ordinary first preparation requires both heads to be `absent`. For a later revision, set
`expected_target` to the current verified local mirror commit and `expected_head`
to the reviewed destination branch head (40 lowercase hex digits). Keep the same
plan and digest when retrying incomplete delivery. Changing the destination pair
or migrating an old mirror requires explicit reconciliation. Unowned targets are
always refused, including historical extra files/local bindings.

## Explicit local legacy reconciliation

This bounded operation supports related Git histories whose approved heads have
identical trees, as observed for this kit. It does not merge old content. Obtain a
complete SHA-1 v2 Git bundle from a separate inspection repository, containing
exactly `refs/heads/muse-mirror` and `refs/heads/main` (or the plan's named branches).
Only those approved histories may be included; prerequisites, extra refs/objects,
unrelated heads, different base trees and unsafe bundle paths are refused. Creating
a bundle from retained local objects is offline; any new remote fetch needs its
own authority. The physical bundle must be a singly linked, non-executable regular
file, at most 128 MiB compressed; Git subprocesses have a 30-second deadline.

Keep the ordinary plan fields. Set `expected_target` to `absent` and destination
`expected_head` to the approved legacy mirror SHA, and add:

```json
{
  "reconciliation": {
    "bundle": "/physical/reviewed-history.bundle",
    "bundle_sha256": "<raw SHA-256 of the complete bundle>",
    "mirror_head": "<40-character approved legacy mirror SHA>",
    "base_head": "<40-character approved GitHub base SHA>",
    "delta": {
      "example/removed-local-file": {
        "before": "<raw SHA-256 of old bytes>",
        "after": null,
        "mode_before": "100644",
        "mode_after": null
      }
    }
  }
}
```

`delta` must enumerate **every** changed path, with raw before/after SHA-256 and
`100644`/`100755` modes; absence is JSON null. The engine computes and compares the
complete delta against the source projection. Missing or unexplained deletions,
mode changes and extra dispositions fail. The plan's raw digest covers all of it.

Run `mirror reconcile` with the usual `--plan-file` and `--expect-plan` arguments.
The engine validates and unpacks the bundle into a temporary bare repository using
strict Git object checking, verifies reachability and the exact disposition, then
installs its owned target at the absent physical path. It imports no configuration,
hooks, remotes, alternates, working files or foreign refs. The initial source-exact
commit has the legacy mirror as **first parent** and GitHub base as **second parent**.
Both histories become ancestors without force or an automatic content merge.

Retry `reconcile` with the same plan; `verify` remains read-only. Interrupted import
does not install a partial target. Interrupted ref/record writes use the normal
verified retry path. The ownership marker and correspondence record retain the
entire reconciliation binding. Later exports keep that reconciliation block
unchanged, advance the ordinary expected heads/source revision, and use `prepare`;
their sole parent is the verified prior mirror commit. The stored origin delta
describes the initial reconciliation, not a later source change. An old record
without the new tree/parent fields must first run `prepare` with its exact original
plan to refresh correspondence before advancing; `verify` does not write records.

Delivery rechecks both named GitHub heads, including on retries and before PR work.
The initial base must match `reconciliation.base_head`. A later reviewed source
plan may add `destination.expected_base` with the exact newly approved base SHA;
otherwise the original base remains required. This explicit observation pin is
covered by the new plan digest and does not change the immutable origin binding.
A moved base still refuses until that new plan is reviewed; no automatic rebinding
or extra parent is introduced.

## Prepare and verify locally

From the initialized source checkout, with the actual approved digest:

```sh
./.overseer/bin/ok mirror prepare \
  --plan-file .overseer/local/approved-mirror.json --expect-plan PLAN_SHA256
./.overseer/bin/ok mirror verify \
  --plan-file .overseer/local/approved-mirror.json --expect-plan PLAN_SHA256
```

`./scripts/muse-bridge-deploy.sh prepare ...` is an equivalent bound wrapper when
that script is installed. Old positional commit-message invocation fails. `verify`
is read-only, performs the real checks, and requires an already prepared commit;
it is not the native exporter's unchecked dry-run.

Preparation reads pinned Muse objects through the R1 read-only APIs and validates
all blobs, including excluded blobs. It does not invoke native `git-export`: that
version mutates source bridge files, runs bridge hooks, can skip missing objects,
and infers modes from shebangs. Git plumbing writes the exact projected tree with
no checkout, index, filters or inherited hooks. Each committed blob, mode and path
is compared with the approved source before the target ref is updated.

Projection excludes R1 config/launcher/local backups and inputs, canonical NEXT,
checkout-local `.cursor/`, all Git/Muse administration, `.env` and `.env.*`, and the
old local bridge sentinel. Actual excluded snapshot paths appear in the report;
ignore rules alone are not evidence. Templates and living summaries remain.
An old snapshot may contain local bindings; projection omits them without changing
Muse history. Normal adoption still refuses tracked local bindings under R1.

Supported files are regular, singly linked files. Working bytes must match the
snapshot, the shared stage must be empty, and source revision/config are rechecked.
Untracked source files are never copied. Source executable bits must agree with
the explicit list; Git modes are normalized to `100644`/`100755`. Read/write
permission differences such as Muse's generated `0600` become `100644`. Symlinks,
hardlinks and special permission bits are refused. A shebang is not mode authority.
Empty-directory metadata is reported and omitted because Git does not represent it.
The local projection limit is 32 MiB of blob bytes, with a 48 MiB helper-output cap
and 30-second helper deadline. These are explicit bounds, not full filesystem or
arbitrary Muse-domain fidelity.

Source bridge-hook configuration causes refusal and is preserved. Targets must
have the exact engine-created Git config and no hooks or foreign entries. Global
and environment Git configuration is isolated, and hooks are disabled on every
Git command. Nothing installs or activates editor/Muse/Git hooks.

## Separately authorized delivery and retry

Only after approving actual payload and named destinations, invoke `mirror deliver`
with the same plan arguments and an explicit physical `--gh /path/to/gh` executable.
No delivery was run against a real remote during R2. Preparation and verification
never contact remotes. Ordinary local `status`/`next` remain offline.

Git reads and pushes receive an ephemeral credential helper restricted to the
exact approved GitHub HTTPS repository path. The helper invokes that physical
`gh auth token --hostname github.com`, keeps the returned token in memory, and
answers only Git's matching credential request. Store/erase are no-ops. Helpers
are reset per command, HTTP redirects are disabled, and other Git transport
protocols are refused. No credential enters a URL, persistent target config,
record or report. Fixture tokens validate this wiring; actual authentication and
write acceptance still need separately authorized delivery evidence.

Delivery observes the exact public staging repository's JSON `/refs` response and
requires its code-domain repository ID and main revision to match approval. It
refuses unknown, moved or unpublished sources, redirects, unsupported hosts and
malformed responses. Authenticated/private MuseHub and production trust are outside
this adapter; there is no login, fingerprint reset or host fallback. The public
staging read protocol was verified on 2026-10-09 using this adapter. Write rights,
native source publication and authenticated Git delivery remain unvalidated;
fixture evidence and successful signed reads are not remote write-acceptance evidence.

It compares the explicit Git URL/branch head independently of whether export made
a new commit, rechecks source/target/remote immediately before writing, uses a
normal non-force push of the exact commit to the distribution branch, and reads
back the head. A lost push response is resolved by readback. A stale remote stops
for reconciliation; there is no force push or direct main publication. Git's push
negotiation protects the ref update; these checks are not a cross-service atomic
transaction and cannot freeze MuseHub/GitHub while an operation runs.

PR list/create/readback always specify the GitHub repository, head/base branches
and target cwd. The PR must be open, from that repository, and at the exact mirror
commit. Only an exact empty PR-list response authorizes creation; malformed
observations and invalid URLs refuse before any create attempt. Failure remains visible and retryable. Authentication/network/PR failures
never erase a successful export or verified push. Retry first observes current
state, skips only verified completed stages, and retries missing push/PR work.

Reports separate `export`, `authority`, `push`, and `pr`, with source checkout UUID,
physical roots, revisions, destination repository/branches, observed remote head,
and PR URL when verified. An `ok` preparation result means local preparation only;
its push/PR remain `not_attempted` and Hub remains unchecked offline.

One ordinary source-directory lock and target-parent lock serialize operators.
A single `.overseer/local/git-bridge.json` correspondence record binds this source
to one target/pair. Commit trailers bind source revision and exact plan digest.
No-change retry retains the Git SHA and record bytes. An interrupted record write
can recover from a verified commit with the exact parent/tree/trailers. A new source
revision with the same projection gets a correspondence commit with no file delta.
Interrupted preparation can leave unreachable local objects, but never publishes
an unchecked tree; ordinary rerun can finish. There is no new ledger or daemon.

The [validation record](docs/validation/V1-RECOVERY.md#r2-controlled-mirror-preparation-and-retry--2026-10-08)
contains actual local results and remaining R3 work.
