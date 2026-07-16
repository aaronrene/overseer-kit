# Phase Q3-release — Desktop installers (Thinking freeze)

Status: **Reviewed → `pass` (QR-r3).** Q3-release Thinking is **spec-only** and must not land
CI workflows, signing config, or installer binaries in this phase. The Q3-release Auto build
(`{step}b`) is cleared only after this document is reviewed → `pass`; it is the only phase that
writes release-pipeline files. Do **not** re-derive this contract during the Auto build. Do **not**
reopen Track Q engine/API surfaces (`docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md`, Q1–Q3 packaging
ground truth).

```yaml
phase: Q3-RELEASE
outputs:
- id: q3-release-desktop-installers
  path: docs/PHASE-Q3-RELEASE-DESKTOP-INSTALLERS.md
  frozen: true
frozen_inputs:
- id: kit-spec-cli
  path: docs/OVERSEER-KIT-SPEC.md#5
- id: freeze-ceremony
  path: docs/OVERSEER-KIT-SPEC.md#6
- id: kit-boundary
  path: AGENTS.md
- id: track-q-q0-distribution
  path: docs/PHASE-TRACK-Q-Q0-OVERSEER-APP.md
- id: track-q-q2a-ok-entrypoint
  path: docs/PHASE-TRACK-Q-Q2A-OK-CLI-ENTRYPOINT.md
- id: q3-desktop-runbook
  path: docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md
- id: q3-desktop-readme
  path: desktop/README.md
- id: q3-desktop-tools
  path: tools/desktop/constants.py
- id: q3-bundle-script
  path: scripts/bundle-desktop-kit.sh
- id: decision-tiers
  path: policy/tiers.yaml
- id: test-tiers
  path: policy/test-tiers.yaml
- id: roadmap-q3-release-row
  path: docs/ROADMAP.md
review_stamp:
  reviewed_at: '2026-07-14T00:58:04Z'
  verdict: pass
  reviewer_mode: agent
  reviewer_model: thinking-high
  reviewer_provider: local
  kit_version: 0.1.0
  artifact_digest: sha256:91d39951c9cd391c22245c918a0369ab9c0bb03c21a074925298a531bc0ae7db
```

**Downstream edge:** the Q3-release Auto build treats this document as ground truth without
re-deriving it (SPEC §6 mandatory reviewed freeze). Track Q Q0–Q3 (`ok app`, Tauri shell,
`tools/desktop/`, `scripts/bundle-desktop-kit.sh`) remain **inputs** — Auto may wire CI around
them; Auto must **not** rewrite launcher, bind, auth, or `api/*` contracts.

**Review record (§6.2):** every freeze-review finding MUST cite **file+line** per SPEC §6; uncited
findings are invalid and are discarded. Fixes applied during the loop are Tier 1 (feature branch);
merge to `main` is Tier 3 and is never part of this loop.

| Round | Reviewer | Verdict | Resolution |
| --- | --- | --- | --- |
| QR-r1 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI checklist dry-run **pass** (0 findings). Semantic findings (non-escalating): **R1-M1** §QR.4.3 missing Auto v1 arch freeze; **R1-M2** no publish allowlist vs Tauri `targets: all`; **R1-M3** Release upload + Actions token permissions unspecified; **R1-M4** soft-skip wording vs fail-closed; **R1-M5** Windows cloud-signer alternate underspecified; **R1-M6** bundle copy allowlist / `.env` refuse not frozen; **R1-N1** Q3 DONE prerequisite + thin frozen_inputs. No escalation categories. |
| QR-r1 fix | Author (cited items only) | — | **R1-M1** arches. **R1-M2** §QR.4.5 allowlist. **R1-M3** §QR.4.6. **R1-M4** fail-closed. **R1-M5** §QR.5.2. **R1-M6** §QR.6.3. **R1-N1** frozen_inputs. |
| QR-r2 | Freeze-review loop (checklist + thinking, `thinking-high`) | findings | CLI **blocked** on C4 false positive (OIDC permission key prose tripped `SECRET_RE`). Semantic: **R2-M1** Path C honesty omitted system-Python prerequisite; **R2-M2** macOS hardened-runtime / timestamp missing; **R2-M3** macOS runner not pinned; **R2-M4** Apple API-key notarization secret names missing; **R2-N1** embed-Python not in rejection table; **R2-N2** `workflow_dispatch` inputs incomplete. No true escalation (C4 = false positive). |
| QR-r2 fix | Author (cited items only) | — | **R2-C4** rephrased OIDC permission prose. **R2-M1** §QR.0/§QR.2/§QR.9 Python honesty. **R2-M2** §QR.5.1 hardened runtime + timestamp. **R2-M3** pin `macos-14`. **R2-M4** §QR.6.2 API-key names. **R2-N1** rejection + out-of-scope. **R2-N2** §QR.4.2 inputs. |
| QR-r3 | Freeze-review loop (checklist + thinking, `thinking-high`) | **pass** | CLI checklist gate clean (0 findings, dry-run). Semantic re-read confirmed R1/R2 RESOLVED: arches + publish allowlist; Release permissions (OIDC prose safe for C4); fail-closed signing; dispatch inputs; Python 3.11+ runtime honesty; hardened runtime + timestamp; pinned `macos-14`/`macos-15`; Apple API-key secret names; closed bundle allowlist; rejection table; credential boundary; seven-tier matrix complete; Track Q engine boundary held; no `security`/`irreversible`/`real_money`/`gates_tier3` escalation. Stamp written by `ok review --freeze`. |

---

## §QR.0 — Simple summary

Today Path C (Tauri desktop) only works if you install Rust, Node, and Python and build from
source. Operators who want a native window without that toolchain are stuck on Path A (docs +
terminal) or Path B (`ok app` in a browser).

**Q3-release freezes how continuous integration builds, signs, and publishes** macOS `.dmg`,
Windows `.msi`, and Linux `.AppImage` installers for the **same** Q3 Tauri shell — so Path C can
mean “download a signed installer,” not only “compile Rust/Node.”

**Frozen runtime honesty:** Auto v1 installers still require **system Python 3.11+** on `PATH`
(or a usable interpreter the bundled `cli/ok` shim can `exec`). The installer removes the
Rust/Node **build** toolchain requirement; it does **not** embed a Python interpreter. Embedding
Python is deferred (§QR.1 out of scope / §QR.10).

**Technical summary:** freeze CI matrix + artifact contract; OS code-signing + notarization /
Authenticode boundary; secret names as GitHub Actions secrets only (never in-repo); release
manifest with checksums and honest signing status; rejection table; Auto deliverables under
`.github/workflows/` + `templates/ci/` + `tools/desktop_release/`; seven-tier matrix. Spec-only —
no workflow YAML or secrets in Thinking.

---

## §QR.1 — Scope

**In scope (freeze only — this phase writes no code):**

- Product goal vs Path A / B / C honesty (§QR.2).
- What exists now / verified baseline (§QR.3).
- CI publish surface: triggers, runners, artifact types (§QR.4).
- Signing + notarization contract per platform (§QR.5).
- Credential / secret boundary (§QR.6).
- Release manifest + publish destination (§QR.7).
- Version alignment rules (§QR.8).
- Boundary + capability table (§QR.9).
- Rejection table (§QR.10).
- Auto build deliverables (§QR.11).
- Fail-closed / error behavior (§QR.12).
- Seven-tier test matrix for Auto (§QR.13).
- Hard stops + tier linkage (§QR.14).
- Definitions of Done (§QR.15).

**Out of scope (explicit non-goals — prevent creep):**

- **Any Track Q engine / API rewrite.** No changes to `tools/app/`, closed `api/*`, bind/auth,
  exit codes, or `ok app` semantics. Q3 shell (`desktop/`, `tools/desktop/`) stays packaging.
- **In-app auto-updater / update CDN.** Publishing installers is in scope; shipping a live
  updater endpoint, forced auto-update, or updater UI is **deferred** to a later freeze.
- **App Store / Microsoft Store / Flathub / Snap submission.** GitHub Releases only for Auto v1.
- **Hosted governance dashboard / Track O / Track P redesign.** Untouched.
- **Embedding consumer product runtimes** (Scooling `src/phase9a/`, Knowtation vault, etc.).
- **Embedding a Python interpreter / PyInstaller / uv-managed runtime inside the installer.**
  Auto v1 ships the Q3 resource kit + Tauri shell only; end hosts need Python 3.11+ (§QR.0).
- **Committing signing certificates, private keys, Apple/Windows secrets, or `.p12`/`.pfx` files.**
- **Tier-3 merge, staging push, live capability flips, or operator secret vault mutations** —
  this freeze never authorizes them.
- **Claiming Muse content-addressed provenance for binary blobs.** Muse remains canonical for
  source; GitHub Releases are a **distribution channel** for installers (§QR.7.2).
- **Thinking phase shipping workflows, binaries, or runbook “installers are live” claims.**

---

## §QR.2 — Product identity (frozen)

| Concern | Q3-release (this phase) | Not this phase |
| --- | --- | --- |
| What it is | CI pipeline that builds + signs + publishes Q3 Tauri installers | New desktop engine or second UI |
| Path C today | Build-from-source (`npm run tauri build`) | — |
| Path C after Auto DONE + live secrets + tag | Download signed `.dmg` / `.msi` / `.AppImage` (no Rust/Node build); **still needs Python 3.11+** | Embed Python / zero-dependency binary |
| Path A / Path B | Remain fully valid without installers | — |
| Authority | Same local `ok app` engine inside the bundle | Remote governance SaaS |
| Distribution host | GitHub Releases on the kit GitHub mirror repo | MuseHub binary store (none) |

**Frozen one-liner:** Q3-release is **packaging/distribution CI** for the existing Tauri shell —
frontend/distribution of governance, never a runtime redesign.

**Honesty rule (frozen):** until a GitHub Release actually publishes platform artifacts with
`signing.status: signed` (or platform-equivalent per §QR.5), operator docs MUST continue to say
pre-built installers are **not** available. Auto MUST update `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md`
§Release vs dev to describe the pipeline and the “secrets configured + tag cut” operator gate —
not invent a false “download now” claim before a live release exists. Auto MUST also state that
signed installers require **Python 3.11+** on the host (same shim contract as `cli/ok`) and MUST
NOT claim a zero-dependency / non-technical install until a later freeze embeds a runtime.

---

## §QR.3 — What exists now (verified, do not redesign)

| Element | Current shape | Source |
| --- | --- | --- |
| Local web UI | `ok app` stdlib loopback; port `8765`; Bearer + CSRF | Track Q / Q1 |
| Canonical launcher name | `ok` (+ `overseer` compat shim) | Track Q / Q2b |
| Tauri shell | `desktop/` spawns `ok app`, loads loopback UI | Track Q / Q3 |
| Python launcher contract | `tools/desktop/` constants + banner parse | Q3 |
| Bundle script | `scripts/bundle-desktop-kit.sh` → `desktop/src-tauri/resources/kit/` | Q3 |
| Bundle targets | Tauri `bundle.targets: "all"`; product `Overseer Kit`; id `com.overseer.kit.desktop` | `desktop/src-tauri/tauri.conf.json` |
| Kit version string | `0.1.0` in `VERSION`, mirrored in desktop package/Cargo/tauri conf | tree |
| Path C docs | Build-from-source; signed installers “not automated in CI yet” | `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` |
| Kit GitHub Actions | **No** `.github/workflows/` in-repo today; only `templates/ci/freeze-review-github-actions.yml` | tree |
| Signing config | **None** in `tauri.conf.json` / Cargo features | tree |

Q3-release **must not** change Q1–Q3 runtime semantics. It **adds** a release pipeline around the
existing `npm run tauri build` / `bundle-desktop-kit.sh` path.

---

## §QR.4 — CI publish surface (frozen)

### §QR.4.1 — Workflow files (Auto deliverables)

| Path | Role |
| --- | --- |
| `.github/workflows/desktop-release.yml` | Kit dogfood workflow — builds, signs (fail-closed without §QR.6.2 secrets on publish), uploads release assets |
| `templates/ci/desktop-release-github-actions.yml` | Vendored example for documentation parity with K11 freeze-review template (may be identical or a documented subset) |

**Prerequisite (frozen):** Track Q / Q3 Tauri packaging is **DONE** (build-verified). Auto must not
reopen Q3 launcher/API work; it only adds the release pipeline around the shipped tree.

Auto MAY add a second workflow `.github/workflows/desktop-build-smoke.yml` (PR / `workflow_dispatch`)
that builds **one** Linux AppImage **without** OS code-signing secrets for CI smoke — must never
upload to a GitHub Release labeled as signed.

### §QR.4.2 — Triggers (frozen)

**Release job** (publishes installers) runs only on:

1. `push` of an annotated or lightweight tag matching `v*` where the tag name (without leading
   `v`) **equals** the kit `VERSION` file contents after trim, **or**
2. `workflow_dispatch` with the frozen inputs below.

**`workflow_dispatch` inputs (frozen):**

| Input | Required | Default | Rule |
| --- | --- | --- | --- |
| `version` | yes | — | Must equal `VERSION` (trim); else fail closed |
| `publish` | no | `true` | When `true`, upload to GitHub Release after signing. When `false`, build + sign may
  still run (operator secret check) but MUST NOT attach assets to a GitHub Release |
| `allow_partial` | no | `false` | See §QR.4.3 |

Tag-push triggers imply `publish: true` and `allow_partial: false`.

Signing MUST NOT be soft-skipped when `publish: true` (tag push or dispatch).

**Forbidden triggers for the publish job:** `pull_request`, `push` to feature branches, schedule.
Those may only run the optional unsigned smoke workflow.

### §QR.4.3 — Runner matrix + arches (frozen)

| Runner | Artifact(s) required | Auto v1 arch | Notes |
| --- | --- | --- | --- |
| `macos-14` or `macos-15` (not unpinned `macos-latest`) | `.dmg` | `aarch64` (arm64 runner native) | Pin a known arm64 image so arch does not silently flip; codesign + notarization required (§QR.5.1) |
| `windows-latest` | `.msi` | `x86_64` | Authenticode required for release publish (§QR.5.2) |
| `ubuntu-22.04` or `ubuntu-24.04` (prefer LTS pin over floating `ubuntu-latest`) | `.AppImage` | `x86_64` | Detached signature required for release publish (§QR.5.3) |

**Multi-arch deferred:** universal macOS DMG, Windows arm64, and Linux aarch64 are **out of Auto
v1**. Manifest `platform` remains OS-level (`macos`/`windows`/`linux`); arch is recorded in the
actual `filename` and MAY be added as an optional `arch` field by Auto without a new freeze if
values stay within `{aarch64, x86_64}`.

All three matrix legs MUST succeed before the release is considered complete. Partial publish
(only one OS) is **fail-closed** for the orchestrating “finalize” job unless the operator
explicitly dispatches with frozen input `allow_partial: true` (default `false`) — and even then
the release notes MUST list missing platforms as unavailable (never as signed).

### §QR.4.4 — Build steps (frozen contract, not shell paste)

Each matrix leg MUST, in order:

1. Checkout the tagged commit (immutable SHA for that tag).
2. Set up Python 3.11+, Node (LTS), Rust per `desktop/src-tauri/rust-toolchain.toml` (1.88+).
3. Run `./scripts/bundle-desktop-kit.sh` (or rely on Tauri `beforeBuildCommand` that invokes it —
   both are acceptable; tests assert the script remains the single copy path into
   `resources/kit/`).
4. `cd desktop && npm ci && npx tauri build` (or `npm run tauri -- build`).
5. Locate bundle outputs under `desktop/src-tauri/target/release/bundle/` (platform-specific
   subdirs).
6. Apply platform signing (§QR.5).
7. Compute SHA-256 of each published file; emit manifest fragment (§QR.7).
8. Upload artifacts to the GitHub Release for tag `v{VERSION}` (§QR.4.6 / §QR.7.2).

**Pinned tools:** Auto documents exact action versions (`actions/checkout@v4`, etc.) in the
workflow; bumping major action versions after DONE needs a follow-up change, not silent drift in
this freeze.

### §QR.4.5 — Publish allowlist (frozen)

Tauri `bundle.targets` may remain `"all"` or Auto MAY narrow it to the explicit set that produces
the three installer types. Regardless of what the build emits, **GitHub Release assets** for Auto
v1 are restricted to this allowlist:

| Allowed Release asset | Notes |
| --- | --- |
| `*.dmg` | macOS only |
| `*.msi` | Windows only |
| `*.AppImage` | Linux only |
| `*.AppImage.minisig` or `*.AppImage.asc` | Detached Linux signature sidecar |
| `overseer-kit-desktop-{VERSION}-manifest.json` | §QR.7.1 |
| `SHA256SUMS.txt` | §QR.7.3 |

**Must not attach** to the Release (even if built): unsigned copies, `.deb`, `.rpm`, raw `.app`
zips, NSIS `.exe` (unless Authenticode-signed **and** a later freeze adds them to this allowlist),
workflow logs, or any file matching secret patterns in §QR.6.3.

### §QR.4.6 — Release create/upload + token permissions (frozen)

| Rule | Requirement |
| --- | --- |
| Mechanism | Create or update the GitHub Release for tag `v{VERSION}` via `gh release upload` **or**
  `softprops/action-gh-release` (or documented equivalent). Auto picks one and tests assert it. |
| Contents | Release body is a short operator-facing note: version, SHA, link to runbook verify steps;
  **no** secrets, certs, or env dumps. |
| `permissions` | Workflow `permissions` MUST be least-privilege: `contents: write` (releases/tags assets)
  and Actions OIDC identity permission set to write **only** if a documented cloud signer
  requires OIDC; default is OIDC identity permission **omitted**. No `actions: write`, no
  `pull-requests: write`, no `repository-projects`. |
| Token | Default Actions `GITHUB_TOKEN` only for Release upload; never a PAT with repo-admin scope in
  workflow YAML. |

---

## §QR.5 — Signing contract (frozen)

“Signed installer” means **platform-appropriate code signature** as defined below. A Release MUST
NOT mark an artifact `signing.status: signed` unless that platform’s rules are met.

### §QR.5.1 — macOS (`.dmg`)

| Rule | Requirement |
| --- | --- |
| Identity | Apple **Developer ID Application** certificate |
| Codesign | Required on the `.app` / `.dmg` produced by Tauri |
| Hardened runtime | Required (`codesign` with hardened runtime enabled) for notarization eligibility |
| Secure timestamp | Required (Apple timestamp authority) on the signed binary / disk image |
| Notarization | Required (`notarytool` / Tauri notarization integration) before publish |
| Stapling | Required when Apple returns a staple-able ticket |
| Fail-closed | Missing Apple secrets on a release job → job **fails**; do not upload unsigned `.dmg` to the Release |

### §QR.5.2 — Windows (`.msi`)

| Rule | Requirement |
| --- | --- |
| Identity (primary) | Authenticode certificate as PFX consumed via `WINDOWS_CERTIFICATE` +
  `WINDOWS_CERTIFICATE_PASSWORD` (§QR.6.2) |
| Identity (alternate) | Azure Trusted Signing (or equivalent cloud Authenticode) **only** when the
  runbook documents the exact Actions OIDC identity steps and still produces a verifiable
  Authenticode signature on the `.msi`; method in manifest remains `authenticode` |
| Sign | Required on the `.msi` before publish |
| Fail-closed | Missing Windows secrets / cloud signer config on a release job → job **fails**; do not
  upload unsigned `.msi` |

NSIS `.exe` bundles are **not** on the §QR.4.5 publish allowlist for Auto v1.

### §QR.5.3 — Linux (`.AppImage`)

Linux has no Gatekeeper/Authenticode equivalent in Auto v1. Frozen definition of “signed” for
`.AppImage`:

| Rule | Requirement |
| --- | --- |
| Detached signature | Minisign **or** GPG detached signature over the AppImage bytes |
| Public key | Published in-repo as a **public** key file under `desktop/keys/` (e.g.
  `desktop/keys/release.minisign.pub` or `desktop/keys/release.gpg.asc`) — public material only |
| Fail-closed | Missing Linux signing private-key secret on a release job → job **fails**; do not upload
  unsigned AppImage as `signed` |
| Honesty | Runbook MUST state AppImage signing is **detached cryptographic** signature, not OS
  vendor notarization |

Tauri updater private key (`TAURI_SIGNING_PRIVATE_KEY`) is **out of scope** for Auto v1 (no
updater). Do not conflate updater keys with §QR.5.3.

### §QR.5.4 — Cross-cutting signing rules

- Release jobs NEVER soft-skip signing when `publish: true`.
- Optional smoke workflows MAY build unsigned artifacts for CI only; artifact names MUST include
  `unsigned` or live only as workflow artifacts (not GitHub Release assets).
- Operator docs MUST NOT call unsigned smoke builds “official installers.”

---

## §QR.6 — Credential / secret boundary (frozen)

### §QR.6.1 — Where secrets live

| Store | Allowed | Forbidden |
| --- | --- | --- |
| GitHub Actions **repository secrets** (and optional environments) | Yes — sole store for private signing material in Auto v1 | — |
| Kit git tree / Muse commits / governance docs / test fixtures | — | **Never** private keys, `.p12`, `.pfx`, Apple app-specific passwords, notarization credentials |
| Workflow YAML | References `${{ secrets.NAME }}` / `${{ vars.NAME }}` only | Literal secret values, base64 cert blobs, PEM private keys |
| Release assets / manifest JSON | Public keys, checksums, signing **status** enums | Private keys, cert passwords |

Configuring or rotating these secrets is **Tier 3** (`policy/tiers.yaml` — secrets and credential
changes). Auto lands workflow references; Auto does **not** write secret values.

### §QR.6.2 — Frozen secret **names** (contract for Auto + tests)

Auto MUST use these exact GitHub Actions secret names (or document a single additive alias map in
the runbook — default is these names):

| Secret name | Platform | Purpose |
| --- | --- | --- |
| `APPLE_CERTIFICATE` | macOS | Base64 Developer ID Application `.p12` / cert blob |
| `APPLE_CERTIFICATE_PASSWORD` | macOS | Certificate password |
| `APPLE_ID` | macOS | Apple ID for notarization |
| `APPLE_TEAM_ID` | macOS | Team ID |
| `APPLE_APP_SPECIFIC_PASSWORD` | macOS | App-specific password (**password mode only** — see alternate modes below) |
| `APPLE_SIGNING_IDENTITY` | macOS | Codesign identity string (e.g. `Developer ID Application: …`) |
| `WINDOWS_CERTIFICATE` | Windows | Base64 PFX (or provider-specific blob documented in runbook) |
| `WINDOWS_CERTIFICATE_PASSWORD` | Windows | PFX password |
| `LINUX_SIGNING_KEY` | Linux | Minisign/GPG **private** key material for detached signature |
| `LINUX_SIGNING_KEY_PASSWORD` | Linux | Optional passphrase; empty allowed if key is unencrypted |

**Apple notarization auth — two frozen alternatives (exactly one configured per repo):**

| Mode | Required secrets | Notes |
| --- | --- | --- |
| App-specific password (default) | `APPLE_ID` + `APPLE_TEAM_ID` + `APPLE_APP_SPECIFIC_PASSWORD` | Matches table above |
| App Store Connect API key | `APPLE_API_KEY` (`.p8` contents or base64) + `APPLE_API_KEY_ID` + `APPLE_API_ISSUER` + `APPLE_TEAM_ID` | Prefer this in CI; do **not** also require `APPLE_APP_SPECIFIC_PASSWORD` when this mode is active |

Auto’s runbook MUST document which mode the kit dogfood uses. Mixing both modes in one job without
a documented precedence is forbidden. Auto must not invent additional Apple auth env names without
amending this freeze.

### §QR.6.3 — Refuse rules (frozen)

- Workflow lint / unit tests MUST fail if workflow files match private-key PEM headers
  (`BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`), PFX magic committed as blobs, or hard-coded
  password assignments.
- `tools/desktop_release/` helpers MUST treat any attempt to write secret values into the repo
  tree as refuse (used by tests; not a runtime daemon).
- Bundle script (`scripts/bundle-desktop-kit.sh`) MUST keep a **closed copy allowlist** (today:
  `adapters`, `cli`, `tools`, `policy`, `templates`, `cursor`, `VERSION`, `pyproject.toml`). Auto
  MUST NOT expand the allowlist to `.env*`, consumer `.overseer/` secrets, `*.p12`, `*.pfx`,
  private keys, or credential files. Security tests assert those paths are absent from a
  fresh bundle destination.
- Private key files under `desktop/keys/` (if ever present locally) MUST be gitignored; only
  public key material is committed.

### §QR.6.4 — Least privilege

| Credential | Allowed use | Forbidden use |
| --- | --- | --- |
| Apple / Windows / Linux signing secrets | Sign release artifacts in CI | Commit, log, echo to stdout, attach to Release, use for git push / muse / deploy |
| `GITHUB_TOKEN` (Actions default) | Upload assets to the Release for the triggering tag | Force-push `main`, delete repos, mutate unrelated workflows |
| Any signing secret | — | Model provider calls, OpenRouter, hosted-dashboard tokens |

---

## §QR.7 — Release manifest + publish destination (frozen)

### §QR.7.1 — Manifest artifact

Every complete release MUST attach `overseer-kit-desktop-{VERSION}-manifest.json` with at least:

```json
{
  "schema_version": 1,
  "product": "Overseer Kit",
  "identifier": "com.overseer.kit.desktop",
  "version": "0.1.0",
  "git_tag": "v0.1.0",
  "git_sha": "<40-char-hex>",
  "artifacts": [
    {
      "platform": "macos",
      "filename": "Overseer Kit_0.1.0_aarch64.dmg",
      "sha256": "<64-hex>",
      "signing": { "status": "signed", "method": "developer_id_notarized" }
    },
    {
      "platform": "windows",
      "filename": "Overseer Kit_0.1.0_x64_en-US.msi",
      "sha256": "<64-hex>",
      "signing": { "status": "signed", "method": "authenticode" }
    },
    {
      "platform": "linux",
      "filename": "Overseer Kit_0.1.0_amd64.AppImage",
      "sha256": "<64-hex>",
      "signing": { "status": "signed", "method": "minisign_detached" }
    }
  ]
}
```

Frozen enums:

| Field | Allowed values |
| --- | --- |
| `artifacts[].platform` | `macos` \| `windows` \| `linux` |
| `artifacts[].signing.status` | `signed` \| `unsigned` \| `unavailable` |
| `artifacts[].signing.method` | `developer_id_notarized` \| `authenticode` \| `minisign_detached` \| `gpg_detached` \| `none` |

Rules:

- `status: signed` requires a non-`none` method from the matching platform row in §QR.5.
- `unsigned` / `unavailable` MUST NOT appear on a GitHub Release that operator docs call
  “signed installers available” — finalize job fails closed if any required platform is not
  `signed` (unless `allow_partial: true`, which forces explicit `unavailable` rows and forbids
  marketing language in auto-generated release notes).

Exact Tauri-generated filenames may vary by arch; Auto’s manifest builder records the **actual**
filename produced. Tests use fixtures, not live Tauri output, for schema validation.

### §QR.7.2 — Publish destination

| Destination | Role |
| --- | --- |
| GitHub Release on the kit’s GitHub remote, tag `v{VERSION}` | **Sole** Auto v1 binary distribution channel |
| MuseHub | Canonical **source** history only — no binary publish API in this freeze |
| npm / PyPI / Homebrew / winget | **Out of scope** Auto v1 |

Regime note (`muse+git-mirror`): cutting a GitHub Release does **not** replace Muse as canonical
source; it does **not** authorize SD-14 mirror shortcuts or `main` merges. Release publish is
orthogonal to Muse↔Git alignment gates (KH2). Operators SHOULD cut release tags from commits that
already exist on both Muse canonical history and the GitHub mirror tip — Auto documents this in
the runbook; Auto does **not** automate Muse tag creation in v1.

### §QR.7.3 — Checksums

In addition to the manifest, Auto MUST attach a plain `SHA256SUMS.txt` (or equivalent) listing
`sha256  filename` lines for every installer asset. Manifest `sha256` fields MUST match that
file.

---

## §QR.8 — Version alignment (frozen)

Before publish, Auto MUST verify equality (string trim) of:

1. Root `VERSION` file
2. `desktop/package.json` → `version`
3. `desktop/src-tauri/Cargo.toml` → `package.version`
4. `desktop/src-tauri/tauri.conf.json` → `version`
5. Git tag `v{VERSION}` (or `workflow_dispatch` `version` input)

Mismatch → fail closed (exit non-zero in the version-check step); no upload.

---

## §QR.9 — Boundary & capability table (frozen)

| Concern | Q3-release Auto | Runtime / operator |
| --- | --- | --- |
| Build Tauri installers in CI | Yes | Configures secrets; cuts tag |
| Sign / notarize | Yes (CI + secrets) | Owns Apple/Windows/Linux credentials |
| Provide Python on end-user hosts | **Never** (Auto v1) | Installs Python 3.11+; later freeze may embed |
| Change `ok app` / `api/*` | **Never** | — |
| Merge to `main` | **Never** | Tier-3 human |
| Hosted multi-repo dashboard | **Never** (separate product) | — |
| Auto-update installed apps | **Never** in Auto v1 | Later freeze |
| Path A / B without installers | Unaffected | Still recommended where appropriate |

| Capability | `git-only` | `muse+git-mirror` / `muse-only` |
| --- | --- | --- |
| Consume published installers | Full (download from GitHub Releases) | Full |
| Kit source canonical | GitHub `main` | MuseHub |
| Release tag cut | Operator on GitHub | Operator; prefer Muse-aligned SHA (§QR.7.2) |

---

## §QR.10 — Rejection table (frozen)

| Proposal | Verdict |
| --- | --- |
| Rewrite Track Q engine / add `api/*` routes for “installer mode” | **Reject** |
| Commit Apple/Windows/Linux private keys or `.p12`/`.pfx` into the repo | **Reject** |
| Publish unsigned `.dmg`/`.msi`/`.AppImage` on a Release labeled signed | **Reject** |
| Soft-skip signing when secrets missing on release publish | **Reject** |
| In-app auto-updater / update CDN in Auto v1 | **Reject** (deferred) |
| App Store / Microsoft Store / Flathub submission in Auto v1 | **Reject** |
| Embed a Python interpreter / claim zero-dependency Path C in Auto v1 | **Reject** (deferred; honesty: Python 3.11+ still required) |
| Embed Scooling/Knowtation product runtime into the installer | **Reject** |
| Claim Muse SHA provenance for binary blobs as ledger `verification_evidence` without a later freeze | **Reject** |
| Thinking phase ships workflow YAML / binaries | **Reject** |
| This freeze authorizes merge to `main` | **Reject** (Tier 3) |
| This freeze configures live GitHub secrets | **Reject** (Tier 3 — operator) |
| Replace Path A as the only supported normie path | **Reject** (installers additive) |
| MuseHub-only installer distribution (no GitHub Release path) | **Reject** (K7 baseline — GitHub distribution required) |
| PR-triggered publish to GitHub Releases | **Reject** (§QR.4.2) |

---

## §QR.11 — Auto build deliverables (frozen)

After freeze `pass`, the Auto build ships **only**:

1. **GitHub Actions workflow** `.github/workflows/desktop-release.yml` implementing §QR.4–§QR.8.
2. **Optional smoke workflow** `.github/workflows/desktop-build-smoke.yml` (unsigned Linux-only or
   documented subset) — must not publish signed Releases.
3. **Template copy** `templates/ci/desktop-release-github-actions.yml` (K11-style vendored example).
4. **Library** `tools/desktop_release/` — version-align checker, manifest schema builder/validator,
   secret-pattern refuse helpers, checksum helpers (pure Python; no network required for unit tests).
5. **Public key path** `desktop/keys/` with README stating public-only; placeholder or real public
   key file for Linux detached verify (private key never committed).
6. **Operator runbook update** — extend `docs/TRACK-Q-DESKTOP-OPERATOR-RUNBOOK.md` §Release vs
   dev + new §Signed installers (download, verify sha256 + Linux detached sig, secret setup
   checklist for operators, honesty about AppImage method, **Python 3.11+ host prerequisite**).
7. **`.gitignore` / `.museignore` entries** for local signing material patterns
   (`*.p12`, `*.pfx`, `*.key`, `apple-api-key.json`, etc.) if not already covered.
8. **Seven-tier tests** per §QR.13.
9. **SPEC §5** — additive note that desktop installers are an optional distribution channel for
   the existing `ok app` / Tauri shell (no new CLI subcommand required for Auto v1).

**No new top-level `ok` subcommand is required** for Auto v1. If Auto adds a read-only helper
(e.g. `ok desktop-release --validate-manifest PATH`), it MUST be inert/read-only and allocated
only if tests need a CLI seam — default is library + workflow only.

### §QR.11.1 — Runbook checklist Auto must document (operator, not Auto execution)

- Create Apple Developer ID + notarization credentials; store under §QR.6.2 names.
- Create Windows Authenticode cert; store under §QR.6.2 names.
- Generate Linux minisign/GPG keypair; commit **public** key only; store private key as
  `LINUX_SIGNING_KEY`.
- Ensure `VERSION` and desktop version fields match.
- Align Muse + GitHub tips; cut `v{VERSION}` tag; confirm Release assets + manifest.

---

## §QR.12 — Fail-closed / errors (frozen)

| Condition | Behavior |
| --- | --- |
| Version mismatch (§QR.8) | Fail job; no upload |
| Missing required signing secret on release publish | Fail job; no upload for that platform; finalize fails unless `allow_partial` (still honest) |
| `tauri build` non-zero | Fail job |
| Bundle script missing / non-executable | Fail job |
| Manifest schema invalid | Fail finalize; do not mark Release complete |
| Smoke workflow | May upload **unsigned** workflow artifacts only; never GitHub Release |
| Secret-looking material in git diff of release files | Unit/security tests fail the Auto build locally |

No new process-level `ok` exit code is allocated by this freeze unless Auto adds an optional CLI
validator — if added, reuse exit `2` for validation refuse (no new number without amendment).

---

## §QR.13 — Seven-tier test matrix (Auto build must satisfy)

The Auto build ships all seven tiers green locally before DONE (`policy/test-tiers.yaml`).
Live Apple/Windows notarization and live GitHub Release upload are **not** required for DONE —
those need operator secrets (Tier 3). Tests use fixtures + workflow static analysis.

| Tier | Proves |
| --- | --- |
| **unit** | Version-align checker accepts equal VERSION/package/Cargo/tauri strings and refuses mismatch; manifest schema accepts valid fixture and refuses unknown `platform` / `signing.status` / `signing.method`; `signed` + `method: none` refused; secret-pattern scanner flags PEM/PFX-like blobs and passes clean workflow fixtures; checksum helper matches known vectors; public-key path rules (private key filenames refused under `desktop/keys/`). |
| **integration** | Workflow YAML parses; release workflow declares macOS/Windows/Linux matrix and tag/`workflow_dispatch` triggers only; macOS runner is pinned `macos-14` or `macos-15` (not bare `macos-latest`); workflow `permissions` omit elevated scopes beyond §QR.4.6; smoke workflow (if present) has no Release-publish step; template under `templates/ci/` exists and references §QR.6.2 secret names (including Apple API-key alternate names when documented); `bundle-desktop-kit.sh` still listed as the kit copy path with closed allowlist; `tools/desktop_release` builds a manifest from fixture artifact names; publish-allowlist helper rejects `.deb`/`.rpm`/unsigned names. |
| **e2e** | Fixture “release finalize” path: given three platform artifact fixtures + signatures metadata → writes manifest + `SHA256SUMS.txt` → validates round-trip; simulated missing Apple secret → finalize refuse; runbook contains Path C download section, AppImage honesty sentence, and **Python 3.11+ host prerequisite**; no mutation of Track Q `tools/app` API allowlists; fresh bundle destination contains no `.env` fixture planted outside allowlist. |
| **stress** | Manifest builder handles ≥ 50 artifact filename entries without unbounded memory growth (documented cap or streaming hash); checksum of multi-megabyte fixture file completes without loading entire file twice unboundedly if streaming API exists — otherwise document single-pass bound. |
| **data-integrity** | Twin manifest builds from identical fixtures → byte-identical JSON (canonical key order frozen by builder); sha256 in manifest matches `SHA256SUMS.txt`; re-validate after rewrite succeeds; version-align is pure (no writes). |
| **performance** | Version-align + manifest validate on fixture completes within a documented bound (e.g. ≤ 2s on CI-sized fixture); workflow YAML scan of secret patterns bounded to release workflow paths (no full-repo secret hunt as the only path). |
| **security** | No private key / cert password literals in workflow or template files; `.gitignore` covers `*.p12` `*.pfx` signing patterns; release workflow does not `echo` secret values; `pull_request` cannot publish Releases; `permissions` match §QR.4.6; Track Q launcher still invokes `ok app` only; no new non-loopback bind defaults; security tests assert rejection-table items that are mechanically checkable (unsigned labeled signed refused by validator; non-allowlisted asset types refused). |

---

## §QR.14 — Hard stops + tier linkage (frozen)

| Action | Tier | Rule |
| --- | --- | --- |
| Feature-branch commits for this freeze / Auto | Tier 1 | SD-1 / SD-17 |
| `git push` feature branch / open PR | Tier 1 | No merge |
| Confirm Linux detached-sig algorithm choice if Auto needs GPG vs minisign default | Tier 2 | Freeze default = **minisign**; GPG is allowed alternate via `method: gpg_detached` — record ADR only if changing default |
| Configure / rotate GitHub signing secrets | Tier 3 | Operator only |
| Merge to `main` | Tier 3 | Human only — not authorized here |
| Staging push / live capability flip | Tier 3 | Human only |
| Cut first public signed Release | Operator | Requires secrets + tag; not authorized by this Thinking freeze alone |

Escalation categories for freeze review remain: `security`, `irreversible`, `real_money`,
`gates_tier3`.

---

## §QR.15 — Definitions of Done

### §QR.15.1 — Thinking freeze (this phase)

- [x] This document reviewed → `pass` via `/freeze-review-loop` + `ok review --freeze`
- [x] Review-record table stamped; `review_stamp` filled
- [x] `docs/ROADMAP.md` — Q3-release promoted from exploration backlog; Thinking DONE; Auto TODO
- [x] `docs/OVERSEER-HANDOVER.md` NEXT regenerated for Q3-release Auto (SD-17)
- [x] No workflow / binary / signing-secret material landed in Thinking
- [x] No Tier-3 merge performed

### §QR.15.2 — Auto build (later)

- [x] Mechanical implementation matches §§QR.4–QR.12 and §QR.11
- [x] Seven-tier matrix §QR.13 green
- [x] `/build-verification-review` → `pass` before ROADMAP Auto → DONE
- [x] Governance sync (ROADMAP + HANDOVER) in the closing commit
- [x] Feature-branch push / PR only; merge remains Tier 3
- [x] Track Q engine/API surfaces unchanged
- [x] Live Apple/Windows notarization **not** required for Auto DONE (secrets are operator Tier 3)
