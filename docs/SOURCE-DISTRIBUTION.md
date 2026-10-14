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
and separately bound to the reviewed rc5 package. `tools/ci/muse_artifact.py` and
its manifests verify the exact optional recovery wheel/source. A missing wheel,
Python, dependency or desktop toolchain is a missing prerequisite, not a skip.

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

`tools/ci/supported_v1.py` and the manual-only workflow are prepared reusable
validation drivers. This wave does not run hosted CI or the combined FPR-4
install/migration/rollback/pilot matrix. The completed bounded exercises and source
snapshot remain preserved and are not replaced by these prepared full-product
artifacts. Platforms, native installers, signing, public versions and destinations
require the later owner decision.
