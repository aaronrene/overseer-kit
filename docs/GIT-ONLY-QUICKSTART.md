# Git-only quickstart

Git-only is a permanent supported mode. No Muse package, MuseHub account, login
or later migration is required. Use the [published rc.1 guide](https://github.com/aaronrene/overseer-kit/releases/download/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md)
for checksum-verified source installation, fixed-path update and rollback.
The tag/manifest identify rc.1; `ok --version` still reports `1.0.0`.

Use Git and a tested Python 3.11 or 3.14 environment with the kit's own conventional
`.venv`. Hosted evidence is Linux; local evidence is macOS arm64. The source archive
must be extracted at the physical kit path you intend to retain. Do not install
the historical packaged/editable or desktop product.

## Initialize an authorized Git checkout

Start with an existing unmanaged Git checkout whose files you are authorized to
manage. Review its staged, unstaged and untracked files first. The commands below
are examples for that checkout, not permission to change another repository.

```sh
KIT_ROOT=/absolute/fixed/path/to/overseer-kit
PROJECT_ROOT=/absolute/path/to/authorized-project
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" init --vcs git \
  --repo-name PROJECT-NAME --lane product --model 'GPT-6 Astra'
"$PROJECT_ROOT/.overseer/bin/ok" status --json
"$PROJECT_ROOT/.overseer/bin/ok" next
```

Initialization preserves existing ROADMAP/HANDOVER text. A tracked local binding,
foreign launcher or incompatible legacy config requires [explicit migration](MIGRATE-EXISTING-REPO.md),
not an overwrite. For an already initialized repository bound to the same kit path,
use the guide's update/sync procedure. Never copy another checkout's UUID, config,
launcher or NEXT. Do not add `--hooks`; automatic hooks remain off by default.

## Read and publish one handoff

`status` and `next` are local and read-only. NEXT validates and prints a task;
it does not execute that task. Put reviewed prompt text in a regular UTF-8 file
under the target repository, for example `.overseer/local/task.txt`. Read the
actual UUID, branch, revision and `next_sha256` from `status --json`, then use them:

```sh
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" next-write \
  --repo-id UUID-FROM-STATUS --branch BRANCH-FROM-STATUS \
  --lane product --model 'GPT-6 Astra' \
  --action-id REVIEWED-ACTION --action-kind plan \
  --base-head REVISION-FROM-STATUS --expect-next NEXT-SHA256-FROM-STATUS \
  --prompt-file .overseer/local/task.txt
"$PROJECT_ROOT/.overseer/bin/ok" next
```

Only `next-write` publishes NEXT; keep ROADMAP and HANDOVER as summaries.
Action kinds are `plan`, `implement`, `review`, `maintain`, and `stop`.
No command here pushes, merges, deploys, updates another repository, or adopts Muse.

## Explicit kit updates

Follow the guide to preserve the previous source/dependencies and replace only
reviewed kit files at the same physical path while commands are stopped. A source
change can cause `runtime_changed` until explicit sync:

```sh
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" sync --dry-run --json
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" sync --json
"$PROJECT_ROOT/.overseer/bin/ok" status --json
"$PROJECT_ROOT/.overseer/bin/ok" next
```

Review the preview before apply. Sync preserves identity, authority, application
files, ROADMAP, HANDOVER and NEXT; it does not make stale task prose current.
Use `next-write` explicitly when the authoritative context changes. Rollback
restores your reviewed prior source/dependencies at the same path, then syncs.

The bounded public commands are `status`, `init`, `sync`, `adopt`, `mirror`,
`next` and `next-write`. Historical `governance-sync`, `review` and
`status --check-footprint` instructions do not apply to this CLI.
Muse adoption remains an optional, explicit choice with config rollback; see
[the guide](releases/v1.0.0-rc.1/INSTALL-AND-ROLLBACK.md).
