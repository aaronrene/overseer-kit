# Local source distribution and upgrades

Source archives are prepared locally, without signing, publication or a registry.
Use this installation's conventional venv:

```sh
.venv/bin/python tools/ci/source_package.py build --output /absolute/new-source.tar.gz
.venv/bin/python tools/ci/source_package.py verify --archive /absolute/new-source.tar.gz
.venv/bin/python tools/ci/source_package.py unpack --archive /absolute/new-source.tar.gz --destination /absolute/new-installation
```

The sorted archive has fixed timestamps/ownership, exact bytes and executable
modes, and `SOURCE-MANIFEST.json` listing hashes, sizes and modes. Duplicate,
traversing, symlink and special-file members refuse. Required launchers, engines,
app assets, desktop source, policies, dual-skill sources, templates, tests and CI
dotfiles are included. Live repository config/launchers/NEXT, VCS stores, virtual
environments, dependency caches, generated bundles and secret-shaped paths are
excluded. Git tracking in the source repository is not changed. Preparation of
identical source files produces identical archive bytes.

Provision the unpacked installation's `.venv` from pinned local prerequisites in
`requirements-v1.txt`; test dependencies are in `requirements-v1-dev.txt`. There
is no automatic download or neighboring-runtime fallback. Native Muse is optional
and separately bound to an [exact reviewed rc5 or rc11 source
tree](MUSE-RC11-COMPATIBILITY.md). `tools/ci/muse_artifact.py` and
its existing manifests still verify only the optional rc5 recovery wheel/source;
they are not an rc11 installer. A missing wheel,
Python, dependency or desktop toolchain is a missing prerequisite, not a skip.

Prepared desktop resources use the same manifest but a stricter complete-tree
check: `verify-tree` enumerates every file, directory and symlink, including hidden
entries. Only source-manifest files and their necessary parent directories are
accepted. Excluded files, unapproved empty directories, links and special files
refuse even when the approved source files still match. Keep the resource tree
quiescent between this check and local packaging.

The sole additional resource allowance is an explicitly provisioned conventional
`.venv`, recorded in `RESOURCE-RUNTIME.json`. From this installation's venv, use:

```sh
.venv/bin/python -B tools/ci/source_package.py provision-runtime --directory /absolute/new-resource-kit
.venv/bin/python -B tools/ci/source_package.py verify-tree --directory /absolute/new-resource-kit
```

Provisioning requires a clean verified source tree without an existing `.venv`.
It copies only the exact pinned distributions in that resource's manifested
`requirements-v1.txt` from this interpreter's installed local prerequisites. It
copies no pip, development dependencies, activation scripts, bytecode, ambient
`.pth` files or credentials. The resulting `.venv` retains its `pyvenv.cfg`, normal
interpreter links and declared packages. The separate inventory records bytes,
modes, link targets and interpreter identity; verification recomputes allowed
dependency files from the matching pinned local prerequisites rather than letting
arbitrary files enroll through that inventory. All other `.venv` entries refuse.
Verification requires the same interpreter and pinned local prerequisite bytes
used for provisioning. This is same-platform local preparation, not a portable
Python interpreter bundle, native installer acceptance or release. The complete
Python 3.11 cell and owner platform/distribution decisions remain open.

For an existing checkout, quiesce commands and back up the exact installation,
configuration, owned assets and living documents first. Keep the installation at
its same physical root. Replace source with the reviewed archive, verify its
manifest, then use the explicit bound `sync --dry-run` and `sync` with appropriate
`--only` / `--preserve-modified` choices. Runtime mismatch refuses ordinary use
until explicit refresh. UUID, authority, lanes, settings and existing NEXT remain.
For a schema migration, use `init --migrate --dry-run`, review its complete plan,
then apply the exact plan/config digests. Never silently reset optional settings.

Rollback is explicit and quiescent: restore the prior compatible source at the
same root and its byte-exact matching configuration/owned-asset backup, then
review/refresh its runtime binding. Preserve living documents and NEXT; stale
handoffs need accepted republication. Unknown schemas must refuse on an older
runtime until its matching config is restored. Per-file updates may be partial;
inspect reported paths/backups before retrying. Relocation is a separate rebind
decision. A successful rollback does not clear known defects in the older build.

`tools/ci/supported_v1.py` and the manual-only workflow are reusable validation
drivers. The full integrated selection and local installation/migration/rollback
evidence are recorded separately in [FPR-4 validation](validation/FPR-4-COMBINED.md),
including the unresolved Python 3.11 prerequisite and owner acceptance choices.
Neither the smaller driver nor a local source archive establishes full matrix or
release acceptance. The new integrated pilot requires separate owner selection
and authorization. The completed bounded exercises and source snapshot remain
preserved. Hosted CI, platforms, native installers, signing, public versions and
destinations require the owner decision and applicable evidence.
