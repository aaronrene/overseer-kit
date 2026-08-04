# Track Q — Desktop & app operator runbook

**Audience:** operators, contributors, and non-developer users who want the Overseer governance UI
without living in a terminal.

**Status (2026-07-14):** Track Q is **DONE** (Q0 → Q4b). Mac signed installer is published on
GitHub Release **`v0.1.0`** (Apple Silicon `aarch64` `.dmg`, `signing.status: signed`). 
Windows/Linux signed installers are **not** published yet. Host still needs **Python 3.11+**.
Canonical playbook title: **Open the local console** (Paths 1–3 below; maps to Path C / B / C-dev).

---

## What exists today

| Surface | Who it is for | What you need |
| --- | --- | --- |
| **Docs-first (any AI tool)** | Everyone — the primary, IDE-neutral path | `docs/OVERSEER-HANDOVER.md` paste block + `ok` CLI in terminal |
| **`ok app` (browser)** — Path 2 | Developers / operators comfortable with a terminal | Python 3.11+, initialized repo (`.overseer/`) |
| **Mac desktop installer** — Path 1 | Operators on Apple Silicon | Python 3.11+; set `OVERSEER_REPO_ROOT` for consumer repos |
| **Tauri desktop from source** — Path 3 | Contributors | Build-from-source: Rust 1.88+, Node, Python 3.11+ |
| **Cursor rules/skills** | Cursor users only (optional boost) | Installed automatically via `ok init` / `ok sync` footprint |

The kit is **not Cursor-only**. Cursor rules and Agent Skills are an **optional layer** on top of
portable policy, templates, and CLI. Claude Code, Copilot, or any chatbot works via **handover
paste prompts** and terminal commands — see `README.md` §AI tool compatibility.

---

## Path A — Handover paste (any chatbot; no desktop required)

**Way forward:** Overseer Kit is **developer-centric**. Day-to-day task/product UX belongs in
consumers such as **Scooling**; this kit stays portable governance. Path A remains valid for
anyone with a checkout, but the public site is not an end-user product — it explains and links.

Path A does **not** require Cursor or the desktop app. It **does** require a project that already
has the kit installed (one-time setup). The public website alone does not replace that install step.

1. **Install the kit once** on the machine that holds the project (or use a teammate’s checkout path).
2. In **your project repo**, run once:
   ```bash
   /path/to/overseer-kit/cli/ok -C /path/to/your-repo init --regime git-only --non-interactive
   ```
3. Open `docs/OVERSEER-HANDOVER.md` in your repo (filenames may differ per consumer config).
4. Copy the **Paste-ready prompt** block into **any** AI session (Cursor, Claude, ChatGPT, etc.).
5. When the session ends, run (or ask the agent to run):
   ```bash
   ok governance-sync --dry-run
   ```
6. Commit on a feature branch; merge to `main` only when a human approves (Tier 3).

**Wizard equivalent:** the HANDOVER **NEXT SESSION** block *is* the wizard — one step, one model
label, one paste fence. No separate GUI wizard ships in kit core yet.

**Website visitors:** use the public landing (`docs/landing/` / custom domain) to understand
structure, download the Mac console (Path 1), or clone GitHub. The site does **not** mint CSRF /
session credentials and does **not** run the live console. Day-to-day product UX stays in sister
projects (Track O — consumer UX, not kit core).

---

## Open the local console (Paths 1–3)

### Path 1 — Download Mac console (preferred · Apple Silicon)

1. Confirm **Python 3.11+** (`python3 --version`).
2. Download the signed Apple Silicon (`aarch64`) asset:
   `https://github.com/aaronrene/overseer-kit/releases/download/v0.1.0/Overseer.Kit_0.1.0_aarch64.dmg`
3. Optionally verify `SHA256SUMS.txt` + manifest `signing.status: signed` (§Signed installers below).
4. **Bind a governed checkout before launch:** set `OVERSEER_REPO_ROOT` to the absolute path of
   the consumer (or kit) repo that already has `.overseer/` from `ok init`.  
   **Default without that env var:** the desktop launcher binds `repo_root` to the **bundled kit
   root** inside the app resources — useful for dogfooding the kit, **not** a folder picker.
5. Open the app; desktop shell auto-fills session bootstrap.
6. Confirm the chrome shows the expected bound path before any write action.

*Apple Silicon (`aarch64`) Mac · signed+notarized · requires Python 3.11+. Set
`OVERSEER_REPO_ROOT` to your governed repo. Windows/Linux signed installers are not published yet.
No in-app folder picker in Auto v1.*

### Path 2 — Browser (`ok app`) — legacy “Path B”

```bash
cd /path/to/your-governed-repo   # must have .overseer/ from init
/path/to/overseer-kit/cli/ok app --open
```

The terminal prints **once**:

- `url:` loopback address (default port `8765`)
- `session_credential:` and `csrf_token:`

Paste those into Session bootstrap → Connect. After Connect, the UI collapses bootstrap and shows
the bound checkout from `api/health` → `result.repo_root`.

**Guardrails:** loopback only; Bearer + CSRF on `api/*`; closed Q0 surface except additive
`repo_root` on health (§LAC.6.3).

### Path 3 — Dev desktop (legacy “Path C” build-from-source)

**Prerequisites:** Python 3.11+, Node/npm, **Rust 1.88+** via [rustup](https://rustup.rs/) (Homebrew
Rust 1.87 is too old for current Tauri deps).

```bash
# From overseer-kit root
./scripts/bundle-desktop-kit.sh          # copies Python engine into Tauri resources
cd desktop && npm install
npm run tauri dev                        # dev window → spawns ok app → same UI
```

**Release build (local):**

```bash
npm run tauri build                      # produces platform installer under desktop/src-tauri/target/release/bundle/
```

**Environment overrides:**

| Variable | Purpose |
| --- | --- |
| `OVERSEER_KIT_ROOT` | Kit checkout (auto-detected in dev) |
| `OVERSEER_REPO_ROOT` | Which repo `ok app` binds (**required** for consumer repos; default = bundled kit root) |

---

## Release vs dev (honest status)

| Item | Dev tree (this repo) | Non-dev end user |
| --- | --- | --- |
| Source + tests | ✓ shipped | N/A |
| `ok app` via terminal | ✓ Path 2 | Needs Python 3.11+ + kit path |
| Tauri **build** instructions | ✓ Path 3 / `desktop/README.md` | Requires Rust/Node/Python toolchain |
| **Release CI pipeline** | ✓ `.github/workflows/desktop-release.yml` (+ smoke) | Operator secrets + tag |
| **Mac signed `.dmg` (Apple Silicon)** | ✓ GitHub Release `v0.1.0` · `signing.status: signed` | Path 1 primary CTA |
| **Windows / Linux signed installers** | Pipeline ready; **no** signed Release assets yet | **Unavailable** as primary CTAs |
| Host Python for installers | Still required | **Python 3.11+** on `PATH` (Auto v1 does **not** embed an interpreter) |
| Governance without desktop | ✓ HANDOVER + CLI | ✓ still fully supported |

**Honesty:** do not treat smoke-workflow AppImages (names include `unsigned`) as official installers.
Do not market Windows/Linux downloads until a signed Release row ships.

---

## Signed installers (Path 1 download)

Frozen contracts: `docs/archive/phases/PHASE-Q3-RELEASE-DESKTOP-INSTALLERS.md`,
`docs/archive/phases/PHASE-LANDING-ACCESS-CLARITY.md` (§LAC.2 frozen `.dmg` href).

### Prerequisites on the end host

- **Python 3.11+** available so the bundled `cli/ok` shim can `exec` the local web UI engine.
- The signed installer removes the need to install **Rust/Node** to compile Path 3; it does **not** provide a zero-dependency / embedded-Python install.
- Set `OVERSEER_REPO_ROOT` for consumer repos (default without it = bundled kit root).

### Download + verify

1. Open the kit GitHub Releases page; choose tag `v0.1.0` (or later signed tag matching `VERSION`).
2. Download the **Apple Silicon** asset `Overseer.Kit_0.1.0_aarch64.dmg` plus `SHA256SUMS.txt` and
   `overseer-kit-desktop-{VERSION}-manifest.json`. Win/Linux assets are not primary until signed.
3. Verify SHA-256:
   ```bash
   shasum -a 256 -c SHA256SUMS.txt
   # or: sha256sum -c SHA256SUMS.txt
   ```
4. Confirm the manifest `artifacts[].sha256` matches `SHA256SUMS.txt` and
   `signing.status` is `signed` for your platform.
5. **Linux AppImage only (when a signed Release exists):** verify the **detached** cryptographic
   signature (minisign default):
   ```bash
   minisign -Vm Overseer\ Kit_*_amd64.AppImage -p desktop/keys/release.minisign.pub
   ```
   AppImage signing is **not** OS-vendor notarization (no Gatekeeper/Authenticode equivalent in
   Auto v1). Public key: `desktop/keys/release.minisign.pub` (public material only).

### Operator secret setup checklist (Tier 3 — humans only)

Configure GitHub Actions repository secrets before the first live signed Release. Auto never writes
secret values. Exact names (§QR.6.2):

| Secret | Platform |
| --- | --- |
| `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_SIGNING_IDENTITY` | macOS |
| `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_SPECIFIC_PASSWORD` | macOS notarization (password mode) |
| **or** `APPLE_API_KEY`, `APPLE_API_KEY_ID`, `APPLE_API_ISSUER`, `APPLE_TEAM_ID` | macOS notarization (API key — preferred for kit dogfood CI) |
| `WINDOWS_CERTIFICATE`, `WINDOWS_CERTIFICATE_PASSWORD` | Windows Authenticode |
| `LINUX_SIGNING_KEY`, optional `LINUX_SIGNING_KEY_PASSWORD` | Linux minisign private key |

Also:

1. Align Muse tip + GitHub mirror tip; ensure `VERSION` matches `desktop/package.json`,
   `desktop/src-tauri/Cargo.toml`, and `desktop/src-tauri/tauri.conf.json`.
2. Cut tag `v{VERSION}` (tag-push triggers publish with `publish: true`, `allow_partial: false`).
3. Confirm Release assets are only the §QR.4.5 allowlist (`.dmg` / `.msi` / `.AppImage` +
   sidecar + manifest + `SHA256SUMS.txt`).

Optional: `workflow_dispatch` with inputs `version`, `publish`, `allow_partial` (see workflow).

Workflows:

| File | Role |
| --- | --- |
| `.github/workflows/desktop-release.yml` | Build + sign + publish (fail-closed without secrets when `publish: true`) |
| `.github/workflows/desktop-build-smoke.yml` | Unsigned Linux smoke only — no GitHub Release publish |
| `templates/ci/desktop-release-github-actions.yml` | Vendored example |

Helpers: `tools/desktop_release/` (version-align, manifest, refuse, allowlist, checksums).

---

## Consumer repos (e.g. Scooling)
The desktop app is **not** copied into consumer repos. Consumers get:

| On `ok init` / `ok sync` | Stays in overseer-kit only |
| --- | --- |
| `docs/OVERSEER-HANDOVER.md`, `docs/ROADMAP.md` templates | `tools/app/`, `desktop/`, Tauri shell |
| `.overseer/policy/*`, `policy/tiers.yaml` | Python engine source |
| `.cursor/rules/*`, `.cursor/skills/*` (optional) | `cli/ok` shim (invoke via kit path) |

**Scooling adoption pattern** (same as any `muse+git-mirror` consumer):

```bash
KIT=/path/to/overseer-kit
REPO=/path/to/scooling
$KIT/cli/ok -C $REPO init --migrate --from-config $KIT/tests/fixtures/pilot/config-scooling.yaml --non-interactive
$KIT/cli/ok -C $REPO status --check-footprint
```

- **Product runtime** (`src/phase9a/` router, workers) stays in Scooling — reference only, not vendored.
- **Governance** (handover, roadmap, freeze review, verify-step, honesty) comes from the kit footprint.
- **L1 checkpoints:** Scooling adds `policy/checkpoints.yaml` + `scripts/verify/*` in *its* repo.
- **Desktop UI:** optional; run `$KIT/cli/ok -C $REPO app` or a future published Overseer Kit desktop
  installer pointed at the Scooling checkout via `OVERSEER_REPO_ROOT`.

There is **no MuseHub/Cursor marketplace plugin** for the kit. “Plugin” in kit terms means **L1
checkpoint module** (`verify-step`) and **L2 honesty module** — config-gated engines the consumer
enables in `.overseer/config.yaml`, not an IDE extension.

---

## Quick decision tree

```text
Need governance in a new repo?
  → ok init (Path A or consumer runbook)

Comfortable in terminal + want UI?
  → ok app (Path B)

Want native window + can build Rust?
  → Tauri dev/build (Path C source)

Want native window + signed installer published for this VERSION?
  → Download from GitHub Releases; verify SHA-256 (+ Linux minisig); need Python 3.11+

Non-technical user + no terminal?
  → Path A only (HANDOVER paste into any chatbot) — installers additive when a signed Release exists

Scooling / Knowtation / VideoFactory?
  → Consumer adapter pattern (§Consumer repos above); see docs/CONSUMER-ADAPTER-PATTERN.md
```
