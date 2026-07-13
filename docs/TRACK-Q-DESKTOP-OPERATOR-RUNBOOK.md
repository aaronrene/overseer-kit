# Track Q — Desktop & app operator runbook

**Audience:** operators, contributors, and non-developer users who want the Overseer governance UI
without living in a terminal.

**Status (2026-07-13):** Track Q is **DONE** (Q0 freeze → Q1 web UI → Q2b `ok` CLI → Q3 Tauri
packaging). Source and tests ship in this repo; **pre-built installers are not yet published** from
CI — see §Release vs dev below.

---

## What exists today

| Surface | Who it is for | What you need |
| --- | --- | --- |
| **Docs-first (any AI tool)** | Everyone — the primary, IDE-neutral path | `docs/OVERSEER-HANDOVER.md` paste block + `ok` CLI in terminal |
| **`ok app` (browser)** | Developers / operators comfortable with a terminal | Python 3.11+, initialized repo (`.overseer/`) |
| **Tauri desktop (`desktop/`)** | Same UI in a native window | Rust 1.88+, Node, Python; build from source today |
| **Cursor rules/skills** | Cursor users only (optional boost) | Installed automatically via `ok init` / `ok sync` footprint |

The kit is **not Cursor-only**. Cursor rules and Agent Skills are an **optional layer** on top of
portable policy, templates, and CLI. Claude Code, Copilot, or any chatbot works via **handover
paste prompts** and terminal commands — see `README.md` §AI tool compatibility.

---

## Path A — Non-developer / any chatbot (no desktop required)

This is the **intended normie path** today and does not require Cursor or the desktop app.

1. **Install the kit once** on your machine (or use a teammate’s checkout path).
2. In **your project repo**, run once:
   ```bash
   /path/to/overseer-kit/cli/ok -C /path/to/your-repo init --regime git-only --non-interactive
   ```
3. Open `docs/OVERSEER-HANDOVER.md` in your repo.
4. Copy the **Paste-ready prompt** block into **any** AI session (Cursor, Claude, ChatGPT, etc.).
5. When the session ends, run (or ask the agent to run):
   ```bash
   ok governance-sync --dry-run
   ```
6. Commit on a feature branch; merge to `main` only when a human approves (Tier 3).

**Wizard equivalent:** the HANDOVER **NEXT SESSION** block *is* the wizard — one step, one model
label, one paste fence. No separate GUI wizard ships yet.

---

## Path B — Developer: local web UI (`ok app`)

```bash
cd /path/to/your-governed-repo   # must have .overseer/ from init
/path/to/overseer-kit/cli/ok app
```

The terminal prints **once**:

- `url:` loopback address (default port `8765`)
- `session_credential:` and `csrf_token:`

Paste those into the browser UI auth panel (or use the desktop app’s auto-bootstrap — §Path C).

**Guardrails:** loopback only; Bearer + CSRF on `api/*`; no engine routes added beyond Q0 freeze.

---

## Path C — Developer: Tauri desktop shell

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
| `OVERSEER_REPO_ROOT` | Which repo `ok app` binds (defaults to kit root in dev) |

---

## Release vs dev (honest status)

| Item | Dev tree (this repo) | Non-dev end user |
| --- | --- | --- |
| Source + tests | ✓ shipped | N/A |
| `ok app` via terminal | ✓ | Needs Python + kit path (technical) |
| Tauri **build** instructions | ✓ `desktop/README.md` | Requires dev toolchain |
| **Signed installers** (`.dmg`, `.msi`, `.AppImage`) | Not automated in CI yet | **Not available** until a release pipeline phase |
| Governance without desktop | ✓ HANDOVER + CLI | ✓ **recommended today** |

**Follow-up slice (not queued):** “Q3-release” or K12-style CI publish — build + attach desktop
artifacts per platform. Requires its own Thinking freeze before Auto build.

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
  → Tauri dev/build (Path C)

Non-technical user + no terminal?
  → Path A only (HANDOVER paste into any chatbot) — desktop installers later

Scooling / Knowtation / VideoFactory?
  → Consumer adapter pattern (§Consumer repos above); see docs/CONSUMER-ADAPTER-PATTERN.md
```
