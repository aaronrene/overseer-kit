# Overseer desktop source

The desktop shell launches this installation's `cli/ok app` against an explicitly
selected repository. It uses the same loopback authentication, CSRF, canonical
NEXT and request binding as the CLI. Ambient environment roots and ancestor
searches do not select an installation or project.

Development launch arguments are `--kit-root /physical/installation --repo
/physical/project`. Packaged macOS resolves its own `../Resources/kit` and still
requires `--repo`. Provision the bundled source's conventional `.venv` from pinned
local dependencies before launch. Bindings must name that installation; copying
an existing repository config is not a rebind.

Prepare a fresh portable engine bundle with:

```sh
scripts/bundle-desktop-kit.sh /absolute/new-resource-kit
```

The bundle includes cli, adapters, tools, app assets, policies and templates with
a hash/mode manifest. It excludes virtual environments and local repository
bindings. The Rust/Tauri shell requires the pinned Cargo lock and local toolchain
cache; use the explicitly selected compatible local Rust toolchain with `cargo build --offline --locked` from `desktop/src-tauri`. The locked dependency set needs Rust 1.88 or later. No automatic
installer or dependency fetch is part of local preparation. Native installer
platforms, signing/notarization and publication require later owner choices.

The prior v0.1.0 installer is historical and does not contain this restored build.
Focused launcher/resource checks are recorded with FPR-3; native platform support
and complete packaging remain subject to FPR-4 and independent FPR-5 review.
