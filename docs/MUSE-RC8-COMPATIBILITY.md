# Muse 0.2.3rc8 compatibility candidate

This local feature candidate extends the exact Muse source-pair contract to
`0.2.3rc8` / `a22e489f0f62a1cbfb1ab545646e9bdc89d691bf354b4016468b9b820104598b`.
Independent review and maintainer acceptance are pending. Installation is a
separate, explicitly scoped operation for each consumer.

Accepted main refused this runtime before repository reads. Removing that gate
alone would leave imports of `_BUILTIN_SECRET_PATTERNS` and `_ALWAYS_IGNORE_DIRS`
broken. The rc8 release also moved linked HEAD and stage state into a per-checkout
directory. The candidate handles those changes while retaining the previously
reviewed rc5/rc11/rc13 paths and rejecting every other version/digest pair.
The 436 Python source hashes are in
[`muse-rc8-source-files.json`](../tools/ci/muse-rc8-source-files.json).

## Reader behavior

The rc8 path uses the pure `muse.core.exclusion` policy. It never calls the native
filesystem walker or stat cache, whose native implementation writes cache state.
The existing audit hook continues to reject writes, network and child processes.
Secret negation cannot override the built-in blocklist; `.env.example` follows the
native safe-template policy. Mirror projection keeps its stricter existing public
export exclusions, including `.env.*` and local binding paths.

Ordinary repositories use `.muse/HEAD` and `.muse/code/stage.json`. An rc8 linked
checkout uses `.muse/worktrees/<name>/HEAD` and its own `code/stage.json`. A missing
new-format linked HEAD refuses with `muse_worktree_repair_required`; the reader
never borrows the primary HEAD/stage or performs native migration. Older reviewed
runtimes retain their old registered HEAD and shared-stage behavior.

Identity, HEAD, ref, stage, linked pointer/registration and relevant ignore bytes
are rechecked before returning. Interrupted checkout/merge sentinels refuse.
These checks detect ordinary concurrent changes; they do not promise an atomic
filesystem snapshot against a hostile same-user writer. Native commit integrity
and the N-parent regression use the complete parent list. Reading a tip and its
snapshot is not a full-history export, and Muse's snapshot does not encode
historical POSIX modes.

## First binding, migration and rollback

The existing legacy migration path already supports first binding with an
explicit Muse interpreter and reviewed plan. Qualification uses a synthetic
unbound legacy configuration, large living documents and custom assets. Preview
without a binding remains inapplicable; an explicit binding and tracked-binding
preservation choice permit the supported migration. No real consumer settings
are needed to test this behavior.

Existing bindings retain their identity, settings, NEXT, locks and history.
Changing an already bound runtime uses the existing same-source rebind plan and
its digest/identity checks. A source fix does not update any global launcher or
consumer. Restoring an old rc13 binding against shared rc8 restores a safe refusal;
it is not a working rollback. Working rollback requires a tested matching pair.

A valid synthetic NEXT is published only through the bound writer, with explicit
repository/revision/context and the expected previous digest. Missing NEXT,
wrong context and stale digests refuse. Fixture prompts authorize no real task.

## Repeatable qualification

Use a new isolated source checkout, its conventional `.venv` with
`requirements-v1-dev.txt`, and a separate frozen Muse environment. Keep the full
interpreter/dependency inventory and byte hashes with the private receipt. The
source digest is not a promise about an arbitrary future dependency environment.
Verify every store, pointer, runtime and output path is disposable; no service is
required. The implementation run additionally denied original-source reads,
network access and writes outside its disposable audit boundary at the OS level.

```sh
scripts/check-muse-compatibility.sh /absolute/frozen-muse/bin/python3.14 /absolute/new-results
```

The output directory must not already exist. The command checks the exact
version/source pair, then runs the ordinary adapter/unit tests, full-dependency
Git-only standalone successor, native reader, binding/rebind, NEXT and offline
mirror regressions. `--collect-only` validates the selection without claiming
execution. The existing broad `tools/ci/supported_v1.py` remains available for
broader product assessment.

The retained YAML-only standalone test is incomplete: full-product status imports
Ed25519 verification and requires `cryptography` (plus its pinned dependencies).
It fails with `ModuleNotFoundError: cryptography`. Its existing
`tests/fpr4/test_standalone_dependencies.py` successor provisions all four exact
pins and tests a fresh interpreter with neither Muse nor ambient site-packages.
The compatibility command selects that successor explicitly; it does not silently
call the historical test a pass. It also explicitly deselects the preserved
`test_add_change_delete_and_no_content_source_commit`: that fixture leaves hidden
portable files unstaged, so its purported no-content commit changes the native
snapshot. The selected full-footprint successor checks equal native snapshots
and Git trees, delta handling and retries. Both replacements were independently
assessed in [FPR-5](reviews/FPR-5-REVIEW.md#historical-failures-and-explicit-replacements).
Raw historical failures and interrupted runs remain distinct in the private
qualification receipt.

## CI proposal for review

Use the compatibility command as a dedicated application check after an immutable
Muse artifact and its dependency inputs have a reviewed retrieval mechanism.
Record exact commit/tree, runtime hashes, JUnit results and bound-fixture evidence.
A missing artifact must fail rather than install a moving Muse release. Continue
to run a Git-only job without Muse. Hosting previews do not establish application
acceptance. Do not require an unconfigured artifact-dependent check, change remote
branch protection, trigger hosted jobs or publish artifacts as part of this local
candidate. Existing hosted workflow policy is unchanged.
