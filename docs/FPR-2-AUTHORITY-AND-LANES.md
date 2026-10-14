# Authority, controlled mirrors and repository lanes

FPR-2 adds these local services to the unified `cli/ok`. This is focused
implementation, not complete-product certification or release authorization.

## Explicit authority

Use `init --vcs git` for Git, or `init --regime muse-only --muse-python
/absolute/venv/bin/python` for Muse. `muse+git-mirror` selects Muse authority and
optional Git distribution; fresh mirror mode also requires explicit
`--muse-staging-remote` and `--mirror-branch` settings. Mixed uninitialized checkouts require explicit
selection. Each checkout receives its own UUID; linked native checkouts retain
the native shared source identity and their own branch. Git-only never launches
Muse; Muse-only does not require a Git checkout. A configured unavailable native
runtime refuses without fallback.

Muse uses the separate pinned 0.2.1rc5 environment. Binding records the native
source ID, physical store and runtime source digest. Reads avoid native startup,
GC and stage migration. Dirty/shared-stage status is observational and does not
invalidate an otherwise current revision-bound task. Different external
`working_dir` arrangements remain preserved settings but require explicit pairing;
they are never silently selected as another writable repository.

`adopt` previews or applies an explicit authority change. Supply `--vcs`,
`--expect-config`, `--repo-id`, `--branch`, `--base-head`, `--lane` and `--model`;
Muse additionally needs `--muse-python` when creating its binding. `--dry-run`
reports the backup, tracked local bindings and changed paths. Existing tracked
bindings before Muse adoption require `--tracked-bindings preserve`, or separate
explicit owner untracking before retry. The service never untracks files. Git
adoption retains tracked config/launcher/NEXT without imposing Muse's policy.

Rollback uses `adopt --restore-config .overseer/local/config-before-DIGEST.yaml`
with expected current config and target context. It restores the exact saved
config bytes, including comments; additive ignore rules remain. This can restore
Git even if the formerly selected Muse runtime is unavailable. NEXT and living
documents are preserved and must be explicitly republished for the new authority.
Config is replaced last; partial per-file progress is reported and retryable.
No filesystem transaction or hostile same-user protection is claimed.

## One canonical file and multiple lanes

Declare lanes in schema-3 config `docs.lanes`, each owned by this repository's
UUID. `next --lane NAME` selects an entry. `next --all-lanes` or an unselected
multi-lane call shows labelled valid/missing/stale entries and requests explicit
selection before action. Bound Cursor event payloads accept an explicit `lane`
and use the same display service. Other lanes stay visible beside a selected
entry; no lane inherits freshness from another lane's work.

`next-write --lane NAME` retains the required repository, branch, model, action
and expected whole-file digest arguments. It updates one entry with atomic
whole-file CAS. Schema-1 Git and schema-2 authority documents remain readable;
the first multi-lane write uses schema 3 in the same `docs/NEXT.md`. Strict
frontmatter entries correspond exactly to uniquely delimited prompt bodies;
all prompt digests are checked, including unselected entries. Concurrent writers
must reread/reconcile after a stale digest refusal.

Git permits the exact single closing commit with pinned parent and committed
NEXT reads. In a collection, an unchanged lane does not gain that exception from
another lane's closing commit. Muse publication requires `--vcs muse --base-head
sha256:...` against the exact current native revision, after the work commit.
Every later native commit makes the entry stale. Git mirror commits never refresh
Muse NEXT. Runtime/config-only sync and migration preserve NEXT bytes.

For an explicitly accepted group, `next-write --batch-file FILE` takes a confined
JSON object `{"lanes": {"product": {"model": "GPT-6 Astra", "action_id": "TASK",
"action_kind": "implement", "prompt": "Accepted task.\n"}}}`. Supply the common
repository/branch, whole-file expected digest and Muse revision arguments as
applicable. One atomic write updates just the named entries. After authority
adoption, a collection with a different source requires `--reset-authority`;
that explicit operation replaces the incompatible collection, leaving omitted
configured lanes visibly missing. Repository identity cannot be reset this way.

## Controlled distribution

Prepare a repository-relative JSON plan with the exact native source ID/main
revision, supported staging Hub URL, destination repository/distribution branch,
base and expected heads, physical isolated target, and approved executable paths.
`mirror prepare|reconcile|verify --plan-file FILE --expect-plan SHA256` is offline.
Only a new dedicated bare target or its exactly owned continuation is eligible.
The source checkout/store/runtime cannot overlap it. Native object bytes,
working-file bytes, modes, exclusions, tree, trailers and parents are checked.
Local bindings, NEXT, migration backups, native metadata and secrets are excluded
from projection, while portable templates and CI dotfiles remain eligible.

Initial reconciliation requires a complete bounded SHA-1 v2 bundle with exactly
the two approved refs and an exact approved delta. Its initial commit has both
reviewed parents; subsequent snapshots continue with one parent. Base drift,
foreign target configuration/refs/hooks/alternates, dirty projection and ambiguous
correspondence refuse. Interrupted record writes recover only by validating the
exact commit correspondence.

`upgrade-regime --dry-run --plan-file FILE --expect-plan SHA256` reviews adding
controlled distribution. `--apply --expect-config SHA256` changes the regime and fills missing required mirror settings from the approved
plan, retaining existing settings and authority. It neither exports nor delivers. The old
`--live-bridge` route always refuses, including with `--yes`. Bridge wrappers call
bound `mirror`; they do not run native live export.

Actual delivery is a separate `mirror deliver` operation requiring an explicit
`--allow-network` and physical `--gh` executable. FPR-2 tests use fake transports
and credentials only. The retained live adapter is limited to public staging
MuseHub JSON refs, GitHub HTTPS, native source branch main and SHA-1 Git. It
re-observes authority/remote heads and verifies PR identity on retries. Its helper
scopes credentials to one repository path, resets inherited helpers, disables
redirects, ignores store/erase, and keeps tokens out of arguments/config/evidence.
No live delivery or provider compatibility has been validated by FPR-2.
