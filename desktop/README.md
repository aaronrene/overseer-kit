# Overseer Kit — desktop (Track Q / Q3)

Cross-platform Tauri shell for the Q1 local web UI. The desktop app **does not reimplement governance logic** — it spawns the canonical **`ok app`** subprocess and loads the same loopback UI in a native window.

## Prerequisites

- Python 3.11+ (system or `.venv` at kit root)
- Node.js + npm
- Rust **1.88+** via [rustup](https://rustup.rs/) (`desktop/src-tauri/rust-toolchain.toml` pins 1.88.0)
- macOS / Windows / Linux toolchain for your target platform

## Development

From the kit root:

```bash
# optional: bundle Python engine into Tauri resources (required before release builds)
./scripts/bundle-desktop-kit.sh

cd desktop
npm install
npm run tauri dev
```

Environment overrides:

| Variable | Purpose |
| --- | --- |
| `OVERSEER_KIT_ROOT` | Kit checkout (auto-detected when run from repo) |
| `OVERSEER_REPO_ROOT` | Governance repo to bind (defaults to kit root in dev) |

## Release build

```bash
./scripts/bundle-desktop-kit.sh
cd desktop
npm run tauri build
```

Bundled installers place the Python engine under Tauri resources (`resources/kit/`). The Rust launcher resolves that tree at runtime.

## Architecture

```
desktop/src-tauri/   Tauri shell (Rust)
  launcher.rs        spawns cli/ok app, parses startup banner
tools/desktop/       testable Python launcher contract + manifest checks
scripts/bundle-desktop-kit.sh   copies engine into Tauri resources
```

**Boundary:** packaging only — no new `api/*` routes, subcommands, or exit codes.
