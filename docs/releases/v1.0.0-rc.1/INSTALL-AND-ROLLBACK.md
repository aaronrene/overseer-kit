# Install and roll back Overseer Kit v1.0.0-rc.1

These are operator instructions for the exact accepted source commit
`293e79eb96dc9b94b76fa28ffad5e9e0a6e85b30`. Use the release download procedure
only after the matching tag and prerelease have actually been published.
Run installation or repository mutations only for a repository you are authorized
to manage. These instructions do not run anything automatically.

Use this guide instead of the frozen source's historical Git-only quickstart or
its obsolete README CI setup. The supported public commands are `status`, `init`,
`sync`, `adopt`, `mirror`, `next` and `next-write`. NEXT displays a task; it does
not execute it. There is no background update or implicit Muse conversion.

## Git-only source installation

Use a tested Linux or macOS environment with Git and Python 3.11 or 3.14. Hosted
matrix evidence is Linux; retained local evidence is macOS arm64. Other platforms
and interpreter combinations are not established by those results. Choose a fixed
physical kit path and keep its conventional `.venv` there. Do not use `pip install
overseer-kit`, an editable install, a desktop bundle or a copied bound launcher.

After the separately authorized release is published, download its five named
attachments into one directory. Verify the expected manifest/checksum file from
the reviewed release; checksums detect changed bytes, not independent authorship.

```sh
set -eu
cd /absolute/path/to/downloads
shasum -a 256 -c SHA256SUMS
KIT_ROOT=/absolute/fixed/path/to/overseer-kit
KIT_PYTHON=/absolute/path/to/python3.11
test ! -e "$KIT_ROOT"
mkdir -p "$KIT_ROOT"
tar -xzf overseer-kit-1.0.0-rc.1-source.tar.gz \
  -C "$KIT_ROOT" --strip-components=1
"$KIT_PYTHON" -m venv "$KIT_ROOT/.venv"
"$KIT_ROOT/.venv/bin/python" -m pip install -r "$KIT_ROOT/requirements-v1.txt"
"$KIT_ROOT/.venv/bin/python" -m pip check
"$KIT_ROOT/cli/ok" --version
```

`--version` reports `1.0.0`, the frozen runtime version; identify rc.1 by its
tag/commit and release manifest. Python dependencies are fetched by pip; the
release is not an offline environment image. Git-only installation uses only
the kit requirements (`PyYAML==6.0.3`), with no Muse package or account.

For a new, unmanaged **existing Git checkout**, review its files and run:

```sh
KIT_ROOT=/absolute/fixed/path/to/overseer-kit
PROJECT_ROOT=/absolute/path/to/authorized-project
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" init --vcs git \
  --repo-name PROJECT-NAME --lane product --model 'GPT-6 Astra'
"$PROJECT_ROOT/.overseer/bin/ok" status --json
"$PROJECT_ROOT/.overseer/bin/ok" next
```

Do not add `--hooks`. Initialization preserves existing ROADMAP/HANDOVER text;
tracked checkout-local bindings, a foreign existing launcher or an incompatible
legacy config require explicit migration rather than overwriting. For an already
initialized repository bound to this same kit path, use the update/sync procedure
below. Never copy another checkout's config, UUID, launcher or NEXT into a new one.

Keep prompts under the target repository, such as `.overseer/local/task.txt`.
Read current identity, branch, revision and `next_sha256` from `status --json`,
then supply those actual values rather than copying values from the kit project:

```sh
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" next-write \
  --repo-id UUID-FROM-STATUS --branch BRANCH-FROM-STATUS \
  --lane product --model 'GPT-6 Astra' \
  --action-id REVIEWED-ACTION --action-kind plan \
  --base-head REVISION-FROM-STATUS --expect-next NEXT-SHA256-FROM-STATUS \
  --prompt-file .overseer/local/task.txt
"$PROJECT_ROOT/.overseer/bin/ok" next
```

## Optional Muse runtime and explicit adoption

Staying Git-only requires none of this section. Use a separate conventional
Python 3.14 venv for exactly Muse `0.2.1rc5`. The immutable wheel URL remains:

```text
https://raw.githubusercontent.com/aaronrene/overseer-kit/bff17390675358b764d43f31f71233ed11a673b0/muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl
```

| Artifact or payload | SHA-256 |
| --- | --- |
| Recovery wheel | `6b596288fd61f1d0373ead76eff90f82b14291984bff2dbecf9e51cf0694eb4d` |
| `muse-0.2.1rc5-overseer-recovery1-source.zip`, at the same URL directory | `28f5fefacf5860b600edbb83e3cdd35485b983a900ab229a2a1ea673776ae3f0` |
| Installed Muse Python source | `7b181b6eff6bde1b53105f2a7be7bd8937224988965d7462a3a6b04658f35e92` |
| 388-file payload manifest | `3a30de887720d3019ad8a40b300960f97693fc13b91da8814784dabe897115ff` |

This wheel recovers verified installed bytes; it is not an upstream rc5 release.
Do not substitute the old unavailable sdist, the moving staging installer, another
rc version or the PyPI package named `muse`. Retain the source ZIP for rebuilding
under the recipe in `tools/ci/MUSE-RC5-RECOVERY.md`.

```sh
set -eu
KIT_ROOT=/absolute/fixed/path/to/overseer-kit
MUSE_ENV=/absolute/fixed/path/to/muse-rc5-venv
MUSE_PYTHON=/absolute/path/to/python3.14
WHEEL=/absolute/path/to/downloads/muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl
curl --fail --silent --show-error --proto '=https' \
  'https://raw.githubusercontent.com/aaronrene/overseer-kit/bff17390675358b764d43f31f71233ed11a673b0/muse-0.2.1rc5-1overseerrecovery-py3-none-any.whl' \
  -o "$WHEEL"
"$KIT_ROOT/.venv/bin/python" "$KIT_ROOT/tools/ci/muse_artifact.py" verify --wheel "$WHEEL"
test ! -e "$MUSE_ENV"
"$MUSE_PYTHON" -m venv "$MUSE_ENV"
"$MUSE_ENV/bin/python" -m pip install \
  --constraint "$KIT_ROOT/tools/ci/requirements-muse-rc5.txt" "$WHEEL"
"$MUSE_ENV/bin/python" -m pip check
```

Prepare and review the intended Muse code-domain repository history separately,
preserving existing Git refs, dirty/untracked files and identity. Do not import or
clone onto an existing development tree as part of installation. Native clone may
omit empty snapshot directories and native recursive add may omit dot-directories;
compare the complete immutable manifest. Recreate only verified, root-confined
directory metadata in an isolated checkout. Do not copy the kit's 19 directories
into an unrelated project. A dirty/mismatching snapshot is a stop condition for
mirroring, not a reason to disable verification. Executable modes need an explicit
reviewed policy because Muse snapshots do not store them.

For an existing supported Git binding, read its config digest and UUID with
`status --json`; inspect the intended Muse branch/revision independently. Preview:

```sh
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" adopt --vcs muse \
  --muse-python "$MUSE_ENV/bin/python" \
  --repo-id EXISTING-UUID --lane product --model 'GPT-6 Astra' \
  --branch TARGET-MUSE-BRANCH --base-head TARGET-MUSE-REVISION \
  --expect-config CURRENT-CONFIG-SHA256 --dry-run --json
```

Apply the reviewed result by repeating without `--dry-run`. Preserve the reported
config backup. Review and resolve any tracked-local-binding refusal explicitly.
For an already prepared, uninitialized Muse checkout, use `init --vcs muse
--muse-python /absolute/muse-venv/bin/python` with its own new checkout identity.
After adoption, preserved old NEXT may be invalid; publish reviewed prose through
`next-write` using its prior digest and `--vcs muse --base-head REVISION` plus all
context fields. Status/NEXT remain offline and do not prove Hub publication.
Consult `docs/MIGRATE-EXISTING-REPO.md` and `MUSE-BRIDGE-WORKFLOW.md` for the exact
adoption/mirror contracts. Delivery, credentials, hooks and trust changes require
their own explicit scope; this guide does not publish any repository.

## Update and roll back at the same physical kit path

1. Stop commands that use the kit during source replacement. Preserve the exact
   current source/dependency set and record each repository's config, UUID,
   authoritative branch/revision, NEXT digest, application edits and config backups.
   Inventory staged, unstaged and untracked files; never use a blanket reset/clean.
2. Validate the replacement archive/commit and its complete file/mode manifest in
   a separate staging directory. Use an explicit inventory to replace only kit
   source files at the **same physical installation path**; account for removed
   paths rather than overlaying stale code. Preserve the installation's `.venv`
   or deliberately rebuild it from the selected source requirements. A Git-based
   installation can switch its clean source to the exact reviewed commit. An
   archive installation needs its retained file manifest. Do not move the kit,
   swap it through a symlink, or rebind existing consumers to a new path implicitly.
3. A source change intentionally causes a runtime-pin refusal until explicit sync:

```sh
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" sync --dry-run --json
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" sync --json
"$PROJECT_ROOT/.overseer/bin/ok" status --json
"$PROJECT_ROOT/.overseer/bin/ok" next
```

Review the preview before apply. Sync preserves UUID, authority, application files,
ROADMAP, HANDOVER and NEXT; it does not make a stale task current. If branch/revision
or authority changed, explicitly publish a reviewed NEXT for the new context.

For rollback, restore the exact retained prior kit source/dependency set at that
same path, then preview/apply sync and check status/NEXT. R3 exercised fixed-path
rollback against R2 `c389d748c8fc75e23f492e096298db8b83fab054`; that is historical
fixture evidence, not a recommended public release or permission to roll users
back to it. Use the operator's own reviewed prior source. The older held Git-only
release `06f988e5a078ede81c9dc664520833980a9a19a3` is not a distribution target.

To undo Muse adoption, use the current capable runtime **before** downgrading to
a runtime that cannot read Muse/schema-2 configs. Restore the preserved config
with the current config digest and the restored backend's actual branch/revision:

```sh
"$KIT_ROOT/cli/ok" -C "$PROJECT_ROOT" adopt \
  --restore-config .overseer/local/config-before-OLD-DIGEST.yaml \
  --expect-config CURRENT-CONFIG-SHA256 \
  --repo-id EXISTING-UUID --lane product --model 'GPT-6 Astra' \
  --branch RESTORED-BACKEND-BRANCH --base-head RESTORED-BACKEND-REVISION \
  --dry-run --json
```

After review, repeat without `--dry-run`, verify preserved identity/edits and
publish a new NEXT for the restored authority. Restoring a Git config can work
without the Muse runtime. Restore a saved schema-1 Git config before selecting
an old Git-only runtime. Additive ignore rules stay in place. This does not undo
Git/Muse history, restore stale application files or force-push. Relocation,
automatic rollback and arbitrary old-version compatibility are not promised.
