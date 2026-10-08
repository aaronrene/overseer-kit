# Explicit local adoption and rollback

Git/GitHub-only operation is a permanent choice. It needs neither Muse nor a
MuseHub account. `init` and `sync` do not convert a Git binding. MuseHub authority
with a GitHub mirror is an explicit per-repository choice; R1 implements the local
authority binding, while R2 mirror delivery remains pending.

The supported migration input is the bounded-v1 schema-1 Git config or a schema-2
Git/Muse config. Historical `overseer_config_version` governance configs, copied
bindings and relocated checkouts are refused. Preserve those inputs and arrange
an explicit reviewed conversion; the former `init --migrate` and governance-sync
commands are historical, not supported v1 commands.

## Prepare the source deliberately

Preserve the existing checkout, UUID, config and documents. Inventory committed,
staged, unstaged and untracked application work. Use native `muse bridge git-import`
against a reviewed committed Git baseline in an isolated disposable Muse checkout
first. Compare actual contents and exclusions. Do not import dirty working files,
execute bridge hooks, select a Hub destination implicitly, or mirror the real
project as a side effect of adoption. R1's fixtures test native isolated import;
`ok adopt` itself performs no import, commit, checkout, fetch, push or mirror.

When preserving an existing physical checkout's identity, prepare its Muse history
separately and deliberately before binding it. A separate clone or linked worktree
is a new physical checkout: initialize it with a new Overseer UUID even when it
shares the same logical Muse repository ID. R3 handles this project's isolated
source reconciliation; do not attach the recovery worktree to original Muse refs.

Muse mode supports the code domain in Muse `0.2.1rc5`, using a separate conventional
Python >=3.14 venv. Pass its absolute `bin/python` path. Standard Python symlinks
inside that venv are supported. The kit does not borrow its dependencies, discover
Muse on PATH or call the native CLI for status/NEXT. Its small read-only reader
uses pinned object-reading APIs and resolves registered linked-worktree HEAD
explicitly. Missing/corrupt objects, malformed responses, a changed Muse package,
unregistered links and ambiguous state cause refusal, without Git fallback.

## Review and apply the binding

Read `status --json` for the current UUID and config digest. Inspect the intended
Muse branch/revision locally (for linked Muse worktrees use that registered
worktree's branch, not native CLI main-store discovery). Then run:

```sh
ok -C /absolute/project adopt --vcs muse \
  --muse-python /absolute/muse-venv/bin/python \
  --repo-id EXISTING-UUID --lane product --model 'GPT-6 Astra' \
  --branch TARGET-MUSE-BRANCH --base-head TARGET-MUSE-REVISION \
  --expect-config CURRENT-CONFIG-SHA256 --dry-run --json
```

Use `unborn` only for an empty branch. The dry-run reports changed paths, tracked
local files, the exact backup path, target revision and candidate config digest.
It writes nothing. Apply the reviewed change by repeating the command without
`--dry-run`. To select Git explicitly or upgrade an old schema-1 Git binding, use
`--vcs git`, its Git branch/HEAD, and omit `--muse-python`. No Muse installation or
account is consulted in Git mode. `--expect-config` protects against stale config
writes; repository UUID, physical root, lane/model and target branch/revision
must also agree. Cooperating mutations share a short local directory lock.

The new config retains the UUID, name, physical root and context. Existing NEXT,
ROADMAP, HANDOVER, application edits and hooks remain byte-identical. Config is
published last, through the confined atomic writer. No hooks are installed by
adoption. After authority changes, the preserved old NEXT is intentionally invalid:
publish reviewed prose with `next-write`, the previous NEXT digest, and the new
authority's branch/revision. Muse writes require `--vcs muse --base-head REVISION`.
This is an explicit handoff, not automatic reuse of an imported task.

## Local-file exclusion policy

Fresh initialization and explicit adoption add these root-relative exclusions to
both `.gitignore` and `.museignore`:

- `.overseer/config.yaml`, `.overseer/bin/`, `.overseer/local/`;
- `docs/NEXT.md` and checkout-local `.cursor/` editor assets;
- the other VCS's administration (`.muse/` in Git; `.git/` in Muse).

Use `.overseer/local/` for prompt inputs and config backups. Portable sources in
`templates/`, `cursor/`, ROADMAP and HANDOVER remain versionable. Existing ignore
rules, ordering and comments are retained. Muse rules are appended after global
and each existing domain's rules so negations cannot re-include the bindings.
An explicit `force_track` of a local binding is refused. Unsupported TOML layouts
are refused without rewriting them; conventional table/array syntax is supported.

Ignore rules do not remove existing tracked content. Adoption reports Git index
and selected Muse snapshot/stage paths and refuses apply while local bindings
remain tracked. Review and explicitly remove them from the relevant tracking
state, retaining local files and history, before retrying. In Git mode Muse
tracking is not inspected: installing Muse cannot be a prerequisite for staying
Git-only. A later Muse adoption performs that additional check. R2 must separately
enforce exclusions on the projected export and any existing mirror; ignore files
alone are not proof that a distribution snapshot is safe.

## Roll back without losing later work

Each adoption preserves the exact previous config bytes under the reported
`.overseer/local/config-before-<digest>.yaml` path. Restore them explicitly:

```sh
ok -C /absolute/project adopt \
  --restore-config .overseer/local/config-before-OLD-DIGEST.yaml \
  --expect-config CURRENT-CONFIG-SHA256 \
  --repo-id EXISTING-UUID --lane product --model 'GPT-6 Astra' \
  --branch RESTORED-BACKEND-BRANCH --base-head RESTORED-BACKEND-REVISION \
  --dry-run --json
```

Repeat without `--dry-run` to apply. Restoring Git works even if the Muse runtime
has disappeared. The backup must belong to this checkout and context. Application
files, documents and the current NEXT are preserved, including edits made since
adoption. Publish a new NEXT for the restored backend; old Muse NEXT cannot run in
Git mode. Restored runtime pins remain exact: if kit source changed meanwhile,
review and explicitly `sync` before ordinary use. Relocating between kit installations
is outside this config rollback; combined installation rollback remains R3 work.

Additive exclusions remain on rollback, preserving any later user edits and keeping
backups private. Rollback never resets VCS refs, removes imported history, restores
stale application files, or force-pushes. If a file write fails before config
replacement, the old binding remains; added exclusions and backup are safe to keep
and retry. A directory-fsync failure after replacement can report failure with the
complete new config already present: inspect its digest before retrying. This is
per-file atomicity, not an automatic transaction/recovery subsystem.
