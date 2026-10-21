# Reviewed Muse runtime compatibility

This local candidate adds Muse 0.2.1rc11 to the read-only reader. It retains
0.2.1rc5 compatibility and refuses all other versions or source digests.
It does not upgrade Muse, migrate its store, run its native CLI during reads,
or silently change an existing binding.

| Version | SHA-256 of the sorted package Python sources |
| --- | --- |
| 0.2.1rc5 | `7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92` |
| 0.2.1rc11 | `c68f34f8a7b8a645e9ef433fcd34477591819df42944e856556c2bb43dd037fe` |

The digest concatenates each sorted package-relative `*.py` filename, NUL,
file bytes, NUL. Both the child reader and parent protocol validator require
an exact reviewed version/digest pair. The repository additionally binds the
exact Python path, version, digest, source ID and store. A shared environment
upgrade therefore still refuses ordinary bound reads until explicit rebinding.

## Installed-source review, 2026-10-20

Reviewed the installed package at
`/Users/aaronrenecarvajal/.local/share/muse/venv/lib/python3.14/site-packages/muse`.
Every Muse API imported by `cli/v1_muse_reader.py` is listed below. This is an
implementation compatibility check by the fixing agent, not independent
acceptance or a general Muse audit.

| Imported API | Installed source and behavior checked |
| --- | --- |
| `read_commit` | `core/commits.py`: reads typed JSON object bytes, constructs `CommitRecord`, verifies its content hash, returns a record or `None`. Its `snapshot_id` remains the snapshot key. No repair or write. |
| `read_snapshot` | `core/snapshots.py`: reads typed JSON bytes, constructs `SnapshotRecord`, verifies manifest/directory identity, returns a record or `None`. `manifest` and `directories` retain their shapes. No repair or write. |
| `validate_branch_name` | `core/validation.py`: validates a string against branch-name restrictions and returns it or raises. No I/O. |
| `resolve_patterns` | `core/ignore.py`: concatenates global and selected-domain pattern lists in order. No I/O. |
| `is_ignored` | `core/ignore.py`: delegates to `check_path_with_pattern` and `_matches`; ordered glob rules and negation, last match wins. No I/O. |
| `_BUILTIN_SECRET_PATTERNS` | `core/snapshot.py`: static list of excluded secret-shaped filenames. Reader retains its existing exclusion behavior. |
| `hash_file` | `core/types.py`: stats and streams bytes read-only; hashes `blob <size>\0<content>` and returns a prefixed SHA-256 ID. |
| `_ALWAYS_IGNORE_DIRS` | `plugins/code/plugin.py`: static directory set including VCS stores, dependency/build/cache directories. The reader walks independently without loading or writing Muse's stat cache. |

Also checked the callees used for object paths and verification:
`commit_path`, `snapshot_path`, `object_path`, `objects_dir`, the
`core/paths.py` helpers, `_shard_prefix_len` / `_cached_shard_prefix_len`,
`cli/config.py:get_limit` / `_config_path` / `_load_config`, record
deserializers, hash verification, and commit/snapshot identity calculations.
The shard limit path reads repository TOML and uses only a process-local cache.
The imported modules work under the reader's existing audit hook, which refuses
writes, filesystem mutations, network connections and child processes.

The hand-read storage contract also remains compatible: `.muse/repo.json`,
symbolic HEAD and branch refs, linked-worktree `musestore:` pointers plus
`worktrees/<name>.json` / `<name>.HEAD`, and code stage JSON with `entries`.
`plugins/code/stage.py:read_stage` still deletes obsolete binary stage files,
so the reader deliberately does not call it. Native CLI discovery/GC, stage
migration and stat-cache APIs remain excluded. Unknown or corrupt state refuses.

## Explicit same-source rebinding

Use the new candidate's `cli/ok`, because the old installed launcher is still
bound to its old Kit/runtime. Supply the current expected config digest, UUID,
branch/head, lane/model, and an explicit Muse Python:

```sh
NEW_KIT/cli/ok -C REPOSITORY adopt --rebind-muse-runtime \
  --muse-python /absolute/reviewed/venv/bin/python3.14 \
  --repo-id UUID --branch BRANCH --base-head MUSE_HEAD \
  --lane LANE --model 'SAVED MODEL' --expect-config CONFIG_SHA256 \
  --tracked-bindings preserve --dry-run --json
```

Review the full `plan`, including old/new Muse and Kit bindings, complete
normalized config, changed asset bytes/digests, protected inputs and tracked
bindings. To apply, repeat the same arguments without `--dry-run` and add
`--expect-rebind REBIND_SHA256` from that preview. A changed plan refuses.
The tracked-binding choice preserves tracking; it never stages or untracks.

This narrow operation requires an existing schema-3 Muse binding and preserves
source identity, store, authority, regime, remotes, branches, UUID, lanes, model,
and every other setting. It can move the Kit binding to the new runtime copy.
Only the exact generated old launcher can be replaced. The version lock changes
only the existing launcher's hash and aggregate footprint digest. Ignore files,
hooks, policies, ledgers, living documents and NEXT remain byte-identical.

Original config, launcher and lock are copied under the reported
`.overseer/local/rebind-<original-config-digest>/` backup. Writes use the shared
directory lock, compare-and-swap checks and config-last ordering, with runtime,
source, revision and protected-input rechecks before each replacement. This is
per-file atomicity, not a multi-file transaction. If an apply is interrupted after its first write, it refuses with
`partial_asset_update: restore .overseer/bin/ok, .overseer/version.lock, then
.overseer/config.yaml from each copy present in <backup>/, then preview again;
reason: <reason>; completed: <paths>`. Explicit `sync` cannot repair this state.
If `reason` is `stale_write: <path>` or `context_changed_before_rebind`, another
writer changed a file during the apply. Before copying, save each of the three live
files whose SHA-256 matches neither the preview's `assets[].before.sha256` nor
`assets[].after`, because the restore overwrites it.
Copy each of those three backup files that exists over its live path, in that
order, and set each restored live path's mode to its preview `assets[].before.mode`.
Then run the same `--dry-run` again and apply its new `--expect-rebind` digest. Live files are replaced only after all three copies exist, so a missing
copy means its live file was not changed. A restored config whose Muse runtime
differs from the installed venv still refuses ordinary reads until the rebind
completes; restoration does not downgrade Muse.

Rebinding neither accepts a prompt nor publishes NEXT. Operator acceptance and
`next-write` with the exact prior NEXT digest remain separate steps.

## Validation across reviewed runtimes

The Muse tests take the current runtime from the probed `--muse-python` venv and
use the single other `MUSE_RUNTIMES` entry as the stale binding.
`tools/ci/supported_v1.py` accepts only an exact (version, digest) pair from
`cli/v1_revision.py:MUSE_RUNTIMES` and refuses before running pytest otherwise.
The prepared hosted `muse` job installs only the reviewed rc5 recovery wheel. There
is no hosted rc11 job: no reviewed rc11 distribution artifact exists, and hosted
execution is not authorized. Run the rc11 matrix locally:

    .venv/bin/python tools/ci/supported_v1.py \
      --muse-python /absolute/rc11-venv/bin/python3.14 \
      --junitxml /absolute/scratch/combined.xml

